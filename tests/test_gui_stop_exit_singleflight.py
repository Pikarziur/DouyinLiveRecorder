# tests/test_gui_stop_exit_singleflight.py — 停止/退出对同一子进程的单飞锁（2026-09-29 审查 M-16）。
#
# 故障形态：gui.py 的「停止录制」（stop_recording → 后台线程，最长 15s+）与「彻底退出」
# （quit_application → _shutdown_and_quit）互不知情，两个线程会对**同一个 pid** 交叉执行
# FreeConsole→AttachConsole→GenerateConsoleCtrlEvent→FreeConsole。控制台附着是**进程全局**
# 状态，交叉时 CTRL_BREAK 可能错投或整个丢失，最坏退化为 taskkill 硬杀 —— 子进程 main.py 的
# safe_exit（atexit 清理其下 ffmpeg）就没机会跑，留下孤儿 ffmpeg 继续录制。
#
# 修复形态：两条路径都收敛到 _stop_child_once 这个唯一入口 ——
#   ① 登记在途停止线程（_stop_inflight），退出时**复用**它（join 完成后再收尾）；
#   ② _console_stop_lock 串行化临界区（锁只由调用方 _stop_child_once 持有，
#      被调的 _send_stop_signal_and_wait 内部一律不加锁 —— AGENTS「持锁层次二选一」）；
#   ③ 拿锁后复核 proc.poll()，进程已退出就不再发第二遍信号。
#
# 判据经**子进程**驱动 gui.py 真实实现（同 test_gui_monitor.py：pytest 进程 import gui 会把
# DLR_GUI_PARENT 注进整个会话）。桩只补「进程/控件替身」与唯一的外部副作用点
# `_send_ctrl_break_to_child`，停止判定与排队逻辑一律走真实代码。
# 无头环境限制：真窗下的按钮禁用/托盘菜单不可点等交互无法实测，本文件锁的是并发语义本身。
#
# 为什么只把 `_send_ctrl_break_to_child` 当作打桩点：它是本链路唯一真正碰操作系统控制台的
# 函数（FreeConsole/AttachConsole/GenerateConsoleCtrlEvent 全在里面）。把它换成记账替身后，
# 被测的「单飞闸门」——线程登记、锁、拿锁后的 proc.poll() 复核——仍然全部走真实代码，
# 这正是 AGENTS「测试不得自实现被测逻辑」所要求的边界：桩的是外部副作用，不是判定本身。
# FakeProc 同样只提供 poll/wait/terminate 三个状态查询：wait 一调即置已退出，等价于
# 「子进程在预算内正常收尾」这条最常见路径；超时强杀分支由 _send_stop_signal_and_wait 自身
# 的既有语义负责，本文件不重复锁（动的是信号核心，不是 M-16 的闸门）。
#
# 四个场景的分工（缺一不可，去掉任意一个都会留下盲区）：
#   A 直调 _stop_child_once 两次 → 只证「闸门 + 锁」本身；
#   B 退出链 _shutdown_and_quit 复用在途停止线程 → 证「退出收尾仍完整、登记被注销」；
#   C 真实入口 stop_recording + quit_application 并发 → 证两条链的登记/注销接线都没漏；
#   D 单独退出 → 反向护栏，闸门不得把无并发场景的正常退出也拦住。

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUI_SOURCE = (ROOT / "gui.py").read_text(encoding="utf-8")
# 载荷锚点：customtkinter/Tk 初始化期会往 stdout 写非受控行，整段 parse 必炸。
# 前置换行是必需的——gui 的导入期打印可能不带结尾换行，若 marker 落在某行中间，
# 「按最后一个换行切」之类的宽松解析会把杂散前缀混进 JSON。父侧只按字节找这个串。
_MARKER = "\n@@WP_E_STOPFLIGHT@@ "

# 四个场景在**同一支子进程**里顺序跑完（并发语义要的是同一份模块级状态：ATTACHES 记账、
# gui._send_ctrl_break_to_child 的替身），每个场景开头都 del 清空那两张表，
# 否则上一场景的附着记录会冒充本场景的结论（例如「只有 1 次附着」其实全是上一轮的）。
# 对 gui 模块级名字的替换全部包在 try/finally 里还原：泄漏出去会波及同会话其它 GUI 用例。
_SCRIPT = r"""
import json
import sys
import threading
import time
import types

import gui

G = gui.LiveRecorderGUI
out = {}


class FakeProc:
    # 只替 subprocess.Popen 的「状态查询」面：poll/wait 的语义按停止链的用法给出。
    def __init__(self, pid):
        self.pid = pid
        self._exited = False
        self.wait_calls = 0

    def poll(self):
        return 0 if self._exited else None

    def wait(self, timeout=None):
        self.wait_calls += 1
        self._exited = True
        return 0

    def terminate(self):
        self._exited = True


class FakeWidget:
    def configure(self, **kwargs):
        return None


def base_stub(pid=4242):
    stub = object.__new__(G)
    stub._process_lock = threading.Lock()
    stub._process = None
    stub._process_pid = None
    stub._running = False
    stub._stopping = False
    stub._quitting = False
    stub._session_id = 7
    stub._stop_inflight = None
    stub._stop_inflight_lock = threading.Lock()
    stub._console_stop_lock = threading.Lock()
    stub._log_lines = []
    stub._log = lambda message, level="info": stub._log_lines.append([message, level])
    stub._post_ui_calls = []
    stub.post_ui = lambda callback: stub._post_ui_calls.append(getattr(callback, "__name__", repr(callback)))
    stub._cleanups = []
    stub._cleanup_zombie_ffmpeg = lambda target_pid: stub._cleanups.append(target_pid)
    stub.start_btn = FakeWidget()
    stub.stop_btn = FakeWidget()
    proc = FakeProc(pid)
    stub._proc = proc
    stub.process = proc
    stub.process_pid = proc.pid
    stub.running = True
    return stub


ATTACHES = []
ATTACH_LOCK = threading.Lock()
# 在途窗口内的交叉附着检测：enter/exit 各记一次，父侧判区间是否重叠。
ATTACH_SPANS = []


def make_attach_spy(sleep_seconds=0.35):
    def _spy(pid):
        thread = threading.current_thread().name
        with ATTACH_LOCK:
            ATTACHES.append([thread, pid])
            enter = time.monotonic()
        time.sleep(sleep_seconds)  # 模拟 FreeConsole/AttachConsole/GenerateCtrlEvent 的实际耗时
        with ATTACH_LOCK:
            ATTACH_SPANS.append([enter, time.monotonic(), thread])
        return True

    return _spy


def _spans_overlap(spans):
    ordered = sorted(spans, key=lambda s: s[0])
    return any(ordered[i][1] > ordered[i + 1][0] for i in range(len(ordered) - 1))


original_ctrl = gui._send_ctrl_break_to_child
try:
    # ─── A：两个线程并发走单飞入口 → 只允许一次控制台附着 ───────
    del ATTACHES[:]
    del ATTACH_SPANS[:]
    gui._send_ctrl_break_to_child = make_attach_spy()
    stub = base_stub()
    worker_a = threading.Thread(target=lambda: G._stop_child_once(stub, stub._proc), name="stop-A")
    stub._stop_inflight = worker_a  # 等价于 stop_recording 的登记（start 前登记）
    worker_a.start()
    time.sleep(0.05)  # 让 A 确定进入临界区
    G._stop_child_once(stub, stub._proc)  # 当前线程扮演「退出」路径
    worker_a.join(timeout=10)
    out["concurrent_once"] = {
        "attaches": list(ATTACHES),
        "overlap": _spans_overlap(ATTACH_SPANS),
        "reuse_logged": any("已有停止流程在途" in line[0] for line in stub._log_lines),
        "wait_calls": stub._proc.wait_calls,
    }

    # ─── B：停止在途时走真实退出链 → 复用而不是二次附着 ──────────
    del ATTACHES[:]
    del ATTACH_SPANS[:]
    gui._send_ctrl_break_to_child = make_attach_spy()
    stub = base_stub()
    stop_thread = threading.Thread(target=lambda: G._stop_child_once(stub, stub._proc), name="stop-B")
    stub._stop_inflight = stop_thread
    stop_thread.start()
    time.sleep(0.05)
    G._shutdown_and_quit(stub)
    stop_thread.join(timeout=10)
    out["quit_reuses_stop"] = {
        "attaches": list(ATTACHES),
        "attach_threads": sorted({row[0] for row in ATTACHES}),
        "overlap": _spans_overlap(ATTACH_SPANS),
        "reuse_logged": any("已有停止流程在途" in line[0] for line in stub._log_lines),
        "cleanups": list(stub._cleanups),
        "finalize_posted": "self._finalize_quit" in str(stub._post_ui_calls) or "_finalize_quit" in str(
            stub._post_ui_calls
        ),
        "running": stub.running,
        "process_cleared": stub.process is None and stub.process_pid is None,
        "inflight_left": stub._stop_inflight is not None and stub._stop_inflight.is_alive(),
    }

    # ─── C：真实入口 stop_recording + quit_application 并发 ───────
    del ATTACHES[:]
    del ATTACH_SPANS[:]
    gui._send_ctrl_break_to_child = make_attach_spy()
    # messagebox 换成浅拷贝替身（改 stdlib/三方模块本体属性会波及全进程，AGENTS 明令）。
    real_messagebox = gui.messagebox
    gui.messagebox = types.SimpleNamespace(
        askokcancel=lambda *args, **kwargs: True,
        showwarning=lambda *args, **kwargs: None,
        showerror=lambda *args, **kwargs: None,
        askyesno=lambda *args, **kwargs: True,
    )
    try:
        stub = base_stub()
        stub_quit = stub  # 两条路径作用在同一个实例（与真实 GUI 一致）
        t1 = threading.Thread(target=lambda: G.stop_recording(stub_quit), name="ui-stop")
        t2 = threading.Thread(target=lambda: G.quit_application(stub_quit), name="ui-quit")
        t1.start()
        time.sleep(0.02)
        t2.start()
        t1.join(timeout=15)
        t2.join(timeout=15)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and (stub._stop_inflight is not None and stub._stop_inflight.is_alive()):
            time.sleep(0.05)
        out["real_entries"] = {
            "attaches": list(ATTACHES),
            "overlap": _spans_overlap(ATTACH_SPANS),
            "cleanups": list(stub._cleanups),
            "stopping_reset": stub._stopping is False,
            "quitting_set": stub._quitting is True,
            "process_cleared": stub.process is None,
            "finalize_posted": "_finalize_quit" in str(stub._post_ui_calls),
            "inflight_cleared": stub._stop_inflight is None or not stub._stop_inflight.is_alive(),
        }
    finally:
        gui.messagebox = real_messagebox

    # ─── D：单独退出（无在途停止）仍要正常发信号 + 注销登记 ───────
    del ATTACHES[:]
    del ATTACH_SPANS[:]
    gui._send_ctrl_break_to_child = make_attach_spy(0.05)
    stub = base_stub()
    worker = threading.Thread(target=lambda: G._shutdown_and_quit(stub), name="quit-only")
    stub._register_stop_worker(worker)
    worker.start()
    worker.join(timeout=10)
    out["quit_alone"] = {
        "attaches": list(ATTACHES),
        "cleanups": list(stub._cleanups),
        "finalize_posted": "_finalize_quit" in str(stub._post_ui_calls),
        "inflight_cleared": stub._stop_inflight is None,
        "process_cleared": stub.process is None,
    }
finally:
    gui._send_ctrl_break_to_child = original_ctrl

sys.stdout.write("\n@@WP_E_STOPFLIGHT@@ " + json.dumps(out, ensure_ascii=False))
"""


def _child_env() -> dict[str, str]:
    # M-31① 同口径：显式钉死 UTF-8，不依赖宿主 shell 恰好带该环境变量。
    # 本文件的日志判据是中文子串（「已有停止流程在途」），中文 Windows（ACP=936）下
    # 子进程若不钉 UTF-8，这些串在 json.dumps(ensure_ascii=False) 里落进 GBK stdout、
    # 父侧按 utf-8 解码即 UnicodeDecodeError——且只在没带 UTF-8 环境变量的机器上复现。
    # 基底只读、绝不写回本进程环境（AGENTS：环境变量一律用 monkeypatch，本进程没有改它的理由）。
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.fixture(scope="module")
def results() -> dict[str, Any]:
    # module 作用域：本文件的判据是**并发时序**，四个场景必须在同一支进程、同一份模块级
    # 记账状态里跑（见 _SCRIPT 上方说明）；按用例分进程会让场景 A/B 的「在途登记」根本不存在。
    # 代价是同会话内场景彼此共享 gui 模块对象，因此脚本里所有临时替换都必须 finally 还原。
    proc = subprocess.run(
        [sys.executable, "-c", _SCRIPT],
        # 脚本不读 stdin，但仍显式给一支空管道：不传 stdin=PIPE 时子进程继承父控制台句柄，
        # 无头/GUI 宿主下继承到的可能是不可用句柄，表现为随机尽早退出。
        input=b"{}",
        capture_output=True,
        # 300s 上限是必需的而非凑数：场景 C 的两个线程各带 15s 的 join 预算，且闸门一旦
        # 失效（例如 _stop_inflight_lock 与 join 形成锁序交叉）就会永久阻塞——超时让本文件
        # 以 TimeoutExpired 失败，好过把整个 pytest 会话挂死。
        timeout=300,
        cwd=str(ROOT),
        env=_child_env(),
    )
    marker = _MARKER.encode("utf-8")
    assert proc.returncode == 0, (
        "stop/exit single-flight subprocess failed: " + proc.stderr.decode("utf-8", errors="replace")[-4000:]
    )
    # 判定一律按字节（AGENTS「探测子进程输出一律按字节比较」）：不传 text=/encoding=，
    # 与宿主码页、子进程控制台语言完全解耦；载荷的 utf-8 编码由上面注入的 PYTHONIOENCODING 保证。
    assert marker in proc.stdout, "no result marker in: " + proc.stdout.decode("utf-8", errors="replace")[-1000:]
    # 与 test_gui_tail_robustness.results 同口径：json.loads 的 Any 不收窄就会一路扩散到
    # 下面每个 case["attaches"] 断言（mypy 在 return 处报 no-any-return）。只加声明、不改行为，
    # 且不用行内 type: ignore 注释（Linux 必要 / Windows 多余 → basedpyright reportUnnecessaryTypeIgnoreComment）。
    return cast(dict[str, Any], json.loads(proc.stdout.split(marker, 1)[1].decode("utf-8")))


def test_concurrent_stop_and_exit_attach_console_once(results: dict[str, Any]) -> None:
    # M-16 的本体判据：两个线程并发操作同一 pid，控制台附着**只能发生一次**。
    # 删掉单飞闸门（退出路径直调 _send_stop_signal_and_wait）时这里会出现 2 条附着记录。
    case = results["concurrent_once"]
    assert len(case["attaches"]) == 1, f"二次附着子进程控制台：{case['attaches']}"
    # 计数为 1 与「区间不交叉」是**两条独立**判据，不能互相替代：
    # 只锁计数的话，「两线程串行但各发一次信号、第二次被 proc.poll() 复核拦下」也会是 1 次
    # 真实附着——那种实现仍然正确，但 overlap 判据要锁的是「不存在同时改进程全局状态的窗口」，
    # 它是「有没有锁」的直接证据，计数只是「锁是否有效」的间接证据。
    assert case["overlap"] is False, f"控制台附着区间交叉（进程全局状态被两线程同改）：{case}"
    # 复用要留下可见痕迹：只有 join 语义、没有任何日志的实现行为正确但不可诊断，
    # 用户视角是「点了退出但界面十几秒没反应」。这条把「必须说明在等什么」钉住。
    assert case["reuse_logged"] is True, "未复用正在进行的停止线程（应等待其完成后再收尾）"
    # wait_calls 是 FakeProc 的记账：停止核心（proc.wait）只能被跑一遍。
    # 这条与 attaches 计数一起构成「二次停止」的双向证据——附着替身只覆盖 win32 分支，
    # 万一某次改动把 Linux SIGINT 分支也接进同一入口，wait 记账仍能独立抓到重复执行。
    assert case["wait_calls"] == 1, f"停止链被跑了两遍：{case}"


def test_shutdown_and_quit_reuses_inflight_stop_worker(results: dict[str, Any]) -> None:
    # 场景 B 与 A 的差别是**入口**：这里退出走真实的 _shutdown_and_quit，而不是直调闸门。
    # A 过了不代表 B 过——B 才证明「退出链在复用停止线程之后，自己的收尾一步没少」。
    case = results["quit_reuses_stop"]
    assert len(case["attaches"]) == 1, f"退出路径对同一 pid 二次附着：{case['attaches']}"
    # 附着必须发生在**在途停止线程**上，而不是退出线程：闸门若只加锁不做复用，
    # 计数同样是 1（退出线程等锁后复核 poll() 发现已退出、于是根本不再附着），
    # 但那属于「靠复核兜底」而非「复用」——线程名这一维才是 reuse 语义的直接证据。
    assert case["attach_threads"] == ["stop-B"], f"附着发生在错误的线程上：{case['attach_threads']}"
    assert case["reuse_logged"] is True
    # 退出收尾仍必须完整：兜底清理按**已捕获的 pid** 调用一次、UI 收尾已投递、状态已复位。
    # child_pid 必须在停链之前捕获：_stop_child_once 会把 self.process 清成 None，
    # 之后才读到 None 的话 _cleanup_zombie_ffmpeg 直接空转，孤儿 ffmpeg 又回来了。
    assert case["cleanups"] == [4242], case["cleanups"]
    assert case["finalize_posted"] is True
    assert case["running"] is False
    assert case["process_cleared"] is True
    # 注销必须在无条件路径上（finally）：漏掉不会让本轮退出出错，只会让**下一次**停止/退出
    # 白等一次 join 预算——即典型的「第一次没事、以后越来越慢」，行为锁很难抓到，故显式断言。
    assert case["inflight_left"] is False, "在途登记未注销：后续停止/退出会白等一次 join 预算"


def test_real_entries_serialize_stop_and_quit(results: dict[str, Any]) -> None:
    # 走真实入口 stop_recording + quit_application（messagebox/按钮为替身）。
    # 这一层才证明「登记时机」的接线没漏：两条链各自都要在 start() 之前登记在途线程，
    # A/B 场景是手工赋值 stub._stop_inflight 模拟登记的，绕过了真实登记调用点。
    case = results["real_entries"]
    assert len(case["attaches"]) == 1, f"真实两入口并发时二次附着：{case['attaches']}"
    assert case["overlap"] is False
    assert case["stopping_reset"] is True, "_stopping 必须无条件复位（MID-56 的约束不被本次改动打破）"
    assert case["quitting_set"] is True
    assert case["process_cleared"] is True
    assert case["finalize_posted"] is True
    # 兜底清理必须被调用一次；pid 取值取决于哪条路径先收尾——停止链先跑完时
    # quit 读到的 self.process 已是 None（此时也确实无需再发信号），两种都算通过。
    # 这里刻意不钉死是哪一种：两入口的先后是真并发决定的，钉死就等于要求脚本再造一个
    # 同步点，而那个同步点在生产代码里并不存在——会造出「只有测试里成立」的假时序。
    assert len(case["cleanups"]) == 1, case["cleanups"]
    assert case["cleanups"][0] in (4242, None), case["cleanups"]
    # 同样不钉线程名：真实两入口下谁先登记谁就是复用方，两种都属正确行为。
    assert case["inflight_cleared"] is True


def test_quit_without_inflight_stop_still_signals_child(results: dict[str, Any]) -> None:
    # 反向护栏：单飞闸门不得把「没有并发」的正常退出也拦住。
    # 前三条场景全是「有对端」的正向收敛，只看它们的话，把闸门写成「一律跳过停止」
    # 也能让 A/B/C 同时变绿（附着 0 次会被 len==1 抓到，但 wait/清理缺失必须单独锁）。
    # 本场景 D 的专属形态：登记的在途线程**就是当前线程自己**，
    # _current_stop_worker 若只判 is_alive 而不排除 current_thread()，退出会 join 自己→死锁。
    case = results["quit_alone"]
    assert len(case["attaches"]) == 1, case["attaches"]
    assert case["cleanups"] == [4242]
    assert case["finalize_posted"] is True
    assert case["inflight_cleared"] is True
    assert case["process_cleared"] is True


# ─── 结构锁：调用点唯一 + 锁的持有层次只有一处 ────────────────


def test_stop_signal_has_exactly_one_guarded_call_site() -> None:
    # _send_stop_signal_and_wait 只允许由 _stop_child_once 调用（AGENTS：改锁层次必须
    # grep 全部调用点）。第二个调用点就是「绕开闸门」的形态，静态即红。
    # 为什么要有这条 AST 锁而不是只靠 A/B/C 的行为锁：新增一个绕过闸门的调用点
    # （例如「停止中排队启动」之类的新功能直接调核心）在现有场景里根本不会被执行到，
    # 三条行为锁会全体保持绿色——只有静态枚举能看见「多了一处没受闸的调用」。
    tree = ast.parse(GUI_SOURCE)
    sites: list[tuple[int, str]] = []
    for fn in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
        for call in ast.walk(fn):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
                if call.func.attr == "_send_stop_signal_and_wait":
                    sites.append((call.lineno, fn.name))
    assert sites and all(name == "_stop_child_once" for _, name in sites), f"出现未受闸的停止调用点：{sites}"

    guarded = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_stop_child_once")
    locks = [
        n
        for n in ast.walk(guarded)
        if isinstance(n, ast.With)
        and any(
            isinstance(item.context_expr, ast.Attribute) and item.context_expr.attr == "_console_stop_lock"
            for item in n.items
        )
    ]
    # 必须锁「_stop_child_once 里出现 with self._console_stop_lock」这一具体形态：
    # 只靠 A 场景的 overlap 判据，无法区分「有锁」与「恰好没撞上」（见上一条用例的说明）。
    assert locks, "_stop_child_once 必须自行持有 _console_stop_lock（锁层次唯一处）"

    # 被调方不得再加锁：否则「调用方持锁 + 内部自持锁」两套并存 = AGENTS 记过的自死锁形态。
    # 反向也要锁死，是因为 thread 版 Lock 非重入：一旦 _send_stop_signal_and_wait 内补上
    # 同名锁，症状是「点退出后界面再也不响应、且不报任何错」——正是 web_api
    # _purge_expired_tokens 那次自死锁事故的同一征兆，必须在静态层拦住而不是等运行期发现。
    inner = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_send_stop_signal_and_wait")
    # 判据取「with 里出现任意 *_lock 属性」而非只认 _console_stop_lock：
    # _process_lock / _stop_inflight_lock 加进来同样会与外层形成锁序交叉（登记方持锁去 join），
    # 那类故障不体现在本文件的四个场景里，只能靠这条放宽的静态约束兜住。
    assert not any(
        isinstance(node, ast.With)
        and any(
            isinstance(item.context_expr, ast.Attribute) and item.context_expr.attr.endswith("_lock")
            for item in node.items
        )
        for node in ast.walk(inner)
    ), "_send_stop_signal_and_wait 内部不得再持锁"


def test_stop_worker_registered_before_thread_start() -> None:
    # 登记必须先于 start()：否则「刚点停止、线程尚未活着」的窗口里退出路径看不见在途停止。
    # 这是本文件唯一能锁住「登记时机」的判据——时序窗口只有几微秒，行为测试无论跑多少遍
    # 都可能一直落在窗口外（表现为「偶发红」），故改为静态比行号。
    tree = ast.parse(GUI_SOURCE)
    for name in ("stop_recording", "quit_application"):
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
        register_line = next(
            (
                node.lineno
                for node in ast.walk(fn)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "_register_stop_worker"
            ),
            None,
        )
        # start() 的枚举故意放宽成「任意 .start()」：本函数内唯一的 start() 就是工作线程启动，
        # 若将来出现第二个（如弹幕/托盘）宁可让本条误红、由人确认，也不可漏红——
        # 误红成本是一次人工核对，漏红成本是 M-16 的登记时机约束静默消失。
        start_line = next(
            (
                node.lineno
                for node in ast.walk(fn)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "start"
            ),
            None,
        )
        assert register_line is not None, f"{name} 未登记在途停止线程"
        assert start_line is None or register_line < start_line, f"{name} 的登记晚于 start()"
