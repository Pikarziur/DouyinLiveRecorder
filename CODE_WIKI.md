# DouyinLiveRecorder 项目架构文档

简体中文  |  [**English**](CODE_WIKI_EN.md)

## 目录

- [文档统计与索引](#文档统计与索引)
- [项目概述](#项目概述)
  - [项目基本信息](#项目基本信息)
  - [功能特性](#功能特性)
  - [已支持平台](#已支持平台)
  - [画质代码对照](#画质代码对照)
  - [技术栈](#技术栈)
- [系统架构](#系统架构)
- [目录结构](#目录结构)
- [核心模块详解](#核心模块详解)
- [关键类与函数](#关键类与函数)
- [依赖关系](#依赖关系)
- [配置文件说明](#配置文件说明)
- [运行方式](#运行方式)
- [打包与发布](#打包与发布)
- [设计模式](#设计模式)
- [常见问题排查](#常见问题排查)
- [贡献指南](#贡献指南)
- [更新日志](#更新日志)

## 文档统计与索引

> 本节由对**工作空间内所有 `*.md` 文件**的统计分析归纳而来（初版生成于 2026-08-09，2026-09-20 复核刷新，2026-09-27 随文档体积整理复算，2026-09-28 随版本同步与更新日志拆分归档两次复算）。
> **计数必须可复算**：下方数字是 2026-09-28 用取数命令得到的，命令一并写在这里，不复算即视为过期——
> `python -c "import pathlib; sk={'.git','.venv','node_modules','__pycache__','.mypy_cache','.pytest_cache'}; p=[x for x in pathlib.Path('.').rglob('*.md') if not (set(x.parts) & sk)]; print(len(p))"`

### 统计概览

排除 `.git/`/`.venv/`/`node_modules/` 后，工作空间共 **106** 个 Markdown 文件（2026-09-28 随更新日志拆分归档复算；较同日上一读数 101 增加 5：新落的 4 份 `docs/changelog/` 归档卷 + 1 份 harness 会话报告），按来源与维护方式分为七类：

| 分类 | 路径 | 数量 | 性质 | 是否手工维护 |
| --- | --- | --- | --- | --- |
| 项目根文档（事实来源） | `AGENTS.md` + 中英成对的 `README` / `CODE_WIKI` | 5 | 事实来源（source of truth，中英双语文档各成对） | ✅ 是 |
| 架构参考子文档 | `docs/agent-reference/**` | 6 | 从根文档外迁的**纯参考性长段**：目录树、一次性实测读数、会话经验、锁分类口径、更新日志的文件清单附录 | ✅ 是 |
| 一次性审查报告 | `docs/worklog/*.md` | 9 | 历史审查/诊断/提案产出：`CODE_REVIEW_2026-09-17`（AGENTS 约定评审）/`-09-18`/`-09-20`/`-09-21`/`-09-22`/`-09-22_1`/`-09-22_2` + `DIAGNOSIS_2026-09-23_*` + `PROPOSAL_2026-09-22_*`；原散在仓库根目录，现归档于此 | ❌ 历史产物 |
| 变更日志归档 | `docs/changelog/**` | 4 | **2026-09-28 新增**：根文档更新日志按发布周期滚动归档的历史条目卷（`README` / `CODE_WIKI` 中英各两卷）；条目逐字保留，只增不改 | ✅ 是 |
| 本地工具生成文档 | `.qoder/**` | 1 | 原 `.qoder/repowiki/**` 的 302 份 AI 生成英文知识库已于 2026-09-20 复核时确认不在工作区；现存 1 份为 harness 实践会话报告 | ❌ 自动生成 |
| 工作区记忆 | `.workbuddy/**` | 66 | 项目级持久记忆（`memory/` 53 份）+ 历次文档整理的 `docold/`/`docnew/`/`docopt/` 快照（各 4 份）+ 1 份质量报告 | ❌ 本地项目数据 |
| 历史记忆 | `.codebuddy/memory/**` | 14 | 旧版 agent 记忆（遗留） | ❌ 缓存 |
| CI 附带说明 | `.github/**/*.md` | 1 | workflow/issue 模板随附的说明文档 | ✅ 是 |

**结论**：真正由人工维护、应作为改动来源的文档是仓库根目录的 **5 个**（`AGENTS.md` 与中英成对的 `README` / `CODE_WIKI`）加上 `docs/agent-reference/` 的参考子文档与 `docs/changelog/` 的滚动归档卷；`docs/worklog/` 下的审查报告属历史产物，`.workbuddy/` 是不可删除的项目级持久数据，其余为 AI 生成衍生文档或旧版本地缓存，不应合并进本文档，以免引入与代码不同步的冗余内容。（统计快照初版生成于 2026-08-09；根文档数于 2026-08-28 随中英双语文档补齐更新为 5；2026-09-20 复核刷新；2026-09-27 起改为「取数命令 + 读数时刻」口径；2026-09-28 实测为 106）

### 根文档索引

| 文件 | 角色 | 主要内容 |
| --- | --- | --- |
| `AGENTS.md` | 编码代理约定 | 版本号单一事实源（`pyproject.toml`）、代码风格（black / isort / mypy）、项目结构、依赖/测试/构建命令、关键约定 |
| `README.md` | 用户/开发者说明 | 功能特性、已支持平台（51 个）、快速开始、配置说明、使用说明、Docker 部署、开发指南、FAQ、更新日志 |
| `CODE_WIKI.md` | 项目架构文档（本文档） | 模块详解、依赖关系、设计模式、常见问题排查、贡献指南、更新日志 |
| `README_EN.md` | 用户/开发者说明（英文） | `README.md` 的英文对应版（2026-08-24 新增，与中文版结构对齐） |
| `CODE_WIKI_EN.md` | 项目架构文档（英文） | 本文档的英文对应版（2026-08-24 新增，条目与中文版一一对应） |

> 五份文档职责互补：改动平台支持/配置项时须同步更新 `README.md` 与本文档；工程约定以 `AGENTS.md` 为准；`README_EN.md` / `CODE_WIKI_EN.md` 随对应中文版同步更新。

### 参考子文档索引（`docs/agent-reference/`）

> 这里是「从根文档外迁的纯参考性长段」的落点，判定口径见 `AGENTS.md` 头部：约束句留根文件，佐证读数与清单外迁。

| 文件 | 内容 | 外迁自 |
| --- | --- | --- |
| `project-structure.md` | 完整目录树 | `AGENTS.md`「项目结构」 |
| `measured-evidence.md` | 一次性实测读数（探针提速 / keepalive / 虎牙选档 / 斗鱼钳制 / 发布链体积） | `AGENTS.md` 坑条目末尾的长段读数 |
| `session-learnings.md` | 会话经验双轨记录（完成定义第 6 步） | `.workbuddy/memory/*.md` |
| `lock-classification.md` | 锁的可重入性分类口径 | `AGENTS.md`「已知坑」 |
| `changelog-file-inventories.md` | **2026-09-27 新增**：本文档更新日志里 41 个「涉及文件（按模块分类）」清单块的逐字原文；原处保留小节标题 + 一行指针 | 本文档更新日志 |
| `changelog-file-inventories-en.md` | 同上条目的英文对应版（32 个清单块），对应 `CODE_WIKI_EN.md` | `CODE_WIKI_EN.md` 更新日志 |

### 变更日志归档索引（`docs/changelog/`）

> **2026-09-28 新增，与上一节的分工不同**：`docs/agent-reference/` 放「从根文档抽走的参考长段」，本目录放「按发布周期滚走的完整历史条目」。
> 滚动规则：根文档只保留**当前发布周期**（本文档）或**最近三个正式发布**（`README`）的条目，其余整卷迁入归档；新条目写入根文档后，超出窗口的最旧条目随即追加到对应归档卷尾部。
> 归档卷**只增不改**：条目正文逐字保留，仅对上一轮粗剪留下的行尾 `…` / 句中截断按 `.workbuddy/docold` 基线做逐行前缀回补（各卷卷首写明口径）。

| 文件 | 内容 | 迁出自 |
| --- | --- | --- |
| `code-wiki-history-zh.md` | 本文档更新日志的 164 条历史条目（2026-05-17 ~ 2026-09-24） | `CODE_WIKI.md`「更新日志」 |
| `code-wiki-history-en.md` | 同上条目的英文对应版（164 条，与中文版一一对应） | `CODE_WIKI_EN.md`「Changelog」 |
| `release-notes-history-zh.md` | `README.md` 的 17 条早期发布说明（v4.0.0 ~ v4.0.9.4，2024-07-13 ~ 2026-09-06） | `README.md`「更新日志」 |
| `release-notes-history-en.md` | 同上条目的英文对应版（17 条） | `README_EN.md`「Changelog」 |

## 项目概述

### 项目基本信息

- **项目名称**: DouyinLiveRecorder (抖音直播录制器)
- **版本**: 4.4.0
- **作者**: Hmily
- **开源协议**: MIT
- **项目地址**: [GitHub](https://github.com/ihmily/DouyinLiveRecorder)

### 功能特性

- ✅ 支持 60+ 个直播平台（抖音、TikTok、YouTube、快手、虎牙、斗鱼、B站、小红书等）
- ✅ 循环值守直播状态，开播自动录制，断播自动停止
- ✅ 多种视频格式输出：TS、MKV、FLV、MP4、MP3、M4A
- ✅ 命令行 + GUI + Web 管理面板三模式运行
- ✅ 多平台消息推送：钉钉、微信、邮箱、TG、Bark、NTFY、PushPlus
- ✅ Docker 容器化部署
- ✅ 国际化支持（简体中文 / English (US) / English (UK) / 繁體中文）
- ✅ 灵活配置：画质选择、分段录制、自定义保存路径等
- ✅ 实际画质回采与降级告警（支持抖音、TikTok、快手、虎牙、斗鱼、B站、网易CC）
- ✅ Web 安全：Token 认证、路径穿越防护、敏感配置脱敏

### 已支持平台

归纳自 `README.md`，当前已列出 **51** 个平台（README 对外标称 60+，含持续添加中的平台）：

**国内站点（37 个）**：抖音 | 快手 | 虎牙 | 斗鱼 | YY | B站 | 小红书 | bigo | blued | 网易CC | 千度热播 | 猫耳FM | Look直播 | TwitCasting | 百度 | 微博 | 酷狗 | 花椒 | 流星 | Acfun | 畅聊 | 映客 | 音播 | 知乎 | 嗨秀 | VV星球 | 17Live | 浪Live | 飘飘 | 六间房 | 乐嗨 | 花猫 | 淘宝 | 京东 | 咪咕 | 连接 | 来秀

**海外站点（14 个）**：TikTok | SOOP(原AfreecaTV) | PandaTV | WinkTV | TTingLive(原Flextv) | PopkonTV | TwitchTV | LiveMe | ShowRoom | CHZZK | Shopee | YouTube | Faceit | Picarto

> 各平台流解析函数位于 `src/stream.py`、数据获取函数位于 `src/spider.py`；新增平台见「贡献指南 → 添加新平台支持」。

### 画质代码对照

录制画质以代码表示，对应中文名与说明如下（配置项 `原画|超清|高清|标清|流畅` 即映射到该表）：

| 画质代码 | 中文名 | 说明 |
| --- | --- | --- |
| OD | 原画 | Original Definition，最高画质 |
| BD | 蓝光 | Blu-ray，超高清 |
| UHD | 超清 | Ultra HD |
| HD | 高清 | High Definition |
| SD | 标清 | Standard Definition |
| LD | 流畅 | Low Definition，最低画质 |

支持实际画质回采与降级告警的平台：抖音、TikTok、快手、虎牙、斗鱼、B站、网易CC。当平台实际下发画质低于设置画质时，自动告警并标记。

### 技术栈

| 技术 | 用途 |
| --- | --- |
| Python 3.14+ | 核心编程语言 |
| asyncio + httpx | 异步网络请求 |
| asyncio | 异步装饰器支持 |
| FFmpeg | 视频录制与转码 |
| Node.js + exejs/PyExecJS | 运行 JavaScript 签名算法（exejs 优先，PyExecJS 回退） |
| Loguru | 结构化日志 |
| CustomTkinter + pystray + Pillow | GUI 图形界面与系统托盘 |
| FastAPI + uvicorn | Web 管理面板后端 |
| HTML + CSS + JavaScript | Web 管理面板前端 |
| Docker | 容器化部署 |
| gettext (msgfmt) | 国际化翻译编译 |
| mypy | 静态类型检查（`--strict` 模式，`disallow_untyped_defs = true`） |
| pyflakes | 静态代码检查 |
| websockets | 弹幕 WebSocket 传输层（`src/ws_client.py`，各平台弹幕共用） |
| protobuf | 抖音弹幕协议解码（`src/proto/douyin_pb2`，protoc 生成模块） |
| brotli | B站弹幕解压（protover=3 需 brotli 解压） |

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                                │
├──────────────────┬──────────────────────┬───────────────────────┤
│ 命令行 (main.py) │ GUI 图形界面 (gui.py)│ Web 面板 (web.py)     │
│                  │                      │ └ src/web_api.py      │
│                  │                      │ └ web/ (前端静态资源)  │
└──────────────────┴──────────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        核心业务层                                │
├──────────────────────┬─────────────────────┬────────────────────┤
│  直播间管理 (room.py)│  数据爬虫 (spider.py)│  流解析 (stream.py)│
├──────────────────────┴─────────────────────┴────────────────────┤
│                    FFmpeg 录制进程管理                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层                                │
├──────────────────────┬─────────────────────┬────────────────────┤
│  日志 (logger.py)  │  工具 (utils.py)  │  代理 (proxy.py) │
├──────────────────────┴─────────────────────┴────────────────────┤
│                    配置管理 + 消息推送 (msg_push.py)             │
└─────────────────────────────────────────────────────────────────┘
```

### 工作流程

1. **配置解析阶段**
   - 读取 `config/config.ini` 主配置
   - 读取 `config/URL_config.ini` 直播间列表
   - 初始化 Node.js 环境和 FFmpeg 路径
2. **直播检测阶段**
   - 使用异步任务并发检测多个直播间
   - 各平台独立的 API 调用与签名算法
   - 动态调整并发数以避免限流
3. **流地址获取阶段**
   - 调用各平台的直播流 API
   - 根据配置选择不同画质（原画/超清/高清/标清/流畅）
   - 回采平台实际下发的画质（`actual_quality`）与可用档位（`available_qualities`）
   - 验证流地址可用性
4. **录制执行阶段**
   - 启动 FFmpeg 子进程
   - 实时监控录制状态
   - 记录实际画质，画质降级时输出告警日志
   - 支持分段录制
   - 支持转码为 MP4
5. **状态通知阶段**
   - 开播/关播事件触发
   - 调用配置的消息推送渠道
   - 记录日志

## 目录结构

```
DouyinLiveRecorder/
├── config/                              # 配置文件目录
│   ├── config.ini                      # 主配置文件
│   └── URL_config.ini                  # 直播间地址列表
├── src/                                 # 核心源码包
│   ├── __init__.py                     # 包初始化 + Node.js 环境配置 + 弹幕注册表/工厂（get_danmaku_class / get_danmaku_collector）
│   ├── spider.py                       # 直播数据爬虫（60+ 平台）
│   ├── stream.py                       # 直播流地址解析（含画质回采）
│   ├── room.py                         # 直播间信息解析
│   ├── utils.py                        # 工具函数库
│   ├── logger.py                       # Loguru 日志配置
│   ├── proxy.py                        # 代理检测
│   ├── ab_sign.py                      # 抖音签名算法 (A-Bogus)
│   ├── node_install.py                # Node.js 自动安装/初始化
│   ├── ffmpeg_master_download.py       # FFmpeg master 构建下载器（按平台/架构拉取 + 校验，含挑战页识别与 TOFU）
│   ├── ttwid.py                        # 抖音访客 ttwid 获取
│   ├── web_api.py                      # Web 管理面板 FastAPI 应用
│   ├── web_config.py                   # Web 面板配置读写（不依赖 FastAPI）
│   ├── web_tray.py                     # Web 模式系统托盘（Windows 最小化到托盘）
│   ├── http_config.py                  # HTTP 客户端共享运行时配置（SSL 验证开关）
│   ├── async_http.py                   # 异步 HTTP 客户端 (httpx)
│   ├── sync_http.py                    # 同步 HTTP 客户端
│   ├── javascript/                     # JavaScript 签名脚本
│   │   ├── crypto-js.min.js            # 加密库
│   │   ├── x-bogus.js                  # 抖音 X-Bogus 签名
│   │   ├── haixiu.js                   # 嗨秀签名
│   │   ├── liveme.js                   # LiveMe 签名
│   │   └── migu.js                     # 咪咕签名
│   ├── ffmpeg_install.py                # FFmpeg 安装脚本
│   ├── ffmpeg_proc.py                   # FFmpeg 进程注册/注销/终止/清理（抽离自 main.py）
│   ├── video_postprocess.py             # 视频后处理：分段/转码/字幕（抽离自 main.py）
│   ├── stream_select.py                 # 流地址选择/校验/画质码/抖音限速（抽离自 main.py）
│   ├── notify.py                        # 推送/脚本/成功失败计数/并发调节（抽离自 main.py）
│   ├── scheduler.py                     # 并发调度中枢（自适应容量 + 按平台熔断 + 可运行时调容信号量）
│   ├── recorder_status.py               # 录制状态快照与展示（抽离自 main.py）
│   ├── config_io.py                     # 配置读写/安全数值转换/备份（抽离自 main.py）
│   ├── config_bool.py                   # 布尔配置解析（是/否 与 true/false/1/0/yes/no 等价，零依赖模块）
│   ├── base.py                          # 弹幕基类与数据结构（DanmakuBase / DanmakuMessage / DanmakuMessageType）
│   ├── collector.py                     # 弹幕采集器（线程化包装 DanmakuBase，落 SRT + 上报监控枢纽）
│   ├── cookie_cache.py                  # 按 URL 的访客 Cookie 进程内缓存（防并发重复请求触发风控）
│   ├── danmaku_monitor.py               # 弹幕监控枢纽（进程单例，内存快照 + JSONL 边车）
│   ├── srt_writer.py                    # SRT 字幕分段写入（时间轴对齐 ffmpeg segment）
│   ├── ws_client.py                     # 弹幕 WebSocket 传输层（各平台弹幕共用，proxy=None 直连）
│   ├── log_archive.py                   # 运行日志归档（停止录制流程收尾：四日志按时间戳改名）
│   ├── platforms/                       # 各平台弹幕客户端：Douyin/Douyu/Huya/Bilibili/Twitch + 私有签名 _tars/_xbogus
│   └── proto/                           # 抖音弹幕 protobuf（douyin.proto + 生成的 douyin_pb2）
├── web/                                 # Web 管理面板前端
│   ├── index.html                      # 单页应用入口
│   ├── app.js                          # 前端逻辑（API 调用、SSE、渲染）
│   └── style.css                       # 样式表（主题、响应式）
├── i18n/                                # 国际化翻译目录（多语言多格式）
│   ├── zh_CN/LC_MESSAGES/
│   │   ├── zh_CN.po                   # 简体中文翻译源（gettext）
│   │   └── zh_CN.mo                   # 编译后的翻译（运行时必需，随仓库/镜像分发）
│   ├── en_US.json                     # 英语（美国）目录（JSON 格式）
│   ├── en_GB.json                     # 英语（英国）目录（JSON 格式）
│   └── zh_TW.yaml                     # 繁体中文目录（YAML 格式）
├── typings/                             # 第三方库类型存根（仅静态检查用）
├── ffmpeg/                              # FFmpeg 二进制目录（Windows，git 忽略 exe）
├── node/                                # Node.js 二进制目录（Windows，git 忽略）
├── main.py                              # 命令行入口
├── gui.py                               # GUI 图形界面入口（CustomTkinter）
├── web.py                               # Web 管理面板入口
├── i18n.py                              # 国际化实现（print 翻译包装）
├── msg_push.py                          # 消息推送模块
├── index.html                           # 独立 M3U8/FLV 播放器页面
├── StopRecording.vbs                    # Windows 停止录制脚本
├── build_exe.py                         # PyInstaller 打包脚本（CLI/GUI/Web 三入口）
├── DouyinLiveRecorder.spec              # 由 build_exe.py 自动生成（.gitignore 已忽略）
├── requirements.txt                     # Python 依赖列表
├── uv.lock                              # uv 依赖锁文件（随仓库分发；镜像/CI 走 pip + requirements.txt，不消费）
├── pyproject.toml                      # Python 项目配置（版本号/工具配置/覆盖率门禁单一事实源）
├── scripts/                             # 辅助脚本
│   ├── check_version.py                # 版本号一致性校验（CI static job 调用）
│   ├── check_annotations.py            # 注释规范与逻辑等价性校验（禁 docstring / 密度下限 / --baseline AST 等价比对，CI static job 调用）
│   ├── check_coverage.py               # 逐模块覆盖率门禁（CI test job 调用，阈值 MODULE_THRESHOLDS）
│   ├── compile_po.py                   # gettext 翻译编译（.po → .mo；--check 零副作用校验同步，CI static job 调用）
│   ├── extract_i18n_strings.py         # i18n 待翻译串提取器（AST 扫描 print/logger 字面量 + 四语目录比对，维护期使用）
│   └── sync_version.py                 # 版本号同步脚本（pyproject → 各文档）
├── Dockerfile                          # Docker 构建文件（多阶段）
├── docker-compose.yaml                 # Docker Compose（recorder/web/gui 三服务）
├── .dockerignore                       # Docker 构建上下文排除文件
├── .gitignore                          # Git 排除文件
├── README.md                           # 项目说明（中文版，中英成对）
├── tests/                               # 单元测试目录（asyncio_mode=auto，覆盖率 source=src）
│   ├── conftest.py                     # Pytest 配置与 fixtures
│   ├── test_stream.py                  # stream.py 核心路径测试（工具函数 + 平台流解析）
│   ├── test_async_http.py              # async_http.py 核心路径测试（客户端管理 + 请求）
│   ├── test_sync_http.py               # sync_http.py 同步客户端测试
│   ├── test_room.py                    # room.py 直播间解析测试
│   ├── test_spider.py                  # spider.py 爬虫测试
│   ├── test_spider_platform.py         # spider.py 多平台分发测试
│   ├── test_utils.py                   # utils.py 工具函数测试
│   ├── test_douyin_url_resolution.py   # 抖音 URL 分发逻辑测试
│   ├── test_ttwid.py                   # 抖音 ttwid 共享缓存测试
│   ├── test_ab_sign.py                 # A-Bogus 签名算法测试
│   ├── test_proxy.py                   # 代理检测测试
│   ├── test_concurrency.py             # 线程安全并发测试
│   ├── test_i18n.py                    # i18n 翻译加载/环境变量独立性/po-mo 同步回归测试
│   ├── test_anchor_rename.py           # 主播名自动同步测试（config_io.update_anchor_name + main.rename_anchor_directory）
│   ├── test_scheduler.py               # 调度器测试（ResizableSemaphore / PlatformBreaker / ConcurrencyScheduler 共 16 用例）
│   ├── test_record_failure_feedback.py # 录制结果反馈测试（成功样本/快速失败退避/慢速失败/缺 -i/容量回退/直下失败与成功样本共 7 用例）
│   ├── test_stream_select.py           # 流选择与探针退避标记测试
│   ├── test_cookie_cache.py            # 访客 Cookie 缓存测试
│   ├── test_danmaku_monitor.py         # 弹幕监控枢纽测试
│   ├── test_http_config.py             # HTTP 配置测试
│   ├── test_config_io_readonly.py      # 配置只读/语言键迁移测试
│   ├── test_config_io_backup.py        # 配置备份测试
│   ├── test_bilibili_danmaku_info.py   # B站弹幕信息获取测试
│   ├── test_huya_danmaku.py            # 虎牙弹幕测试
│   ├── test_concurrency_rate_limit.py  # 抖音速率限制并发测试
│   ├── test_node_install.py            # Node.js 自动安装器离线测试（2026-09-21 新增）
│   ├── test_web_tray.py                # Web 控制台系统托盘离线测试（2026-09-21 新增）
│   ├── test_platform_danmaku_offline.py # 斗鱼/B站/Twitch 弹幕帧编解码离线测试（2026-09-21 新增）
│   ├── test_config_io_update_file.py   # 配置写侧（update_file / 主播名 / 备份脱敏）测试（2026-09-21 新增）
│   └── test_video_postprocess_paths.py # 视频后处理分支与异常分类测试（2026-09-21 新增）
├── .github/                             # GitHub Actions 工作流目录
│   ├── ISSUE_TEMPLATE/                 # Issue 模板（Bug 报告 / 功能请求）
│   ├── PULL_REQUEST_TEMPLATE.md         # PR 模板
│   ├── actions/
│   │   └── retry/                      # 复合动作：网络安装命令线性退避重试包装（ci.yml / build-release.yml 共用）
│   └── workflows/
│       ├── ci.yml                      # CI 静态验证（setup/static/typecheck/test/concurrency/integration/build-verify/summary）
│       ├── build-release.yml           # 三平台构建（lite + full 双产物）+ 自动发布 Release
│       └── issue-translator.yml        # Issue 自动翻译工作流（中英互译）
├── .coveragerc-concurrency             # 并发测试专用覆盖率配置（CI concurrency-test job 使用，不设全局阈值）
├── CODE_WIKI.md                        # 本架构文档（中文版）
├── CODE_WIKI_EN.md                     # 本架构文档（英文版）
├── README_EN.md                        # 项目说明（英文版）
└── ...
```

## 核心模块详解

### 1. 主程序模块 (`main.py`)

**职责**: 整个录制器的指挥中心，负责流程调度

**核心功能**:

- 配置文件读取与解析
- 直播间 URL 列表解析
- 并发控制与任务调度
- FFmpeg 进程管理
- 错误重试与动态调优
- 消息推送触发
- 退出信号处理

**关键状态变量**:

```python
recording: set              # 正在录制的直播间集合
monitoring: int             # 正在监控的直播间数
running_list: list          # 正在运行的 URL 列表
error_count: int            # 当前错误计数
error_window: list          # 错误时间窗口（用于动态调优）
url_tuples_list: list       # 解析后的 URL 配置列表 [(quality, url, anchor_name)...]
recording_time_list: dict   # 录制时间与画质记录 {name: [start_time, quality_zh, actual_quality_zh]}
```

**主流程函数**:

- `main()` - 入口函数
- `read_config()` - 读取配置
- `check_url_config()` - 检查 URL 配置
- `start_recording()` - 启动录制（解析 actual_quality，降级时输出告警）
- `stop_recording()` - 停止录制
- `check_live_status()` - 检测直播状态
- `display_info()` - 终端状态展示（兼容新旧 recording_time_list 格式）
- `get_status()` - 返回录制状态 dict（含 actual_quality 字段，供 Web API 使用）
- `select_source_url()` - 在 m3u8/FLV 源间选择，HLS 源校验失败时回退 FLV（`delay_default=120s` 轮询）；新增 `proxy_addr` 参数透传给三处校验调用，避免 TikTok 等需代理平台直连校验误判不可达；计算「末位候选」（FLV 无 record_url 备选时、record_url 恒为）并以 `last_resort` 传给校验器——稳定拒绝也仅告警放行、交由 ffmpeg 实际拉流定夺；**HLS 采集排除列表**（`main.hls_collection_exclude_platforms`，配置键「HLS采集排除平台(逗号分隔)」）：命中平台无视「是否启用HLS采集」配置、恒按 FLV 采集（等效于仅对该平台关闭 HLS 采集，HLS 候选整组剔除、不作回退；仅剩 HLS 源无回退时告警并放弃本轮，恢复指引指向移出排除列表），列表外平台行为不变
- `_validate_stream_url()` - 流地址校验：content-type 判定补充 `mpegurl`；HEAD 被拒时对 `.m3u8` 源（**含 404**）补 `Range: bytes=0-0` GET 探测——抖音 CDN 的 m3u8 常对 HEAD 返回 4xx，此前会被误判不可达而总回退 FLV；新增 `verify` 参数沿用全局 SSL 开关（与异步校验一致）；所有失败路径记录 warning（URL + 异常类型/状态码/content-type），不再静默吞异常；GET 复核（`_confirm_get_ok`）收到 401/403 先原样重试一次（间隔 0.8s）再定罪——斗鱼 hw/虎牙 al 等 CDN 对毫秒级连击探针（HEAD→GET）偶发 403（实测同 URL 片刻后重试即 200、ffmpeg 单次 GET 正常），重试可区分「偶发限流」与「稳定拒绝」，历史虎牙假绿场景重试仍 403 依旧被正确否决

**重构（2026-08-16）**：下列职责已抽离至 `src/` 子模块，经 `main.py` re-export 保持 `main.<name>` 命名空间兼容（`web.py`/`gui.py`/`web_api.py`/测试零改动）：

- FFmpeg 进程管理 → `src/ffmpeg_proc.py`（进程注册/注销/终止/清理）
- 视频后处理（分段/转码/字幕）→ `src/video_postprocess.py`
- 流地址选择/校验/画质码/抖音限速 → `src/stream_select.py`（`select_source_url`/`_validate_stream_url`/`get_quality_code`/`_douyin_rate_limit` 等）
- 推送/脚本/成功失败计数/并发调节 → `src/notify.py`（`push_message`/`record_error`/`record_success`/`adjust_max_request`/`clear_record_info` 等）
- 录制状态快照/展示 → `src/recorder_status.py`（`get_status`/`display_info`）
- 配置读写/安全数值转换/备份 → `src/config_io.py`（`update_file`/`delete_line`/`read_config_value`/`_safe_int`/`_safe_float`/`backup_file`/`backup_file_start`）

深度耦合 main 全局的模块一律用运行时 `import main` 惰性访问全局，避免启动期传参膨胀调用点；`main.py` 顶部加 `__main__` 守卫规避 `python main.py` 时子模块 `import main` 触发整文件二次执行。

**房间录制线程闭包整改（2026-08-16）**：新增直播间时为每路 URL 起一个 daemon 线程运行 `start_record`。原实现用「默认参数绑定循环变量」（`def _room_thread_target(_key=thread_key, _args=args)`）规避闭包晚期绑定陷阱，且 `_args: tuple[Any, ...]` 使用了项目 basedpyright 全局禁用的显式 `Any`。整改后：

- `_args` 类型具体化为 `tuple[tuple[str, str, str], int]`（`url_tuple` 为 `tuple[str, str, str]`，与 `start_record(url_data, count_variable)` 签名一致）；
- 通过 `threading.Thread(target=..., args=(thread_key, args))` 在创建线程时显式绑定当前循环值，移除默认参数 hack，语义更清晰、更易维护；
- 线程退出仍 `finally: create_var.pop(_key, None)` 清理，防止 `create_var` 字典长期无界增长。

**弹幕录制集成（2026-08-16 接线定稿）**：`start_record` 各平台分支收集 `record_danmaku_args`（每轮重置 `None`）→ 6 处 `check_subprocess(..., platform=platform, danmaku_args=record_danmaku_args)` 全部接线 → `get_danmaku_collector(platform, args, base_filename, segment_seconds)` 创建采集器。采集器在 `while process.poll() is None` 循环外 `stop()`（`DanmakuCollector.stop()` 有 `_stop_called` 防重入，幂等）。分段文件名约定：ffmpeg 视频分段模板统一 `_%03d`（FLV 已从 `_%02d` 对齐；音频仍 `_%02d` 但无弹幕），SRT 分片 `{seg:03d}`（`_000.srt` 对 `_000.ts`）；`check_subprocess` 同时剥离 `_%02d`/`_%03d` 占位符。抖音空 cookie 时 `DouyinDanmaku.start()` 协程内 `await get_ttwid()` 动态获取（采集线程独立事件循环，可直接 await；进程级缓存）。`弹幕分片时长(秒)` 走 `_safe_float(..., 1800.0)`。弹幕平台注册表见 `src/__init__.py` 的 `get_danmaku_class`（斗鱼直播/B站直播/虎牙直播/抖音直播/TwitchTV）。

**房间日志关联字段绑定（2026-09-20）**：`start_record` 作为房间线程主体，在**线程入口**即调 `set_room_context(f"序号{count_variable}")` 绑定日志关联字段（否则早于 `record_name` 的退出标志 / 注释退出 / 解析失败 / 熔断退避日志无法归属房间），并在每轮解析出主播名、`record_name = f"序号{count_variable} {anchor_name}"` 之后刷新为完整房间名。字段如何进入日志行、哪些线程带/不带该标记，见「6. 日志模块」与 `AGENTS.md`「已知坑」。

### 2. 爬虫模块 (`src/spider.py`)

**职责**: 负责从各大直播平台获取直播间数据

**支持平台**:

国内：抖音、快手、虎牙、斗鱼、YY、B站、小红书、bigo、blued、网易CC、千度热播、猫耳FM、Look直播、TwitCasting、百度、微博、酷狗、花椒、流星、Acfun、畅聊、映客、音播、知乎、嗨秀、VV星球、17Live、浪Live、飘飘、六间房、乐嗨、花猫、淘宝、京东、咪咕、连接、来秀

海外：TikTok、SOOP(原AfreecaTV)、PandaTV、WinkTV、TTingLive(原Flextv)、PopkonTV、TwitchTV、LiveMe、ShowRoom、CHZZK、Shopee、YouTube、Faceit、Picarto

**关键函数**:

- `get_douyin_web_stream_data()` - 获取抖音 Web 端直播数据（`web/enter` API 优先，失败静默重试 1 次，再回退 HTML 抓取）
- `get_douyin_app_stream_data()` - 获取抖音 App 端直播数据（备用方案，内置 URL 分发逻辑，见下方「抖音 URL 分发」）
- `get_tiktok_stream_data()` - 获取 TikTok 直播数据
- `get_youtube_stream_data()` - 获取 YouTube 直播数据
- `get_bilibili_stream_data()` - 获取 B站直播流数据（返回 dict，含 url/current_qn/accept_qn）
- `get_play_url_list()` - 获取 M3U8 播放列表中的清晰度选项
- `get_params()` - 从 URL 提取参数

**抖音 URL 分发逻辑**（`get_douyin_app_stream_data`，2026-08-01 优化后）：

| URL 形态 | 处理路径 |
| --- | --- |
| `live.douyin.com/<房间号或抖音号>` | 直调 `get_douyin_web_stream_data`（`web/enter` API 接受抖音号，无需重定向解析） |
| `www.douyin.com/user/<sec_uid>`（网页端主页） | 跳过必然失败的 `get_sec_user_id` 探测，走 `resolve_from_homepage()`：`get_unique_id()` 解析抖音号 → 拼接 `live.douyin.com/<抖音号>` → 直调网页端 |
| `v.douyin.com/<短链>`（App 短链，可能指向直播间或主页） | 先 `get_sec_user_id()` 跟随重定向；抛 `UnsupportedUrlError` 时回退 `resolve_from_homepage()` |

- `resolve_from_homepage()` 直调 `get_douyin_web_stream_data`（网页端 API 优先、内置 HTML 兜底），不再绕经旧版 HTML 优先抓取路径（约 1MB 页面），并**显式透传 proxy_addr / cookies**（旧实现未透传，导致代理与 Cookie 配置在主页路径静默失效）
- `web/enter` API 调用封装为 `_try_web_api()` + `for attempt in range(2)`：首次失败（如瞬时风控 `status_code=10002`）→ `await asyncio.sleep(0.5)` 缓冲 → 静默重试；重试成功直接返回、跳过 HTML 兜底；两次都失败才记 WARNING 并回退 HTML（取 HEVC 原画的 HTML 抓取是各网页端路径通用行为，保持不变）

**实现特点**:

- 使用异步 HTTP 客户端 (`httpx`)
- 各平台独立的签名算法
- 代理支持
- Cookie 支持
- 错误重试机制
- B站 spider 返回 dict 结构（含 `current_qn`/`accept_qn` 元信息），供 stream 模块回采实际画质

### 3. 直播流解析模块 (`src/stream.py`)

**职责**: 解析直播流地址，支持多种画质选择，回采平台实际下发的画质

**画质映射**:

```python
QUALITY_MAPPING = {"OD": 0, "BD": 1, "UHD": 2, "HD": 3, "SD": 4, "LD": 5}
QUALITY_MAPPING_BIT = {
    'OD': 99999, 'BD': 4000, 'UHD': 2000, 'HD': 1000, 'SD': 800, 'LD': 600
}
QUALITY_LEVEL = {"OD": 0, "BD": 0, "UHD": 1, "HD": 2, "SD": 3, "LD": 4}  # 等级值越大画质越低
QUALITY_CODE_TO_ZH = {"OD": "原画", "BD": "蓝光", "UHD": "超清", "HD": "高清", "SD": "标清", "LD": "流畅"}
NETEASE_QUALITY_MAP = {"blueray": "OD", "ultra": "UHD", "high": "HD", "standard": "SD"}
```

**画质工具函数**:

- `bitrate_to_quality(bitrate)` - 根据码率反查画质代码（0/未知回退 OD）
- `code_to_zh(code)` - 画质代码转中文名
- `is_downgrade(requested, actual)` - 判定是否降级（actual 等级值 > requested）
- `get_quality_index()` - 解析画质参数，返回索引
- `_pad_list()` - 填充列表到指定最小长度（部分平台已改用显式截断替代）

**各平台流地址解析函数**:

| 函数 | 平台 | 实际画质回采方式 |
| --- | --- | --- |
| `get_douyin_stream_url()` | 抖音 | 从 `flv_pull_url` / `hls_pull_url_map` 的 key 提取画质标签 |
| `get_tiktok_stream_url()` | TikTok | 从 `vbitrate` 字段通过 `bitrate_to_quality()` 反查 |
| `get_kuaishou_stream_url()` | 快手 | 从 `flv_url_list` 的 `bitrate` 字段反查 |
| `get_huya_stream_url()` | 虎牙 | 从 `exsphd` ratio 值映射，处理降级选择 |
| `get_douyu_stream_url()` | 斗鱼 | 从平台下发的 `rate` 字段反向映射 |
| `get_bilibili_stream_url()` | B站 | 从 spider 返回的 `current_qn` 反向映射为画质代码 |
| `get_netease_stream_url()` | 网易CC | 从画质名（blueray/ultra/high）通过 `NETEASE_QUALITY_MAP` 映射 |

**返回值结构**（各平台统一）:

```python
{
    "is_live": True,
    "anchor_name": "主播名",
    "title": "直播标题",
    "quality": "UHD",              # 用户设置的画质
    "actual_quality": "UHD",       # 平台实际下发的画质
    "available_qualities": ["OD", "UHD", "HD"],  # 平台可用的画质档位
    "m3u8_url": "http://...",
    "flv_url": "http://...",
    "record_url": "http://...",
}
```

**实现特点**:

- 按带宽排序的清晰度选择
- 自动降级策略（首选画质不可用时自动降级）
- FLV 与 M3U8 双协议支持
- 状态码验证
- 显式截断替代 `_pad_list` 静默填充，避免越界
- 画质降级检测（`is_downgrade`），供 main.py 告警使用
- 斗鱼 FLV→m3u8 同 token HLS 候选：`get_douyu_stream_url` 在 `rtmp_live` 以 `.flv` 结尾时，将路径 `.flv` 改 `.m3u8`（查询串原样保留）附为 `m3u8_url`——斗鱼 wsAuth token 对 FLV/HLS 通用（实测 hw CDN 200 + `application/vnd.apple.mpegurl`，两级 m3u8），HLS 采集开启时经 `select_source_url` 优先校验选用、不可达自动回退 FLV；HLS 逐段拉取不维持长连接，缓解游客态 FLV 长连接约 70 秒被 CDN 掐断导致的反复分段

### 4. 直播间信息模块 (`src/room.py`)

**职责**: 解析直播间 URL，提取房间 ID、主播信息、抖音号等

**关键函数**:

- `get_sec_user_id()` - 获取房间 ID 和用户 sec_user_id
- `get_unique_id()` - 获取抖音号（含 30 分钟 TTL 的 sec_uid→抖音号进程级缓存，对齐 `ttwid.py` 的 `threading.Lock` 跨线程/跨 asyncio 循环去重模式）
- `is_user_homepage_url()` - 判断 URL 是否为「网页端主播主页」形态（`douyin.com/user/<sec_uid>`，v.douyin.com 短链不属于此类）；用于零请求快速路径——sec_user_id 直接在路径中，无需发请求跟随重定向
- `extract_sec_user_id()` - 从 URL 中显式正则提取 sec_user_id
- `get_live_room_id()` - 获取直播间 web ID
- `get_xbogus()` - 生成 X-Bogus 签名

**异常处理**:

- `UnsupportedUrlError` - 不支持的 URL 格式异常

**关键常量与接口**:

- `DESKTOP_UA` - 桌面 Chrome UA。`iesdouyin.com/web/api/v2/user/info/` 等接口用旧移动端 UA 会被静默限流（HTTP 200 + 空 body），必须使用桌面 UA
- 主页解析走 `https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=<sec_uid>` JSON 接口（取 `unique_id`，空则退 `short_id`）——旧 `iesdouyin.com/share/user/<sec_uid>` 页面已是 JS 反爬壳页，HTML 正则不可靠

### 5. 工具模块 (`src/utils.py`)

**职责**: 提供通用工具函数

**主要工具**:

| 工具函数 | 功能描述 |
| --- | --- |
| `Color` 类 | 终端彩色输出常量 |
| `trace_error_decorator()` | 错误追踪装饰器 |
| `check_md5()` | 计算文件 MD5 |
| `dict_to_cookie_str()` | cookie 字典转字符串 |
| `read_config_value()` | 读取配置文件值 |
| `update_config()` | 更新配置文件 |
| `remove_emojis()` | 移除文本中的表情符号 |
| `remove_duplicate_lines()` | 移除文件重复行 |
| `handle_proxy_addr()` | 处理代理地址格式 |
| `generate_random_string()` | 生成随机字符串 |

### 6. 日志模块 (`src/logger.py`)

**职责**: 基于 Loguru 配置结构化日志

**日志输出**:

- **控制台**: 彩色日志输出（`custom_format`，不含房间列）
- **`logs/streamget.log`**: DEBUG 级别（排除 INFO），行结构 `时间 | 级别 | 房间 | 模块:函数:行号 - 消息`
- **`logs/PlayURL.log`**: INFO 级别（仅直播流地址），行结构 `时间 | 房间 | 消息`
- **`logs/gui.log`**: 仅 GUI 父进程写（独占句柄），不带房间列——GUI 进程不执行录制，该列恒为空

**房间关联字段 `extra[room]`（2026-09-20 新增）**:

- 房间线程的全部日志行带一个稳定关联列，用于从多房间交织落盘的日志里切出单个房间的链路（切法与边界见 `AGENTS.md`「已知坑」同名条目）
- 实现：`ROOM_FIELD` + `set_room_context()` / `get_room_context()` 读写一个 `ContextVar`，由 `logger.configure(extra={ROOM_FIELD: ""}, patcher=_room_patcher)` 注册的全局 patcher 在**调用线程**内写进 `record["extra"]`（故 `enqueue=True` 不串味）；调用点显式 `bind(room=...)` 优先于线程级兜底
- 房间线程在 `main.py::start_record` 入口绑 `序号N`、解析出主播名后升级为完整 `record_name`；`set_room_context("")` 为解绑
- **`extra` 默认值不可删**：缺它时未绑定房间的日志格式化 `KeyError: 'room'`，loguru 不抛异常而是每条日志向 stderr 吐 `Logging error in Loguru Handler` 并丢弃该行；回归锁 `tests/test_logger_room_context.py`
- 只加关联标识：日志级别、INFO/其余两档 `filter`、`rotation`、`retention` 均未改动

**日志文件开关**:

- 通过 `config/config.ini` 的 `是否启用日志文件(是/否)` 控制
- 默认启用，保持向后兼容
- logger.py 在初始化时直接读取配置（不依赖 main.py 执行顺序）

**日志轮转**: 300 KB 自动轮转，保留 1 份

### 7. 消息推送模块 (`msg_push.py`)

**职责**: 支持多种消息推送渠道

**支持渠道**:

| 渠道 | 函数名 | 说明 |
| --- | --- | --- |
| 钉钉 | `dingtalk()` | 群机器人推送 |
| 微信 | `xizhi()` | Server酱 / WeChat |
| Telegram | `tg_bot()` | Bot 消息 |
| 邮件 | `send_email()` | SMTP 协议 |
| Bark | `bark()` | iOS 通知 |
| NTFY | `ntfy()` | 开源推送服务 |
| PushPlus | `pushplus()` | 微信推送平台 |

### 8. 国际化模块 (`i18n.py`)

**职责**: 基于 gettext 的多语言支持系统，自动翻译项目源码的 print 输出。

**实现机制**:

- `translated_print` 包装 `builtins.print`，自动翻译调用者来自项目根（`src/` 包及 `main.py` 等顶层脚本）的输出；`main.py` 导入时无条件安装 `builtins.print = translated_print`（任何语言下均安装——zh_CN/zh_TW 把英文常量串译为中文，en_US/en_GB 把中文串译为英文，未知串恒等返回）
- 支持源码运行和 PyInstaller 打包两种路径检测（`_internal/i18n` vs `i18n/`）
- **多格式目录加载（2026-08 起）**：`i18n.py` 按语言依次探测 gettext `.mo` → `<lang>.json` → `<lang>.yaml`，三种格式均为「原文 → 译文」扁平映射，行为一致；`PyYAML` 为运行时依赖（缺失时仅损失 YAML 格式支持）。`_load_yaml_catalog()` 捕获 `yaml.YAMLError`（非 OSError/ValueError 子类）——损坏的 yaml 目录返回 None 降级到下一格式，而非让 `set_language` 抛异常（Web 语言切换接口 500）
- **语言热切换**：`set_language(lang)` 归一化（`normalize_language` 别名表：zh_cn/zh-CN/en/en-US/zh-Hant/zh_CN.UTF-8 等写法均可）后热替换 `_tr` 翻译函数，无需重启进程。三个切换入口：Web 面板（`GET/PUT /api/language`，写回 config + 热切换 + 前端 `data-i18n` 文案重绘；`PUT` 在配置缺 `language` 键时降级为节末追加补建，不再恒 500）、GUI（侧边栏「语言 Language」菜单）、CLI 主循环（每轮按 config 重同步）
- 默认语言：简体中文（zh_CN）；受支持语言：zh_CN / en_US / en_GB / zh_TW

**翻译文件**:

| 文件 | 说明 | 条目数 |
| --- | --- | --- |
| `i18n/zh_CN/LC_MESSAGES/zh_CN.po` | 简体中文翻译源文件（gettext，可编辑） | 496 |
| `i18n/zh_CN/LC_MESSAGES/zh_CN.mo` | 编译后的二进制翻译文件（gettext 运行时唯一读取，随仓库/镜像分发） | 496 |
| `i18n/en_US.json` | 英语（美国）目录（JSON 格式，英文源恒等 + 中文源译英） | 496 |
| `i18n/en_GB.json` | 英语（英国）目录（JSON 格式，英式拼写：minimise/unrecognised 等） | 496 |
| `i18n/zh_TW.yaml` | 繁体中文目录（YAML 格式，简→繁字符转换 + 台湾用语适配） | 496 |

**维护流程**: 修改 `.po` 后必须执行 `python scripts/compile_po.py` 重新编译并一并提交 `.mo`，否则翻译改动不会生效；`python scripts/compile_po.py --check`（CI `static` job）在两者不同步时拦截——其内部 `write_mo()` 为**纯内存产出不落盘**，`--check` 模式零副作用、真实比对磁盘上已提交的 `.mo`，仅非 check 模式才写盘。CI 路径过滤器（paths-filter）将 `i18n/**` 视为触发条件：纯翻译变更同样会运行该门禁。**四种语言的目录键集合必须一致**（`tests/test_i18n.py::test_catalogs_share_same_keyset` 强制校验）——新增 msgid 时需同步更新四个目录。新增待翻译串的提取与比对用 `python scripts/extract_i18n_strings.py`（AST 扫描运行时代码 print 常量串 + logger f-string 模板底稿并与四语目录比对；f-string 模板归一化约定：格式/转换符丢弃、表达式内双引号转单引号；纯占位符模板（如 `{color}{text}`）与 gettext 头部空 msgid 已过滤，不产生噪声）。

**翻译覆盖范围**（2026-08-27 全量补全后，覆盖运行时全部常量串与 logger 模板底稿）:

- `src/spider.py` — 各平台直播数据获取/登录/风控消息（含 B站 buvid 认证链路）
- `main.py` — 主程序通用消息、录制链、画质降级、主播名同步、磁盘空间
- `gui.py` — GUI 界面消息（控件文本、进程管理、托盘、退出确认）
- `src/scheduler.py` — 并发模式切换与容量调整播报
- `src/stream_select.py` — 流地址校验全套消息（探针退避、GET 复核、末位放行）
- `src/collector.py` / `src/danmaku_monitor.py` — 弹幕采集与监控
- `src/async_http.py` / `src/sync_http.py` / `src/cookie_cache.py` — HTTP 客户端与 cookie 缓存
- `msg_push.py` — 七渠道推送失败分支（微信/钉钉/TG/Bark/ntfy/PushPlus/邮件）
- `src/ffmpeg_install.py` / `src/node_install.py` — ffmpeg/Node.js 自动安装
- `src/config_io.py` / `src/utils.py` — 配置读写、备份、磁盘空间
- `src/notify.py` — 自定义脚本执行错误
- `web.py` / `src/web_tray.py` — Web 面板启动与托盘
- `src/room.py` / `src/recorder_status.py` / `src/ttwid.py` / `src/ffmpeg_proc.py` / `src/platforms/bilibili.py` / `src/platforms/douyin.py` / `build_exe.py` — 其余运行时消息

> 注：运行时真正参与翻译查找的是 `print()` 输出的常量英文串；`logger.*` 输出与 f-string 插值后的文本不经过查找，目录中相关条目仅作为后续日志接入 i18n 时的现成翻译底稿保留。

### 9. GUI 模块 (`gui.py`)

**职责**: 提供现代化图形用户界面

**设计特点**:

- **高对比度色彩系统**: 满足 WCAG AA 无障碍标准
- **DPI 感知字体**: 自适应分辨率缩放
- **系统托盘**: 最小化到托盘运行
- **现代组件**: 卡片式设计、渐变横幅、状态指示器

**主要组件**:

- `Colors` - 色彩常量类
- `DpiFont` - DPI 感知字体系统
- `SystemTray` - 系统托盘管理
- `CardFrame` - 卡片容器
- `GradientBanner` - 渐变横幅
- `StatusIndicator` - 状态指示器
- `ModernTextWidget` - 现代文本控件

**导航页面**:

- 📊 控制台 - 录制状态总览、启停控制
- 🎯 画质监控 - 实时检测各直播间实际画质是否与设置一致
- 📝 URL 配置 - 直播间地址管理
- 📋 运行日志 - 子进程日志查看

**画质监控页面** (`_build_quality_page`):

- 通过解析 main.py 子进程 stdout 日志获取画质信息
- 解析 loguru 日志前缀（`|` + `-` 分隔），提取 message 内容
- 降级告警匹配：`{name} 画质降级：设置 {zh}({code}) 实际 {zh}({code})`
- 录制状态匹配：`{name}[{quality}] 正在录制中 {duration}`
- 统计卡片：录制中 / 画质正常 / 画质降级 计数
- 降级行以红色背景高亮，正常行显示"✓ 同等"
- 线程安全：`_quality_lock` 保护共享数据，UI 更新仅在主线程执行
- 超时清理：30 秒未更新的录制标记自动清除

### 10. 异步 HTTP 客户端 (`src/async_http.py`)

**职责**: 封装 httpx，提供统一的异步 HTTP 接口

**功能**:

- 代理支持
- 超时设置
- 自动重试
- 状态码检查
- HTTP/2 支持
- **连接池复用**: 按 (代理, verify, http2) 维度复用 AsyncClient，发挥 keepalive 连接池作用
- **事件循环检测**: 缓存记录每个 client 创建时的事件循环引用，检测到 `asyncio.run()` 导致循环变更时自动重建客户端，避免 `'NoneType' object has no attribute 'send'` 错误
- **模块级锁随事件循环重建**（2026-08-12 修复）: 保护 `_client_cache` 读写的 `_client_lock` 原是模块级单例 `asyncio.Lock()`，在首个 room 的 `asyncio.run()` 循环里惰性绑定后，后续 room 各自 `asyncio.run()` 起新循环再次 `await` 会触发 `RuntimeError: ... is bound to a different event loop`；该异常被 `async_req` 吞掉后返回空串，被 `spider.py` 误判成「风控空响应」并级联触发 HTML 兜底失败。现 `_get_client_lock()` 改为缓存 `(lock, loop)` 二元组，当前循环变更时自动重建锁，与 `_client_cache` 的「client + loop」机制一致，从源头消除跨循环锁错误
- **异常日志带类型**（2026-08-12 收口）: `async_req`、`_close_all_clients` 内所有 `except Exception as e: logger.debug(e)` 改为带 `type(e).__name__`（必要时含 URL），消除 Windows 下异常 `str()` 为空时打出空白日志、无法定位的问题
- **SSL 验证**: 由全局配置 `src/http_config.py` 统一控制，默认启用
- **跨循环旧客户端不再调度关闭**（2026-09-04 修复）: 淘汰他循环创建的旧 AsyncClient 时一律**不创建** `aclose()` 协程（旧循环运行中/已停止/已关闭同样对待），释放引用交由 GC 兜底。旧实现 `run_coroutine_threadsafe` 只调度不等待，旧循环处于 `asyncio.run` 收尾窗口（已停未关）时回调永不执行，GC 报 "coroutine ... aclose was never awaited" 且数量随机波动（1~2 条 flaky，经 unraisableexception 逸出）；「is_running 门控 + 等待 future」实测仍无法根治（收尾阶段任务可能已创建却永不步进 `Task was destroyed but it is pending`，future 永不完成还会把收尾竞态放大成秒级阻塞）；在当前循环直接 await 则会操作绑定旧循环的 transport。回归锁：`tests/test_async_http_lock.py::test_cross_loop_running_old_loop_skips_close` / `test_cross_loop_stopped_old_loop_skips_close`
- **连接池清理**: 进程退出时通过 atexit / 信号处理器释放所有复用的 AsyncClient
- **`get_response_status()` m3u8 容错**（2026-08-05 增强）: HEAD 校验失败时，若 URL 以 `.m3u8` 结尾则补一次 `Range: bytes=0-0` GET 轻量探测（**含 404 在内的所有非 2xx 均触发探测**，返回 200/206 即判可达）；非 m3u8 源（FLV/record_url）行为不变。异常日志带 URL + `type(e).__name__`（如 `ConnectTimeout` / `TimeoutError`），避免 Windows 下 `socket.timeout` 的 `str()` 为空时只输出空白消息；探测失败记录 `status_code` / `content-type` 便于排障

**被以下模块导入**:

- `src/spider.py` - `async_req()`
- `src/stream.py` - `get_response_status()`

### 11. HTTP 客户端配置 (`src/http_config.py`)

**职责**: 提供 HTTP 客户端共享运行时配置

**功能**:

- SSL 证书验证全局开关（`ssl_verify`），默认启用（True，安全优先）；已整合进「是否启用https录制」——开启=https 拉流 + 禁用证书验证，关闭=http 拉流 + 默认严格校验（由 main.py 每轮热同步）
- 提供 `set_ssl_verify()` / `set_https_recording()` 函数，由主配置启动时及主循环每轮设置
- 平台级 SSL 覆盖（`ssl_verify_platform_overrides`）：兼容保留，整合后不改变实际行为
- 异步 / 同步 HTTP 客户端在发起请求时读取此配置

### 12. 同步 HTTP 客户端 (`src/sync_http.py`)

**职责**: 封装 requests 和 urllib，提供同步 HTTP 接口

**功能**:

- 代理支持
- 超时设置
- Cookie 支持
- 重定向跟踪
- **SSL 验证**: 由全局配置 `src/http_config.py` 统一控制，并可经 `ssl_verify` 参数做**单次覆盖**（见下）
- **Session 生命周期管理（2026-09-02）**: thread-local `requests.Session` 经模块级 `WeakSet` 弱引用登记（线程销毁后条目自动回收、不阻止 GC）；`atexit` 注册 `close_all_sessions()` 在进程退出时统一优雅关闭全部存活连接池（80+ 房间长跑场景）；另提供 `close_session()` 供房间线程退出路径显式释放当前线程 Session，关闭后下次 `_session()` 自动重建
- **Opener 构造形态（F-12 落地后，2026-09-24 校准本小节）**: 仅 `_opener_secure`（禁用代理 + 保留证书验证）在模块级预构建；不校验证书的 `SSLContext` 与 opener 一律**按需惰性构造**（`_get_insecure_context()` / `_get_insecure_opener()`）——2026-09-12 审查 6.7 指出「import 期即存在不校验上下文」等于给全进程开静默降级面，故禁止改回常驻
- **`ssl_verify` 单次覆盖（F-12）**: `sync_req(..., ssl_verify=None/True/False)` 由 `_resolve_ssl_verify()` 裁决（`None` = 跟随 `http_config.ssl_verify` 全局开关，显式传值以本次调用为准），且该次裁决必须**同时透传 urllib 与 requests(代理) 两条路径**，凭据类调用点可显式强制校验而不被全局降级拖下水
- **线程级 Session 公开出口（MIN-08）**: `session()` 供「必须拿状态码 / 响应头、无法走 `sync_req`（其失败契约是一律返回空串）」的调用点复用同一份连接池；打桩目标仍是 `_session`（测试约定）
- **响应体上限（SEV-2226 收尾，2026-09-23）**: 无代理 urllib 路径两道上限缺一不可——`_read_capped()` 限制压缩/原始响应体读入（`_MAX_RESPONSE_BYTES` 8 MiB）、`_gunzip_capped()` 分块解压并限制产出（`_MAX_DECOMPRESSED_BYTES` 32 MiB），超限抛 `ValueError` 由既有失败分支记脱敏日志并返回空串；**代理分支的 `response.text` 由 requests 自行解码 gzip，仍不受该上限保护**（已知残留缺口，见源码注释）
- **现状（SEV-2226 取证，2026-09-23）**: 本模块**当前无任何生产 importer**（`src/spider.py` 走 `from .async_http import async_req` 的 httpx 异步面；原调用方 `src/weverse_auth.py` 已于 2026-09-23 删除），去留待维护者决定；本体仍承载 F-12 不变量与 `tests/test_sync_http.py` 对该不变量的回归锁

### 13. Web 管理面板 (`web.py` + `src/web_api.py` + `src/web_config.py` + `web/`)

**职责**: 提供 Web 界面远程管理录制器，包括仪表盘、直播间管理、配置编辑、日志查看

**架构**:

- `web.py` - 入口：守护线程运行 `main.main()`，主线程运行 uvicorn；支持后台隐藏运行模式
- `src/web_api.py` - FastAPI 应用：认证（Token）、REST API 路由、SSE 推送、静态资源挂载
- `src/web_config.py` - 配置读写（不依赖 FastAPI，便于单测）
- `web/` - 前端静态资源（单页应用）

**后台运行模式** (`web_show_console = false`):

- `_enter_background_mode()` 在启动录制引擎前调用
- Windows 下通过 `ctypes` 调用 `GetConsoleWindow()` + `ShowWindow(hwnd, SW_HIDE)` 隐藏控制台窗口
- stdout/stderr 重定向到 `logs/web_console.log`（行缓冲，实时写入）
- 程序完全后台运行，通过 Web 面板管理
- 恢复控制台：设置 `web_show_console = true` 后重启

**控制台编码 / `ctypes` 健壮性（2026-08-16 整改）**:

- kernel32 / user32 的 `WinDLL` 句柄缓存为模块级单例（`_KERNEL32` / `_USER32`），避免 `_fix_encoding()` 与 `_enter_background_mode()` 多次调用时重复加载 DLL；加载失败时仍保持 `None`，后续调用自动重试
- 补全 `restype` 声明：`SetConsoleOutputCP` / `SetConsoleCP` 返回 `BOOL`（显式 `restype = ctypes.c_int`），`ShowWindow` 返回 `BOOL`，与既有的 `GetConsoleWindow.restype = c_void_p` 一致，消除对 ctypes 默认返回类型的隐式依赖
- `_enter_background_mode()` 中 `GetConsoleWindow()` 的返回值已为 `c_void_p`，移除多余 `cast(ctypes.c_void_p, ...)`，直接判空后 `ShowWindow(hwnd, 0)`

**API 路由**:

| 路由 | 方法 | 功能 |
| --- | --- | --- |
| `/api/login` | POST | 密码登录，返回 Token |
| `/api/status` | GET | 获取录制状态（含 actual_quality） |
| `/health` | GET | 探活端点（`{"status": "ok", "version"}`，恒公开、不受认证支配；CI 冒烟 / LB 健康检查用） |
| `/api/rooms` | GET/POST | 直播间列表查询 / 新增 |
| `/api/rooms/{url}` | PUT/DELETE | 编辑 / 删除直播间 |
| `/api/rooms/toggle` | POST | 启用 / 禁用直播间 |
| `/api/recording/toggle` | POST | 录制全局开关（开始/停止录制；停止时触发运行日志归档） |
| `/api/config` | GET/PUT | 读取 / 修改配置 |
| `/api/logs/stream` | GET | SSE 实时日志推送 |

**前端功能** (`web/`):

- `index.html` - 单页应用入口（仪表盘 / 直播间 / 配置 三个视图）
- `app.js` - 前端逻辑（Token 认证、API 调用、SSE 日志流、状态渲染）
- `style.css` - 样式表（明暗主题、响应式布局、降级高亮）

**录制表格展示**:

- 名称 / 设置画质 / 实际画质 / 开始时间 / 已录时长
- 实际画质与设置画质不一致时标红显示（`.quality-down` 样式）

**安全机制**:

- 密码变更后自动吊销所有现有 Token，强制重新登录
- 监听 `0.0.0.0` 且未启用认证时输出安全告警
- 文件下载路径校验（`_is_within` 防目录穿越）
- 敏感配置项（Cookie / 账号密码 / web_password）API 返回时脱敏为 `***`
- **未认证危险配置写保护**：`web_auth_enable = false` 时，`PUT /api/config` 禁止改写 [Recorder] 与 [Push] 危险键（如「录制完成后执行自定义脚本」`run_script`），仅允许 [Web] 及白名单键，阻断未认证 RCE 链
- **INI 注入防护**：配置值与直播间名称过滤 `\n`/`\r`，防止向 `config.ini` / `URL_config.ini` 注入任意新行 / 新节
- **登录爆破限流**：`/api/login` 连续失败达阈值（默认 5 次 / 5 分钟）后锁定一段时间（默认 10 分钟），防御密码在线爆破
- **推送日志脱敏**：`msg_push.py` 的 `_mask_url()` 对失败日志中的 webhook URL 遮挡 query 内 token / secret，避免凭证经日志泄露

### 14. 弹幕采集子系统 (`src/platforms/` + `src/collector.py` + 关联模块)

**职责与架构总览**: 提供与视频录制同步、按半小时分片的直播弹幕（bullet-chat）采集能力——弹幕落为 SRT 字幕文件，并可经「弹幕监控」独立查看（仅监控不落盘）。弹幕模块自 `dart_simple_live` 移植，原位于 `src/danmaku/`，后随目录扁平化迁移至 `src/` 根（基类 `src/base.py`、采集器 `src/collector.py`、监控 `src/danmaku_monitor.py`、传输 `src/ws_client.py`、缓存 `src/cookie_cache.py`、字幕 `src/srt_writer.py`、`src/proto/`、各平台实现 `src/platforms/`）。

**与流解析解耦**: 弹幕子系统与 `src/spider.py`（视频流地址解析）是**平行的两套抽象**。`spider.py` 负责解析视频流地址，弹幕客户端经 `src/__init__.py` 的注册表/工厂解耦；`spider.py` 完全不 import `src/platforms`。仅 B站弹幕在 AUTH 被拒时会懒加载回调 `spider.invalidate_bili_buvid_cache()`。

**生命周期接线**（与录制同起同停）:

- `main.start_record` 各平台分支收集 `record_danmaku_args`（每轮重置 `None`）；
- 6 处 `check_subprocess(..., platform=platform, danmaku_args=record_danmaku_args)` 全部接线；
- 由 `src/__init__.py:get_danmaku_collector(platform, danmaku_args, base_filename, segment_seconds, only_fans, room_name, write_srt)` 工厂按平台取弹幕类并构造 `DanmakuCollector`；平台不支持或 `danmaku_args` 为空时返回 `None`；
- `DanmakuCollector` 在 `while process.poll() is None` 循环外 `stop()`，`DanmakuCollector.stop()` 有 `_stop_called` 防重入（幂等）。

**平台注册表**（`src/__init__.py:get_danmaku_class`，平台名与 `main.py` 标识一致）:

| 平台标识 | 弹幕类（`src/platforms/`） |
| --- | --- |
| 斗鱼直播 | `DouyuDanmaku` |
| B站直播 | `BilibiliDanmaku` |
| 虎牙直播 | `HuyaDanmaku` |
| 抖音直播 | `DouyinDanmaku` |
| TwitchTV | `TwitchDanmaku` |

**关键文件**:

- **基类与数据结构 (`src/base.py`)**: `DanmakuBase(ABC)` 定义统一契约——类属性 `heartbeat_interval=45.0`；构造 `__init__(on_message, on_close, on_ready)` 保存回调并置 `_stopped=False`；四个抽象方法 `async start(args)` / `async stop()` / `async heartbeat()` / `decode_message(data: bytes|str)`，辅助 `_emit(msg)` 经 `on_message` 上抛。`DanmakuMessageType(Enum)`（`CHAT/GIFT/ONLINE/SUPER_CHAT`）；`DanmakuMessage` dataclass（`type/user_name/message/data/color/timestamp_ms`，`timestamp_ms` 由采集器注入）。
- **弹幕采集器 (`src/collector.py`)**: `DanmakuCollector` 把异步弹幕客户端包装为线程化的同步采集器。构造参数含 `danmaku_cls / danmaku_args / base_filename / segment_seconds / only_fans / room_name / platform_name / write_srt`（`write_srt=False` 为仅监控不落盘模式）；`start()` 锚定 SRT 时间轴并起 daemon 线程 `_run()`（新 `asyncio.new_event_loop()`，实例化弹幕类 `run_until_complete(danmaku.start(args))`）；`_on_message` 把全部类型上报监控枢纽 `hub.room_message(...)`，仅 `CHAT` 且用户名/内容非空才写 SRT；`stop(timeout=8.0)` 幂等，`message_count` 属性。依赖 `src.base` / `src.danmaku_monitor` / `src.srt_writer`。
- **各平台弹幕客户端 (`src/platforms/`)**: 五个 `DanmakuBase` 子类 + 两个私有签名/编解码工具。
| 文件 | 类 | WebSocket 端点 | 关键协议/逻辑 |
| --- | --- | --- | --- |
| `douyin.py` | `DouyinDanmaku` | `wss://webcast100-ws-web-lq.douyin.com/webcast/im/push/v2/` | gzip 解 `PushFrame.payload`→`Response`（protobuf）；`danmaku_signature`（`_xbogus`）生成 `signature`；Cookie 缺失 `await get_ttwid()`；`backup_url` 把 `lq`→`lf` |
| `douyu.py` | `DouyuDanmaku` | `wss://danmuproxy.douyu.com:8506` | 小端二进制帧 + STT 文本协议；`_dispatch` 处理 `chatmsg`（按 `if==1` 粉丝过滤）emit CHAT；心跳发 `mrkl` |
| `huya.py` | `HuyaDanmaku` | `wss://cdnws.api.huya.com` | Tars 二进制协议（`_tars`）；`_make_join_data()` 写 `WSRegisterReq`；`cmdType==7`→`_decode_chat`（HYMessage） |
| `bilibili.py` | `BilibiliDanmaku` | `wss://{host}/sub`（遍历 `host_list`） | 16B 大端帧头；`protover=2` zlib / `=3` brotli 解压；`operation==8` AUTH_REPLY 校验 `code==0`，失败/超时经 `_reject_auth()` + `spider.invalidate_bili_buvid_cache()`；`_auth_watchdog`(8s) 兜底 |
| `twitch.py` | `TwitchDanmaku` | `wss://irc-ws.chat.twitch.tv` | 纯 IRC；匿名 `justinfan{random}` 连接；`PING`→`PONG`，正则解析 PRIVMSG emit CHAT；代理经 `handle_proxy_addr` 或系统代理 |
| `_tars.py` | （私有）Tars 编解码器 | — | 虎牙用极简 Tars：`TarsInputStream` / `TarsOutputStream`，头字节高 4 位 tag、低 4 位 type |
| `_xbogus.py` | （私有）X-Bogus 签名 | — | 抖音弹幕用：`generate_xbogus`（RC4 + 自定义 base64）、`danmaku_signature(room_id, unique_id)` |
- **弹幕监控枢纽 (`src/danmaku_monitor.py`)**: `DanmakuMonitorHub`（进程单例，经 `get_hub()` 惰性创建）聚合各房间弹幕事件——`room_started/room_connected/room_closed/room_stopped/room_message`，内存快照 `snapshot(since=0)` 供 Web API 消费，并写 JSONL 边车 `logs/danmaku_monitor.jsonl`（5MB 轮转）。所有方法异常全吞；含 10s×6 桶速率窗与每秒 ≤10 条采样折叠。
- **SRT 字幕写入 (`src/srt_writer.py`)**: `SrtWriter` 按 `segment_seconds` 分片输出 `{base}_{seg:03d}.srt`（单文件模式 `{base}.srt`），时间轴以 `time.monotonic()` 为基准、与 ffmpeg `segment -reset_timestamps` PTS 对齐；`write()` 持 `threading.Lock` 写条目并 flush。
- **WebSocket 传输层 (`src/ws_client.py`)**: `WsClient` 各平台弹幕共用的异步 WS 客户端。`connect()` 显式 `proxy=None`（弹幕直连、不跟随系统代理，避免 SOCKS 需 python-socks 报错）；`ping_interval=None`（各平台自带心跳）；`max_size=None`、`asyncio.Lock` 串行发送；支持 `on_message/on_ready/on_heartbeat/on_close/on_reconnect` 回调与 `max_reconnect` 重连策略。
- **访客 Cookie 缓存 (`src/cookie_cache.py`)**: 进程内唯一「按网址动态获取访客 cookie」缓存，避免多 room 并发重复请求触发风控。`fetch_cookies(url, proxy, *, ttl=30min, fetcher=None)` 无锁快速路径 + singleflight 去重（2026-09-02 重写：`threading.Lock` 仅保护缓存字典与在途登记表的同步读写、**锁内绝无 await**——旧 RLock 跨 await 持有时同循环协程全部可重入、互斥失效；同循环等待者复用 future，跨循环经 `loop.call_soon_threadsafe` 交付（future 非线程安全）；拉取协程被取消时立即交付空结果，等待者带超时兜底防永久挂起）；`get_cookie_str` / `invalidate` / `clear`。
- **抖音弹幕协议 (`src/proto/`)**: `douyin.proto`（Proto3）定义 `Response/Message/ChatMessage/GiftMessage/...` 等；`douyin_pb2.py` 为 protoc 生成（DO NOT EDIT），`douyin_pb2.pyi` 为基于pyright 类型存根。抖音弹幕解析链路：`PushFrame.payload`（gzip 后 `Response`）→`Message.payload`→`ChatMessage`。

### 15. 并发调度中枢 (`src/scheduler.py`)

**职责**: 统一管理全局网络并发容量、按平台（host）隔离熔断降级、支持自适应调速与固定并发双模式的可运行时调容信号量系统。

**核心类**:

- **`ResizableSemaphore`**: 可运行时调容的信号量，实现上下文管理器协议。支持 `set_value(n)` 运行时增减容量——增大时唤醒相应数量的等待者，减小时仅降低上限、不强行回收已持有槽位。`__init__` / `set_value` 允许容量为 0（暂停态）。消除旧「销毁重建信号量」的竞态风险。
- **`PlatformBreaker`**: 按 key（host）隔离的熔断器，实现 `closed → open → half-open` 三态状态机。连续失败样本比例超阈值即 open（跳过探测并进入冷却），冷却后经**唯一**探针放行；探针成功恢复 closed、失败重新 open。用于将单平台抖动隔离降级，避免连锁拖垮全局。**探针带租约（`_PROBE_LEASE_SECONDS = 60s`，2026-08-27 起）**：探针被授予后超过租约仍未回报样本（主播未开播等待轮、`disable_record`、房间线程退出等不触发 `record` 的路径）时，`allow()` 重新授予探针实现自愈——无租约时 `_probing` 标志永不复位会导致该 host 永久熔断直到进程重启。
- **`ConcurrencyScheduler`**: 调度中枢，整合自适应容量、平台熔断、录制并发上限三大能力。
  - **网络并发容量** = `max(配置下限, min(上限, ceil(活跃数/缩放因子)))`；错误率极高时温和降容但永不低于安全下限（默认 min=1 / max=128）
  - **自适应模式**（默认，`最大同时录制数(0为不限制) = 0`）：容量随活跃任务数动态缩放，错误率反馈驱动温和背压
  - **固定并发模式**（`最大同时录制数(0为不限制) ≠ 0`）：忽略动态调速器与错误背压，网络容量恒为「同一时间访问网络的线程数」（最小 1 槽位，热更新即时生效）
  - **录制并发软上限**：通过 `recording_semaphore` 管控同时 ffmpeg 录制数，默认 0 为不限制
  - `adjust_loop` 守护循环每 5 秒重算容量，取代旧的单向压制 `adjust_max_request`

**关键函数**:

- `host_of(url)`: 从 URL 提取主机名（截到首个 `/`、`?`、`#` 为止，小写、保留端口）作为熔断 key；空串或解析异常统一归 `"unknown"`（互不相关的坏 URL 共享同一熔断 key，粗粒度兜底）
- `allow(key)`: 预检指定 host 是否已熔断，返回 False 时调用方应跳过本轮探测；half-open 态带探针租约（见 `PlatformBreaker`）
- `record_error(key)` / `record_success(key)`: 按 host 计入成功/失败样本，驱动熔断器状态迁移

**接线点**（固定几处，不改动 50+ 平台分派函数）:

- `notify.record_error/record_success` 增 `key` 形参，委托给 `scheduler`
- `start_record` 入口在平台分派前做 `scheduler.allow(record_host)` 熔断预检
- `start_record` 解析成功分支（`anchor_name` 非空）上报 `record_success(record_host)`——half-open 探针依赖本轮结果闭环，探针房间进入长时间录制期间同 host 其余房间不再饿死
- `check_subprocess` 的录制循环受 `recording_semaphore` 管控
- `main()` 首轮初始化调度器，`semaphore` / `recording_semaphore` 指向其属性

**线程安全**（2026-08-27 加固）: 配置字段（模式/配置上限/活跃数/错误窗口）由 main 主线程与 `adjust_loop` 守护线程并发读写，`_compute_capacity()` 单次加锁快照全部可变输入、`set_configured_limit()` / `set_dynamic_mode()` 锁内写入（幂等检查与写入原子）；`Lock` 不可重入，所有 setter 在锁释放后再调 `recompute()`，全链路无嵌套持锁。

**配置项**:

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| 最大同时录制数(0为不限制) | 0=不限制（同时兼作并发模式开关：0=动态调速，非0=固定并发） | 0 |
| 同一时间访问网络的线程数 | 动态模式下为容量下限之一；固定模式下为固定并发限制值 | 3 |

**测试**: `tests/test_scheduler.py` 共 16 用例，覆盖信号量调容、熔断器状态机（含探针租约超时自愈）、自适应容量缩放/下限、固定并发模式、按 key 隔离、录制并发软上限等。

## 关键类与函数

### 签名算法 (`src/ab_sign.py`)

抖音平台的 A-Bogus 签名算法，包含：

- SM3 哈希
- RC4 加密
- 复杂的参数混淆

### 配置文件管理 (`src/utils.py`)

```python
def read_config_value(file_path: Path, section: str, key: str) -> str | None
def update_config(file_path: Path, section: str, key: str, new_value: str) -> None
```

### 错误处理装饰器

```python
@trace_error_decorator
async def some_function():
    # 自动捕获并记录异常（支持同步和异步函数）
    pass
```

**实现特点**:

- 使用 `asyncio.iscoroutinefunction()` 检测函数类型
- 异步函数使用 `async wrapper` 正确 `await` 并捕获异常
- 统一返回 `{}` 空字典，与调用方 `.get()` 用法兼容
- `execjs.ProgramError` 单独处理（Node.js 环境问题）

### 动态并发调整

`main.py` 中实现的基于错误率的动态并发数调整机制，避免被平台限流。

### 并发调度器 (`src/scheduler.py`)

```python
# 可运行时调容信号量
class ResizableSemaphore:
    def set_value(self, n: int) -> None: ...
    def acquire(self) -> None: ...
    def release(self) -> None: ...

# 按平台熔断器
class PlatformBreaker:
    def allow(self) -> bool: ...
    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...

# 调度中枢
class ConcurrencyScheduler:
    network_semaphore: ResizableSemaphore
    recording_semaphore: ResizableSemaphore
    def set_dynamic_mode(self, enabled: bool) -> None: ...
    def set_recording_limit(self, limit: int) -> None: ...
    def allow(self, key: str) -> bool: ...
    def record_error(self, key: str) -> None: ...
    def record_success(self, key: str) -> None: ...

# 辅助函数
def host_of(url: str) -> str: ...
```

## 依赖关系

### Python 依赖 (`requirements.txt`，与 `pyproject.toml [project.dependencies]` 保持一致)

| 包名 | 版本要求 | 用途 |
| --- | --- | --- |
| requests | >=2.34.2 | 同步 HTTP 请求（现仅 ffmpeg / node 安装下载脚本使用；各平台解析走 httpx 异步面） |
| urllib3 | >=2.7.0 | 传输层（requests 之下；显式声明以防解析回退落入 CVE-2026-44431 区间） |
| httpx[http2] | >=0.28.1 | 异步 HTTP 客户端（含 HTTP/2，`src/async_http.py` 并发抓取流地址） |
| h2 | >=4.4.1 | httpx `http2=True` 的运行期依赖（`Client.__init__` 内 `import h2`） |
| socksio | >=1.0.0 | httpx SOCKS 代理（socks5/socks5h）的运行期依赖（传输层内 `import socksio`） |
| loguru | >=0.7.3 | 结构化日志（`src/logger.py` 统一封装） |
| pycryptodome | >=3.23.0 | 加密算法（SM3、RC4、AES） |
| distro | >=1.9.0 | Linux 发行版检测 |
| tqdm | >=4.69.0 | 下载进度条 |
| exejs | >=1.0.1 | JavaScript 执行引擎（PyExecJS 的活跃维护继任者，优先使用） |
| PyExecJS | >=1.5.1 | JS 执行引擎回退兼容（exejs 未安装时使用） |
| customtkinter | >=6.0.0 | 现代化 GUI 框架 |
| pystray | >=0.19.5 | 系统托盘（GUI / Web 托盘模式） |
| Pillow | >=12.3.0 | 图像处理（托盘图标生成） |
| fastapi | >=0.140.0 | Web 管理面板后端框架 |
| starlette | >=1.3.1 | ASGI 工具集（fastapi 传递依赖，`src/web_api.py` 直接导入故显式声明；下限 0.49.1→1.0.1→1.3.1 见 CVE/PYSEC 说明） |
| uvicorn[standard] | >=0.51.0 | ASGI 服务器 |
| python-multipart | >=0.0.32 | 表单/文件上传解析 |
| pydantic | >=2.13.4 | 请求模型校验 |
| websockets | >=14.0 | 弹幕 WebSocket 客户端（`src/ws_client.py`；`additional_headers` 为 14.0+ API） |
| protobuf | >=6.33.5,<8 | 抖音弹幕协议解码（`src/proto/douyin_pb2.py`；上限 <8 为 gencode 兼容护栏） |
| brotli | >=1.2.0 | B站弹幕解压（protover=3） |
| PyYAML | >=6.0.3 | YAML 翻译目录支持（`i18n/zh_TW.yaml`） |

> 注 1：[历史注] 旧版此处记录「Weverse 平台认证由 `src/weverse_auth.py` 实现、不再依赖 pip 上的 `weverse` 包」。
> 该模块（连同 `tests/test_weverse_auth.py`）已于 2026-09-23 整体删除，结论仅作备查：pip 上的 `weverse`
> 包会拉入已废弃的 pycrypto==2.6.1（Python 3.10+ 无法编译），**任何时候都不要加入依赖清单**。
>
> 注 2：可执行文件打包需 PyInstaller，属于构建期可选依赖：`pip install .[build]`
>
> （对应 `pyproject.toml` 的 `[project.optional-dependencies] build`）。

### 外部依赖

| 依赖 | 用途 | 安装方式 |
| --- | --- | --- |
| FFmpeg | 视频录制与转码 | Windows 内置（`ffmpeg/`），Linux/macOS 手动安装；Docker 内 apt 安装 |
| Node.js | 运行 JavaScript 签名算法 | Windows 自动安装（`node/`），Linux 需包管理器安装；Docker 内 apt 安装 Node 24 |

### 模块依赖关系图

```
main.py
├── src/spider.py
│   ├── src/room.py
│   ├── src/ab_sign.py
│   ├── src/async_http.py
│   │   └── src/http_config.py
│   ├── src/http_config.py
│   └── src/utils.py
├── src/stream.py
│   ├── src/spider.py
│   └── src/async_http.py
├── src/scheduler.py (并发调度中枢)
│   ├── ResizableSemaphore (可运行时调容信号量)
│   ├── PlatformBreaker (按平台熔断器)
│   └── ConcurrencyScheduler (调度中枢)
├── src/notify.py (record_error/record_success 委托调度器)
├── src/http_config.py
├── src/async_http.py
├── src/utils.py
│   └── src/logger.py
├── msg_push.py
└── src/ffmpeg_install.py

src/__init__.py (弹幕注册表/工厂)
├── get_danmaku_collector() → src/collector.py
│   └── DanmakuCollector
│       ├── src/base.DanmakuBase (契约)
│       ├── src/platforms/<X>Danmaku (各平台实现)
│       │   ├── src/ws_client.WsClient (传输，proxy=None 直连)
│       │   ├── src/cookie_cache.fetch_cookies (访客 cookie)
│       │   ├── src/proto.douyin_pb2 (抖音解码)
│       │   └── src/ttwid.get_ttwid (抖音动态 ttwid)
│       ├── src/srt_writer.SrtWriter (落 SRT)
│       └── src/danmaku_monitor.get_hub() (监控枢纽，进程单例)

web.py
├── src/web_api.py
│   ├── src/web_config.py
│   └── main.py (get_status 等函数)
└── web/ (静态资源)
```

## 配置文件说明

### 主配置文件 (`config/config.ini`)

#### [录制设置] 节

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| language | 界面语言；留空跟随系统，支持常见语言别名并归一到 `zh_CN` / `en_US` / `en_GB` / `zh_TW` | （空） |
| 是否跳过代理检测(是/否) | 跳过启动时代理可用性检测 | 是 |
| 是否启用日志文件(是/否) | 将运行日志写入 `logs/` | 是 |
| 直播保存路径(不填则默认) | 录制文件保存路径；留空使用 `downloads/` | （空） |
| 是否自动更新主播名(是/否) | 主播改名后同步 URL 配置与录制目录/文件 | 是 |
| 保存文件夹是否以作者区分 | 按主播名创建子目录 | 是 |
| 保存文件夹是否以时间区分 | 按时间创建子目录 | 否 |
| 保存文件夹是否以标题区分 | 按直播标题创建子目录 | 否 |
| 保存文件名是否包含标题 | 在录制文件名中加入直播标题 | 否 |
| 是否去除名称中的表情符号 | 清理主播名/标题中的 emoji | 是 |
| 视频保存格式ts\ | mkv\ | flv\ | mp4\ | mp3音频\ | m4a音频 | 录制输出格式 | ts |
| 原画\ | 超清\ | 高清\ | 标清\ | 流畅 | 默认录制画质 | 原画 |
| 自定义画质选项(逗号分隔) | GUI/Web 可选画质子集；留空使用内置全集 | （空） |
| 是否使用代理ip(是/否) | 是否启用录制代理 | 否 |
| 代理地址 | 代理服务器地址；裸 `ip:端口` 自动补 `http://` | （空） |
| 同一时间访问网络的线程数 | 网络请求并发数 | 3 |
| 最大同时录制数(0为不限制) | 全局录制并发上限 | 0 |
| 循环时间(秒) | 直播状态检测间隔；运行时下限钳制为 30 秒 | 120 |
| 排队读取网址时间(秒) | 逐条调度直播间 URL 的间隔 | 0 |
| 是否显示循环秒数 | 是否显示轮询倒计时 | 否 |
| 是否显示直播源地址 | 是否在日志中显示解析后的源地址 | 否 |
| 分段录制是否开启 | 是否按时长分段输出 | 是 |
| 是否启用HLS采集(是/否) | 优先使用 HLS；关闭或不可达时走非 HLS 候选 | 是 |
| HLS采集排除平台(逗号分隔) | 命中平台恒按 FLV 采集；留空不排除任何平台 | （空） |
| 是否启用https录制 | 开启时使用 HTTPS 并跳过证书校验；关闭时恢复 HTTP/默认校验 | 否 |
| 禁用SSL证书验证的平台(逗号分隔) | 平台级证书校验豁免；启动时补齐虎牙/B站必需项 | 虎牙直播,B站直播 |
| 录制空间剩余阈值(gb) | 可用磁盘空间低于该值时停止新录制 | 1.0 |
| 视频分段时间(秒) | 视频分段时长 | 1800 |
| 录制完成后自动转为mp4格式 | 录制结束后自动转封装为 MP4 | 否 |
| mp4格式重新编码为h264 | MP4 后处理时重新编码为 H.264 | 否 |
| 追加格式后删除原文件 | 后处理成功后删除原始录制文件 | 是 |
| 生成时间字幕文件 | 生成时间轴字幕文件 | 否 |
| 是否录制完成后执行自定义脚本 | 录制完成后执行用户命令 | 否 |
| 自定义脚本执行命令 | 自定义脚本/命令内容 | （空） |
| 使用代理录制的平台(逗号分隔) | 按域名子串匹配并走代理 | tiktok, sooplive, pandalive, winktv, flextv, popkontv, twitch, liveme, showroom, chzzk, shopee, shp, youtu, faceit |
| 额外使用代理录制的平台(逗号分隔) | 在内置代理平台列表之外追加平台 | （空） |
| 是否录制弹幕(是/否) | 将弹幕落为 SRT 字幕 | 否 |
| 是否弹幕监控(是/否) | 实时查看弹幕但不要求落盘 | 否 |
| 弹幕分片时长(秒) | 弹幕 SRT 分片时长 | 1800 |
| 弹幕录制平台(逗号分隔) | 允许采集弹幕的平台白名单 | 斗鱼直播,B站直播,虎牙直播,抖音直播,TwitchTV |
| 单次录制时长上限(秒,0为不限制) | 单次 ffmpeg 录制的最长时长；0 表示不限制 | 21600 |

#### [推送配置] 节

| 配置项 | 说明 | 默认值 |  |  |  |  |  |  |
| -------------------- | ------------------------------------------------------------------------ | ------ | -- | -- | ---- | ---- | ------------- | --- |
| 直播状态推送渠道 | 可选渠道：微信 | 钉钉 | tg | 邮箱 | bark | ntfy | pushplus（可多选） | (空) |
| 钉钉推送接口链接 | 钉钉 Webhook | (空) |  |  |  |  |  |  |
| 微信推送接口链接 | Server酱 URL | (空) |  |  |  |  |  |  |
| bark推送接口链接 | Bark API | (空) |  |  |  |  |  |  |
| bark推送中断级别 | Bark 中断级别，可选 critical（重要提醒）/ active（默认）/ timeSensitive（时效性）/ passive（静默） | active |  |  |  |  |  |  |
| tgapi令牌 | Telegram Bot Token | (空) |  |  |  |  |  |  |
| tg聊天id | 聊天 ID | (空) |  |  |  |  |  |  |
| smtp邮件服务器 | SMTP 服务器 | (空) |  |  |  |  |  |  |
| 是否使用SMTP服务SSL加密(是/否) | 是否启用 SMTP SSL 加密（留空视为「是」）；启用时端口通常为 465 | 是 |  |  |  |  |  |  |
| ntfy推送地址 | NTFY 服务地址 | (空) |  |  |  |  |  |  |
| pushplus推送token | PushPlus Token | (空) |  |  |  |  |  |  |
| 只推送通知不录制(是/否) | 是否仅通知不录制 | 否 |  |  |  |  |  |  |

#### [Cookie] 节

各平台的 Cookie 配置（录制部分平台必填）。特殊键：

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| 抖音cookie | 录制抖音必填，至少包含 ttwid，留空将触发风控 | (空) |
| ttwid | 可单独固定抖音 ttwid（填 `ttwid=xxx` 或仅值均可）；留空则自动获取，填写后优先于自动获取（`src/ttwid.py`） | (空) |

#### [Authorization] 节

特殊平台的 Token 配置

#### [账号密码] 节

部分平台的账号密码配置

#### [Web] 节

Web 管理面板配置（`web.py` 模式专用）

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| web_host | 监听地址（Docker 内需设为 0.0.0.0） | 127.0.0.1 |
| web_port | 监听端口 | 8000 |
| web_auth_enable | 是否启用密码认证。关闭时 API 禁止改写 [Recorder]/[Push] 危险配置（如自定义脚本），但仍允许修改 [Web] 设置 | false |
| web_password | 登录密码（认证开启时必填，PBKDF2-HMAC-SHA256 哈希存储） | (空) |
| web_token_expiry | Token 有效期（秒） | 86400 |
| web_show_console | 是否显示控制台窗口（false 时后台隐藏运行） | true |
| web_minimize_to_tray | 控制台最小化到系统托盘（仅 Windows 生效；关闭按钮被禁用，退出请用托盘图标「退出程序」） | true |
| web_trusted_proxy | 反向代理场景下的可信代理列表（逗号分隔直连 IP，如 127.0.0.1）：仅列表内的直连对端才信任 `X-Forwarded-For` 解析真实客户端 IP（防伪造头绕过登录限流）；留空 = 一律使用直连对端地址。未启用认证且公网暴露时请勿填写 | (空) |
| web_allowed_hosts | 除服务端自动放行的 Host 之外，额外登记的域名白名单（逗号分隔，支持 `*.example.com` 后缀匹配）。Host 判定规则见 `src/web_config.py::is_host_allowed`：**IP 字面量**与**无点号单标签名**天然放行（DNS 重绑定至少要一个多级注册域名），**多级域名**必须显式登记否则 400 拒绝；`web_host` 绑到 `0.0.0.0`/`::` 时不入名单（通配符绑址本身不是合法 Host 值）。故仅当 `web_host` 为通配绑址且用**域名**访问面板时才需要填写；以 IP 直连或本机 `127.0.0.1` 默认场景无需填写 | (空) |

### 直播间配置文件 (`config/URL_config.ini`)

**格式**:

```ini
# 基础格式
https://live.douyin.com/745964462470

# 指定画质（画质,直播间地址）
超清，https://live.douyin.com/745964462470

# 指定画质和主播名（画质,直播间地址,主播:名称）
高清，https://live.bilibili.com/123456，主播: B站主播

# 注释直播间（在地址前加 #）
# https://live.douyin.com/123456789
```

**主播名自动更新**: 开启 `config.ini` 的 `[录制设置] 是否自动更新主播名(是/否)`（默认开启）后，每轮轮询解析到平台最新主播名与当前使用名不一致时，会自动完成：

1. 重命名保存目录中旧主播名命名的文件夹（`{保存路径}/{平台}/{旧主播名}`，目标已存在则逐项合并）；
2. 同步重命名文件夹内（含日期/标题子目录）所有以旧主播名为前缀的录制文件（`{旧主播名}_*`）及弹幕 SRT/时间字幕等同前缀产物，并把以 `_{旧主播名}` 结尾的标题目录（`{标题}_{旧主播名}`）一并改名；
3. 更新 `URL_config.ini` 对应行的主播名字段（按 URL 精确匹配该行，保留画质段、`#` 注释前缀与行尾换行风格，全角冒号统一半角，幂等）。

**触发与安全性**

- 触发点在每轮解析直播数据之后、录制启动之前，此刻该房间线程必然不在录制中（录制期间阻塞在 ffmpeg 守护里），因此改名不会触碰正在写入的文件，进行中的录制不受影响。
- 跳过条件：`platform == "自定义录制直播"`（其主播名含每轮随机 UUID，不应反复触发改名），或平台返回名为「空白昵称」等无效名。
- 同步顺序：**先改文件系统、后写配置文件**；两者全部成功才切换本轮使用名。任一失败（如配置文件被编辑器锁定、目录改名失败）保持旧名，下轮轮询自动重试（已完成的目录改名幂等，不会重复操作）。
- 被后台转码/播放器占用的个别文件改名失败仅告警跳过、不阻塞整体，其余文件照常处理，下轮补齐；同时清理旧名残留的录制状态条目（`recording` / `recording_time_list`），避免监控页长期挂旧名。
- 配置写入持 `file_update_lock`，与录制线程的 `update_file` / Web API 写入互斥，避免半写。

关闭该选项则保持手动填写的名称不变。

## 运行方式

### 方式 1: 源码运行

#### 前置要求

- Python 3.14+
- FFmpeg
- Node.js

#### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

#### 命令行模式

```bash
python main.py
```

#### GUI 图形界面模式

```bash
python gui.py
```

#### Web 管理面板模式

```bash
python web.py
# 默认监听 http://localhost:8000
```

### 方式 2: Docker 运行

#### Dockerfile 多阶段构建说明（基础镜像 `python:3.14-slim-bookworm`）

```dockerfile
# 阶段 1: builder
# - 仅安装 build-essential（编译无二进制轮子的依赖）
# - 创建 Python 虚拟环境 /opt/venv 并安装 requirements.txt
#   （Node.js 只在运行时需要，builder 阶段不安装）

# 阶段 2: runtime
# - 精简基础镜像 + apt 安装 ffmpeg / nodejs(24 LTS) / tzdata / procps
# - 从 builder 复制 /opt/venv 虚拟环境
# - 非 root 用户 recorder(uid=1000) 运行
# - HEALTHCHECK 兼容 main.py 与 web.py 两种模式（pgrep）
# - ENTRYPOINT ["python", "main.py"]，EXPOSE 8000（Web 模式用）
```

**`.dockerignore` 要点**（2026-08-28 同步后）：

- 排除平台二进制（`ffmpeg/`、`node/`，容器内 apt 安装）、`config/*.ini`（运行时挂载）、`typings/`、`build_exe.py`、根目录 `index.html`（独立的 M3U8 播放器页，面板用 `web/`）等桌面/构建专用文件；
  [2026-09-21 修订：本行原列 `gui_legacy.py`，该文件已于 v4.1.0-dev / 2026-09-10 删除且 `.dockerignore` 中无该条目，属 MIN-15 的第 4 处陈旧引用，就地清除]
- **保留 `i18n/**/*.mo` 编译翻译文件与 `i18n/*.json`、`i18n/*.yaml` 多语言目录** ——
  运行时必需（gettext / JSON / YAML 三种翻译目录格式）且 Dockerfile 不会重新编译/生成，
  仅排除 `.po` 源文件与编译脚本；
- 排除本地工具 / AI 助手生成目录（`.mimosa/`、`.qoder/`、`.agents/`、`.pnpm-store/`、`.dsh-validation/`、`.ego-browser-test/`、`.plugin-src/`、`pytest-cache-files-*/` 等，与 `.gitignore` 同源维护）；
- 排除镜像运行不消费的内容：`uv.lock`（镜像走 pip + requirements.txt）、`scripts/`（维护脚本，运行时链路零引用）、`tests/`、`AGENTS.md` / `README_EN.md` / `CODE_WIKI_EN.md` 等文档、`.coveragerc-concurrency`（CI 专用）。

#### 使用 docker compose (推荐)

仓库根目录的 `docker-compose.yaml` 已定义三个服务（共享同一镜像，通过 YAML 锚点复用配置）：

| 服务 | 入口 | 启动命令 | 端口 |
| --- | --- | --- | --- |
| `recorder`（默认） | `python main.py` | `docker compose up -d` | 无（纯 CLI） |
| `web`（profile） | `python web.py` | `docker compose --profile web up -d` | `127.0.0.1:8000:8000` |
| `gui`（profile） | `python gui.py` | `docker compose --profile gui up -d` | 无（需 X11） |

统一挂载卷：`./config`、`./downloads`、`./logs`、`./backup_config`。

> ⚠️ **Web 模式必读**：`web.py` 默认监听 `127.0.0.1:8000`，容器内必须在
>
> `config/config.ini` 的 `[Web]` 节设置 `web_host = 0.0.0.0`，宿主机端口映射才能访问；
>
> 同时强烈建议开启 `web_auth_enable = true` 并配置密码。

## 打包与发布

本项目提供一键式可执行文件打包（`build_exe.py`）与跨平台自动构建发布（`GitHub Actions`），将 **CLI / GUI / Web 三个入口**统一构建为可分发的发布目录。

### 1. 打包脚本 `build_exe.py`

PyInstaller `onedir` 模式 + `contents_directory='_internal'`，动态生成 `.spec` 文件后调用 PyInstaller 完成**三入口共享依赖**构建：

| 产物（exe 同级） | 入口 | 模式 |
| --- | --- | --- |
| `DouyinLiveRecorder(.exe)` | `main.py` | 控制台（CLI 录制核心） |
| `DouyinLiveRecorder-GUI(.exe)` | `gui.py` | 无控制台窗口（GUI） |
| `DouyinLiveRecorder-Web(.exe)` | `web.py` | 控制台（Web 管理面板，监听 `0.0.0.0:8000`） |

三个入口共用一个 `COLLECT`，依赖去重后体积约为独立打包的 1/3。

**用法**：

```bash
python build_exe.py              # 打包并生成 zip 产物
python build_exe.py --smoke      # 打包后额外运行冒烟测试（CI 推荐）
python build_exe.py --no-zip     # 仅打包不压缩
python build_exe.py --no-runtime # 跳过 ffmpeg/node 打包（交由用户运行时自动下载，减小体积）
python build_exe.py --dual       # 同时生成 lite（无运行时）与 full（下载并打包 ffmpeg+node）两个 zip
```

**数据文件与隐藏导入**：

- `datas`：`src/javascript`（JS 签名脚本）、`i18n`（翻译）、`web`（前端静态资源），均经 `__file__` 定位，PyInstaller 自动收进 `_internal/`；`collect_data_files('customtkinter')`（主题 JSON）。
- `config/` 不进 `_internal`，由 `copy_external_binaries()` 复制到 exe 同级（见目录规范）。
- `hiddenimports`：`i18n`、`src.async_http`（main.py 经 `__import__` 动态导入）、`h2`（httpx[http2] 懒加载）；`a_web` 额外 `collect_submodules('uvicorn')`（协议模块按字符串导入）。
- `excludes`：CLI 排除 GUI/Web 库（tkinter/customtkinter/pystray/PIL/fastapi/uvicorn/starlette）；GUI 排除 Web 库；Web 排除 GUI 库；三个入口均额外排除 `brotlicffi`（修复打包后 brotlicffi 模块缺失 `error` 属性的报错，httpx 无 brotli 时自动回退）。

**版本号**：从 `pyproject.toml` 的 `version` 字段解析（单一事实源），用于 zip 命名，解析失败回退 `0.0.0`。`main.py` 运行时同样从 `pyproject.toml` 动态读取版本号（优先 `importlib.metadata`，回退直接解析文件）。

### 2. 目录结构规范（打包产物）

采用 `onedir + contents_directory='_internal'` 后，PyInstaller 把依赖与经 `__file__` 定位的资源收进 exe 同级的 `_internal/`；而经 `sys.argv[0]`/`sys.executable` 定位的运行时资源由打包脚本在 `COLLECT` 之后复制到 exe 同级。最终产物结构：

```
dist/DouyinLiveRecorder/
├── DouyinLiveRecorder.exe          # CLI 录制核心
├── DouyinLiveRecorder-GUI.exe      # 图形界面
├── DouyinLiveRecorder-Web.exe      # Web 管理面板
├── config/                          # 配置目录（exe 同级，运行时直接读写）
├── ffmpeg/                          # FFmpeg 运行时（exe 同级，Windows 内置）
├── node/                            # Node.js 运行时（exe 同级，Windows 内置）
├── logs/                            # 日志目录（运行时默认创建于 exe 同级）
├── downloads/                       # 默认下载目录（config.ini 未指定时位于 exe 同级）
├── backup_config/                   # 配置备份目录（exe 同级）
└── _internal/                       # 依赖包 + src/ 及打包资源统一管理
    ├── (Crypto/ PIL/ certifi/ h2/ pydantic/ customtkinter/ watchfiles/ websockets/ yaml/ + 运行库 .dll)
    ├── src/            src/javascript/
    ├── i18n/
    └── web/
```

**关键约定（硬性）**：

- `node/`、`ffmpeg/`、`config/` 与 exe 保持**同级**（而非 `_internal/`）。
- `src/` 及全部 Python 依赖包统一收进 `_internal/`。
- 运行时可写目录 `logs/`、`downloads/`（未通过 `config.ini` 的 `直播保存路径(不填则默认)` 指定时）、`backup_config/` 均默认创建在 **exe 同级目录**。

### 3. 路径收敛机制 `_app_root()`

项目存在"双轨路径"：`main.py`/`src/ffmpeg_install.py`/`src/__init__.py` 等用 `sys.argv[0]`/`sys.executable` 定位运行时资源；`src/logger.py`、`i18n.py`、`src/web_api.py` 等用 `__file__` 定位打包资源。冻结后前者指向 exe 同级（发布根），后者指向 `_internal/`。

为统一收敛，新增 `src/logger._app_root()`（与 `main.py` 内联同名函数）：

```python
def _app_root() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))  # = exe 同级
    return os.path.split(os.path.realpath(sys.argv[0]))[0]
```

- `main.py` 的 `script_path`、`src/__init__.py`、`src/node_install.py`、`src/ffmpeg_install.py` 的 `execute_dir` 均收敛到 exe 同级，使 `config/ffmpeg/node` 正确定位。
- `src/logger.py` 的 `script_path` 改为 `_app_root()`，使 `logs/`、`backup_config/` 落在 exe 同级。
- `gui.py` 新增 `self.app_root`：冻结时若 `script_dir` 为 `_internal` 则回退一层到发布根，config/downloads 据此定位；CLI 子进程经同目录 `DouyinLiveRecorder.exe` 拉起（见下）。
- `i18n.py` 支持 `_internal/i18n` 与 `i18n/` 双路径检测。

### 4. 冻结版适配要点

- **GUI 子进程拉起（关键修复）**：`gui.py` 冻结后 `sys.executable` 指向 GUI 自身，原 `[sys.executable, main.py]` 会无限递归拉起 GUI。改为冻结时直接调用同目录的 `DouyinLiveRecorder.exe`，源码运行保持原样。
- **GUI 子进程 pythonw 兼容（2026-08-09）**：源码模式下若 GUI 经 `pythonw.exe` 启动，`sys.executable` 指向 pythonw（GUI 子系统、无控制台），原 `[sys.executable, main.py]` 会让录制核心也以 pythonw 运行——`CREATE_NEW_CONSOLE` 对其无效，`AttachConsole(pid)` 必失败、CTRL_BREAK 永远送不到、停止只能硬杀（ffmpeg 孤儿化）。现检测解释器 basename 以 `pythonw` 开头时改用同目录 `python.exe`（console 子系统）拉起录制核心；打包版（CLI exe `console=True`）不受影响。
- **GUI 停止录制优雅退出（2026-08-09）**：`_send_ctrl_break_to_child` 失败时不再只 `proc.terminate()`（`TerminateProcess` 硬杀、ffmpeg 孤儿化且 `wait()` 立即成功绕过整树清理），改为 `taskkill /F /T /PID` 整树终止；日志按路径区分"优雅退出"与"硬杀路径"，不再谎报 ffmpeg 已清理。
- **中文 UTF-8 编码（关键修复）**：冻结后子进程 stdout 为管道，Python 回退到 GBK 写输出，而 GUI 以 UTF-8 读取管道 → 中文乱码（如 `自动获取 Cookie ttwid 成功` 变成乱码）。在 `main.py`/`gui.py`/`web.py` 顶部加入 `_fix_encoding()`：Windows 下 `sys.stdout/stderr.reconfigure(encoding='utf-8', errors='replace')` + `ctypes.windll.kernel32.SetConsoleOutputCP(65001)/SetConsoleCP(65001)`；非 Windows 仅 reconfigure。stream 加 `None`/`hasattr` 保护（windowed exe 的 stdout 可能为 `None`）。`web.py` 原有 `reconfigure(errors='replace')` 升级为同时设 `encoding='utf-8'`。

### 5. 冒烟测试

`build_exe.py --smoke` 在打包后自动运行三项验证（CI 推荐开启）：

- **CLI**：启动数秒，确认进入监控循环且输出无 `Traceback`/`ImportError`/`ModuleNotFoundError`。
- **Web**：HTTP 探活 `http://127.0.0.1:8000/`，返回 200 视为面板可用；同时验证内置 ffmpeg 被命中（不触发下载）。
- **GUI**：启动 8 秒确认进程存活无崩溃（无显示环境 `DISPLAY` 未设置时自动跳过）。

冒烟前会向 exe 级 `config/URL_config.ini` 写入一条注释 URL，避免 CLI 因 URL 列表为空而阻塞在 `input()`。

### 6. GitHub Actions CI 静态验证（`ci.yml`）

工作流文件：`.github/workflows/ci.yml`，在 push 到 main / PR 时运行，确保代码风格、类型安全与功能正确性在合入前通过验证（2026-08-28 优化后结构如下）。

**统一策略**：

- `setup` job 集中声明**共享常量**（Python 版本矩阵 / Node 版本 / black / isort / mypy 固定版本号）并执行路径过滤，常量输出至 job outputs 供各 job 与 `strategy.matrix` 引用（matrix 无法引用 env 上下文），是全工作流的单一事实源；
- **actions 大版本统一 v7**（`checkout` / `setup-python` / `setup-node` / `upload-artifact`），与 build-release.yml 完全一致；
- **网络安装重试统一经 `.github/actions/retry` 复合动作**（线性退避 ×3；`command` / `label` / `attempts` / `backoff` 可参数化）——pip / apt 安装共 9 处调用，重试策略只在 action.yml 一处维护，禁止 job 内重新内联重试循环；
- **apt 强化参数**（对齐 build-release.yml 的 Linux 构建）：`DEBIAN_FRONTEND=noninteractive` + `Acquire::Retries=3` + `--no-install-recommends`；
- 每个 job 显式 `timeout-minutes`；同分支/PR 新推送 `cancel-in-progress: true` 取消旧运行（快速反馈，与发布流的不可取消策略有意区分）；
- pip 缓存统一以 `hash(requirements.txt + pyproject.toml)` 为 key（仓库无 lock 文件参与安装）。

**路径过滤**：`setup` job 使用 `dorny/paths-filter@v4` 检测变更文件类别，命中即运行全部下游 job。触发清单：Python 源码（`src/**`、根目录入口 `main.py`/`gui.py`/`web.py`/`i18n.py`/`msg_push.py`/`build_exe.py`）、`tests/**`、`scripts/**`、依赖清单（`requirements.txt` / `pyproject.toml` / `.coveragerc-concurrency`）、**`i18n/**`**、**`web/**`**、**`Dockerfile` / `docker-compose.yaml`**、工作流与复合动作（**`.github/workflows/**` / `.github/actions/**`**）。仅**纯文档（`*.md`）变更不触发**。**`i18n/**` 是触发条件**——纯翻译变更同样会跑 static job 的 compile_po --check 同步门禁；**`web/**` 亦是触发条件**（2026-09-20 补齐）——`web/app.js` 的 `parseConfigBool + CONFIG_*_TOKENS` 与 `src/config_bool.py` 是跨语言布尔口径不变量（AGENTS.md「布尔配置项统一解析口径」），改任一侧都须由 test job 跑 `tests/frontend/test_quality_ui.mjs` 回归锁（旧口径「纯前端 web/ 不触发」已被证伪，详见更新日志对应条目）。

**并行 jobs**（均 `needs: setup` 条件门控）：

| Job | 运行环境 | 内容 |
| --- | --- | --- |
| `static` | py3.14 | `black --check .` + `isort --check .` + `python scripts/check_version.py`（版本号单一事实源校验） + `python scripts/compile_po.py --check`（i18n po/mo 同步校验，零副作用） + `python scripts/check_annotations.py`（注释规范：禁 docstring / 密度下限 / 模块头，零副作用） |
| `typecheck` | py3.14 | 安装 requirements + 固定版 mypy/pytest 后运行无参 `mypy`（范围由 `pyproject.toml [tool.mypy].files` 定义） |
| `test` | py3.14 | `pytest --cov=src --cov-report=term-missing`（全局 `fail_under=50` 门禁，`fail-fast: false`）+ `scripts/check_coverage.py` 逐模块门禁 + coverage.xml 上传 + 可选 Codecov |
| `concurrency-test` | py3.14 | 并发专项：`COVERAGE_RCFILE=.coveragerc-concurrency` 下跑 `test_concurrency_rate_limit.py` + `test_concurrency.py` + `test_async_http_lock.py`（专用配置不设全局阈值） |
| `integration-verify` | py3.14 + Node 24 | apt 装 ffmpeg；验证 ffmpeg/node 二进制可发现，并调 `check_ffmpeg_installed()` / `check_nodejs_installed()` 验证探测逻辑 |
| `build-verify` | py3.14 打包解释器 | `build_exe.py --smoke --no-runtime --no-zip`（lite 打包 + CLI/Web/GUI 三入口冒烟，Linux 经 `xvfb-run -a`）；发布级完整打包留给 build-release.yml |
| `ci-summary` | — | 唯一 required check：汇总上游全部 job 结果（skipped 视为通过——路径过滤跳过不会让分支保护永久 pending） |

### 7. GitHub Actions 自动构建与发布（`build-release.yml`）

工作流文件：`.github/workflows/build-release.yml`（任务名 `Build (${{ matrix.os }})`）。

**触发方式**：

- 手动触发（`workflow_dispatch`，可选 `create_release` 输入）：默认仅构建并上传 artifact，勾选后亦创建 Release。
- 推送 `v*` 标签（如 `v4.0.9.1`）：构建 + 自动创建 GitHub Release 并附产物（`permissions: contents: write`，仅 build / release 相关 job 授予）。

**构建矩阵**：`windows-latest` / `ubuntu-latest` / `macos-latest`，Python 3.14（`fail-fast: false`；与 ci.yml build-verify 的打包解释器同值，保证「CI 验证的打包环境 == 实际发布的打包环境」）。

**流程**：

1. `prepare` job：用 tomllib 从 pyproject.toml 提取版本号并校验 tag 一致（打错 tag 直接失败），跑 `check_version.py` 确认各消费方动态读取。
2. `release-create` job：发版路径下**预创建** Release 记录（单例 job，消除多平台 build 并发创建同一 Release 的竞态；不传 files）；手动发版路径在此补建轻量 tag（Release 必须挂在 tag 上）。
3. build job（矩阵）：各平台以系统包管理器装 ffmpeg 供冒烟——Windows `choco`、Linux `apt`（额外 `xvfb`，GUI 冒烟需虚拟显示）、macOS `brew`（`brew trust aws/tap` 为独立幂等步骤，`HOMEBREW_*` 变量在命令内 export）；**全部网络安装命令经 `.github/actions/retry` 复合动作包装**（线性退避 ×3，系统包管理器退避 15s、pip 10s）；依赖为 `pip install -r requirements.txt` + `pip install ".[build]"`。
4. `python build_exe.py --smoke --dual`（Linux 用 `xvfb-run -a` 包裹）：PyInstaller 只跑一次；出包前先清 `dist/` 内上一轮残留的 `DouyinLiveRecorder-v*.zip`（否则会被 `path: dist/*.zip` 连同本轮一起扫进附件），随后先产 **lite** zip（不含 ffmpeg/node，运行时自动下载）→ 下载运行时 → 再产 **full** zip（内置运行时，约 300MB）；两次 `make_zip` 的**返回路径**必须互不相同且都真实落件，否则当场 `SystemExit`。冒烟排在**两个** zip 之后（MID-2254），跑的是已装满运行时的发布目录——不是 lite 版本。
5. 产物发布：发版路径（tag / 手动勾选 create_release）由 build job 经 `softprops/action-gh-release@v3` 把 zip **直传 Release**（显式 `tag_name` 与 release-create 指向同一 Release，GitHub 支持同 Release 并发上传不同 asset）；仅构建路径走 `upload-artifact@v7`（`compression-level: 0` 跳过二次压缩，留存 30 天供人工取回）。
6. `release` job（发版路径）：`gh release download` 拉回已发布附件校验齐全（3 平台 × lite/full = 6 个 zip，缺失即失败不发布残缺 Release），生成 `SHA256SUMS.txt`，最后经 `softprops/action-gh-release@v3` 补传校验和并写发版说明（`generate_release_notes: true`）。

**产物命名**：`DouyinLiveRecorder-v{version}-{os}-{arch}-{lite|full}.zip`（如 `DouyinLiveRecorder-v4.0.9.1-windows-amd64-full.zip`）。

### 8. 本地打包步骤

```bash
pip install pyinstaller          # 安装打包器
python build_exe.py --smoke      # 打包 + 冒烟测试
python build_exe.py --smoke --dual  # 与 CI 一致：lite + full 双产物
# 产物：dist/DouyinLiveRecorder/ 发布目录 + dist/DouyinLiveRecorder-vX.Y.Z-*.zip
```

注意：本仓库为本地副本，工作流需推送至 GitHub 仓库后才可运行。lite 产物（及 CI Linux/macOS 产物）不含 `ffmpeg`/`node`，首次运行会自动下载。

## 设计模式

### 1. 适配器模式 (Adapter Pattern)

各直播平台的 API 接口被统一适配为相同的调用接口，`spider.py` 和 `stream.py` 中实现。

### 2. 装饰器模式 (Decorator Pattern)

`trace_error_decorator` 用于错误追踪，`utils.py` 中实现。

### 3. 策略模式 (Strategy Pattern)

不同的消息推送渠道（钉钉、微信、TG 等）实现为独立函数，运行时根据配置选择。

### 4. 单例模式 (Singleton Pattern)

日志配置通过模块导入副作用实现单例，`src/logger.py` 中实现。

### 5. 模板方法模式 (Template Method Pattern)

各平台的录制流程遵循相同的模板：检测 → 获取流 → 录制 → 推送。

### 6. 工厂 / 注册表模式 (Factory + Registry Pattern)

弹幕子系统通过 `src/__init__.py` 的 `get_danmaku_class(platform)` 注册表（中文平台名 → 弹幕类）与 `get_danmaku_collector(...)` 工厂统一创建各平台采集器；`main.py` 按平台标识取采集器，无需感知具体平台实现。新增弹幕平台只需在注册表登记并实现 `DanmakuBase` 的 `start/stop/heartbeat/decode_message` 四个抽象方法，对调用方零侵入。

## 常见问题排查

### 问题 1: 提示缺少 FFmpeg

**解决**:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
程序已内置，无需安装
```

### 问题 2: 提示缺少 Node.js

**解决**:

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Windows
程序会自动下载安装
```

### 问题 3: 抖音风控无法获取数据

**风控特征（实测）**:

- 风控信号是 **HTTP 200 + 空响应体**，不是 4xx。排查解析失败时先看 `len(response.text)`，为 0 基本就是 UA/Cookie 被拒
- 旧移动端 UA 会被静默限流（`iesdouyin.com` 接口必现），需使用桌面 Chrome UA（`room.DESKTOP_UA`）
- `iesdouyin.com/share/user/<sec_uid>` 已是 JS 反爬壳页，页面内无 `unique_id`，任何 HTML 正则都不可靠
- `web/enter` 接口偶发 `status_code=10002 unknown error` 属瞬时软拒绝（风控/缺 msToken/限流），代码已做静默重试 1 次，属正常容错，不代表房间不可用

**解决**:

- 更新 Cookie
- 降低循环监测频率
- 更换 IP
- 更新 UA（使用 `room.DESKTOP_UA` 桌面 Chrome UA）
- 若日志出现 `10002` 后 HTML 兜底成功，属正常链路，无需处理

### 问题 4: HLS 校验失败日志空白 / 总回退 FLV

**现象**（日志连续出现，且无任何可排障信息）：

```
get_response_status 校验失败（判定为不可达）:      ← 消息是空的
HLS URL validation failed, falling back to FLV    ← 原因完全不可见
```

**根因**（三层，均已修复于 2026-08-05）：

- 异常日志只打印 `{e}`，而 Windows 下 `socket.timeout` / `TimeoutError` 的 `str()` 返回**空字符串**，导致超时异常打出来是空白
- `main.py::_validate_stream_url` 用 `except Exception: return False` 把失败原因全部吞掉，回退时无任何线索
- m3u8 源 HEAD 探测只覆盖 `400/401/403/405`，**404 直接判不可达**；且 `select_source_url` → 校验调用**不透传代理**，TikTok 等境外平台直连校验必超时误判

**修复后**：异常日志带 URL + 异常类型；所有失败路径记录 warning（含 status_code / content-type）；m3u8 HEAD 非 2xx（含 404）一律补 Range GET 探测；`select_source_url` 透传 `proxy_addr`。重新运行后日志会直接给出真实原因（如 `ConnectTimeout`、`HEAD=404, Range-GET=403`）；若仍不可达则是 CDN 域名被墙或主播流地址已失效等环境问题，而非代码误判。

### 问题 5: 弹幕连接失败 "connecting through a SOCKS proxy requires python-socks"（系统代理冲突）

**现象**（B站及复用 `WsClient` 的所有平台弹幕连接断开，日志可见）：

```
[弹幕采集]BilibiliDanmaku 连接关闭: connecting through a SOCKS proxy requires python-socks
```

**前置两个已修复子问题**（均为真实缺陷，但非最终根因）：

- **短号 room_id 未转真实 room_id**：`get_bilibili_danmaku_info` 曾直接用 URL 短号（如 `live.bilibili.com/462`）请求 getDanmuInfo，B站返回的 token 与真实房间不匹配，join 后收不到弹幕；现先调 `room/v1/Room/room_init` 把短号转真实 room_id（462 → 763679）再走后续流程（`src/spider.py`）。
- **心跳协程从未被 await**：`BilibiliDanmaku.heartbeat` 是 `async def`，但 `WsClient._heartbeat_loop` 曾直接 `self._on_heartbeat()` 调用未 await，B站长连接几十秒无心跳被服务器断开；现检测 `inspect.isawaitable(result)` 后 `await result`（`src/ws_client.py`）。

**根因（系统代理"幽灵"）**：`websockets.connect(proxy=True)` 默认**自动探测并跟随代理**，经 `urllib.request.getproxies()` 获取代理配置；在 macOS 上该调用不只读 shell 环境变量，而是直接读**系统网络设置**（System Preferences → Network → Proxies）里的系统级代理。若代理工具（Clash 类）在系统设置写入了 HTTP/HTTPS/SOCKS 三层代理（如 `socks5://127.0.0.1:7890`），`env | grep -i proxy` 查不到（`scutil --proxy` 可读到），但 websockets 会跟随该 SOCKS 代理——而 SOCKS 协议需要 `python-socks` 库支持，未安装即报上述错误。视频拉流走 ffmpeg/自备 header，不经过 websockets，故录制不受代理影响；独立测试脚本因运行环境/系统代理状态不同而时好时坏。

**修复（弹幕直连）**：`src/ws_client.py` 的 `connect()` 显式传入 `proxy=None`，弹幕 WS 直连服务器、不感知系统代理与 `ALL_PROXY` 等环境变量：

```python
async with websockets.connect(
    url,
    additional_headers=self._headers,
    open_timeout=self.connect_timeout,
    ping_interval=None,   # 各平台自带心跳, 关闭库默认 ping
    max_size=None,
    ssl=self._ssl_context,
    proxy=None,           # 弹幕连接直连, 不跟随系统代理
) as ws:
```

该修复对**所有平台**（B站/斗鱼/虎牙/抖音/Twitch 等）弹幕连接统一生效（均复用 `WsClient`）。

**决策依据**：弹幕通道本就国内直连、不需出网代理，与"关闭代理录制"的整体直连语义一致；依赖最小化（不新增 `python-socks`）；不动系统设置；显式声明优于隐式探测（避免库升级改默认行为再踩坑）。若个别境外平台弹幕确需代理，可后续为 `WsClient` 增可选 `proxy` 参数按需透传，不全局跟随。

**验证**：无代理状态下完整跑通 `main.py`，弹幕正常落盘生成 SRT；`mypy src/ws_client.py` / `py_compile` 通过。排查弹幕异常先看 `logs/streamget.log`（DEBUG 记录采集线程启动 / 连接就绪 / 收到首条弹幕 / 连接关闭原因）。

### 问题 6: 抖音/斗鱼等平台状态"正在直播中"却完全不录制（无报错、无文件）

**现象**：`py web.py`（或 `python main.py`）运行期间，抖音、斗鱼房间每个监测周期都打印"正在直播中…"，但从未出现"准备开始录制视频"，不产生任何录制文件；同一配置下虎牙、B站可正常录制。日志无任何报错、警告或提示，状态面板一直显示"正在直播中"。

**影响范围**：所有 `get_record_headers()` 返回 `None` 的平台（实测：抖音、斗鱼）。这类平台的共同特征是没有专属录制请求头规则（Referer/Origin）且未配置对应 Cookie。

**根因（历史性结构 Bug）**：`main.py` 的 `run()` 中 `headers = get_record_headers(platform, ...)` 后的 `if headers:` 错误地包住了其后的**整个录制链**——tls_verify/proxy 插入、录制状态注册、TS/FLV/MP4/MKV 全部录制分支、`check_subprocess` 启动 ffmpeg、`record_success` 周期计数（约 490 行）。凡 `get_record_headers` 返回 `None` 的平台（`_RECORD_HEADER_RULES` 未配置 Referer/Origin 且无 Cookie），整个录制块被**静默跳过**：不打印、不报错、不录制、每周期空转。有专属录制头的平台（虎牙/B站）恰好不受影响，使问题看起来像"个别平台解析问题"而非全局结构问题。

**修复**：

1. **缩进层级修正（main.py）**：`if headers:` 块内只保留 `-headers` 插入（4 行）；tls_verify 插入、代理插入、录制状态注册、全部录制分支、周期计数**整体左移 4 空格**，脱离条件嵌套，无条件执行。
2. **校验器 UA 对齐（src/stream_select.py）**：新增 `MOBILE_UA` 常量（与 `main.py` ffmpeg 命令默认 UA 一字不差），`_validate_stream_url` 对无桌面 UA 的平台发移动 UA——斗鱼 hwa CDN 对非浏览器 UA 的 GET 偶发 403，校验与录制两端 UA 必须完全一致（方法 GET + 头 Referer/Cookie + UA 三位一体）。

**排查提示**：长录制链的入口条件必须与"是否录制"语义精确对应；"条件为假整块跳过"是最危险的失败模式（不抛异常、不打日志）。当所有代码路径分析都表明"应该有日志"而实际没有时，可在 `select_source_url` 返回后临时插桩打印真实 `real_url`、并对照缩进层级绘图核验块边界，是最短定位路径。

## 贡献指南

### 代码规范

- 格式化: `black .`
- 导入排序: `isort .`
- 类型检查: `mypy`（已启用 `disallow_untyped_defs = true`，`--strict` 模式全通过）
- 类型检查（增强，本地）: `basedpyright` 已在 `pyproject.toml` 配置 `[tool.basedpyright]`（standard 模式、排除 `typings/`/`node/`/`ffmpeg/` 等、`venvPath` 指向 workbuddy managed venv）；CI 仍以 `mypy` 为准（basedpyright 非 CI 检查项，换机需重新指定 venvPath）
- 注释规范: 模块/函数说明统一使用 `#` 行注释，**不使用三引号 `"""` 文档字符串**；多行说明每行以 `#` 开头（功能性多行字符串字面量除外，如模板/SQL，应改用单引号 + 换行拼接而非 `"""`）

### 测试与覆盖率

- 运行测试: `pytest`（`asyncio_mode = "auto"`，异步用例无需显式标记）；当前 496 passed / 2 skipped，总覆盖率 50.34%
- 覆盖率配置集中在 `pyproject.toml`：`source = ["src"]`，全局门禁 `fail_under = 50`
- 高频变更核心模块设独立覆盖率门禁（记录于 `pyproject.toml` 注释，CI 中通过 `--cov-fail-under` 或脚本检查）：

| 模块 | 门禁 | 当前覆盖 |
| --- | --- | --- |
| `spider.py` | ≥50% | 50% |
| `stream.py` | ≥70% | 70% |
| `utils.py` | ≥80% | 82% |
| `ttwid.py` | ≥85% | 85% |
| `ab_sign.py` | ≥95% | 99% |
| `proxy.py` | ≥50% | 51% |

- 并发专项测试（`test_concurrency.py` / `test_concurrency_rate_limit.py`）使用专用配置 `.coveragerc-concurrency`（不设全局阈值），验证 `threading.Lock` 去重与抖音速率限制在多线程环境下的正确性

#### Web/接口冒烟测试工具（`scripts/smoke_test.py`）

通用、零依赖（纯标准库）的 Web/接口冒烟测试工具，用于快速验证 Web 管理面板等**运行中 HTTP 接口**的可达性与核心响应。

- 配置驱动：JSON 描述检查项（`url` / `method` / `expected_status` / `timeout` / `headers` / `body` / `expect_contains` / `expect_json`）
- `base_url` 前缀拼接，无需每个接口写完整地址
- 三种输出：控制台（带颜色）、JSON 报告、HTML 报告
- 任一检查失败退出码非 0，便于接入 CI
- **已接入 CI**：默认用例 `scripts/smoke_web.json` 探活 Web 面板 `/` 与 `/health`（后者为 `src/web_api.py` 提供的公开探活端点）；`.github/workflows/ci.yml` 的 `test` job 在 pytest 之后受控启动 `python web.py`，经 `scripts/_ci_web_smoke.sh` 做就绪等待 + 断言（走 `.github/actions/retry`），失败保留 `logs/web-smoke-*` 工件并使 job 变红——补齐 TestClient 覆盖不到的「面板进程能否真正监听并应答」链路

用法：

```bash
# 检查本机 Web 管理面板（默认 127.0.0.1:8000，示例见 scripts/smoke_web.json）
python scripts/smoke_test.py -c scripts/smoke_web.json

# 生成 HTML 报告
python scripts/smoke_test.py -c scripts/smoke_web.json -r smoke_report.html -f html
```

> 与 `build_exe.py --smoke`（打包产物冒烟，见上文第 5 节）不同，本工具针对**运行中的 HTTP 接口**做轻量探活，两者互补。

### 添加新平台支持

1. 在 `src/spider.py` 中添加平台数据获取函数
2. 在 `src/stream.py` 中添加流地址解析函数，返回值包含 `actual_quality` 和 `available_qualities` 字段
3. 在 `main.py` 中添加平台识别逻辑
4. 更新 `README.md` 和本文档

## 更新日志

> **真机验证留存约定**（与 `AGENTS.md`「完成定义」第 2 步同源）：涉及录制链路 / 选源 / ffmpeg 参数 /
> 平台解析的改动，真机验证结论写在本文件对应版本条目的「验证」子节，中英同步。
> **滚动归档**：本节只保留当前发布周期的条目，更早条目整卷存于 [`docs/changelog/code-wiki-history-zh.md`](docs/changelog/code-wiki-history-zh.md)（口径见上方「变更日志归档索引」）。
> 格式：`[YYYY-MM-DD] 平台 | 脱敏 URL | 脚本 | 结果 | 消息数`。
> 无法执行时结果列写 `SKIP(原因)`（如 `SKIP(无外网)` / `SKIP(房间未开播)`），
> 并补「交回用户」动作（如「请用户有活房间时手动跑」）；此情形不得宣布完成定义第 1→6 步完成。
> 脚本直跑时额外输出 `VERIFICATION_RESULT: {"platform":..., "status":..., ...}` 结构化一行供机器解析。
> 脚本：`tests/test_{bili,douyin,douyu,huya,twitch}_live_collector.py`（`python file.py <URL> [秒数]`，
> 需活房间 + 外网，默认人工通道）。

### v4.3.0-dev (2026-09-27) — 本日改动按模块分类总览：发布链四处修复 + finding 4/5/6 + 四文档体积整理 + AGENTS 精简 + 元数据一致性同步

> 本节是 2026-09-27 全天改动的**模块级总览**（摘要表 + 判据读数）。路径级明细已按当日整理口径外迁，
> 与其余 73 个历史清单同处一地；同日四条明细条目（发布链三处故障、finding 4/5/6 + 文档整理、`AGENTS.md` 精简）在本节下方，可交叉印证。

| 模块 | 变更性质 | 主要文件 | 关键读数 / 判据 |
| --- | --- | --- | --- |
| 打包与发布链 | 修改 `make_zip` 命名与守卫、更正 Linux ffmpeg 来源与八槽钉定；**新增** `_clean_stale_release_zips` / `_drop_stale_release_zips` / `_assert_dual_zips_are_two_files` 与 `--dual`↔`--no-zip` 互斥 | `build_exe.py` | 未删任何函数或下载源；产物名 `DouyinLiveRecorder-v4.3.0-windows-amd64-{lite,full}.zip` |
| CI 与发布工作流 | **新增** `release-guard` job 与 `Verify dist contains both lite & full zips` 步骤 | `.github/workflows/build-release.yml` | `gh release delete` 默认不删 tag；`fail_on_unmatched_files: true` 不放宽；08:14 的他人改动本会话未触碰（已备案） |
| 测试 | **新增** 9 条用例（10 个断言单元），改造 `_stub_build_steps`，更正两处注释 | `tests/test_build_exe.py` | 单文件 100 → **105 passed**；4 次变异各自只红自己那条；`DIST_DIR` 已改指 `tmp_path` 以免真删用户产物 |
| 根约定 | `make_zip` 条目补 ④⑤ 判据与 9 个锁名；protobuf 区间更正为 `>=6.33.5,<8`；体积精简 | `AGENTS.md` | 97,034 → **95,715 B**（−1.4%）；token 保全审计：`test_` 名 / CVE 编号 / `UPPER_SNAKE` 名丢失均为 0 |
| 中英 wiki | **新增** 4 条明细条目 + 本总览；73 个历史清单块外迁；109（zh）/181（en）处表格截断补回；索引与统计小节重写；「打包与发布」第 4 步更正 | `CODE_WIKI.md`、`CODE_WIKI_EN.md` | `^### v` 169 → **173 = 173**；未闭合代码 span 段落 26/18 → **0**；两侧均纯 CRLF |
| 面向用户文档 | **同日后续步骤：版本条目同步**（把 09-26 ~ 09-27 的变更并入 `v4.3.0` 条目、日期区间延至 09-27、测试读数与「本机恒红用例」的旧记述一并更正） | `README.md`（104,040 → 109,648 B）、`README_EN.md`（123,017 → 129,644 B） | 五小节条目数中英逐节相等（🐛 9 / ✨ 12 / ⚠️ 9 / 🛠️ 7 / 🧪 4）且顺序一致；`^### v` 20 = 20；两文件仍纯 CRLF。此前一致性审计中它们确属「无需更新」，本次是**新增内容**而非压缩，README 更新日志依旧不做精简 |
| 参考子文档与本机记录 | **新增** 两份文件清单附录；追加会话经验与日志 | `docs/agent-reference/changelog-file-inventories.md`（130,064 → 139,024 B）、`-en.md`（98,458 → 107,897 B）、`session-learnings.md`、`.workbuddy/memory/2026-09-27.md` | 41（zh）/ 32（en）条历史清单 + 本块；指针定位逐条命中，孤立表头 0 |
| 构建产物元数据 | **重建** egg-info，修掉两处真实漂移 | `DouyinLiveRecorder.egg-info/`（gitignored + dockerignored） | `PKG-INFO` 的 `Requires-Dist: h2` `>=4.3.0` → `>=4.4.1`；内嵌 README 补 v4.3.0 段；其余四个文件逐字节不变 |
| 依赖 / 版本 / 忽略清单 / 配置 / i18n | **仅 1 处注释修复，其余经核对确认无需更新** | `requirements.txt`（行内注释补全）、`pyproject.toml`、`Dockerfile`、`docker-compose.yaml`、`.gitignore`、`.dockerignore`、`.coveragerc-concurrency`、`config/config.ini`、四语目录 | `websockets>=14.0` 的行内注释原先断在「…14.0+ API，」（行尾注释无法续行，属真截断），按 `pyproject.toml` 同条注释补全为「12/13.x 时 `connect()` 直接 TypeError 且被重连循环吞掉，弹幕永远连不上」；**规格本身零改动**，23↔23 包名集合仍相等、`tests/test_regression_2026_09_22_gates.py` 25 passed、文件行尾仍纯 LF。其余：`python 3.14` / `node 24` 跨 workflow 同值；工具与实装版本一致；排除清单四套无缺项；`config.ini` 6 节 143 键且本轮零新增配置面；四目录 780 键集相等、`.mo` 与 `.po` 同步 781 条、提取器缺失 0 条 |

- **一致性核验读数（本轮实测，均可复算）**：`grep -c '^### v' CODE_WIKI.md CODE_WIKI_EN.md` → 173 = 173；
  `importlib.metadata.version('DouyinLiveRecorder')` → 4.3.0；`scripts/check_version.py` PASS；
  `scripts/compile_po.py --check` 同步 781 条；`scripts/extract_i18n_strings.py` 缺失 0 条；
  `pytest tests/test_i18n.py -k "keyset or sync or catalogs"` → 6 passed；
  `pytest tests/test_proto_runtime_compat.py tests/test_i18n.py` → 43 passed。
- **本轮未做（诚实边界）**：`requirements.txt` 与 `pyproject.toml` 未新增任何依赖（无需求）；`config/config.ini` 未写入
  （含凭据、被忽略，且无新增键需求）；`README*.md` 未改动（用户 09-27 口径）；`docs/agent-reference/session-learnings.md`
  仍是 `docs/agent-reference/` 内唯一 LF-only 文件（finding 7 遗留，不在本轮范围）。
> 路径级明细已逐字外迁至 [docs/agent-reference/changelog-file-inventories.md](docs/agent-reference/changelog-file-inventories.md)（条目：v4.3.0-dev (2026-09-27) — 本日改动按模块分类总览：发布链四处修复 + finding 4/5/6 + 四文档体积整理 + AGENTS 精简 + 元数据一致性同步｜小节：本日改动按模块分类总览（新增 / 修改 / 删除 + 文件路径））。

### v4.3.0-dev (2026-09-27) — `AGENTS.md` 体积精简：三处真重复消除 + 读数指针化；实测结论是「根文件已达约束密度下限」

- **动因**：用户要求精简 `AGENTS.md` 体积，保留全部核心指令/关键约束。先按冗余类别量化，再决定手法。
- **实测的冗余分布**：可外迁的**一次性实测读数**其实早已外迁干净——`BtbN 126,600,656 B / 108,761,296 B`、
  `johnvansickle 41,888,096 B`、`autobuild-2024-10-31`、`latest` 于 2026-09-26T13:22:38Z 重发、日更标签仅剩
  `09-13~09-26` 共 15 条、`api.github.com` 的 `assets[].digest` 六项读数**逐条早已存在于
  `docs/agent-reference/measured-evidence.md`「运行时上游完整性产物实测」**，而 `AGENTS.md` 又抄了一遍 →
  本轮把 SEV-10 条目与「来源增删改三处」条目里的这些数值改为指向该小节（并写明「本文件不再复制数值」）。
- **消除的三处真重复**（本文件自身的「不得出现第二份事实源」口径）：① 「关键约定」第 14 条与「已知坑 → i18n」
  的提取器盲区条目内容重叠 → 合并进第 14 条（吸收四目录文件名与「报 0 缺失假绿」两点），删除后者；
  ② 「项目概览」的版本行把「关键约定」第 1 条（`importlib.metadata` / `APP_VERSION` / `zh_CN.po`）整段复述
  → 压成一行指针；③ 「风险控制」两条路由句把细则条目里的命令与目录清单重抄一遍 → 只留判据 + 指向细则
  （命令 `pip install --ignore-installed --no-deps -r requirements.txt` 与 `downloads/`/`logs/`/`backup_config/`
  禁令在「CI / workflow 约定」「测试收尾清理临时脚本」两处细则里逐字仍在）。
  另把「格式化命令」里 `PYTHONUTF8` 父进程转发与 `reconfigure(errors="replace")` 两条同因条目合并为一条。
- **读数**：`AGENTS.md` 97,034 → **95,715 B**（−1,319，−1.4%），496 行、纯 CRLF（LF-only 0）。
- **为什么只有 1.4%（结论级，写给后来的会话）**：全文顶层条目 **224 条、平均 383 B**（口径：
  `python -c "import pathlib,re; t=pathlib.Path('AGENTS.md').read_text(encoding='utf-8'); top=[x for x in t.splitlines() if re.match(r'^([-*] |[0-9]+[.] )', x)]; print(len(top), sum(len(x.encode()) for x in top)//len(top))"`），
  逐条核对后几乎每条都是「判据 + 常量名 + 用例名 + 错误码」的不可压缩载荷。
  保全审计的实测口径：原文 997 个 code span 中仅 15 个不再以原形态出现在 `AGENTS.md`，逐条核对分别是
  ①9 个 `::test_…` 片段（改成「文件名写一次 + 用例名并列」的写法，**55 个用例名全部仍在**）与
  ②6 个已在 wiki/measured-evidence 留存的读数；`test_` 标识符、CVE/PYSEC/GHSA 与 MIN/SEV/MID 编号、
  `UPPER_SNAKE` 常量与环境变量名三类 token 的**丢失数均为 0**（仅 3 个体积字节读数按设计只留在 measured-evidence）。
  故在现有架构下体积已接近下限；要进一步下降只能改架构（把「已知坑」细则按主题外迁、根文件只留索引与硬规则），
  而这与本文件开头「『已知坑』的约束句一律留在本文件内」的自我约定冲突，**须用户先批准**，本轮未做。
- **验证**：`scripts/run_gates.py --list` 仍解析出 8 条门禁（解析器读「格式化命令」章节的 bash 围栏，本轮未动该围栏）；
  `pytest tests/test_run_gates.py tests/test_regression_2026_09_22_gates.py` → **67 passed / 1 skipped**
  （含「首条命令必须是逐字 black 门禁行」「`PYTHONUTF8=1` 前缀必须被解析为 env」「章节改名即返空」三条来源锁）；
  行尾形态不变。纯文档改动，完成定义第 2 步真机验证不适用。

### v4.3.0-dev (2026-09-27) — 发布链第四处加固：`--dual` 出包后校验两个返回路径 + 出包前清 `dist/` 陈旧 zip，并完成四文档体积整理（外迁 73 个历史文件清单块 + 补回被 `…` 截断的表格单元格）

- **动因**：上一条目收尾时并行审查代理列出 finding 1~8，用户批准已修的 1/2/3，要求补做 4/5/6，并顺带整理四份文档体积。
  4 = `make_zip` 的返回值在 `--dual` 分支被 `_ =` 丢弃，本地没有任何「两个变体真的互不相同且都落件」的事后校验，
  且 `dist/` 不清理时上一轮残留会被 `path: dist/*.zip` 扫进附件；5 = 产物名示例仍写着 `windows-x64`
  （Windows 实测架构段是 `amd64`，`x64` 只是 `_NODE_ARCH_MAP` 归一后的运行时键名）；6 = 「两条既有用例**只**断言
  `zip_path.is_file()`」不精确（其中 `test_make_zip_aborts_when_archive_still_contains_logs` 断言的是 `SystemExit` 文本）。
- **处置（`build_exe.py`，三项）**：① `_assert_dual_zips_are_two_files(lite_zip, full_zip)`——名字相同即 `SystemExit`
  （`zipfile "w"` 原地截断不报错，单次调用的守卫看不见「两次撞一个文件」），其中一个不存在同样 `SystemExit`；
  ② `_clean_stale_release_zips()` + `_drop_stale_release_zips()`——**只在真要出包时**按 `{APP_NAME}-v*.zip` 命中并删除，
  返回并打印被删清单（静默删除与不删同样糟），`--no-zip` 路径一律不清；清理点必须在**第一个** zip 之前，
  放进 `make_zip` 内会让第二次删掉第一次的产物；③ 非 `--dual` 路径接住 `make_zip` 返回值，末行打印实际产物名。
- **同族更正**：`tests/test_build_exe.py` 的截断事故注释改写成真实产物名 + 精确用例判据；「打包与发布」第 4 步
  原写「冒烟测试跑在 lite 版本上」已被 MID-2254 的顺序改动证伪，改为「冒烟排在**两个** zip 之后、跑装满运行时的发布目录」，
  并补写清理与事后校验；该步顺带修掉一处陈旧异常类名（`ChallengePageError` 已于 2026-09-23 按 MIN-2267 删除，
  实际只剩 `IntegrityError` / `NetworkError`）——同一行还留着会把代码 span 截断的 `…`。
- **回归锁（`tests/test_build_exe.py` 新增 5 条用例，全部做过变异验证）**：
  `test_dual_build_aborts_when_both_variants_land_on_one_zip`、
  `test_dual_build_aborts_when_a_variant_zip_is_missing`、
  `test_dual_build_prunes_stale_zips_before_first_zip`、
  `test_no_zip_build_keeps_existing_dist_zips`（反向锁：不出包就不许删）、
  `test_clean_stale_release_zips_only_touches_own_artifacts`（含「`dist/` 不存在时空操作」与幂等）。
  `_stub_build_steps` 的 `make_zip` 桩改为**按 suffix 产出不同名字并真实落件**——旧桩返回常量 `stub.zip`，
  接上新校验后三条 `--dual` 用例会全部误红；`DIST_DIR` 一并改指 `tmp_path`，否则测试会真删仓库 `dist/` 下的用户产物。
  变异读数：清理函数改空操作 → 2 红；`--dual` 分支去掉清理接线 → 1 红；事后校验整体失效 → 1 红；
  仅存在性校验失效 → 1 红；四次变异都只红自己那条，改完 `build_exe.py` 与备份逐字节相同。
- **文档体积整理（口径：只搬不删）**：先实测冗余，结论是四份文档**没有**可删的空白行/重复段落
  （行尾空白 0 行、连续空行 >1 的段 0 处、与 `CODE_WIKI` 逐字重复的行 README 侧仅 1 行），体积全在正文里。
  真正可动的是更新日志里 73 个「涉及文件（按模块分类）」历史清单块（zh 41 块 / en 32 块），逐字搬到
  `docs/agent-reference/changelog-file-inventories.md` / `-en.md`，原处保留小节标题 + 一行「条目名｜小节名」指针。
  同时发现并修复上一轮（2026-09-25）压缩脚本的静默信息损失：表格单元格里 109（zh）/181（en）处被
  `…` 截断的原文按前缀唯一匹配从 `.workbuddy/docold` 补回（zh +18,439 B / en +33,117 B，2 处匹配不唯一刻意跳过）。
  读数（**本条目写入前**，`README*` 与原件逐字节相同）：`CODE_WIKI.md` 638,616 → 552,368 B（−86,248，−13.5%）、
  `CODE_WIKI_EN.md` 692,281 → 649,906 B（−42,375，−6.1%）、`README.md` 104,040 B 与 `README_EN.md` 123,017 B 未改；
  新增两份附录 130,064 B / 98,458 B。用户口径确认：README 的更新日志面向使用者，不做压缩。
- **完整性自证**（可复算）：`grep -c '^### v'` 两侧仍 **170 = 170**；逐行对账「原文件里每一条非空行要么仍在原文档、
  要么在附录里」，仅上述 109/181 条被补回的表格行以旧形态消失；指针定位 41/32 条全部命中附录中真实存在的
  「条目 + 小节」对；孤立表头 0 处；未闭合代码 span 段落数由 26（zh）/18（en）降到 0；
  外迁块边界一律落在标题或「验证/影响范围/结论」类标签之前，故没有把表头与表体切开；
  四份文档 + 两份附录全部纯 CRLF（LF-only 计数 0）。
- **顺带修正的文档漂移**：`CODE_WIKI(_EN)`「文档统计与索引」原写「285 个 Markdown 文件」且未附取数命令、无法复算，
  现改为「取数命令 + 读数时刻」口径（2026-09-27 实测 100），并把审查报告的行改成真实位置 `docs/worklog/`（9 份）、
  新增 `docs/agent-reference/` 行与「参考子文档索引」小节；`CODE_WIKI_EN.md` 打包命令代码块内 9 行中文注释补英文。
  已知未做：EN 文档代码块内仍有 162 行中文（架构图与目录树标签），属翻译工作量而非体积冗余，留给后续单独一轮。
- **验证**：`scripts/run_gates.py` 8/8 rc=0（含 `check_annotations.py` PASS、平均注释密度 23.8%、
  `compile_po.py --check` 781 条同步、`check_version.py`、`check_runtime_pins.py` 全槽位钉定）；
  其内置全量 pytest 兜底 **3240 passed / warnings summary 空**（较上轮 3235 = 本次新增 5 条用例）；
  `pytest --cov=src` → 3240 passed / 14 skipped、总覆盖率 **83.91%**，`scripts/check_coverage.py`
  **PASSED：42 个模块全部达标**（`src/proto/douyin_pb2.py` 显式豁免）；`basedpyright`（不带路径）0 errors /
  0 warnings / 0 notes；`mypy`（无参）Success；black / isort 对 `build_exe.py`、`tests/test_build_exe.py` unchanged；
  `python -m pytest tests/test_build_exe.py` 单文件独立跑 **105 passed**（100 → 105）。
- **未实测与交回动作**：① 本机**未**跑 `python build_exe.py --smoke --dual`（需 PyInstaller 全量构建 + 约 300MB 上游下载），
  「清理 + 两个 zip 同时落 `dist/`」的真实链路仍由 CI 的 `Verify dist contains both lite & full zips` 首跑确认；
  ② 文档整理为纯文档改动，不涉及录制链路/选源/ffmpeg 参数/平台解析，故完成定义第 2 步真机验证不适用；
  ③ 被补回的表格单元格以 `.workbuddy/docold`（2026-09-25 整理前快照）为准，若某条原文在该快照之前就被改写过，
  补回的是快照形态；④ 若不希望历史清单外迁（要求全部留在原文档内），删除本条目两处改动即可回滚：
  两份附录文件 + 73 行指针。

### v4.3.0-dev (2026-09-27) — 发布链第三处故障：`make_zip` 用 `Path.with_suffix(".zip")` 截断产物名，lite 被 full 原地覆盖

- **现象**：`Build & Release` 这次**通过了**钉定校验与 `Build executables + smoke test`，红在下一步
  `Verify dist contains both lite & full zips`：`Found 0 lite zip(s) and 0 full zip(s)`，
  `Error: Expected both *-lite.zip and *-full.zip in dist/, but missing one or both.`，而
  `Full listing:` 明确列出一个 160,298,993 B 的文件 `dist/DouyinLiveRecorder-v4.3.zip`。
  即产物**存在**，但两个变体的名字里 `-lite` / `-full` 与 `-<os>-<arch>` 段全部消失——与前两次同族
  红（`Pattern 'dist/*-lite.zip' does not match any files`）症状同源、病因完全不同，断点又前移了一步。
- **根因**：`build_exe.make_zip()` 先拼 `zip_base = DIST_DIR / f"{APP_NAME}-v{version}-{os}-{arch}{suffix}"`
  再 `zip_path = zip_base.with_suffix(".zip")`。`Path.with_suffix` 按**最后一个点**切分扩展名，而版本号
  本身带点：本机实测三平台真实产物名截断结果一致——
  `Path('DouyinLiveRecorder-v4.3.0-windows-amd64-lite').suffix == '.0-windows-amd64-lite'` →
  `with_suffix('.zip')` 得 `DouyinLiveRecorder-v4.3.zip`（`-full` 同解；`linux-x86_64` 亦同解）。
  于是 `--dual` 的两次 `make_zip` 写到同一个路径，第二次（full）以 `zipfile` 的 `"w"` 模式截断重写第一次
  （lite），磁盘上只剩 full 的内容、却顶着一个不含任何变体/平台标识的名字。
- **为什么长期没被抓到**：`make_zip` 的两条既有用例对**名字**都不设判据（一条只断言 `zip_path.is_file()`，
  一条只断言 `SystemExit` 的文本）——名称漂移对「文件在不在」完全隐形；仓库里唯一看名字的判据是 CI 的
  `dist/*-lite.zip` 通配，所以只有真跑 `--dual` 才红。同理，非 `--dual` 路径（`ci.yml` 的 build-verify 用
  `--no-zip`）从未暴露名称丢平台段的问题。
- **处置（三项，均在 `build_exe.py`）**：① `.zip` 与其余段拼进同一个 f-string，命名保持单点定义，
  并在 `make_zip` 内写明禁用 `with_suffix` 的判据注释；② 新增结构性不变量——拼出的 `zip_path.parent`
  必须仍是 `DIST_DIR`，否则 `SystemExit`（`version`/`suffix` 含路径分隔符时 f-string 产出的是**子路径**，
  成品会静默落到 `dist/` 之外，Windows 下 pathlib 连 `\` 也当分隔符）；③ `--dual` 与 `--no-zip` 判为互斥
  并 fail-fast——`--dual` 分支从不读 `no_zip`，旧形态下 `--dual --no-zip` 会**静默无视**用户显式写的
  `--no-zip`、照样压出两个大 zip（矛盾组合要么报错要么有一个参数不起作用，不得各走一半）。
- **回归锁（`tests/test_build_exe.py`，四条 / 五个用例，全部做过变异验证）**：
  `test_make_zip_name_keeps_dotted_version_and_variant_suffix`（正则结构锁：完整 `v4.3.0` +
  `<os>-<arch>` + `-lite`/`-full` + `.zip`；Windows 实跑名形如
  `DouyinLiveRecorder-v4.3.0-windows-amd64-lite.zip`）、
  `test_dual_suffixes_do_not_collide_on_one_zip`（两次 `make_zip` 必须产出两个不同文件）、
  `test_make_zip_refuses_name_containing_path_separator`（`version` 与 `suffix` **两个入参位各测一次**，
  用 `'/'` 而非 `os.sep`，两侧平台都真实走到拒收分支）、
  `test_dual_and_no_zip_are_mutually_exclusive`（断言 `order == []`，锁「判定早于任何构建步骤」）。
  变异读数：把实现改回 `with_suffix(".zip")` → 前两条用例红，而既有两条 `make_zip` 用例仍绿（证伪旧口径）；
  把 ②③ 两个守卫改成 `if False:` → 后两条用例红（②那一删是 `FileNotFoundError`，证明断言真被执行到）。
- **验证**：`pytest tests/test_build_exe.py` **100 passed**；`run_gates.py` 8/8 rc=0（其内置全量 pytest
  兜底 **3235 passed**、warnings summary 空）；`pytest --cov=src` → `check_coverage.py` **PASSED：42 个模块全部达标**；
  `basedpyright build_exe.py tests/test_build_exe.py`
  0 errors / 0 warnings / 0 notes；`mypy`（无参）158 files Success；`black --check` / `isort --check-only`
  对两文件 unchanged；`check_annotations.py` 通过；改动文件行尾形态不变（`build_exe.py` 与 `AGENTS.md`
  纯 CRLF、`tests/test_build_exe.py` 纯 LF）。
- **未实测与交回动作**：① 本机**未**跑 `python build_exe.py --smoke --dual`（需 PyInstaller 全量构建 +
  约 300MB 上游下载），「lite + full 两个 zip 同时落在 dist/」只能由 CI 的
  `Verify dist contains both lite & full zips` 步骤首跑确认；② 已失败的这次 Release 记录由
  `release-guard` 回收（`needs.build.result != 'success'`），tag 保留，修好后重跑工作流即可；
  ③ 历史发布物里凡是 `DouyinLiveRecorder-v<主版本>.<次版本>.zip` 形态的名字都属于本缺陷产物（lite 那份
  从未真正分发出去），重跑发版才会生成带平台与变体的正确附件。

### v4.3.0-dev (2026-09-27) — 发布链修复：Linux ffmpeg 钉定改钉「月末不可变 release 标签」，并新增 `release-guard` 回收 build 失败遗留的空 Release

- **背景**：tag 推送触发的 `Build & Release` 在 Linux build job 的 ffmpeg 下载步终止，日志末行
  `[build][FATAL] _ffmpeg_temp.tar.xz SHA256 不匹配（期望 87de0900…，实际 0cfb2146…），已终止构建`；紧随
  其后的 `softprops/action-gh-release` 步骤报 `⚠️ Pattern 'dist/*-lite.zip' does not match any files`
  （`fail_on_unmatched_files: true`）。后者是「dist/ 无产物」的**连带症状**，不是独立故障——关掉
  `fail_on_unmatched_files` 只会把这唯一可见的信号抹掉。
- **根因**：`_FFMPEG_DOWNLOAD_URLS` 的 linux 两槽指向 BtbN 的 `releases/download/latest/...`。`latest` 是
  **滚动别名**：同名资产被上游反复重传，digest 随之变化——实测 tag `latest` 的 `published_at` =
  2026-09-26T13:22:38Z，即当日更早取到的钉定值 `87de0900…` 在同日即失配；linuxarm64 的 `30774c8f…` 同样
  已失效（当前 `f2fe35e9…`）。
- **处置（用户选定「换月度不可变标签」）**：两槽 URL 改钉**月末** autobuild 标签
  `autobuild-2026-08-31-13-27`（资产 `ffmpeg-n9.0.1-11-ge47273f4d9-linux{64,arm64}-gpl-9.0.tar.xz`），
  钉定值取自 `api.github.com/repos/BtbN/FFmpeg-Builds/releases/tags/<标签>` 的 `assets[].digest`
  （linux64 `182c1b50…`、linuxarm64 `e2dd447c…`）。为什么必须钉月末标签：该库全量仅 **38 条** release，
  日更 `autobuild-*` 只保留最近约两周（实测仅剩 09-13~09-26 共 15 条）→ 钉日更标签等于预埋一次 404；
  月末标签实测可回溯到 `autobuild-2024-10-31`，是 URL 与 digest 双双不可变的唯一组合。代价：内置 ffmpeg
  落后于 `latest` 的 n9.0.2（现 n9.0.1-11-ge47273f4d9），升级要人工换标签 + 换钉定值——与 SEV-10 的
  人工闸口同口径，刻意不改自动取哈希。
- **护栏（第二项）**：`build-release.yml` 新增 `release-guard` job（`needs: [prepare, build]`、
  `if: always() && 发版路径 && needs.build.result != 'success'`），build 未全绿时用 `gh release delete`
  回收 `release-create` 预建的空/残缺 Release（默认**不删 tag**）并留 `::warning::`。动因：
  `release-create` 为消除三平台并发创建竞态，刻意在 build **之前**建记录；build 失败时收尾的 `release`
  job 因 `needs: build` 被跳过，那条记录就以空 Release 形态留在仓库里，用户点进去一个附件都没有。
- **改动面**：`build_exe.py`（URL 两条 + 钉定表两格 + 三处注释/取数口径更正：维护说明、Linux 来源段、
  归档布局示例）；`tests/test_build_exe.py`（新增 `test_linux_ffmpeg_urls_pin_an_immutable_release_tag`：
  禁 `/releases/download/latest/`、禁 `n9.0-latest-` 资产名、两架构必须同一标签）；
  `.github/workflows/build-release.yml`（新增 `release-guard`，矩阵/缓存/构建/上传逻辑零改动）；
  `AGENTS.md`（SEV-10 条目补「取数端点必须是月末标签」+ 回归锁名、「CI / workflow 约定」新增空 Release
  护栏条目、体积读数按新资产更新）；`docs/agent-reference/measured-evidence.md`（2026-09-27 复测表）。
- **实测（2026-09-27）**：`releases/latest` → linux64 150,999,836 B / `0cfb2146…`、linuxarm64 127,395,868 B /
  `f2fe35e9…`（与旧钉定值均不相等）；`releases?per_page=100` → 全库 38 条；月末标签资产 → linux64
  126,600,656 B / `182c1b50…`、linuxarm64 108,761,296 B / `e2dd447c…`（另有 `checksums.sha256` 资产可供
  二次核对）；gyan.dev Windows `.sha256` 仍 `60f46726…`（未漂移）；nodejs.org 首个 `lts` 仍 `v24.21.0`
  （未漂移）。月末资产经前缀取回确认是合法 xz（魔数 `fd377a585a00`），顶层目录
  `ffmpeg-n9.0.1-11-ge47273f4d9-linux64-gpl-9.0/`。
- **验证**：`pytest tests/test_build_exe.py tests/test_check_runtime_pins.py` **115 passed**；全量 `pytest`
  3229 passed / 14 skipped 且 warnings summary 为空（唯一失败 `test_web_config.py::TestFormatUrlLine::
  test_normal_line` = 沙箱 DNS 解析 `live.douyin.com` 失败，单独重跑该用例 **1 passed**，与本次改动无关）；
  `mypy`（无参）158 files Success；`basedpyright tests/test_build_exe.py` 0 errors / 0 warnings / 0 notes；
  `black --check` / `isort --check-only` unchanged；`check_annotations.py` 通过；
  `check_runtime_pins.py --strict` 仍 rc=0；`yaml.safe_load` 解析 workflow 通过且 `jobs` 顺序为
  prepare / release-create / build / release-guard / release。改动文件行尾形态不变（build_exe.py、
  AGENTS.md、CODE_WIKI*.md、measured-evidence.md 纯 CRLF；tests/test_build_exe.py 与 workflow 纯 LF）。
- **未实测与交回动作**：① 本机 `github.com` 直链被重置（前缀取回 http=000、全量取回在 5.4MB 处中断），
  「按新 URL 全量下载并比对钉定值」只能由 GitHub runner 首跑验证；② 月末资产归档内的
  `bin/ffmpeg` / `bin/ffprobe` 未由本次前缀直接确认（5.4MB 前缀只覆盖 `doc/`），沿用 09-26 对同系列资产的
  实测——缺件时 `_extract_linux_ffmpeg_binaries()` 会 `SystemExit`，不会退化成「一行 warning + 静默空包」；
  ③ Linux full 包体积随换标签变化（126,600,656 B / 108,761,296 B），须由 CI 产物经
  `scripts/report_bundle_size.py` 复核后再决定是否需要按平台调阈值。

### v4.3.0-dev (2026-09-27) — 修复发布链第二处故障：`_PINNED_RUNTIME_SHA256` 八个槽位被误改成官方签名档标记，按官方通道重新回填哈希

- **现象**：粘贴日志只有末两行 `Run softprops/action-gh-release@v3` / `⚠️ Pattern 'dist/*-lite.zip'
  does not match any files`。该行的判读口径与上一条同源（`fail_on_unmatched_files: true` 是产物缺失的
  唯一可见信号，不得关闭）。但本机复算时发现**当前工作区还有第二处、且更早发作的故障**：
  `build_exe.py` 的 `_PINNED_RUNTIME_SHA256` 中 8 个槽位取值被整体写成 `OFFICIAL_SIGNATURE_PIN`
  （文件 mtime 07:58，晚于上一条 01:45 的收尾记录），使发布链断点由 build job 前移到 prepare job。
- **根因**：签名档只适用于「上游确实不公布哈希、且已在 `_RUNTIME_GPG_SIGNATURES` 登记签名 URL +
  完整 40 位主钥指纹」的槽位，本仓只有 macOS 的 ffmpeg/ffprobe 四槽符合。node 五槽（nodejs.org
  `SHASUMS256.txt`）、windows-x64/ffmpeg（gyan.dev `.sha256`）、linux 两槽 ffmpeg（BtbN 资产的
  `assets[].digest`）都有官方公布值，改成标记后 `_is_signature_satisfied` 因「该槽未登记」判 False
  → `_slot_is_gated` 三个析取项全 False。两条后果：`scripts/check_runtime_pins.py --strict` **rc=1**
  （prepare 的 fail-closed 步直接红），以及 `tests/test_build_exe.py::
  test_table_never_declares_signature_mode_without_satisfaction` **转红**（该锁正是为拦下这种改写而存在）。
- **处置**：8 个槽位一律按 AGENTS.md/`build_exe.py` 维护说明的**官方通道**重新取数后回填，
  **未**使用本地下载自算值：
  `curl -sS https://nodejs.org/dist/v24.21.0/SHASUMS256.txt`（win-x64 `.zip`、linux/macos `.tar.gz`
  五种资产，扩展名与 `_download_nodejs` 实际取用的包一致）；
  `curl -sSL https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip.sha256` → `60f46726…47ba`
  （未漂移）；`curl -sS https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/tags/autobuild-2026-08-31-13-27`
  → linux64 `182c1b50…` / linuxarm64 `e2dd447c…`（与 measured-evidence.md 记录逐字相等，月末标签 digest 不可变）；
  并确认 `dist/index.json` 首个 `lts` 仍 `v24.21.0`（Krypton）。macOS 两槽的 ffmpeg/ffprobe 保持签名档不动。
- **改动面**：仅 `build_exe.py`（钉定表 8 格取值 + 表头一行 `[2026-09-27 恢复]` 注 + 每条 node 行的来源资产名注释）；
  逻辑、URL 表、判定函数、测试与 workflow **零改动**。
- **验证**：改前 `check_runtime_pins.py --strict` **rc=1**、`test_table_never_declares_signature_mode_without_satisfaction`
  FAILED（offenders 逐槽点名 8 个）；改后 `--strict` 与结构模式均 **rc=0**，`pytest tests/test_build_exe.py`
  **95 passed**，`python scripts/run_gates.py` **8/8 全绿 rc=0**，全量 `pytest` **3230 passed / 14 skipped**
  且 warnings summary 为空，`basedpyright build_exe.py` 0 errors / 0 warnings / 0 notes，
  `black --check` / `isort --check-only` / `py_compile` 均通过。行尾形态不变（build_exe.py 纯 CRLF，
  1686 个 CRLF / 0 个孤立 LF）。
- **未实测与交回动作**：① 「按钉定值全量下载并比对」仍只能由 GitHub runner 首跑验证——本机 `github.com`
  直链被重置，只有 `api.github.com` 与 `nodejs.org`/`gyan.dev` 可用；② 本次会话期间 `build-release.yml`
  在 08:14 被**并行**改动（新增 `Verify dist contains both lite & full zips` 一步、构建命令加 `| tee build_exe.log`），
  该文件不由本条改动、也未由本条复核，`pipefail` 下 `tee` 不会吞掉 `SystemExit`，但发版前请由作者确认。

### v4.3.0-dev (2026-09-26) — 发布链完整性门禁新增「官方签名档」，Linux ffmpeg 换源 BtbN：让 `build-release.yml` 的 prepare 由 rc=1 转 rc=0，同时不放宽 SEV-10 的 fail-closed 语义

- **背景**：`build-release.yml` 的 prepare job 在 `Verify runtime binary SHA256 pins (fail-closed)` 一步报
  `Error: Process completed with exit code 1.`，日志正文即 `scripts/check_runtime_pins.py --strict` 的输出：
  矩阵内 2 个槽位（`linux-x64/ffmpeg`、`macos-arm64/ffmpeg`）仍是占位标记。定位结论——报错步骤在
  `.github/workflows/build-release.yml:141-149`，rc=1 由 `check_runtime_pins.py` 的 `--strict` 分支返回；
  这不是缺陷而是门禁按设计拦停（`build_exe.py` 钉定表注释与 `AGENTS.md` SEV-10 条目均写明「上游不公布哈希时
  宁可让发布链红」）。
- **为什么不删门禁**：钉定表不在工作流里（事实源是 `build_exe._PINNED_RUNTIME_SHA256`，workflow 只有
  `DLR_RUNTIME_SHA256` 透传）；且 `require_pinned_hashes()` 在 `GITHUB_ACTIONS=true` 下自动为真，删掉 prepare
  那步只会把同一处失败从 prepare 后移到三个 build job（各先跑完 pip 安装、仍在下载前 `SystemExit`），产物数不变 0。
- **处置（用户选定「按上游能力分档」）**：类别 ①「发布期运行时二进制」在**同一口径**
  `build_exe._slot_is_gated()` 下并上第二档**官方签名档**——取值 = `OFFICIAL_SIGNATURE_PIN` 标记，且该槽在
  `_RUNTIME_GPG_SIGNATURES` 确有登记、指纹为 40 位十六进制（标记本身绝不构成放行，与第 4 类 `SOURCE_BUILD_PROVENANCE`
  同一条「换个更容易填的标记拿免检」防线）。macOS 两槽（evermeet 只给 `/sig` 不给哈希）走该档；Linux 两槽换源到
  BtbN 的 n9.0 系列资产，取 `api.github.com` 的 `assets[].digest` 作官方公布哈希正常钉定，故不需要 MD5 降级档。
- **顺带修掉 SEV-2221**：`_download_file()` 下载前的闸口原只认 `_is_pinned()`，而验签调用点在下载后、
  「哈希已过」分支内——占位值的 macOS 槽永远走不到下载，那一档 P-2 验签在真实构建路径上**一次都没跑过**。
  现闸口认两档，签名档槽位下载后**必须**验签（BADSIG / 指纹不在环内 / 发布路径 gpg 缺失或取不到签名一律
  `SystemExit`），并把实测 SHA256 打进食包日志作滚动别名的审计线索。
- **改动面**：`build_exe.py`（新常量与谓词、`_download_file` 分派、`_unpinned_action` 报错点名「签名档未满足」
  的具体原因、`_FFMPEG_DOWNLOAD_URLS` Linux 两条、钉定表 4 格、Linux 解压抽成布局无关的
  `_extract_linux_ffmpeg_binaries()`）；`scripts/check_runtime_pins.py`（按档 `[NOTE]` 播报，判定仍委托
  `_slot_is_gated`）；`tests/test_build_exe.py`（+12 用例：签名档真值表、大小写无关、指纹形状关、表/登记同批不变量、
  SEV-2221 可达性锁、验签失败与 gpg 缺失必须终止、未登记标记不得发起下载、两种归档布局与缺件终止；`_ALLOWED_HOSTS`
  增 `github.com` 移除 `johnvansickle.com`；`_FakeResponse` 补 `headers` 与分块排空）；
  `tests/test_check_runtime_pins.py`（`_fake_module` 暴露新符号 + 2 条签名档分流用例）；
  `.github/workflows/build-release.yml` **仅注释**（4 处：`DLR_RUNTIME_SHA256` 说明、prepare 步说明、来源主机清单、
  gnupg 步骤「验签已是唯一判据」），矩阵/缓存/构建/上传/Release 逻辑零改动；`AGENTS.md`（SEV-10 条目、三类边界条目、
  新增「发布面来源增删同改三处」条目）；`docs/agent-reference/measured-evidence.md`（本次全部取数命令与读数）。
- **实测（2026-09-26）**：`evermeet.ca/ffmpeg/getrelease/zip/sig` → 200 / `application/pgp-signature` / 594 B 二进制
  OpenPGP 包，落点 `e.deolaha.ca:4242/pub/ffmpeg/ffmpeg-9.0.2.zip.sig`；`keys.openpgp.org` 查
  `0x476C4B611A660874` → 200，UID `static FFmpeg binaries (signing key)`，服务端回显指纹 ≡ 钉定值（**独立第二渠道**，
  R-2 的「指纹未经二渠道确认」就此解掉）；`johnvansickle ...amd64-static.tar.xz.md5` → 200 且取值与 09-22 逐字相同、
  `.sha256` → 404；BtbN `linux64-gpl-9.0` 150,998,508 B / `linuxarm64-gpl-9.0` 127,417,700 B，归档成员经前缀取回后
  `tar -tJf` 实测为 `bin/ffmpeg`、`bin/ffprobe`。
- **验证**：`scripts/run_gates.py` 8/8 全绿；`pytest` 全量 **3220 passed 且 warnings summary 为空**；
  `pytest tests/test_build_exe.py tests/test_check_runtime_pins.py` 105 passed；
  `check_runtime_pins.py --strict` 由 rc=1 → **rc=0**（两条 `[NOTE]` 明确说「走官方签名档」而非「已钉定」）；
  5 条变异全部被抓红（漏并签名档 / SEV-2221 回退 / 光标记即满足 / 写死 `bin/` 布局 / 缺件不终止）。
- **未实测与交回动作**：① 本机 `github.com/.../releases/download/...` 直链 `Connection was reset`，
  「按来源表全量下载并比对钉定值」只能由 GitHub runner 首跑验证；② evermeet 验签在真实构建路径的首次执行即
  macOS CI 跑（`--recv-keys` 能否成功已由 keyserver 探针旁证，但 `gpg` 全流程未在本机跑过）；③ Linux full 包体积
  因换源大幅上涨（见上表读数），`report_bundle_size.py` 本机无 Linux 未实测，须由 CI 产物复核后再决定是否需要
  按平台调体积门禁阈值。滚动别名只钉住「谁签的」钉不住「哪个版本」，evermeet 出新构建时 macOS 产物会随之变化而
  门禁不会拦——这是该档的固有边界，靠日志里的实测 SHA256 做事后审计。

### v4.3.0-dev (2026-09-26) — CI typecheck 门禁补装固定版本 pytest，并修掉 `tests/test_proto_runtime_compat.py` 的 `[return]` 误报：消除「本机绿、CI 红」的检查面漂移（纯 CI / 测试改动，零运行期变更）

- **背景**：CI 的 `typecheck` job 报 `tests/test_proto_runtime_compat.py:33: error: Missing return statement  [return]`（checked 159 files），而本机 `mypy` 158 files 全绿、完全无法复现。
- **根因**：该 job 只装 `requirements.txt + mypy`、**未装 pytest** → `import pytest` 被解析为 `Any`，`pytest.fail()` 的 `NoReturn` 标注丢失，mypy 认为 `_declared_protobuf_specifier() -> str` 可能隐式返回 `None`。这是环境差异而非代码缺陷；同一原因还意味着 `tests/` 里所有 `pytest.*`（fixture / `MonkeyPatch` / `raises`）此前**全部免检**——门禁本就是半盲的。本机复现手法：`mypy --no-site-packages`（遮蔽已装包即可精确复现同一条；该模式额外多出的 5 条 `no-any-return` 属过度剥离噪声）。
- **改动性质**：只改 CI 工作流 + 一条测试辅助函数 + `AGENTS.md`；`src/`、`main.py`、`gui.py`、`web.py`、`web/app.js`、`requirements.txt` / `pyproject.toml` 零改动，未增删任何依赖（pytest 只进 typecheck job 的临时安装，不进运行时清单）。

**涉及文件（按模块分类）**：

> 明细清单已逐字外迁至 [docs/agent-reference/changelog-file-inventories.md](docs/agent-reference/changelog-file-inventories.md)（条目：v4.3.0-dev (2026-09-26) — CI typecheck 门禁补装固定版本 pytest，并修掉 `tests/test_proto_runtime_compat.py` 的 `[return]` 误报：消除「本机绿、CI 红」的检查面漂移（纯 CI / 测试改动，零运行期变更）｜小节：涉及文件（按模块分类））。

**验证**：`mypy`（无参）与 `mypy --platform linux` 均 Success 158 files（本机 pytest 9.1.1，与 CI 新口径同版本）；`mypy --no-site-packages` 下原 `[return]` 已消失，仅剩 5 条剥离噪声；`basedpyright tests/test_proto_runtime_compat.py` 0 errors / 0 warnings / 0 notes；`black --check` unchanged；`pytest tests/test_proto_runtime_compat.py` 4 passed；`yaml.safe_load` 解析 `ci.yml` 通过且 outputs / steps 结构如预期；改动文件行尾形态不变（`ci.yml` 纯 LF，`AGENTS.md` 与该测试文件纯 CRLF）。

**遗留观察**：CI 那次运行报 `checked 159 source files`，本机按 `[tool.mypy].files` 口径数出 158 个 `.py`，差 1 个未定位（疑为该次运行所在提交上的多余文件），与本次修复无关。

### v4.3.0-dev (2026-09-26) — 仓库元数据与文档同源同步：依赖表 / 目录树 / egg-info / 忽略清单对齐，清理已删除模块 `weverse_auth` 的残留记载（纯元数据与文档改动，零运行期代码变更）

- **背景**：全仓通读核对「版本 / 依赖 / 目录树 / 忽略清单」四类同源信息，发现多处滞后：`CODE_WIKI*.md` 依赖表仍停在 16 条且 `starlette` 下限写着 `>=0.49.1`；目录树仍列 2026-09-23 已删除的 `src/weverse_auth.py` 与 `tests/test_weverse_auth.py`；`DouyinLiveRecorder.egg-info/requires.txt` 缺 2026-09-23 补入的 `h2`/`socksio`；`AGENTS.md` 依赖条数仍写 21 条。
- **改动性质**：只改文档 / 元数据 / 忽略清单并重建 `egg-info`；`src/`、`main.py`、`gui.py`、`web.py`、`web/app.js` 零改动，运行期依赖集合未变（两侧各 23 条、包名集合逐项相等）。

**涉及文件（按模块分类）**：

> 明细清单已逐字外迁至 [docs/agent-reference/changelog-file-inventories.md](docs/agent-reference/changelog-file-inventories.md)（条目：v4.3.0-dev (2026-09-26) — 仓库元数据与文档同源同步：依赖表 / 目录树 / egg-info / 忽略清单对齐，清理已删除模块 `weverse_auth` 的残留记载（纯元数据与文档改动，零运行期代码变更）｜小节：涉及文件（按模块分类））。

**验证**：`scripts/check_version.py` rc=0（`pyproject.toml` 为版本唯一事实源，四处消费方均动态读取）；`scripts/check_runtime_pins.py` rc=0；`pytest tests/test_regression_2026_09_22_gates.py tests/test_build_exe.py` 全绿（含「requirements.txt 与 pyproject 包名集合相等」回归锁）；`pytest tests/test_i18n.py tests/test_i18n_migration.py tests/test_i18n_tr.py tests/test_frontend_*.py` 56 passed；`node --test tests/frontend/*.mjs` 通过。

**交回用户（需人工裁定）**：`config/config.ini` 的 `禁用SSL证书验证的平台(逗号分隔)` 现为 `虎牙直播,B站直播,抖音直播`，而代码强制集 `main.SSL_DISABLE_REQUIRED_PLATFORMS` 只有 `虎牙直播`/`B站直播`、README 默认值同为这两个。`抖音直播` 一项属历史遗留的额外豁免（会关闭抖音拉流的证书校验），是否移除由用户决定——本次未擅自改动安全相关开关。

### 更早的更新日志（已归档）

164 条 2026-05-17 ~ 2026-09-24 的逐日开发记录已于 2026-09-28 逐字迁出至 [code-wiki-history-zh.md](docs/changelog/code-wiki-history-zh.md)；该卷同时按 `.workbuddy/docold` 基线回补了上一轮粗剪留下的行尾 `…` / 句中截断（口径见其卷首）。
迁出原因：仅「更新日志」一节就占本文件 68.6% 的字符数（242,626 / 353,821）。根文档只保留当前发布周期的条目 + 本指针，正文才恢复可读。
