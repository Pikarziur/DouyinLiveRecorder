# -*- coding: utf-8 -*-
# 真实房间端到端验证:BilibiliDanmaku + collector 线程 → SRT 产出。
#
# 用法:python tests/test_bili_live_collector.py https://live.bilibili.com/545068  [秒数]

import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import spider
from src.collector import DanmakuCollector
from src.platforms.bilibili import BilibiliDanmaku

URL = sys.argv[1] if len(sys.argv) > 1 else "https://live.bilibili.com/545068"
# 双模式运行：既支持 `python 本文件.py <URL> <秒数>` 手动验证，也允许被 pytest 直接收集执行。
# 末尾的 `and not sys.argv[2].startswith("-")` 是必需的守卫：pytest 运行时 sys.argv[2]
# 可能是 `-q`、`-x` 等选项，缺少该守卫会执行 int('-q') 并抛出 ValueError，
# 表现为「一跑 pytest 就在收集期崩溃」，且报错位置与该行相距较远，排查成本高。
# 在此之上再补 isdigit 数值性判定（R7③，2026-09-30）：`pytest a.py b.py …` 一次点多个文件时
# sys.argv[2] 是**下一个测试文件的路径**，它不带 `-` 前缀、只判非选项就会放行，随后 int(路径) 当场
# ValueError，本模块收集直接 ERROR（2026-09-30 实测：4 errors during collection）。
# 真机调用 `python 本文件.py <URL> 60` 的语义完全不变（"60".isdigit() 为真）。
_SECONDS_RAW = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else ""
SECONDS = int(_SECONDS_RAW) if _SECONDS_RAW.isdigit() else 20


def main() -> None:
    info = asyncio.run(spider.get_bilibili_danmaku_info(url=URL, proxy_addr=None))
    assert isinstance(info, dict), f"弹幕信息获取失败: {info!r}"
    # 契约前置校验：确保后续下标访问不会因缺字段而 KeyError。
    # 仅 token 额外要求非空（断言语义），room_id / server_host 只需存在。
    required_keys = ("room_id", "server_host", "token")
    missing = [k for k in required_keys if k not in info]
    assert not missing and info.get("token"), f"弹幕信息缺失或无效字段: {missing} | info={info!r}"
    # token 为字符串令牌，断言非空后按 str 处理以避免 object 类型告警。
    token = info["token"]
    assert isinstance(token, str), f"token 类型异常: {type(token)!r}"
    print(f"[OK] danmaku_info: room={info['room_id']} host={info['server_host']} token_len={len(token)}")

    # 输出目录固定为 tests/_out_live：先清空再写，避免上一轮遗留的 SRT
    # 混入本轮结果，导致「文件存在」的断言通过但实际内容来自旧数据。
    # 「清空」的范围现收窄到本脚本自己的产物前缀（R7④，2026-09-30）：无差别删掉目录里每一项会
    # 把并行运行的其它平台验证产物一起删（真机验证常多平台同开），且目录里混进子目录时
    # os.remove 直接抛 IsADirectoryError/PermissionError，本轮验证卡在清理阶段。
    # 原意「本轮从干净目录开始」不变，只是删得准。
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_out_live")
    os.makedirs(base_dir, exist_ok=True)
    for f in os.listdir(base_dir):
        if f.startswith("真实弹幕验证"):
            stale = os.path.join(base_dir, f)
            # 先判是文件再删：子目录一律跳过，交由 tests/conftest.py 的会话收尾统一 rmtree。
            if os.path.isfile(stale):
                os.remove(stale)

    base = os.path.join(base_dir, "真实弹幕验证_545068")
    collector = DanmakuCollector(
        danmaku_cls=BilibiliDanmaku,
        danmaku_args=info,
        base_filename=base,
        # segment_seconds=None 表示不按时间分片：短时验证只需单文件 SRT，
        # 开启分片会额外产生 _001/_002 等后缀文件，增加结果判定的复杂度。
        segment_seconds=None,
    )
    collector.start()
    print(f"[OK] collector 已启动,监听 {SECONDS}s...")
    # 采集在独立线程中运行，此处主线程睡眠等待其积累消息；
    # SECONDS 需足够长以覆盖 WebSocket 握手 + 进房 + AUTH 的耗时。
    time.sleep(SECONDS)
    count = collector.message_count
    # stop() 必须在计数之后、判定之前调用：它负责收尾写入 SRT，
    # 提前停止会导致 SRT 尚未落盘，后续 isfile 判定失败。
    collector.stop()
    print(f"[OK] 收到弹幕消息数: {count}")

    srt_file = base + ".srt"
    if os.path.isfile(srt_file):
        with open(srt_file, encoding="utf-8") as fh:
            content = fh.read()
        print("=== SRT 内容(前 20 行) ===")
        print("\n".join(content.splitlines()[:20]))
        # count 为 0 不算失败：SRT 已生成说明连接与 AUTH 链路正常，
        # 只是该时段无人发言（冷门房间/深夜常见），与连接失败要区分开。
        if count > 0:
            print("[PASS] 端到端:真实弹幕已写入 SRT")
        else:
            print("[WARN] 当前房间该时段无弹幕(连接正常)")
    else:
        print(f"[FAIL] SRT 未生成: {srt_file}")
        print(
            f'VERIFICATION_RESULT: {json.dumps({"platform": "bilibili", "script": "test_bili_live_collector.py", "url": URL, "status": "FAIL", "messages": 0})}'
        )
        sys.exit(1)
    _srt_sz = os.path.getsize(srt_file)
    print(
        f'VERIFICATION_RESULT: {json.dumps({"platform": "bilibili", "script": "test_bili_live_collector.py", "url": URL, "status": "PASS" if count > 0 else "WARN", "messages": count, "srt_bytes": _srt_sz})}'
    )


if __name__ == "__main__":
    main()
