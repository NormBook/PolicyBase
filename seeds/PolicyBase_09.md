# PolicyBase 不可变文献包、Edition、Manifest 与包级回滚

> 状态：主权威
> 分卷编号：PolicyBase_09
> 主题：storage
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷是**不可变文献包、edition、manifest、operation、current 指针与包级回滚**的唯一 owner。以不可变 edition 闭合 ingest、更新、纠错、重新处理、脱敏、回滚与索引消费。

owner 主题（本卷完整展开）：

- 正式目录结构、Edition identity、`current.json`、`switches/`、包级 Rollback；
- `switch_kind`（7 值）唯一枚举与切换语义；
- Edition 文件权威、manifest 最小合同；
- **文件角色枚举（16）**、**operations 唯一枚举（19）+ operation status**；
- 合规/授权/确认门（三布尔 `disclosure_ok/sensitivity_ok/pii_ok`）；
- 原子创建与切换、Update/Correction/Reprocess/Redaction；
- `normalized_lf_markdown_body`（本卷 owner）；
- integrity 拒绝条件、不变量。

非 owner 主题（一句引用，不展开）：

- `edition_kind` 元数据语义（initial/correction/source_update/reprocess/redaction 五值）见 PolicyBase_06 §edition-kind；本卷 `switch_kind` 与之关系见 §4.4。
- 身份层 ID、registry generation、availability、alias 见 PolicyBase_07。
- 去重与 reviewed decision 见 PolicyBase_08。
- 内容生产状态机、content-layer review decision、OCR engine 见 PolicyBase_13。
- 索引实现、`record_hash` frame 见 PolicyBase_14（其 `record_hash.body` 引用本卷 `normalized_lf_markdown_body`，`record_hash.semantic_hash` 引用 PolicyBase_07）。
- **repository rebootstrap**（删除远程仓库/.git/edition 块）不在本卷范围；本卷只覆盖 edition/包级回滚。

核心规则：

1. `{doc_id}` 表示文献身份（见 PolicyBase_07）；`editions/{edition_id}` 表示一次不可变确认快照。
2. edition 一旦成为 current 即永久只读，不得就地修改 `index.md`、`_profile.yaml`、`_sources.yaml`、assets 或 manifest。
3. `current.json` 是唯一 current 权威，原子替换；`switches/` 保存不可变切换事件；edition 不自称 current。
4. candidate、页图、OCR、layout、模型输出只有经确认并随新 edition 写入后才进入正式包。
5. 原件、派生物、operation、授权与确认链必须可审计；未授权、未确认、合规失败一律 fail closed。

## 2. 迁移目标

| 目标 | 内容 |
|---|---|
| `docs/specs/storage.md` | 人类可读规格 |
| `data/schemas/document_manifest.schema.json` | edition manifest |
| `data/schemas/current-pointer.schema.json` | current 指针 |
| `data/schemas/current-switch-event.schema.json` | 不可变切换/回滚事件 |
| `data/schemas/package-audit-event.schema.json` | 不改变 edition 的运行/失败/恢复事件 |
| `data/vocabularies/file_roles.yaml` | 文件角色 |
| `data/vocabularies/operation_kinds.yaml` | operation 枚举 |
| `src/policybase/pipeline/storage/` | 原子写入、切换、回滚、GC |
| `tests/golden/document_package/` | normal/edge/error/crash recovery |

## 3. 正式目录

```text
data/documents/{TYPE}/{h0h1}/{h2h3}/{doc_id}/
├── current.json
├── switches/
│   └── {switch_event_id}.json
├── audit/
│   └── {audit_event_id}.json
└── editions/
    ├── {edition_id}/
    │   ├── index.md
    │   ├── manifest.json
    │   ├── _sources.yaml        # 按需
    │   ├── _profile.yaml        # 按需
    │   └── assets/              # 按需
    └── {edition_id}/...
```

每个 edition 自包含，禁止从 edition 文件以相对路径引用其他 edition。跨 edition 继承通过 manifest 的 `parent_edition_id` 与文件 provenance 表达；实现可内容寻址去重物理字节，但逻辑读取必须看到完整、自包含、不可变的 edition，且不得依赖可修改的外部路径。

临时产物、candidate、页图缓存、失败输出、模型中间物、staging 只存在于被忽略工作区。正式目录禁止符号链接、设备文件、绝对路径与 `..`。

## 4. Edition 与 current

### 4.1 Edition identity

`edition_id` 格式见 PolicyBase_06，表示"确认内容 + 决定其可消费性的稳定证据快照"，payload 固定为：

```text
sha256(
  frame("frontmatter", canonical_yaml(frontmatter_without_edition_id)) +
  frame("body", normalized_lf_markdown_body) +
  frame("profile", canonical_yaml(profile_or_absent)) +
  frame("sources", canonical_yaml(sources_or_absent)) +
  frame("assets", canonical_json(asset_semantic_projection)) +
  frame("evidence", canonical_json(evidence_semantic_projection))
)
```

`frame` 固定为 `utf8_byte_length(name):nameutf8_byte_length(payload):payload`，长度按 UTF-8 字节计算。`canonical_yaml` 必须先以禁止 duplicate key、tag、anchor、float 与隐式 timestamp 的受限 YAML 解析为 `null|boolean|integer|string|array|object`，字符串正规化为 NFC、object key 按 Unicode code point 排序，再按 RFC 8785 canonical JSON 的 UTF-8 字节输出；absent 固定投影为字符串 `<absent>`，不得等同 null 或空对象。数组顺序由对应 schema 明确；集合型数组先按稳定 key 排序。

### 4.2 normalized_lf_markdown_body（本卷 owner）

本卷是 `normalized_lf_markdown_body` 的唯一 owner。规则：

- 去 BOM；统一 CRLF/CR 为 LF；保留其他字符；
- 结尾固定恰好一个 LF（无则补、多余则删）；
- 不做 NFC、不做空白折叠、不做语义改写——确定性投影而非内容规整。

此值同时是本卷 `frame("body", ...)` 的输入，也是 PolicyBase_14 `record_hash.body` 的引用对象（见 PolicyBase_14 §record-hash）。

### 4.3 投影与幂等

`asset_semantic_projection` 只投影资产的 role、sha256、derived_from、access、index/publication policy。`evidence_semantic_projection` 投影 compliance/authorization/content-confirm decision hash、处理 input/output/tool/prompt/schema version 与状态，但排除 actor display name、墙钟时间、日志路径、随机 operation ID。

相同完整投影保持幂等；相同内容但不同决定或处理证据可形成不同 edition。manifest 中不进入投影的追加运行/尝试不得修改 edition，写入本包 `audit/` 的 immutable event。`edition_id` 不通过自身或 manifest 自引用形成循环。PolicyBase_14 `record_hash` 复用本卷 `frame` 规则。

### 4.4 current.json 与 switch_kind（7 值，本卷唯一 owner）

`current.json` 示例：

```json
{
  "schema_version": "1",
  "doc_id": "REG-a1b2c3d4e5",
  "edition_id": "ed-9f86d081884c7d659a2feaa0",
  "previous_edition_id": "ed-2c26b46b68ffc68ff99b453c",
  "switch_event_id": "sw-7c222fb2927d828af22f5921",
  "switch_kind": "source_update",
  "switched_at": "2026-08-03T03:15:00Z",
  "evidence_ref": "switches/sw-7c222fb2927d828af22f5921.json"
}
```

`switch_kind` 唯一枚举（7 值）：

```text
initial
source_update
correction
reprocess
redaction
rollback
recovery
```

前 5 个值与 PolicyBase_06 `edition_kind`（initial/correction/source_update/reprocess/redaction）**同名同语义对齐**——即对应 `edition_kind` 的 edition 被 current 选中时的切换名；本卷在此基础上**扩展两个包级切换值**，不对应任何 edition 内容变更：

- `rollback`：current 原子切回已存在的某历史 confirmed edition，不创建新 edition（见 §5）；
- `recovery`：从崩溃/失败初始/中断的写入恢复后发布的指针修正，`from` 可为 `<failed edition>` 或 null，`to` 可为 null（见 §6.3、§10）。

`edition_kind` 的元数据语义（frontmatter 字段含义、profile 联动）由 PolicyBase_06 owner；本卷只 owner `switch_kind` 切换事件语义。PolicyBase_06 §edition-kind 会 cross-ref 本卷 §4.4。

指针必须引用存在且 integrity、compliance、confirmation 均通过的 edition，并引用存在的 immutable switch event。

### 4.5 switch event

switch event 至少包含 event_id、doc_id、from/to edition、kind、actor、reason、created_at、target confirmation evidence、前一 event ID 与 `expected_previous_event_id`。event_id 为 canonical event payload 的 SHA-256 前 24 hex。事件文件一经创建不得修改或删除；事件只有被 `current.json` 直接或经后继事件链引用时才表示已生效切换。

崩溃留下的未引用 event 是 abandoned intent，不改变 current，可保留供恢复审计。有效事件链不得断裂或成环。Git 可提供额外证据，但不是 switch 历史的唯一承载。

每次写入在 doc 级 exclusive lock 下执行；首次 `expected_previous_event_id` 为 null。CAS 不匹配稳定返回 `current_conflict`，调用方重新读取后重算，不得覆盖并发 writer。临时文件名必须包含 operation ID，原子 replace 后再次 fsync 父目录。

## 5. 包级 Rollback（switch_kind=rollback）

rollback 只把 `current.json.edition_id` 原子切回某个已存在的 confirmed edition：

- 不复制、不改写目标历史 edition；
- 在新 current 指针记录被替换 edition 与 rollback evidence；
- 写新的 immutable switch event（`switch_kind=rollback`），记录 actor、reason、time 与前一事件；
- P4 起存在 active index 且采用同步投影时，索引事务重投影目标 edition；失败则原子恢复旧指针；P3 尚无 active index 时该步骤不适用（见 PolicyBase_14）；
- 回滚不删除较新 edition。

> **级别边界**：本卷 rollback 是 edition/包级指针回切，作用于单一 `{doc_id}` 包内。删除远程仓库、`.git` 历史、整包物理清除或跨包重建属于 repository rebootstrap 范围，不在本卷范围。

## 6. recovery 级切换声明

`switch_kind=recovery` 表达"对中断写入/失败初始的指针级修复"，是包级 event，**不是** repository rebootstrap（后者建立新的仓库与 .git）。

### 6.1 失败初始

首次写入没有旧 current：在最后一步 PolicyBase_07 registry CAS 前，包不可被默认消费者发现。若 package pointer 发布后的任一步失败，recovery event 明确 `from=<failed edition>, to=null, recovery_kind=failed_initial`，CAS 删除 current 指针并保留 unpublished package/audit；禁止伪造不存在的旧 edition。只有 registry generation CAS 成功后，初始 locator/edition 才可被 list/show/search/export 发现。

### 6.2 read-back 失败

registry 切换后的 read-back 失败必须发布显式 recovery registry generation，不能改写已发布 generation。失败 edition 留作非 current 审计或隔离。

### 6.3 与 repository rebootstrap 的边界

recovery event（本卷）只修正本包 current 指针与 switch 链；仓库级 repository rebootstrap、不可继承对象清单、重新认证规则不在本卷范围。本卷 `audit/` 中的 `recovery_scan` event 见 §8.2。

## 7. Edition 文件权威

| 文件 | 权威内容 |
|---|---|
| `index.md` | PolicyBase_06 frontmatter + 本 edition confirmed 主 Markdown |
| `manifest.json` | edition、文件事实、处理链、授权、合规与确认 |
| `_sources.yaml` | source observations、发现/获取链、内容 hash |
| `_profile.yaml` | 分类激活的扩展字段 |
| `assets/` | 经授权保存的原件、确认派生物与必要审计工件 |

frontmatter 的 `id/edition_id` 必须分别等于包与 edition 目录；manifest 同样一致。`index.md` 必须登记为 `main_markdown`。

`_sources.yaml` 保存 source_id、original/canonical URL、accessed、raw format、source registry/profile/recipe/rule snapshot、observation hash、handoff。frontmatter `sources[]` 只是可检索摘要，由它派生。

## 8. manifest 最小合同与 operations

### 8.1 manifest 最小合同

manifest 至少包含：

- `schema_version`、`doc_id`、`edition_id`、`edition_kind`、`parent_edition_id`；
- `files[]`；
- `operations[]`（非空）；
- `issuer_resolution_snapshot`；
- `content_pipeline`（PolicyBase_13 状态、selected file、confirmation）；
- `external_transfer_authorizations[]`（按需）。

除 manifest 自身外，edition 中每个版本控制文件恰好登记一次。每个 file 至少有 `id/role/path/media_type/format/sha256/size_bytes`。派生文件有非空 `derived_from[]`，引用同 manifest 文件且无环。

operation 至少有 `id/kind/status/performed_at`；按类型补充 input/output、tool、prompt、model、decision、actor、evidence、error。成功且产生文件的 operation 必须有输出；失败必须有稳定 `error_code`。

### 8.2 operations 唯一枚举（19，本卷唯一 owner）

本节是 `manifest.operations[].kind` 的唯一权威：

```text
insert
merge
source_observation
source_download
external_import
identity_migration
hash_collision_rewrite
conversion
extraction
ocr
layout
model_refine
human_review
content_confirm
compliance_gate
authorization_review
publication_gate
edition_create
manual_review_hold
```

operation status：`pending_manual|succeeded|failed|needs_review|confirmed|rejected`。

### 8.3 与 switch_kind 的关系

旧的就地 `correction` 不再允许。纠错表达为：`human_review` → `content_confirm` → `edition_create(edition_kind=correction)`，随后写包级 switch event 并切换 current。重新 OCR/排版/模型处理表达为 `edition_kind=reprocess`。来源变化表达为 `edition_kind=source_update`。`switch_kind` 中的 `rollback/recovery` 属包级 switch event kind，**不**写进不可变 edition 的 `manifest.operations[]`。

### 8.4 记录粒度

自动 operation 记录工具包名、版本、配置/profile hash 与代码 revision。人工 operation 记录 actor、时间、理由与 diff。各 operation 类别（OCR / layout / model refine / correction）的 `schema_version / backend_version / prompt_version / config_hash` 最小必填集与 `<absent>`（声明该维度对此类操作不适用）的判定见 PolicyBase_13 §4「操作类别 × 版本维度」表。模型 operation 额外遵守 PolicyBase_13 §12（backend/model/adapter version、prompt schema version、模板 hash）与 PolicyBase_04 §external-model-gate。

### 8.5 audit/ 事件

`audit/` 只保存**不改变 edition identity** 的 `no_change_observation|failed_attempt|abandoned_intent|failed_initial|recovery_scan` 事件，必须引用 input/candidate/run/current/edition hash 与幂等键；不得在其中补写或覆盖 manifest 应承载的成功处理、确认、授权或文件事实。相同 event payload 幂等，保留策略不得早于其引用的 edition/package。

## 9. 文件角色枚举（16，本卷唯一 owner）

受控角色：

```text
main_markdown
source_record
extension_profile
original_attachment
converted_attachment
raw_capture
extracted_text
ocr_candidate
layout_candidate
model_refined_candidate
confirmed_markdown
content_geometry
content_diff
audit_artifact
candidate_manifest
switch_event
```

规则：

- 原始附件始终保留为 `original_attachment`，派生物不得替代；
- `raw_capture` 只在保存授权允许时进入正式 edition，否则留 candidate 审计；
- OCR/layout/model candidate 默认不可索引、不可发布；
- `content_geometry` 保存页、块、坐标、阅读顺序与表格结构，不冒充正文；
- `confirmed_markdown` 是进入 `index.md` 前的确认输入；edition 内 `index.md` 为唯一主正文；
- `candidate_manifest` 是模型调用发生 edition 创建之前时的授权权威（见 §10.2），仍被 `.gitignore` 排除；
- `switch_event` 仅对应 `switches/{switch_event_id}.json`，不进 edition 目录；
- 空派生文件禁止登记。

## 10. 合规、授权与确认门

### 10.1 三布尔合规门

每个可成为 current 的 edition 必须有最新有效 `compliance_gate` operation，且 `disclosure_ok/sensitivity_ok/pii_ok` 三个布尔**均为 true**。`classification_level=public` 只是声明，不替代检测证据（见 PolicyBase_04 §disclosure-mode 与 §classification-level）。

文件 access 至少区分：local storage、local indexing、external transfer、redistribution。任一缺失按 false。

### 10.2 外传授权与 candidate manifest

外部传输授权唯一存在处理对象的 `manifest.json.external_transfer_authorizations[]`。模型 operation 必须引用有效授权且覆盖所有 input file 与 scope。

模型调用发生在 edition 创建之前时，受控 candidate 工作区必须有使用同一 manifest schema 的 `candidate manifest`（角色 `candidate_manifest`）；它是该次调用的授权权威。授权记录与模型 operation 在确认入库时逐字节/按 canonical JSON 复制进新 edition manifest，并保留 candidate ID/hash。既有 immutable edition 不得为追加新授权而修改；reprocess 必须先建立新的 candidate manifest。candidate manifest 仍被 `.gitignore` 排除，PII/受限原文不得因该记录进入正式包。

### 10.3 content_confirm

current edition 还必须有 `content_confirm` operation：

- status=`confirmed`；
- 指向 selected confirmed Markdown；
- 记录 reviewer/规则、diff、来源证据与 confirmation time；
- 确认内容与 `index.md` hash 一致。

candidate、needs_review、pending_manual、rejected 或未通过 gate 的 edition 不得成为 current。

## 11. 原子创建与切换

正式消费状态由本卷的 publish coordinator 唯一发布。固定锁顺序为：PolicyBase_07 global identity registry lock → 按 canonical doc_id 排序的 doc lock → P4 索引事务；任何调用方不得反序获取。普通 current update 也发布新的 registry generation，使 entry 同时绑定 canonical doc_id、package locator、edition_id 与 current pointer hash。

在同一文件系统下：

1. 在忽略的 staging 生成完整 edition；
2. 计算所有 hash 与 edition_id；
3. 运行 schema、integrity、合规、授权、content confirmation；
4. 原子 rename 到不存在的 `editions/{edition_id}`；若已存在则验证完全相同；
5. 读取 current 与 predecessor event，生成带 expected predecessor 的 immutable switch event；
6. 生成 operation-unique `current.json.{operation_id}.tmp`，引用该 event，fsync 文件与目录；
7. 再次比较 expected predecessor，以 CAS 原子 replace `current.json` 并 fsync 父目录；
8. 只读复核 current、event 与 edition；
9. 生成尚未发布的新 PolicyBase_07 registry generation，entry 绑定本次 edition/current hash；P4 active index 存在时索引器投影并绑定该 generation（见 PolicyBase_14），P3 记录 `index_not_yet_applicable`；
10. 复核 package/current/index/registry candidate 全部一致后，最后以 expected registry generation CAS 切换 PolicyBase_07 registry `current.json`，这一步才使新消费状态生效；
11. registry CAS 前 任一步失败时，写 recovery/audit、以 CAS 恢复旧 package current，旧 registry generation 保持权威；异步索引未 fresh 时不得切 registry。registry 切换后的 read-back 失败必须发布显式 recovery registry generation（见 §6.2）。失败 edition 留作非 current 审计或隔离。

禁止先删除旧包、覆盖非空目录、原地修改 edition，或切换后再补写属于 edition identity 的 operation/evidence。

## 12. Update / Correction / Reprocess / Redaction

| 场景 | 行为 |
|---|---|
| observation 完全相同 | 不建 edition；run/provenance 写 acquisition ledger 或本包 `audit/` immutable event，不改 `_sources.yaml` |
| 来源正文/元数据变化 | PolicyBase_08 判断后建 `source_update` edition |
| 人工纠错 | 从 current 派生 `correction` edition，保存 diff 与 reviewer |
| 工具/规则升级 | 从指定 edition 派生 `reprocess` edition，不覆盖旧产物 |
| 脱敏 | 建 `redaction` edition，重新执行全部 gate |
| 回滚 | 原子选择已有 confirmed edition（switch_kind=rollback），不建内容副本 |

若 identity 改变，按 PolicyBase_07 stage 新 doc_id package 并原子发布 identity registry generation；旧 package/edition 不改写，不得通过原 package 内 edition 偷换 `doc_id`。

## 13. 索引与发布消费

### 13.1 默认消费源

默认只消费 PolicyBase_07 current identity registry 中 `availability=active` 的 canonical entry，再消费其 package `current.json` 指向 edition。`withdrawn/quarantined` 默认从 list/search/export 与 show body 排除；显式授权审计可按 alias/package locator 读取历史。显式 `--edition`/`--history` 查询可读取历史，但历史 edition 不混入默认结果。索引记录必须保存 registry generation、canonical doc_id、package locator、edition_id 与 current 指针摘要。

### 13.2 索引投影与发布门（跨卷声明）

- PolicyBase_14 indexing 是本卷 current/edition 的**索引投影**，不是另一份消费权威；其 `record_hash.body` 引用本卷 `normalized_lf_markdown_body`（§4.2），`record_hash.semantic_hash` 引用 PolicyBase_07。
- 只有 selected confirmed Markdown 与允许本地索引的 confirmed 附件文本进入 FTS。candidate、几何 JSON、diff、prompt、日志不得进入正文。
- 发布（export/redistribution）还必须通过 PolicyBase_04 发布门（publication gate、redistribution gate、外传授权）；本卷的 `publication_gate` operation 是 edition 内证据，不替代 PolicyBase_04 的运行时发布门。

### 13.3 删除与撤回

删除一个 edition 默认禁止；只有未被 current、parent、历史索引、operation 或保留策略引用，且有显式 GC 审计时才能清理非权威缓存。confirmed edition 属长期审计记录，不由普通 clean 命令删除。仓库撤回/隔离通过 PolicyBase_07 registry availability generation 表达，不冒充法规 validity 或 `edition_kind`，不直接删除包；恢复同样发布新 generation。

## 14. integrity 拒绝条件

至少拒绝：

- current 缺失、悬空、指向未确认或 gate 失败 edition；
- active identity entry 的 locator/current 缺失，alias 成环/多目标，或 withdrawn/quarantined 被默认消费；
- current 引用的 switch event 缺失、payload hash 不符、事件链断裂或成环；
- doc/edition ID 与目录、frontmatter、manifest 不一致；
- edition 内容被原地修改、payload hash 不符；
- parent 悬空、跨 doc 或成环；
- 未登记文件、重复 id/path、hash/size 不符；
- path escape、绝对路径、symlink 或设备文件；
- derived_from 悬空/成环；
- 空派生物、成功 operation 无输出、失败无 error_code；
- candidate 角色被标记为可索引/可发布；
- `content_confirm` 缺失或 selected hash 不等于 `index.md`；
- 外传授权无效、合规 gate 缺失或 `disclosure_ok/sensitivity_ok/pii_ok` 任一非 true；
- `switch_kind` 取值不在本卷 §4.4 七值枚举内；
- rollback 删除或修改历史 edition；
- expected predecessor/CAS 不匹配却覆盖 current，或首次 recovery 引用不存在的旧 edition；
- 旧式就地 correction 修改已发布文件。

退出码：0 通过；1 数据违规；2 命令、配置、I/O 或验证环境错误。

## 15. 验收合同

golden 至少覆盖：首次写入及每个 crash point、source update、correction、reprocess、redaction、rollback、双 writer CAS、切换崩溃恢复、P3 无索引成功、P4 同步索引失败窗口拒绝读取并回切、异步索引 freshness 隔离、相同完整 payload 幂等、相同内容不同 evidence 得到不同 edition、canonical serialization golden bytes、parent 环、current 悬空、旧 edition 字节不变、identity registry migration、candidate 不可消费、模型授权失效、withdraw/quarantine/restore 而不删除历史。

```bash
policybase verify integrity
pytest tests/golden/document_package/
```

## 16. 不变量

1. 已确认 edition 永不原地修改。
2. current 是单一原子指针，不是 edition 字段。
3. correction/update/reprocess/redaction 都创建 edition；rollback/recovery 选择旧 edition 或修正指针，不创建内容 edition。
4. 原件不被派生物替代。
5. 未确认、未授权、合规失败的内容不被索引或发布。
6. edition-bound operation、file 与授权事实只在 manifest 维护一份；非 edition 运行/失败事实只在 acquisition ledger 或包外 audit event 维护。
7. identity migration、alias、availability 由 PolicyBase_07 registry 原子 generation 管理，不改写历史包。
8. default consumer 必须执行 registry/current/index freshness barrier。
9. `switch_kind` 取值集合恒为 §4.4 七值；`edition_kind` 取值集合由 PolicyBase_06 owner，二者前 5 值同名同语义对齐。
