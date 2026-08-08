# PolicyBase 去重、更新判断与入库

> 状态：主权威
> 分卷编号：PolicyBase_08
> 主题：dedup
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷是 PolicyBase 文献同一性判断、来源更新判断、多源组合、**身份层 reviewed decision**、ingest 重验、内容指纹与外部导入的唯一 owner。

本卷必须分别回答三个问题，**不得用一个 `merge` 同时回答三者**：

1. 是同一文献还是另一文献？（身份层）
2. 是重复 observation、同文献新 edition，还是身份不明？（更新层）
3. 哪些字段/正文可以从多个来源组合？（内容层）

owner 主题（本卷完整展开）：

- §4 Issuer 前置门；
- §5 Tier 用途表（**Tier/canonical key 由 PolicyBase_07 计算，本卷只定义用途**）；
- §6 observation 更新状态机（`no_change/create_edition/create_document/manual_review_hold`）；
- §7 内容指纹算法（`whitespace-stripped-unicode15.1-prefix128-sha256-v1`）；
- §8 别名与历史 ID 用途；
- §9 身份层 reviewed decision（4 值：`merge/keep_separate/mark_identity_alias/manual_review_hold`）；
- §10 多源组合；
- §11 Ingest 流程（重验）；
- §13 Hash 碰撞锁与单一 migration batch（算法引 PolicyBase_07）；
- §14 外部导入。

非 owner 主题（一句引用，不展开）：

- ID、canonical key、Tier 0-5 字段序列、碰撞 ID 算法、identity registry generation、alias、availability、`registry_entry_semantic_hash` 见 PolicyBase_07。
- `edition_kind` 元数据语义、frontmatter 字段、validity 见 PolicyBase_06。
- edition identity、`switch_kind`、manifest、原子创建与切换、`normalized_lf_markdown_body`、operations 枚举见 PolicyBase_09。
- 内容生产状态机、内容工件 schema、内容层 review decision 见 PolicyBase_13（本卷 §9 只 owner 身份层 decision，与内容层 decision 是两个互不混用的 decision 类型，本卷不复制其枚举）。
- `action enum`（9 动作）+ DAG 见 PolicyBase_04 §action-enum。
- CLI 入口（`source/scrape/import/prepare`、`--decisions` 绑定）见 PolicyBase_17；命令词法、AUTH_ID scope 路由见 PolicyBase_15。
- 索引投影、`record_hash`、freshness gate 见 PolicyBase_14。
- 诊断码全集、退出码、解析早拒绝序见 PolicyBase_19。

## 2. 迁移目标

| 目标 | 内容 |
|---|---|
| `docs/specs/dedup-ingest.md` | 人类可读合同 |
| `data/schemas/dedup_decision.schema.json` | 身份层 decision、证据、动作 |
| `data/schemas/observation-update.schema.json` | observation 更新状态机输入/输出 |
| `data/schemas/content-fingerprint.schema.json` | 内容指纹算法版本与输入约束 |
| `src/policybase/pipeline/dedup/` | 候选生成、issuer 门、Tier 用途、observation 比较、组合 |
| `src/policybase/pipeline/importers/` | update/ingest/edition 编排 |
| `tests/golden/dedup/` | 同一、分离、更新、hold、组合、碰撞、外部导入 |

## 3. 术语

| 术语 | 含义 |
|---|---|
| `candidate` | 尚未成为正式 edition 的采集/导入记录。 |
| `observation` | 某来源、URL、时间点的原始响应及内容 hash（schema 见 PolicyBase_09 `_sources.yaml`）。 |
| `document` | `doc_id` 标识的文献（身份 owner PolicyBase_07）。 |
| `edition` | 同一 doc 的不可变确认快照（owner PolicyBase_09）。 |
| `duplicate candidate` | 机器证据提示可能与已有 doc 同一、但尚未裁决的候选。 |
| `candidate basis` | 机器证据集合，**不等于授权**；任一新 basis 必须先经 Decision 落入 schema。 |
| `reviewed decision` | 身份层受控人工决定（§9，4 值）；与内容层 review decision（PolicyBase_13）区分。 |

初始 candidate basis 集合（新增 basis 须经 Decision）：

```text
canonical_key_equal
document_number_alias_hit
content_fingerprint_equal
source_url_equal
source_observation_equal
identity_field_changed
forwarding_link
historical_id_hit
```

## 4. Issuer 前置门

任一条件成立，**禁止自动同一/合并**：

- primary issuer 未解析、命中 99 域或 `issuer_unresolved=true`（99 域算法见 PolicyBase_07 §issuer-unresolved-99）；
- 两个已解析 primary issuer 不同；
- raw primary issuer name 不同且无注册别名证据；
- 多个同优先级 issuer 命中无法唯一确定。

issuer 门失败仍可生成 `duplicate candidate`，但**不得**覆盖正文、元数据或 current。source priority、文号、标题或内容相似**均不能**绕过 issuer 门。不同机关的预决算、年报、指南、贯彻件和转载**默认是独立文献**。

issuer 门与 PolicyBase_07 P1-P5 机关解析、`primary_issuer_org_id` 16 位格式是同一身份链的前后两段：解析由 PolicyBase_07 owner，本卷只 owner「解析结果是否允许自动同一」的判定门。

## 5. Tier 用途表

**Tier/canonical key 由 PolicyBase_07 计算，本卷只定义用途**——本卷不重定义 Tier 字段序列、Tier 选择规则或 `id_quality`，只规定每个 Tier 命中在本卷去重/更新判定中的法律后果。

| 证据（Tier 由 PolicyBase_07 计算） | 结果 |
|---|---|
| issuer gate 通过且 Tier 0/1/2 canonical key 相同 | 自动同一 document，可继续 §6 更新判断 |
| Tier 3 canonical key 相同 | `duplicate candidate`，须 §9 review |
| Tier 4 canonical key 相同 | 强 `duplicate candidate`，须 §9 review |
| Tier 5 canonical URL 相同 | 只证明同一来源地址，进入 §6 observation 比较 |
| Tier 不同但文号/别名/历史 ID 强相关 | `duplicate candidate`，须 §9 review |
| issuer gate 失败 | `duplicate candidate`，须 §9 review |

Tier 4（raw 机关名 + 规范标题 + 日期）**不能区分**正文、转载、修订稿与配套件，因此**禁止**自动同一。Tier 5 canonical URL 可复用或内容漂移，**禁止**单独授权文献合并；同 URL 只触发 observation 比较，不触发身份合并。

## 6. Observation 与更新状态机

来源刷新先按 PolicyBase_09 `_sources.yaml` schema 计算 versioned observation hash，覆盖允许保存的 raw bytes，或在不能保存 raw 时覆盖响应语义摘要、关键字段与正文 hash。比较后动作固定为 4 值：

```text
no_change
create_edition
create_document
manual_review_hold
```

该状态机是「同一 document 内时间维度的更新判断」，与 §9 身份层 reviewed decision 是**两个正交 decision 类型**：§6 在「身份已确定同一」的前提下回答「这次刷新要不要建新 edition」；§9 在「身份未确定」时回答「两个 doc 是否合并」。两者不得混用、不得同时取值。

### 6.1 no_change

同 source/URL 的 observation hash 已存在。只更新 run/checkpoint/`last_seen` 等非正式运行事实（写入 acquisition ledger 或本包 `audit/` immutable event，见 PolicyBase_09 §audit-events）；**不创建 edition**，**不修改 current**，不伪造 operation。

### 6.2 create_edition

身份仍属于同一 doc，但存在可解释变化：来源正文/元数据/有效性更新、新增更权威载体、人工纠错、脱敏或 reprocess。创建何种 edition 由 PolicyBase_06 `edition_kind` 表达、由 PolicyBase_09 `switch_kind` 切换落地；本卷只决定「需要建 edition」。

### 6.3 create_document

独立文号、独立制定主体、独立文本、来源明确宣告新修订/新发布，或法律语义证明是另一文献时，按 PolicyBase_07 重新执行身份计算与完整去重，**stage 新 `doc_id` package 并发布 identity registry generation**。**不得**在旧 doc 下用 edition 偷换身份。

### 6.4 manual_review_hold

身份字段冲突、来源只给模糊「更新」、标题复用、正文变化无法解释，或更新会影响人工确认字段时，current 保持不变并进入 §9 review 队列。`hold` **不允许**正式写入或覆盖 current。

### 6.5 决策记录

每次 §6 决策必须记录：old/new observation hash、current edition、身份字段 diff、正文 diff 摘要、basis、evidence、actor/tool、time。记录载体为 candidate 工作区与（成功时）edition manifest `operations[]`（owner PolicyBase_09），本卷不复制其 schema。

## 7. 内容指纹

内容指纹**只用于候选召回，不自动合并**。

算法 version 固定为 `whitespace-stripped-unicode15.1-prefix128-sha256-v1`：

```text
sha256(first_128_unicode_scalars(remove_unicode_white_space(body)).encode("utf-8"))
```

`remove_unicode_white_space` 删除 Unicode 类别 `Separator`（Zs/Zl/Zp）与 ASCII 空白（`\t\n\r\f\v `），不做 NFC、不做繁简转换、不做形近字映射——确定性投影而非内容规整。`first_128_unicode_scalars` 按 Unicode scalar value 序取前 128 个，不按字节截断。

不可信输入**不得**作为指纹输入：

- 空/模板正文；
- 未确认 OCR/layout/model 输出（确认链见 PolicyBase_13）；
- 未授权全文（外传授权见 PolicyBase_09 §external-transfer-authorization）。

相同指纹**只生成 `duplicate candidate`**，仍须 §4 issuer 门与 §9 review；不同指纹**也不能否定**同一文献（同文献可有不同排版/OCR/脱敏版本）。

## 8. 别名与历史 ID 用途

文号别名、旧系统 ID、PolicyBase_07 identity registry alias、Tier 5 升级记录用于**候选召回或重定向**，**不直接写** `relations[].alias_of`——`alias_of` 不是业务关系枚举；`relations[]` 字段与关系类型受控枚举的 owner 是 PolicyBase_06 §10，本卷只 owner `alias_of` 的身份层语义。

别名命中且 issuer/identity 证据闭合时，可支持 §5 Tier 0-2 自动同一判断；**只有别名时必须 review**。identity alias、两个已入库 doc 的正式合并、survivor 选择必须形成 §9 `reviewed decision`，再按 PolicyBase_07 §identity-migration 发布 identity migration batch；旧包和旧 edition 不改写。

## 9. 身份层 reviewed decision

身份层 reviewed decision 唯一枚举（4 值，本卷唯一 owner）：

```text
merge
keep_separate
mark_identity_alias
manual_review_hold
```

**与内容层 review decision 的区分**：内容层 review decision 见 PolicyBase_13 §5，回答「这次内容确认接受哪些候选内容」；本卷 decision 回答「两个 doc 的身份是否合并/分离/标记别名」。两者**不得混用、不得同时取值**。

每个身份层 decision 至少包含：`decision_id`、`candidate`、`target_doc`、`action`（上述 4 值之一）、`basis[]`、`evidence`、`reviewer`、`time`、`notes`。非法 `action` 返回 `invalid_reviewed_decision`（诊断码全集见 PolicyBase_19）。

需要 review 的场景：Tier 3/4 命中、issuer gate 失败、别名无闭环、内容指纹命中、身份/正文冲突、同 URL 语义变化、hash 碰撞集合的真实重复判断。

各动作约束：

- `merge`：指定 survivor 与被合并 doc、正反证据与恢复方案；只改变 PolicyBase_07 registry，**不**把两个包的历史 edition 拼接或改写；按 PolicyBase_07 §identity-migration 发布 migration batch。
- `keep_separate`：必须留下 **negative evidence**（记录为何不合并），避免下次重复提示。
- `mark_identity_alias`：必须指定 survivor、loser、正反证据与恢复方案；**只改变** PolicyBase_07 registry alias 表，不写业务关系 `alias_of`，不拼接/改写历史 edition。
- `manual_review_hold`：**不允许**正式写入或覆盖 current；candidate 留忽略工作区或受控审计，不得出现正式半包。

## 10. 多源组合

只在「§5 自动同一成立」**或**「§9 decision=`merge`」**之后**才允许组合字段/正文：

1. 注册来源 priority 数字小者优先；同级再看官方原始发布、公报/法库、正文/字段/附件完整度；
2. 低优先来源**只补缺失字段**，不覆盖高优先来源已确认字段；
3. 人工确认字段**不被自动覆盖**（确认链见 PolicyBase_13）；
4. title、文号、issuer、日期、validity、正文冲突进入 diff/review；
5. 未确认 OCR/layout/model、待确认转换件、授权未知全文**不得覆盖** confirmed 内容；
6. 所有 provenance/observation 保留；
7. 组合结果必须进入新的 candidate→confirmation→edition 链路（PolicyBase_13 状态机 + PolicyBase_09 原子切换），**不得就地修改 current**。

source priority 是**排序建议，不是合并授权**。组合不得绕过 §4 issuer 门、§9 review、PolicyBase_13 内容确认、PolicyBase_04 合规门。

## 11. Ingest 流程

ingest 是「candidate → 正式 edition + current 切换」的端到端重验链路。`ingest` action（动作语义）引用 PolicyBase_04 §action-enum 的 action enum，**不重定义 action**；edition 创建与 atomic switch 引用 PolicyBase_09 §atomic-create-switch，**不重定义 manifest/operation schema**。

```text
candidate
  -> schema/source/compliance preflight       # PolicyBase_04 合规门
  -> PolicyBase_07 identity (Layer 0-6, Tier)
  -> §4 issuer gate + §5 Tier 用途 / candidate signals
  -> 身份层 decision (§5 自动同一 或 §9 reviewed decision)
  -> §6 observation/update decision (4 值)
  -> PolicyBase_13 content pipeline (raw -> ... -> human_confirmed)
  -> PolicyBase_13 内容层 review decision (accept_all/...)
  -> PolicyBase_09 immutable edition staging (edition_create operation)
  -> PolicyBase_09 integrity/compliance/authorization 三 gate
  -> PolicyBase_09 atomic edition write + current switch (switch_kind)
  -> PolicyBase_14 index transaction           # P4 起且已有 active index 时
```

阶段边界：

- P3 尚无 active index 时，流程在 confirmed current 的原子切换和只读复核后成功，索引步骤记为 `not_yet_applicable`；**不得**为尚未实现的 P4 能力阻塞 P3。
- P4 起若配置为同步投影，适用的索引事务属于切换合同（PolicyBase_09 §atomic-create-switch），失败按 PolicyBase_09 原子恢复旧 current；异步投影必须以 PolicyBase_14 freshness gate 阻止陈旧结果被发布。

失败边界：

- 适用的任一步失败**不得**留下错误 current；已有包读取失败不得猜测状态。
- 正式切换前 operation 已完整写入 edition；切换后**只读验证，不补写历史**。
- `edition_create` 引用 PolicyBase_09 operations 枚举，本卷不复制。

## 12. Fail-closed 诊断（dedup/ingest 维度）

本卷 owner 以下 dedup/ingest 维度诊断（通用 `cli_*` 码与退出码全集见 PolicyBase_19）：

```text
existing_package_read_error
missing_reviewed_decision
invalid_reviewed_decision
dedup_gate_failed
issuer_unresolved_auto_merge
issuer_mismatch_auto_merge
tier4_auto_merge_forbidden
url_identity_insufficient
update_identity_ambiguous
hash_collision_rewrite_failed
hash_suffix_collision
content_confirmation_missing
edition_write_failed
current_switch_failed
index_projection_failed
```

`compliance_gate_failed`、`authorization_gate_failed`、`manifest_malformed` 由 PolicyBase_09 owner（合规/授权门与 manifest 合同）；通用解析与退出码归 PolicyBase_19。

失败 candidate 只留忽略工作区或受控审计，**不得出现正式半包**。P4 起同步索引失败按 PolicyBase_09 原子恢复旧 current；P3 无 active index 时 `index_projection_failed` 不适用，异步索引失败由 PolicyBase_14 freshness gate 隔离陈旧结果。

## 13. Hash 碰撞

碰撞 ID 算法、`hash_collision_rewrite` identity event schema 与 registry generation 由 PolicyBase_07 §collision-algorithm owner。本卷只 owner「碰撞集合如何在锁与单一 migration batch 中全员迁移」的协调约束：

- 碰撞集合必须在 **全局 identity lock** 与**单一 registry migration batch** 中**全员迁移** canonical ID；
- **不改写**旧包/旧 edition 字节；
- **不保留** canonical 裸短 hash 槽；
- **不用**递增序号（以上四点算法细节见 PolicyBase_07 §collision-algorithm）；
- 碰撞**不等于**重复，仍须执行 §4 issuer 门、§5 Tier 判定、§9 review；
- 迁移使用 PolicyBase_09 `operations[].kind=hash_collision_rewrite` 与 PolicyBase_07 identity event；
- 失败时**不得**切换 registry generation 或形成混合 canonical ID 状态。

## 14. 外部导入

用户提供文件**不等于**有保存、索引、外传或发布授权。外部导入必须走 §11 完整流程：

- **不能**用文件名、导入顺序、source_id、URL 或附件 hash 铸造普通 `doc_id`（身份生成语义见 PolicyBase_07 §basic-id）；
- **不能**默认 `merge` 或默认确认；
- 外传授权唯一存在处理对象 edition/candidate 的 manifest（owner PolicyBase_09 §external-transfer-authorization）；
- 外部导入的 candidate 必须经过 PolicyBase_04 合规门、PolicyBase_13 内容确认，方可进入 §11 链路。

## 15. 验收合同

golden 至少覆盖：

- Tier 0/1/2 自动同一；Tier 3/4 必须 review；
- Tier 5 同 observation=`no_change`、变化 observation 进入 §6 update；
- unresolved/different issuer 禁止自动同一；
- §7 内容指纹只召回，不自动合并；
- §6 `create_edition/create_document/manual_review_hold` 的身份与正文 diff；
- 人工确认字段不被来源优先级覆盖；
- §9 `mark_identity_alias` 不写业务关系；`merge` survivor 与可逆 registry migration；`keep_separate` 留 negative evidence；`manual_review_hold` 不写 current；
- §13 碰撞集合全员 registry generation 原子迁移，旧 edition 字节不变；
- §11 content confirmation、edition/current/index 任一失败保持旧 current；
- §14 外部导入不默认合并/确认。

```bash
policybase verify dedup
pytest tests/golden/dedup/
pytest tests/golden/ingest/
```

`policybase verify` 命令词法、退出码归 PolicyBase_19。

## 16. 不变量

1. Tier 4/5 不自动合并文献（Tier 定义见 PolicyBase_07）。
2. 同 URL 不等于同内容或同 edition。
3. 不同/未解析 issuer 不自动合并。
4. 更新只通过新 edition（PolicyBase_09），不覆盖 current。
5. source priority 不绕过 identity、review、confirmation 或合规门。
6. 身份层 reviewed decision（本卷 §9 4 值）与内容层 review decision（PolicyBase_13）是两个正交 decision 类型，不得混用。
7. §6 observation 更新状态机（4 值）与 §9 身份层 reviewed decision（4 值）正交，不得同时取值。
8. ingest 在 P2 建立 versioned 基础，P3 内容链消费同一合同；P4 起索引事务受 PolicyBase_09 切换合同与 PolicyBase_14 freshness gate 约束。
