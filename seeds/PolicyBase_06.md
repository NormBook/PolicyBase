# PolicyBase 元数据、版次与有效性

> 状态：主权威
> 分卷编号：PolicyBase_06
> 主题：metadata
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与权威边界

本卷是 **通用元数据 / edition_kind / validity / spatial_scope / 扩展 profile / 写入流程 / 元数据视角概念边界** 的唯一 owner。

非本卷 owner 的主题只一句引用：

- classification（分类树/TYPE/层级）见 PolicyBase_05 §classification-tree；
- `classification_level` 枚举（`public` 等公开性层级值）+ 密级 sensitivity 维度见 PolicyBase_04 §classification-level，本卷只消费 frontmatter 的 `classification_level` 字段；
- `doc_id` / `edition_id` / canonical key 生成语义、`historical_ids`、`id_quality`、legacy drift、碰撞算法见 PolicyBase_07 §id-semantics；本卷的 `edition_id` / `edition_kind` 字段入口也归属 PolicyBase_09 §manifest-contract（manifest 最小合同）；
- 去重与「新 edition 是否构成新文献」的裁决见 PolicyBase_08 §reviewed-decision；
- edition 目录、文件权威、current 指针、`switch_kind`、operations 见 PolicyBase_09 §edition-identity / §switch-kind / §operations；
- 内容处理与版面见 PolicyBase_13 §content-state-machine；索引投影见 PolicyBase_14 §docs-meta；
- `disclosure.mode`（proactive 等）枚举与合规门见 PolicyBase_04 §disclosure-mode；
- `relations[]` 是 frontmatter 文档级元数据字段，本卷 owner；关系类型受控枚举见 §11，各类型的语义 owner 于 §11 显式 cross-ref。

四库上下文：本卷字段下限在四库（zcwjk / gz / flk / xxgk）下保持一致；库间差异仅在 §3.2、§5、§6 的字段取值域上显式标注，不改变字段 schema。

## 2. 迁移目标

| 目标 | 内容 |
|---|---|
| `data/schemas/frontmatter.schema.json` | 通用字段、类型、受控值（本卷 §3 下限） |
| `data/schemas/document_frontmatter.schema.json` | 主动公开、密级消费、PII 发布约束（密级枚举引用 PolicyBase_04） |
| `data/schemas/edition.schema.json` | edition 身份与父版次约束（本卷 §4） |
| `docs/specs/metadata.md` | 人类可读规格 |
| `tests/golden/metadata/` | normal / edge / error |

两层 frontmatter schema 必须通过唯一入口组合校验；不得只通过其中一层即入库。

## 3. 通用 frontmatter

```yaml
schema_version: "1"
id: REG-a1b2c3d4e5
edition_id: ed-9f86d081884c7d659a2feaa0
edition_kind: source_update
parent_edition_id: ed-2c26b46b68ffc68ff99b453c

classification:
  system: state_law
  hierarchy: regulation
  subtype: administrative_regulation
  document_form: 条例

title: 优化营商环境条例
document_number: 中华人民共和国国务院令第722号
document_number_normalized: 国务院令第722号
document_number_canonical: LING-722
issuers:
  - name: 中华人民共和国国务院
    org_id: "1000000000010001"
    issuer_unresolved: false
    level: central_government
    role: primary

issue_date: 2019-10-22
publish_date: 2019-10-23
effective_date: 2020-01-01
implementation_date: 2020-01-01
validity:
  status: effective
  effective_from: 2020-01-01
  validity_period: {type: permanent, max_until: null}

spatial_scope:
  codes: ["100000"]
  labels: [全国]
subjects: [营商环境]
direction: downward
disclosure:
  mode: proactive
  channel: [government_website, policy_library]
sources:
  - source_id: cn-xzfgk
    url: https://www.gov.cn/zhengce/xzfgk/...
    accessed: "2026-08-04T03:00:00Z"
relations: []
making_process: administrative_legislation
making_process_detail: null
type_tags: []
classification_level: public
urgency: regular
id_quality: standard
historical_ids: []
language: zh-Hans
```

### 3.1 字段下限

| 字段 | 约束 |
|---|---|
| `schema_version` | 必填，受控版本 |
| `id` | 必填，等于包 `doc_id`（生成语义见 PolicyBase_07） |
| `edition_id` | 必填，等于当前 edition 目录名与 manifest 值；字段入口归 PolicyBase_09 §manifest-contract |
| `edition_kind` | 必填，受控 5 值，见 §4 |
| `parent_edition_id` | 首版为 null；后续版必填且指向同一 doc 的已有 edition |
| `classification` | 必填，结构与受控值由 PolicyBase_05 定义 |
| `title` | 必填非空 |
| `issuers[]` | 必填，至少一个 `role: primary` |
| `validity` | 必填，见 §6 |
| `spatial_scope` | 可空 object；存在时遵守 §5，不再允许 string |
| `subjects[]` | 可空 array[string]；禁止旧的单值 `subject` |
| `disclosure.mode` | 必填，枚举与红线见 PolicyBase_04 §disclosure-mode；正式正文必须为 `proactive` |
| `sources[]` | 必填摘要，只含 `source_id` / `url` / `accessed` |
| `relations[]` | 可空数组，关系类型受控枚举见 §11 |
| `classification_level` | 消费字段；公开性层级枚举（`public` 等）与密级 sensitivity 见 PolicyBase_04 §classification-level。正式 edition 只能为 `public`，其他值仅允许候选审计 |
| `id_quality`、`historical_ids[]` | 见 PolicyBase_07 §id-semantics |
| `language` | BCP 47，默认 `zh-Hans` |

`document_number*`、日期、`direction`、`making_process`、`type_tags`、`urgency` 可按 schema 可空，但不得以空字符串代替 null。附件、文件 hash、处理 confidence、页坐标、prompt 与模型信息禁止进入 frontmatter，只写 manifest。

### 3.2 四库差异（字段取值域）

字段 schema 在四库一致；以下字段的典型取值域存在库间差异，须在迁移与校验时显式标注，不得隐藏在通用描述里：

| 字段 | zcwjk | gz | flk | xxgk |
|---|---|---|---|---|
| `classification.system` | 多见 `policy` / `process` | 多见 `administrative_rule` | 多见 `state_law` | 多见 `disclosure` |
| `making_process` | 行政规范性文件为主 | 规章制定程序为主 | 立法程序为主 | 公开发布流程为主 |
| `validity.status` 典型值 | `effective` / `expired` 居多 | `effective` / `superseded` 居多 | 全 12 值最广覆盖 | `effective` / `archived` 居多 |
| `spatial_scope` 来源形态 | 多为发文机关层级 | 多为部门或地方政府 | 多为国家或省级 | 多为发布主体辖区 |
| `document_number` 形态 | 部门发文字号 | 政府令 / 部门令 | 主席令 / 国务院令 / 法规编号 | 公开版文号 |

差异是统计与典型形态，不是字段 schema 的库级分支；同一字段在四库下都走同一 schema 与 §3.1 下限。

## 4. edition_kind（5 值）

`edition_id` 格式与 canonical edition payload 算法见 PolicyBase_09 §edition-identity；本卷只固定 frontmatter 中 `edition_kind` 字段的受控值与语义边界。

`edition_kind` 受控 5 值：

| 值 | 含义 |
|---|---|
| `initial` | 首次确认入库 |
| `source_update` | 来源内容或元数据发生变化 |
| `correction` | 人工纠错，不表示来源发布了新版本 |
| `reprocess` | 工具、OCR、版面或模型版本升级后的重新处理 |
| `redaction` | 合规脱敏后形成的新确认版 |

除首版外，edition 必须通过 `parent_edition_id` 形成无环有向链。`source_update` 与法规修订不是同义词：来源网页机械更新可以产生新 edition，但是否构成法律意义上的新文献、修订或替代由身份、去重与关系规则判断（PolicyBase_07、PolicyBase_08）。

**switch_kind cross-ref**：包级切换动作（rollback / recovery 等共 7 值）见 PolicyBase_09 §switch-kind。本卷 `edition_kind`（5 值）是 PolicyBase_09 `switch_kind`（7 值）的同名前缀子集——两者命名空间不同：`edition_kind` 描述「这次确认的内容从何而来」，是 edition 自带属性；`switch_kind` 描述「current 指针如何被移动到某个 edition」，是包级操作事实。rollback **不是** `edition_kind`：它把历史确认 edition 重新选为 current，不复制 edition，因此记为 `switch_kind=rollback` 而非新增 edition。frontmatter 不保存 `is_current`；current 是 PolicyBase_09 指针事实，避免同一包出现多个自称 current 的 edition。

## 5. 空间范围

`spatial_scope` 固定为 object，不再在「自由标签或受控数据」之间留待实现选择：

```yaml
spatial_scope:
  codes: ["420000", "420100"]
  labels: [湖北省, 武汉市]
```

规则：

1. `codes[]` 使用版本化行政区划受控码，按 Unicode code point 去重排序。
2. `labels[]` 保存来源原文或人工确认名称，与 codes 按语义对应，但不要求位置一一配对。
3. 能解析时至少有一个 code；暂不能解析时 `codes: []` 且保留 labels，并进入 `spatial_scope_unresolved` 复核。
4. 全国使用 `codes: ["100000"]`，不得同时列出所有省级代码。
5. 跨区域适用允许多值；不得压缩为逗号字符串。
6. 行政区划表变化不静默改写历史 edition；新 edition 记录新的受控数据版本证据。

四库差异：`codes` 的受控源与粒度由来源矩阵决定（来源矩阵治理见 PolicyBase_10 §source-matrix）；flk 多为国家或省级，zcwjk / gz / xxgk 可下钻到市县。受控码本身的版本与发布由 PolicyBase_10 注册，不在本卷展开。

## 6. 有效性

`validity.status` 固定 12 值：

```text
drafting, under_review, under_deliberation, promulgated_pending,
effective, abolished, expired, superseded, partially_effective,
suspended, unknown, archived
```

来源专有状态保留在 provenance；无法确定时为 `unknown`，不得猜测。`classification.system=process` 不得为 `effective`。有效性变化产生新 edition；不得原地重写已发布 edition。

四库差异：flk 全 12 值覆盖最广（含 `promulgated_pending` / `partially_effective` 等立法中间态）；gz 与 zcwjk 以 `effective` / `superseded` / `expired` 为主；xxgk 多见 `effective` 与 `archived`。差异是取值分布，不是枚举集合的库级裁剪——四库共用同一 12 值枚举。

## 7. 扩展 profile

扩展字段写 `_profile.yaml`，不进通用 frontmatter。每个 profile schema 必须声明：

- `profile_id` 与 schema version；
- `activation_predicate`；
- `required_when_active`；
- `forbidden_when_inactive`。

未激活 profile 禁止存在；激活后缺字段必须拒绝。公报期号、专项主题词、库内检索别名等不进入通用 frontmatter，统一走 profile。profile 变化跟随 edition，不允许一个 `_profile.yaml` 被多个 edition 原地共享和改写。

## 8. 写入与更新流程

固定顺序（owner 边界：本卷固定 frontmatter 视角的序与失败语义，落地写入与原子切换由 PolicyBase_09 §operations / §atomic-switch 执行）：

1. 分类并推导 TYPE（PolicyBase_05）；
2. 生成或解析 `doc_id`（PolicyBase_07）；
3. 去重与「更新还是新文献」判断（PolicyBase_08）；
4. 生成候选 frontmatter、正文与 profile；
5. 本地合规检查（PolicyBase_04）；
6. 内容处理与人工确认（PolicyBase_13）；
7. 计算 immutable `edition_id`（PolicyBase_09）；
8. 按 PolicyBase_09 §operations 写入新 edition；
9. 原子切换 current（PolicyBase_09 §atomic-switch，`switch_kind` 见同卷）；
10. 按 PolicyBase_14 更新索引。

切换前失败不改变旧 current。切换后复核或同步索引失败时，PolicyBase_09 必须最终恢复旧 current；失败窗口内所有消费者通过 current/index freshness barrier 拒绝不一致读取，不能把「最终回切」描述成新指针从未可见。首次写入没有旧 current 时按 PolicyBase_09 的 unpublished initial recovery 处理。索引层只读可消费 current 或显式请求的历史 edition，不得反向修改元数据。

## 9. 验收合同

golden 至少覆盖：

- `spatial_scope` 全国、单地、多地、未解析与旧 string 拒绝；
- `subjects[]` 多值与旧单值 `subject` 拒绝；
- `edition_kind` 五值（initial / source_update / correction / reprocess / redaction）；
- `parent_edition_id` 悬空、跨 doc parent、edition 环、payload/id 不一致拒绝；
- 正式 edition 的非 `public` `classification_level` 拒绝（枚举由 PolicyBase_04 提供）；
- profile 激活、缺失与错误出现；
- `validity.status` 受控值与 `process` / `effective` 冲突。

最低入口（脚本「待实现，重构期不执行」）：

```bash
policybase verify integrity
policybase verify spec
pytest tests/golden/metadata/
```

## 10. relations[] 与关系类型受控枚举

`relations[]` 是 frontmatter 文档级元数据字段（本卷 owner），保存本文献对其它文献/资源的声明型关系。每条记录至少含 `type`、`target_doc_id`（或显式 `target_edition_id`）与 `evidence`。`relations[]` 不替代 PolicyBase_07 identity registry 的身份事实、PolicyBase_09 current 指针或 PolicyBase_08 身份层 reviewed decision——它只承载文献间可消费的关系声明。

关系类型受控枚举（本卷 owner；各类型的语义 owner 见下）：

| `type` | 含义 | 语义 owner |
|---|---|---|
| `alias_of` | 身份层别名声明；**不写关系索引表**，只随 PolicyBase_08 身份层 reviewed decision `mark_identity_alias` 审计 | PolicyBase_08 §9（身份层 alias decision） |
| `supersedes` / `supersedes_by` | 本文献替代/被替代为更新生效版 | PolicyBase_09 §switch-kind（supersession） |
| `replaces` / `replaced_by` | 立法意义上的取代（旧法被新法整体取代） | PolicyBase_09 §switch-kind |
| `amends` / `amended_by` | 部分修订 | PolicyBase_09 §switch-kind |
| `cites` | 引用另一文献作为依据 | PolicyBase_14 §12（关系索引投影） |
| `implements` / `implemented_by` | 上位法实施/被实施 | PolicyBase_14 §12 |
| `authorizes` / `authorized_by` | 授权另一文献或事项 / 被授权依据 | PolicyBase_14 §12 |
| `based_on` / `basis_for` | 制定依据 | PolicyBase_14 §12 |
| `repeals` / `repealed_by` | 废止 | PolicyBase_09 §switch-kind |
| `partial_repeal_of` | 部分废止 | PolicyBase_09 §switch-kind |
| `publishes` / `published_by` | 发布载体关系 | PolicyBase_14 §12 |
| `forwards` / `forwarded_by` | 转发 | PolicyBase_14 §12 |
| `attachment_of` / `has_attachment` | 附件载体 | PolicyBase_14 §12 |
| `part_of` / `has_part` | 组成部分 | PolicyBase_14 §12 |
| `interpreted_by` / `interprets` | 解释关系 | PolicyBase_14 §12 |
| `replies_to` / `replied_by` | 答复关系 | PolicyBase_14 §12 |
| `succeeds` / `succeeded_by` | 编年序列前后继 | PolicyBase_14 §12 |
| `ratified_by` / `ratifies` | 批准关系 | PolicyBase_14 §12 |
| `listed_in_registry` / `lists` | 被目录、清单或登记册收录 / 收录另一文献 | PolicyBase_14 §12 |
| `next_cycle` / `previous_cycle` | 同一周期性事项的下一周期 / 上一周期 | PolicyBase_14 §12 |
| `conflicts_with` | 对称冲突 | PolicyBase_14 §12 |
| `parallel_document` | 对称并行文献 | PolicyBase_14 §12 |

owner 边界裁定：

- **本卷（PolicyBase_06）** owner `relations[]` 字段 schema（位置、必含子字段、可空、不在 frontmatter 中保存派生反向边）与关系类型受控枚举集合。
- **PolicyBase_08** owner `alias_of` 的语义——它是身份层 `mark_identity_alias` reviewed decision 的声明投影，不是业务关系；关系索引投影（PolicyBase_14 §12）明确排除 `alias_of`，不写入关系表。
- **PolicyBase_09** owner `supersedes/replaces/amends/repeals` 等 supersession 类关系的切换语义（`switch_kind`、current 指针事实、edition supersession）。
- **PolicyBase_14 §12** owner 关系索引的正向/对称枚举集合与反向派生视图（`docs_meta.relations_json` 投影、反向派生、`derived=true` 标记）；本卷枚举与 PolicyBase_14 §12 的正向/对称集合保持一致，差异仅在 `alias_of`（身份层声明，不计入关系索引）。

未列入上表的 `type` 一律拒绝；新增类型必须先经本卷与对应语义 owner 同步，再进入 PolicyBase_14 关系索引投影。

## 11. 不变量

1. `doc_id` 是文献身份，`edition_id` 是不可变快照（语义见 PolicyBase_07）。
2. current 不是 frontmatter 自声明字段，是指针事实（PolicyBase_09）。
3. 已发布 edition 永不原地修改。
4. `spatial_scope` 固定为 codes + labels。
5. 候选处理事实与模型事实不进入 frontmatter。
6. 新 edition 不自动意味着新文献；该裁决属于 PolicyBase_08。
7. `edition_kind`（5）与 `switch_kind`（7）是不同命名空间，前者是 edition 自带属性，后者是包级操作事实（PolicyBase_09）。
