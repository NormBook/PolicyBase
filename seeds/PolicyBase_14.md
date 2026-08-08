# PolicyBase 索引、中文检索、历史版与导出

> 状态：主权威
> 分卷编号：PolicyBase_14
> 主题：indexing
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷是 **SQLite FTS5、中文 analyzer、索引投影、`record_hash` 全字段 frame、关系索引、JSONL 发布镜像、重建迁移** 的唯一 owner。索引只消费 PolicyBase_09 正式包的 current.json 投影（current 的业务权威归 09），不决定采集、去重、OCR、确认、合规结论或身份审计。

不变量（本卷守护 §1）：

- **SQLite 是检索主产物；所有索引均可从文献包确定性重建，不是业务权威。** 删除索引不删除文献；撤回不抹历史。
- 默认搜索只返回 current edition；历史版必须显式请求。保留历史不得污染普通结果。

非职责（一句引用，不展开）：

- `current.json` 的业务权威、edition 文件权威、`normalized_lf_markdown_body` 规范化规则 → 见 PolicyBase_09 §storage.authority。
- `registry_entry_semantic_hash` 算法、canonical_doc_id、identity/availability event → 见 PolicyBase_07 §22。
- candidate/ingest/index 合规门的 PII/未确认文本/未授权文件不进索引的判定规则 → 见 PolicyBase_04 §7。
- candidate 不可索引的文件角色与内容生产状态机 → 见 PolicyBase_09 文件角色 + PolicyBase_13 内容生产状态机。

## 2. 迁移目标

| 目标 | 内容 |
|---|---|
| `docs/specs/index.md` | 索引与查询规格 |
| `data/schemas/indexer.schema.json` | schema、analyzer、ranking、发布投影 |
| `data/vocabularies/relation_types.yaml` | 关系枚举 |
| `src/policybase/pipeline/indexers/` | SQLite/FTS/历史/关系 |
| `src/policybase/pipeline/exporters/` | JSONL 与其他发布格式 |
| `tests/golden/index/` | normal/edge/error/migration |

## 3. 索引产物与版本

```text
_indexes/search.sqlite
_indexes/docs.jsonl
_indexes/index-manifest.json
```

`index-manifest.json` 至少记录：schema version、analyzer profile/version/hash、ranking profile/version/hash、PolicyBase_07 registry generation、projected current-set hash、source snapshot hash、freshness、构建时间、tool revision。任一不兼容版本变化必须走 §14 的可审计 `reindex`，不得在旧索引上混写不同分词结果。

## 4. 数据表（current 的索引投影）

本节是 `docs_meta` / `editions_meta` / `index_state` 表的唯一 owner。投影源是 PolicyBase_09 `current.json` 与 edition manifest；本卷不重定义 current 的业务字段语义，只定义其在检索层的列形态与排除规则。

### 4.1 current 文献表

```sql
CREATE TABLE docs_meta (
  doc_id TEXT PRIMARY KEY,
  registry_entry_hash TEXT NOT NULL,
  package_locator TEXT NOT NULL,
  edition_id TEXT NOT NULL,
  current_pointer_hash TEXT NOT NULL,
  previous_edition_id TEXT,
  type_prefix TEXT NOT NULL,
  title TEXT,
  document_number TEXT,
  document_number_normalized TEXT,
  issuer TEXT,
  issuers_json TEXT,
  issue_date TEXT,
  publish_date TEXT,
  effective_date TEXT,
  effective_until TEXT,
  validity_status TEXT,
  classification_system TEXT,
  hierarchy TEXT,
  subtype TEXT,
  profile_status TEXT,
  spatial_codes_json TEXT,
  spatial_labels_json TEXT,
  subjects_json TEXT,
  document_form TEXT,
  source_ids_json TEXT,
  source_domains_json TEXT,
  sources_json TEXT,
  relations_json TEXT,
  availability_status TEXT,
  classification_level TEXT,
  disclosure_mode TEXT,
  search_quality TEXT,
  index_status TEXT NOT NULL,
  pii_detected INTEGER DEFAULT 0,
  record_hash TEXT NOT NULL,
  analyzer_profile TEXT NOT NULL,
  language TEXT
);

CREATE TABLE index_state (
  singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
  registry_generation_id TEXT NOT NULL,
  projected_current_set_hash TEXT NOT NULL,
  analyzer_profile_hash TEXT NOT NULL,
  freshness TEXT NOT NULL CHECK (freshness IN ('fresh','stale','rebuilding'))
);
```

`classification_level` / `disclosure_mode` 的枚举语义归 PolicyBase_04，本表只投影存储。`validity_status` 枚举归 PolicyBase_06。`availability_status` 来源归 PolicyBase_07 identity registry。

### 4.2 edition 历史表

```sql
CREATE TABLE editions_meta (
  registry_entry_hash TEXT NOT NULL,
  package_locator TEXT NOT NULL,
  doc_id TEXT NOT NULL,
  edition_id TEXT NOT NULL,
  parent_edition_id TEXT,
  edition_kind TEXT NOT NULL,
  is_current INTEGER NOT NULL,
  created_at TEXT,
  content_hash TEXT NOT NULL,
  record_hash TEXT NOT NULL,
  title TEXT,
  validity_status TEXT,
  source_observation_hashes_json TEXT,
  PRIMARY KEY (doc_id, edition_id)
);
```

历史表是检索投影，不替代 PolicyBase_09 edition manifest。默认 FTS 只为 current 建行。是否建立独立历史 FTS 由版本化 index profile 显式启用；未启用时历史正文通过 `show --edition` 直接读包。

## 5. FTS5 与中文 analyzer profile

```sql
CREATE VIRTUAL TABLE docs_fts USING fts5(
  doc_id UNINDEXED,
  edition_id UNINDEXED,
  title,
  body,
  document_number,
  issuer,
  subjects,
  tokenize='unicode61'
);
```

应用层 analyzer 预分词，SQLite 使用 `unicode61` 保存 token。analyzer 必须是版本化 profile，至少记录：

- tokenizer backend/package/version；
- user dictionary 内容 hash；
- 法规简称、机关别名和同义词表版本/hash；
- Unicode version、繁简策略和标点/数字策略；
- query 与 document 是否使用同一 tokenizer；
- 降级策略。

P3/P4 基线可以是 `jieba-v1`；jieba 不可用时只允许显式 `unicode61-degraded-v1`，`search_quality=degraded`，不能与标准索引在同一次构建中混用。profile 变化强制全量 rebuild（执行细节见 §14）。

文号同时保存原始、normalized 和 canonical 精确字段；精确文号查询优先结构化等值/别名，不依赖中文分词。简称、同义词只扩展召回，不改文献元数据，不参与 PolicyBase_07 的 ID 或 PolicyBase_08 自动去重。

可选拼音、模糊、短语、高亮能力必须由新 analyzer/query profile 和 golden 晋升；实现不得隐式启用。

## 6. 可索引正文选择

默认正文为 current edition `index.md` 的 confirmed Markdown（**body 规范化规则归 PolicyBase_09 `normalized_lf_markdown_body`，本卷只引用，不重定义**），加上 manifest 明确允许本地索引的 confirmed 附件文本。必须同时满足：

- current 指针和 edition integrity 通过（合同见 PolicyBase_09）；
- content_confirm 有效且 selected hash 与 index.md 一致；
- 合规三项均 true（**判定规则见 PolicyBase_04 §7，本卷只引用结论**）；
- `local indexing access=true`；
- 非空且文件角色为可索引正文（**candidate 不可索引的文件角色判定见 PolicyBase_09；状态判定见 PolicyBase_13 内容生产状态机**）；
- analyzer profile 已锁定。

页/块 geometry 可用于结果定位，但 geometry、diff、prompt、日志和模型响应不得拼入 FTS body。索引器应保存命中正文到 `file_id/page/block_id` 的映射，使结果可回到原始页证据；无法定位的网页段落至少记录 source span。

## 7. 状态与排除

`index_status`：

| 值 | FTS | 发布镜像 |
|---|---|---|
| `indexed` | current 正文 | 仍需 publication gate |
| `metadata_only` | 无正文 | 仅允许元数据 |
| `needs_review` | 无 | 无 |
| `withdrawn` | 无 | 依发布策略仅状态元数据 |
| `pii_excluded` | 无 | 无 |

PII 新命中时（**PII/未确认文本/未授权文件不进索引的规则见 PolicyBase_04 §6 本地预检与 §7 index 合规门，本卷只执行结论**），同一事务必须原子完成三件事，缺一不得提交：（1）删除旧 FTS 行；（2）把 docs_meta 收缩为 `doc_id/edition_id/type/pii_detected/index_status/record_hash`；（3）**JSONL 发布镜像在同一事务内置 `stale=true` 并将该 doc 行移出可发布集合**，直至独立批次全量重写提交。`stale=true` 未清期间，publication gate（**规则见 PolicyBase_04 §7 发布门**）必须在导出侧/发布侧前置 barrier 拒绝任何命中或含旧 PII 文献的发布/导出请求，使 PII fail-closed 在索引侧、导出侧、发布侧三处同时硬闭合——异步窗口不得让含旧 PII 的 JSONL 行可被发布或导出。不得作为新 candidate 绕过 PolicyBase_04 入库门。恢复必须由新的 redaction edition 和新 gate 驱动。

confirmed/current edition 的合法性不以 `local indexing access` 为前提。local storage 获准但全文索引未获准时，PolicyBase_13 仍可确认/回滚该 edition，本卷必须投影为 `metadata_only` 或相应排除状态；不得把"不能全文索引"反向解释为"不能保留 confirmed edition"。尚无 active index 时，本卷投影状态为 `index_not_yet_applicable`，current 切换不调用不存在的索引器。

撤回、失效和来源不可达不是文件删除：法规效力使用 PolicyBase_06 `validity`，仓库撤回/隔离使用 PolicyBase_07 registry `availability`，二者正交投影并保留历史。普通索引更新不得因目录暂时缺失就永久抹掉审计事实；只有经 PolicyBase_07 identity/availability event 与 PolicyBase_09 存储合同共同授权的迁移/清理才能删除默认投影。

## 8. record_hash（全字段 frame 设计）

本卷是 `record_hash` 全字段 frame 设计的唯一 owner。`record_hash` 是增量正确性唯一依据；mtime/size 只诊断。current record hash 覆盖的 frame 序列：

```text
frame("doc_id", doc_id)
+ frame("registry_entry", registry_entry_semantic_hash)
+ frame("package_locator", package_locator)
+ frame("edition_id", edition_id)
+ frame("current_pointer", canonical current semantic projection including pointer hash)
+ frame("frontmatter", canonical_yaml(frontmatter))
+ frame("body", normalized_lf_markdown_body)
+ frame("manifest", index/publication semantic projection)
+ frame("profile", profile or <absent>)
+ frame("attachments", sorted confirmed indexed attachment frames)
+ frame("analyzer", analyzer profile hash)
```

字段归属裁定（本卷只 frame，不重定义被引算法）：

- `frame("registry_entry", registry_entry_semantic_hash)` 的算法 owner 是 **PolicyBase_07 §22**；本卷只调用其结果作为输入帧，不重定义。
- `frame("body", normalized_lf_markdown_body)` 的规范化规则 owner 是 **PolicyBase_09**；本卷只 frame 该规范化产物，不重定义 LF/空白/锚点规范化。
- `frame("current_pointer", …)` 的 current 语义投影权威归 **PolicyBase_09 `current.json`**。

frame 二进制规则：复用 PolicyBase_09 的固定形态 `utf8_byte_length(name):name utf8_byte_length(payload):payload`。数组按明确 ID/code point 排序；不得依赖文件遍历、manifest 顺序或 locale。纯审计时间/actor/log 不进入 current hash；会改变可消费性、内容、授权、current 或 analyzer 的字段必须进入。

record_hash 相同跳过；不同则在同一 SQLite 事务更新 docs_meta、FTS、edition current flag、relations 和 `index_state`。每个 doc 投影保存稳定 registry entry hash、package locator 和 PolicyBase_09 current pointer hash；全局 generation 只保存在 index_state/manifest。

`projected_current_set_hash` 固定为：只取当前 registry 的 canonical entries，按 canonical_doc_id Unicode code point 排序，逐项 `frame("entry", registry_entry_semantic_hash)` 后连接并 SHA-256；alias 列表由 PolicyBase_07 校验，不进入默认 current set。空集合按空字节 SHA-256，禁止使用文件遍历、locale 或数据库返回顺序。

全局 `registry_generation_id` 只进入 `index_state` / `index-manifest`，不进入每个 doc 的 record_hash；否则一次 generation 变化会强迫全库重写。增量事务只更新 entry semantic hash 变化的行，未变化行允许来自更早投影批次但其稳定 entry hash 必须仍匹配；事务结束时统一更新 global generation/current-set hash/freshness。

所有 list/search/export 读路径必须先解析当前 registry/current，再比较 `index_state.registry_generation_id/projected_current_set_hash/freshness` 以及命中文献的 `registry_entry_hash/current_pointer_hash`。完全一致才可返回索引结果；不一致稳定返回 `temporarily_unavailable_stale_projection`，不得把新 current 与旧索引拼接。同步模式在 current 切换后的事务窗口也执行该 barrier，失败后由 PolicyBase_09 回切；异步模式持续 stale 直到完整投影事务提交。current 切换失败不得留下可消费的新旧混合行。

## 9. 查询边界

默认：

```text
current_only=true
include_history=false
include_withdrawn=false
```

显式能力：

- `--edition EDITION_ID`：读取指定 doc 的具体 edition；
- `--history`：列出 edition timeline，不把每版当普通独立文献；
- `--as-of TIMESTAMP`：选择该时间点当时的 current edition；
- `--include-withdrawn`：包括撤回状态；
- `--diff FROM..TO`：从 edition artifact/diff 投影差异。

历史查询结果必须显示 `doc_id/edition_id/is_current/edition_kind`。默认列表计数按 doc，不按 edition。导出历史必须显式 `--history` 且通过各 edition 的 publication gate。

## 10. 搜索排序

基线为 FTS5 `bm25()`，确定性全序：

```text
score DESC,
(effective_date IS NULL) ASC,
effective_date DESC,
title COLLATE BINARY ASC,
doc_id COLLATE BINARY ASC
```

SQLite bm25 负值先取负，并在过滤后的完整候选集合归一化；单项或无方差为 1。结构化 validity/recency/hierarchy 权重只能在版本化 ranking profile 中启用，枚举、基准日、缺失值和衰减必须完整。混合体系不启用 hierarchy 效力权重。

## 11. 空间、主题和来源查询

PolicyBase_06 `spatial_scope.codes[]/labels[]` 分别投影 canonical JSON。精确地域过滤优先 codes，labels 用于展示/召回。`subjects[]` 投影为 JSON 和 FTS subject token，不压成业务权威字符串。

多来源不得只保留一个 source_id；`source_ids_json/source_domains_json` 均为去重排序数组。source 过滤对任一来源命中。四库（zcwjk/gz/flk/xxgk）下同一字段的取值域/来源差异由来源矩阵（PolicyBase_10）与 profile 决定，本卷只投影，不在索引层重写差异。

## 12. 关系索引

基础表只写正向和对称关系：

```text
forward: based_on, implements, authorizes, amends, supersedes,
repeals, partial_repeal_of, replaces, publishes, forwards, attachment_of,
part_of, cites, interpreted_by, replies_to, succeeds, ratified_by,
listed_in_registry, next_cycle
symmetric: conflicts_with, parallel_document
```

反向由显式映射视图派生：`basis_for/implemented_by/authorized_by/amended_by/supersedes_by/repealed_by/replaced_by/published_by/forwarded_by/has_attachment/has_part/interprets/replied_by/succeeded_by/ratifies/lists/previous_cycle`。`alias_of` 只属于 PolicyBase_08 的身份层 decision 审计，不得写关系表。派生边导出时标 `derived=true`，不得反写 edition。正向和派生反向名称与 PolicyBase_06 §10 的受控关系类型一致。

## 13. JSONL 与发布

JSONL 是 current 可发布记录镜像，默认一 doc 一行并包含 `edition_id`。可发布字段来自 docs_meta 固定映射；JSON 字符串列必须解析为对象/数组后 canonical 输出。不得发布 record_hash、路径、内部状态、PII、prompt、模型日志、未授权全文、candidate 或审计正文。

SQLite 事务后置 `stale=true`；JSONL 在独立批次全量写临时文件并原子 rename。失败保留旧完整文件并保持 stale；发布端拒绝 stale。字段级 canonical hash 对账，不得只比行数。

JSONL 批次写出前必须确认无 `stale=true` 标记的 PII 撤下未决（见 §7 PII fail-closed 三处硬闭合）。publication gate（**规则见 PolicyBase_04 §7 发布门**）在 JSONL 镜像存在任一 `stale=true` PII 撤下行未清时，必须前置 barrier 拒绝整批 JSONL 发布/导出；异步全量重写完成并清除 `stale=true` 前不得降级为"部分发布"。

## 14. 重建与迁移（analyzer version → 可审计 reindex）

唯一全量命令：

```bash
policybase index --rebuild
```

重建先写新 SQLite/JSONL/manifest 到 staging，完成 schema、数量、字段 hash、registry/current-set hash、FTS 排除和抽样查询后原子切换整个索引集合。切换前 freshness=`rebuilding` 且消费者继续使用仍匹配 current 的旧集合，否则拒绝；失败保留旧索引并按 hash 决定 fresh/stale。analyzer/schema 不兼容时普通增量命令必须拒绝并提示 rebuild。

可审计 reindex 合同：

- rebuild 触发条件之一即 §5 analyzer profile version/hash 变化、§4 schema version 变化、`projected_current_set_hash` 与当前 registry 不一致超阈值、或人工 `--rebuild`。
- 每次 rebuild 必须把旧 manifest 留档（analyzer/ranking/registry generation/构建时间），并在新 manifest 记录 `rebuild_reason` 与触发 actor；rebuild 不删除 edition 文件，只换索引集合。
- rebuild 跨 freshness `fresh→rebuilding→fresh`，任一中间态消费者按 §8 stale barrier 处理；rebuild 不得在 `rebuilding` 期间被另一次 rebuild 抢占，须先完成或失败回滚。
- 降级路径：jieba 标准索引 rebuild 失败时，不允许隐式回退 `unicode61-degraded-v1`；降级必须由独立 rebuild 显式声明 analyzer profile，并在 manifest 标 `search_quality=degraded`。

## 15. 验收合同

golden 至少覆盖：current-only、edition history/as-of/diff、rollback 重投影、analyzer version mismatch 强制 rebuild、jieba 标准与 unicode61 显式降级、文号精确查询、地域 codes、多主题、多来源、页块定位、PII 撤下、withdrawn 保留历史、JSONL 字段级一致性、关系反向派生和稳定分页。

```bash
policybase index --check
policybase index --rebuild
pytest tests/golden/index/
```

## 16. 不变量

1. 默认只搜 current；历史必须显式。
2. 索引记录绑定 registry generation、package/current pointer、edition_id 和 analyzer version。
3. 未确认、未授权、合规失败内容不进 FTS/发布（规则见 PolicyBase_04）。
4. analyzer 变化全量重建，不能混合质量。
5. 删除索引不删除文献；撤回不抹历史。
6. JSONL 是镜像，不是反向写入源。
7. `registry_entry_semantic_hash` 算法归 PolicyBase_07；`normalized_lf_markdown_body` 规范化归 PolicyBase_09；本卷只 frame，不重定义。
