# -*- coding: utf-8 -*-
# i18n.tr() 帮手回归：先查表再插值，避免 f-string 在查表前先替换模板。
#
# 旧实现：f"[{record_name}] xxx" 先被 Python 求值为 "[房间A] xxx"，
#         目录里的 msgid 是 "[{record_name}] xxx"，查不到 → 翻译静默退化为原文。
# 新实现：tr("[{record_name}] xxx", record_name=record_name)
#         模板先查表（带占位符的模板原样查），命中后再 .format(**kwargs)。

from types import SimpleNamespace

import i18n


def test_tr_passes_through_when_no_translation() -> None:
    # 未命中目录时按原文格式（恒等映射 + format 二次插值）
    assert i18n.tr("plain text {x}", x=1) == "plain text 1"


def test_tr_with_placeholder_passes_through_correctly() -> None:
    # 含占位符但目录无翻译的模板：仍能正常 format
    assert i18n.tr("[{room}] hello", room="A") == "[A] hello"


def test_tr_with_format_expression_via_kwarg() -> None:
    # f-string 的 {type(e).__name__} 不能直接当 .format 占位符，
    # tr() 强制调用方预求值——这里 type_name=type(e).__name__ 演示等价效果
    try:
        raise ValueError("boom")
    except ValueError as e:
        out = i18n.tr("caught {type_name}: {e}", type_name=type(e).__name__, e=e)
    assert out == "caught ValueError: boom"


def test_tr_missing_kwarg_falls_back_to_template() -> None:
    # MI-23 修复后语义：占位符未传对应 kwarg 时**不再抛异常**，降级为原文模板。
    # 旧测试断言「必须 KeyError」，锁定的正是会导致错误分支二次崩溃的前提：
    # i18n.tr() 的调用点大量位于 except 分支内，而译文是外部可编辑数据（译者可能把
    # {e} 写成 {err}）。二次异常会顶掉原始异常，把「网络失败」升级成崩溃并掩盖真实故障。
    # 现在保证 tr() 永不抛——拼写错误仍可通过「日志里出现未插值的花括号」识别。
    assert i18n.tr("hello {name}") == "hello {name}"


def test_tr_translates_then_formats() -> None:
    # 注入临时目录键后：tr() 翻译命中、占位符按 .format 二次插值
    saved = i18n._tr
    try:
        i18n._tr = lambda template: {
            "Hello {name}, you are {age}": "你好 {name},你 {age} 岁",
        }.get(template, template)
        out = i18n.tr("Hello {name}, you are {age}", name="张三", age=18)
        assert out == "你好 张三,你 18 岁"
    finally:
        i18n._tr = saved


def test_tr_does_not_match_substituted_form() -> None:
    # 反向回归：f-string 求值后用 tr() 查带占位符的目录键必须 miss（恒等回退）
    # ——这正是旧实现的「翻译静默失效」失败模式，新接口通过文档约束规避
    saved = i18n._tr
    try:
        i18n._tr = lambda template: {
            "[{record_name}] template": "已翻译",
        }.get(template, template)
        out_runtime = i18n.tr("[房间A] template")  # 已插值的字符串查模板键
        # 翻译命中的是模板键 "[{record_name}] template"，已插值的「[房间A] template」miss
        assert out_runtime == "[房间A] template"
    finally:
        i18n._tr = saved


# ---------------------------------------------------------------------------
# M-19（2026-09-29）：tr() 的「永不抛」承诺此前只覆盖 KeyError/IndexError/ValueError，
# 漏了**值侧**两类失败——占位符语法完全合法，但实参为 None 时 str.format 抛
# AttributeError（{x.y}）或 TypeError（{x:d}）。Python 3.14.7 实测两者直接穿透 tr()。
# 危害与 MI-23 同一条：tr 的调用点大量位于 except 分支内，二次异常顶掉原始异常，
# 「网络失败」升级成崩溃且真实故障被掩盖。以下用例即该缺口的回归锁。
# 注：conftest 的 _pin_identity_translation 把 _tr 钉成恒等映射，所以「恒等 + 原文
# 也格式化失败 → 返回裸模板」是本组用例的默认路径；需要「译文命中」时按本文件既有
# 惯例临时替换 i18n._tr（走 i18n 自己的引用点，不改翻译机制本身）。
# ---------------------------------------------------------------------------


def test_tr_attribute_error_placeholder_degrades_to_template() -> None:
    # {x.y} 在 x=None 时 .format 抛 AttributeError('NoneType' object has no attribute 'y')：
    # 译文（恒等）与原文两级格式化都会抛，必须落到「返回裸模板」这一层而不是向外抛。
    assert i18n.tr("value {x.y}", x=None) == "value {x.y}"


def test_tr_type_error_format_spec_degrades_to_template() -> None:
    # {x:d} 在 x=None 时 .format 抛 TypeError(unsupported format string passed to
    # NoneType.__format__)：同上，恒等映射下两级都失败 → 裸模板。
    assert i18n.tr("count {x:d}", x=None) == "count {x:d}"


def test_tr_attribute_error_falls_back_to_original_template() -> None:
    # 降级顺序必须保持「先试原文模板」：译文里多出取属性占位符 {a.b}（译者手滑），
    # 原文模板并无该占位符 → 译文格式化抛 AttributeError，原文仍可用 name 正常插值。
    saved = i18n._tr
    try:
        i18n._tr = lambda template: "详情 {a.b} {name}" if template == "detail {name}" else template
        assert i18n.tr("detail {name}", a=None, name="A") == "detail A"
    finally:
        i18n._tr = saved


def test_tr_type_error_falls_back_to_original_template() -> None:
    # 同上一条，只是失败类型换成 TypeError（译文用 {age:d}、调用方传 None）。
    # 这两条一起锁住「AttributeError/TypeError 走的是与 KeyError 完全相同的两级降级」，
    # 而不是被新增的 except 分支直接吞成裸模板。
    saved = i18n._tr
    try:
        i18n._tr = lambda template: "年龄 {age:d}" if template == "age {age}" else template
        assert i18n.tr("age {age}", age=None) == "age None"
    finally:
        i18n._tr = saved


def test_tr_valid_attribute_and_format_spec_still_interpolate() -> None:
    # 反向锁：扩异常元组不得把**合法**的属性占位符/格式符一并吞掉。
    # 传真对象时 {x.y} 照常取值、传 int 时 {x:d} 照常格式化——降级只在异常时发生。
    obj = SimpleNamespace(y=7)
    assert i18n.tr("row {x.y}", x=obj) == "row 7"
    assert i18n.tr("n {x:d}", x=5) == "n 5"


def test_tr_missing_key_degradation_path_unchanged() -> None:
    # 既有降级路径复核（M-19 只加异常类型、不改语义）：缺 kwarg 仍是 KeyError 支路，
    # 返回未插值的原文模板，且与新增的两种异常给出同一形态的输出。
    assert i18n.tr("hello {name}", name="A") == "hello A"
    assert i18n.tr("hello {name}") == "hello {name}"
    assert i18n.tr("hello {name}", name=None) == "hello None"
