# 抵达 / ARRIVE

> 让混乱的思考，准确抵达。<br>
> Help tangled thoughts arrive intact.

[中文](#中文介绍) · [English](#english-introduction)

## 中文介绍

世界有多少人，就有多少种内在语言。

我们脑中的想法通常不是完整的句子，而是片段、感受、记忆、矛盾、联想，以及一些自己能够隐约感觉、却暂时说不清楚的东西。当它们需要被表达时，我们很容易把“还没想清楚”误认为“没有想法”，也可能在追求流畅和漂亮的过程中，丢掉真正想说的内容。

**抵达（ARRIVE）** 是一个帮助人们表达复杂思考的开放框架。它先接住未经整理的思绪，再通过多轮澄清、关系梳理、语义校准和接收端验证，把只有本人能够隐约理解的“内在语言”，转化为他人可以理解、而本人仍然认得的表达。

抵达不替你决定应该想什么，也不把所有人的声音改造成同一种标准语言。它追求的不是文辞漂亮，而是表达忠实；不是快速生成，而是减少思想在传递过程中的失真。

一句话描述：

> 帮助人们把零碎、混乱、矛盾的内在思考，整理成准确、可理解且仍保留本人声音的表达。

### 它如何工作

```text
混乱思绪 → 忠实采集 → 语义澄清 → 思考建模 → 面向对方转译 → 双向校准 → 表达成品
```

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

**ARRIVE** is an open framework for expressing complex thought. It receives unstructured thinking first, then uses iterative clarification, relationship mapping, semantic calibration, and audience-side verification to translate a private inner language into an expression another person can understand—and its author can still recognize as their own.

ARRIVE does not decide what you should think or standardize every person into the same voice. Its priority is not polished prose but faithful expression; not instant generation but reducing distortion as thought moves from one mind to another.

In one sentence:

> ARRIVE helps people turn fragmented, tangled, and contradictory thoughts into clear, understandable expression without losing their own voice.

### How it works

```text
Tangled thoughts → faithful capture → clarification → thought mapping
                 → audience-aware translation → two-way calibration → expression
```

Every expression is evaluated from both ends:

1. **Self-recognition**: the author still recognizes the result as what they meant;
2. **Audience comprehension**: the receiver can accurately restate what the author intended to communicate.

Contradiction, uncertainty, and open questions do not need to be erased. Expressing complexity accurately is itself a form of clarity.

### What it can produce

ARRIVE is output-agnostic. It can help create:

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
│   └── 路线图.md
├── content/
│   ├── inbox/              # 未经整理的思绪 / raw thought dumps
│   ├── samples/            # 用于验证框架的样本 / validation samples
│   ├── maps/               # 思考地图 / thought maps
│   ├── responses/          # 带时间的观点回应 / time-indexed responses
│   └── decisions/          # 项目决定时间线 / project decisions
├── sources/                 # 外部思想来源 / external sources
├── outputs/                # 表达成品 / expression outputs
└── templates/
    ├── 思绪采集.md
    ├── 表达任务.md
    ├── 思考地图.md
    ├── 转译校准.md
    ├── 长文结构.md
    ├── 外部来源.md
    └── 观点回应.md
```

## 开始使用 / Getting started

最简单的开始方式，是把一段未经整理的思绪放入 `content/inbox/`，或者直接说：

```text
继续收集，不要急着替我总结。

我脑中现在有这些互相缠绕的想法……
```

Start by placing an unedited thought dump in `content/inbox/`, or simply say:

```text
Keep collecting. Do not summarize me yet.

These are the thoughts currently tangled together in my mind...
```

核心协作流程见 [思考转译协作机制](./思考转译协作机制.md)。长文是其中一种特殊输出模式，见 [长文写作协作机制](./长文写作协作机制.md)。

网络文章、书籍、视频等外部思想材料按 [外部来源管理规范](./sources/README.md) 登记、分类和摘要。原作者观点与使用者认同分别记录，避免引用关系失真。

所有“喜欢、认同、采用或不再认同”都进入 [观点回应时间线](./content/responses/README.md)，并保留发生时间。项目不使用最新结论覆盖过去的自己。

See [思考转译协作机制](./思考转译协作机制.md) for the core workflow. Long-form writing is one specialized output mode, documented in [长文写作协作机制](./长文写作协作机制.md).

Web articles, books, videos, and other external material are registered, classified, and summarized according to the [external source protocol](./sources/README.md). An author's claims and a user's endorsement are recorded separately to preserve attribution.

Every reaction—resonance, agreement, adoption, or later disagreement—is recorded in a [time-indexed response history](./content/responses/README.md). The project never overwrites a past self with the latest conclusion.

## 当前阶段 / Current stage

项目目前处于 `v0.x`：使用作者自己的真实思绪作为第一套样本，验证哪些澄清和转译方法确实能够减少表达失真。

ARRIVE is currently at `v0.x`: using the author's real thoughts as its first validation set to discover which clarification and translation methods genuinely reduce distortion.

## 隐私 / Privacy

仓库当前按私有项目管理。`content/private/` 已被 Git 忽略，适合存放不应上传的高敏感原始材料。即使仓库是私有的，也不要提交密码、令牌、证件、精确住址或未经同意的第三方敏感信息。

The repository is currently private. `content/private/` is excluded from Git and should be used for highly sensitive raw material that must not be uploaded. Never commit credentials, identity documents, precise addresses, or sensitive third-party information without consent.

## 项目边界 / Boundaries

抵达是一套表达与理解框架，不是心理诊断、医疗建议、法律意见或事实裁决工具。它可以帮助一个人更准确地陈述自己的观察和感受，但不能仅凭单方叙述推断他人的内心、意图或人格。

ARRIVE is a framework for expression and understanding—not psychological diagnosis, medical advice, legal advice, or factual adjudication. It can help someone state their own observations and feelings accurately, but it must not infer another person's inner state, intent, or personality from a one-sided account.
