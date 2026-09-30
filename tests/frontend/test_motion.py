# tests/frontend/test_motion.mjs 的 pytest 驱动入口（M-28，CODE_REVIEW_2026-09-29_2）。
#
# 被驱动的 .mjs 是 web/motion.js（背景粒子 + 滚动入场动效层）的 5 条不变量用例：
# 粒子数边界与移动端/低核数减半、prefers-reduced-motion 命中时完全不创建 canvas、
# 正常模式创建 canvas 并启动单 rAF 循环、destroy() 的完整清理（停循环/断观察器/移除自建
# canvas/清空粒子）、入场元素被加上 reveal 与 is-revealed。
#
# 为什么需要这个包装（M-28 的成因）：全仓此前没有任何 .py 引用过 test_motion.mjs，而
#   ① `node --test <文件>` 只跑被点名的那一个文件，不会顺带发现同级其他 .mjs；
#   ② CI 唯一的前端入口 .github/workflows/ci.yml「Gate frontend tests not skipped」按 node-id
#      点名的是另两条包装（test_frontend_quality_ui / test_frontend_regression_gates）。
# 两个条件叠加 = motion.js 的降级/清理回归锁在正常 CI 里从不执行，等于没有锁。本文件把它
# 接进 pytest（全量收集）与 CI（node 清单）两条回路，缺一条都会重新漂回「游离门禁」。
#
# 子进程驱动一律复用、不重复实现：node --test 的「管道形态挂死 + GBK 码页解码崩溃」两类坑
# （MID-64）已在 tests/test_frontend_quality_ui.py 里沉淀成经过回归锁的 _run_node（输出重定向
# 到临时文件而非管道、超时回收整棵进程树、一律二进制捕获后显式按 UTF-8 解码）与
# _parse_node_summary；_run_node 的 cwd 取的就是 tests/frontend/，与本 .mjs 同目录。直接 import
# 复用可避免出现第二份「改了这一份、忘了那一份」的子进程硬化代码。
#
# Node 缺失时整体 skip（环境限制口径，不是失败），与同目录另两个前端包装保持一致；ci.yml 的
# 「有 skip 即红」判据负责在 CI 上把这种静默消失抓回来（MID-2264）。
from pathlib import Path

import pytest

from tests.test_frontend_quality_ui import _NODE_BIN, _parse_node_summary, _run_node

_FRONTEND_TEST = Path(__file__).parent / "test_motion.mjs"

# 用例条数下限（M-28）：node --test 在收集到 0 个用例时同样退出 0（.mjs 被误改名 / 整块 test()
# 被删都一样绿），只看 returncode 就是假绿。刻意取下限而不是等号——新增动效不变量时不必回头改
# 包装层，但删掉既有用例会立刻变红。当前 .mjs 实跑 5 条。
_EXPECTED_MIN_PASS = 5

pytestmark = pytest.mark.skipif(_NODE_BIN is None, reason="Node.js 运行时不可用，跳过前端动效层用例")


def test_motion_frontend() -> None:
    # skipif 已保证 node 存在；assert 收窄 Optional 供类型检查（mypy / basedpyright）。
    assert _NODE_BIN is not None
    returncode, stdout, stderr = _run_node(_NODE_BIN, ["--test", str(_FRONTEND_TEST)])
    detail = f"前端动效层用例失败（exit {returncode}）:\n{stdout}\n{stderr}"
    assert returncode is not None, detail + "\n（node --test 超时未退出，进程树已尝试回收）"
    assert returncode == 0, detail

    # 「跑到了用例、且用例真的有断言」必须显式核对，口径与另两条前端包装完全一致。
    summary = _parse_node_summary(stdout)
    assert {"tests", "pass", "fail"} <= set(summary), f"未能从 node 输出解析到汇总行:\n{stdout}\n{stderr}"
    assert summary["fail"] == 0, detail
    # skipped 也要判：node 侧 test(..., {skip: true}) 既不红也不绿，是 M-2264 同族的静默消失形态。
    assert summary.get("skipped", 0) == 0, f"存在被跳过的动效用例（降级/清理锁未执行）:\n{stdout}"
    assert summary["pass"] >= _EXPECTED_MIN_PASS, (
        f"node --test 执行的用例数低于下限 {_EXPECTED_MIN_PASS}（包装层未真正驱动 .mjs，"
        f"或 motion 不变量用例被删）: {summary}\n{stdout}"
    )
    assert summary["tests"] >= summary["pass"], f"汇总计数自相矛盾: {summary}"
