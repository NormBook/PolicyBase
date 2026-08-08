# PolicyBase 文献分类与 TYPE 体系

> 状态：主权威
> 分卷编号：PolicyBase_05
> 主题：taxonomy
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 本卷定位与非职责边界

本卷是 v3 candidate 内「分类树 / TYPE 决定层 / 完整分类树 / TYPE 前缀表 / 完整性与一致性约束 / 公文文种 / 行文方向 / 概念重叠」的唯一 owner。回答一份文献属于哪个 `System -> Hierarchy -> Subtype -> Form` 分类位置、使用哪个 3 位 TYPE 前缀、公文文种与行文方向如何独立记录、概念重叠时如何确定主分类。

非本卷职责（一句引用，不展开）：

- frontmatter 字段下限、`edition_kind`、`spatial_scope`、`validity`、`subjects[]` 等元数据：见 PolicyBase_06。
- `doc_id` / DOC_ID 生成语义、canonical 形态、Layer/Tier、归一化、碰撞算法：见 PolicyBase_07。TYPE 前缀表是 DOC_ID 前缀生成输入，本卷只定义前缀本身，不定义拼接算法。
- `classification_level` 枚举与密级 sensitivity 维度：见 PolicyBase_04 §classification；本卷 `classification.system` 字段消费该枚举。
- `disclosure.mode` 完整枚举（`proactive/upon_request/not_disclosable/unknown`）：owner 是 PolicyBase_04，本卷只定义 `classification.system = disclosure` 的分类语义并在约束表中引用。
- 采集来源 URL、采集流程、附件清单：见 PolicyBase_10 / PolicyBase_11。
- 内容生产状态机、OCR/layout/精修状态、版次与 edition 文件权威：见 PolicyBase_13 / PolicyBase_09。

分类描述文献的法源 / 载体性质，不描述抓取批次、附件格式、OCR 状态、排版质量或内容 edition。处理与版本事实分别由 PolicyBase_09 / PolicyBase_13 / PolicyBase_14 承载，不得新增 subtype 伪装处理状态。

## 2. 权威与历史来源

本卷是 v3 candidate 内分类与 TYPE 的唯一 owner。历史 `v1/v2 种子`只解释规则来源，内容已不可恢复，不能作为上位契约、冲突裁判或实施锚点。规则必须由本卷正文、机器 schema 和 golden 自足表达；发现疑似遗漏走 Decision 修订本卷，不得引用不可核验的旧章节补规则。

## 3. 冲突规则与硬性解释

冲突处理顺序：

1. 按 PolicyBase_01 的跨卷冲突规则与主权威地图裁决。
2. 本卷正文与机器 schema / golden 不一致时，停止实施并通过 Decision 同步修正，不能让任一方静默覆盖另一方。
3. 历史来源只作 provenance，不参与优先级。
4. 本卷不得未经 Decision 新增 TYPE。

硬性解释（卷内自洽基线）：

1. `PRC` 固定表示 `process`，即过程性文献层；`PRC` 不是党内法规。
2. 党内法规使用 `PCH/PPC/PRT/PRU`。

> 第 4 条 / 第 14 条约束表 / 第 19 条不变量对 `PRC = process` 的语义做一致性表述；本卷不再于其他章节重申。

## 4. 迁移目标

本卷最终拆入以下机器权威：

| 文件 | 内容 |
|------|------|
| `data/taxonomy/classification_tree.yaml` | 分类树、文种、subtype 受控词 |
| `data/taxonomy/type_prefix_map.yaml` | TYPE 推导映射 |
| `docs/data/data-dictionary.md` | 人类可读定义 |
| `tests/golden/classification/`（待落地） | 分类树覆盖样例 |
| `tests/golden/type_prefix/`（待落地） | TYPE 推导与拒绝样例 |

## 5. 基本模型

PolicyBase 使用四层分类树：

```text
Layer 1: System    法源体系
Layer 2: Hierarchy 法源层级
Layer 3: Subtype   法源子类
Layer 4: Form      公文文种
```

独立维度（不进入分类树，与 TYPE 正交）：

```text
direction
classification_level
urgency
disclosure.mode
validity.status
```

核心原则：

1. `System -> Hierarchy -> Subtype` 构成嵌套分类树。
2. `Form`、行文方向、密级、紧急程度、公开方式与生命周期是正交维度，不决定 TYPE。
3. TYPE 用于物理分桶、ID 前缀与检索入口；TYPE 不等于完整分类。
4. 精细类别以 subtype 与独立维度为权威。

§7 中出现在 subtype 之下的更深缩进（如 `local_regulation -> provincial`、`treaty -> bilateral`）只是说明性分组，不构成第五层，也不是当前可持久化枚举。正式数据只能把 Layer 3 父节点写入 `subtype`；更深叶子不得写入正式文献包，直至维护者通过 schema Issue 为其确定独立维度或新的 subtype 字面量。实现不得把同名叶子（例如不同父节点下的 `provincial`）直接写入 `subtype`。

## 6. TYPE 前缀决定层

校验器必须按下表推导 TYPE。

| system | TYPE 决定层 | hierarchy 规则 |
|--------|-------------|----------------|
| `state_law` | `hierarchy` | 必填 |
| `party_regulation` | `subtype` | 可为空 |
| `judicial` | `subtype` | 可为空 |
| `disclosure` | `system` | 必须省略或为 null |
| `process` | `system` | 必须省略或为 null |
| `military_law` | system 或完整映射 | 可为空 |
| `international_law` | system 或完整映射 | 可为空 |
| `administrative_decision` | system 或完整映射 | 可为空 |
| `auxiliary` | `subtype` | 可为空 |

普通三层体系缺 `hierarchy` 必须失败；明确允许空 `hierarchy` 的体系不得因此失败。`disclosure` 与 `process` 是简化两层模型，`hierarchy` 不参与 TYPE 推导。

## 7. 完整分类树

包含 9 个 system、20 个 TYPE、完整 subtype 枚举与 orthogonal dimensions。

```text
state_law
  constitution [CON]
    constitution
    constitutional_interpretation
  law [LAW]
    basic_law
    non_basic_law
    legislative_interpretation
  npc_decision [DEC]
    npc_resolution
    npcsc_decision
    authorization_decision
  regulation [REG]
    administrative_regulation
    supervisory_regulation
    local_regulation
      provincial
      municipal
      autonomous_prefecture
    sez_regulation
      traditional_sez
      pudong
      hainan_ftp
    autonomous_regulation
  rule [RUL]
    department_rule
    local_government_rule
      provincial
      municipal
  normative [NOR]
    administrative_normative
    joint_party_state_normative
    judicial_normative
  policy [POL]
    general_policy

disclosure [DIS]
  budget_disclosure
  validity_registry
  statistical_publication
  audit_publication
  work_report
  other_disclosure

process [PRC]
  draft
  review_report
  legislative_bill
  consultation_feedback

party_regulation
  party_charter [PCH]
  party_principle [PPC]
  party_regulation [PRT]
  party_rule [PRU]

military_law [MIL]
  military_regulation
  military_rule
  military_normative

international_law [TRE]
  treaty
    multilateral
    bilateral
  agreement
  protocol
  exchange_of_notes
  joint_declaration
  mou

judicial
  judicial_interpretation [JUD]
    spc_interpretation
    spp_interpretation
  guiding_case [CAS]
    spc_case
    spp_case
  gazette_case [CAS]

administrative_decision [ADM]
  antitrust_decision
  trade_remedy_determination
  administrative_review_decision
  administrative_licensing_decision
  administrative_penalty_decision
  administrative_coercion_decision

auxiliary
  interpretation_document [INT]
  service_guide [SVC]
```

## 8. state_law 体系

`state_law` 是国家法体系，必须填写 `hierarchy`，由 `hierarchy` 决定 TYPE。

| hierarchy | TYPE | 中文 |
|-----------|------|------|
| `constitution` | CON | 宪法层 |
| `law` | LAW | 法律层 |
| `npc_decision` | DEC | 人大决定层 |
| `regulation` | REG | 法规层 |
| `rule` | RUL | 规章层 |
| `normative` | NOR | 规范性文件层 |
| `policy` | POL | 政策文件层 |

`constitution` 包括宪法、宪法修正案与宪法解释；`law` 包括基本法律、非基本法律与法律解释；`regulation` 包括行政法规、监察法规、地方性法规、经济特区法规、自治条例与单行条例。`rule` 包括部门规章与地方政府规章；`normative` 包括行政规范性文件、党政联合规范性文件与司法规范性文件。

## 9. disclosure 与 process 体系

`disclosure` 是法定公开载体层，TYPE 为 `DIS`。subtype 包括 `budget_disclosure`、`validity_registry`、`statistical_publication`、`audit_publication`、`work_report`、`other_disclosure`。`disclosure` 只用于便利分桶与检索面分组，不替代 `disclosure.mode`（枚举 owner 为 PolicyBase_04）。

`process` 是过程性记录层，TYPE 为 `PRC`，固定表示过程性文献，不是党内法规。subtype 包括 `draft`、`review_report`、`legislative_bill`、`consultation_feedback`，只表示立法、制定、审议、征求意见或反馈过程中的记录文献。

`disclosure` 与 `process` 的 `hierarchy` 不参与 TYPE 推导；其与 `disclosure.mode`、`validity.status` 的组合约束见 §14。

## 10. party_regulation 体系

`party_regulation` 是党内法规体系，TYPE 由 subtype 决定；党内法规不得使用 `PRC`。

| subtype | TYPE | 中文 | 效力序 |
|---------|------|------|--------|
| `party_charter` | PCH | 党章 | 1 |
| `party_principle` | PPC | 准则 | 2 |
| `party_regulation` | PRT | 条例 | 3 |
| `party_rule` | PRU | 规定、办法、规则、细则 | 4 |

党内法规效力序只在 `party_regulation` 体系内有效。跨体系不得用该效力序比较国家法、军事法、司法解释或国际法。党政联合规范性文件若属于国家法规范性文件层，主分类使用 `state_law / normative / joint_party_state_normative`，TYPE 为 `NOR`。

> 本轮范围说明：党务仅保留 TYPE，并受 PolicyBase_04「主动公开入口门」与密级 / 敏感性 fail-closed 约束。党务来源矩阵留后续阶段。

## 11. 其他体系

`military_law` 共用 `MIL`，subtype 包括 `military_regulation`、`military_rule`、`military_normative`。军事法公开版适用 PolicyBase_04 主动公开入口门与密级拦截；涉密内容由密级门 fail-closed 拦截。

`international_law` 共用 `TRE`，subtype 包括 `treaty`、`agreement`、`protocol`、`exchange_of_notes`、`joint_declaration`、`mou`；`treaty` 可细分为 `multilateral` 与 `bilateral`。

`judicial` 按 subtype 决定 TYPE：`judicial_interpretation` 使用 `JUD`，`guiding_case` 与 `gazette_case` 使用 `CAS`；`judicial_interpretation` 可细分为 `spc_interpretation` 与 `spp_interpretation`，`guiding_case` 可细分为 `spc_case` 与 `spp_case`。

`administrative_decision` 共用 `ADM`，subtype 包括 `antitrust_decision`、`trade_remedy_determination`、`administrative_review_decision`、`administrative_licensing_decision`、`administrative_penalty_decision`、`administrative_coercion_decision`。

`auxiliary` 包括 `interpretation_document [INT]` 与 `service_guide [SVC]`。

共用 TYPE 的体系中，TYPE 只负责分桶；精细分类以 subtype 为权威。

> 本轮范围说明：军事（`MIL`）仅保留 TYPE。军事来源矩阵留后续阶段。国防 / 安全作为 PolicyBase_06 `subjects[]` 主题标签，地域适用范围使用 PolicyBase_06 `spatial_scope`；公开法律归入 `flk` 法规库（`LAW/REG`），涉密由密级门拦截。

## 12. TYPE 前缀表（20）

PolicyBase v3 固定使用 20 个 TYPE：

| TYPE | 类别 |
|------|------|
| CON | 宪法层 |
| LAW | 法律层 |
| DEC | 人大决定层 |
| REG | 法规层 |
| RUL | 规章层 |
| NOR | 规范性文件层 |
| POL | 政策文件层 |
| DIS | 法定公开载体层 |
| PRC | 过程性文献层 |
| PCH | 党章 |
| PPC | 准则 |
| PRT | 党内法规条例 |
| PRU | 党内规定、办法、规则、细则 |
| MIL | 军事法 |
| TRE | 国际法 |
| JUD | 司法解释 |
| CAS | 指导案例与公报案例 |
| ADM | 行政决定 |
| INT | 解读文献 |
| SVC | 服务文献 |

本表是 DOC_ID 前缀生成输入（生成语义与拼接算法见 PolicyBase_07）。本表不得扩展为 21 个或更多 TYPE，除非先通过 Decision 修改本卷、机器映射与 golden，并完成迁移评审。

## 13. TYPE 完整性约束

TYPE 映射的机器权威是分类树中的 `[TYPE]` 标记（§7）、TYPE 前缀决定层规则（§6）与 `data/taxonomy/type_prefix_map.yaml`；说明文字不得作为唯一机器权威。schema 与 golden 必须覆盖每个 Layer 3 subtype。

校验必须保证：

1. 每个 subtype 恰好映射到一个 3 位 TYPE。
2. `DIS` 与 `PRC` 的 `hierarchy` 不参与 TYPE 推导。
3. `PRC` 只对应 `process`。
4. 党内法规只使用 `PCH/PPC/PRT/PRU`。
5. 司法体系不得用空泛 system 级前缀覆盖 subtype 级前缀。
6. `MIL/TRE/ADM` 等共用 TYPE 时，精细分类仍以 subtype 为权威。

## 14. 分类一致性约束

`classification.system` 与正交维度组合时，下列情况必须拒绝（schema violation，拒绝入库）：

| 编号 | 拒绝条件 | 触及的硬性解释 |
|------|----------|----------------|
| C1 | `classification.system = process` 且 `validity.status = effective` | `PRC = process`，过程性文献不得为生效 |
| C2 | `classification.system = disclosure` 且 `disclosure.mode = not_disclosable` | disclosure 体系语义与公开方式冲突 |
| C3 | `classification.system = state_law` 但缺少 `hierarchy` | state_law 由 hierarchy 决定 TYPE |
| C4 | `classification.system = disclosure` 但填写非空 `hierarchy` | disclosure 是两层模型 |
| C5 | `classification.system = process` 但填写非空 `hierarchy` | process 是两层模型 |
| C6 | `classification.system = party_regulation` 但 TYPE 不是 `PCH/PPC/PRT/PRU` | 党内法规 TYPE 受限 |
| C7 | `TYPE = PRC` 但 `classification.system` 不是 `process` | `PRC` 固定表示 `process` |

`disclosure.mode` 完整枚举（`proactive/upon_request/not_disclosable/unknown`）owner 为 PolicyBase_04；本约束表只引用其语义做组合校验，不重列枚举。采集边界可以比 schema 更严格；schema 通过不等于可以发布。

## 15. 公文文种

公文文种是 Layer 4 `Form`，独立于 `System`、`Hierarchy`、`Subtype`，不决定 TYPE。

官方 15 种：

```text
决议, 决定, 命令(令), 公报, 公告, 通告, 意见,
通知, 通报, 报告, 请示, 批复, 议案, 函, 纪要
```

法规类扩展：

```text
条例, 规定, 办法, 细则, 规则, 通则, 规范
```

实践扩展：

```text
说明, 报表, 目录, 清单, 白皮书, 指南, 方案, 公约, 路线图
```

文种记录文本形式，不替代法源分类。例如「条例」可能是行政法规、地方性法规或党内法规条例；「通知」可能发布规范性文件、政策文件或服务指南。分类不得只凭标题中的文种词作最终判断。

## 16. 行文方向

行文方向是独立维度，不决定 TYPE。

| direction | 对应文种 | 场景 |
|-----------|----------|------|
| `downward` | 决议、决定、命令、通知、通报、批复、纪要 | 上级到下级 |
| `upward` | 报告、请示、议案 | 下级到上级 |
| `parallel` | 函 | 不相隶属机关之间 |
| `public` | 公报、公告、通告 | 面向全社会 |
| `flexible` | 意见 | 多方向 |

方向判断应结合文种、发文主体、受文对象与发布语境。单独根据文种推断方向只能作为候选。同一文种存在特殊语境时，允许使用不同于默认方向的 direction，但必须可解释。

## 17. 概念重叠规则

概念重叠时，主分类必须稳定、可解释、可复核。

| 场景 | 处理方式 |
|------|----------|
| 印发通知与被印发文件各有独立文号 | 两份独立文献，用 `publishes` 关系连接 |
| 印发通知与被印发内容共享文号 | 一份文献，正文中分区记录 |
| 转发或批转 | 转发件与被转发件是两份独立文献，用 `forwards` 关系连接 |
| 党政联合发文 | `issuers[]` 多值，必要时记录党字文号与政字文号 |
| 同时是规范性文件与政策文件 | `classification.hierarchy` 取法源最高者，其余进入 `type_tags[]` |
| 修正 vs 修订 | 按修改决定的具体条款判断原文状态 |

印发、转发、批转优先看文号与文本独立性：各有独立文号时原则上是两份文献；共享文号且同一发布载体不可拆分时原则上是一份文献。规范性文件与政策文件重叠时，主分类优先保留法源效力较高的 hierarchy。修正与修订不得只按标题词判断，应以条款效果判断原文是否继续有效、部分有效、被替代或废止。

### 17.1 文献、版本与处理结果的分类边界

1. 来源网页内容变化、OCR 重跑、排版精修与人工纠错通常产生同一 `doc_id` 的新 edition，不改变 classification。
2. 法律意义上的修订、修正决定、新文号或独立制定文本是否构成新文献，先按 PolicyBase_07 / PolicyBase_08 做身份判断；分类树本身不授权覆盖旧文献。
3. `draft`、正式文本、审议报告之间若是独立文献，分别入库并用关系连接；不得把过程性文献当成正式文本的 edition。
4. 扫描 PDF、网页正文、附件 PDF 是载体或 manifestation，不是 subtype。
5. OCR / layout / model 状态不得写入 `classification`、`type_tags[]` 或 `document_form`；其权威在 PolicyBase_13 内容管线与 PolicyBase_09 manifest。

## 18. 迁移验收下限

落地时至少验证：

1. 每个 system 有 golden 样例。
2. 每个 state_law hierarchy 有 golden 样例。
3. 每个 subtype 有 TYPE 推导样例。
4. `PRC = process` 有正向样例。
5. 党内法规使用 `PCH/PPC/PRT/PRU` 有正向样例。
6. 党内法规误用 `PRC` 有拒绝样例。
7. `disclosure` 与 `process` 非空 `hierarchy` 有拒绝样例。
8. `state_law` 缺少 `hierarchy` 有拒绝样例。
9. `process` 文献标为 `effective` 有拒绝样例。
10. `disclosure` 文献标为 `not_disclosable` 有拒绝样例。

本卷只规定验收行为，不绑定具体 CLI 参数（CLI 入口见 PolicyBase_15 ~ PolicyBase_19）。

## 19. 本卷不变量

后续实现不得破坏：

1. 分类模型是 `System -> Hierarchy -> Subtype -> Form`。
2. 公文文种与行文方向是独立维度，不决定 TYPE。
3. `state_law` 的 TYPE 由 `hierarchy` 决定。
4. `disclosure` 的 TYPE 是 `DIS`。
5. `process` 的 TYPE 是 `PRC`；`PRC` 固定表示 `process`，不是党内法规。
6. 党内法规使用 `PCH/PPC/PRT/PRU`。
7. 共用 TYPE 的体系中，精细类别以 subtype 为权威。
8. 分类树与独立维度冲突时，必须拒绝入库（约束见 §14）。
9. 概念重叠时，主分类与辅助标签必须稳定、可解释、可复核。
10. 分类与 immutable edition 正交；内容处理或版次变化不得伪造新分类。
