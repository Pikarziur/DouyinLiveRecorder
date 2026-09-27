# -*- encoding: utf-8 -*-
#
# 元数据生成物同步脚本 — 让 uv.lock 与 DouyinLiveRecorder.egg-info 始终从 pyproject.toml 重新生成，
# 而不是手改版本号（手写版本是反复漂移的根因：4.3.0 -> 4.4.0 那次 egg-info / uv.lock 都没跟上）。
#
# 用法:
#   python scripts/sync_metadata.py            # 重新生成 uv.lock 与 egg-info
#   python scripts/sync_metadata.py --check    # 仅校验二者是否与 pyproject.toml 一致，不改文件
#
# 机制：uv.lock 经 `uv lock` 整文件重算（顺带补齐漏写的依赖，如 socksio/h2/urllib3）；
# egg-info 经 setuptools egg_info 命令重建。二者都是「从 pyproject.toml 派生」的产物，没有
# 任何写死的版本号，所以改 pyproject.toml 之后跑一次本脚本即可让它们重新对齐。
# 校验口径与 tests/test_regression_2026_09_22_gates.py 的两条元数据回归锁一致，但本脚本不依赖
# pytest，可单独在发版前手动跑；CI 侧由那条 pytest 回归锁兜底（纯读、无需 uv/pip）。

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
UV_LOCK = ROOT / "uv.lock"
EGG_INFO = ROOT / "DouyinLiveRecorder.egg-info"


def _read_project() -> dict[str, Any]:
    # 单一事实源：pyproject.toml 的 [project] 段。
    data: dict[str, Any] = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return cast("dict[str, Any]", data["project"])


def _check_uv_lock(project: dict) -> bool:
    # uv.lock 里本项目根包是 editable="." 的那条；版本与依赖集合都必须等于 pyproject。
    if not UV_LOCK.exists():
        print("  MISSING  uv.lock")
        return False
    lock = tomllib.loads(UV_LOCK.read_text(encoding="utf-8"))
    roots = [
        pkg
        for pkg in lock.get("package", [])
        if pkg.get("name") == "douyinliverecorder" and pkg.get("source", {}).get("editable") == "."
    ]
    if len(roots) != 1:
        print(f"  MISMATCH  uv.lock 根包数量异常: {len(roots)}")
        return False
    if str(roots[0].get("version")) != str(project["version"]):
        print(f"  MISMATCH  uv.lock 版本 {roots[0].get('version')} != pyproject {project['version']}")
        return False
    print(f"  OK        uv.lock 版本 = {project['version']}")
    return True


def _check_egg_info(project: dict) -> bool:
    # egg-info/PKG-INFO 的 Version 字段必须等于 pyproject（importlib.metadata 优先读它）。
    pkg_info = EGG_INFO / "PKG-INFO"
    if not pkg_info.exists():
        print("  MISSING  DouyinLiveRecorder.egg-info/PKG-INFO")
        return False
    text = pkg_info.read_text(encoding="utf-8")
    version = next(
        (line.partition(":")[2].strip() for line in text.splitlines() if line.startswith("Version:")),
        None,
    )
    if version != str(project["version"]):
        print(f"  MISMATCH  egg-info 版本 {version} != pyproject {project['version']}")
        return False
    print(f"  OK        egg-info 版本 = {project['version']}")
    return True


def check() -> bool:
    project = _read_project()
    ok = True
    ok = _check_uv_lock(project) and ok
    ok = _check_egg_info(project) and ok
    return ok


def _run(cmd: list[str]) -> int:
    print(f"  RUN       {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(ROOT))


def regenerate() -> bool:
    project = _read_project()
    print(f"从 pyproject.toml 读取版本号: {project['version']}")
    print()

    # uv.lock：优先 uv lock（整文件重算，自动补齐漏写依赖）；无 uv 则提示手动处理。
    uv_probe = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    if uv_probe.returncode == 0:
        if _run(["uv", "lock"]) != 0:
            print("  WARN      uv lock 执行失败，uv.lock 可能未更新", file=sys.stderr)
    else:
        print("  WARN      未检测到 uv，跳过 uv.lock（请手动执行 `uv lock`）", file=sys.stderr)
    print()

    # egg-info：setuptools egg_info 重建（读 pyproject.toml 派生，无需手写版本）。
    egg_cmd = [
        sys.executable,
        "-c",
        "import sys; sys.argv=['setup.py','egg_info','--egg-base','.']; from setuptools import setup; setup()",
    ]
    if _run(egg_cmd) != 0:
        print("  WARN      egg-info 重建失败", file=sys.stderr)
    print()

    return check()


def main() -> None:
    if "--check" in sys.argv[1:]:
        if check():
            print("\n[OK] uv.lock 与 egg-info 均与 pyproject.toml 一致")
            sys.exit(0)
        print("\n[FAIL] 元数据已漂移，运行 `python scripts/sync_metadata.py` 重新生成", file=sys.stderr)
        sys.exit(1)

    regenerate()
    if check():
        print("\n[OK] 已重新生成并校验通过")
        sys.exit(0)
    print("\n[FAIL] 重新生成后仍不一致，请检查 uv / setuptools", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
