# -*- coding: utf-8 -*-
# 真机验证 4 项保守实施回归。
#
# 4 项原始变更详情见 CODE_WIKI v4.1.0-dev：
# ① spider.py：_safe_loads / _is_safe_http_url 保护 JSON 解析与 URL scheme 校验
# ② ws_client.py：心跳回调 wait_for 兜底 + 超时主动关连接
# ③ proxy.py：ProxyInfo 接受 IPv6 主机（[::1] / ::1）
# ④ video_postprocess.py：_run_ffmpeg_checked 超时分类型（不再被 unknown error 吞）

import json
import subprocess
import time
import types
from pathlib import Path
from typing import Any, cast

import pytest

# ======================================================================
# ① spider.py 防御
# ======================================================================


def test_spider_safe_loads_returns_none_on_bad_json() -> None:
    from src.spider import _safe_loads

    # 合法 JSON 但非 dict（如数组）：应返回 None（供调用方按业务判空）
    assert _safe_loads("[1,2,3]") is None
    # 合法 dict
    assert _safe_loads('{"a": 1}') == {"a": 1}
    # 损坏的 JSON（缺右括号）：应捕获 JSONDecodeError 返 None，不抛
    assert _safe_loads("{a: 1") is None


def test_spider_is_safe_http_url_whitelist() -> None:
    from src.spider import _is_safe_http_url

    # 允许的协议
    assert _is_safe_http_url("https://live.douyin.com/123")
    assert _is_safe_http_url("http://example.com")
    assert _is_safe_http_url("wss://danmuproxy.douyu.com:8506")
    assert _is_safe_http_url("ws://example.com/ws")
    # 拒绝的协议（SSRF 风险面）
    assert not _is_safe_http_url("file:///etc/passwd")
    assert not _is_safe_http_url("gopher://internal/secret")
    assert not _is_safe_http_url("ftp://internal/data")
    # 缺 scheme 的相对路径也应拒绝
    assert not _is_safe_http_url("//example.com/path")


# ======================================================================
# ② ws_client 心跳超时
# ======================================================================


def test_ws_heartbeat_timeout_closes_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    # 心跳回调 hang 住超过 _HEARTBEAT_TIMEOUT_SECONDS 时，循环应主动关连接退出，
    # 让外层 connect() 进入重连路径而非永远等待。
    # 策略：patch 内部 websockets.connect 不直接连真实 ws，而是返回假协程
    import asyncio
    import inspect

    from loguru import logger

    from src import ws_client

    # M-29（CODE_REVIEW_2026-09-29_2）假绿修复。旧用例只断 `len(close_called) >= 1`，而**用例自己**
    # 末尾那句无条件 `await client.close()` 本身就会产生一次 ws.close()：把生产侧
    # src/ws_client.py::_heartbeat_loop 的 wait_for 超时分支整块删掉，外部关闭也「恰好」满足断言，
    # 于是超时特性有无 = 全绿。现按三条正交通道归因，全部只观察生产代码自身的行为、不复制心跳逻辑：
    #   ① 来源：沿调用栈取「最近一个位于 ws_client.py 内的调用帧」的协程名——超时分支从
    #      _heartbeat_loop 里 await close()，外部停止从 WsClient.close() 里 await，是两条不同代码；
    #   ② 生产自带的判别位 client._stopped：WsClient.close() 先置 True 再关连接，超时分支不置位；
    #   ③ 时刻：第一次 close 必须落在超时点上（≥ 超时阈值下界）且**早于**用例发起外部停止的那一刻。
    # 另加 ④ 生产侧「心跳回调超时」warning 文本 + 其发出时刻，防止「留着 close、删掉告警」的半吊子改动。
    closes: list[dict[str, Any]] = []
    heartbeat_calls: list[float] = []
    stop_requested_at: list[float] = []

    # 断言与语言解耦（手法与口径同 tests/conftest.py::_pin_identity_translation）：本用例要锁的
    # warning 文案在 en_US/en_GB 目录里都有译文，而同一会话内任何 `import main`（main.py 模块级
    # 调 i18n.set_language）都会在**用例运行中**把 i18n._tr 从恒等映射重绑成真目录，于是
    # 「按简中模板断言日志文本」当场失效——2026-09-29 本机实测同文件
    # test_video_postprocess_timeout_logged_as_timeout 正是这样红的。用例内再钉一次恒等。
    import i18n

    monkeypatch.setattr(i18n, "_tr", lambda text: text)

    _started_at = time.monotonic()
    # 超时阈值 = max(1.0, heartbeat_interval + 1.0)（_HEARTBEAT_TIMEOUT_SECONDS 是 _heartbeat_loop
    # 的局部常量、无法 monkeypatch），故心跳 hang 8s 必然大于阈值；外部停止安排在 3.0s——
    # 既晚于超时点（≈1.1s）、又早于心跳自身返回（8s），「超时先于外部停止」才是可判定的。
    _STOP_AFTER_SECONDS = 3.0
    _HEARTBEAT_HANG_SECONDS = 8.0
    _TIMEOUT_FLOOR_SECONDS = 1.0

    class _FakeWs:
        # 模拟底层 ws：close() 记录标记，__aiter__ 返回空流（心跳之外没消息）
        def __init__(self) -> None:
            pass

        async def close(self) -> None:
            # 归因①：谁 await 了这次 close()。假 ws 自身的帧往上一格就是 await 它的生产协程，
            # 再向上找第一个落在 ws_client.py 里的帧即可（比只取 f_back 更耐重构：生产侧若把
            # 关闭动作下沉一层私有 helper，归因仍指向那条代码路径）。
            source = "unknown"
            frame = inspect.currentframe()
            caller = frame.f_back if frame is not None else None
            while caller is not None:
                if caller.f_code.co_filename.replace("\\", "/").endswith("src/ws_client.py"):
                    source = caller.f_code.co_name
                    break
                caller = caller.f_back
            closes.append(
                {
                    "source": source,
                    "elapsed": time.monotonic() - _started_at,
                    "stopped": client._stopped,
                }
            )

        def __aiter__(self) -> "_FakeWs":
            return self

        async def __anext__(self) -> bytes:
            # 永不返回下一帧，循环将卡在 async for；停止由 close() 触发
            await asyncio.sleep(60)
            return b""

    class _FakeConnectCtx:
        async def __aenter__(self) -> _FakeWs:
            return _FakeWs()

        async def __aexit__(self, *exc: Any) -> None:
            pass

    def fake_connect(*args: Any, **kwargs: Any) -> _FakeConnectCtx:
        # websockets v10+ 的 connect 是「可 awaitable + 上下文管理器」对象，
        # async with 直接调 __aenter__ 不需 await；故 fake 也不能 async。
        return _FakeConnectCtx()

    async def slow_heartbeat() -> None:
        heartbeat_calls.append(time.monotonic() - _started_at)
        # 心跳 hang 远超 max(1.0, heartbeat_interval+1.0) 阈值，必然触发超时分支
        await asyncio.sleep(_HEARTBEAT_HANG_SECONDS)

    client = ws_client.WsClient(
        url="ws://example.invalid",
        on_message=lambda _d: None,
        on_heartbeat=slow_heartbeat,
        heartbeat_interval=0.05,  # 极短间隔
    )
    # 把超时阈值也调小（heartbeat_interval+1 = 1.05s），用 monkeypatch 改常量
    # 因为 _HEARTBEAT_TIMEOUT_SECONDS 是 _heartbeat_loop 内的局部变量，
    # 这里改不了，直接靠 hang 时长大于默认 1.05s 触发
    # MID-66（tests/test_test_hygiene.py R1 规则）：websockets 是三方模块本体，
    # setattr 到它上面等于全进程换掉 connect——同会话其它用例的真实/打桩连接都会吃到假实现。
    # 正确写法是浅拷贝替身，只替换 ws_client 命名空间里的全局名（与 subprocess/httpx 同源）。
    _ws_shim = types.SimpleNamespace(**vars(ws_client.websockets))
    _ws_shim.connect = fake_connect
    monkeypatch.setattr(ws_client, "websockets", _ws_shim)

    logged: list[tuple[float, str]] = []
    sink_id = logger.add(lambda msg: logged.append((time.monotonic() - _started_at, str(msg))), level="WARNING")

    async def run_and_stop() -> None:
        t = asyncio.create_task(client.connect())
        # 先等到「心跳被挂起 + wait_for 超时 + 超时分支主动 close」全部发生，再请求外部停止：
        # 停止时刻因此成为一条硬上界，第一次 close 若来自超时分支必然早于它。
        await asyncio.sleep(_STOP_AFTER_SECONDS)
        stop_requested_at.append(time.monotonic() - _started_at)
        await client.close()
        try:
            await asyncio.wait_for(t, timeout=0.5)
        except TimeoutError:
            # 假 ws 的 __anext__ 睡 60s，connect() 不会自己退出；取消它只是收尾，
            # 判定所需的 close 归因早已记录完毕。
            t.cancel()

    try:
        asyncio.run(run_and_stop())
    finally:
        logger.remove(sink_id)

    # 前置：心跳回调确实被调用过（否则「超时」无从谈起，整条用例只是在测重连）
    assert heartbeat_calls, "心跳回调从未被调用，本用例没有覆盖超时路径"
    assert closes, f"心跳超时后没有任何 ws.close()（超时分支未主动关连接）: {closes}"

    first = closes[0]
    # 归因①/②：第一次 close 必须来自 _heartbeat_loop，且当时 _stopped 仍为 False
    # （外部 client.close() 一定先置 True 再关连接）。删掉超时分支后这里必然错位。
    assert (
        first["source"] == "_heartbeat_loop"
    ), f"第一次 close 的来源不是心跳超时分支（超时特性疑似被删，只剩外部停止）: {closes}"
    assert first["stopped"] is False, f"第一次 close 时 _stopped 已置位，说明它来自外部停止而非超时分支: {closes}"
    # 归因③：时刻——既不能「一进来就关」（那样是别的路径），也必须早于用例请求外部停止
    assert stop_requested_at, "用例没有记录外部停止时刻，无法判定超时先于停止"
    assert (
        first["elapsed"] >= _TIMEOUT_FLOOR_SECONDS
    ), f"第一次 close 早于超时阈值下界 {_TIMEOUT_FLOOR_SECONDS}s，不是超时分支的产物: {first}"
    assert first["elapsed"] < stop_requested_at[0], (
        f"第一次 close（{first['elapsed']:.3f}s）没有早于外部停止（{stop_requested_at[0]:.3f}s）"
        "——心跳超时分支未主动关连接"
    )
    # 归因④：生产侧「心跳回调超时」warning 必须发出，且发出时刻同样早于外部停止
    timeout_warnings = [(at, msg) for at, msg in logged if "心跳回调超时" in msg]
    assert timeout_warnings, f"未记录「心跳回调超时」warning，实际 WARNING 日志: {[m for _, m in logged]}"
    assert timeout_warnings[0][0] < stop_requested_at[0], f"超时告警晚于外部停止，归因不成立: {timeout_warnings}"
    assert "关闭连接以触发重连" in timeout_warnings[0][1], f"告警文案缺「触发重连」语义: {timeout_warnings[0][1]}"
    # 收尾自证：用例结束时客户端确实处于停止态（外部 close 走完了）
    assert client._stopped is True


# ======================================================================
# ③ proxy.py IPv6
# ======================================================================


def test_proxy_info_accepts_ipv6_with_brackets() -> None:
    from src.proxy import ProxyInfo

    # [::1]:8080 形如 Windows 注册表 ProxyServer 的 IPv6 字面量
    info = ProxyInfo("[::1]", "8080")
    assert info.ip == "[::1]"
    assert info.port == "8080"


def test_proxy_info_accepts_bare_ipv6() -> None:
    from src.proxy import ProxyInfo

    # 不带方括号的裸 IPv6（少见但兜底）
    info = ProxyInfo("::1", "8080")
    assert info.ip == "::1"
    assert info.port == "8080"


def test_proxy_info_rejects_invalid_ip() -> None:
    from src.proxy import ProxyInfo

    # 端口合法但 IP 既非 IPv4/IPv6/域名：必须抛 ValueError
    with pytest.raises(ValueError):
        ProxyInfo("not a host!@#", "8080")


# ======================================================================
# ④ video_postprocess 超时分类型
# ======================================================================


def test_video_postprocess_timeout_logged_as_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 模拟 ffmpeg 卡死：替换 _run_ffmpeg_checked 抛 TimeoutExpired，
    # 验证调用方把异常分到「超时」分支而不是「unknown error」分支。
    import io

    from loguru import logger

    # 断言与语言解耦用 i18n._tr 恒等映射（手法与口径同 tests/conftest.py::_pin_identity_translation），
    # 钉死动作见下方 import 之后的 monkeypatch.setattr。
    import i18n

    # 必须先 import main，让 video_postprocess 的循环依赖（notify → video_postprocess）
    # 在「先 main 后 video_postprocess」顺序下完成解析；否则 pytest 在子测试里 import
    # src.video_postprocess 会撞上 notify 内部的延迟导入失败。
    import main  # noqa: F401
    from src import video_postprocess

    # 恒等映射必须打在 `import main` **之后**：main.py 模块级会调 i18n.set_language(language)
    # 把 i18n._tr 重绑成真目录（宿主中文 Windows 上探测出 en_US），于是「按简中模板断言日志文本」
    # 的口径当场失效——2026-09-29 本机实测本用例正是被这条重绑打红的（日志变成
    # "ffmpeg remux/transcode timed out"）。本用例锁的是「异常被分到超时分支而非 unknown error
    # 分支」这一**分类语义**，与目录语言无关，故在用例内钉死恒等，把断言与宿主语言/导入顺序解耦
    # （同文件 ② 心跳用例采用同一手法）。
    monkeypatch.setattr(i18n, "_tr", lambda text: text)

    buf = io.StringIO()
    sink_id = logger.add(buf, format="{level} | {message}", level="DEBUG")
    try:

        def fake_run(*args: Any, **kwargs: Any) -> str:
            raise subprocess.TimeoutExpired(cmd=["ffmpeg"], timeout=600)

        monkeypatch.setattr(video_postprocess, "_run_ffmpeg_checked", fake_run)
        target = tmp_path / "input.ts"
        target.write_bytes(b"\x47" * 100)  # 合法 TS magic
        # 三个 caller 各自走一遍，验证都把异常分到 TimeoutExpired 分支
        video_postprocess.segment_video(
            str(target), str(tmp_path / "out_%03d.ts"), "mpegts", "1800", is_original_delete=False
        )
        video_postprocess.converts_mp4(str(target), is_original_delete=False)
        video_postprocess.converts_m4a(str(target), is_original_delete=False)
        text = buf.getvalue()
        # 三处都应在日志里出现「超时」字样（不再被「unknown error」吞）
        assert text.count("超时") >= 3, f"超时未被分类: {text}"
        # M-29 同族收紧（CODE_REVIEW_2026-09-29_2 的「三处都超时」聚合计数无法归因）：
        # 上面那条只数「超时」出现几次——一个入口多打两行同样凑够 3，而某个入口真退化成
        # unknown error 时，另两个入口照样把计数顶起来，聚合计数对「哪一条丢了」全盲。
        # 现按三个入口各自的专属文案逐条归因（锚点与 src/video_postprocess.py 里三个
        # except subprocess.TimeoutExpired 分支一一对应：segment_video / converts_mp4 /
        # converts_m4a），并反向钉死「本用例三次调用没有任何一次落到 unknown error 兜底分支」。
        # 改生产文案须同步改这三条锚点——聚合计数做不到这件事，所以才不算冗余。
        assert "ffmpeg 转封装/转码超时" in text, f"segment_video 的超时分支未被单独归因: {text}"
        assert "ffmpeg 转 MP4 超时" in text, f"converts_mp4 的超时分支未被单独归因: {text}"
        assert "ffmpeg 抽音频超时" in text, f"converts_m4a 的超时分支未被单独归因: {text}"
        assert "An unknown error occurred" not in text, f"超时被兜底成 unknown error（分类语义丢失）: {text}"
    finally:
        logger.remove(sink_id)
