# src/ui_theme.py
# GUI 主题层（阶段3：UI 现代化）：语义 token + 多主题 + ttk 主题注册 + 偏好持久化 + WCAG 对比度自证。
#
# 设计约束（提案 PROPOSAL_2026-09-29_ui-modernization §5.2）：
#   · 全部颜色经由语义槽位引用，任何主题不得绕过槽位直写控件颜色——多套主题由同一组
#     槽位派生，避免「每套主题各写一遍颜色」的漂移；对比度因此可以机检（见 CONTRAST_REQUIREMENTS）。
#   · 槽位清单 = 提案 §5.2 十二槽 + on_primary：深色/高对比主题下主按钮填充是亮蓝，按钮标签
#     需要近黑前景，`surface`（面板底色）在深色主题里兼作按钮前景的语义不成立，故单列一槽。
#     浅色主题 on_primary == surface（#FFFFFF），该槽在浅色下是中性的。
#   · 品牌色沿用现有 Colors 的品牌蓝色相：light 的 primary 取 #4358E8（同色相加深）——
#     原 #4F6DF5 与白色标签对比度实测 4.34:1，低于正文 AA 4.5:1；同 hue 加深后 5.53:1。
#   · 本模块不创建窗口、不依赖显示器：import 期只定义数据与纯函数，Tk 相关工作全部发生在
#     ThemeManager.apply(root) 调用期（无头 Linux CI 可安全 import，`import gui` 链路不受影响）。
#   · 持久化走 config.ini [GUI] gui_theme（键名无 configparser 分隔符 `=` / `:`），
#     写入经 src/web_config.update_or_append_config_line（缺节/缺键补建 + 行级注释保留 + 原子写），
#     刻意不使用 config_io.read_config_value——它写回时持 main.file_update_lock，与录制进程耦合，
#     GUI 进程不该把 [GUI] 键的补写混进录制引擎的锁体系。
from __future__ import annotations

import configparser
import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, cast, final

from src.web_config import update_or_append_config_line

# 语义槽位全集：每套主题必须逐槽给出（tests/test_ui_theme.py 的注册表完整性锁强制）。
TOKEN_NAMES: tuple[str, ...] = (
    "surface",
    "surface_alt",
    "border",
    "on_primary",
    "text",
    "text_muted",
    "primary",
    "primary_hover",
    "success",
    "danger",
    "warning",
    "disabled_bg",
    "disabled_fg",
)

# 主题 id 全集（持久化值即 id 原文，故必须是安全的配置值：无空格无分隔符）。
THEME_IDS: tuple[str, ...] = ("light", "dark", "high_contrast")

# 用户配置缺失/非法时的回退主题。选 dark 而非 light：运行日志与弹幕终端本就是深色底
# （Colors.TERMINAL_BG），dark 主题下与既有视觉的跳变最小。
DEFAULT_THEME = "dark"

# 三套主题的 token 取值。全部取值经 CONTRAST_REQUIREMENTS 机检达标
# （2026-09-29 迭代定稿，迭代脚本已删；tests/test_ui_theme.py 持续回归）。
THEMES: dict[str, dict[str, str]] = {
    "light": {
        "surface": "#FFFFFF",
        "surface_alt": "#F4F6FB",
        "border": "#848DA0",
        "on_primary": "#FFFFFF",
        "text": "#1E293B",
        "text_muted": "#5D6C84",
        "primary": "#4358E8",
        "primary_hover": "#3247C9",
        "success": "#16A34A",
        "danger": "#DC2626",
        "warning": "#C2690A",
        "disabled_bg": "#E2E6EE",
        "disabled_fg": "#6E7686",
    },
    "dark": {
        "surface": "#171A23",
        "surface_alt": "#0F1117",
        "border": "#626C84",
        "on_primary": "#FFFFFF",
        "text": "#E2E8F0",
        "text_muted": "#8B93A7",
        "primary": "#4463F0",
        "primary_hover": "#5068F2",
        "success": "#16A34A",
        "danger": "#DC2626",
        "warning": "#D97706",
        "disabled_bg": "#262B3A",
        "disabled_fg": "#7E8798",
    },
    "high_contrast": {
        "surface": "#000000",
        "surface_alt": "#111111",
        "border": "#FFFFFF",
        "on_primary": "#000000",
        "text": "#FFFFFF",
        "text_muted": "#D0D4DC",
        "primary": "#A9BCFF",
        "primary_hover": "#C3D2FF",
        "success": "#4ADE80",
        "danger": "#FF6B6B",
        "warning": "#FFB224",
        "disabled_bg": "#1F1F1F",
        "disabled_fg": "#A8A8A8",
    },
}

# 对比度契约（机检判据）：(前景槽位, 背景槽位, 最低比值)。
#   4.5 = WCAG 1.4.3 正文 AA（按钮标签、正文、次级文字均按正文计——13px 未达 WCAG「大字」门槛）；
#   3.0 = WCAG 1.4.11 非文本（边框、状态色块、焦点环）+ 禁用态自加压（WCAG 豁免禁用控件，
#         这里仍取 3.0 自证，避免「禁用即随便灰」漂移）。
# 新增槽位/组合时先在此登记，再取色——机检是取色的前置门，不是事后核对。
CONTRAST_REQUIREMENTS: tuple[tuple[str, str, float], ...] = (
    ("text", "surface", 4.5),
    ("text", "surface_alt", 4.5),
    ("text_muted", "surface", 4.5),
    ("text_muted", "surface_alt", 4.5),
    ("on_primary", "primary", 4.5),
    ("on_primary", "primary_hover", 4.5),
    ("primary", "surface", 3.0),
    ("success", "surface", 3.0),
    ("danger", "surface", 3.0),
    ("warning", "surface", 3.0),
    ("success", "surface_alt", 3.0),
    ("danger", "surface_alt", 3.0),
    ("warning", "surface_alt", 3.0),
    ("border", "surface", 3.0),
    ("border", "surface_alt", 3.0),
    ("disabled_fg", "disabled_bg", 3.0),
)

_HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

# 持久化落点：config.ini [GUI] gui_theme（提案假设 #2，用户未要求独立文件）。
GUI_SECTION = "GUI"
THEME_KEY = "gui_theme"


def is_valid_hex(color: str) -> bool:
    # 严格 #RRGGBB：tk 颜色语法还接受 #RGB / 颜色名，这里刻意收窄——token 只允许
    # 六位十六进制，保证对比度计算与 ttk configure 都拿到确定形态。
    return _HEX_PATTERN.match(color) is not None


def _linearize(channel: int) -> float:
    # sRGB → 线性 RGB（WCAG 相对亮度公式的逐通道步骤；0.03928 是 8bit 分段阈值）。
    c = channel / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    # WCAG 2.x 相对亮度：R/G/B 分别按 0.2126/0.7152/0.0722 加权。
    if not is_valid_hex(color):
        raise ValueError(f"非法颜色值（须为 #RRGGBB）: {color!r}")
    raw = color.lstrip("#")
    r = _linearize(int(raw[0:2], 16))
    g = _linearize(int(raw[2:4], 16))
    b = _linearize(int(raw[4:6], 16))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    # WCAG 对比度：(较亮亮度 + 0.05) / (较暗亮度 + 0.05)，值域 [1.0, 21.0]。
    # 0.05 的偏置保证纯黑（亮度 0）参与比较时分母不为零。
    lum_fg = relative_luminance(fg)
    lum_bg = relative_luminance(bg)
    lighter = max(lum_fg, lum_bg)
    darker = min(lum_fg, lum_bg)
    return (lighter + 0.05) / (darker + 0.05)


def load_theme_preference(config_file: str | Path) -> str:
    # 读取 [GUI] gui_theme。返回 "" 表示「未设置」（节/键缺失、值为空、值不在 THEME_IDS），
    # 调用方应回退到外观跟随（CTk appearance mode）而非 DEFAULT_THEME——用户没选过主题时
    # 保持升级前的跟随系统行为，只有显式选择过的偏好才覆盖它。
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(config_file, encoding="utf-8-sig")
    except OSError, configparser.Error:
        # 损坏/不可读的配置按「未设置」处理：主题选择永远不能阻断 GUI 启动
        return ""
    if not parser.has_section(GUI_SECTION):
        return ""
    raw = parser.get(GUI_SECTION, THEME_KEY, fallback="").strip().lower()
    return raw if raw in THEME_IDS else ""


def save_theme_preference(config_file: str | Path, theme_id: str) -> bool:
    # 持久化主题偏好。经 update_or_append_config_line：行级替换优先、缺键/缺节补建，
    # 注释与节顺序保留、原子写。False = 文件不存在等不可写情形，调用方告警但不阻断内存态切换。
    if theme_id not in THEME_IDS:
        raise ValueError(f"未知主题 id: {theme_id!r}（合法值: {THEME_IDS}）")
    return update_or_append_config_line(config_file, GUI_SECTION, THEME_KEY, theme_id)


# ttk 注册主题名前缀与基底主题。基底选 clam：ttk 内置主题里唯一在 Windows/Linux/macOS
# 三平台元素结构一致、且完整支持 configure/map 逐元素上色的主题；aqua/vista/xpnative
# 是平台私有引擎，theme_create 挂上去的配色大多被忽略。
_TTK_THEME_PREFIX = "dlr-"
_TTK_BASE_THEME = "clam"


@final
class ThemeManager:
    # 主题运行时状态：当前主题 id + ttk 主题注册。
    # select/apply 都幂等：select 对相同 id 短路（不重复写配置、不触发下游重绘），
    # apply 对已注册的 ttk 主题名跳过 theme_create（重复创建抛 TclError）。
    def __init__(self) -> None:
        self._theme_id = DEFAULT_THEME

    @property
    def theme_id(self) -> str:
        return self._theme_id

    def tokens(self) -> dict[str, str]:
        # 当前主题的 token 只读视图（拷贝返回，调用方改动不得反灌注册表）。
        return dict(THEMES[self._theme_id])

    def select(self, theme_id: str) -> str:
        # 切换当前主题（内存态）。未知 id 抛 ValueError——调用链里 id 来自 THEME_IDS
        # 白名单（菜单映射 / load_theme_preference），走到这里还是未知值属编程错误，
        # 静默回退会把「显示名映射漂移」藏起来。
        if theme_id not in THEME_IDS:
            raise ValueError(f"未知主题 id: {theme_id!r}（合法值: {THEME_IDS}）")
        if theme_id == self._theme_id:
            # 幂等短路：重复选择同主题不做任何事（含持久化），下游无需自行去重
            return self._theme_id
        self._theme_id = theme_id
        return self._theme_id

    def apply(self, root: tk.Misc) -> str:
        # 把当前主题注册为 ttk 主题并启用，返回 ttk 主题名（"dlr-<id>"）。
        # 幂等：主题名已注册则只切 theme_use；重复 apply 同一主题无害。
        style = ttk.Style(root)
        name = _TTK_THEME_PREFIX + self._theme_id
        if name not in style.theme_names():
            # typeshed 把 settings 收窄成 _ThemeSettingsValue TypedDict；本构造器返回结构等价的
            # 宽松形状（configure: dict[str, object] / map: list[tuple[str, str]]），cast 收敛给存根
            style.theme_create(name, _TTK_BASE_THEME, settings=cast(Any, self._build_ttk_settings()))
        style.theme_use(name)
        return name

    def _build_ttk_settings(self) -> dict[str, dict[str, dict[str, object]]]:
        # 由当前主题 token 派生 ttk 元素配色。三态统一走 map：hover/active/pressed、
        # selected、disabled/readonly——CTk 没有的状态机制正是本次换 ttk 的机制性收益，
        # 新增控件类型时在此登记，禁止在控件创建处散落配色。
        t = THEMES[self._theme_id]
        return {
            # "." 是 ttk 全局兜底：未单独登记的元素从这里继承底色/前景/选区/光标色
            ".": {
                "configure": {
                    "background": t["surface"],
                    "foreground": t["text"],
                    "bordercolor": t["border"],
                    "lightcolor": t["surface_alt"],
                    "darkcolor": t["border"],
                    "troughcolor": t["surface_alt"],
                    "focuscolor": t["primary"],
                    "selectbackground": t["primary"],
                    "selectforeground": t["on_primary"],
                    "insertcolor": t["text"],
                }
            },
            "TFrame": {"configure": {"background": t["surface"]}},
            "TLabel": {"configure": {"background": t["surface"], "foreground": t["text"]}},
            "TButton": {
                "configure": {
                    "background": t["primary"],
                    "foreground": t["on_primary"],
                    "bordercolor": t["primary"],
                    "lightcolor": t["primary"],
                    "darkcolor": t["primary"],
                    "focuscolor": t["on_primary"],
                    "padding": (10, 5),
                },
                "map": {
                    # 悬停与按下共用 hover 深色：clam 的 active 状态同时覆盖鼠标悬停与键盘焦点
                    "background": [
                        ("disabled", t["disabled_bg"]),
                        ("pressed", t["primary_hover"]),
                        ("active", t["primary_hover"]),
                    ],
                    "foreground": [("disabled", t["disabled_fg"])],
                    "bordercolor": [
                        ("disabled", t["disabled_bg"]),
                        ("pressed", t["primary_hover"]),
                        ("active", t["primary_hover"]),
                    ],
                },
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": t["surface_alt"],
                    "foreground": t["text"],
                    "insertcolor": t["text"],
                    "bordercolor": t["border"],
                    "lightcolor": t["surface_alt"],
                    "darkcolor": t["surface_alt"],
                },
                "map": {
                    "fieldbackground": [("disabled", t["disabled_bg"])],
                    "foreground": [("disabled", t["disabled_fg"])],
                    # 聚焦边框升为主色：非文本 3:1 已达标（primary vs surface_alt），
                    # 键盘焦点位置因此可辨（WCAG 2.4.7）
                    "bordercolor": [("focus", t["primary"]), ("disabled", t["disabled_bg"])],
                    "lightcolor": [("focus", t["primary"])],
                    "darkcolor": [("focus", t["primary"])],
                },
            },
            "TCombobox": {
                "configure": {
                    "fieldbackground": t["surface_alt"],
                    "background": t["surface_alt"],
                    "foreground": t["text"],
                    "arrowcolor": t["text"],
                    "bordercolor": t["border"],
                    "lightcolor": t["surface_alt"],
                    "darkcolor": t["surface_alt"],
                },
                "map": {
                    "fieldbackground": [("readonly", t["disabled_bg"]), ("disabled", t["disabled_bg"])],
                    "foreground": [("readonly", t["disabled_fg"]), ("disabled", t["disabled_fg"])],
                    "bordercolor": [("focus", t["primary"]), ("disabled", t["disabled_bg"])],
                },
            },
            "TNotebook": {"configure": {"background": t["surface_alt"], "bordercolor": t["border"]}},
            "TNotebook.Tab": {
                "configure": {"background": t["surface_alt"], "foreground": t["text_muted"], "padding": (12, 6)},
                "map": {
                    "background": [("selected", t["surface"])],
                    "foreground": [("selected", t["text"]), ("active", t["text"])],
                },
            },
            "Treeview": {
                "configure": {
                    "background": t["surface_alt"],
                    "fieldbackground": t["surface_alt"],
                    "foreground": t["text"],
                    "bordercolor": t["border"],
                },
                "map": {
                    # 行选中走 primary 填充 + on_primary 文字（对比度契约已覆盖该对）
                    "background": [("selected", t["primary"])],
                    "foreground": [("selected", t["on_primary"])],
                },
            },
            "Treeview.Heading": {
                "configure": {"background": t["surface"], "foreground": t["text_muted"]},
                "map": {"foreground": [("active", t["text"])], "background": [("active", t["surface"])]},
            },
            "Vertical.TScrollbar": {
                "configure": {
                    "background": t["surface_alt"],
                    "troughcolor": t["surface_alt"],
                    "bordercolor": t["border"],
                    "arrowcolor": t["text_muted"],
                },
                "map": {"background": [("active", t["border"])], "arrowcolor": [("active", t["text"])]},
            },
            "Horizontal.TScrollbar": {
                "configure": {
                    "background": t["surface_alt"],
                    "troughcolor": t["surface_alt"],
                    "bordercolor": t["border"],
                    "arrowcolor": t["text_muted"],
                },
                "map": {"background": [("active", t["border"])], "arrowcolor": [("active", t["text"])]},
            },
            "TCheckbutton": {
                "configure": {"background": t["surface"], "foreground": t["text"]},
                "map": {"foreground": [("disabled", t["disabled_fg"])]},
            },
            "TRadiobutton": {
                "configure": {"background": t["surface"], "foreground": t["text"]},
                "map": {"foreground": [("disabled", t["disabled_fg"])]},
            },
            "TProgressbar": {
                "configure": {
                    "background": t["primary"],
                    "troughcolor": t["surface_alt"],
                    "bordercolor": t["border"],
                    "lightcolor": t["primary"],
                    "darkcolor": t["primary"],
                }
            },
            "TSeparator": {"configure": {"background": t["border"]}},
            "TScale": {
                "configure": {"background": t["surface"], "troughcolor": t["surface_alt"], "bordercolor": t["border"]}
            },
        }
