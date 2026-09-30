# tests/test_gui_wrap_hints.py — 长提示文案自适应折行回归锁（2026-09-29 文字截断修复）。
#
# 根因：长文案标签的请求宽超出父容器分配宽时，Tk pack 按默认 anchor=center **两侧对称裁切**
# （150% DPI 下控制台「启动后将调用 main.py…」提示与弹幕占位提示两侧各缺半个字；画质页说明的
# 定宽 wraplength=1000 在窄窗口下同样右缘裁切）。
# 修复（gui.py）：_compute_wraplength 纯函数（设备像素→逻辑值，除以 CTk 控件缩放率）+
# _bind_adaptive_wraplength（把 wraplength 绑到标签自身窗口宽，要求 pack(fill=tk.X)）+
# 占位文案收敛到 _make_quality_placeholder / _make_danmaku_placeholder 两个工厂。
#
# 三层锁：纯函数单测与 AST 源码锁无头可跑（Linux CI 全量执行）；
# 真窗用例需要显示器，无显示环境 skip——与 tests/test_ui_theme.py 的 TestApplyTtk 同一口径，
# 是本文件唯一 skip 面。

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUI_SOURCE = (ROOT / "gui.py").read_text(encoding="utf-8")
GUI_TREE = ast.parse(GUI_SOURCE)

_MARKER = "\n@@WRAP@@ "

# 子进程驱动真实 gui 代码（不在 pytest 进程 import gui：DLR_GUI_PARENT 会跨用例污染 src.logger）。
# compute：纯函数，无窗口；window：真窗验证 fill=X 标签在窄容器自动折行、加宽后 wraplength 增长。
_SCRIPT = r"""
import json
import sys
import time

import tkinter as tk

import customtkinter as ctk

out = {"skipped": None, "ok": False}
try:
    import gui

    req = json.loads(sys.stdin.read())
    if req["call"] == "compute":
        out["result"] = gui._compute_wraplength(req["width"], req["scale"], req.get("margin", 8))
        out["ok"] = True
    elif req["call"] == "should_apply":
        out["result"] = gui._wrap_should_apply(req["current"], req["new"], req["scale_changed"])
        out["ok"] = True
    elif req["call"] == "window":
        # 刻意不调 set_widget_scaling：手动缩放覆盖与 CTk 的系统 DPI 追踪在真窗映射时会互相
        # 触发全量重缩放（实测事件风暴 → update() 永不返回）。系统自身的 DPI 已让
        # get_widget_scaling 返回真实缩放率，设备像素→逻辑值换算由 compute 分支的锚点锁钉死。
        root = ctk.CTk()
        root.geometry("1120x300")
        body = ctk.CTkFrame(root)
        body.pack(fill=tk.X, padx=18)
        b1 = ctk.CTkButton(body, text="start", width=200)
        b1.pack(side=tk.LEFT, padx=(0, 12))
        b2 = ctk.CTkButton(body, text="stop", width=200)
        b2.pack(side=tk.LEFT)
        label = ctk.CTkLabel(body, text=req["text"], font=ctk.CTkFont(size=12), anchor="w", justify="left")
        label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        gui._bind_adaptive_wraplength(label)
        root.update_idletasks()
        root.update()
        # 2026-09-29 卡死修复后写入是防抖的（风暴安静 120ms 才结算），读数前等防抖落地
        time.sleep(0.4)
        root.update()
        narrow_wrap = int(label.cget("wraplength"))
        narrow_req = int(label.winfo_reqwidth())
        narrow_win = int(label.winfo_width())
        root.geometry("1600x300")
        root.update_idletasks()
        root.update()
        time.sleep(0.4)
        root.update()
        wide_wrap = int(label.cget("wraplength"))
        out.update(
            narrow_wrap=narrow_wrap,
            narrow_req=narrow_req,
            narrow_win=narrow_win,
            wide_wrap=wide_wrap,
            clipped_narrow=narrow_req > narrow_win + 1,
            ok=True,
        )
        root.destroy()
    elif req["call"] == "stress":
        # 2026-09-29 卡死回归锁：DPI 反复翻转（用户跨屏拖拽的真实路径，与 check_dpi_scaling
        # 同一回调链）。修复前绑定追逐每次瞬时宽度写 wraplength，几何失效喂进 CTk 重缩放的
        # 递归 idle 泵，队列永不排空（120s 泵不完 = 卡死）；修复后防抖 + 迟滞，必须能排空。
        root = ctk.CTk()
        app = gui.LiveRecorderGUI(root)
        root.geometry("1120x740")
        root.update_idletasks()
        root.update()

        def find_labels(widget, acc):
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    acc.append(child)
                find_labels(child, acc)
            return acc

        targets = {}
        for lb in find_labels(root, []):
            t = str(lb.cget("text"))
            for prefix in ("启动后将调用", "暂无弹幕监控数据", "暂无录制中的直播间", "「切换画质」"):
                if t.startswith(prefix):
                    targets[prefix] = lb

        changes = {k: 0 for k in targets}
        last = {k: 0 for k in targets}

        def make_cb(key, widget):
            def cb(event=None):
                cur = int(widget.cget("wraplength"))
                if cur != last[key]:
                    changes[key] += 1
                    last[key] = cur

            return cb

        for k, lb in targets.items():
            lb.bind("<Configure>", make_cb(k, lb), add="+")

        for s in (1.2, 1.5, 1.2, 1.5, 1.2, 1.5, 1.2, 1.5):
            ctk.set_widget_scaling(s)
            end = time.time() + 0.15
            while time.time() < end:
                root.update()
                time.sleep(0.004)
        out.update(changes=changes, ok=True)
        root.destroy()
    else:
        raise SystemExit("unknown call: " + req["call"])
except tk.TclError as e:
    # 无显示环境（Linux CI 无 X server）：真窗用例跳过；compute 调用不建窗，不受影响
    out["skipped"] = f"{type(e).__name__}: {e}"
except Exception as e:  # noqa: BLE001 - 把异常带回主进程断言
    out["error"] = f"{type(e).__name__}: {e}"
sys.stdout.write("\n@@WRAP@@ " + json.dumps(out, ensure_ascii=True))
"""


def _wrap_call(call: str, **kwargs: Any) -> dict[str, Any]:
    # 结果用带前缀的单行 JSON 回传：CTk/自定义脚本可能向 stdout 混出杂散行，
    # 前缀标记让解析与杂散输出解耦；回传侧 ensure_ascii=True 免受控制台码页影响。
    payload = json.dumps({"call": call, **kwargs}, ensure_ascii=False)
    proc = subprocess.run(
        [sys.executable, "-c", _SCRIPT],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, f"gui subprocess failed: {proc.stderr[-2000:]}"
    assert _MARKER in proc.stdout, f"no result marker in: {proc.stdout[-500:]}"
    result: dict[str, Any] = json.loads(proc.stdout.split(_MARKER, 1)[1])
    return result


def _compute(width: int, scale: float, margin: int = 8) -> int:
    # 经子进程驱动 gui._compute_wraplength 本体（非本地复刻）——测试自实现被测逻辑是假绿
    out = _wrap_call("compute", width=width, scale=scale, margin=margin)
    assert out["ok"], out.get("error")
    return int(out["result"])


class TestComputeWraplength:
    # 锚点：(宽-边距)/缩放率 取整。1584 设备像素在 1.5× 下 ≈ 1050 逻辑像素——
    # 与 2026-09-29 修复探针实测一致，数值固化防止折算公式漂移。
    def test_device_to_logical_conversion(self) -> None:
        assert _compute(1584, 1.5) == 1050
        assert _compute(2008, 1.0) == 2000
        assert _compute(3008, 2.0) == 1500

    def test_floor_at_120(self) -> None:
        # 极窄容器逐字折行也好过 wraplength→0（0 = 不折行 = 回到两侧裁切）
        assert _compute(50, 1.0) == 120
        assert _compute(0, 2.0) == 120

    def test_zero_or_negative_scale_treated_as_identity(self) -> None:
        assert _compute(1008, 0) == 1000
        assert _compute(1008, -1) == 1000

    def test_monotonic_in_width(self) -> None:
        values = [_compute(w, 1.5) for w in (200, 400, 800, 1600)]
        assert values == sorted(values)


def _should_apply(current: int, new: int, scale_changed: bool) -> bool:
    out = _wrap_call("should_apply", current=current, new=new, scale_changed=scale_changed)
    assert out["ok"], out.get("error")
    return bool(out["result"])


class TestWrapShouldApply:
    # 迟滞判据（2026-09-29 卡死修复的纯函数面）：滚动条出现/消失使容器宽 ±~11 逻辑像素，
    # 无迟滞时「折行变高→滚动条翻转→宽度变→再折行」在阈值边界无限互振。

    def test_first_apply_always(self) -> None:
        assert _should_apply(0, 300, False) is True

    def test_small_delta_suppressed(self) -> None:
        assert _should_apply(780, 772, False) is False  # 8 ≤ max(12, 15)
        assert _should_apply(300, 292, False) is False  # 8 ≤ 12

    def test_significant_delta_applies(self) -> None:
        assert _should_apply(780, 760, False) is True  # 20 > 15
        assert _should_apply(300, 287, False) is True  # 13 > 12

    def test_threshold_is_relative_to_value(self) -> None:
        # 大值用 2%（更宽容），小值用 12px 下限——保证同一像素噪声在不同字号下都被吸收
        assert _should_apply(1500, 1490, False) is False  # 10 ≤ 30
        assert _should_apply(1500, 1460, False) is True  # 40 > 30

    def test_scale_change_always_forces(self) -> None:
        # 跨屏拖拽/系统 DPI 调整后换算基准变了，即便值几乎相同也必须重算一次
        assert _should_apply(780, 779, True) is True


class TestSourceLocks:
    def test_bind_helper_defined_once_and_wired_to_four_sites(self) -> None:
        defs = [
            n for n in ast.walk(GUI_TREE) if isinstance(n, ast.FunctionDef) and n.name == "_bind_adaptive_wraplength"
        ]
        assert len(defs) == 1
        calls = [
            n
            for n in ast.walk(GUI_TREE)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_bind_adaptive_wraplength"
        ]
        # 4 个接线点：控制台按钮行提示、画质说明、画质占位工厂、弹幕占位工厂
        assert len(calls) == 4, f"_bind_adaptive_wraplength 接线点应为 4，实际 {len(calls)}"

    def test_binding_is_debounced_hysteresis_and_guarded(self) -> None:
        # 2026-09-29 卡死修复锁：绑定必须 ① 防抖（Configure 风暴期零写入——同步追写会喂进
        # CTk 重缩放的递归 idle 泵，队列永不排空）② 迟滞判据 ③ 销毁竞态 TclError 守卫
        fn = next(
            n for n in ast.walk(GUI_TREE) if isinstance(n, ast.FunctionDef) and n.name == "_bind_adaptive_wraplength"
        )
        src = ast.get_source_segment(GUI_SOURCE, fn)
        assert src, "_bind_adaptive_wraplength 源码段提取失败"
        assert "after_cancel" in src and ".after(" in src, "缺防抖（after_cancel + after）"
        assert "_wrap_should_apply" in src, "缺迟滞判据"
        assert src.count("TclError") >= 2, "缺销毁竞态 TclError 守卫"

    def test_wrap_should_apply_defined_once(self) -> None:
        defs = [n for n in ast.walk(GUI_TREE) if isinstance(n, ast.FunctionDef) and n.name == "_wrap_should_apply"]
        assert len(defs) == 1

    def test_placeholder_text_defined_once_each(self) -> None:
        # 占位文案收敛进唯一工厂：刷新路径重建占位时必须复用工厂，禁止再写一份（曾经 4 处重复）
        for needle in ("暂无录制中的直播间", "暂无弹幕监控数据"):
            assert GUI_SOURCE.count(needle) == 1, f"{needle} 文案须只出现一次（工厂内）"

    def test_no_constant_wraplength_kwargs(self) -> None:
        # 定宽 wraplength（原 wraplength=1000）在窄窗口下重新引入右缘裁切；
        # gui.py 所有 wraplength 赋值必须流经 _bind_adaptive_wraplength 的动态值
        offenders = [
            node
            for node in ast.walk(GUI_TREE)
            if isinstance(node, ast.Call)
            for kw in node.keywords
            if kw.arg == "wraplength" and isinstance(kw.value, ast.Constant)
        ]
        assert not offenders, f"发现定宽 wraplength 调用点: {len(offenders)} 处"

    def test_placeholder_factories_use_fill_and_bind(self) -> None:
        # fill=tk.X 是自适应换行的前提（窗口宽由 packer 分配、与标签自请求解耦）；
        # 工厂丢掉 fill 或绑定会让折行静默失效
        for fn_name in ("_make_quality_placeholder", "_make_danmaku_placeholder"):
            fn = next(n for n in ast.walk(GUI_TREE) if isinstance(n, ast.FunctionDef) and n.name == fn_name)
            src = ast.get_source_segment(GUI_SOURCE, fn)
            assert src, f"{fn_name} 源码段提取失败"
            assert "fill=tk.X" in src, f"{fn_name} 缺 fill=tk.X（自适应折行前提）"
            assert "_bind_adaptive_wraplength" in src, f"{fn_name} 缺自适应绑定"

    def test_placeholder_factories_called_by_build_and_refresh(self) -> None:
        # 初始构建与刷新重建两条路径都必须走工厂——只改构建路径的话，第一轮刷新后裁切复发
        pairs = {
            "_make_quality_placeholder": ("_build_quality_page", "_update_quality_display"),
            "_make_danmaku_placeholder": ("_build_danmaku_page", "_update_danmaku_display"),
        }
        for factory, users in pairs.items():
            for user in users:
                fn = next(n for n in ast.walk(GUI_TREE) if isinstance(n, ast.FunctionDef) and n.name == user)
                src = ast.get_source_segment(GUI_SOURCE, fn)
                assert src and f"self.{factory}(" in src, f"{user} 未复用 {factory}"


class TestRealWindowWrap:
    def test_narrow_wraps_without_clipping_and_widens(self) -> None:
        result = _wrap_call(
            "window",
            text="启动后将调用 main.py 循环监测 URL 配置中的直播间并自动录制",
        )
        if result.get("skipped"):
            pytest.skip(f"无显示环境，跳过真窗用例: {result['skipped']}")
        assert result["ok"], result.get("error")
        assert not result[
            "clipped_narrow"
        ], f"窄容器下标签仍溢出（会两侧裁切）: reqwidth={result['narrow_req']} winfo_width={result['narrow_win']}"
        assert result["narrow_wrap"] >= 120
        # 加宽后 wraplength 必须跟随增长：绑在 <Configure> 上持续自适应，不是一次性初值
        assert (
            result["wide_wrap"] > result["narrow_wrap"]
        ), f"加宽后 wraplength 未增长: narrow={result['narrow_wrap']} wide={result['wide_wrap']}"

    def test_dpi_flip_stress_drains_event_loop_with_bounded_writes(self) -> None:
        # 2026-09-29 卡死回归锁：DPI 反复翻转（用户跨屏拖拽走 check_dpi_scaling 同一回调链）下，
        # 事件循环必须能排空（修复前绑定追逐每次瞬时宽度写 wraplength，几何失效喂进 CTk 重缩放
        # 的递归 idle 泵，update() 永不返回，子进程直接超时）；且 wraplength 写入有界。
        result = _wrap_call("stress")
        if result.get("skipped"):
            pytest.skip(f"无显示环境，跳过真窗用例: {result['skipped']}")
        assert result["ok"], result.get("error")
        changes: dict[str, int] = result["changes"]
        # 防抖 + 迟滞下每次翻转至多结算一次；放宽到 24 防计时抖动，无界互振会远超此界
        assert all(v <= 24 for v in changes.values()), f"wraplength 写入无界（互振回归）: {changes}"
        # 防抖必须在位：四个绑定标签都被压力路径真实触达过
        assert len(changes) == 4, f"压力路径未触达全部绑定标签: {sorted(changes)}"
