# PolicyBase CLI：查询、展示与导出参数合同

> 状态：主权威
> 分卷编号：PolicyBase_16
> 主题：cli-query-export
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷是 `policybase list` / `policybase show` / `policybase export` 三个公开子命令的**绑定参数、参数合同、组合规则、输出合同、禁止参数、版次选择模型、Filter 语义、业务诊断码、组合测试矩阵与示例**唯一 owner。

本卷不定义、不复制以下主题，遇到只一句引用：

- 全局 CLI 词法、配置发现、命令域路由、跨命令标识、`--dry-run` 适用矩阵、阶段演进 —— 见 PolicyBase_15 §命令域路由 与 §`--dry-run` 适用规则路由。
- 解析早拒绝序、通用 `cli_*` 诊断码（`cli_required_argument` / `cli_unknown_argument` / `cli_argument_format` / `cli_argument_range` / `cli_mutually_exclusive` / `cli_argument_dependency` / `cli_parameter_not_applicable` 等）、统一退出码 0/1/2/3 映射、依赖安装 —— 见 PolicyBase_19 §3 解析早拒绝序、§4 通用诊断码、§5 统一退出码。
- ID 生成语义与 canonical 形态（`DOC_ID` / `EDITION_ID` / `SOURCE_ID` / `AUTH_ID` 的格式串、长度、Tier 计算）—— 见 PolicyBase_07 §5 基本 ID 与 §15 canonical key；CLI 词法投影见 PolicyBase_15 §跨命令标识（ID CLI 词法投影）。
- 索引字段定义、FTS5 analyzer profile、可索引正文选择、record_hash、查询边界、ranking profile —— 见 PolicyBase_14 §4 current 文献表、§5 FTS5 与中文 analyzer、§6 可索引正文、§9 查询边界、§10 搜索排序。
- 元数据字段下限、edition_kind、validity、spatial_scope、frontmatter 安全投影 —— 见 PolicyBase_06。
- edition 文件权威、current.json、switch chain、不可变包、operations —— 见 PolicyBase_09。
- 公开性 / PII / 密级 / 授权 / publication gate 业务规则 —— 见 PolicyBase_04。
- 内容生产状态机、内容层 review decision —— 见 PolicyBase_13。
- `source` / `scrape` / `import` / `prepare` 绑定 —— 见 PolicyBase_17；`process` 11 子命令绑定 —— 见 PolicyBase_18；`index` / `verify` 绑定 —— 见 PolicyBase_19。

三个命令均不得：

- 修改文献包、edition、`current.json`、索引或来源注册表；
- 触发采集、OCR、模型、自动修复、索引 rebuild 或依赖安装；
- 把 candidate、needs_review、未确认内容当作正式查询结果；
- 提供绕过 PII、publication gate、redistribution 或历史保留策略的开关。

`export` 会在用户指定目录创建发布产物，因此是「发布写入命令」，但**不写业务权威**。

退出码映射（0 成功 / 1 业务或门禁拒绝 / 2 用法配置环境错误 / 3 合同允许的 partial export）由 PolicyBase_19 §5 统一定义；本卷诊断码表的 `exit` 列只是对该映射的引用。

## 2. 绑定前置与词法引用

参数在访问 SQLite、读取文献包或创建目录之前完成词法、长度、类型、互斥和依赖校验。非法输入不得被「尝试执行后再解释」。

### 2.1 标识符（引用）

`DOC_ID`、`EDITION_ID`、`SOURCE_ID`、`AUTH_ID` 的生成语义、canonical 形态、长度与字符集**不在本卷重定义**：

- 生成语义与 canonical 形态：见 PolicyBase_07 §5 基本 ID 与 §15 canonical key。
- CLI 词法投影（参数位置上的形态检查、scope 路由）：见 PolicyBase_15 §跨命令标识（ID CLI 词法投影）。

本卷只在词法正确后讨论**业务语义**：词法正确但不存在的对象是**业务错误**（exit 1），词法错误是**用法错误**（exit 2）。`DOC_ID` 的 collision 扩展形式由 PolicyBase_07 schema 判定，CLI 不自行截断或补齐。`SOURCE_ID` 不得接受省名、域名或显示名称作为别名。

| 名称 | 本卷业务用途 |
|---|---|
| `DOC_ID` | `show` 的唯一 positional；`export --doc` 的目标 |
| `EDITION_ID` | `--edition` / `--diff A..B` 的版次定位 |
| `SOURCE_ID` | `list --source` / `export --filter 'source:…'` 的来源过滤值 |
| `CURSOR` | CLI 返回的不透明 base64url 分页 token；1..2048 ASCII bytes；不得自行拼接；query hash 或 index generation 不匹配即拒绝 |

### 2.2 时间和年份

- `TIMESTAMP` 只接受 RFC 3339，必须带 `Z` 或显式 UTC offset；拒绝无时区时间、闰秒和本地化日期。
- CLI 将 timestamp 规范为 UTC 后比较 switch event 的 `switched_at`；相同时间按 event chain 顺序判定，不能按文件 mtime。
- `--year` 为十进制整数 `1900..当前 UTC 年+5`，不接受 `24`、`2024.0`、范围字符串或前后空白。范围越界归 `cli_argument_range`（→ PolicyBase_19 §4）。

### 2.3 文本

| 参数 | Unicode scalar 数 | 规则 |
|---|---:|---|
| `--keyword` | 1..256 | trim 后非空；最多出现 8 次；多次为 AND |
| `--issuer` | 1..256 | trim 后非空；精确字段过滤，不执行 shell/SQL pattern |
| `--subject` | 1..128 | 最多 16 次；多次为 AND |
| `--filter` | 1..4096 | UTF-8；使用版本化 filter parser（§3）；禁止裸 SQL、注释、分号和未知字段 |

所有文本拒绝 NUL、C0/C1 控制字符、孤立 surrogate、双向覆盖字符和无效 UTF-8。展示文字可以包含正常中文标点；参数不得被 shell 再解释。

### 2.4 枚举与数量

| 参数 | 受控值/范围 | 默认 |
|---|---|---|
| `--type` | PolicyBase_05 已晋升 TYPE 名或前缀 | 无 |
| `--validity` | PolicyBase_06 `validity.status` | 无 |
| `--spatial-code` | 6 位 ASCII 数字 | 无 |
| `--limit` | 1..1000 | `list=20`，`show --history=50` |
| 全局 `--output` | `text\|json` | TTY 为 text；非 TTY 仍为 text，自动切换禁止 |
| `export --format` | `jsonl\|csv\|markdown\|site` | `jsonl` |
| `show --attachments` | flag | false |
| `export --attachments` | `none\|metadata\|files` | `none` |

全局 `--output` 必须按 PolicyBase_15 命令域规则位于 command 之前，控制 CLI 控制面输出，**不等于** `export --format`。例如 `policybase --output json export --format markdown ...` 表示写 Markdown 产物，并在 stdout 返回 JSON 执行摘要。放在 command 后的 `--output` 必须作为位置错误拒绝，不得迁就解析。

## 3. Filter 语义

filter grammar 必须版本化，P4 基线记为 `query-filter-v1`。Filter **字段集**引用 PolicyBase_14 索引字段（§4 current 文献表、§9 查询边界、§11 空间主题与来源查询），不在本卷重定义字段域或取值范围。允许字段名至少包括：

```text
title, keyword, document_number, issuer, type, hierarchy, subtype,
validity, issue_date, publish_date, effective_date, spatial_code,
subject, source, availability, language
```

各字段的语义、来源列、可索引性与四库差异以 PolicyBase_14 为准；本卷只规定**操作符与解析规则**。

允许操作符仅为：

```text
field:value
field="quoted value"
issue_date>=YYYY-MM-DD
issue_date<=YYYY-MM-DD
AND OR NOT ( )
```

解析规则：

1. 字段名、操作符和枚举大小写敏感，未知字段立即拒绝（→ `cli_argument_format`，PolicyBase_19 §4）。
2. 相邻表达式不得隐式 AND；必须显式写 `AND`，避免漏写造成范围扩大。
3. `--filter` 与专用筛选参数（`--keyword` / `--type` / `--issuer` / `--source` / `--year` / `--validity` / `--spatial-code` / `--subject` / `--include-withdrawn`）可以组合，整体为 AND。
4. 同一专用参数多次出现时，只有 §2.3 明确允许的参数（`--keyword` / `--subject`）可重复；其他重复立即拒绝。
5. parser 产生参数化 AST；不得把 filter 拼成 SQL。
6. 最大 AST 深度 16、节点数 256、OR 分支 64；超限以用法错误拒绝（→ `cli_argument_range`）。
7. 字符串里的 `*`、`%`、`_` 是普通字符；v1 不支持通配和 regex。

纠正提示必须包含未知 token 的位置和一个合法示例，但不得回显控制字符或完整敏感输入。

## 4. 版次选择模型

所有命令默认选择 current。以下五种 selector 互斥：

| selector | 语义 |
|---|---|
| 无 selector | 读取执行开始时快照中的 current |
| `--edition EDITION_ID` | 读取指定 doc 的一版；必须属于该 doc |
| `--as-of TIMESTAMP` | 读取该时刻已生效 switch chain 所指 edition |
| `--history` | 读取该 doc 或结果集的全部可见 confirmed edition timeline |
| `--diff A..B` | 比较同一 doc 的两个 confirmed edition |

具体规则：

1. `--edition`、`--as-of`、`--history`、`--diff` 任意两个同时出现，解析阶段即拒绝（→ `cli_mutually_exclusive`）。
2. `A..B` 两端必须是完整 `EDITION_ID`（形态见 PolicyBase_07 §5、PolicyBase_15 §跨命令标识），恰好一个 `..`；不接受 `current`、空端点、范围或跨 doc edition。
3. `--as-of` 选取 `switched_at <= timestamp` 的有效链尾；时间早于 initial 时返回 `query_no_edition_as_of`，不得回退到最早版。
4. `--history` 按 switch chain 和 edition lineage 展示，不把回滚伪造成新 edition；回滚作为 switch event 单独显示。
5. current 在命令开始后发生变化时，单次命令仍使用开始时锁定的 index/package snapshot；摘要返回 `snapshot_id`。
6. edition 保存在本地不等于可展示或可发布。每一版都按查询时的最新安全/PII/publication 决策重新判定（业务规则见 PolicyBase_04）。

## 5. `policybase list`

### 5.1 语法

```text
policybase list
  [--keyword TEXT]... [--filter EXPR]
  [--type TYPE] [--issuer TEXT] [--source SOURCE_ID]
  [--year YEAR] [--validity STATUS]
  [--spatial-code CODE] [--subject TEXT]...
  [--include-withdrawn]
  [--limit N] [--cursor CURSOR]
```

`list` 查询 current 索引（投影见 PolicyBase_14 §4），每篇文献最多一行/一个 item；**不接受任何 edition selector**。

### 5.2 参数合同

| 参数 | 必填 | 行为 |
|---|---|---|
| `--keyword` | 否 | analyzer 查询（profile 见 PolicyBase_14 §5）；多次为 AND |
| `--filter` | 否 | §3 表达式 |
| `--type` | 否 | exact TYPE/前缀，不做模糊映射 |
| `--issuer` | 否 | issuer 原名/确认别名的结构化匹配 |
| `--source` | 否 | 完整注册 `SOURCE_ID`（生成语义见 PolicyBase_07；注册身份见 PolicyBase_10）；存在性在查询前验证 |
| `--year` | 否 | 等价于 `issue_date` 的 UTC 公历年；不回退到 publish year |
| `--validity` | 否 | exact enum（取值域见 PolicyBase_06） |
| `--spatial-code` | 否 | 对 `spatial_scope.codes[]` exact match（字段定义见 PolicyBase_06 / PolicyBase_14 §11） |
| `--subject` | 否 | 对 `subjects[]` exact/受控别名匹配（字段来源见 PolicyBase_14 §11）；多次为 AND |
| `--include-withdrawn` | 否 | 加入 withdrawn current 的安全元数据；不自动显示正文 |
| `--limit` | 否 | 本页最多结果数 |
| `--cursor` | 否 | 继续 token 内封装的原 query/sort/snapshot；与全部筛选参数和 `--limit` 互斥 |

空筛选合法，表示列出可见 current 文献；仍受 `--limit`。**不提供 `--all` 或无限 limit**。

### 5.3 排序与分页

排序唯一采用 PolicyBase_14 §10 ranking profile 的确定性全序。用户不得在 v1 自定义排序。响应必须返回 `query_hash`、`snapshot_id`、`next_cursor|null` 和 `count`。

cursor 封装完整 canonical query、query hash、limit、ranking profile、index generation、last sort key 和过期时间；不得包含正文或 PII。调用方续页只传 `--cursor`，不得重复或修改筛选参数与 limit。以下情况拒绝 cursor，而不是静默重新从第一页开始：

- cursor 与任何筛选条件或 limit 同时出现；
- index generation/ranking profile 不兼容；
- cursor 损坏、过期或签名/HMAC 无效。

### 5.4 输出

text 每行最少显示：`doc_id`、title、issuer、issue_date、validity、current edition_id；正文、PII 命中值和内部路径不得显示。长字段按 Unicode grapheme 安全截断，JSON 不截断允许字段。

JSON item 至少包含：

```json
{"doc_id":"REG-a1b2c3d4e5","edition_id":"ed-0123456789abcdef01234567","title":"…","issuer":"…","issue_date":"2024-01-01","validity":"effective","withdrawn":false}
```

无结果是成功：退出 0，items 为空。索引 stale、schema/analyzer 不兼容或安全投影失败**不是**「无结果」，必须非零退出。

### 5.5 禁止参数

`list` 拒绝：`--edition`、`--as-of`、`--history`、`--diff`、`--attachments`、`--target-dir`、`--format`、`--raw`、`--include-candidate` 和 positional `DOC_ID`（→ `cli_unknown_argument`）。

## 6. `policybase show`

### 6.1 语法

```text
policybase show DOC_ID
  [--edition EDITION_ID | --as-of TIMESTAMP | --history | --diff A..B]
  [--metadata] [--body] [--relations] [--attachments]
  [--include-withdrawn]
  [--limit N] [--cursor CURSOR]
```

`DOC_ID` 恰好一个且必填（词法见 PolicyBase_07 §5 / PolicyBase_15 §跨命令标识）。禁止从 stdin 猜 ID、接受路径，或把 title 当 ID 搜索。

### 6.2 展示 section

不指定 section 时：

- 普通 current/edition/as-of：等价于 `--metadata --body`；
- `--history`：timeline，不隐式输出每版正文；
- `--diff`：等价于比较 metadata + body；
- withdrawn：只有显式 `--include-withdrawn` 才返回，且默认只返回安全元数据和撤回状态。

显式 section 可组合：

| section | 内容 |
|---|---|
| `--metadata` | PolicyBase_06 可展示字段的安全投影 |
| `--body` | selected confirmed Markdown（正文来源见 PolicyBase_14 §6） |
| `--relations` | PolicyBase_14 §12 正向/派生关系，标记 `derived` |
| `--attachments` | 仅附件清单、role/media type/hash/可见性，不把附件字节写 stdout |

`--history` 禁止与四个 section 参数组合；timeline 字段固定。`--limit/--cursor` 只适用于 `--history`，与 current、`--edition`、`--as-of` 或 `--diff` 组合必须在解析阶段拒绝（→ `cli_parameter_not_applicable`，PolicyBase_19 §4）。`--diff` 只允许 `--metadata` 和/或 `--body`，禁止 `--relations`、`--attachments`、`--limit`、`--cursor`。

### 6.3 history

`show DOC_ID --history` 返回 edition lineage 和 current switch timeline（edition/switch 字段权威见 PolicyBase_09）：

- edition：edition_id、kind、parent、created_at、content hash、是否 current；
- switch：event_id、from/to、kind、switched_at、reason 的安全摘要；
- 分页：`--limit` 1..1000，默认 50；`--cursor` 规则同 §5.3。

禁止输出 actor 的个人信息、内部 evidence 路径、prompt、模型日志、原始 PII 或授权凭据。历史为空不可能出现在合法 doc；结构损坏返回 integrity 错误，不得伪造 initial。

### 6.4 as-of 与 diff

`--as-of` 读取当时 current，而不是「created_at 最近的 edition」。如果后来发现该历史内容含 PII 或禁止公开，仍须按当前 gate 遮蔽或拒绝正文（业务规则见 PolicyBase_04）。

`show` 的正文和附件读取依据 local-view/local-storage access 与当前安全、PII 决策，不要求 redistribution 权限；但这不允许显示被拒绝的正文。元数据也必须走安全投影：PII 命中后最多返回 PolicyBase_14 收缩后的安全 envelope，不得因 `--metadata` 回显原 frontmatter 敏感字段。

`--diff A..B`：

- 两个 edition 必须属于 positional `DOC_ID`；
- A 是基线、B 是目标，方向不得自动排序；
- metadata 使用 canonical field-aware diff；body 使用 normalized LF Markdown unified diff（normalized body 见 PolicyBase_09）；
- text 输出路径标签固定为 `A/index.md` 和 `B/index.md`，不暴露本地绝对路径；
- identical 为成功，退出 0，并明确 `different=false`；
- 任一版正文不可展示时，请求 body diff 整体拒绝，不得通过差异泄露片段；用户可改用 `--metadata`。

### 6.5 对象不存在与撤回

- doc 不存在：`query_doc_not_found`，退出 1；
- edition 存在但不属于 doc：统一返回 `query_edition_not_in_doc`，不得透露它属于哪个 doc；
- current withdrawn 且未给 `--include-withdrawn`：`query_withdrawn_excluded`，提示重试参数；
- `--include-withdrawn` 不授予正文读取权，正文仍按 access/publication/PII gate 判定（见 PolicyBase_04）。

### 6.6 禁止参数

`show` 拒绝 `--filter`、`--keyword`、`--source`、`--year`、`--format`、`--target-dir`、`--edit`、`--raw`、`--candidate`、`--prompt` 和任何写入/确认参数（→ `cli_unknown_argument`）。

## 7. `policybase export`

### 7.1 语法

```text
policybase export
  (--doc DOC_ID | --filter EXPR)
  [--edition EDITION_ID | --as-of TIMESTAMP | --history | --diff A..B]
  [--include-withdrawn]
  [--attachments none|metadata|files]
  [--metadata-only]
  [--format jsonl|csv|markdown|site]
  --target-dir DIR
  [--allow-partial]
  [--dry-run]
```

`--doc` 与 `--filter` 恰好一个必填。**禁止无 selector 导出整个库**；导出全库必须显式写可审计的 `--filter 'type:… OR …'`，v1 不提供恒真表达式。`--target-dir` 必填，即使 `--dry-run` 也必须完成路径校验。`--dry-run` 适用规则路由见 PolicyBase_15。

### 7.2 selector 组合

| 组合 | 是否允许 | 说明 |
|---|---|---|
| `--doc DOC_ID`，无 edition selector | 是 | 导出 current |
| `--doc` + `--edition` | 是 | edition 必须属于 doc |
| `--doc` + `--as-of` | 是 | 导出当时 current |
| `--doc` + `--history` | 是 | 导出该 doc 全部可发布历史版 |
| `--doc` + `--diff A..B` | 是 | 导出同 doc 差异 |
| `--filter`，无 selector | 是 | 导出匹配 current |
| `--filter` + `--history` | 是 | 对每个匹配 doc 导出可发布历史版 |
| `--filter` + `--as-of` | 是 | 在同一 as-of snapshot 执行过滤和选版 |
| `--filter` + `--edition` | 否 | edition 不能应用于集合 |
| `--filter` + `--diff` | 否 | diff 必须绑定单一 doc |

`--as-of` + `--filter` 的过滤字段来自 as-of edition，不得先以 current 过滤再回看历史。

### 7.3 格式合同

| format | 正文 | 多记录 | attachments=files | 产物 |
|---|---|---|---|---|
| `jsonl` | 默认含获准正文 | 是 | 禁止 | UTF-8 LF，一 edition 一行 |
| `csv` | 禁止；隐含 metadata-only | 是 | 禁止 | RFC 4180 UTF-8，固定列 |
| `markdown` | 是 | 是 | 允许 | 每 edition 独立目录，`index.md` + 可选 assets |
| `site` | 是 | 是 | 允许 | 版本化静态站点结构和 manifest |

条件规则：

1. `--metadata-only` 与 `--attachments files` 冲突；与 `metadata` 合法。
2. `--attachments files` 只允许 markdown/site；每个附件还必须通过 redistribution gate（业务规则见 PolicyBase_04）。
3. `--diff` 只允许 jsonl/markdown；禁止 csv/site、history、attachments 和 metadata-only。
4. csv 固定为 metadata-only；显式 `--metadata-only` 可出现但不改变语义。
5. jsonl 的 `attachments=metadata` 只写可发布附件元数据，不写 base64/路径/文件内容。
6. markdown/site 中的资源引用必须是 target 内相对路径；禁止外部绝对路径和 `..`。
7. csv 只允许 `--attachments none`；附件元数据不得塞入未版本化自由文本列。

所有格式必须生成 `export-manifest.json`，至少包含 export schema/version、query hash、snapshot ID、format、created_at、tool revision、item doc/edition ID、每个文件 hash、publication decision refs 和 rejected item 摘要。manifest 不含密钥、绝对源路径、PII 值或未发布正文。

### 7.4 目标目录与原子性

`DIR`：

- UTF-8 path 总长 1..4096 bytes；拒绝 NUL、设备文件和 dangling/untrusted symlink；
- 必须不存在；其最近已存在父目录必须可写且位于用户明确提供的路径下；
- 不得等于仓库根、`data/documents`、`_indexes`、`.git` 或其中任何权威目录；
- 不执行 `~`、环境变量或 command substitution 展开；这些由调用 shell 显式完成。

导出先写同一文件系统的 sibling staging 目录，完成 schema、hash、publication 和路径检查后原子 rename 到尚不存在的 `DIR`。只要最终 `DIR` 已存在（即使为空）就以 `export_target_exists` 拒绝，从而避免删除、覆盖和跨文件逐项提交。**不提供 `--force`、`--overwrite` 或递归清空**。

`--dry-run` 可以只读索引/包并验证 gate，输出 planned paths/hashes；不得创建 target、staging、lock 或临时产物。dry-run 后数据改变，真实导出必须重新判定，不能复用授权结论。

### 7.5 partial 语义

默认全有或全无：任何 item 未通过 publication/redistribution/integrity gate，整个导出退出 1，不落最终目录。

`--allow-partial` 只允许 `--filter` 的多文献导出；与 `--doc`、`--diff` 冲突。启用后：

- 合法 item 写入，拒绝 item 只写安全摘要；
- 全部成功退出 0；部分成功退出 3；全部失败退出 1；
- manifest 记录 accepted/rejected 计数和每个拒绝项的稳定 code；
- 禁止把 gate 失败降级为 metadata-only，除非调用者本来显式请求 `--metadata-only` 且元数据本身可发布。

### 7.6 publication 与 PII 门

每个 edition、正文和附件分别检查（业务规则见 PolicyBase_04）：

1. edition confirmed、integrity 通过；
2. 当前有效 `disclosure_ok/sensitivity_ok/pii_ok` 均为 true；
3. 文件 `redistribution=true`；
4. publication gate 有效且覆盖目标格式/字段；
5. withdrawn 的发布策略允许，且调用者显式 `--include-withdrawn`；
6. history/as-of 也按查询时最新安全裁决检查，不能依赖历史时期的宽松决定。

任何 `--output json`、`--metadata-only`、`--history`、`--as-of`、`--allow-partial` 都不是授权开关。PII 命中值不得进入错误信息、manifest 或 rejected 摘要。

## 8. stdout、stderr 与副作用

### 8.1 text 模式

- `list/show` 成功内容写 stdout；普通诊断、纠正提示写 stderr。
- `export` 成功只向 stdout 写摘要和产物相对清单，文件正文只写 target。
- 失败且没有可用结果时 stdout 为空，单一主诊断写 stderr；必要的 secondary diagnostics 紧随其后。
- progress 只在交互 TTY 且显式全局启用时写 stderr；默认无进度噪声。

### 8.2 JSON 模式

全局 `--output json` 时 stdout 恰好一个 UTF-8 JSON object，换行结尾；成功、业务拒绝和用法错误均使用 PolicyBase_19 §4 通用 envelope。stderr 默认为空；只有无法构造 JSON 的进程级故障可写最小 ASCII 诊断。

`policybase --output json show ... --body` 必须把 Markdown 作为 JSON string 字段，不得在 envelope 前后输出裸正文。`policybase --output json export ...` 返回 manifest path、accepted/rejected、written paths 和 hashes，不嵌入导出正文。

### 8.3 副作用表

| 命令 | 网络 | 业务权威写入 | 索引写入 | 用户目标写入 |
|---|---|---|---|---|
| list | 禁止 | 无 | 无 | 无 |
| show | 禁止 | 无 | 无 | 无 |
| export --dry-run | 禁止 | 无 | 无 | 无 |
| export | 禁止 | 无 | 无 | 原子创建 target |

访问时间、最近查看、shell history 或「使用统计」不得偷偷写回文献包。必要的本地安全审计只能写 PolicyBase_19 约束的独立审计 sink；sink 失败是否 fail closed 由 PolicyBase_04 动作级策略决定，不得污染 stdout。

## 9. 业务诊断码

本节只列**业务诊断码**（query/content/export/pii/publication 维度）。通用 `cli_*` 诊断码（`cli_required_argument` / `cli_unknown_argument` / `cli_argument_format` / `cli_argument_range` / `cli_mutually_exclusive` / `cli_argument_dependency` / `cli_parameter_not_applicable` 等）由 PolicyBase_19 §4 唯一定义；本卷在 §2-§7 用法错误处一律改引用。退出码 0/1/2/3 的统一映射见 PolicyBase_19 §5；本表 `exit` 列只是引用。

稳定 diagnostic code 统一使用 lowercase snake_case。

| diagnostic code | exit | 条件 | 纠正提示 |
|---|---:|---|---|
| `query_doc_not_found` | 1 | doc 不存在 | 检查 ID 或用 list 查找 |
| `query_source_not_found` | 1 | `SOURCE_ID` 词法合法但未注册 | 用 `policybase source list`（绑定见 PolicyBase_17）获取完整 ID |
| `query_edition_not_in_doc` | 1 | edition 不属于 doc/不存在 | 检查 `show DOC_ID --history`；不泄露其他 doc |
| `query_no_edition_as_of` | 1 | 时间早于 initial/无有效 chain | 使用 history 查有效时间 |
| `query_withdrawn_excluded` | 1 | 未显式包括撤回 | 如有权限，添加 `--include-withdrawn` |
| `query_cursor_invalid` | 2 | 损坏/签名无效/查询不匹配 | 丢弃 cursor，从第一页重试 |
| `query_cursor_stale` | 1 | index generation 已变化 | 从第一页重试并记录新 snapshot |
| `query_index_stale` | 1 | 索引 stale/不兼容 | 由维护者运行 `policybase index --check`/`--rebuild`（绑定见 PolicyBase_19） |
| `query_integrity_failed` | 1 | package/current/edition 失败 | 运行 `policybase verify integrity`（绑定见 PolicyBase_19） |
| `content_access_denied` | 1 | 正文/附件不可展示 | 改为 metadata（若允许）或完成授权流程 |
| `pii_excluded` | 1 | 当前 PII 决策禁止 | 不回显命中值；走 redaction/review |
| `publication_gate_failed` | 1 | edition/字段/附件不能发布 | 输出安全 gate 摘要 |
| `export_target_exists` | 2 | target 已存在，包括空目录 | 使用尚不存在的新路径；无 force 建议 |
| `export_path_unsafe` | 2 | 权威目录、逃逸、symlink、设备文件 | 选择独立普通目录 |
| `export_io_failed` | 2 | staging/fsync/rename 失败 | 保留旧 target，报告安全恢复建议 |
| `export_partial` | 3 | `--allow-partial` 且部分成功 | 查看 manifest rejected 摘要 |

若同一次预检发现多个用法错误，primary diagnostic 按命令行 token 顺序选择；JSON 可包含全部 diagnostics，但不得继续访问索引或文件系统对象以搜集更多错误。

## 10. 参数组合测试矩阵

机器测试必须从声明式 matrix 生成 parser/help/golden，至少包含：

### 10.1 list

| case | 参数 | 预期 |
|---|---|---|
| L-N01 | 无参数 | 0，current 第一页 |
| L-N02 | keyword×2 + type + year | 0，全部 AND |
| L-N03 | filter + spatial-code + subject | 0，参数化 AST |
| L-E01 | `--limit 0` / `1001` | 2 `cli_argument_range`（→ PolicyBase_19 §4） |
| L-E02 | `--year 24` | 2 `cli_argument_range` |
| L-E03 | `--source hubei` | 2 `cli_argument_format`（词法见 PolicyBase_07/15），不映射简称；完整但未注册 ID 才是 `query_source_not_found` |
| L-E04 | unknown filter field / SQL comment | 2 `cli_argument_format` |
| L-E05 | `--history` | 2 `cli_unknown_argument` |
| L-E06 | cursor + 任一筛选/limit | 2 `cli_mutually_exclusive` |
| L-E07 | cursor 损坏/签名错误 | 2 `query_cursor_invalid` |
| L-X01 | withdrawn 未 include | 不出现在结果中 |
| L-X02 | 空结果 | 0，items=[] |

### 10.2 show

| case | 参数 | 预期 |
|---|---|---|
| S-N01 | DOC_ID | current metadata+body |
| S-N02 | `--edition E --attachments` | 指定版附件清单 |
| S-N03 | `--as-of RFC3339 --metadata` | 当时 current 元数据 |
| S-N04 | `--history --limit 10` | timeline 分页 |
| S-N05 | `--diff A..B --body` | 有方向 diff |
| S-X01 | identical diff | 0，different=false |
| S-E01 | 缺/多 positional DOC_ID | 2（`cli_required_argument`/`cli_argument_format`） |
| S-E02 | edition + as-of/history/diff | 2 `cli_mutually_exclusive` |
| S-E03 | history + body | 2 `cli_mutually_exclusive` |
| S-E04 | diff + attachments/cursor | 2 `cli_mutually_exclusive` |
| S-E05 | as-of 无时区 | 2 `cli_argument_format` |
| S-E06 | edition 属于其他 doc | 1 `query_edition_not_in_doc`，不泄露所有者 |
| S-E07 | body 命中 PII | 1 `pii_excluded`，stdout 不含片段 |
| S-E08 | withdrawn 无 include | 1 `query_withdrawn_excluded`，给显式纠正提示 |
| S-E09 | current/edition/as-of + limit/cursor | 2 `cli_parameter_not_applicable` |

### 10.3 export

| case | 参数 | 预期 |
|---|---|---|
| E-N01 | doc + target | current JSONL 原子导出 |
| E-N02 | filter + history + markdown | 每 edition 独立目录 |
| E-N03 | filter + as-of + csv | 以历史字段过滤，metadata only |
| E-N04 | doc + diff + markdown | diff artifact |
| E-N05 | site + attachments files | 每文件 gate + manifest |
| E-X01 | dry-run | 0，无任何文件/目录/lock |
| E-X02 | allow-partial 部分拒绝 | 3 `export_partial`，manifest 有安全摘要 |
| E-E01 | doc 与 filter 都无/都有 | 2（`cli_required_argument`/`cli_mutually_exclusive`） |
| E-E02 | filter + edition/diff | 2 `cli_mutually_exclusive` |
| E-E03 | doc + allow-partial | 2 `cli_argument_dependency` |
| E-E04 | metadata-only + attachment files | 2 `cli_mutually_exclusive` |
| E-E05 | jsonl/csv + attachment files | 2 `cli_mutually_exclusive` |
| E-E06 | diff + csv/site/history | 2 `cli_mutually_exclusive` |
| E-E07 | target 已存在/权威目录/symlink | 2（`export_target_exists`/`export_path_unsafe`），无删除 |
| E-E08 | 任一 publication gate 失败 | 1 `publication_gate_failed`，默认无最终 target |
| E-E09 | fsync/rename 故障注入 | 2 `export_io_failed`，旧 target 不变、staging 可审计清理 |

matrix 还必须对每个参数覆盖：最小值、最大值、低一位、高一位、重复、空值、NUL、控制字符、RTL、无效 UTF-8、超长值和 shell/SQL/path 注入。

## 11. 可复制示例

### 11.1 Normal

```bash
policybase list --keyword 药品 --type regulation --year 2024 --limit 20

policybase --output json list \
  --filter 'issuer="国务院" AND validity:effective' \
  --spatial-code 100000

policybase show REG-a1b2c3d4e5 --metadata --body
policybase show REG-a1b2c3d4e5 --history --limit 20
policybase show REG-a1b2c3d4e5 \
  --as-of 2026-01-01T00:00:00Z --metadata
policybase show REG-a1b2c3d4e5 \
  --diff ed-0123456789abcdef01234567..ed-89abcdef0123456701234567 \
  --body

policybase export --doc REG-a1b2c3d4e5 \
  --format markdown --target-dir ./out/reg-a1b2c3d4e5

policybase export --filter 'type:regulation AND validity:effective' \
  --history --format jsonl --target-dir ./out/effective-regulations
```

### 11.2 Edge

```bash
# 查看撤回项的安全元数据；该参数不授予正文访问
policybase show REG-a1b2c3d4e5 --include-withdrawn --metadata

# 同一过滤器的批量导出允许明确的部分成功
policybase export --filter 'spatial_code:420000 AND validity:effective' \
  --format site --target-dir ./out/hubei-site --allow-partial

# 只验证选择、路径和发布门，不创建目录
policybase export --doc REG-a1b2c3d4e5 --edition ed-0123456789abcdef01234567 \
  --metadata-only --format jsonl --target-dir ./out/check-only --dry-run
```

### 11.3 Error 与纠正提示

```bash
# ERROR cli_mutually_exclusive（通用码，PolicyBase_19 §4）：
policybase show REG-a1b2c3d4e5 --edition ed-0123456789abcdef01234567 --history
# 改为：policybase show REG-a1b2c3d4e5 --history
# 或：  policybase show REG-a1b2c3d4e5 --edition ed-0123456789abcdef01234567

# ERROR cli_argument_dependency（通用码）：集合不能指定单一 edition
policybase export --filter 'validity:effective' \
  --edition ed-0123456789abcdef01234567 --target-dir ./out/bad
# 改为 --history、--as-of，或用 --doc 绑定该 edition

# ERROR export_target_exists（业务码，本卷 §9）：不会覆盖或清空目录
policybase export --doc REG-a1b2c3d4e5 --target-dir ./out/existing
# 改为新的空目录，例如 ./out/run-20260804
```

## 12. 验收合同

最低机器验收：

```bash
pytest tests/commands/test_list.py
pytest tests/commands/test_show.py
pytest tests/commands/test_export.py
pytest tests/golden/query_export/
pytest tests/security/test_query_export_boundaries.py
```

必须断言：

- help 中的必填、默认、范围、互斥和示例与同一声明式参数 schema 生成；
- parser 在打开 index/package/target 前拒绝全部非法组合（用法错误归 PolicyBase_19 §4 通用码）；
- current/history/as-of/diff 使用固定 snapshot 和 edition 语义（edition 权威见 PolicyBase_09）；
- text/JSON stdout、stderr 无混流；
- PII、candidate、授权失败和 publication 失败没有内容侧信道（业务规则见 PolicyBase_04）；
- export 默认原子全有或全无，partial 仅在显式允许时退出 3；
- target 故障、路径逃逸、symlink 和任何已存在目录不会删除或覆盖用户文件；
- filter 只产生受限 AST 和参数化查询（字段域见 PolicyBase_14）；
- normal、edge、error matrix 逐项映射稳定 diagnostic code。

## 13. 不变量

1. `list` 永远一 doc 一条 current 结果，历史必须由 `show/export` 显式请求。
2. `show` 只读，不能编辑、确认、纠错或补授权。
3. `export` 必须显式选择 doc/filter 和 target，不能无意导出全库。
4. 历史保存不等于历史内容始终有展示或再分发权限。
5. 参数错误在副作用前拦截（用法错误归 PolicyBase_19 §4 通用码），并提供合法替代命令。
6. `--output` 不是 `--format`，metadata-only/partial/history 都不是授权旁路。
7. 无效、安全失败和空结果有不同的稳定诊断与退出语义（退出码映射见 PolicyBase_19 §5）。
