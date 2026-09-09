# 抵达 / Arrive

[![Data boundary](https://github.com/Linzeyu912/Arrive/actions/workflows/data-boundary.yml/badge.svg)](https://github.com/Linzeyu912/Arrive/actions/workflows/data-boundary.yml)
[![React](https://img.shields.io/badge/React-18.3-61dafb?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646cff?logo=vite)](https://vite.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178c6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2-d71f00?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003b57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> 让混乱的思考，准确抵达。<br>
> Help tangled thoughts arrive intact.

[中文](#中文介绍) · [English](#english-introduction)

## 中文介绍

世界有多少人，就有多少种内在语言。

我们脑中的想法通常不是完整的句子，而是片段、感受、记忆、矛盾、联想，以及一些自己能够隐约感觉、却暂时说不清楚的东西。当它们需要被表达时，我们很容易把“还没想清楚”误认为“没有想法”，也可能在追求流畅和漂亮的过程中，丢掉真正想说的内容。

**抵达（Arrive）** 是一个帮助人们表达复杂思考的开放框架。它先接住未经整理的思绪，再通过镜像确认、按需歧义检查、关键词语义确认、关系梳理和接收端验证，把只有本人能够隐约理解的“内在语言”，转化为他人可以理解、而本人仍然认得的表达。

抵达不替你决定应该想什么，也不把所有人的声音改造成同一种标准语言。它追求的不是文辞漂亮，而是表达忠实；不是快速生成，而是减少思想在传递过程中的失真。

一句话描述：

> 帮助人们把零碎、混乱、矛盾的内在思考，整理成准确、可理解且仍保留本人声音的表达。

### 理论基础与设计主线

Arrive 以通信中的“编码—传递—解码”过程作为基础设计框架，而不只是借用三个模块名称。人与人交流的形式可以自然、轻松，工具内部仍需要明确：信息从哪里产生、怎样形成表达、经过什么通道，以及接收者怎样重建含义。我们的目标是让底层机制严谨，让使用过程不生硬。

这里需要区分理论的适用范围：[香农的通信理论](https://www.nokia.com/bell-labs/publications-and-media/publications/a-mathematical-theory-of-communication/)研究消息的可靠传输，并不直接解决语义理解。Arrive 借鉴通信过程的结构，再结合[共同理解与沟通校准研究](./docs/research/README.md#ref-0003-grounding-in-communication)，处理个人含义、语境差异和反馈。因此，本项目的语义编码与解码不是对通信工程中信源编码、信道编码算法的直接实现，也不宣称人际沟通与信号传输完全等同。

| 环节 | Arrive 要解决的问题 | 设计约束 |
| --- | --- | --- |
| 编码：第一重点 | 怎样把零碎想法组织成忠实、可解释的表达 | 原话留存、镜像确认、关键词语义确认；不替用户决定含义 |
| 传递：基础保障 | 怎样让已确认内容经过通道后仍完整、可追溯 | 保留版本、来源与语境；内容送达不等于被理解 |
| 解码：第二重点，后续开发 | 怎样帮助具体接收者准确理解 | 结合自愿提供的背景与理解习惯，不篡改已确认含义 |
| 反馈：校准机制 | 怎样发现遗漏或误解，并回到相关环节修正 | 表达者确认与接收者复述分别验证；理解不等于赞同 |

歧义、背景差异和遗漏是需要检查的失真来源，但不把情绪、个体差异或不同意见简单当作应被消除的“噪声”。也不把镜像确认等同于已经具备数学保证的纠错编码。

### 它如何工作

```text
混乱思绪 → 编码（当前重点）→ 共享语义表示 → 传递 → 解码（后续开发）→ 接收者理解
```

编码先回答“我究竟想传递什么”：保留个人含义，用可解释的公共语言表达；没有共识的地方明确说明差异。编码是第一重点，解码其次。解码再回答“怎样让这个具体的人理解”，根据接收者的知识背景、概念习惯和思路选择词汇、顺序、例子与语境；后续支持接收者自愿提供画像。

镜像确认用于校准整段意思；关键词语义确认用于校准会改变命题或关系的关键用词。用户可以确认单一含义、多义、个人定义或明确保留未知，系统不替用户裁定唯一正确解释。

一份表达需要同时通过两项检查：

1. **本人仍然认得**：整理后的内容没有替换、简化或背叛原本的想法；
2. **对方能够理解**：接收者有机会准确复述表达者真正想传达的内容。

矛盾、犹豫和没有答案的部分不必被强行消除。准确表达复杂性，本身就是一种清晰。

### 文献怎样服务于产品

公共文献有两项用途：首先指导实际设计，帮助我们判断该解决什么问题、采用什么方法、怎样检验是否有用；其次用于项目介绍与对外传播，让读者能追溯设计依据，而不是只看到功能口号。

每项研究应关联具体设计选择，并说明证据范围与局限。[研究依据目录](./docs/research/README.md)区分理论基础、交互研究与工程标准。我们可以说“设计参考了相关理论与研究”，但不能仅凭引用就声称“Arrive 已被科学验证”。工具自身的有效性还需要通过忠实度、接收者理解和使用负担等实际评估建立；论文作者也不因此为本项目背书。

### 它可以产生什么

抵达不限定最终形式。输出可以是：

- 一段重要对话的表达准备；
- 一封难以写出的信；
- 一篇文章或观点说明；
- 一份用于做决定的思考记录；
- 一段个人经历的准确叙述；
- 一部长期形成的自传式思想作品。

个人经历和长文是这个项目的第一批验证样本，但不是项目本身。

## 录入后自动转换与留存（Docling）

后端会在录入时自动保存原始内容并创建持久化处理任务：网页来源自动抓取，本地文件自动提取 Markdown，直接输入的文本保存为 Markdown。后台调用 [Docling](https://github.com/docling-project/docling) 的精简 Python 转换模块，不接入其服务或界面，用户无需点击转换按钮。

安装后端即包含转换依赖：`python -m pip install -e ./backend`。原件、Markdown 和定位 JSON 都保存在 Git 忽略的 `ARRIVE_DATA_DIR`；失败不丢弃录入内容，程序重启恢复中断任务。接口、保存结构及限制见 [自动录入归一化指南](./docs/外部作品归档.md)。

验证状态：合成 HTML 已跑通“接口录入 → 自动处理 → Markdown 读取”，中文 Word 转换及纯文本保存已验证。本机文字 PDF 与中文扫描 PDF/OCR 已通过合成样本自动录入验收，包括 Markdown、页码定位和原件校验；此前 DLL 阻塞本次不再复现（BE-010）。复杂版面准确性尚未专项验收；Docker 容器运行待验证。

## Windows 双击启动（本机）

双击项目根目录的 **[启动Arrive.cmd](./启动Arrive.cmd)**。启动器会自动启动前后端并打开浏览器，不需要手动打开两个终端。保留“抵达 · Arrive”小窗口；点击“停止并退出”或关闭该窗口，即可停止本次启动的服务。

本机依赖已经安装。启动器使用 `backend/.venv` 和 `frontend/node_modules`；迁移到新电脑后需先按前后端 README 安装依赖。端口被占用时会显示提示，不会关闭其他程序。日志保存在数据根的 `logs/launcher/`，不会进入 Git。

## Docker 一键运行

安装并启动 Docker（含 Compose v2）后，无需单独安装 Node、Python 或数据库：

```sh
git clone https://github.com/Linzeyu912/Arrive.git
cd Arrive
docker compose up --build -d --wait
```

打开 [http://127.0.0.1:8080](http://127.0.0.1:8080)。首次需要联网构建；前后端依赖及基础镜像均已锁定。数据默认保存在项目内被 Git 忽略的 `arrive-data/`，停止或重建容器不会删除该目录。

配置已完成，当前本机 Docker 引擎不可用，容器构建与联调尚待验收。详细安装前提、升级备份、旧命名卷迁移及排障见 [Docker 运行指南](./docs/Docker运行指南.md)。当前服务仅供本地或受控环境使用。

## 技术栈

前端通过 REST API 连接现有 Python 后端，业务规则与持久化由后端负责。

| 层次 | 当前使用 | 用途 |
| --- | --- | --- |
| 前端界面 | React 18.3、React Router 6、TypeScript（strict） | 页面、导航与类型检查 |
| 前端构建与样式 | Vite 6、原生 CSS / CSS 变量、npm | 开发代理、构建、视觉样式与依赖管理 |
| 后端 API | Python 3.12+、FastAPI、Pydantic 2、Uvicorn | HTTP 接口、输入校验与本地服务 |
| 数据与迁移 | SQLAlchemy 2、SQLite、Alembic | 持久化与版本化数据库迁移 |
| 测试 | Pytest、Vitest、Testing Library、Playwright | 后端测试、前端测试与浏览器验收 |
| 运行与检查 | Docker Compose、GitHub Actions | 可选容器运行、提交后的数据边界检查 |

顶部技术徽章是静态说明，具体依赖范围与锁定版本以 [前端配置](./frontend/package.json)、[前端锁文件](./frontend/package-lock.json) 和 [后端配置](./backend/pyproject.toml) 为准。Data boundary 徽章显示数据边界工作流状态，不代表前后端全部测试已经在 CI 中通过。

安装与运行见 [前端 README](./frontend/README.md) 和 [后端 README](./backend/README.md)；当前能力、已知问题与验证范围见 [开发交接](./docs/开发进度与模型交接.md)。

## English introduction

There are as many inner languages as there are people in the world.

Thought rarely begins as polished sentences. It appears as fragments, feelings, memories, contradictions, associations, and meanings we can sense before we can explain them. When we try to communicate too quickly, we may mistake “not yet articulated” for “having nothing to say.” We may also produce fluent language that no longer carries what we actually meant.

**Arrive** is an open framework for expressing complex thought. It receives unstructured thinking first, then uses mirror confirmation, on-demand ambiguity checks, key-term meaning confirmation, relationship mapping, and audience-side verification to translate a private inner language into an expression another person can understand—and its author can still recognize as their own.

Arrive does not decide what you should think or standardize every person into the same voice. Its priority is not polished prose but faithful expression; not instant generation but reducing distortion as thought moves from one mind to another.

In one sentence:

> Arrive helps people turn fragmented, tangled, and contradictory thoughts into clear, understandable expression without losing their own voice.

### Theoretical foundations and design rationale

Arrive uses encoding, transmission, and decoding as a foundational process model, not merely as names for software modules. Everyday conversation can feel natural while the underlying design remains explicit about where information originates, how it becomes an expression, how it travels, and how a receiver reconstructs its meaning. Rigorous foundations should support a lightweight experience.

[Shannon’s communication theory](https://www.nokia.com/bell-labs/publications-and-media/publications/a-mathematical-theory-of-communication/) addresses reliable message transmission, not semantic understanding itself. Arrive draws on that process structure and complements it with [research on grounding in communication](./docs/research/README.md#ref-0003-grounding-in-communication) to address personal meaning, context, and feedback. Our semantic encoding and decoding are not direct implementations of source or channel coding algorithms, nor a claim that human communication is identical to signal transmission.

| Stage | Product question | Design constraint |
| --- | --- | --- |
| Encoding: first priority | How can fragmented thoughts become faithful, explainable expression? | Preserve inputs and confirm interpretations and key meanings with the author |
| Transmission: foundational support | How can confirmed content travel intact and remain traceable? | Preserve versions, provenance, and context; delivery is not understanding |
| Decoding: second priority, planned | How can a particular receiver understand accurately? | Use voluntarily provided context without changing confirmed meaning |
| Feedback: calibration | How can omissions and misunderstandings be identified and repaired? | Check author intent and receiver restatement separately; understanding is not agreement |

Ambiguity, missing context, and omissions are possible sources of distortion. Emotions and differing viewpoints are not simply “noise” to remove, and mirror confirmation is not a mathematically guaranteed error-correcting code.

### How it works

```text
Tangled thoughts → Encoding (current focus) → shared semantic representation
                 → transmission → Decoding (planned) → receiver understanding
```

Encoding first answers, “What does the sender actually mean?” It preserves personal meaning in explainable public language and makes differences explicit where no consensus exists. Encoding is the first priority, followed by decoding. Decoding asks, “How can this particular receiver understand it accurately?” and adapts vocabulary, order, examples, and context to the receiver’s knowledge and reasoning path. Voluntary receiver-provided profiles are planned for this later stage.

Mirror confirmation calibrates the overall message; key-term confirmation calibrates words whose interpretation would change a proposition or relation. A user may confirm one meaning, multiple meanings, a personal definition, or an explicit unknown—the system does not declare one universally correct reading on the user’s behalf.

Every expression is evaluated from both ends:

1. **Self-recognition**: the author still recognizes the result as what they meant;
2. **Audience comprehension**: the receiver can accurately restate what the author intended to communicate.

Contradiction, uncertainty, and open questions do not need to be erased. Expressing complexity accurately is itself a form of clarity.

### How research serves the product

Public literature serves two purposes: first, guiding practical decisions about problems, methods, and evaluation; second, making the rationale traceable in project introductions and public communication.

The [research directory](./docs/research/README.md) distinguishes theoretical foundations, interaction studies, and engineering standards, linking them to design choices and limitations. “Informed by research” does not mean “Arrive has been scientifically validated.” Product effectiveness must be established through evaluations of fidelity, receiver understanding, and user effort. Citation does not imply endorsement by the cited authors.

### What it can produce

Arrive is output-agnostic. It can help create:

- preparation for an important conversation;
- a difficult letter or message;
- an essay or position statement;
- a structured record for decision-making;
- a faithful account of personal experience;
- a long-form autobiographical work of thought.

Personal experience and long-form writing are the project's first validation cases, not its definition.

---

## 核心原则 / Core principles

- **忠实先于漂亮 / Fidelity before polish**
- **澄清而不替代 / Clarify, do not replace**
- **保留复杂性 / Preserve complexity**
- **共享语义但不伪造共识 / Shared semantics without false consensus**
- **表达面向真实接收者 / Design for a real audience**
- **在表达两端校准 / Validate at both ends**

## 仓库结构 / Repository structure

```text
.
├── README.md
├── AGENTS.md
├── 思考转译协作机制.md
├── 长文写作协作机制.md
├── docs/
│   ├── 项目愿景.md
│   ├── 思考转译框架.md
│   ├── 软件与数据隔离规范.md
│   ├── 数据目录规范.md
│   ├── 外部来源管理规范.md
│   ├── 观点回应时间线规范.md
│   └── 路线图.md
├── backend/                # API、领域模型与数据库迁移 / backend software
├── scripts/                # 工程边界检查 / repository safeguards
└── templates/
    ├── 思绪采集.md
    ├── 表达任务.md
    ├── 思考地图.md
    ├── 转译校准.md
    ├── 长文结构.md
    ├── 外部来源.md
    ├── 来源快照.md
    ├── 镜像确认.md
    ├── 关键词语义确认.md
    └── 观点回应.md
```

## 开始使用 / Getting started

先在软件仓库之外建立数据目录，并通过 `ARRIVE_DATA_DIR` 指向它。可以直接输入一段未经整理的想法；也可以导入外部来源后，针对全文或具体句段写下它触发的思考。来源原文与个人批注分开保存；个人素材经过镜像确认后可作为证据进入思考地图，依赖关键词的概念与命题还需要完成语义确认。当前这部分是人工协作与空白模板流程；相应 API 属于后续纵向开发切片。

```text
继续收集，不要急着替我总结。

我脑中现在有这些互相缠绕的想法……
```

Create a data directory outside the software repository and point `ARRIVE_DATA_DIR` to it. You can enter an unedited thought directly, or import an external source and annotate the whole work or a specific passage with the thought it triggered. Source content and personal annotations remain separate. Mirror-confirmed personal material may enter a thought map as evidence; concepts and propositions that depend on key terms still require meaning confirmation. This is currently a human-guided, template-based workflow, with the corresponding APIs planned as later vertical slices.

```text
Keep collecting. Do not summarize me yet.

These are the thoughts currently tangled together in my mind...
```

每个新克隆执行一次 `git config core.hooksPath .githooks`，启用提交前的数据边界检查；也可以随时运行 `python scripts/check_data_boundary.py`。CI 会在 push 和 pull request 时重复检查。

For every new clone, run `git config core.hooksPath .githooks` once to enable the pre-commit data-boundary check. You can also run `python scripts/check_data_boundary.py` directly; CI repeats the check on pushes and pull requests.

核心协作流程见 [思考转译协作机制](./思考转译协作机制.md)。长文是其中一种特殊输出模式，见 [长文写作协作机制](./长文写作协作机制.md)。

网络文章、书籍、视频等外部思想材料按 [外部来源管理规范](./docs/外部来源管理规范.md) 登记、保存快照、定位批注和分类。原文、使用者批注、原作者观点与使用者认同分别记录，避免引用关系失真。

所有“喜欢、认同、采用或不再认同”都进入 [观点回应时间线](./docs/观点回应时间线规范.md)，并保留发生时间。项目不使用最新结论覆盖过去的自己。

See [思考转译协作机制](./思考转译协作机制.md) for the core workflow. Long-form writing is one specialized output mode, documented in [长文写作协作机制](./长文写作协作机制.md).

Web articles, books, videos, and other external material are registered, snapshotted when permitted, annotated with stable anchors, and classified according to the [external source protocol](./docs/外部来源管理规范.md). Source content, user annotations, author claims, and user endorsement remain distinct.

Every reaction—resonance, agreement, adoption, or later disagreement—is recorded in a [time-indexed response history](./docs/观点回应时间线规范.md). The project never overwrites a past self with the latest conclusion.

## 当前阶段 / Current stage

项目目前处于 `v0.x`，开发重点是编码闭环。当前纵向切片先实现直接输入、来源定位批注、完整时间记录与镜像确认；随后实现已经确认的按需歧义检查与关键词语义确认，再定义稳定的共享语义表示。传递层只先定义契约，接收者解码留待后续开发。

Arrive is currently at `v0.x`, focused on the encoding loop. The next vertical slice covers direct input, source-anchored annotations, complete timestamps, and mirror confirmation. The confirmed on-demand ambiguity and key-term semantics slice follows, before stable shared-semantic encoding. Transmission is currently a contract boundary, and receiver-specific decoding comes later.

开发进度、里程碑和后续顺序见 [开发进度与后续规划](./docs/路线图.md)。See the [development roadmap](./docs/路线图.md) for current status and upcoming milestones.

## 后端 MVP / Backend MVP

仓库已经包含一个可运行的 FastAPI 后端，把素材、来源命题、个人命题、观点回应时间线和思考地图落实为数据库实体与 REST API。这是编码系统的数据基础；来源快照、定位批注、镜像确认、关键词语义确认和编码版本 API 尚待后续切片实现。

第一期前端已实现记录、素材、来源和观点页面，主要流程已通过真实后端联调；草稿保护仍有待修问题。运行方式、接口对应和验收记录见 [前端 README](./frontend/README.md)。

跨模型接手请先阅读 [开发进度与模型交接](./docs/开发进度与模型交接.md)，其中按前端、后端记录已完成内容、已知问题、验证依据与下一步。

The repository includes a runnable FastAPI backend for materials, attributed source propositions, personal propositions, time-indexed responses, and thought maps. This is the data foundation for encoding; source snapshots, anchored annotations, mirror confirmation, key-term semantics, and encoding-revision APIs remain planned work.

```powershell
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn arrive.main:app --reload
```

启动后打开 `http://127.0.0.1:8000/docs`。详细说明见 [Backend README](./backend/README.md) 和 [后端架构](./docs/后端架构.md)。

## 隐私 / Privacy

本地个人部署默认将整个数据根放在克隆目录内、由 Git 整体忽略的 `arrive-data/`，其中保存全部运行数据：当前结构化加工结果在其中的 SQLite，后续附件、草稿与导出使用同一数据根。启动自动建立数据目录和忽略文件；Docker 同样默认挂载该目录到容器 `/data`。不同克隆需要独立数据时，请分别指定 `ARRIVE_DATA_DIR`。目录分开和 Git 忽略不等于加密或备份，详情见 [本地部署与数据说明](./backend/README.md#本地个人部署的数据归属)。

软件与个人数据采用目录分离和 Git 跟踪隔离。GitHub 仓库保存代码、项目框架、指导方法、[公共研究依据](./docs/research/README.md)、空白模板和完全虚构的测试数据；用户个人原话、阅读批注、分析、时间线、草稿、成品、真实测试数据与运行数据库统一保存在不进入 Git 的 `ARRIVE_DATA_DIR`。公共文献可以收录链接与原创摘要，全文副本须有再分发许可。个人数据的 `shareable` 不等于允许提交到 GitHub。完整规则见 [软件与数据隔离规范](./docs/软件与数据隔离规范.md)。

The repository includes software, the framework, methods, and [public research references](./docs/research/README.md). Personal inputs, annotations, derived outputs, and real user test data remain outside Git. Third-party full texts are bundled only where redistribution is permitted; otherwise we provide links and original summaries.

Software and user data are physically separated. Personal source records, analyses, timelines, drafts, finished personal work, databases, and other runtime artifacts live in an external `ARRIVE_DATA_DIR`. A `shareable` label never authorizes a Git commit; publishing personal content requires a separate explicit decision. See the [software/data separation policy](./docs/软件与数据隔离规范.md).

## 项目边界 / Boundaries

本地运行后，首页自动读取数据库中的已保存记录；后端启动时适配旧来源文件，并在“本地档案”保留旧文件原件。配置、支持格式与限制见 [本地数据库与旧文件适配](./docs/本地数据库与旧文件适配.md)。

抵达是一套表达与理解框架，不是心理诊断、医疗建议、法律意见或事实裁决工具。它可以帮助一个人更准确地陈述自己的观察和感受，但不能仅凭单方叙述推断他人的内心、意图或人格。

Arrive is a framework for expression and understanding—not psychological diagnosis, medical advice, legal advice, or factual adjudication. It can help someone state their own observations and feelings accurately, but it must not infer another person's inner state, intent, or personality from a one-sided account.
