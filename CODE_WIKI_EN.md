# DouyinLiveRecorder Project Architecture Document

English&nbsp;&nbsp;|&nbsp;&nbsp;[**简体中文**](CODE_WIKI.md)

## Table of Contents

- [Document Statistics and Index](#document-statistics-and-index)
- [Project Overview](#project-overview)
  - [Project Basic Information](#project-basic-information)
  - [Features](#features)
  - [Supported Platforms](#supported-platforms)
  - [Quality Code Reference](#quality-code-reference)
  - [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [Core Module Details](#core-module-details)
- [Key Classes and Functions](#key-classes-and-functions)
- [Dependencies](#dependencies)
- [Configuration File Reference](#configuration-file-reference)
- [How to Run](#how-to-run)
- [Packaging and Release](#packaging-and-release)
- [Design Patterns](#design-patterns)
- [Troubleshooting](#troubleshooting)
- [Contributing Guide](#contributing-guide)
- [Changelog](#changelog)

## Document Statistics and Index

> This section is summarized from a statistical analysis of **all `*.md` files in the workspace** (first generated on 2026-08-09; re-checked on 2026-09-20; recomputed on 2026-09-27 alongside the doc size pass, and again on 2026-09-28 with the version sync and the changelog split-and-archive).
> **Counts must be recomputable**: the numbers below came from the command written right here, measured 2026-09-28 — a figure that cannot be recomputed counts as stale:
> `python -c "import pathlib; sk={'.git','.venv','node_modules','__pycache__','.mypy_cache','.pytest_cache'}; p=[x for x in pathlib.Path('.').rglob('*.md') if not (set(x.parts) & sk)]; print(len(p))"`

### Statistics Overview

Excluding `.git/`/`.venv/`/`node_modules/`, the workspace contains **106** Markdown files (recomputed 2026-09-28 with the changelog split; +5 over the same-day reading of 101: the four new `docs/changelog/` archive volumes plus one harness session report), grouped by source and maintenance method into seven categories:

| Category | Path | Count | Nature | Manually Maintained |
| --- | --- | --- | --- | --- |
| Project root docs (source of truth) | `AGENTS.md` + `README` / `CODE_WIKI` CN-EN pairs | 5 | Source of truth (CN/EN document pairs) | Yes |
| Architecture reference sub-docs | `docs/agent-reference/**` | 6 | **Purely reference material moved out** of the root docs: directory tree, one-off measured readings, session learnings, lock-classification policy, and the changelog file inventories | Yes |
| One-off review reports | `docs/worklog/*.md` | 9 | Historical review / diagnosis / proposal output: `CODE_REVIEW_2026-09-17` (AGENTS conventions review), `-09-18`, `-09-20`, `-09-21`, `-09-22`, `-09-22_1`, `-09-22_2`, plus `DIAGNOSIS_2026-09-23_*` and `PROPOSAL_2026-09-22_*`; these used to sit at the repo root and are archived here | No (archived) |
| Changelog archives | `docs/changelog/**` | 4 | **Added 2026-09-28**: the historical entry volumes that the root documents' changelogs roll over per release window (`README` / `CODE_WIKI`, two volumes per language); entries are kept verbatim and the volumes are append-only | Yes |
| Local tool-generated docs | `.qoder/**` | 1 | The 302 AI-generated English architecture/knowledge files under `.qoder/repowiki/**` were confirmed absent at the 2026-09-20 re-check; the single remaining file is a harness practice session report | No (auto-generated) |
| Workspace memory | `.workbuddy/**` | 66 | Local agent's daily work logs (53 files under `memory/`) + the `docold/`/`docnew/`/`docopt/` snapshots of earlier doc passes (4 each) + one quality report | No (cache) |
| Historical memory | `.codebuddy/memory/**` | 14 | Legacy agent memory (deprecated) | No (cache) |
| CI sidecars | `.github/**/*.md` | 1 | Notes shipped with workflows / issue templates | Yes |

**Conclusion**: the hand-maintained documents that should act as the source for changes are the **5** root docs (`AGENTS.md` plus the `README` / `CODE_WIKI` CN-EN pairs), the `docs/agent-reference/` sub-docs, and the rolling archive volumes under `docs/changelog/`; the reports under `docs/worklog/` are historical artifacts, `.workbuddy/` is project-level persistent data that must not be deleted, and everything else is AI-generated derivative documentation or a local cache that must not be merged into this document, to avoid introducing content that is out of sync with the code. (Snapshot first generated on 2026-08-09; root-doc count updated to 5 on 2026-08-28 as the CN/EN pairs were completed; refreshed on 2026-09-20: total 324 -> 285, the `.qoder/repowiki/**` directory no longer exists, and a row for the 2 review reports was added. **Since 2026-09-27 this section carries a command-plus-timestamp discipline**: the old 285 shipped without a recompute command and can no longer be reproduced. Measured 101 on 2026-09-27, 106 on 2026-09-28 after the changelog split.)

### Root Document Index

| File | Role | Main Content |
| --- | --- | --- |
| `AGENTS.md` | Coding agent conventions | Single source of truth for version (`pyproject.toml`), code style (black / isort / mypy), project structure, dependency/test/build commands, key conventions |
| `README.md` | User/developer guide | Features, supported platforms (51), quick start, configuration, usage, Docker deployment, development guide, FAQ, changelog |
| `CODE_WIKI.md` | Project architecture doc (Chinese) | Module details, dependencies, design patterns, troubleshooting, contributing guide, changelog |
| `README_EN.md` | User/developer guide (English) | English counterpart of `README.md` (added 2026-08-24, structure aligned with the Chinese version) |
| `CODE_WIKI_EN.md` | Project architecture doc (English) | English counterpart of this document (added 2026-08-24, entries correspond one-to-one with the Chinese version) |

> The five documents are complementary: when changing platform support or configuration items, both `README.md` and the wiki must be updated in sync; engineering conventions follow `AGENTS.md`; `README_EN.md` / `CODE_WIKI_EN.md` are updated in sync with their Chinese counterparts.

### Reference Sub-Document Index (`docs/agent-reference/`)

> This is where purely reference material moved out of the root docs lands. The rule for what may move lives at the top of `AGENTS.md`: constraints stay in the root file, supporting readings and listings move out.

| File | Content | Moved from |
| --- | --- | --- |
| `project-structure.md` | Full directory tree | `AGENTS.md` "Project Structure" |
| `measured-evidence.md` | One-off measured readings (probe speed-up / keepalive / Huya tier sampling / Douyu clamping / release-chain bundle sizes) | long reading blocks at the end of `AGENTS.md` pitfall entries |
| `session-learnings.md` | Session learnings (step 6 of the Definition of Done) | `.workbuddy/memory/*.md` |
| `lock-classification.md` | Re-entrancy classification of locks | `AGENTS.md` "Known pitfalls" |
| `changelog-file-inventories.md` | **Added 2026-09-27**: verbatim text of the 41 "Files involved (classified by module)" inventories from the Chinese changelog; the original spots keep their section heading plus a one-line pointer | `CODE_WIKI.md` changelog |
| `changelog-file-inventories-en.md` | English counterpart of the row above (32 inventory blocks), pointed to from `CODE_WIKI_EN.md` | `CODE_WIKI_EN.md` changelog |

### Changelog Archive Index (`docs/changelog/`)

> **Added 2026-09-28.** This directory has a different job from `docs/agent-reference/`: that one holds purely reference passages lifted out of the root docs, this one holds whole historical changelog entries rolled out of the release window.
> Rotation rule: the root documents keep only the **current release window** (this file) or the **three most recent releases** (`README`); everything older moves to the volume below. When a new entry is written to a root document, the oldest entry that falls out of the window is appended to the matching archive volume.
> The volumes are **append-only**: entry bodies stay verbatim; the only change is the per-line restoration of the trailing `…` / mid-sentence cuts left by the earlier trimming pass, matched against the `.workbuddy/docold` baseline (each volume's header states the exact rule).

| File | Content | Moved from |
| --- | --- | --- |
| `code-wiki-history-en.md` | The 164 historical entries of this document's changelog (2026-05-17 ~ 2026-09-24) | `CODE_WIKI_EN.md` "Changelog" |
| `code-wiki-history-zh.md` | Chinese counterpart of the entries above (164, one-to-one) | `CODE_WIKI.md` "更新日志" |
| `release-notes-history-en.md` | The 17 earlier release notes of `README_EN.md` (v4.0.0 ~ v4.0.9.4, 2024-07-13 ~ 2026-09-06) | `README_EN.md` "Changelog" |
| `release-notes-history-zh.md` | Chinese counterpart of the rows above (17) | `README.md` "更新日志" |

## Project Overview

### Project Basic Information

- **Project Name**: DouyinLiveRecorder (Douyin Live Recorder)
- **Version**: 4.4.0
- **Author**: Hmily
- **License**: MIT
- **Project URL**: [GitHub](https://github.com/ihmily/DouyinLiveRecorder)

### Features

- ✅ Supports 60+ live streaming platforms (Douyin, TikTok, YouTube, Kuaishou, Huya, Douyu, Bilibili, Xiaohongshu, etc.)
- ✅ Continuously monitors live status; auto-records when a stream starts and auto-stops when it ends
- ✅ Multiple output video formats: TS, MKV, FLV, MP4, MP3, M4A
- ✅ Three run modes: CLI + GUI + Web management panel
- ✅ Multi-platform message push: DingTalk, WeChat, email, Telegram, Bark, NTFY, PushPlus
- ✅ Docker containerized deployment
- ✅ Internationalization support (Chinese/English)
- ✅ Flexible configuration: quality selection, segmented recording, custom save paths, etc.
- ✅ Actual quality feedback and downgrade alerting (supports Douyin, TikTok, Kuaishou, Huya, Douyu, Bilibili, NetEase CC)
- ✅ Web security: Token authentication, path traversal protection, sensitive config masking

### Supported Platforms

Summarized from `README.md`; currently **51** platforms are listed (README advertises 60+ externally, including platforms still being added):

**Domestic sites (37)**: Douyin | Kuaishou | Huya | Douyu | YY | Bilibili | Xiaohongshu | bigo | blued | NetEase CC | Qiandu Rebo | Maoer FM | Look Live | TwitCasting | Baidu | Weibo | Kugou | Huajiao | Liuxing | Acfun | Changliao | Inke | Yinbo | Zhihu | Haixiu | VV Planet | 17Live | Lang Live | Piaopiao | 6Rooms | Lehai | Huamao | Taobao | JD | Migu | Lianjie | Laixiu

**Overseas sites (14)**: TikTok | SOOP (formerly AfreecaTV) | PandaTV | WinkTV | TTingLive (formerly Flextv) | PopkonTV | TwitchTV | LiveMe | ShowRoom | CHZZK | Shopee | YouTube | Faceit | Picarto

> Each platform's stream-parsing function lives in `src/stream.py`, and its data-fetching function lives in `src/spider.py`; for adding a new platform see "Contributing Guide → Adding New Platform Support".

### Quality Code Reference

Recording quality is expressed by codes; the corresponding Chinese names and descriptions are as follows (the config item `原画|超清|高清|标清|流畅` maps to this table):

| Quality Code | Chinese Name | Description |
| --- | --- | --- |
| OD | 原画 (Original) | Original Definition, highest quality |
| BD | 蓝光 (Blu-ray) | Blu-ray, ultra high definition |
| UHD | 超清 (Ultra HD) | Ultra HD |
| HD | 高清 (HD) | High Definition |
| SD | 标清 (SD) | Standard Definition |
| LD | 流畅 (Smooth) | Low Definition, lowest quality |

Platforms that support actual quality feedback and downgrade alerting: Douyin, TikTok, Kuaishou, Huya, Douyu, Bilibili, NetEase CC. When the quality actually delivered by the platform is lower than the configured quality, an alert is automatically raised and flagged.

### Tech Stack

| Technology | Purpose |
| --- | --- |
| Python 3.14+ | Core programming language |
| asyncio + httpx | Asynchronous network requests |
| asyncio | Async decorator support |
| FFmpeg | Video recording and transcoding |
| Node.js + exejs/PyExecJS | Run JavaScript signing algorithms (exejs preferred, PyExecJS fallback) |
| Loguru | Structured logging |
| CustomTkinter + pystray + Pillow | GUI and system tray |
| FastAPI + uvicorn | Web management panel backend |
| HTML + CSS + JavaScript | Web management panel frontend |
| Docker | Containerized deployment |
| gettext (msgfmt) | Internationalization translation compilation |
| mypy | Static type checking (`--strict` mode, `disallow_untyped_defs = true`) |
| pyflakes | Static code checking |
| websockets | Danmaku (live comments) WebSocket transport layer (`src/ws_client.py`, shared across platforms) |
| protobuf | Douyin danmaku protocol decoding (`src/proto/douyin_pb2`, protoc-generated module) |
| brotli | Bilibili danmaku decompression (protover=3 requires brotli decompression) |

## System Architecture

### Overall Architecture Diagram

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

### Workflow

1. **Configuration parsing phase**
   - Read the `config/config.ini` main configuration
   - Read the `config/URL_config.ini` live room list
   - Initialize the Node.js environment and FFmpeg path
2. **Live detection phase**
   - Use async tasks to concurrently detect multiple live rooms
   - Platform-specific API calls and signing algorithms
   - Dynamically adjust concurrency to avoid rate limiting
3. **Stream address acquisition phase**
   - Call each platform's live stream API
   - Select different qualities based on configuration (Original/Ultra HD/HD/SD/Smooth)
   - Feed back the quality actually delivered by the platform (`actual_quality`) and available tiers (`available_qualities`)
   - Validate stream address availability
4. **Recording execution phase**
   - Launch the FFmpeg subprocess
   - Monitor recording status in real time
   - Record the actual quality; output an alert log when quality is downgraded
   - Support segmented recording
   - Support transcoding to MP4
5. **Status notification phase**
   - Triggered by live-start/live-end events
   - Call the configured message push channels
   - Write logs

## Directory Structure

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
│   ├── ffmpeg_master_download.py       # FFmpeg master-build downloader (per-platform/arch fetch + verification, challenge-page aware, TOFU)
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
│   ├── notify.py                        # Push/script/success-failure counting/concurrency adjustment (extracted from main.py)
│   ├── scheduler.py                     # Concurrency scheduling hub (adaptive capacity + per-platform circuit breaker + runtime-resizable semaphore)
│   ├── recorder_status.py               # Recording status snapshot and display (extracted from main.py)
│   ├── config_io.py                     # 配置读写/安全数值转换/备份（抽离自 main.py）
│   ├── config_bool.py                   # Boolean config parsing (是/否 equals true/false/1/0/yes/no; dependency-free module)
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
├── uv.lock                              # uv dependency lock file (committed to the repo; image/CI use pip + requirements.txt, do not consume it)
├── pyproject.toml                      # Python 项目配置（版本号/工具配置/覆盖率门禁单一事实源）
├── scripts/                             # 辅助脚本
│   ├── check_version.py                # 版本号一致性校验（CI static job 调用）
│   ├── check_annotations.py            # Annotation-convention & AST-equivalence checker (no docstrings / density floor / --baseline equivalence compare, invoked by the CI static job)
│   ├── check_coverage.py               # Per-module coverage gate (invoked by the CI test job, thresholds in MODULE_THRESHOLDS)
│   ├── compile_po.py                   # gettext catalog compiler (.po → .mo; --check zero-side-effect sync check, invoked by the CI static job)
│   ├── extract_i18n_strings.py         # i18n pending-translation string extractor (AST scan + four-catalog comparison, maintenance-time tool)
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
│   ├── test_scheduler.py               # Scheduler tests (ResizableSemaphore / PlatformBreaker / ConcurrencyScheduler, 16 cases)
│   ├── test_record_failure_feedback.py # Recording failure feedback tests (success/fast-fail backoff/slow-fail/missing -i/capacity fallback/direct-download failure & success sampling, 7 cases)
│   ├── test_stream_select.py           # Stream selection and probe backoff marking tests
│   ├── test_cookie_cache.py            # Visitor Cookie cache tests
│   ├── test_danmaku_monitor.py         # Danmaku monitoring hub tests
│   ├── test_http_config.py             # HTTP configuration tests
│   ├── test_config_io_readonly.py      # Config readonly/language key migration tests
│   ├── test_config_io_backup.py        # Config backup tests
│   ├── test_bilibili_danmaku_info.py   # Bilibili danmaku info fetch tests
│   ├── test_huya_danmaku.py            # Huya danmaku tests
│   ├── test_concurrency_rate_limit.py  # Douyin rate-limit concurrency test
│   ├── test_node_install.py            # Node.js auto-installer offline tests (added 2026-09-21)
│   ├── test_web_tray.py                # Web console system-tray offline tests (added 2026-09-21)
│   ├── test_platform_danmaku_offline.py # Douyu/Bilibili/Twitch danmaku frame codec offline tests (added 2026-09-21)
│   ├── test_config_io_update_file.py   # Config write-side tests (update_file / anchor name / backup redaction) (added 2026-09-21)
│   └── test_video_postprocess_paths.py # Video post-processing branch and exception-classification tests (added 2026-09-21)
├── .github/                             # GitHub Actions workflow directory
│   ├── ISSUE_TEMPLATE/                 # Issue templates (Bug report / Feature request)
│   ├── PULL_REQUEST_TEMPLATE.md         # PR template
│   ├── actions/
│   │   └── retry/                      # Composite action: linear-backoff retry wrapper for network install commands (shared by ci.yml / build-release.yml)
│   └── workflows/
│       ├── ci.yml                      # CI static verification (setup/static/typecheck/test/concurrency/integration/build-verify/summary)
│       ├── build-release.yml           # Three-platform build (lite + full dual artifact) + auto-publish Release
│       └── issue-translator.yml        # Issue auto-translation workflow (CN↔EN)
├── .coveragerc-concurrency             # Concurrency test coverage config (used by CI concurrency-test job, no global threshold)
├── CODE_WIKI.md                        # This architecture document (Chinese)
├── CODE_WIKI_EN.md                     # This architecture document (English)
├── README_EN.md                        # Project README (English)
```

## Core Module Details

### 1. Main Program Module (`main.py`)

**Responsibility**: The command center of the entire recorder, responsible for workflow orchestration.

**Core functions**:

- Configuration file reading and parsing
- Live room URL list parsing
- Concurrency control and task scheduling
- FFmpeg process management
- Error retry and dynamic tuning
- Message push triggering
- Exit signal handling

**Key state variables**:

```python
recording: set              # 正在录制的直播间集合
monitoring: int             # 正在监控的直播间数
running_list: list          # 正在运行的 URL 列表
error_count: int            # 当前错误计数
error_window: list          # 错误时间窗口（用于动态调优）
url_tuples_list: list       # 解析后的 URL 配置列表 [(quality, url, anchor_name)...]
recording_time_list: dict   # 录制时间与画质记录 {name: [start_time, quality_zh, actual_quality_zh]}
```

**Main flow functions**:

- `main()` - entry function
- `read_config()` - read configuration
- `check_url_config()` - check URL configuration
- `start_recording()` - start recording (parses `actual_quality`, outputs an alert on downgrade)
- `stop_recording()` - stop recording
- `check_live_status()` - detect live status
- `display_info()` - terminal status display (compatible with old and new `recording_time_list` formats)
- `get_status()` - return recording status dict (includes the `actual_quality` field, used by the Web API)
- `select_source_url()` - selects between m3u8/FLV sources, falling back to FLV when HLS source validation fails (polling with `delay_default=120s`); a new `proxy_addr` parameter is passed through to the three validation calls to avoid misjudging proxy-required platforms like TikTok as unreachable on direct validation; computes the "last-resort candidate" (when FLV has no `record_url` fallback, or `record_url` is always present) and passes it to the validator as `last_resort` — even a stable rejection only warns and passes through, leaving the final decision to ffmpeg's actual stream pull; **HLS capture exclusion list** (`main.hls_collection_exclude_platforms`, config key "HLS采集排除平台(逗号分隔)"): listed platforms ignore the "whether to enable HLS capture" setting and always use FLV capture (equivalent to disabling HLS capture for that platform only — the whole HLS candidate group is removed with no fallback; when only HLS sources remain with no fallback, it warns and gives up the round, with recovery guidance pointing to removing the platform from the exclusion list); platforms outside the list behave unchanged
- `_validate_stream_url()` - stream address validation: the content-type check now also accepts `mpegurl`; when HEAD is rejected, for `.m3u8` sources (including **404**) it adds a `Range: bytes=0-0` GET probe — Douyin CDN's m3u8 often returns 4xx to HEAD, which used to be misjudged as unreachable and always fell back to FLV; a new `verify` parameter follows the global SSL switch (consistent with async validation); all failure paths now log a warning (URL + exception type/status code/content-type) instead of silently swallowing the exception; the GET re-check (`_confirm_get_ok`) retries once verbatim (0.8s interval) when receiving 401/403 before convicting — CDNs such as Douyu hw/Huya al occasionally return 403 to millisecond-level back-to-back probes (HEAD→GET) (in practice the same URL returns 200 after a brief retry, and ffmpeg's single GET works normally); the retry distinguishes "intermittent rate limiting" from "stable rejection", and the historically false-green Huya scenario that still returns 403 after retry is correctly rejected

**Refactoring (2026-08-16)**: The following responsibilities have been extracted into `src/` submodules, re-exported by `main.py` to preserve `main.<name>` namespace compatibility (zero changes to `web.py`/`gui.py`/`web_api.py`/tests):

- FFmpeg process management → `src/ffmpeg_proc.py` (process register/unregister/terminate/cleanup)
- Video post-processing (segment/transcode/subtitle) → `src/video_postprocess.py`
- Stream address selection/validation/quality-code/Douyin rate-limit → `src/stream_select.py` (`select_source_url`/`_validate_stream_url`/`get_quality_code`/`_douyin_rate_limit`, etc.)
- Push/script/success-failure counting/concurrency adjustment → `src/notify.py` (`push_message`/`record_error`/`record_success`/`adjust_max_request`/`clear_record_info`, etc.)
- Recording status snapshot/display → `src/recorder_status.py` (`get_status`/`display_info`)
- Config read/write/safe numeric conversion/backup → `src/config_io.py` (`update_file`/`delete_line`/`read_config_value`/`_safe_int`/`_safe_float`/`backup_file`/`backup_file_start`)

Modules deeply coupled to main's globals uniformly use a runtime `import main` to lazily access globals, avoiding parameter bloat at call sites during startup; a `__main__` guard is added at the top of `main.py` to prevent a submodule's `import main` from re-executing the entire file when running `python main.py`.

**Room recording thread closure fix (2026-08-16)**: When adding a new live room, a daemon thread is spawned for each URL to run `start_record`. The original implementation used "default-argument binding of loop variables" (`def _room_thread_target(_key=thread_key, _args=args)`) to avoid the closure late-binding trap, and `_args: tuple[Any, ...]` used an explicit `Any` that the project's basedpyright globally disallows. After the fix:

- `_args` is concretized to `tuple[tuple[str, str, str], int]` (`url_tuple` is `tuple[str, str, str]`, consistent with the `start_record(url_data, count_variable)` signature);
- the current loop value is explicitly bound at thread creation via `threading.Thread(target=..., args=(thread_key, args))`, removing the default-argument hack for clearer and more maintainable semantics;
- the thread still cleans up on exit with `finally: create_var.pop(_key, None)`, preventing unbounded growth of the `create_var` dict.

**Danmaku recording integration (finalized wiring on 2026-08-16)**: Each platform branch of `start_record` collects `record_danmaku_args` (reset to `None` each round) → all 6 `check_subprocess(..., platform=platform, danmaku_args=record_danmaku_args)` calls are wired up → `get_danmaku_collector(platform, args, base_filename, segment_seconds)` creates the collector. The collector calls `stop()` outside the `while process.poll() is None` loop (`DanmakuCollector.stop()` has `_stop_called` to prevent re-entry, idempotent). Segmented filename convention: the ffmpeg video segment template is unified to `_%03d` (FLV aligned from `_%02d`; audio still uses `_%02d` but has no danmaku), SRT shards use `{seg:03d}` (`_000.srt` pairs with `_000.ts`); `check_subprocess` also strips the `_%02d`/`_%03d` placeholders. When Douyin has an empty cookie, `DouyinDanmaku.start()` dynamically fetches it via `await get_ttwid()` inside the coroutine (the collection thread has its own event loop, so it can `await` directly; process-level cache). "Danmaku shard duration (seconds)" goes through `_safe_float(..., 1800.0)`. The danmaku platform registry is `get_danmaku_class` in `src/__init__.py` (Douyu Live / Bilibili Live / Huya Live / Douyin Live / TwitchTV).

**Room log correlation field binding (2026-09-20)**: `start_record`, being the room-thread body, calls `set_room_context(f"序号{count_variable}")` at the **thread entry** (otherwise the logs that precede `record_name` — exit flag / commented-out exit / resolution failure / breaker back-off — could not be attributed to a room), and upgrades the value to the full room name after each round assigns `record_name = f"序号{count_variable} {anchor_name}"`. How the field reaches the log line, and which threads do or do not carry it, is documented in "6. Logging Module" and the `AGENTS.md` "Known pitfalls" entry.

### 2. Spider Module (`src/spider.py`)

**Responsibility**: Responsible for fetching live room data from each major streaming platform.

**Supported platforms**:

Domestic: Douyin, Kuaishou, Huya, Douyu, YY, Bilibili, Xiaohongshu, bigo, blued, NetEase CC, Qiandu Rebo, Maoer FM, Look Live, TwitCasting, Baidu, Weibo, Kugou, Huajiao, Liuxing, Acfun, Changliao, Inke, Yinbo, Zhihu, Haixiu, VV Planet, 17Live, Lang Live, Piaopiao, 6Rooms, Lehai, Huamao, Taobao, JD, Migu, Lianjie, Laixiu

Overseas: TikTok, SOOP (formerly AfreecaTV), PandaTV, WinkTV, TTingLive (formerly Flextv), PopkonTV, TwitchTV, LiveMe, ShowRoom, CHZZK, Shopee, YouTube, Faceit, Picarto

**Key functions**:

- `get_douyin_web_stream_data()` - fetch Douyin Web-end live data (prefers the `web/enter` API, silently retries once on failure, then falls back to HTML scraping)
- `get_douyin_app_stream_data()` - fetch Douyin App-end live data (fallback; contains built-in URL dispatch logic, see "Douyin URL Dispatch" below)
- `get_tiktok_stream_data()` - fetch TikTok live data
- `get_youtube_stream_data()` - fetch YouTube live data
- `get_bilibili_stream_data()` - fetch Bilibili live stream data (returns a dict containing url/current_qn/accept_qn)
- `get_play_url_list()` - fetch clarity options from the M3U8 playlist
- `get_params()` - extract parameters from URL

**Douyin URL dispatch logic** (`get_douyin_app_stream_data`, optimized on 2026-08-01):

| URL Form | Handling Path |
| --- | --- |
| `live.douyin.com/<room number or Douyin ID>` | Directly calls `get_douyin_web_stream_data` (the `web/enter` API accepts Douyin IDs, no redirect resolution needed) |
| `www.douyin.com/user/<sec_uid>` (web homepage) | Skips the doomed-to-fail `get_sec_user_id` probe and uses `resolve_from_homepage()`: `get_unique_id()` resolves the Douyin ID → assembles `live.douyin.com/<Douyin ID>` → directly calls the web endpoint |
| `v.douyin.com/<short link>` (App short link, may point to a live room or homepage) | First `get_sec_user_id()` to follow the redirect; on `UnsupportedUrlError` falls back to `resolve_from_homepage()` |

- `resolve_from_homepage()` directly calls `get_douyin_web_stream_data` (web API preferred, with built-in HTML fallback), no longer routing through the old HTML-first scraping path (about 1MB page), and **explicitly passes through proxy_addr / cookies** (the old implementation did not, causing proxy and Cookie config to silently fail on the homepage path)
- The `web/enter` API call is wrapped as `_try_web_api()` + `for attempt in range(2)`: on first failure (e.g. transient risk-control `status_code=10002`) → `await asyncio.sleep(0.5)` to buffer → silent retry; on retry success returns directly, skipping the HTML fallback; only when both attempts fail is a WARNING logged and HTML fallback used (HTML scraping for the HEVC original is common behavior across all web-end paths and is unchanged)

**Implementation characteristics**:

- Uses the async HTTP client (`httpx`)
- Platform-specific signing algorithms
- Proxy support
- Cookie support
- Error retry mechanism
- The Bilibili spider returns a dict structure (containing `current_qn`/`accept_qn` metadata) for the stream module to feed back the actual quality

### 3. Live Stream Parsing Module (`src/stream.py`)

**Responsibility**: Parse live stream addresses, support multiple quality selection, and feed back the quality actually delivered by the platform.

**Quality mapping**:

```python
QUALITY_MAPPING = {"OD": 0, "BD": 1, "UHD": 2, "HD": 3, "SD": 4, "LD": 5}
QUALITY_MAPPING_BIT = {
    'OD': 99999, 'BD': 4000, 'UHD': 2000, 'HD': 1000, 'SD': 800, 'LD': 600
}
QUALITY_LEVEL = {"OD": 0, "BD": 0, "UHD": 1, "HD": 2, "SD": 3, "LD": 4}  # 等级值越大画质越低
QUALITY_CODE_TO_ZH = {"OD": "原画", "BD": "蓝光", "UHD": "超清", "HD": "高清", "SD": "标清", "LD": "流畅"}
NETEASE_QUALITY_MAP = {"blueray": "OD", "ultra": "UHD", "high": "HD", "standard": "SD"}
```

**Quality utility functions**:

- `bitrate_to_quality(bitrate)` - reverse-lookup the quality code from bitrate (0/unknown falls back to OD)
- `code_to_zh(code)` - convert quality code to Chinese name
- `is_downgrade(requested, actual)` - determine whether a downgrade occurred (actual level value > requested)
- `get_quality_index()` - parse the quality parameter and return an index
- `_pad_list()` - pad a list to a specified minimum length (some platforms now use explicit truncation instead)

**Per-platform stream address parsing functions**:

| Function | Platform | Actual-quality feedback method |
| --- | --- | --- |
| `get_douyin_stream_url()` | Douyin | Extract quality label from keys of `flv_pull_url` / `hls_pull_url_map` |
| `get_tiktok_stream_url()` | TikTok | Reverse-lookup via `bitrate_to_quality()` from the `vbitrate` field |
| `get_kuaishou_stream_url()` | Kuaishou | Reverse-lookup from the `bitrate` field of `flv_url_list` |
| `get_huya_stream_url()` | Huya | Map from the `exsphd` ratio value, handle downgrade selection |
| `get_douyu_stream_url()` | Douyu | Reverse-map from the platform-delivered `rate` field |
| `get_bilibili_stream_url()` | Bilibili | Reverse-map `current_qn` returned by spider into a quality code |
| `get_netease_stream_url()` | NetEase CC | Map from quality name (blueray/ultra/high) via `NETEASE_QUALITY_MAP` |

**Return value structure** (unified across platforms):

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

**Implementation characteristics**:

- Bandwidth-sorted clarity selection
- Automatic downgrade strategy (auto-downgrade when preferred quality is unavailable)
- FLV and M3U8 dual-protocol support
- Status code validation
- Explicit truncation replacing `_pad_list`'s silent padding, avoiding out-of-bounds
- Quality downgrade detection (`is_downgrade`), used by main.py for alerting
- Douyu FLV→m3u8 same-token HLS candidate: when `rtmp_live` ends with `.flv`, `get_douyu_stream_url` changes the path `.flv` to `.m3u8` (query string preserved as-is) and attaches it as `m3u8_url` — Douyu's wsAuth token works for both FLV and HLS (verified: hw CDN returns 200 + `application/vnd.apple.mpegurl`, two-level m3u8); when HLS collection is enabled it is validated and preferred via `select_source_url`, falling back to FLV when unreachable; HLS pulls segment-by-segment without maintaining a long connection, mitigating the repeated segmentation caused by the visitor-state FLV long connection being cut by the CDN after about 70 seconds

### 4. Live Room Info Module (`src/room.py`)

**Responsibility**: Parse live room URLs, extract room ID, anchor info, Douyin ID, etc.

**Key functions**:

- `get_sec_user_id()` - get the room ID and the user's sec_user_id
- `get_unique_id()` - get the Douyin ID (includes a 30-minute TTL sec_uid→Douyin-ID process-level cache, aligned with `ttwid.py`'s `threading.Lock` cross-thread/cross-asyncio-loop deduplication pattern)
- `is_user_homepage_url()` - determine whether a URL is in the "web anchor homepage" form (`douyin.com/user/<sec_uid>`; `v.douyin.com` short links do not belong to this category); used as a zero-request fast path — the sec_user_id is directly in the path, no request needed to follow a redirect
- `extract_sec_user_id()` - explicitly regex-extract sec_user_id from the URL
- `get_live_room_id()` - get the live room web ID
- `get_xbogus()` - generate the X-Bogus signature

**Exception handling**:

- `UnsupportedUrlError` - unsupported URL format exception

**Key constants and interfaces**:

- `DESKTOP_UA` - desktop Chrome UA. Interfaces such as `iesdouyin.com/web/api/v2/user/info/` will be silently rate-limited (HTTP 200 + empty body) if an old mobile UA is used; the desktop UA must be used
- Homepage parsing uses the JSON interface `https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=<sec_uid>` (take `unique_id`, fall back to `short_id` if empty) — the old `iesdouyin.com/share/user/<sec_uid>` page is now a JS anti-scraping shell page, and HTML regex is unreliable

### 5. Utility Module (`src/utils.py`)

**Responsibility**: Provide general-purpose utility functions.

**Main utilities**:

| Utility Function | Description |
| --- | --- |
| `Color` class | Terminal color output constants |
| `trace_error_decorator()` | Error tracing decorator |
| `check_md5()` | Compute file MD5 |
| `dict_to_cookie_str()` | Convert cookie dict to string |
| `read_config_value()` | Read configuration file value |
| `update_config()` | Update configuration file |
| `remove_emojis()` | Remove emoji from text |
| `remove_duplicate_lines()` | Remove duplicate lines from a file |
| `handle_proxy_addr()` | Normalize proxy address format |
| `generate_random_string()` | Generate a random string |

### 6. Logging Module (`src/logger.py`)

**Responsibility**: Configure structured logging based on Loguru.

**Log output**:

- **Console**: colorized log output (`custom_format`, no room column)
- **`logs/streamget.log`**: DEBUG level (excluding INFO), line layout `time | level | room | module:function:line - message`
- **`logs/PlayURL.log`**: INFO level (live stream addresses only), line layout `time | room | message`
- **`logs/gui.log`**: written only by the GUI parent process (exclusive handle), carries no room column — the GUI process does not record, so the column would always be empty

**Room correlation field `extra[room]` (added 2026-09-20)**:

- Every line emitted by a room thread carries a stable correlation column, used to cut a single room's chain out of the interleaved multi-room log file (extraction command and boundaries: the identically named `AGENTS.md` "Known pitfalls" entry)
- Implementation: `ROOM_FIELD` plus `set_room_context()` / `get_room_context()` reading and writing a `ContextVar`, pushed into `record["extra"]` by the global patcher registered via `logger.configure(extra={ROOM_FIELD: ""}, patcher=_room_patcher)` **in the calling thread** (hence no cross-talk under `enqueue=True`); an explicit call-site `bind(room=...)` outranks the thread-level fallback
- The room thread binds `序号N` at the `main.py::start_record` entry and upgrades it to the full `record_name` once the anchor name resolves; `set_room_context("")` unbinds
- **The `extra` default must not be removed**: without it, formatting an unbound record raises `KeyError: 'room'`, loguru swallows it, prints `Logging error in Loguru Handler` to stderr for every line and drops the line; regression lock `tests/test_logger_room_context.py`
- Only the identifier was added: log levels, the two INFO/other `filter` buckets, `rotation` and `retention` are unchanged

**Log file switch**:

- Controlled via `是否启用日志文件(是/否)` in `config/config.ini`
- Enabled by default, preserving backward compatibility
- `logger.py` reads the configuration directly at initialization (not dependent on main.py execution order)

**Log rotation**: auto-rotates at 300 KB, keeping 1 backup

### 7. Message Push Module (`msg_push.py`)

**Responsibility**: Support multiple message push channels.

**Supported channels**:

| Channel | Function | Description |
| --- | --- | --- |
| DingTalk | `dingtalk()` | Group bot push |
| WeChat | `xizhi()` | Server酱 / WeChat |
| Telegram | `tg_bot()` | Bot message |
| Email | `send_email()` | SMTP protocol |
| Bark | `bark()` | iOS notification |
| NTFY | `ntfy()` | Open-source push service |
| PushPlus | `pushplus()` | WeChat push platform |

### 8. Internationalization Module (`i18n.py`)

**Responsibility**: A gettext-based multilingual support system that automatically translates `print` output from the project source code.

**Implementation mechanism**:

- `translated_print` wraps `builtins.print`, automatically translating output whose caller comes from the project root (`src/` package and top-level scripts like `main.py`); `main.py` unconditionally installs `builtins.print = translated_print` at import time (installed under any language — zh_CN/zh_TW translate English constant strings into Chinese, en_US/en_GB translate Chinese strings into English, unknown strings are returned identically)
- Supports both source-run and PyInstaller-packaged path detection (`_internal/i18n` vs `i18n/`)
- **Multi-format catalog loading (since 2026-08)**: `i18n.py` probes in order gettext `.mo` → `<lang>.json` → `<lang>.yaml`; all three formats are flat "original → translation" mappings with consistent behavior; `PyYAML` is a runtime dependency (only YAML format support is lost if missing). `_load_yaml_catalog()` catches `yaml.YAMLError` (not an OSError/ValueError subclass) — a corrupted yaml catalog returns None and degrades to the next format instead of letting `set_language` raise (web language-switch endpoint 500)
- **Hot language switch**: `set_language(lang)` normalizes (via the `normalize_language` alias table: `zh_cn`/`zh-CN`/`en`/`en-US`/`zh-Hant`/`zh_CN.UTF-8` and other spellings all work) then hot-swaps the `_tr` translation function without restarting the process. Three switch entry points: Web panel (`GET/PUT /api/language`, writes back to config + hot switch + redraws frontend `data-i18n` text; on `PUT`, a missing `language` config key now falls back to appending it at the end of its section instead of an unconditional 500), GUI (sidebar "Language" menu), CLI main loop (re-syncs per round from config)
- Default language: Simplified Chinese (zh_CN); supported languages: zh_CN / en_US / en_GB / zh_TW

**Translation files**:

| File | Description | Entries |
| --- | --- | --- |
| `i18n/zh_CN/LC_MESSAGES/zh_CN.po` | Simplified Chinese translation source (gettext, editable) | 496 |
| `i18n/zh_CN/LC_MESSAGES/zh_CN.mo` | Compiled binary translation (the only file gettext reads at runtime, distributed with repo/image) | 496 |
| `i18n/en_US.json` | US English catalog (JSON format, English source identical + Chinese source translated to English) | 496 |
| `i18n/en_GB.json` | UK English catalog (JSON format, British spelling: minimise/unrecognised, etc.) | 496 |
| `i18n/zh_TW.yaml` | Traditional Chinese catalog (YAML format, simplified→traditional character conversion + Taiwan usage adaptation) | 496 |

**Maintenance workflow**: After modifying `.po` you must run `python scripts/compile_po.py` to recompile and commit the `.mo` together, otherwise translation changes will not take effect; `python scripts/compile_po.py --check` (CI `static` job) blocks when the two are out of sync — internally `write_mo()` is **pure in-memory output with no disk write**, so `--check` has zero side effects and genuinely compares against the committed `.mo` on disk; only non-check mode writes the file. The CI path filter (paths-filter) treats `i18n/**` as a trigger condition: translation-only changes also run this gate. **The key sets of all four language catalogs must be consistent** (enforced by `tests/test_i18n.py::test_catalogs_share_same_keyset`) — when adding a new msgid you must update all four catalogs. To extract and compare pending-translation strings, run `python scripts/extract_i18n_strings.py` (AST-scans runtime code for print constant strings + logger f-string template drafts and compares against the four catalogs; f-string template normalization conventions: format/conversion specifiers dropped, double quotes inside expressions converted to single quotes; pure-placeholder templates (e.g. `{color}{text}`) and the gettext header empty msgid are filtered out, producing no noise).

**Translation coverage** (after the full 2026-08-27 replenishment, covering all runtime constant strings and logger template drafts):

- `src/spider.py` — per-platform live data fetch/login/risk-control messages (including the Bilibili buvid auth chain)
- `main.py` — main program general messages, recording chain, quality downgrade, anchor-name sync, disk space
- `gui.py` — GUI interface messages (widget text, process management, tray, exit confirmation)
- `src/scheduler.py` — concurrency mode switching and capacity-adjustment broadcasts
- `src/stream_select.py` — the full stream-URL validation message set (probe backoff, GET recheck, last-resort pass-through)
- `src/collector.py` / `src/danmaku_monitor.py` — danmaku capture and monitoring
- `src/async_http.py` / `src/sync_http.py` / `src/cookie_cache.py` — HTTP clients and cookie cache
- `msg_push.py` — seven-channel push-failure branches (WeChat/DingTalk/TG/Bark/ntfy/PushPlus/email)
- `src/ffmpeg_install.py` / `src/node_install.py` — ffmpeg/Node.js auto installation
- `src/config_io.py` / `src/utils.py` — config read/write, backup, disk space
- `src/notify.py` — custom script execution errors
- `web.py` / `src/web_tray.py` — web panel startup and tray
- `src/room.py` / `src/recorder_status.py` / `src/ttwid.py` / `src/ffmpeg_proc.py` / `src/platforms/bilibili.py` / `src/platforms/douyin.py` / `build_exe.py` — remaining runtime messages

> Note: What actually participates in translation lookup at runtime is the constant English string output by `print()`; `logger.*` output and f-string-interpolated text do not go through lookup, and the related entries in the catalogs are kept only as ready-made translation drafts for later log i18n integration.

### 9. GUI Module (`gui.py`)

**Responsibility**: Provide a modern graphical user interface.

**Design features**:

- **High-contrast color system**: meets the WCAG AA accessibility standard
- **DPI-aware fonts**: adaptive resolution scaling
- **System tray**: minimize to tray
- **Modern components**: card-based design, gradient banner, status indicators

**Main components**:

- `Colors` - color constant class
- `DpiFont` - DPI-aware font system
- `SystemTray` - system tray management
- `CardFrame` - card container
- `GradientBanner` - gradient banner
- `StatusIndicator` - status indicator
- `ModernTextWidget` - modern text widget

**Navigation pages**:

- 📊 Console - recording status overview, start/stop control
- 🎯 Quality Monitor - detect in real time whether each room's actual quality matches the setting
- 📝 URL Config - live room address management
- 📋 Run Logs - subprocess log viewer

**Quality Monitor page** (`_build_quality_page`):

- Obtains quality info by parsing the stdout log of the main.py subprocess
- Parses the loguru log prefix (`|` + `-` separators) to extract the message content
- Downgrade alert match: `{name} 画质降级：设置 {zh}({code}) 实际 {zh}({code})`
- Recording status match: `{name}[{quality}] 正在录制中 {duration}`
- Statistics cards: recording / quality normal / quality downgraded counts
- Downgraded rows are highlighted with a red background; normal rows show "✓ Same"
- Thread safety: `_quality_lock` protects shared data; UI updates run only on the main thread
- Timeout cleanup: recording markers not updated for 30 seconds are auto-cleared

### 10. Async HTTP Client (`src/async_http.py`)

**Responsibility**: Wrap httpx to provide a unified async HTTP interface.

**Features**:

- Proxy support
- Timeout setting
- Auto retry
- Status code checking
- HTTP/2 support
- **Connection pool reuse**: reuse AsyncClient by (proxy, verify, http2) dimensions, leveraging the keepalive connection pool
- **Event loop detection**: cache and record the event loop reference at each client's creation; automatically rebuild the client when `asyncio.run()` causes a loop change, avoiding the `'NoneType' object has no attribute 'send'` error
- **Module-level lock rebuilt with the event loop** (fixed 2026-08-12): the `_client_lock` protecting `_client_cache` reads/writes was a module-level singleton `asyncio.Lock()`; after it lazily bound to the first room's `asyncio.run()` loop, subsequent rooms each started a new loop via `asyncio.run()` and `await`ing it again triggered `RuntimeError: ... is bound to a different event loop`; that exception was swallowed by `async_req` and returned an empty string, which `spider.py` misjudged as "risk-control empty response" and cascaded into HTML fallback failure. Now `_get_client_lock()` caches a `(lock, loop)` tuple and automatically rebuilds the lock when the current loop changes, consistent with `_client_cache`'s "client + loop" mechanism, eliminating cross-loop lock errors at the source
- **Typed exception logs** (consolidated 2026-08-12): all `except Exception as e: logger.debug(e)` inside `async_req` and `_close_all_clients` now include `type(e).__name__` (with URL when necessary), eliminating the blank-log problem on Windows when an exception's `str()` is empty and impossible to locate
- **SSL verification**: uniformly controlled by the global config `src/http_config.py`, enabled by default
- **No more scheduled close of stale cross-loop clients** (fixed 2026-09-04): when evicting a stale AsyncClient created on another event loop, **no** `aclose()` coroutine is ever created (running / stopped / closed old loops are all treated the same); the reference is dropped and GC handles cleanup. The old implementation scheduled via `run_coroutine_threadsafe` without waiting — when the old loop sat inside the `asyncio.run` teardown window (stopped but not yet closed) the callback never executed, and GC reported "coroutine ... aclose was never awaited" with randomly fluctuating counts (1~2 flaky occurrences, escaping via unraisableexception); the "is_running gate + wait for future" variant was empirically still incurable (during teardown a scheduled task may be created yet never stepped — `Task was destroyed but it is pending` — and a never-resolving future amplifies the race into multi-second blocking); awaiting directly on the current loop would operate a transport bound to the old loop. Regression locks: `tests/test_async_http_lock.py::test_cross_loop_running_old_loop_skips_close` / `test_cross_loop_stopped_old_loop_skips_close`
- **Connection pool cleanup**: release all reused AsyncClients on process exit via atexit / signal handlers
- **`get_response_status()` m3u8 fault tolerance** (enhanced 2026-08-05): when HEAD validation fails, if the URL ends with `.m3u8` it adds a lightweight `Range: bytes=0-0` GET probe (all non-2xx including **404** trigger the probe; returns 200/206 → reachable); behavior for non-m3u8 sources (FLV/record_url) is unchanged. Exception logs include URL + `type(e).__name__` (e.g. `ConnectTimeout` / `TimeoutError`), avoiding blank messages when Windows `socket.timeout`'s `str()` is empty; probe failures log `status_code` / `content-type` for troubleshooting

**Imported by**:

- `src/spider.py` - `async_req()`
- `src/stream.py` - `get_response_status()`

### 11. HTTP Client Configuration (`src/http_config.py`)

**Responsibility**: Provide shared runtime configuration for HTTP clients.

**Features**:

- Global SSL certificate verification switch (`ssl_verify`), enabled by default (True, security first); integrated into "whether to enable https recording" — enabled = https pull + disable cert verification, disabled = http pull + default strict verification (hot-synced by main.py each round)
- Provides `set_ssl_verify()` / `set_https_recording()` functions, set at startup from the main config and each round in the main loop
- Platform-level SSL override (`ssl_verify_platform_overrides`): kept for compatibility; integration does not change actual behavior
- Async / sync HTTP clients read this config when issuing requests

### 12. Sync HTTP Client (`src/sync_http.py`)

**Responsibility**: Wrap requests and urllib to provide a synchronous HTTP interface.

**Features**:

- Proxy support
- Timeout setting
- Cookie support
- Redirect tracking
- **SSL verification**: uniformly controlled by the global config `src/http_config.py`, and overridable **per single call** via the `ssl_verify` parameter (see below)
- **Session lifecycle management (2026-09-02)**: the thread-local `requests.Session` is registered through a module-level `WeakSet` (entries are reclaimed automatically once a thread dies, GC is never blocked); `atexit` registers `close_all_sessions()` to shut down every still-live connection pool gracefully at process exit (80+ rooms running for a long time); `close_session()` additionally lets a room thread release its own Session explicitly on the exit path, and the next `_session()` call rebuilds it automatically
- **Opener construction shape (after F-12; this subsection recalibrated 2026-09-24)**: only `_opener_secure` (proxy disabled, certificate verification kept) is pre-built at module level; the non-verifying `SSLContext` and its opener are always built **lazily on demand** (`_get_insecure_context()` / `_get_insecure_opener()`) — the 2026-09-12 review item 6.7 pointed out that a non-verifying context existing at import time equals a silent process-wide downgrade surface, so reverting to module-level residency is forbidden
- **`ssl_verify` per-call override (F-12)**: `sync_req(..., ssl_verify=None/True/False)` is decided by `_resolve_ssl_verify()` (`None` = follow the `http_config.ssl_verify` global switch; an explicit value wins for that call), and the same decision must be **passed through both the urllib and the requests (proxy) paths** — credential-carrying call sites can force verification instead of being dragged down by the global switch
- **Public accessor for the thread-level Session (MIN-08)**: `session()` serves call sites that must read the status code / response headers and therefore cannot use `sync_req` (whose failure contract collapses everything into an empty string) while still reusing the same connection pool; the patch target remains `_session` (test convention)
- **Response body caps (SEV-2226 follow-up, 2026-09-23)**: on the proxy-free urllib path both caps are required — `_read_capped()` limits the compressed/raw body read (`_MAX_RESPONSE_BYTES`, 8 MiB) and `_gunzip_capped()` decompresses in chunks while limiting the produced bytes (`_MAX_DECOMPRESSED_BYTES`, 32 MiB); exceeding a cap raises `ValueError`, which the existing failure branch logs masked and turns into an empty string. **The proxy branch's `response.text` is gzip-decoded by requests itself and is still NOT covered by these caps** (known residual gap, see the source comment)
- **Current status (SEV-2226 forensics, 2026-09-23)**: this module **currently has no production importer at all** (`src/spider.py` uses the httpx async surface via `from .async_http import async_req`; the former caller `src/weverse_auth.py` was deleted on 2026-09-23); keeping or removing it is left to the maintainer — the module still carries the F-12 invariant and the `tests/test_sync_http.py` regression lock on it

### 13. Web Management Panel (`web.py` + `src/web_api.py` + `src/web_config.py` + `web/`)

**Responsibility**: Provide a Web interface to remotely manage the recorder, including dashboard, live room management, config editing, and log viewing.

**Architecture**:

- `web.py` - entry: a daemon thread runs `main.main()`, the main thread runs uvicorn; supports a hidden background run mode
- `src/web_api.py` - FastAPI app: authentication (Token), REST API routes, SSE push, static asset mounting
- `src/web_config.py` - config read/write (does not depend on FastAPI, convenient for unit tests)
- `web/` - frontend static assets (single-page application)

**Background run mode** (`web_show_console = false`):

- `_enter_background_mode()` is called before starting the recording engine
- On Windows, `ctypes` calls `GetConsoleWindow()` + `ShowWindow(hwnd, SW_HIDE)` to hide the console window
- stdout/stderr redirected to `logs/web_console.log` (line-buffered, written in real time)
- The program runs fully in the background and is managed via the Web panel
- Restore console: set `web_show_console = true` and restart

**Console encoding / `ctypes` robustness (fixed 2026-08-16)**:

- kernel32 / user32 `WinDLL` handles are cached as module-level singletons (`_KERNEL32` / `_USER32`), avoiding repeated DLL loads when `_fix_encoding()` and `_enter_background_mode()` are called multiple times; on load failure they remain `None` and subsequent calls auto-retry
- Completed `restype` declarations: `SetConsoleOutputCP` / `SetConsoleCP` return `BOOL` (explicit `restype = ctypes.c_int`), `ShowWindow` returns `BOOL`, consistent with the existing `GetConsoleWindow.restype = c_void_p`, eliminating implicit reliance on ctypes' default return type
- In `_enter_background_mode()`, `GetConsoleWindow()` already returns `c_void_p`; removed the redundant `cast(ctypes.c_void_p, ...)`, directly checking for null then `ShowWindow(hwnd, 0)`
- **Tray-module alignment (2026-09-02)**: `src/web_tray.py`'s console-window restyling (`_patch_console_window`) and tray restore (`_on_show`) switched to the same `WinDLL` + explicit `argtypes`/`restype` conventions (HWND/HMENU declared as `c_void_p`, fixing 64-bit handles being truncated by ctypes' default `c_int` — which could redirect window operations to a wrong address), with module-level `_KERNEL32`/`_USER32` singleton caching; the second parameter of `SetWindowPos` (insert-after window) is accordingly narrowed to `c_void_p | None`

**API routes**:

| Route | Method | Function |
| --- | --- | --- |
| `/api/login` | POST | Password login, returns Token |
| `/api/status` | GET | Get recording status (includes `actual_quality`) |
| `/health` | GET | Liveness endpoint (`{"status": "ok", "version"}`, always public / not gated by auth; for CI smoke / LB health checks) |
| `/api/rooms` | GET/POST | Live room list query / add |
| `/api/rooms/{url}` | PUT/DELETE | Edit / delete a live room |
| `/api/rooms/toggle` | POST | Enable / disable a live room |
| `/api/recording/toggle` | POST | Recording master switch (start/stop recording; stopping triggers runtime log archiving) |
| `/api/config` | GET/PUT | Read / modify config |
| `/api/logs/stream` | GET | SSE real-time log push |

**Frontend features** (`web/`):

- `index.html` - single-page application entry (dashboard / rooms / config three views)
- `app.js` - frontend logic (Token auth, API calls, SSE log stream, status rendering)
- `style.css` - stylesheet (light/dark theme, responsive layout, downgrade highlight)

**Recording table display**:

- Name / configured quality / actual quality / start time / recorded duration
- When actual quality differs from configured quality, shown in red (`.quality-down` style)

**Security mechanisms**:

- After a password change, all existing Tokens are automatically revoked, forcing re-login
- Outputs a security warning when listening on `0.0.0.0` without authentication enabled
- File download path validation (`_is_within` prevents directory traversal)
- Sensitive config items (Cookie / account password / web_password) are masked as `***` in API responses
- **Unauthenticated dangerous-config write protection**: when `web_auth_enable = false`, `PUT /api/config` is forbidden from overwriting dangerous keys in [Recorder] and [Push] (such as "run custom script after recording" `run_script`); only [Web] and whitelisted keys are allowed, blocking the unauthenticated RCE chain
- **INI injection protection**: config values and live room names filter `\n`/`\r` to prevent injecting arbitrary new lines / new sections into `config.ini` / `URL_config.ini`
- **Login brute-force rate limiting**: after `/api/login` fails consecutively up to a threshold (default 5 times / 5 minutes), it locks for a period (default 10 minutes), defending against online password brute-forcing
- **Push log masking**: `_mask_url()` in `msg_push.py` masks tokens / secrets in the query of webhook URLs in failure logs, preventing credential leakage via logs

### 14. Danmaku Collection Subsystem (`src/platforms/` + `src/collector.py` + related modules)

**Responsibility and architecture overview**: Provides live danmaku (bullet-chat) collection synchronized with video recording, sharded by half-hour — danmaku is written to SRT subtitle files and can also be viewed independently via "Danmaku Monitor" (monitor only, no disk write). The danmaku module was ported from `dart_simple_live`, originally located in `src/danmaku/`, then migrated to the `src/` root along with the directory flattening (base class `src/base.py`, collector `src/collector.py`, monitor `src/danmaku_monitor.py`, transport `src/ws_client.py`, cache `src/cookie_cache.py`, subtitles `src/srt_writer.py`, `src/proto/`, and per-platform implementations `src/platforms/`).

**Decoupled from stream parsing**: The danmaku subsystem and `src/spider.py` (video stream address parsing) are **two parallel abstractions**. `spider.py` is responsible for parsing video stream addresses; the danmaku client is decoupled via the registry/factory in `src/__init__.py`; `spider.py` does not import `src/platforms` at all. Only Bilibili danmaku lazily calls back `spider.invalidate_bili_buvid_cache()` when AUTH is rejected.

**Lifecycle wiring** (starts and stops together with recording):

- Each platform branch of `main.start_record` collects `record_danmaku_args` (reset to `None` each round);
- All 6 `check_subprocess(..., platform=platform, danmaku_args=record_danmaku_args)` calls are wired up;
- The factory `src/__init__.py:get_danmaku_collector(platform, danmaku_args, base_filename, segment_seconds, only_fans, room_name, write_srt)` picks the danmaku class by platform and constructs a `DanmakuCollector`; returns `None` when the platform is unsupported or `danmaku_args` is empty;
- `DanmakuCollector` calls `stop()` outside the `while process.poll() is None` loop; `DanmakuCollector.stop()` has `_stop_called` to prevent re-entry (idempotent).

**Platform registry** (`src/__init__.py:get_danmaku_class`, platform names consistent with `main.py` identifiers):

| Platform ID | Danmaku Class (`src/platforms/`) |
| --- | --- |
| Douyu Live | `DouyuDanmaku` |
| Bilibili Live | `BilibiliDanmaku` |
| Huya Live | `HuyaDanmaku` |
| Douyin Live | `DouyinDanmaku` |
| TwitchTV | `TwitchDanmaku` |

**Key files**:

- **Base class and data structures (`src/base.py`)**: `DanmakuBase(ABC)` defines the unified contract — class attribute `heartbeat_interval=45.0`; constructor `__init__(on_message, on_close, on_ready)` saves callbacks and sets `_stopped=False`; four abstract methods `async start(args)` / `async stop()` / `async heartbeat()` / `decode_message(data: bytes|str)`, helper `_emit(msg)` pushes up via `on_message`. `DanmakuMessageType(Enum)` (`CHAT/GIFT/ONLINE/SUPER_CHAT`); `DanmakuMessage` dataclass (`type/user_name/message/data/color/timestamp_ms`, `timestamp_ms` injected by the collector).
- **Danmaku collector (`src/collector.py`)**: `DanmakuCollector` wraps the async danmaku client into a threaded synchronous collector. Constructor params include `danmaku_cls / danmaku_args / base_filename / segment_seconds / only_fans / room_name / platform_name / write_srt` (`write_srt=False` means monitor-only, no disk write); `start()` anchors the SRT timeline and spawns a daemon thread `_run()` (new `asyncio.new_event_loop()`, instantiates the danmaku class, `run_until_complete(danmaku.start(args))`); `_on_message` reports all types to the monitor hub `hub.room_message(...)`, and only `CHAT` with non-empty username/content is written to SRT; `stop(timeout=8.0)` is idempotent, with a `message_count` property. Depends on `src.base` / `src.danmaku_monitor` / `src.srt_writer`.
- **Per-platform danmaku clients (`src/platforms/`)**: five `DanmakuBase` subclasses + two private signing/codec utilities.
| File | Class | WebSocket Endpoint | Key Protocol/Logic |
| --- | --- | --- | --- |
| `douyin.py` | `DouyinDanmaku` | `wss://webcast100-ws-web-lq.douyin.com/webcast/im/push/v2/` | gzip-decode `PushFrame.payload`→`Response` (protobuf); `danmaku_signature` (`_xbogus`) generates `signature`; when Cookie missing `await get_ttwid()`; `backup_url` changes `lq`→`lf` |
| `douyu.py` | `DouyuDanmaku` | `wss://danmuproxy.douyu.com:8506` | Little-endian binary frame + STT text protocol; `_dispatch` handles `chatmsg` (filters fans by `if==1`) and emits CHAT; heartbeat sends `mrkl` |
| `huya.py` | `HuyaDanmaku` | `wss://cdnws.api.huya.com` | Tars binary protocol (`_tars`); `_make_join_data()` writes `WSRegisterReq`; `cmdType==7`→`_decode_chat` (HYMessage) |
| `bilibili.py` | `BilibiliDanmaku` | `wss://{host}/sub` (iterates `host_list`) | 16-byte big-endian frame header; `protover=2` zlib / `=3` brotli decompression; `operation==8` AUTH_REPLY checks `code==0`, on failure/timeout via `_reject_auth()` + `spider.invalidate_bili_buvid_cache()`; `_auth_watchdog`(8s) fallback |
| `twitch.py` | `TwitchDanmaku` | `wss://irc-ws.chat.twitch.tv` | Pure IRC; anonymous `justinfan{random}` connection; `PING`→`PONG`, regex-parse PRIVMSG to emit CHAT; proxy via `handle_proxy_addr` or system proxy |
| `_tars.py` | (private) Tars codec | — | Huya uses a minimal Tars: `TarsInputStream` / `TarsOutputStream`, header byte high 4 bits tag, low 4 bits type |
| `_xbogus.py` | (private) X-Bogus signature | — | Used by Douyin danmaku: `generate_xbogus` (RC4 + custom base64), `danmaku_signature(room_id, unique_id)` |
- **Danmaku monitor hub (`src/danmaku_monitor.py`)**: `DanmakuMonitorHub` (process singleton, lazily created via `get_hub()`) aggregates danmaku events from each room — `room_started/room_connected/room_closed/room_stopped/room_message`; in-memory snapshot `snapshot(since=0)` for the Web API to consume, and writes a JSONL sidecar `logs/danmaku_monitor.jsonl` (5MB rotation). All methods swallow exceptions; includes a 10s×6-bucket rate window and ≤10 messages/sec sampling fold.
- **SRT subtitle writer (`src/srt_writer.py`)**: `SrtWriter` shards by `segment_seconds` to `{base}_{seg:03d}.srt` (single-file mode `{base}.srt`); the timeline is based on `time.monotonic()` and aligned with ffmpeg's `segment -reset_timestamps` PTS; `write()` holds a `threading.Lock` to write entries and flush.
- **WebSocket transport layer (`src/ws_client.py`)**: `WsClient` is the async WS client shared by all platform danmaku. `connect()` explicitly sets `proxy=None` (danmaku connects directly, not following the system proxy, avoiding the SOCKS-requires-python-socks error); `ping_interval=None` (each platform has its own heartbeat); `max_size=None`, `asyncio.Lock` serializes sending; supports `on_message/on_ready/on_heartbeat/on_close/on_reconnect` callbacks and a `max_reconnect` reconnect policy.
- **Visitor Cookie cache (`src/cookie_cache.py`)**: the only in-process "dynamically fetch visitor cookie by URL" cache, avoiding risk-control triggers from concurrent duplicate requests across multiple rooms. `fetch_cookies(url, proxy, *, ttl=30min, fetcher=None)` uses a lock-free fast path + singleflight deduplication (rewritten 2026-09-02: `threading.Lock` only guards the synchronous reads/writes of the cache dict and the in-flight registry — **never awaiting while holding the lock**; under the old RLock-across-await scheme, same-loop coroutines could all re-enter the lock, voiding mutual exclusion; same-loop waiters reuse a future, cross-loop delivery goes through `loop.call_soon_threadsafe` (futures are not thread-safe); if the fetching coroutine is cancelled it immediately delivers an empty result to waiters, and waiters carry a timeout fallback to prevent hanging forever); `get_cookie_str` / `invalidate` / `clear`.
- **Douyin danmaku protocol (`src/proto/`)**: `douyin.proto` (Proto3) defines `Response/Message/ChatMessage/GiftMessage/...`; `douyin_pb2.py` is protoc-generated (DO NOT EDIT), `douyin_pb2.pyi` is a pyright-based type stub. Douyin danmaku parsing chain: `PushFrame.payload` (gzip → `Response`) → `Message.payload` → `ChatMessage`.

### 15. Concurrency Scheduling Hub (`src/scheduler.py`)

**Responsibility**: Uniformly manages global network concurrency capacity, per-platform (host) isolated circuit breaker degradation, and supports both adaptive speed adjustment and fixed concurrency modes with runtime-resizable semaphores.

**Core Classes**:

- **`ResizableSemaphore`**: A runtime-resizable semaphore implementing the context manager protocol. Supports `set_value(n)` for runtime capacity adjustments — on increase, wakes the corresponding number of waiters; on decrease, only lowers the upper bound without forcibly reclaiming held slots. `__init__` / `set_value` allow a capacity of 0 (paused state). Eliminates the race condition of the old "destroy-and-recreate semaphore" approach.

- **`PlatformBreaker`**: A per-key (host) isolated circuit breaker implementing a `closed → open → half-open` three-state state machine. When the continuous failure sample ratio exceeds the threshold, it opens (skips probing and enters cooldown); after cooldown, a **single** probe is released; probe success restores closed, probe failure re-opens. Used to isolate and degrade single-platform jitter, preventing cascading global failures. **The probe carries a lease (`_PROBE_LEASE_SECONDS = 60s`, since 2026-08-27)**: if no sample is reported after the lease expires (not-live waiting rounds, `disable_record`, room-thread exit — paths that never trigger `record`), `allow()` re-grants the probe for self-healing — without the lease, the `_probing` flag never resets and the host stays permanently circuit-broken until process restart.

- **`ConcurrencyScheduler`**: The scheduling hub, integrating adaptive capacity, platform circuit breaker, and recording concurrency limit capabilities.
  - **Network concurrency capacity** = `max(configured lower bound, min(upper bound, ceil(active count / scale factor)))`; when the error rate is extremely high, capacity is gently reduced but never below the safe lower bound (default min=1 / max=128)
  - **Adaptive mode** (default, `Max simultaneous recordings (0=unlimited)` = 0): capacity dynamically scales with active task count, error feedback drives gentle backpressure
  - **Fixed concurrency mode** (`Max simultaneous recordings (0=unlimited)` ≠ 0): ignores the adaptive governor and error backpressure; network capacity is fixed to "Network thread count" (minimum 1 slot, hot-updates take effect immediately)
  - **Recording concurrency soft limit**: controls the simultaneous ffmpeg recording count via `recording_semaphore`, default 0 means unlimited
  - `adjust_loop` daemon recalculates capacity every 5 seconds, replacing the old one-way suppression `adjust_max_request`

**Key Functions**:

- `host_of(url)`: Extracts the hostname from the URL (cut at the first `/`, `?`, or `#`; lowercased, port kept) as the circuit breaker key; empty strings or parse errors uniformly map to `"unknown"` (unrelated broken URLs share one breaker key — a coarse-grained fallback)
- `allow(key)`: Pre-checks whether the specified host is circuit-broken; returns False when the caller should skip this round of probing; the half-open state carries a probe lease (see `PlatformBreaker`)
- `record_error(key)` / `record_success(key)`: Records success/failure samples per host, driving circuit breaker state transitions

**Wiring Points** (fixed locations, does not modify 50+ platform dispatch functions):

- `notify.record_error/record_success` adds a `key` parameter, delegates to `scheduler`
- `start_record` entry performs `scheduler.allow(record_host)` circuit breaker pre-check before platform dispatch
- The parse-success branch of `start_record` (non-empty `anchor_name`) reports `record_success(record_host)` — the half-open probe relies on this round's result to close the loop, so other rooms on the same host no longer starve while the probe room is in a long recording
- `check_subprocess` recording loop is governed by `recording_semaphore`
- `main()` initializes the scheduler in the first round; `semaphore` / `recording_semaphore` point to its attributes

**Thread Safety** (hardened 2026-08-27): the config fields (mode/configured limit/active count/error window) are read and written concurrently by the main thread and the `adjust_loop` daemon; `_compute_capacity()` snapshots all mutable inputs under a single lock, and `set_configured_limit()` / `set_dynamic_mode()` write inside the lock (idempotence check + write atomic). `Lock` is non-reentrant, so all setters call `recompute()` only after releasing the lock — no nested lock holding anywhere in the chain.

**Configuration Items**:

| Config Item | Description | Default |
| --- | --- | --- |
| Max simultaneous recordings (0=unlimited) | 0=unlimited (also serves as concurrency mode switch: 0=adaptive speed, non-zero=fixed concurrency) | 0 |
| Network thread count | In adaptive mode, one of the capacity lower bounds; in fixed mode, the fixed concurrency limit value | 3 |

**Tests**: `tests/test_scheduler.py` has 16 test cases covering semaphore resizing, circuit breaker state machine (including probe-lease timeout self-healing), adaptive capacity scaling/lower bound, fixed concurrency mode, per-key isolation, recording concurrency soft limit, etc.

## Key Classes and Functions

### Signing Algorithm (`src/ab_sign.py`)

Douyin's A-Bogus signing algorithm, including:

- SM3 hash
- RC4 encryption
- Complex parameter obfuscation

### Configuration File Management (`src/utils.py`)

```python
def read_config_value(file_path: Path, section: str, key: str) -> str | None
def update_config(file_path: Path, section: str, key: str, new_value: str) -> None
```

### Error Handling Decorator

```python
@trace_error_decorator
async def some_function():
    # 自动捕获并记录异常（支持同步和异步函数）
    pass
```

**Implementation characteristics**:

- Detects function type via `asyncio.iscoroutinefunction()`
- Async functions use `async wrapper` to correctly `await` and catch exceptions
- Uniformly returns `{}` empty dict, compatible with the caller's `.get()` usage
- `execjs.ProgramError` handled separately (Node.js environment issue)

### Dynamic Concurrency Adjustment

`main.py` implements an error-rate-based dynamic concurrency adjustment mechanism to avoid being rate-limited by platforms.

### Concurrency Scheduler (`src/scheduler.py`)

```python
# Runtime-resizable semaphore
class ResizableSemaphore:
    def set_value(self, n: int) -> None: ...
    def acquire(self) -> None: ...
    def release(self) -> None: ...

# Per-platform circuit breaker
class PlatformBreaker:
    def allow(self) -> bool: ...
    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...

# Scheduling hub
class ConcurrencyScheduler:
    network_semaphore: ResizableSemaphore
    recording_semaphore: ResizableSemaphore
    def set_dynamic_mode(self, enabled: bool) -> None: ...
    def set_recording_limit(self, limit: int) -> None: ...
    def allow(self, key: str) -> bool: ...
    def record_error(self, key: str) -> None: ...
    def record_success(self, key: str) -> None: ...

# Helper function
def host_of(url: str) -> str: ...
```

## Dependencies

### Python Dependencies (`requirements.txt`, kept consistent with `pyproject.toml [project.dependencies]`)

| Package | Version Requirement | Purpose |
| --- | --- | --- |
| requests | >=2.34.2 | Synchronous HTTP requests (now only the ffmpeg / node install-download scripts; platform parsing uses the httpx async surface) |
| urllib3 | >=2.7.0 | Transport layer (under requests; declared explicitly to prevent resolution fallback into the CVE-2026-44431 range) |
| httpx[http2] | >=0.28.1 | Async HTTP client (with HTTP/2; `src/async_http.py` fetches stream URLs concurrently) |
| h2 | >=4.4.1 | Runtime dependency of httpx `http2=True` (`import h2` inside `Client.__init__`) |
| socksio | >=1.0.0 | Runtime dependency of httpx SOCKS proxy (`socks5`/`socks5h`, `import socksio` in the transport layer) |
| loguru | >=0.7.3 | Structured logging (wrapped by `src/logger.py`) |
| pycryptodome | >=3.23.0 | Cryptographic algorithms (SM3, RC4, AES) |
| distro | >=1.9.0 | Linux distribution detection |
| tqdm | >=4.69.0 | Download progress bar |
| exejs | >=1.0.1 | JavaScript execution engine (active-maintained successor to PyExecJS, preferred) |
| PyExecJS | >=1.5.1 | JS execution engine fallback compatibility (used when exejs is not installed) |
| customtkinter | >=6.0.0 | Modern GUI framework |
| pystray | >=0.19.5 | System tray (GUI / Web tray mode) |
| Pillow | >=12.3.0 | Image processing (tray icon generation) |
| fastapi | >=0.140.0 | Web management panel backend framework |
| starlette | >=1.3.1 | ASGI toolkit (transitive dependency of fastapi, explicitly declared because `src/web_api.py` imports it directly; lower bound 0.49.1 → 1.0.1 → 1.3.1, see the CVE/PYSEC notes) |
| uvicorn[standard] | >=0.51.0 | ASGI server |
| python-multipart | >=0.0.32 | Form/file upload parsing |
| pydantic | >=2.13.4 | Request model validation |
| websockets | >=14.0 | Danmaku WebSocket client (`src/ws_client.py`; `additional_headers` is a 14.0+ API) |
| protobuf | >=6.33.5,<8 | Douyin danmaku protocol decoding (`src/proto/douyin_pb2.py`; the `<8` cap is a gencode compatibility guard) |
| brotli | >=1.2.0 | Bilibili danmaku decompression (protover=3) |
| PyYAML | >=6.0.3 | YAML translation catalog support (`i18n/zh_TW.yaml`) |

> Note 1: [Historical note] this section used to record that "Weverse platform authentication is implemented by
> `src/weverse_auth.py` calling the API directly via requests, and no longer depends on the pip `weverse` package".
> That module (together with `tests/test_weverse_auth.py`) was removed entirely on 2026-09-23; the conclusion is kept
> for reference only: the pip `weverse` package pulls in the deprecated pycrypto==2.6.1 (uncompilable on Python 3.10+),
> so it must **never** be added to the dependency list.
>
> Note 2: Executable packaging requires PyInstaller, an optional build-time dependency: `pip install .[build]`
>
> (corresponding to `pyproject.toml`'s `[project.optional-dependencies] build`).

### External Dependencies

| Dependency | Purpose | Installation |
| --- | --- | --- |
| FFmpeg | Video recording and transcoding | Built-in on Windows (`ffmpeg/`), manual install on Linux/macOS; installed via apt inside Docker |
| Node.js | Run JavaScript signing algorithms | Auto-installed on Windows (`node/`), needs a package manager on Linux; Node 24 installed via apt inside Docker |

### Module Dependency Graph

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
├── src/scheduler.py (concurrency scheduling hub)
│   ├── ResizableSemaphore (runtime-resizable semaphore)
│   ├── PlatformBreaker (per-platform circuit breaker)
│   └── ConcurrencyScheduler (scheduling hub)
├── src/notify.py (record_error/record_success delegates to scheduler)
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

## Configuration File Reference

### Main Configuration File (`config/config.ini`)

#### [Recording Settings] section

| Config Item | Description | Default |
| --- | --- | --- |
| language | Interface language (blank follows system language; values support zh_cn/zh_CN/en/en_US/en_GB/zh_TW etc., normalized via resolve_language; falls back to en_US if unrecognized or the language file is missing; Web/GUI can switch instantly and write back to this key) | (empty) |
| 是否跳过代理检测(是/否) | Whether to skip proxy detection | Yes |
| 是否启用https录制 | Combined switch (merges the former "whether to force https recording" and "whether to disable SSL certificate verification (yes/no)"): enabled = https pull + skip cert verification; disabled = http pull + default cert verification (https-only overseas platforms stay as-is) | No |
| 禁用SSL证书验证的平台(逗号分隔) | Platform-level cert-verification exemption list: **only takes effect when certificate verification is required** (i.e. http recording mode, where TLS cert verification is on by default since FFmpeg 9.0) — platforms in the list skip cert verification (for platforms with abnormal certs like Huya/Bilibili); in https recording mode cert verification is already skipped globally, making the list redundant. At startup, missing required platforms are auto-appended (Huya Live, Bilibili Live — only appended, user-entered items are never removed) | 虎牙直播,B站直播 |
| 是否启用日志文件(是/否) | Whether to write logs to a file | Yes |
| 直播保存路径(不填则默认) | Recording file save path | (empty, defaults to current directory) |
| 保存文件夹是否以作者区分 | Whether to categorize by anchor name | Yes |
| 是否自动更新主播名(是/否) | Auto-sync on anchor rename: updates the anchor-name field in URL_config.ini, and renames the recording folder and its recording files (including danmaku/subtitle and other same-prefix artifacts) previously named with the old anchor name; triggered only when that room is not currently recording, so in-progress recordings are unaffected; if disabled, the manually entered name is kept unchanged | Yes |
| 视频保存格式ts | mkv | flv | mp4 | mp3 audio | m4a audio | ts/mkv/flv/mp4/mp3/m4a | ts |
| 原画 | Ultra HD | HD | SD | Smooth | Default quality | Original |
| 是否使用代理ip(是/否) | Whether to enable proxy | No |
| 代理地址 | Proxy server address; supports protocol prefixes (`http://` / `https://` / `socks://` etc.); a bare address (`ip:port`) automatically gets the `http://` prefix prepended | (empty) |
| 同一时间访问网络的线程数 | Concurrency (number of threads accessing the network at the same time) | 3 |
| 循环时间(秒) | Live status check interval | 120 |
| 分段录制是否开启 | Whether to segment recordings | Yes |
| 是否启用HLS采集(是/否) | Whether to prefer HLS (m3u8) source collection; falls back to FLV when disabled or the source is unavailable | Yes |
| HLS采集排除平台(逗号分隔) | HLS capture exclusion list: listed platforms **ignore the "whether to enable HLS capture" setting and always use FLV capture** (equivalent to disabling HLS capture for that platform only — the whole HLS candidate group is removed with no fallback, and the h265-FLV → HLS switch is disabled as well); platforms outside the list are unaffected and keep HLS priority. Platform names must match exactly (e.g. 斗鱼直播); both Chinese and English commas are supported; hot-reloaded every main-loop iteration | (empty, excludes nothing) |
| 视频分段时间(秒) | Segment duration | 1800 |
| 使用代理录制的平台(逗号分隔) | Matches live room URLs by domain substring; a hit routes through the proxy (requires "whether to use proxy ip" enabled first) | tiktok, sooplive, pandalive, winktv, flextv, popkontv, twitch, liveme, showroom, chzzk, shopee, shp, youtu, faceit |
| 额外使用代理录制的平台 | Append additional proxy-routed platforms (comma-separated) beyond the table above; the proxy address falls back to a value other than "proxy address" | (empty) |
| 是否录制弹幕(是/否) | Whether to write danmaku to SRT subtitle files | No |
| 是否弹幕监控(是/否) | Independent danmaku monitor switch: the GUI "Danmaku Monitor" page / Web "Danmaku Monitor" tab shows the danmaku stream and stats in real time; decoupled from "whether to record danmaku" — monitor-only does not write SRT; when both are on, the same danmaku connection is reused | No |
| 弹幕录制平台(逗号分隔) | Platforms that currently support danmaku recording (names must match exactly): Douyu Live, Bilibili Live, Huya Live, Douyin Live, TwitchTV (see the danmaku registry in `src/__init__.py`) | 斗鱼直播,B站直播,虎牙直播,抖音直播,TwitchTV |
| 弹幕分片时长(秒) | Danmaku SRT shard duration (requires segmented recording enabled) | 1800 |

#### [Push Configuration] section

| Config Item | Description | Default |
| --- | --- | --- |
| 直播状态推送渠道 | Optional channels: WeChat | DingTalk | Telegram | Email | Bark | NTFY | PushPlus (multi-select) | (empty) |
| 钉钉推送接口链接 | DingTalk Webhook | (empty) |
| 微信推送接口链接 | Server酱 URL | (empty) |
| bark推送接口链接 | Bark API | (empty) |
| bark推送中断级别 | Bark interruption level, options: critical (important reminder) / active (default) / timeSensitive (time-sensitive) / passive (silent) | active |
| tgapi令牌 | Telegram Bot Token | (empty) |
| tg聊天id | Chat ID | (empty) |
| smtp邮件服务器 | SMTP server | (empty) |
| 是否使用SMTP服务SSL加密(是/否) | Whether to enable SMTP SSL encryption (blank is treated as "Yes"); when enabled the port is typically 465 | Yes |
| ntfy推送地址 | NTFY service address | (empty) |
| pushplus推送token | PushPlus Token | (empty) |
| 只推送通知不录制(是/否) | Whether to notify only without recording | No |

#### [Cookie] section

Cookie configuration for each platform (required for recording some platforms). Special keys:

| Config Item | Description | Default |
| --- | --- | --- |
| 抖音cookie | Required for recording Douyin; must at least contain ttwid, blank triggers risk control | (empty) |
| ttwid | Can pin a Douyin ttwid (enter `ttwid=xxx` or just the value); blank auto-fetches, but a filled value takes priority over auto-fetch (`src/ttwid.py`) | (empty) |

#### [Authorization] section

Token configuration for special platforms

#### [Account Password] section

Account/password configuration for some platforms

#### [Web] section

Web management panel configuration (specific to `web.py` mode)

| Config Item | Description | Default |
| --- | --- | --- |
| web_host | Listen address (set to 0.0.0.0 inside Docker) | 127.0.0.1 |
| web_port | Listen port | 8000 |
| web_auth_enable | Whether to enable password authentication. When disabled, the API forbids overwriting dangerous [Recorder]/[Push] config (such as custom scripts), but still allows modifying [Web] settings | false |
| web_password | Login password (required when auth is enabled, stored hashed with PBKDF2-HMAC-SHA256) | (empty) |
| web_token_expiry | Token validity period (seconds) | 86400 |
| web_show_console | Whether to show the console window (false = hidden background run) | true |
| web_minimize_to_tray | Minimize console to system tray (Windows only; close button disabled, exit via tray icon "Exit Program") | true |
| web_trusted_proxy | Trusted proxy list for reverse-proxy scenarios (comma-separated direct IPs, e.g. 127.0.0.1): only direct peers in the list are trusted for `X-Forwarded-For` real-client-IP resolution (prevents forged headers from bypassing login rate limiting); blank = always use the direct peer address. Do not fill when unauthenticated and exposed to the public internet | (empty) |
| web_allowed_hosts | Extra registered domain allowlist (comma-separated; supports `*.example.com` suffix matching) on top of the hosts the server allows automatically. See `src/web_config.py::is_host_allowed` for the Host rule: **IP literals** and **dot-less single-label names** pass implicitly (DNS rebinding needs at least a multi-label registered domain), while **multi-label domains** must be registered explicitly or they are rejected with 400; `web_host` bound to `0.0.0.0`/`::` is not added to the allowlist (a wildcard bind address is not a valid Host value). So this only needs filling when `web_host` is a wildcard bind and the panel is reached via a **domain name** — not for direct-IP access or the default `127.0.0.1` setup | (empty) |

### Live Room Configuration File (`config/URL_config.ini`)

**Format**:

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

**Automatic anchor-name update**: After enabling `[Recording Settings] 是否自动更新主播名(是/否)` in `config.ini` (enabled by default), whenever a polling round resolves that a platform's latest anchor name differs from the currently used name, it automatically:

1. Renames the folder previously named with the old anchor name in the save directory (`{save path}/{platform}/{old anchor name}`, merging item-by-item if the target already exists);
2. Synchronously renames all recording files prefixed with the old anchor name inside the folder (including date/title subdirs) (`{old anchor name}_*`) and same-prefix artifacts like danmaku SRT/timed subtitles, and also renames title directories ending with `_{old anchor name}` (`{title}_{old anchor name}`);
3. Updates the anchor-name field of the corresponding line in `URL_config.ini` (exact URL match of that line, preserving the quality segment, the `#` comment prefix and line-ending style, normalizing full-width colons to half-width, idempotent).

**Triggering and safety**:

- The trigger point is after each round's live-data parsing and before recording startup; at this moment the room's thread is necessarily not recording (during recording it is blocked inside the ffmpeg daemon), so the rename will not touch files being written, and in-progress recordings are unaffected.
- Skip conditions: `platform == "自定义录制直播"` (its anchor name contains a per-round random UUID and should not repeatedly trigger renaming), or the platform returns an invalid name such as "blank nickname".
- Sync order: **filesystem first, then config file**; the round's used name is switched only when both succeed. On any failure (e.g. config file locked by an editor, directory rename failed) the old name is kept and retried on the next polling round (completed directory renames are idempotent and will not repeat).
- An individual file occupied by a background transcode/player that fails to rename only warns and skips, without blocking the whole; other files are processed normally and backfilled next round; meanwhile stale recording-status entries (under `recording` / `recording_time_list`) of the old name are cleaned up to avoid the monitor page hanging onto the old name long-term.
- Config writes hold `file_update_lock`, mutually exclusive with the recording thread's `update_file` / Web API writes, avoiding half-written states.

Disabling this option keeps the manually entered name unchanged.

## How to Run

### Method 1: Run from Source

#### Prerequisites

- Python 3.14+
- FFmpeg
- Node.js

#### Install Dependencies

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

#### CLI Mode

```bash
python main.py
```

#### GUI Mode

```bash
python gui.py
```

#### Web Management Panel Mode

```bash
python web.py
# 默认监听 http://localhost:8000
```

### Method 2: Run with Docker

#### Dockerfile Multi-stage Build Notes (base image `python:3.14-slim-bookworm`)

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

**`.dockerignore` key points** (after the 2026-08-28 sync):

- Exclude platform binaries (`ffmpeg/`, `node/`, installed via apt in the container), `config/*.ini` (mounted at runtime), `typings/`, `build_exe.py`, the root `index.html` (a standalone M3U8 player page; the panel uses `web/`), and other desktop/build-specific files;
  [2026-09-21 revision: this line previously listed `gui_legacy.py`, deleted in v4.1.0-dev / 2026-09-10 and absent from `.dockerignore` — the 4th stale MIN-15 reference, corrected in place]
- **Keep `i18n/**/*.mo` compiled translation files and `i18n/*.json`, `i18n/*.yaml` multilingual catalogs** — they are required at runtime (gettext / JSON / YAML, the three translation catalog formats) and the Dockerfile will not recompile/regenerate them; only the `.po` sources and compile scripts are excluded;
- Exclude local tool / AI-assistant generated directories (`.mimosa/`, `.qoder/`, `.agents/`, `.pnpm-store/`, `.dsh-validation/`, `.ego-browser-test/`, `.plugin-src/`, `pytest-cache-files-*/`, etc., maintained in sync with `.gitignore`);
- Exclude content the image does not consume at runtime: `uv.lock` (the image uses pip + requirements.txt), `scripts/` (maintenance scripts, zero references from the runtime chain), `tests/`, docs such as `AGENTS.md` / `README_EN.md` / `CODE_WIKI_EN.md`, and `.coveragerc-concurrency` (CI-specific).

#### Using Docker Compose (recommended)

The `docker-compose.yaml` at the repo root defines three services (sharing one image, reusing config via YAML anchors):

| Service | Entry | Start Command | Port |
| --- | --- | --- | --- |
| `recorder` (default) | `python main.py` | `docker compose up -d` | None (pure CLI) |
| `web` (profile) | `python web.py` | `docker compose --profile web up -d` | `127.0.0.1:8000:8000` |
| `gui` (profile) | `python gui.py` | `docker compose --profile gui up -d` | None (requires X11) |

Shared mount volumes: `./config`, `./downloads`, `./logs`, `./backup_config`.

> ⚠️ **Web mode required reading**: `web.py` listens on `127.0.0.1:8000` by default; inside the container you must set `web_host = 0.0.0.0` in the `[Web]` section of `config/config.ini` for the host port mapping to be reachable;
>
> at the same time it is strongly recommended to enable `web_auth_enable = true` and configure a password.

## Packaging and Release

This project provides one-click executable packaging (`build_exe.py`) and cross-platform automated build/release (`GitHub Actions`), unifying the **CLI / GUI / Web three entry points** into distributable release directories.

### 1. Packaging Script `build_exe.py`

PyInstaller `onedir` mode + `contents_directory='_internal'`, dynamically generates the `.spec` file and then calls PyInstaller to build **three entries sharing dependencies**:

| Artifact (beside the exe) | Entry | Mode |
| --- | --- | --- |
| `DouyinLiveRecorder(.exe)` | `main.py` | Console (CLI recording core) |
| `DouyinLiveRecorder-GUI(.exe)` | `gui.py` | No console window (GUI) |
| `DouyinLiveRecorder-Web(.exe)` | `web.py` | Console (Web management panel, listens on `0.0.0.0:8000`) |

The three entries share one `COLLECT`; after dependency de-duplication the size is about 1/3 of independent packaging.

**Usage**:

```bash
python build_exe.py              # build and produce the zip artifact
python build_exe.py --smoke      # additionally run smoke tests after building (recommended for CI)
python build_exe.py --no-zip     # build only, no zip
python build_exe.py --no-runtime # skip bundling ffmpeg/node (downloaded at runtime instead, smaller artifact)
python build_exe.py --dual       # emit both zips: lite (no runtime) and full (ffmpeg+node bundled)
```

**Data files and hidden imports**:

- `datas`: `src/javascript` (JS signing scripts), `i18n` (translations), `web` (frontend static assets), all located via `__file__`, automatically collected into `_internal/` by PyInstaller; `collect_data_files('customtkinter')` (theme JSON).
- `config/` does not go into `_internal`; it is copied beside the exe by `copy_external_binaries()` (see the directory convention).
- `hiddenimports`: `i18n`, `src.async_http` (dynamically imported by main.py via `__import__`), `h2` (httpx[http2] lazy load); `a_web` additionally `collect_submodules('uvicorn')` (protocol modules imported by string).
- `excludes`: CLI excludes GUI/Web libraries (tkinter/customtkinter/pystray/PIL/fastapi/uvicorn/starlette); GUI excludes Web libraries; Web excludes GUI libraries; all three entries additionally exclude `brotlicffi` (fixes the post-packaging error of the `brotlicffi` module missing the `error` attribute; httpx auto-falls back when no brotli is present).

**Version number**: Parsed from the `version` field of `pyproject.toml` (single source of truth), used for zip naming; falls back to `0.0.0` on parse failure. `main.py` also reads the version dynamically from `pyproject.toml` at runtime (prefers `importlib.metadata`, falls back to parsing the file directly).

### 2. Directory Structure Convention (packaging artifact)

After adopting `onedir + contents_directory='_internal'`, PyInstaller collects dependencies and `__file__`-located resources into `_internal/` beside the exe; runtime resources located via `sys.argv[0]`/`sys.executable` are copied beside the exe by the packaging script after `COLLECT`. Final artifact structure:

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

**Key conventions (mandatory)**:

- `node/`, `ffmpeg/`, `config/` stay **beside the exe** (not in `_internal/`).
- `src/` and all Python dependency packages are uniformly collected into `_internal/`.
- Writable runtime directories `logs/`, `downloads/` (when not specified via `直播保存路径(不填则默认)` in `config.ini`), `backup_config/` are all created by default in the **exe's sibling directory**.

### 3. Path Convergence Mechanism `_app_root()`

The project has a "dual-track path" problem: `main.py`/`src/ffmpeg_install.py`/`src/__init__.py` etc. locate runtime resources via `sys.argv[0]`/`sys.executable`; `src/logger.py`, `i18n.py`, `src/web_api.py` etc. locate packaged resources via `__file__`. After freezing, the former points to the exe's sibling directory (release root), the latter to `_internal/`.

To unify convergence, `src/logger._app_root()` was added (same name as the inline function in `main.py`):

```python
def _app_root() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.realpath(sys.executable))  # = exe 同级
    return os.path.split(os.path.realpath(sys.argv[0]))[0]
```

- `main.py`'s `script_path`, `src/__init__.py`, `src/node_install.py`, `src/ffmpeg_install.py`'s `execute_dir` all converge to the exe's sibling directory, so `config/ffmpeg/node` are located correctly.
- `src/logger.py`'s `script_path` is changed to `_app_root()`, so `logs/`, `backup_config/` land beside the exe.
- `gui.py` adds `self.app_root`: when frozen, if `script_dir` is `_internal` it falls back one level to the release root, from which config/downloads are located; the CLI subprocess is launched via the sibling `DouyinLiveRecorder.exe` (see below).
- `i18n.py` supports dual-path detection of `_internal/i18n` and `i18n/`.

### 4. Frozen Build Adaptation Notes

- **GUI subprocess launch (critical fix)**: After `gui.py` is frozen, `sys.executable` points to the GUI itself; the original `[sys.executable, main.py]` would recursively launch the GUI infinitely. Changed to directly call the sibling `DouyinLiveRecorder.exe` when frozen; source-run stays as before.
- **GUI subprocess pythonw compatibility (2026-08-09)**: In source mode, if the GUI is started via `pythonw.exe`, `sys.executable` points to pythonw (GUI subsystem, no console); the original `[sys.executable, main.py]` would also run the recording core under pythonw — `CREATE_NEW_CONSOLE` is ineffective on it, `AttachConsole(pid)` is guaranteed to fail, CTRL_BREAK can never be delivered, and stopping can only hard-kill (orphaning ffmpeg). Now when the interpreter basename starts with `pythonw`, it switches to launching the recording core with the sibling `python.exe` (console subsystem); the packaged version (CLI exe `console=True`) is unaffected.
- **GUI graceful stop on recording (2026-08-09)**: When `_send_ctrl_break_to_child` fails, instead of only `proc.terminate()` (`TerminateProcess` hard-kill, orphaning ffmpeg and `wait()` succeeding immediately bypassing whole-tree cleanup), it now uses `taskkill /F /T /PID` for whole-tree termination; logs distinguish "graceful exit" from "hard-kill path" by path, no longer falsely reporting ffmpeg as cleaned up.
- **Chinese UTF-8 encoding (critical fix)**: After freezing, the subprocess stdout is a pipe and Python falls back to GBK for output, while the GUI reads the pipe as UTF-8 → Chinese mojibake (e.g. `自动获取 Cookie ttwid 成功` becomes garbled). Added `_fix_encoding()` at the top of `main.py`/`gui.py`/`web.py`: on Windows `sys.stdout/stderr.reconfigure(encoding='utf-8', errors='replace')` + `ctypes.windll.kernel32.SetConsoleOutputCP(65001)/SetConsoleCP(65001)`; on non-Windows only reconfigure. stream gets `None`/`hasattr` guards (stdout of a windowed exe may be `None`). `web.py`'s original `reconfigure(errors='replace')` is upgraded to also set `encoding='utf-8'`.

### 5. Smoke Tests

`build_exe.py --smoke` automatically runs three verifications after packaging (CI recommended to enable):

- **CLI**: Launch for a few seconds, confirm it enters the monitoring loop and outputs no `Traceback`/`ImportError`/`ModuleNotFoundError`.
- **Web**: HTTP liveness probe `http://127.0.0.1:8000/`, returns 200 means the panel is usable; also verifies the built-in ffmpeg is hit (no download triggered).
- **GUI**: Launch for 8 seconds to confirm the process survives without crashing (auto-skipped when no display environment `DISPLAY` is set).

Before smoke testing, a commented URL is written to the exe-level `config/URL_config.ini` to avoid the CLI blocking on `input()` because the URL list is empty.

### 6. GitHub Actions CI Static Verification (`ci.yml`)

Workflow file: `.github/workflows/ci.yml`, runs on push to main / PR, ensuring code style, type safety, and functional correctness pass verification before merge (structure after the 2026-08-28 optimization).

**Unified strategy**:

- The `setup` job centrally declares **shared constants** (Python version matrix / Node version / pinned black / isort / mypy versions) and performs path filtering; constants are exported to job outputs for reference by all jobs and `strategy.matrix` (matrix cannot reference the env context), serving as the workflow's single source of truth;
- **actions major versions unified at v7** (`checkout` / `setup-python` / `setup-node` / `upload-artifact`), fully consistent with build-release.yml;
- **Network-install retries uniformly go through the `.github/actions/retry` composite action** (linear backoff ×3; `command` / `label` / `attempts` / `backoff` parameterizable) — 9 pip / apt call sites; the retry strategy is maintained in action.yml alone, and re-inlining retry loops inside jobs is forbidden;
- **apt hardening flags** (aligned with the Linux build of build-release.yml): `DEBIAN_FRONTEND=noninteractive` + `Acquire::Retries=3` + `--no-install-recommends`;
- Every job sets an explicit `timeout-minutes`; a new push to the same branch/PR cancels stale runs via `cancel-in-progress: true` (fast feedback, deliberately different from the non-cancellable release pipeline);
- pip caching uniformly keyed by `hash(requirements.txt + pyproject.toml)` (no lock file participates in installation).

**Path filtering**: the `setup` job uses `dorny/paths-filter@v4` to detect changed file categories; a match runs all downstream jobs. Trigger list: Python source (`src/**`, root entry points `main.py`/`gui.py`/`web.py`/`i18n.py`/`msg_push.py`/`build_exe.py`), `tests/**`, `scripts/**`, dependency manifests (`requirements.txt` / `pyproject.toml` / `.coveragerc-concurrency`), **`i18n/**`**, **`web/**`**, **`Dockerfile` / `docker-compose.yaml`**, and the workflow and composite actions (**`.github/workflows/**` / `.github/actions/**`**). Only **pure documentation (`*.md`) changes do not trigger**. **`i18n/**` is a trigger condition** — translation-only changes also run the static job's compile_po --check sync gate; **`web/**` is likewise a trigger** (added 2026-09-20) — `web/app.js`'s `parseConfigBool + CONFIG_*_TOKENS` and `src/config_bool.py` form a cross-language boolean-parsing invariant (AGENTS.md "Unified parsing of boolean config values"), so a change on either side must run the `tests/frontend/test_quality_ui.mjs` regression lock via the test job (the old "pure frontend web/ does not trigger" claim has been falsified; see the matching changelog entry).

**Parallel jobs** (all gated by `needs: setup`):

| Job | Environment | Content |
| --- | --- | --- |
| `static` | py3.14 | `black --check .` + `isort --check .` + `python scripts/check_version.py` (version single-source-of-truth check) + `python scripts/compile_po.py --check` (i18n po/mo sync check, zero side effects) + `python scripts/check_annotations.py` (annotation conventions: no docstrings / density floor / module headers, zero side effects) |
| `typecheck` | py3.14 | Install requirements + pinned mypy, then run `mypy` (scope comes entirely from `pyproject.toml [tool.mypy].files`; the minimum supported version is still used so conclusions hold for the oldest interpreter) |
| `test` | py3.14 | `pytest --cov=src --cov-report=term-missing` (global `fail_under=50` gate, `fail-fast: false`); on the minimum version additionally runs the `scripts/check_coverage.py` per-module gate + coverage.xml upload + optional Codecov |
| `concurrency-test` | py3.14 | Concurrency-specific: under `COVERAGE_RCFILE=.coveragerc-concurrency` runs `test_concurrency_rate_limit.py` + `test_concurrency.py` + `test_async_http_lock.py` (dedicated config sets no global threshold) |
| `integration-verify` | py3.14 + Node 24 | apt install ffmpeg; verify the ffmpeg/node binaries are discoverable, and call `check_ffmpeg_installed()` / `check_nodejs_installed()` to verify detection logic |
| `build-verify` | py3.14 packaging interpreter | `build_exe.py --smoke --no-runtime --no-zip` (lite packaging + CLI/Web/GUI three-entry smoke, on Linux via `xvfb-run -a`); release-grade full packaging is left to build-release.yml |
| `ci-summary` | — | The only required check: aggregates the results of all upstream jobs (skipped counts as passed — path-filter skips never leave branch protection permanently pending) |

### 7. GitHub Actions Automated Build and Release (`build-release.yml`)

Workflow file: `.github/workflows/build-release.yml` (job name `Build (${{ matrix.os }})`).

**Trigger methods**:

- Manual trigger (`workflow_dispatch`, optional `create_release` input): by default only builds and uploads artifacts; checking the input also creates a Release.
- Push a `v*` tag (e.g. `v4.0.9.1`): build + automatically create a GitHub Release with artifacts attached (`permissions: contents: write`, granted only to the build / release jobs).

**Build matrix**: `windows-latest` / `ubuntu-latest` / `macos-latest`, Python 3.14 (`fail-fast: false`; same value as ci.yml's build-verify packaging interpreter, guaranteeing "the packaging environment validated by CI == the one actually released").

**Steps**:

1. `prepare` job: extracts the version from pyproject.toml via tomllib and validates tag consistency (a mistagged release fails immediately); runs `check_version.py` to confirm all consumers read the version dynamically.
2. `release-create` job: on the release path **pre-creates** the Release record (a singleton job eliminating the race where multi-platform build jobs concurrently create the same Release; no files attached); on the manual release path it also creates the lightweight tag (a Release must be attached to a tag).
3. build job (matrix): each platform installs ffmpeg via its system package manager for smoke testing — Windows `choco`, Linux `apt` (plus `xvfb`; GUI smoke needs a virtual display), macOS `brew` (`brew trust aws/tap` as a separate idempotent step, `HOMEBREW_*` variables exported inline in the command); **all network-install commands are wrapped by the `.github/actions/retry` composite action** (linear backoff ×3; system package managers back off 15s, pip 10s); dependencies via `pip install -r requirements.txt` + `pip install ".[build]"`.
4. `python build_exe.py --smoke --dual` (on Linux wrapped with `xvfb-run -a`): PyInstaller runs only once. Before any packaging, stale `DouyinLiveRecorder-v*.zip` leftovers under `dist/` are pruned (otherwise `path: dist/*.zip` sweeps last run's artifacts into this run's attachment set). It then produces the **lite** zip (no ffmpeg/node, auto-downloaded at runtime) → downloads the runtimes → produces the **full** zip (built-in runtime, ~300MB). The two `make_zip` **return paths** must differ and both must exist on disk, otherwise the build exits with `SystemExit` right there. Smoke runs after **both** zips (MID-2254) against the release directory that already holds the runtimes — not against the lite build.
5. Artifact publishing: on the release path (tag / manual with create_release) the build job uploads zips **directly to the Release** via `softprops/action-gh-release@v3` (explicit `tag_name` pointing at the same Release as release-create; GitHub supports concurrent uploads of distinct assets to the same Release); the build-only path uses `upload-artifact@v7` (`compression-level: 0` to skip re-compression, retained 30 days for manual retrieval).
6. `release` job (release path): `gh release download` pulls the published assets back to verify completeness (3 platforms × lite/full = 6 zips; any shortfall fails instead of publishing an incomplete Release), generates `SHA256SUMS.txt`, and finally via `softprops/action-gh-release@v3` attaches the checksums and writes the release notes (`generate_release_notes: true`).

**Artifact naming**: `DouyinLiveRecorder-v{version}-{os}-{arch}-{lite|full}.zip` (e.g. `DouyinLiveRecorder-v4.0.9.1-windows-amd64-full.zip`).

### 8. Local Packaging Steps

```bash
pip install pyinstaller          # install the packager
python build_exe.py --smoke      # build + smoke test
python build_exe.py --smoke --dual  # same shape as CI: lite + full artifacts
# output: dist/DouyinLiveRecorder/ release directory + dist/DouyinLiveRecorder-vX.Y.Z-*.zip
```

Note: This repo is a local copy; the workflows only run after being pushed to the GitHub repository. The lite artifact (and CI Linux/macOS artifacts) does not include `ffmpeg`/`node`; they are auto-downloaded on first run.

## Design Patterns

### 1. Adapter Pattern

Each live platform's API is uniformly adapted to the same calling interface, implemented in `spider.py` and `stream.py`.

### 2. Decorator Pattern

`trace_error_decorator` is used for error tracing, implemented in `utils.py`.

### 3. Strategy Pattern

Different message push channels (DingTalk, WeChat, Telegram, etc.) are implemented as independent functions, selected at runtime based on configuration.

### 4. Singleton Pattern

Log configuration is implemented as a singleton via module import side effects, in `src/logger.py`.

### 5. Template Method Pattern

Each platform's recording flow follows the same template: detect → fetch stream → record → push.

### 6. Factory + Registry Pattern

The danmaku subsystem uses the `get_danmaku_class(platform)` registry in `src/__init__.py` (Chinese platform name → danmaku class) together with the `get_danmaku_collector(...)` factory to uniformly create each platform's collector; `main.py` obtains the collector by platform identifier without knowing the concrete platform implementation. To add a new danmaku platform you only need to register it in the registry and implement the four abstract methods `start/stop/heartbeat/decode_message` of `DanmakuBase`, with zero intrusion to callers.

## Troubleshooting

### Issue 1: Prompt says FFmpeg is missing

**Solution**:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
Built-in, no installation needed
```

### Issue 2: Prompt says Node.js is missing

**Solution**:

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Windows
The program auto-downloads and installs it
```

### Issue 3: Douyin risk control prevents data fetching

**Risk-control characteristics (measured)**:

- The risk-control signal is **HTTP 200 + empty response body**, not 4xx. When troubleshooting a parse failure, first check `len(response.text)`; if it is 0 it basically means UA/Cookie was rejected
- The old mobile UA will be silently rate-limited (always reproducible on `iesdouyin.com` interfaces); you must use the desktop Chrome UA (`room.DESKTOP_UA`)
- `iesdouyin.com/share/user/<sec_uid>` is now a JS anti-scraping shell page with no `unique_id` inside, so any HTML regex is unreliable
- The `web/enter` interface occasionally returns `status_code=10002 unknown error`, a transient soft rejection (risk control / missing msToken / rate limiting); the code already does a silent retry once, which is normal fault tolerance and does not mean the room is unavailable

**Solution**:

- Update Cookie
- Lower the polling frequency
- Change IP
- Update UA (use `room.DESKTOP_UA` desktop Chrome UA)
- If the log shows `10002` and then the HTML fallback succeeds, it is a normal path and needs no action

### Issue 4: HLS validation failure with blank logs / always falling back to FLV

**Symptom** (appears continuously in logs, with no troubleshooting info at all):

```
get_response_status 校验失败（判定为不可达）:      ← 消息是空的
HLS URL validation failed, falling back to FLV    ← 原因完全不可见
```

**Root cause** (three layers, all fixed on 2026-08-05):

- The exception log only printed `{e}`, and on Windows `socket.timeout` / `TimeoutError`'s `str()` returns an **empty string**, so a timeout exception prints blank
- `main.py::_validate_stream_url` used `except Exception: return False` to swallow all failure reasons, giving no clue on fallback
- The m3u8 source HEAD probe only covered `400/401/403/405`, **404 was directly judged unreachable**; and `select_source_url` → the validation call **did not pass through the proxy**, so overseas platforms like TikTok would time out on direct validation and be misjudged

**After the fix**: exception logs include URL + exception type; all failure paths log a warning (including status_code / content-type); m3u8 HEAD non-2xx (including 404) always adds a Range GET probe; `select_source_url` passes through `proxy_addr`. After re-running, the log directly gives the real cause (e.g. `ConnectTimeout`, `HEAD=404, Range-GET=403`); if still unreachable it is an environment issue such as the CDN domain being blocked or the stream URL having expired, not a code misjudgment.

### Issue 5: Danmaku connection fails "connecting through a SOCKS proxy requires python-socks" (system proxy conflict)

**Symptom** (Bilibili and all platforms reusing `WsClient` have their danmaku connection dropped, visible in logs):

```
[弹幕采集]BilibiliDanmaku 连接关闭: connecting through a SOCKS proxy requires python-socks
```

**Two pre-fixed sub-issues** (both real defects, but not the final root cause):

- **Short room_id not converted to real room_id**: `get_bilibili_danmaku_info` used to directly request getDanmuInfo with the URL short number (e.g. `live.bilibili.com/462`); the token returned by Bilibili did not match the real room, so no danmaku was received after join; now it first calls `room/v1/Room/room_init` to convert the short number to the real room_id (462 → 763679) before proceeding (`src/spider.py`).
- **Heartbeat coroutine was never awaited**: `BilibiliDanmaku.heartbeat` is `async def`, but `WsClient._heartbeat_loop` used to call `self._on_heartbeat()` directly without awaiting; Bilibili's long connection was dropped by the server after tens of seconds without a heartbeat; now it checks `inspect.isawaitable(result)` and then `await result` (`src/ws_client.py`).

**Root cause (system proxy "ghost")**: `websockets.connect(proxy=True)` by default **auto-detects and follows the proxy**, obtaining proxy config via `urllib.request.getproxies()`; on macOS this call does not only read shell environment variables but directly reads the system-level proxy in **system network settings** (System Preferences → Network → Proxies). If a proxy tool (Clash-like) wrote HTTP/HTTPS/SOCKS three-layer proxies into system settings (e.g. `socks5://127.0.0.1:7890`), `env | grep -i proxy` finds nothing (`scutil --proxy` can read it), but websockets follows that SOCKS proxy — and the SOCKS protocol requires the `python-socks` library, which raises the above error when not installed. Video pulling goes through ffmpeg/its own headers and does not pass through websockets, so recording is unaffected by the proxy; standalone test scripts behave intermittently depending on the run environment/system proxy state.

**Fix (danmaku direct connection)**: `src/ws_client.py`'s `connect()` explicitly passes `proxy=None`, so the danmaku WS connects directly to the server, unaware of the system proxy and environment variables like `ALL_PROXY`:

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

This fix uniformly takes effect for **all platforms** (Bilibili/Douyu/Huya/Douyin/Twitch, etc.) danmaku connections (all reuse `WsClient`).

**Decision basis**: The danmaku channel is inherently a domestic direct connection and does not need an outbound proxy, consistent with the overall direct-connection semantics of "recording with proxy disabled"; minimizes dependencies (no new `python-socks`); does not touch system settings; explicit declaration is better than implicit detection (avoids re-stepping on the pit if a library upgrade changes default behavior). If an individual overseas platform's danmaku genuinely needs a proxy, a later optional `proxy` parameter can be added to `WsClient` to pass through on demand, without global following.

**Verification**: Fully run `main.py` with no proxy; danmaku is correctly written to disk as SRT; `mypy src/ws_client.py` / `py_compile` pass. When troubleshooting danmaku anomalies, first look at `logs/streamget.log` (DEBUG records collector thread start / connection ready / first danmaku received / connection close reason).

### Issue 6: Douyin/Douyu and other platforms show "live streaming" but never record (no error, no file)

**Symptom**: During `py web.py` (or `python main.py`), Douyin and Douyu rooms print "live streaming…" every monitoring cycle, but "preparing to start video recording" never appears, and no recording file is produced; on the same config, Huya and Bilibili record normally. The log has no error, warning, or hint, and the status panel always shows "live streaming".

**Scope**: All platforms where `get_record_headers()` returns `None` (measured: Douyin, Douyu). These platforms share the characteristic of having no dedicated recording request-header rules (Referer/Origin) and no corresponding Cookie configured.

**Root cause (historic structural bug)**: In `main.py`'s `run()`, the `if headers:` after `headers = get_record_headers(platform, ...)` wrongly wrapped the **entire recording chain** that follows — tls_verify/proxy insertion, recording-status registration, all TS/FLV/MP4/MKV recording branches, `check_subprocess` launching ffmpeg, and `record_success` cycle counting (about 490 lines). Any platform where `get_record_headers` returns `None` (`_RECORD_HEADER_RULES` has no Referer/Origin configured and no Cookie) had its entire recording block **silently skipped**: no print, no error, no recording, just idling every cycle. Platforms with dedicated recording headers (Huya/Bilibili) happened to be unaffected, making the problem look like "an individual platform parse issue" rather than a global structural one.

**Fix**:

1. **Indentation-level correction (main.py)**: Inside the `if headers:` block only the `-headers` insertion (4 lines) is kept; tls_verify insertion, proxy insertion, recording-status registration, all recording branches, and cycle counting are **shifted left 4 spaces as a whole**, escaping the conditional nesting and executing unconditionally.
2. **Validator UA alignment (src/stream_select.py)**: Added the `MOBILE_UA` constant (identical character-for-character to `main.py`'s ffmpeg command default UA); `_validate_stream_url` sends a mobile UA for platforms without a desktop UA — Douyu's hwa CDN occasionally returns 403 to non-browser-UA GETs, so the validator and recorder must use exactly the same UA (method GET + header Referer/Cookie + UA, a trinity).

**Troubleshooting tip**: The entry condition of a long recording chain must precisely correspond to the "whether to record" semantics; "skip the whole block when the condition is false" is the most dangerous failure mode (no exception thrown, no log printed). When all code-path analysis says "there should be a log" but there isn't, the shortest path to locate is to temporarily instrument and print the real `real_url` after `select_source_url` returns, and cross-check the block boundaries against the indentation level by drawing a diagram.

## Contributing Guide

### Code Standards

- Formatting: `black .`
- Import sorting: `isort .`
- Type checking: `mypy` (already with `disallow_untyped_defs = true`, fully passes `--strict` mode)
- Type checking (enhanced, local): `basedpyright` is configured in `pyproject.toml` under `[tool.basedpyright]` (standard mode, excludes `typings/`/`node/`/`ffmpeg/` etc., `venvPath` points to the workbuddy managed venv); CI still uses `mypy` as the standard (basedpyright is not a CI check item, and re-specifying venvPath is needed when switching machines)
- Comment standard: Module/function descriptions uniformly use `#` line comments, **do not use triple-quote `"""` docstrings**; multi-line descriptions start each line with `#` (functional multi-line string literals excepted, e.g. templates/SQL, which should use single quotes + line concatenation instead of `"""`)

### Testing and Coverage

- Run tests: `pytest` (`asyncio_mode = "auto"`, async cases need no explicit marker); currently 496 passed / 2 skipped, total coverage 50.34%
- Coverage config is centralized in `pyproject.toml`: `source = ["src"]`, global gate `fail_under = 50`
- High-frequency-change core modules have independent coverage gates (recorded in `pyproject.toml` comments, checked in CI via `--cov-fail-under` or a script):

| Module | Gate | Current Coverage |
| --- | --- | --- |
| `spider.py` | ≥50% | 50% |
| `stream.py` | ≥70% | 70% |
| `utils.py` | ≥80% | 82% |
| `ttwid.py` | ≥85% | 85% |
| `ab_sign.py` | ≥95% | 99% |
| `proxy.py` | ≥50% | 51% |

- Concurrency-specific tests (`test_concurrency.py` / `test_concurrency_rate_limit.py`) use the dedicated config `.coveragerc-concurrency` (no global threshold), verifying the correctness of `threading.Lock` de-duplication and Douyin rate limiting under multi-threaded environments

#### Web/API Smoke Test Tool (`scripts/smoke_test.py`)

A general, zero-dependency (pure standard library) Web/API smoke test tool for quickly verifying the reachability and core responses of **running HTTP interfaces** such as the Web management panel.

- Config-driven: JSON describes check items (`url` / `method` / `expected_status` / `timeout` / `headers` / `body` / `expect_contains` / `expect_json`)
- `base_url` prefix concatenation, no need to write the full address for each interface
- Three outputs: console (colored), JSON report, HTML report
- Any check failure exits with non-zero code, convenient for CI integration
- **Wired into CI**: the default case `scripts/smoke_web.json` probes the Web panel `/` and `/health` (the latter a public liveness endpoint provided by `src/web_api.py`); the `test` job in `.github/workflows/ci.yml` starts `python web.py` in a controlled way after pytest, does readiness-wait + assertions via `scripts/_ci_web_smoke.sh` (through `.github/actions/retry`), keeps `logs/web-smoke-*` artifacts and turns the job red on failure — covering the "can the panel process really bind and respond" path that TestClient cannot reach

Usage:

```bash
# 检查本机 Web 管理面板（默认 127.0.0.1:8000，示例见 scripts/smoke_web.json）
python scripts/smoke_test.py -c scripts/smoke_web.json

# 生成 HTML 报告
python scripts/smoke_test.py -c scripts/smoke_web.json -r smoke_report.html -f html
```

> Unlike `build_exe.py --smoke` (packaging-artifact smoke test, see Section 5 above), this tool does lightweight liveness probing against **running HTTP interfaces**; the two are complementary.

### Adding New Platform Support

1. Add a platform data-fetching function in `src/spider.py`
2. Add a stream-address parsing function in `src/stream.py`, whose return value includes the `actual_quality` and `available_qualities` fields
3. Add platform identification logic in `main.py`
4. Update `README.md` and this document

## Changelog

> **Live-verification retention convention** (same source as `AGENTS.md` DoD step 2): for changes
> affecting the recording chain / source selection / ffmpeg arguments / platform resolvers, write the
> real-device verification conclusion in the "Verification" subsection of the corresponding changelog
> entry here, synchronised in both CN/EN files.
> Format: `[YYYY-MM-DD] platform | masked URL | script | result | message count`.
> When verification cannot run, write `SKIP(reason)` in the result column
> (e.g. `SKIP(no network)` / `SKIP(room offline)`) and note the hand-back action;
> completion (DoD steps 1–6) must not be claimed until the user re-runs and fills in readable counts.
> Scripts also emit a `VERIFICATION_RESULT: {"platform":..., "status":..., ...}` structured line when run directly.
> Scripts: `tests/test_{bili,douyin,douyu,huya,twitch}_live_collector.py`
> (`python file.py <URL> [seconds]`; requires a live room + network; manual channel by default).
> **Rolling archive**: this section keeps only the current release window; older entries live verbatim in [`docs/changelog/code-wiki-history-en.md`](docs/changelog/code-wiki-history-en.md) (rule stated in the "Changelog Archive Index" above).

### v4.3.0-dev (2026-09-27) — Today's changes classified by module: four release-chain fixes + findings 4/5/6 + the four-doc size pass + the AGENTS.md trim + metadata and consistency sync

> This section is the **module-level overview** of everything changed on 2026-09-27 (summary table plus the readings that
> justify each verdict). The path-level detail follows today's documentation policy and lives where the other 73
> historical inventories live; the four same-day detail entries (three release-chain faults, findings 4/5/6 plus the doc
> size pass, and the `AGENTS.md` trim) sit below and cross-verify this one.

| Module | Nature of change | Main files | Key reading / judgement |
| --- | --- | --- | --- |
| Packaging and release chain | `make_zip` naming and guards modified, Linux ffmpeg source and eight pins corrected; **added** `_clean_stale_release_zips` / `_drop_stale_release_zips` / `_assert_dual_zips_are_two_files` plus the `--dual` vs `--no-zip` exclusion | `build_exe.py` | No function or download source deleted; artifact names are `DouyinLiveRecorder-v4.3.0-windows-amd64-{lite,full}.zip` |
| CI and release workflow | **Added** the `release-guard` job and the `Verify dist contains both lite & full zips` step | `.github/workflows/build-release.yml` | `gh release delete` keeps tags by default; `fail_on_unmatched_files: true` not relaxed; the 08:14 edit by another actor was untouched here (logged) |
| Tests | **Added** 9 cases (10 assertion units), reworked `_stub_build_steps`, corrected two comments | `tests/test_build_exe.py` | Single file 100 -> **105 passed**; four mutations each reddened only their own lock; `DIST_DIR` repointed to `tmp_path` so tests cannot delete real artifacts |
| Root conventions | `make_zip` item gained judgements (4) and (5) plus the nine lock names; protobuf range corrected to `>=6.33.5,<8`; volume pass | `AGENTS.md` | 97,034 -> **95,715 B** (-1.4%); token audit: 0 lost among `test_` names, CVE codes and `UPPER_SNAKE` identifiers |
| CN/EN wikis | **Added** four detail entries plus this overview; 73 inventories relocated; 109 (zh) / 181 (EN) truncated table cells restored; statistics and index sections rewritten; step 4 of "Packaging and Release" corrected | `CODE_WIKI.md`, `CODE_WIKI_EN.md` | `^### v` 169 -> **173 = 173**; dangling-code-span paragraphs 26/18 -> **0**; both files pure CRLF |
| User-facing docs | **Version-entry sync in a later step the same day** (09-26 ~ 09-27 changes folded into the `v4.3.0` entry, the date range extended to 09-27, and the stale test readings plus the "permanently red on this host" note corrected) | `README.md` (104,040 -> 109,648 B), `README_EN.md` (123,017 -> 129,644 B) | All five subsections match one-to-one in count (🐛 9 / ✨ 12 / ⚠️ 9 / 🛠️ 7 / 🧪 4) and order; `^### v` 20 = 20; both files still pure CRLF. They genuinely needed no update during the consistency audit; this step **adds** content and still does not compress the README changelog |
| Reference sub-docs and local records | **Added** two inventory appendices; session learnings and work log appended | `docs/agent-reference/changelog-file-inventories.md` (130,064 -> 139,024 B), `-en.md` (98,458 -> 107,897 B), `session-learnings.md`, `.workbuddy/memory/2026-09-27.md` | 41 (zh) / 32 (EN) historical inventories plus this block; every pointer resolves; 0 orphaned table headers |
| Build-artifact metadata | **Rebuilt** egg-info, fixing two real drifts | `DouyinLiveRecorder.egg-info/` (gitignored + dockerignored) | `PKG-INFO`'s `Requires-Dist: h2` `>=4.3.0` -> `>=4.4.1`; embedded README gained the v4.3.0 section; the other four files byte-identical |
| Dependencies / versions / ignore lists / config / i18n | **One comment repair only; the rest verified as needing no update** | `requirements.txt` (inline comment completed), `pyproject.toml`, `Dockerfile`, `docker-compose.yaml`, `.gitignore`, `.dockerignore`, `.coveragerc-concurrency`, `config/config.ini`, the four catalogs | The `websockets>=14.0` inline comment was cut at "…14.0+ API," (a trailing comment cannot continue onto the next line, so this was a real truncation); completed against the matching `pyproject.toml` comment as "12/13.x makes `connect()` raise TypeError immediately and the reconnect loop swallows it, so danmaku never connects". **No specifier changed**: 23 vs 23 package-name sets still equal, `tests/test_regression_2026_09_22_gates.py` 25 passed, the file stays pure LF. Everything else: `python 3.14` / `node 24` identical across workflows; tool pins match what is installed; no gaps in the four exclude sets; `config.ini` has 6 sections / 143 keys and today added no key; four catalogs equal at 780 keys, `.mo` in sync at 781 entries, extractor reports 0 missing |

- **Consistency readings (measured this round, all recomputable)**: `grep -c '^### v' CODE_WIKI.md CODE_WIKI_EN.md` -> 173 = 173;
  `importlib.metadata.version('DouyinLiveRecorder')` -> 4.3.0; `scripts/check_version.py` PASS;
  `scripts/compile_po.py --check` in sync at 781 entries; `scripts/extract_i18n_strings.py` 0 missing;
  `pytest tests/test_i18n.py -k "keyset or sync or catalogs"` -> 6 passed;
  `pytest tests/test_proto_runtime_compat.py tests/test_i18n.py` -> 43 passed.
- **Deliberately not done (honest boundary)**: no dependency added to `requirements.txt` or `pyproject.toml` (nothing required one);
  `config/config.ini` not written (it holds credentials, is ignored, and no new key was needed); `README*.md` untouched per the
  user's 09-27 decision; `docs/agent-reference/session-learnings.md` remains the only LF-only file in that directory
  (finding 7, out of scope this round).

> The path-level inventory was moved verbatim to [docs/agent-reference/changelog-file-inventories-en.md](docs/agent-reference/changelog-file-inventories-en.md) (entry: v4.3.0-dev (2026-09-27) — Today's changes classified by module: four release-chain fixes + findings 4/5/6 + the four-doc size pass + the AGENTS.md trim + metadata and consistency sync | section: Today's change inventory by module (added / modified / removed + file paths)).

### v4.3.0-dev (2026-09-27) — `AGENTS.md` size pass: three real duplications removed and relocated readings turned into pointers; measured conclusion is that the root file is already at its constraint-density floor

- **Motivation**: the user asked to shrink `AGENTS.md` while keeping every core instruction and key constraint.
  Measure the redundancy classes first, then choose the method.
- **What the measurement showed**: the relocatable one-off readings had already been relocated correctly.
  `BtbN 126,600,656 B / 108,761,296 B`, `johnvansickle 41,888,096 B`, `autobuild-2024-10-31`, the `latest`
  republish at 2026-09-26T13:22:38Z, the ~two-week retention of daily `autobuild-*` tags (only
  `09-13~09-26`, 15 entries) and `api.github.com` `assets[].digest` all exist **verbatim** in
  `docs/agent-reference/measured-evidence.md` under "Runtime upstream integrity artifacts", yet `AGENTS.md`
  copied them again. Those numbers in the SEV-10 item and in the "three places to change per source" item are now
  pointers to that section, with an explicit note that the root file no longer duplicates values.
- **Three genuine duplications removed** (the file's own "no second source of truth" rule): (1) key convention 14
  and the 已知坑/i18n extractor-blindspot item overlapped - merged into 14 (absorbing the four catalog filenames and
  the "reports 0 missing, falsely green" consequence) and deleted the latter; (2) the version line in "Project
  overview" restated key convention 1 wholesale - compressed to a pointer; (3) two routing bullets in "Risk control"
  re-quoted the command and the forbidden directory list owned by their detail sections - kept only the judgement
  plus the pointer (the command `pip install --ignore-installed --no-deps -r requirements.txt` and the
  `downloads/`/`logs/`/`backup_config/` prohibition are still word-for-word in "CI / workflow conventions" and
  "temp-script cleanup"). The two same-cause items about parent-process `PYTHONUTF8` and
  `reconfigure(errors="replace")` in "Gate commands" were merged into one.
- **Reading**: `AGENTS.md` 97,034 -> **95,715 B** (-1,319, -1.4%), 496 lines, pure CRLF (LF-only count 0).
- **Why only 1.4% (a conclusion for later sessions)**: the file has **224 top-level items averaging 383 B**
  (command: `python -c "import pathlib,re; t=pathlib.Path('AGENTS.md').read_text(encoding='utf-8'); top=[x for x in t.splitlines() if re.match(r'^([-*] |[0-9]+[.] )', x)]; print(len(top), sum(len(x.encode()) for x in top)//len(top))"`),
  and item by item each one is an incompressible payload of judgement + constant name + test name + error code.
  Preservation audit: of the 997 code spans in the original, only 15 no longer appear in their old form, and each was
  checked: (a) 9 were `::test_...` fragments rewritten as "file name once, then bare test names" - all **55 test
  identifiers still present**; (b) 6 were readings that live on in the wiki / measured-evidence. Loss counts for
  `test_` identifiers, CVE/PYSEC/GHSA and MIN/SEV/MID codes, and `UPPER_SNAKE` constants and environment variables
  are all **0** (only three byte readings now exist solely in measured-evidence, by design). So under the current
  architecture the volume is near its floor; going materially lower requires an architecture change (move 已知坑
  detail into per-topic sub-docs, leaving the root file as index plus hard rules), which contradicts the file's own
  opening rule that "已知坑 constraint sentences stay in the root file" and therefore **needs the user's approval**;
  not attempted in this pass.
- **Verification**: `scripts/run_gates.py --list` still parses 8 gates (the parser reads the fenced bash block of the
  "Gate commands" section, which this pass did not touch);
  `pytest tests/test_run_gates.py tests/test_regression_2026_09_22_gates.py` -> **67 passed / 1 skipped**, including
  the three source locks ("first command must be the verbatim black gate line", "the `PYTHONUTF8=1` prefix must
  parse into env", "renaming the section must return an empty list"). Line-ending form unchanged. Docs-only change,
  so step 2 of the Definition of Done (live-device verification) does not apply.

### v4.3.0-dev (2026-09-27) — Fourth release-chain hardening: `--dual` now validates both return paths after packaging and prunes stale `dist/` zips before packaging; four docs slimmed by relocating 73 historical file inventories and restoring `…`-truncated table cells

- **Motivation**: the closing review of the previous entry produced findings 1-8; the user approved the already-fixed
  1/2/3 and asked for 4/5/6 plus a documentation size pass. (4) `make_zip`'s return value was discarded with `_ =`
  in the `--dual` branch, so nothing locally checked that the two variants really differ and both exist on disk, and
  `dist/` was never cleaned, so leftovers got swept in by `path: dist/*.zip`; (5) the artifact-name example still read
  `windows-x64` (Windows actually yields `amd64`; `x64` only exists as the runtime key after `_NODE_ARCH_MAP`
  normalization); (6) "both pre-existing tests assert *only* `zip_path.is_file()`" was imprecise -
  `test_make_zip_aborts_when_archive_still_contains_logs` asserts the `SystemExit` text.
- **Changes (`build_exe.py`, three)**: (1) `_assert_dual_zips_are_two_files(lite_zip, full_zip)` - identical names
  raise `SystemExit` (`zipfile` `"w"` truncates in place without an error, and a single-call guard cannot see two
  calls landing on one file), and a missing variant raises `SystemExit` too; (2)
  `_clean_stale_release_zips()` + `_drop_stale_release_zips()` - delete only `{APP_NAME}-v*.zip`, only when a zip is
  actually being produced, and print the removed list (silent deletion is as bad as not deleting); the `--no-zip`
  path never cleans. The call must sit **before the first** zip: inside `make_zip` the second call would delete the
  first one's artifact. (3) The non-`--dual` path keeps `make_zip`'s return value and prints the real artifact name.
- **Same-family corrections**: the truncation-incident comment in `tests/test_build_exe.py` rewritten to the true
  artifact name plus the precise per-test judgement; step 4 of "Packaging and Release" claimed "smoke tests run on
  the lite version", which the MID-2254 ordering change already disproved - it now says smoke runs after **both**
  zips against the release directory that holds the runtimes, and records the pruning plus the post-hoc check; the
  same line carried a stale exception name (`ChallengePageError` was removed on 2026-09-23 under MIN-2267; only
  `IntegrityError` / `NetworkError` remain) and a `…` that cut a code span in half.
- **Regression locks (5 new cases in `tests/test_build_exe.py`, all mutation-verified)**:
  `test_dual_build_aborts_when_both_variants_land_on_one_zip`,
  `test_dual_build_aborts_when_a_variant_zip_is_missing`,
  `test_dual_build_prunes_stale_zips_before_first_zip`,
  `test_no_zip_build_keeps_existing_dist_zips` (inverse lock: no packaging means no deletion),
  `test_clean_stale_release_zips_only_touches_own_artifacts` (includes the "missing `dist/` is a no-op" case and
  idempotency). `_stub_build_steps`'s `make_zip` stub now **returns a name derived from `suffix` and really writes
  the file**: the old constant `stub.zip` would turn all three `--dual` cases falsely red once the new check landed;
  `DIST_DIR` is also redirected to `tmp_path`, otherwise the tests would delete the user's real `dist/` artifacts.
  Mutation readings: cleaner made a no-op -> 2 red; `--dual` wiring removed -> 1 red; whole post-hoc check disabled
  -> 1 red; existence check only disabled -> 1 red. Each mutation reddened exactly its own lock, and
  `build_exe.py` came back byte-identical to its backup.
- **Doc size pass (policy: relocate, never delete)**: measured first, and the redundancy the request assumed was
  mostly not there - 0 trailing-whitespace lines, 0 multi-blank runs, and only 1 README line duplicated verbatim from
  `CODE_WIKI`; all the weight is body text. What genuinely moved is 73 historical "Files involved (classified by
  module)" inventories (41 zh blocks / 32 EN blocks) into
  `docs/agent-reference/changelog-file-inventories.md` / `-en.md`, each original spot keeping its section heading plus
  a one-line "entry | section" pointer. The pass also repaired a silent information loss from the 2026-09-25
  compression: 109 (zh) / 181 (EN) table cells truncated with `…` were restored from `.workbuddy/docold` by unique
  prefix match (+18,439 B / +33,117 B; 2 ambiguous matches were deliberately skipped).
  Readings (**before this entry was written**; `README*` are byte-identical to the originals):
  `CODE_WIKI.md` 638,616 -> 552,368 B (-86,248, -13.5%), `CODE_WIKI_EN.md` 692,281 -> 649,906 B (-42,375, -6.1%),
  `README.md` 104,040 B and `README_EN.md` 123,017 B unchanged; new appendices 130,064 B / 98,458 B.
  Confirmed scope: the README changelog is user-facing release notes and is not compressed.
- **Self-proof (recomputable)**: `grep -c '^### v'` is still **170 = 170**; a line-by-line reconciliation shows every
  non-empty original line still lives either in its document or in the appendix (only the 109/181 restored table rows
  vanished in their truncated form); all 41/32 pointers resolve to an existing file **and** to a real
  "entry + section" pair inside it; 0 orphaned table headers; dangling-code-span paragraphs dropped from 26 (zh) /
  18 (EN) to 0; every relocated block ends at a heading or a 验证/Impact/Conclusion-class label, so no table header
  was separated from its body; all four documents plus both appendices are pure CRLF (LF-only count 0).
- **Doc drift fixed on the way**: the "Document Statistics and Index" section claimed **285** Markdown files with no
  command attached, which cannot be recomputed; it now carries the command plus today's reading (**100**), the review
  reports are listed at their real home `docs/worklog/` (9 files), and a `docs/agent-reference/` row plus a new
  "Reference Sub-Document Index" section were added. Nine Chinese comment lines inside EN fenced command blocks were
  translated. Known and left undone: 162 Chinese lines remain inside EN code fences (the architecture diagram and the
  directory tree labels); that is translation work, not size redundancy, and is deferred to its own pass.
- **Verification**: `scripts/run_gates.py` 8/8 rc=0 (incl. `check_annotations.py` PASS at 23.8% mean comment density,
  `compile_po.py --check` in sync at 781 entries, `check_version.py`, `check_runtime_pins.py` fully pinned);
  its built-in full-suite fallback **3240 passed with an empty warnings summary** (up from 3235 = the 5 cases added
  here); `pytest --cov=src` -> 3240 passed / 14 skipped, total coverage **83.91%**, and `scripts/check_coverage.py`
  **PASSED: all 42 modules meet their threshold** (`src/proto/douyin_pb2.py` explicitly exempt);
  `basedpyright` (no path) 0 errors / 0 warnings / 0 notes; `mypy` (no path) Success; black and isort report both
  touched files unchanged; `python -m pytest tests/test_build_exe.py` alone -> **105 passed** (was 100).
- **Not measured / handed back**: (1) `python build_exe.py --smoke --dual` was **not** run locally (full PyInstaller
  build plus ~300MB upstream download), so the real "prune, then both zips land in `dist/`" path is still confirmed
  by CI's `Verify dist contains both lite & full zips` on its first run; (2) this is a docs-only change with no
  recording-chain / source-selection / ffmpeg-argument / platform-parsing touch point, so step 2 of the Definition of
  Done does not apply; (3) restored cells reflect the `.workbuddy/docold` snapshot (pre-2026-09-25), so any wording
  changed before that snapshot comes back in its snapshot form; (4) to reject the relocation, delete this entry's two
  artifacts: the two appendix files plus the 73 pointer lines.

### v4.3.0-dev (2026-09-27) — Third release-chain fault: `make_zip` truncated the artifact name via `Path.with_suffix(".zip")`, so lite was overwritten in place by full

- **Symptom**: this `Build & Release` run **passed** the pin verification and
  `Build executables + smoke test`, then reddened on the next step
  `Verify dist contains both lite & full zips`: `Found 0 lite zip(s) and 0 full zip(s)`,
  `Error: Expected both *-lite.zip and *-full.zip in dist/, but missing one or both.`, while
  `Full listing:` shows exactly one file, `dist/DouyinLiveRecorder-v4.3.zip` at 160,298,993 B.
  So the artifact **did exist** — what had vanished from both variant names were the `-lite`/`-full`
  segments together with `-<os>-<arch>`. Same family as the two earlier reds
  (`Pattern 'dist/*-lite.zip' does not match any files`), different cause, and one step further along.
- **Root cause**: `build_exe.make_zip()` built `zip_base = DIST_DIR / f"{APP_NAME}-v{version}-{os}-{arch}{suffix}"`
  and then `zip_path = zip_base.with_suffix(".zip")`. `Path.with_suffix` splits the extension at the
  **last dot**, and the version itself contains dots: measured locally on the real per-platform names —
  `Path('DouyinLiveRecorder-v4.3.0-windows-amd64-lite').suffix == '.0-windows-amd64-lite'`, so
  `with_suffix('.zip')` yields `DouyinLiveRecorder-v4.3.zip` (`-full` resolves to the **same** name, and so
  does `linux-x86_64`). Both `make_zip` calls of `--dual` therefore wrote one and the same path: the second
  (full) truncated and rewrote the first (lite) through zipfile's `"w"` mode, leaving full's content on disk
  under a name carrying neither variant nor platform.
- **Why it stayed invisible**: neither pre-existing `make_zip` test says anything about the **name** (one
  only asserts `zip_path.is_file()`, the other only the `SystemExit` text) — name drift is completely
  invisible to "does a file exist". The only name-aware judgement in the repo is the CI `dist/*-lite.zip`
  glob, so only a real `--dual` run could redden. The non-`--dual` path (`ci.yml` build-verify uses
  `--no-zip`) never exposed the missing platform segment either.
- **Fix (three parts, all in `build_exe.py`)**: (1) `.zip` is now concatenated inside the same f-string,
  keeping naming a single definition point, with a comment recording why `with_suffix` is banned;
  (2) a new structural invariant — the composed `zip_path.parent` must still be `DIST_DIR`, otherwise
  `SystemExit` (when `version`/`suffix` contain a path separator the f-string produces a **sub-path** and
  the artifact silently lands outside `dist/`; on Windows pathlib treats `\` as a separator too);
  (3) `--dual` and `--no-zip` are now mutually exclusive and fail fast — the `--dual` branch never reads
  `no_zip`, so `--dual --no-zip` used to **silently ignore** the flag the user explicitly typed and emit
  both large zips anyway (a contradictory combination must either error out or honour it, not half-run).
- **Regression locks (`tests/test_build_exe.py`, four functions / five cases, all mutation-verified)**:
  `test_make_zip_name_keeps_dotted_version_and_variant_suffix` (structural regex: full `v4.3.0` +
  `<os>-<arch>` + `-lite`/`-full` + `.zip`; the real Windows name looks like
  `DouyinLiveRecorder-v4.3.0-windows-amd64-lite.zip`),
  `test_dual_suffixes_do_not_collide_on_one_zip` (two `make_zip` calls must yield two distinct files),
  `test_make_zip_refuses_name_containing_path_separator` (runs **both** argument positions — `version` and
  `suffix` — with `'/'` rather than `os.sep` so the refusal branch really executes on both platforms),
  `test_dual_and_no_zip_are_mutually_exclusive` (asserts `order == []`, locking "the judgement precedes
  every build step").
  Mutation readings: reverting the implementation to `with_suffix(".zip")` reddened the first two while the
  pre-existing `make_zip` tests stayed green (disproving the old assertion standard); forcing the two new
  guards to `if False:` reddened the last two — the guard-(2) one via `FileNotFoundError`, which proves its
  assertions are actually reached.
- **Verification**: `pytest tests/test_build_exe.py` **100 passed**; `basedpyright build_exe.py tests/test_build_exe.py`
  0 errors / 0 warnings / 0 notes; `mypy` (no path arguments) Success over 158 files;
  `black --check` / `isort --check-only` report both files unchanged; `check_annotations.py` passes;
  line-ending form of every touched file unchanged (`build_exe.py` and `AGENTS.md` pure CRLF,
  `tests/test_build_exe.py` pure LF).
- **Not measured / handed back**: (1) `python build_exe.py --smoke --dual` was **not** run locally (it needs a
  full PyInstaller build plus ~300 MB of upstream downloads), so "lite + full both present in dist/" can only
  be confirmed by the first CI run of `Verify dist contains both lite & full zips`; (2) the failed Release
  record is reclaimed by `release-guard` (`needs.build.result != 'success'`) and the tag is kept, so a
  re-run republishes; (3) any historical asset named `DouyinLiveRecorder-v<major>.<minor>.zip` is a product
  of this defect — its lite half was never actually distributed, and a re-run is what yields correctly
  named per-platform variants.

### v4.3.0-dev (2026-09-27) — Release-chain fix: Linux ffmpeg pins now point at an immutable month-end release tag, plus a `release-guard` job that rewinds the empty Release left behind by a failed build

- **Background**: a tag-triggered `Build & Release` run died in the Linux build job's ffmpeg download step with
  `[build][FATAL] _ffmpeg_temp.tar.xz SHA256 不匹配（期望 87de0900…，实际 0cfb2146…），已终止构建`, and the
  very next step (`softprops/action-gh-release`) then reported
  `⚠️ Pattern 'dist/*-lite.zip' does not match any files` (`fail_on_unmatched_files: true`). The second message
  is a **downstream symptom** of "dist/ has no artefacts", not a separate fault — turning
  `fail_on_unmatched_files` off would erase the only visible signal.
- **Root cause**: both Linux slots of `_FFMPEG_DOWNLOAD_URLS` pointed at BtbN's
  `releases/download/latest/...`. `latest` is a **rolling alias**: the same asset name is re-uploaded over and
  over, so its digest keeps changing — tag `latest` was republished at `2026-09-26T13:22:38Z`, which invalidated
  the pin value `87de0900…` taken earlier the same day; the arm64 pin `30774c8f…` was stale too (now `f2fe35e9…`).
- **Chosen route (per the user: "switch to an immutable month-end tag")**: both slots now pin the **month-end**
  autobuild tag `autobuild-2026-08-31-13-27` (assets
  `ffmpeg-n9.0.1-11-ge47273f4d9-linux{64,arm64}-gpl-9.0.tar.xz`), with pin values taken from
  `api.github.com/repos/BtbN/FFmpeg-Builds/releases/tags/<tag>` → `assets[].digest`
  (linux64 `182c1b50…`, linuxarm64 `e2dd447c…`). Why month-end specifically: the repo holds only **38 releases**;
  daily `autobuild-*` tags survive only about two weeks (only 09-13…09-26, 15 of them, were left), so pinning a
  daily tag is planting a guaranteed 404, while month-end tags reach back to `autobuild-2024-10-31` — the only
  combination where both URL and digest are immutable. Cost: the bundled ffmpeg lags `latest` (n9.0.2) and now
  sits at n9.0.1-11-ge47273f4d9; upgrading means editing the tag **and** the pin by hand, which is exactly the
  SEV-10 manual gate — deliberately not replaced by auto-fetching the current hash.
- **Second item, the guardrail**: `build-release.yml` gains a `release-guard` job
  (`needs: [prepare, build]`, `if: always() && release path && needs.build.result != 'success'`) that runs
  `gh release delete` on the empty/partial Release pre-created by `release-create` (tag is **kept**) and emits a
  `::warning::`. Why: `release-create` deliberately pre-allocates the Release before build to avoid three build
  jobs racing to create it, but when a build fails the finalizing `release` job is skipped by `needs: build`, so
  an empty Release stays in the repo with zero downloadable assets.
- **Files touched**: `build_exe.py` (two URLs + two pin cells + three comment/maintenance corrections);
  `tests/test_build_exe.py` (new `test_linux_ffmpeg_urls_pin_an_immutable_release_tag`: forbids
  `/releases/download/latest/`, forbids the `n9.0-latest-` asset-name form, requires one shared tag across both
  arches); `.github/workflows/build-release.yml` (new `release-guard` job only — matrix/cache/build/upload logic
  untouched); `AGENTS.md` (SEV-10 entry gains the "month-end tag" rule and its regression lock; a new
  empty-Release guardrail bullet under CI/workflow conventions; volume readings refreshed);
  `docs/agent-reference/measured-evidence.md` (2026-09-27 re-measurement table).
- **Measured (2026-09-27)**: `releases/latest` → linux64 150,999,836 B / `0cfb2146…`, linuxarm64 127,395,868 B /
  `f2fe35e9…` (neither equals the old pins); `releases?per_page=100` → 38 releases total; month-end tag assets →
  linux64 126,600,656 B / `182c1b50…`, linuxarm64 108,761,296 B / `e2dd447c…` (a `checksums.sha256` asset is
  also published, usable as a second cross-check); gyan.dev Windows `.sha256` still `60f46726…` (no drift);
  nodejs.org's first `lts` entry still `v24.21.0` (no drift). A prefix fetch confirmed the month-end asset is a
  valid xz (magic `fd377a585a00`) whose top-level directory is
  `ffmpeg-n9.0.1-11-ge47273f4d9-linux64-gpl-9.0/`.
- **Verification**: `pytest tests/test_build_exe.py tests/test_check_runtime_pins.py` → **115 passed**; full
  `pytest` → 3229 passed / 14 skipped with an empty warnings summary (the single failure,
  `test_web_config.py::TestFormatUrlLine::test_normal_line`, is the sandbox failing to resolve
  `live.douyin.com`; re-run alone it is **1 passed**, unrelated to this change); `mypy` (no args) → Success over
  158 files; `basedpyright tests/test_build_exe.py` → 0 errors / 0 warnings / 0 notes; `black --check` and
  `isort --check-only` unchanged; `check_annotations.py` passes; `check_runtime_pins.py --strict` still rc=0;
  `yaml.safe_load` on the workflow parses with jobs in the order prepare / release-create / build /
  release-guard / release. Line endings unchanged (`build_exe.py`, `AGENTS.md`, `CODE_WIKI*.md`,
  `measured-evidence.md` stay pure CRLF; the test file and the workflow stay pure LF).
- **Not yet verified / handed back**: ① `github.com` direct links are reset on this box (prefix fetch → http=000,
  full fetch died at 5.4 MB), so "download from the new URL and compare against the pin" can only be confirmed by
  the first GitHub runner run; ② `bin/ffmpeg` / `bin/ffprobe` inside the month-end archive were not directly
  confirmed by this prefix (5.4 MB only covered `doc/`) — we rely on the 09-26 measurement for the same asset
  family; if they are missing, `_extract_linux_ffmpeg_binaries()` raises `SystemExit` rather than degrading to a
  silent empty package; ③ Linux full-package size changes with the new tag (126,600,656 B / 108,761,296 B) and
  must be re-checked against CI artefacts via `scripts/report_bundle_size.py` before touching any platform
  threshold.

### v4.3.0-dev (2026-09-27) — Second release-chain fault fixed: eight slots of `_PINNED_RUNTIME_SHA256` had been rewritten to the official-signature marker; hashes re-pinned from the official channels

- **Symptom**: the pasted log only carried the last two lines `Run softprops/action-gh-release@v3` /
  `⚠️ Pattern 'dist/*-lite.zip' does not match any files`. It is read the same way as the entry above
  (`fail_on_unmatched_files: true` is the only visible signal of a missing artefact and must stay on).
  Re-computing locally exposed a **second fault in the current working tree that fires even earlier**:
  eight slot values in `build_exe.py`'s `_PINNED_RUNTIME_SHA256` had been replaced wholesale with
  `OFFICIAL_SIGNATURE_PIN` (file mtime 07:58, i.e. after the 01:45 wrap-up of the previous entry), which
  moves the break point of the release chain from the build job forward to the prepare job.
- **Root cause**: the signature mode only applies to slots whose upstream really publishes no hash *and*
  which are registered in `_RUNTIME_GPG_SIGNATURES` with a signature URL plus the full 40-hex primary
  fingerprint — in this repo that is only the four macOS ffmpeg/ffprobe slots. The five node slots
  (nodejs.org `SHASUMS256.txt`), `windows-x64/ffmpeg` (gyan.dev `.sha256`) and the two Linux ffmpeg slots
  (BtbN `assets[].digest`) all have officially published values; once turned into the marker,
  `_is_signature_satisfied` returns False because the slot is unregistered → all three disjuncts of
  `_slot_is_gated` are False. Two consequences: `scripts/check_runtime_pins.py --strict` returned **rc=1**
  (the prepare job's fail-closed step goes red) and
  `tests/test_build_exe.py::test_table_never_declares_signature_mode_without_satisfaction` **failed** —
  that lock exists precisely to catch this rewrite.
- **Action**: all eight values re-derived from the **official channels** named in the AGENTS.md /
  `build_exe.py` maintenance notes, never from locally downloaded self-computed digests:
  `curl -sS https://nodejs.org/dist/v24.21.0/SHASUMS256.txt` (win-x64 `.zip`, linux/macos `.tar.gz` — the
  five asset names `_download_nodejs` actually fetches);
  `curl -sSL https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip.sha256` → `60f46726…47ba`
  (no drift);
  `curl -sS https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/tags/autobuild-2026-08-31-13-27`
  → linux64 `182c1b50…` / linuxarm64 `e2dd447c…` (byte-identical to what measured-evidence.md records; a
  month-end tag's digest is immutable); plus confirmation that the first `lts` entry of `dist/index.json`
  is still `v24.21.0` (Krypton). The macOS ffmpeg/ffprobe slots keep the signature mode untouched.
- **Scope**: `build_exe.py` only (8 pin values + one `[2026-09-27 restore]` note above the table + a
  per-node-line source asset name). Logic, the URL table, the predicates, tests and workflows untouched.
- **Verification**: before the change `check_runtime_pins.py --strict` was **rc=1** and
  `test_table_never_declares_signature_mode_without_satisfaction` FAILED (8 offenders named per slot);
  afterwards both `--strict` and the structural mode return **rc=0**, `pytest tests/test_build_exe.py`
  **95 passed**, `python scripts/run_gates.py` **8/8 green rc=0**, full `pytest` **3230 passed /
  14 skipped** with an empty warnings summary, `basedpyright build_exe.py` 0 errors / 0 warnings / 0 notes,
  and `black --check` / `isort --check-only` / `py_compile` pass. End-of-line shape unchanged (build_exe.py
  pure CRLF: 1686 CRLF / 0 bare LF).
- **Not measured / handed back**: ① "download in full and compare against the pinned value" still only
  runs on a GitHub runner first — `github.com` direct links are reset on this machine, only
  `api.github.com`, `nodejs.org` and `gyan.dev` are reachable; ② during this session `build-release.yml`
  was modified **concurrently** at 08:14 (a new `Verify dist contains both lite & full zips` step and
  `| tee build_exe.log` on the build command). That file is neither changed nor reviewed by this entry;
  under `pipefail` the `tee` does not swallow `SystemExit`, but its author should confirm before releasing.

### v4.3.0-dev (2026-09-26) — Release-chain integrity gate gains an "official signature" mode and Linux ffmpeg moves to BtbN: `build-release.yml` prepare goes from rc=1 to rc=0 without loosening SEV-10's fail-closed semantics

- **Background**: the prepare job failed at `Verify runtime binary SHA256 pins (fail-closed)` with
  `Error: Process completed with exit code 1.`, and the log body is literally the output of
  `scripts/check_runtime_pins.py --strict`: two in-matrix slots (`linux-x64/ffmpeg`, `macos-arm64/ffmpeg`) still
  carry the placeholder marker. Located precisely at `.github/workflows/build-release.yml:141-149`; rc=1 comes from
  the `--strict` branch of the checker. This is not a defect — the gate stopped the release exactly as designed
  (both the `build_exe.py` pin-table comment and the `AGENTS.md` SEV-10 entry say: if upstream publishes no hash,
  the release chain stays red).
- **Why deleting the gate was not the fix**: the pin table does not live in the workflow (source of truth is
  `build_exe._PINNED_RUNTIME_SHA256`; the YAML only passes values through via `DLR_RUNTIME_SHA256`). And
  `require_pinned_hashes()` is auto-true under `GITHUB_ACTIONS=true`, so removing the prepare step would only move
  the same failure into the three build jobs (each after a full pip install, still aborting before any download) —
  zero artefacts either way.
- **Chosen route (per the user's "grade integrity criteria by what each upstream actually publishes")**: class ①
  "release-time runtime binaries" gains a second satisfaction mode **behind the single predicate**
  `build_exe._slot_is_gated()` — the **official signature mode**: table value = `OFFICIAL_SIGNATURE_PIN`, and the
  slot must actually be registered in `_RUNTIME_GPG_SIGNATURES` with a 40-hex fingerprint. The marker alone never
  grants passage (same anti-"easier-to-fill marker = free pass" wall as the 4th class `SOURCE_BUILD_PROVENANCE`).
  macOS's two slots take this mode (evermeet publishes `/sig`, no hash); the Linux slots moved to BtbN's n9.0-series
  assets, pinning the `assets[].digest` SHA256 published by `api.github.com`, so no MD5 downgrade mode was needed.
- **SEV-2221 fixed on the way**: `_download_file()`'s pre-download gate only accepted `_is_pinned()`, while the
  signature check sat after the download inside the "hash already matched" branch — so a placeholder-valued macOS
  slot never reached the download and the P-2 verification had **never executed** on the real build path. The gate
  now accepts both modes, and a signature-mode slot **must** pass verification after download (BADSIG / signer not
  in the pinned key's primary-or-subkey set / missing gpg or unreachable signature on the release path all
  `SystemExit`); the observed SHA256 is logged as the audit trail for the rolling alias.
- **Scope**: `build_exe.py` (new constant + predicates, `_download_file` dispatch, `_unpinned_action` naming the
  exact reason a signature declaration is unsatisfied, the two Linux rows of `_FFMPEG_DOWNLOAD_URLS`, four pin-table
  cells, and Linux extraction pulled out into the layout-agnostic `_extract_linux_ffmpeg_binaries()`);
  `scripts/check_runtime_pins.py` (per-mode `[NOTE]` announcement, judgement still delegated);
  `tests/test_build_exe.py` (+12 cases: signature-mode truth table, case-insensitive marker, fingerprint shape gate,
  table/registration stay-in-sync invariant, the SEV-2221 reachability lock, abort-on-bad-signature and
  abort-when-gpg-missing, unregistered marker must not download, both archive layouts plus abort-on-missing-binary;
  `_ALLOWED_HOSTS` gains `github.com` and drops `johnvansickle.com`; `_FakeResponse` gains `headers` and drains per
  read); `tests/test_check_runtime_pins.py` (`_fake_module` exposes the new symbols + 2 routing cases);
  `.github/workflows/build-release.yml` — **comments only** (4 spots: the `DLR_RUNTIME_SHA256` legend, the prepare
  step explanation, the source-host list, and the gnupg step noting verification is now the sole criterion);
  matrix / caching / build / upload / release logic untouched. Plus `AGENTS.md` and
  `docs/agent-reference/measured-evidence.md` (every retrieval command and reading from this round).
- **Measured (2026-09-26)**: `evermeet.ca/ffmpeg/getrelease/zip/sig` → 200 / `application/pgp-signature` / 594 B
  binary OpenPGP packet, landing on `e.deolaha.ca:4242/pub/ffmpeg/ffmpeg-9.0.2.zip.sig`; keyserver lookup of
  `0x476C4B611A660874` → 200, UID `static FFmpeg binaries (signing key)`, server-echoed fingerprint equal to the
  pinned value (**a second, independent channel** — this closes R-2's "fingerprint never corroborated");
  `johnvansickle ...amd64-static.tar.xz.md5` → 200 with the same value as 2026-09-22, `.sha256` → 404; BtbN
  `linux64-gpl-9.0` = 150,998,508 B / `linuxarm64-gpl-9.0` = 127,417,700 B, and a ranged prefix fetch + `tar -tJf`
  confirms the binaries sit at `bin/ffmpeg` and `bin/ffprobe`.
- **Verification**: `scripts/run_gates.py` 8/8 green; full `pytest` **3220 passed, empty warnings summary**;
  `pytest tests/test_build_exe.py tests/test_check_runtime_pins.py` → 105 passed; `check_runtime_pins.py --strict`
  went rc=1 → **rc=0**, announcing the two macOS slots as "signature mode" rather than "pinned"; all five mutations
  reddened (gate omits the new mode / SEV-2221 reverted / marker alone satisfies / `bin/` layout hardcoded /
  missing binary no longer aborts).
- **Not yet verified, handed back**: ① the direct `github.com/.../releases/download/...` link resets on this box, so
  "download in full and compare against the pin" can only be proven by the first GitHub runner run; ② evermeet
  verification on the real build path executes for the first time in the macOS CI job (the keyserver probe shows
  `--recv-keys` will resolve, but no local gpg run happened); ③ the Linux full zip grows sharply with the source
  switch, and `report_bundle_size.py` could not be run locally (no Linux, blocked direct link) — re-check the size
  gate from CI artefacts before adjusting any threshold. A rolling alias pins *who signed*, not *which version*: a
  new evermeet build flows through without reddening the gate. That is this mode's inherent boundary; the logged
  observed SHA256 is what makes it auditable afterwards.

### v4.3.0-dev (2026-09-26) — CI typecheck gate: install a pinned pytest and fix the `[return]` false positive in `tests/test_proto_runtime_compat.py`, removing the "green locally, red in CI" coverage drift (CI / test-only change, zero runtime impact)

- **Background**: the CI `typecheck` job reported `tests/test_proto_runtime_compat.py:33: error: Missing return statement  [return]` (checked 159 files), while a local `mypy` run was fully green on 158 files and could not reproduce it at all.
- **Root cause**: that job installs only `requirements.txt + mypy` — **no pytest** — so `import pytest` resolves to `Any`, the `NoReturn` annotation of `pytest.fail()` is lost, and mypy concludes that `_declared_protobuf_specifier() -> str` may fall off the end. This is an environment difference, not a code defect; the same cause also meant that every `pytest.*` in `tests/` (fixtures / `MonkeyPatch` / `raises`) was previously **unchecked** — the gate was effectively half-blind. Local reproduction: `mypy --no-site-packages` (hides installed packages and reproduces the exact error; the 5 extra `no-any-return` reports in that mode are over-stripping noise).
- **Nature of change**: CI workflow + one test helper + `AGENTS.md` only. `src/`, `main.py`, `gui.py`, `web.py`, `web/app.js`, `requirements.txt` / `pyproject.toml` untouched; no dependency added or removed (pytest is installed only inside the typecheck job, never into the runtime list).

**Files touched (grouped by module)**:

> Inventory moved verbatim to [docs/agent-reference/changelog-file-inventories-en.md](docs/agent-reference/changelog-file-inventories-en.md) (entry: v4.3.0-dev (2026-09-26) — CI typecheck gate: install a pinned pytest and fix the `[return]` false positive in `tests/test_proto_runtime_compat.py`, removing the "green locally, red in CI" coverage drift (CI / test-only change, zero runtime impact) | section: Files touched (grouped by module)).

**Verification**: `mypy` (no args) and `mypy --platform linux` both succeed on 158 files (local pytest is 9.1.1, the same version CI now pins); under `mypy --no-site-packages` the original `[return]` is gone and only the 5 stripping-noise reports remain; `basedpyright tests/test_proto_runtime_compat.py` reports 0 errors / 0 warnings / 0 notes; `black --check` unchanged; `pytest tests/test_proto_runtime_compat.py` → 4 passed; `yaml.safe_load` parses `ci.yml` with the expected outputs / steps; line endings of the edited files are unchanged (`ci.yml` pure LF; `AGENTS.md` and the test file pure CRLF).

**Leftover observation**: that CI run reported `checked 159 source files` while the local count under `[tool.mypy].files` is 158 `.py` files — one unaccounted file (likely an extra file on the commit of that run), unrelated to this fix.

### v4.3.0-dev (2026-09-26) — Repo metadata & doc sync: aligned the dependency tables / structure trees / egg-info / ignore lists and cleaned up leftover records of the deleted `weverse_auth` module (metadata & docs only, zero runtime code change)

- **Background**: a full-repo read-through cross-checking the four shared-source families (version / dependencies / structure trees / ignore lists) surfaced several stale spots: the `CODE_WIKI*.md` dependency tables still listed only 16 entries with `starlette` lower bound `>=0.49.1`; the structure trees still listed `src/weverse_auth.py` and `tests/test_weverse_auth.py`, both deleted on 2026-09-23; `DouyinLiveRecorder.egg-info/requires.txt` was missing `h2`/`socksio` (added 2026-09-23); `AGENTS.md` still said "21 runtime dependencies".
- **Nature of change**: docs / metadata / ignore lists only, plus a regenerated `egg-info`. `src/`, `main.py`, `gui.py`, `web.py` and `web/app.js` untouched; the runtime dependency set is unchanged (23 entries on each side, identical package-name sets).

**Files touched (grouped by module)**:

> Inventory moved verbatim to [docs/agent-reference/changelog-file-inventories-en.md](docs/agent-reference/changelog-file-inventories-en.md) (entry: v4.3.0-dev (2026-09-26) — Repo metadata & doc sync: aligned the dependency tables / structure trees / egg-info / ignore lists and cleaned up leftover records of the deleted `weverse_auth` module (metadata & docs only, zero runtime code change) | section: Files touched (grouped by module)).

**Verification**: `scripts/check_version.py` rc=0 (`pyproject.toml` is the single source of truth; all four consumers read it dynamically); `scripts/check_runtime_pins.py` rc=0; `pytest tests/test_regression_2026_09_22_gates.py tests/test_build_exe.py` all green (including the "requirements.txt and pyproject package-name sets are equal" lock); `pytest tests/test_i18n.py tests/test_i18n_migration.py tests/test_i18n_tr.py tests/test_frontend_*.py` 56 passed; `node --test tests/frontend/*.mjs` green.

**Handed back to the user (needs a decision)**: `config/config.ini` currently has `禁用SSL证书验证的平台(逗号分隔) = 虎牙直播,B站直播,抖音直播`, while the code's enforced set `main.SSL_DISABLE_REQUIRED_PLATFORMS` contains only `虎牙直播` / `B站直播` and the README default is the same two. The extra `抖音直播` entry is a legacy exemption that disables certificate verification for Douyin streams; whether to remove it is left to the user — this pass did not touch a security-relevant toggle on its own.

### Earlier entries (archived)

164 day-by-day development entries from 2026-05-17 to 2026-09-24 were moved verbatim to [code-wiki-history-en.md](docs/changelog/code-wiki-history-en.md) on 2026-09-28; that volume also restores the short `…` / mid-sentence tails left by the previous trimming pass against the `.workbuddy/docold` baseline (exact rule in its header).
Reason: the changelog alone took 72.9% of this file's characters (472,669 of 648,535). The root document now keeps only the current release window plus this pointer, which is what makes the rest of the document readable.
