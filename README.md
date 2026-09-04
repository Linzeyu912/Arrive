# 抵达 / Arrive

> 让混乱的思考，准确抵达。<br>
> Help tangled thoughts arrive intact.

[中文](#中文介绍) · [English](#english-introduction)

## 中文介绍

世界有多少人，就有多少种内在语言。

我们脑中的想法通常不是完整的句子，而是片段、感受、记忆、矛盾、联想，以及一些自己能够隐约感觉、却暂时说不清楚的东西。当它们需要被表达时，我们很容易把“还没想清楚”误认为“没有想法”，也可能在追求流畅和漂亮的过程中，丢掉真正想说的内容。

**抵达（Arrive）** 是一个帮助人们表达复杂思考的开放框架。它先接住未经整理的思绪，再通过镜像确认、关系梳理、语义校准和接收端验证，把只有本人能够隐约理解的“内在语言”，转化为他人可以理解、而本人仍然认得的表达。

抵达不替你决定应该想什么，也不把所有人的声音改造成同一种标准语言。它追求的不是文辞漂亮，而是表达忠实；不是快速生成，而是减少思想在传递过程中的失真。

一句话描述：

> 帮助人们把零碎、混乱、矛盾的内在思考，整理成准确、可理解且仍保留本人声音的表达。

### 它如何工作

```text
混乱思绪 → 编码（当前重点）→ 共享语义表示 → 传递 → 解码（后续开发）→ 接收者理解
```

编码先回答“我究竟想传递什么”。它把私人、零碎的内在表示整理成可确认的结构，并尽可能连接到有来源、被广泛认可的共享解释；表达者自己的特殊含义和不同意见仍会单独保留。解码再回答“怎样让这个具体的人理解”，根据接收者的知识背景、概念习惯和思路选择词汇、顺序、例子与语境。

一份表达需要同时通过两项检查：

1. **本人仍然认得**：整理后的内容没有替换、简化或背叛原本的想法；
2. **对方能够理解**：接收者有机会准确复述表达者真正想传达的内容。

矛盾、犹豫和没有答案的部分不必被强行消除。准确表达复杂性，本身就是一种清晰。

### 它可以产生什么

抵达不限定最终形式。输出可以是：

- 一段重要对话的表达准备；
- 一封难以写出的信；
- 一篇文章或观点说明；
- 一份用于做决定的思考记录；
- 一段个人经历的准确叙述；
- 一部长期形成的自传式思想作品。

个人经历和长文是这个项目的第一批验证样本，但不是项目本身。

## English introduction

There are as many inner languages as there are people in the world.

Thought rarely begins as polished sentences. It appears as fragments, feelings, memories, contradictions, associations, and meanings we can sense before we can explain them. When we try to communicate too quickly, we may mistake “not yet articulated” for “having nothing to say.” We may also produce fluent language that no longer carries what we actually meant.

**Arrive** is an open framework for expressing complex thought. It receives unstructured thinking first, then uses mirror confirmation, relationship mapping, semantic calibration, and audience-side verification to translate a private inner language into an expression another person can understand—and its author can still recognize as their own.

Arrive does not decide what you should think or standardize every person into the same voice. Its priority is not polished prose but faithful expression; not instant generation but reducing distortion as thought moves from one mind to another.

In one sentence:

> Arrive helps people turn fragmented, tangled, and contradictory thoughts into clear, understandable expression without losing their own voice.

### How it works

```text
Tangled thoughts → Encoding (current focus) → shared semantic representation
                 → transmission → Decoding (planned) → receiver understanding
```

Encoding first answers, “What does the sender actually mean?” It turns private fragments into a confirmable structure and links concepts to sourced, broadly shared interpretations where possible, while preserving personal meanings and disagreements separately. Decoding then asks, “How can this particular receiver understand it accurately?” and adapts vocabulary, order, examples, and context to the receiver’s knowledge and reasoning path.

Every expression is evaluated from both ends:

1. **Self-recognition**: the author still recognizes the result as what they meant;
2. **Audience comprehension**: the receiver can accurately restate what the author intended to communicate.

Contradiction, uncertainty, and open questions do not need to be erased. Expressing complexity accurately is itself a form of clarity.

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
    └── 观点回应.md
```

## 开始使用 / Getting started

先在软件仓库之外建立数据目录，并通过 `ARRIVE_DATA_DIR` 指向它。可以直接输入一段未经整理的想法；也可以导入外部来源后，针对全文或具体句段写下它触发的思考。来源原文与个人批注分开保存，个人素材经过镜像确认后再进入思考地图。当前这部分是人工协作与空白模板流程；来源快照、定位批注和镜像确认 API 属于下一纵向开发切片。

```text
继续收集，不要急着替我总结。

我脑中现在有这些互相缠绕的想法……
```

Create a data directory outside the software repository and point `ARRIVE_DATA_DIR` to it. You can enter an unedited thought directly, or import an external source and annotate the whole work or a specific passage with the thought it triggered. Source content and personal annotations remain separate, and personal material enters a thought map only after mirror confirmation. This is currently a human-guided, template-based workflow; source snapshots, anchored annotations, and mirror-confirmation APIs are the next vertical slice.

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

项目目前处于 `v0.x`，开发重点是编码闭环。当前纵向切片先实现直接输入、来源定位批注、完整时间记录与镜像确认；语义澄清继续讨论，之后再定义稳定的共享语义表示。传递层只先定义契约，接收者解码留待后续开发。

Arrive is currently at `v0.x`, focused on the encoding loop. The next vertical slice covers direct input, source-anchored annotations, complete timestamps, and mirror confirmation. Semantic clarification remains under discussion; stable shared-semantic encoding follows it. Transmission is currently a contract boundary, and receiver-specific decoding comes later.

开发进度、里程碑和后续顺序见 [开发进度与后续规划](./docs/路线图.md)。See the [development roadmap](./docs/路线图.md) for current status and upcoming milestones.

## 后端 MVP / Backend MVP

仓库已经包含一个可运行的 FastAPI 后端，把素材、来源命题、个人命题、观点回应时间线和思考地图落实为数据库实体与 REST API。这是编码系统的数据基础；编码任务、共享语义锚点和编码版本仍在下一阶段。

The repository includes a runnable FastAPI backend for materials, attributed source propositions, personal propositions, time-indexed responses, and thought maps. This is the data foundation for encoding; encoding tasks, shared semantic anchors, and encoding revisions are the next milestone.

```powershell
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn arrive.main:app --reload
```

启动后打开 `http://127.0.0.1:8000/docs`。详细说明见 [Backend README](./backend/README.md) 和 [后端架构](./docs/后端架构.md)。

## 隐私 / Privacy

软件与数据采用物理隔离。GitHub 仓库只保存代码、通用规范、空白模板和完全虚构的测试数据；使用者原话、外部来源记录、分析、时间线、草稿、成品、数据库及其他运行产物统一保存在仓库外的 `ARRIVE_DATA_DIR`。`shareable` 不等于允许提交到 GitHub，发布必须经过独立确认。完整规则见 [软件与数据隔离规范](./docs/软件与数据隔离规范.md)。

Software and user data are physically separated. GitHub contains only code, generic protocols, blank templates, and fully synthetic test fixtures. Raw thoughts, source records, analyses, timelines, drafts, finished personal work, databases, and all other runtime artifacts live in an external `ARRIVE_DATA_DIR`. A `shareable` label never authorizes a Git commit; publication requires a separate explicit decision. See the [software/data separation policy](./docs/软件与数据隔离规范.md).

## 项目边界 / Boundaries

抵达是一套表达与理解框架，不是心理诊断、医疗建议、法律意见或事实裁决工具。它可以帮助一个人更准确地陈述自己的观察和感受，但不能仅凭单方叙述推断他人的内心、意图或人格。

Arrive is a framework for expression and understanding—not psychological diagnosis, medical advice, legal advice, or factual adjudication. It can help someone state their own observations and feelings accurately, but it must not infer another person's inner state, intent, or personality from a one-sided account.
