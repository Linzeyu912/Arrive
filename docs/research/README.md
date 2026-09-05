# 研究依据与方法借鉴

本目录公开 Arrive 的研究参考与设计理由，不包含用户个人数据、阅读立场或测试记录。研究说明“为什么值得尝试”，不等于证明 Arrive 的整体路线有效。

核查日期：2026-09-05。文献使用独立的 `REF-NNNN` 编号；项目设计解释与原研究结果分别描述。

| 编号 | 来源 | 对应方法 | 留存方式 |
| --- | --- | --- | --- |
| REF-0001 | [Critical Inker](#ref-0001-critical-inker) | 延迟反馈、主动解释、逐项展开 | 官方链接、摘要、CC BY 4.0 全文副本 |
| REF-0002 | [SpeakSoftly](#ref-0002-speaksoftly) | 沟通支持与介入时机 | 官方链接、摘要；未取得全文再分发许可 |
| REF-0003 | [Grounding in Communication](#ref-0003-grounding-in-communication) | 情境中的共同理解与校准 | 官方作者链接、摘要；不内置全文 |
| REF-0004 | [Web Annotation Data Model](#ref-0004-web-annotation-data-model) | 原文与批注分离、定位标准 | 标准链接及设计说明 |
| REF-0005 | [A Mathematical Theory of Communication](#ref-0005-a-mathematical-theory-of-communication) | 通信过程、可靠传输与理论边界 | 官方来源链接与原创评述 |

## 文献的用途与证据层次

实用优先：研究需要帮助确定项目问题、设计方法或评估方式，不为增加引用数量而收录。对外传播时，公开这些依据可帮助读者审查项目思路，但不能把引用数量、学者或机构声望当成产品有效性的证明。

- 理论基础：REF-0005 提供通信问题的基础视角，REF-0003 补充人际共同理解与反馈。
- 交互研究：REF-0001、REF-0002 提供可试验的方法与场景经验，外推时保留研究局限。
- 工程标准：REF-0004 规范批注表示，不是沟通效果的实验证据。
- 产品证据：Arrive 自身仍需检验忠实度、理解准确性和使用负担，不以以上文献替代产品评估。

公开介绍采用“研究内容 → 项目借鉴 → 尚需验证”的结构，不暗示作者背书，不将局部研究结论包装成整体产品验证。

## REF-0001 Critical Inker

- 标题：Critical Inker: Scaffolding Critical Thinking in AI-Assisted Writing Through Socratic Questioning。
- 作者：Philipp Hugenroth、Valdemar Danry、Pattie Maes。
- 版本：arXiv:2604.07167v1，2026-04-08。
- 来源：[论文及许可标记](https://arxiv.org/html/2604.07167v1)、[官方 PDF](https://arxiv.org/pdf/2604.07167v1)。
- 内置副本：[PDF](./papers/critical-inker-2604.07167v1.pdf)；许可与文件信息见 [第三方文献说明](./THIRD_PARTY_NOTICES.md)。

研究内容：面向论证写作，比较可视化反馈与苏格拉底式对话。设计包括写作完成后分析、让用户主动解释、针对具体论证提问及逐项展示。论文包含技术评估和小规模初步试点。

项目借鉴：完整表达后再围绕原句澄清，允许用户纠正和解释，而非仅点击认可。这是方法迁移，不把情感表达变成逻辑测试，也不假定模型一定正确。研究不能直接证明个人表达确认机制的长期效果。

## REF-0002 SpeakSoftly

- 标题：SpeakSoftly: Scaffolding Nonviolent Communication in Intimate Relationships through LLM-Powered Just-In-Time Interventions。
- 作者：Ka I Chan、Hongbo Lan、Jun Fang、Yuntao Wang、Yuanchun Shi。
- 版本：arXiv:2604.05382v1，2026-04-07。
- 来源：[书目](https://arxiv.org/abs/2604.05382v1)、[正文](https://arxiv.org/html/2604.05382v1)、[官方 PDF](https://arxiv.org/pdf/2604.05382v1)。

研究内容：以非暴力沟通原则支持伴侣文字冲突，比较不同深度和语气的改写提示、感受与需要引导。正文第 5.1 节区分模拟阶段 31 名参与者与真实生活阶段 14 名参与者（7 对伴侣），不能把摘要的整体样本口径当成全部完成真实场景测试的规模。

项目借鉴：后续解码可以探索不同程度的表达支持，并评估介入时机与认知负担。不能把推断的需要当成用户事实，也不要求全部表达采用固定温和模板。小样本、特定关系情境和探索性研究限制外推。

版权状态：页面标记 arXiv perpetual non-exclusive license，未取得允许本项目再分发全文的明确许可，因此仓库只收录原创摘要和官方链接，不上传 PDF。公开访问不等于可以重新托管，参见 [arXiv 再利用说明](https://info.arxiv.org/help/license/reuse.html)。

## REF-0003 Grounding in Communication

- 作者：Herbert H. Clark、Susan E. Brennan。
- 年份：1991。
- 来源：[作者所在学校托管的论文](https://web.stanford.edu/~clark/1990s/Clark,%20H.H.%20_%20Brennan,%20S.E.%20_Grounding%20in%20communication_%201991.pdf)。

理论内容：共同理解依赖交流中的反馈与协调，理解标准与当前目的和媒介相关。

项目借鉴：保留编码—传递—解码框架，同时把个人含义、公共语言与差异说明并列保存；不假设公共词义自动保证理解。镜像与后续接收者复述是项目的校准选择，不是该理论对具体软件的效果认证。全文再分发许可未核实，本仓库不内置副本。

## REF-0004 Web Annotation Data Model

- 发布机构：W3C；W3C Recommendation，2017-02-23。
- 来源：[正式标准](https://www.w3.org/TR/annotation-model/)。

标准内容：用批注主体与目标表达注释关系，并提供文本引文、位置等选择器。

项目采用方向：将用户批注与外部原文分离，引用精确原句与上下文，同时另加 Arrive 的不可变快照和哈希。标准不负责判断用户是否共鸣或认同，也不提供网页永久归档保证。当前仅确认建模方向，尚未完成兼容实现；不复制标准全文。

## REF-0005 A Mathematical Theory of Communication

- 作者：Claude E. Shannon。
- 年份：1948；发表于 Bell System Technical Journal。
- 来源：[Nokia Bell Labs 官方文献页](https://www.nokia.com/bell-labs/publications-and-media/publications/a-mathematical-theory-of-communication/)。

理论范围：研究在通信中准确或近似重现消息的问题，讨论信道噪声等因素；原文明确将语义方面排除在其所处理的工程问题之外。

项目借鉴：用编码、传递和解码明确职责，区分内容完整与含义理解。个人含义的确认和接收者理解，需要另行结合语义与人际沟通研究。不能从香农理论直接推出镜像确认的效果，也不能在尚未定义可操作指标时将“语义失真”说成已有数学量化保证。

留存：官方链接与原创评述；全文再分发许可未核实，不内置副本。

## 收录要求

新增资料说明作者、版本、来源、研究结果、项目推论和局限。公共资料不携带用户实例编号、个人批注、设备路径或测试记录。第三方全文仅在许可核实后收录，并保留原许可；论文许可不自动等于其代码许可。未内置的论文仍可以通过官方链接直接阅读。
