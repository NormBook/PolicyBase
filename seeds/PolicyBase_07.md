# PolicyBase ID 与归一化契约

> 状态：主权威
> 分卷编号：PolicyBase_07
> 主题：identifiers
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 本卷定位

本卷是 PolicyBase 文献身份的机器契约：**ID / canonical key / 归一化 / Tier / 碰撞 / identity registry / `registry_entry_semantic_hash` 算法**的唯一 owner。

本卷覆盖：

1. 普通文献 `doc_id` 与 `canonical_key` 的**生成语义与 canonical 形态**。
2. Layer 0-6 归一化流水线与 Tier 0-5 fallback。
3. 文号、机关、标题、URL 的归一化规则。
4. `normalization_profile`、`issuer_resolution_snapshot`、ID 稳定性与 identity registry。
5. 旧 ID、alias、map drift、Tier 5 升级。
6. hash 碰撞集合算法与 `id_quality`。
7. `registry_entry_semantic_hash` 算法（身份注册表 entry 语义 hash，迁入自索引卷；见 §22）。

本卷不覆盖：

1. 去重判定、重复候选、人工合并、多源合并策略——见 PolicyBase_08 §身份层 reviewed decision。
2. ingest decision、主来源选择、字段补全——见 PolicyBase_08。
3. 文献包目录、附件文件清单、不可变 edition 文件权威与 manifest 最小合同——见 PolicyBase_09。
4. 来源注册表、采集 Profile、Recipe、Adapter——见 PolicyBase_10。
5. CLI 词法投影（token 正则、`--id` 形态校验、AUTH_ID scope 路由）——见 PolicyBase_15 §跨命令标识；本卷只定义生成语义与 canonical 形态，不定义 CLI 解析序或词法规则。
6. 索引 `record_hash` 的全字段 frame——见 PolicyBase_14 §record_hash；该卷引用本卷 §22 的 `registry_entry_semantic_hash`。

CLI 词法投影（token 正则）归 PolicyBase_15 §跨命令标识，本卷只定义生成语义与 canonical 形态。

---

## 2. 权威与历史来源

本卷是 v3 candidate 内 ID、canonical key、归一化与 identity registry 的唯一 owner。不可恢复的旧 `v1/v2/rules` seed 只作为历史 provenance，不是可引用的上位权威。以下规则由本卷直接确立：

- `doc_id = "{TYPE}-{hash[:10]}"` 的生成语义。
- Tier 0-5 的 canonical key 字段序列。
- Tier 与 `id_quality` 的绑定关系。
- `primary_issuer_org_id` 必须是 16 位纯数字。
- registry 缺失或机关无法解析时，不得使用 Tier 0-2。
- 转义顺序固定为先反斜杠、后分隔符。
- ID 一旦写入，不可静默重算。
- map drift 标记、Tier 5 升级和碰撞集合重写规则。
- `registry_entry_semantic_hash` 的 framing 顺序与 SHA-256 算法（见 §22）。

发现历史 provenance 与本卷疑似不一致时必须走 Decision；不得依据不可核验的旧章节改变实现。

---

## 3. 冲突规则

冲突时按以下顺序裁决：

1. 按 PolicyBase_01 §3 跨卷不变量、§4 主权威地图定位当前权威。
2. 本卷与未来机器 schema/golden 冲突时停止实施并用 Decision 同步修正。
3. 不得引入未落地的 v4 `TYPE-JD-SRC-NID` 四段 ID。
4. canonical key 相同、相似或 Tier 升级不在本卷中解释为合并动作；合并与去重见 PolicyBase_08。

---

## 4. 迁移目标

本卷最终拆入 `docs/specs/id-normalization.md`、`data/schemas/id.schema.json`、`data/schemas/normalization-profile.schema.json`、`data/schemas/identity-registry.schema.json`、`data/identity/`、`src/policybase/pipeline/normalizers/`、`src/policybase/pipeline/identity/` 和 `tests/golden/id/`（待落地）。

---

## 5. 基本 ID 形态

普通文献主 ID 的**生成语义**固定为：

```text
doc_id = TYPE + "-" + sha256(canonical_key.encode("utf-8")).hexdigest()[:10]
```

- `TYPE` 由分类分卷决定（见 PolicyBase_05）。
- `TYPE` 不进入普通文献 `canonical_key`。
- 禁止用随机数、自增 ID、导入顺序或来源序号铸造 `doc_id`。
- 禁止把 `source_id`、原始 URL、PDF hash 或附件 hash 拼入 Tier 0-4 的普通文献 `doc_id`。

CLI 解析时该 ID 的词法形态（token 正则）见 PolicyBase_15 §跨命令标识；本卷只定义生成语义。

### 5.1 ID 生成权威表（本卷统一 owner）

本卷是所有公共 ID 生成语义的统一权威索引。各 ID 的算法细节由对应业务卷展开，本卷只登记其前缀形态与生成归属，使 PolicyBase_15「ID 生成语义一律以 PolicyBase_07 为权威」成立。新增公共 ID 必须先在本表登记，再进 PolicyBase_15 词法投影表。

| ID | 前缀/形态 | 生成式 / 算法 owner |
|---|---|---|
| `doc_id` | `TYPE` + `-` + 10 hex | 本卷 §5（`TYPE` 见 PolicyBase_05；sha256(canonical_key)[:10]） |
| `edition_id` | `ed-` + 24 hex | PolicyBase_09 §4.1（payload frame 的 SHA-256 前 24 hex） |
| `candidate_id` | `cand-` + 24 hex | PolicyBase_11 candidate manifest |
| `artifact_id` | `art-{stage}-` + hex | PolicyBase_13 §4 内容工件 schema |
| `switch_event_id` | `sw-` + 24 hex | PolicyBase_09 §4.5（canonical event payload SHA-256 前 24 hex） |
| `auth_id` | `auth-` + 24 hex | PolicyBase_04 授权 registry（scope 路由见 PolicyBase_15 §3.1） |
| `review_id` | `rev-` + 24 hex | PolicyBase_13 §5 内容层 review decision |
| `file_id` | `file-` + 24 hex（内容寻址） | PolicyBase_09 manifest `files[]` |
| `run_id` | `run-` + ASCII slug | PolicyBase_11 run manifest |
| `profile_id` | 小写 kebab-case slug（如 `local-government-v1`） | PolicyBase_10 Profile 注册 |
| `backend_id` | 小写 kebab-case slug（如 `rapidocr`） | PolicyBase_13 §10 backend capability |

`source_id`（来源标识，非文献内容寻址）生成归 PolicyBase_10 Source Registry，不进本表。所有 hex 段为小写、SHA-256 前缀；碰撞集合与长度收紧规则见本卷 §25。各 ID 的 CLI token 词法投影见 PolicyBase_15 §3。

---

## 6. 核心术语

| 术语 | 含义 |
|------|------|
| `canonical_key` | 进入 SHA-256 的规范身份串。 |
| `id_quality` | ID 质量单值枚举，与 Tier 一一对应（见 §16）。 |
| `historical_ids[]` | 新 package 对 registry aliases 的只读摘要；旧 ID、碰撞迁移前 ID、Tier 5 升级前 ID 的机器权威在 §21 identity registry，旧 edition 不为补该数组而改写。 |
| `legacy_reason` | `id_quality=legacy` 时的必填单值原因（见 §23）。 |
| `normalization_profile` | 锁定影响 key 的归一化规则与受控数据版本（见 §20）。 |
| `issuer_resolution_snapshot` | 记录机关解析实际依赖（见 §20）。 |
| `controlled_data_manifest_hash` | 受控数据内容摘要。 |

---

## 7. Layer 0-6 流程

ID 计算必须按固定顺序执行：

```text
原始输入
  -> Layer 0 净化
  -> Layer 1 Unicode 归一化
  -> Layer 1b 形近字映射
  -> Layer 1c 繁简转换 + 异体字
  -> Layer 2 模式检测
  -> Layer 3 数值归一化
  -> Layer 4 机关身份解析
  -> Layer 5 组装 canonical_key
  -> Layer 6 SHA-256 哈希
  -> doc_id
```

任一层无法得到高质量字段时，只能按 Tier 规则降级。归一化失败不得阻止保留原始证据，但必须阻止使用不满足条件的高 Tier。

---

## 8. Layer 0：净化

Layer 0 清除非语义噪声：

- Unicode 控制字符：`U+0000-U+001F`、`U+007F-U+009F`。
- 零宽字符：`U+200B`、`U+200C`、`U+200D`、`U+FEFF`。
- HTML 实体残留，例如 `&nbsp;`、`&#160;`。
- 不可见标记字符。
- 连续空白折叠为单个空格。
- 字段首尾空白。

Layer 0 不做语义修正，不补全缺失字段。

---

## 9. Layer 1 / 1b / 1c

Layer 1 先 NFC，再 NFKC。NFKC 用于全角转半角和兼容形式规范化。中文括号、书名号和引号需要显式标点映射：

```text
〔〕 -> []
【】 -> []
《》 -> <>
「」 -> ""
『』 -> ""
```

Layer 1b 的 `CONFUSABLE_MAP` **不是全局改写器**。它只允许用于文号模式识别和机关别名候选召回；标题、正文、自由标签、原始机关名和证据文本不得执行形近字替换。候选召回命中后必须保留原值，并由受控文号/机关记录或人工证据确认；形近字映射本身不得铸造 Tier 0-2 身份，也不得授权自动合并。常见组包括：

```text
已 / 巳 / 己 / 㔾
末 / 未 / 𣎴
戊 / 戍 / 戎 / 戒
日 / 曰
土 / 士
```

Layer 1c 使用 OpenCC 繁简转换和 `VARIANT_CHARS`。常见异体组包括：

```text
群 / 羣
峰 / 峯
秋 / 秌
柏 / 檗
```

映射表必须声明适用字段、方向、证据级别和唯一规范目标字。未声明字段一律禁止应用。任一映射表变化都可能触发 map drift（见 §23）。

---

## 10. Layer 2A：文号模式

文号模式固定为 A/B/C/D：

- **A**：机关代字 + 年份 + 序号，如 `国发〔2019〕24号`。
- **B**：第 N 号或令公布，如 `国务院令第722号`。
- **C**：无规范括号的机关代字 + 年份 + 序号，如 `国发2019 24号`。
- **D**：纯序号，如 `第43号`。

多模式命中时，按 A -> B -> C -> D 取第一个完整匹配。必须保存全部命中供审计。canonical 输出只使用获选模式。`document_number_canonical` 输出格式固定如下：

| 模式 | canonical 格式 | 说明 |
|------|----------------|------|
| A | `{agency_code}-{year}-{seq}` | 机关代字、四位年份、序号；如 `国发〔2019〕24号` -> `GUOFA-2019-24` |
| B | `{order_code}-{seq}` | 令号或第 N 号；`国务院令` 使用 `LING`，如 `国务院令第722号` -> `LING-722` |
| C | `{agency_code}-{year}-{seq}` | 先按 A 的输出格式补正括号和空白 |
| D | `SEQ-{seq}` | 只有纯序号，不能单独用于 Tier 0，需结合更高置信机关与日期 |

`agency_code` 与 `order_code` 必须来自受控映射表；映射表缺失时不得猜测编码，降至 Tier 3 或更低。年份是否保留由模式决定，不得由实现临时选择。无完整匹配时保留 raw 值，降至 Tier 3 或更低。禁止猜测补全文号。

---

## 11. Layer 2B：机关模式

机关模式固定为 P1-P5：

- **P1** 全称精确匹配。
- **P2** 简称匹配。
- **P3** 代字匹配。
- **P4** 模糊匹配。
- **P5** 多级匹配。

机关解析按 P1 -> P2 -> P3 -> P4 -> P5 尝试。P1-P3 必须命中注册表中唯一 `org_id`。P4/P5 必须给出可核验的注册表别名或受控规则。同优先级命中多个不同 `org_id` 时，登记未解析机关。禁止按置信度或字符串距离随意择一。

---

## 12. Layer 3：数值归一化

中文数字转阿拉伯数字：

```text
二十四 -> 24
一百二十二 -> 122
```

序号去前导零：

```text
00722 -> 722
```

两位年份按以下顺序判断：

1. 民国纪年标识或机关 `era: republic`。
2. 与已知 `issue_date` 相差不超过 1 年的世纪候选。
3. 已解析机关的 `era` 与有效期。
4. 仍不唯一或冲突时保留原始两位年份。

世纪不确定时：

```yaml
id_quality: partial
century_ambiguous: true
```

---

## 13. Layer 4：机关身份解析

`org_id` 是纯数字、固定 16 位字符串：

```text
DD AAAAAA FFFF EEEE
```

- `DD` 为体系域。
- `AAAAAA` 为行政区划六码。
- `FFFF` 为全国受控职能码。
- `EEEE` 为同地域、同职能实体序号。

体系域包括：`10` 国家行政机关、`20` 党机关、`30` 人大、`40` 政协、`50` 监察、`60` 法院 / 检察院、`70` 军事 / 武警、`80` 境外政府 / 国际组织、`90` 历史机构或其他组织、`99` 未识别待核验机构。

- `org_id` 不替代原始名称。
- 文号代字独立于 `org_id`。
- 更名但实体连续时保留 `org_id`。
- 合并、拆分、撤销或新设实体必须新建 `org_id`，并由关系表记录沿革。
- 历史文献解析发文日当时存在的机关。

---

## 14. 99 域未解析机关

无法确认机关时，保留原始机关名和文号。99 域不得共用一个固定未知 ID。99 域临时 ID 必须由 `raw_name + "|" + source_id` 确定性派生。派生结果必须仍满足 16 位纯数字 `org_id` 格式。

固定投影算法为：

1. `raw_name` 使用 Layer 0 净化后的 UTF-8 文本，`source_id` 使用来源注册表（见 PolicyBase_10）中的原值。
2. 输入串固定为 `raw_name + "|" + source_id`，不得附加隐式盐或运行时随机值。
3. 计算 `digest = sha256(input.encode("utf-8")).digest()`。
4. 将 digest 按无符号大端整数解释，计算 `tail = integer % 10^14`。
5. `org_id = "99" + zero_pad_decimal(tail, 14)`。
6. normalization profile 必须记录本算法版本 `issuer-unresolved-99-v1`。
7. registry 必须检查同一 `org_id` 是否已绑定不同输入串；发生碰撞时返回 `issuer_99_hash_collision` 并转人工显式映射，不得自动加序号或静默覆盖。

99 域状态由 issuer 字段表达：

```yaml
issuer_unresolved: true
```

`id_quality` 仍按实际 Tier 取单值。后续人工解析成功后，按 §21 生成新 ID/package 和 registry migration；旧 ID 成为 alias，新 package 可摘要到 `historical_ids[]`。

---

## 15. Layer 5：canonical key 与转义

所有 canonical key 必须以 Tier 名开头。字段数量、字段顺序和未知占位符固定。未知字段使用 `?`。日期使用 ISO `YYYY-MM-DD`。字段分隔符为 `|`。

字段值转义顺序固定：

1. 先转义反斜杠：`\` -> `\\`。
2. 再转义分隔符：`|` -> `\|`。

参考实现：

```python
def escape_field(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")

def build_canonical_key(*fields: str) -> str:
    return "|".join(escape_field(field) for field in fields)
```

转义必须可逆。

---

## 16. Tier 0-5

| Tier | canonical_key | id_quality |
|------|---------------|------------|
| 0 | `T0\|primary_issuer_org_id\|document_number_canonical\|date` | `standard` |
| 1 | `T1\|primary_issuer_org_id\|document_number_without_sequence\|titlehash8\|date` | `partial_no_seq` |
| 2 | `T2\|primary_issuer_org_id\|titlehash8\|date` | `partial_organ_only` |
| 3 | `T3\|raw_primary_issuer_name\|raw_document_number\|date` | `raw` |
| 4 | `T4\|raw_primary_issuer_name\|normalized_title\|date` | `auto` |
| 5 | `T5\|canonical_url` | `url` |
| -- | 旧 ID 队列 | `legacy` |
| -- | 世纪不确定 | `partial` |

- Tier 0-2 必须有合法 `primary_issuer_org_id`。
- canonical_key 中的 `date` 取 frontmatter `issue_date`（成文日期，frontmatter 字段规范见 PolicyBase_06）；`issue_date` 缺失时该文献不得进入 Tier 0-4，须降级 Tier 5 或人工补全后再生成正式 ID。
- registry 缺失、机关无法解析或命中 99 域时，不得使用 Tier 0-2。
- Tier 3 raw 字段只做 Layer 0/1 净化。
- Tier 4 使用标题归一化结果。
- Tier 5 使用 canonical URL。

`id_quality=auto` 是历史受控字面量，只表示 Tier 4 的 ID 由 fallback 字段自动铸造，**不表示允许自动去重或自动合并**。PolicyBase_08 明确要求 Tier 4 只生成强候选并经 reviewed decision。Tier 5 也只提供临时来源身份，不授权把 URL 内容变化覆盖为同一 edition。

---

## 17. Tier 选择

Tier 从高到低选择：

- **Tier 0**：机关 ID、完整规范文号、日期均可用。
- **Tier 1**：机关 ID、无序号文号、标题 hash、日期可用。
- **Tier 2**：机关 ID、标题 hash、日期可用。
- **Tier 3**：raw 机关名、raw 文号、日期可保留。
- **Tier 4**：raw 机关名、规范标题、日期可保留。
- **Tier 5**：身份字段不足，但 canonical URL 可用。

不得为了提升 Tier 猜机关、文号、日期或标题。

---

## 18. 标题归一化

标题来源包括页面元数据表、H1、title 标签、OG 标签和明确标题字段。多源不一致时，标记 `title_confidence`。人工确认前不得静默替换既有标题。

用于 hash 的 `normalized_title` 必须：

1. 清除 HTML 和控制字符。
2. 折叠连续空白。
3. 删除来源站点后缀和机械性前后缀标记。
4. `trim`。
5. 执行 Layer 1 和经审定的繁简/异体规则；**禁止执行 Layer 1b 形近字映射**。
6. 规范标点。
7. 再次折叠空白并 `trim`。

`titlehash8` 固定为：

```python
titlehash8 = sha256(normalized_title.encode("utf-8")).hexdigest()[:8]
```

不额外小写，不删除语义标点。

---

## 19. URL 归一化

Tier 5 `canonical_url` 按 RFC 3986 处理。必须执行：

- scheme 和 host 转小写。
- 移除默认端口。
- 删除 fragment。
- 路径移除 dot-segment。
- 百分号编码规范为大写。
- 不解码保留字符。
- query 保留原有键值顺序和重复项。
- query 只规范百分号编码。

URL 归一化算法及版本必须写入 `normalization_profile`。不得默认排序 query。不得默认删除来源参数。

---

## 20. profile 与 snapshot

`normalization_profile` 必须锁定：

- `CONFUSABLE_MAP`。
- `VARIANT_CHARS`。
- OpenCC 包、配置、词典规则。
- URL canonicalization 算法版本。
- 组织注册表、区划、职能码、关系、别名数据版本与 hash。
- 标题清理规则版本。
- 文号解析规则版本。
- 99 域算法版本（`issuer-unresolved-99-v1`）。

每份文献必须持久化 `issuer_resolution_snapshot`。snapshot 至少记录：

- 原始机关名。
- 解析所得 `org_id`。
- 命中的别名或规则。
- 实际依赖的受控记录。
- profile id。
- `controlled_data_manifest_hash`。

snapshot 用于判断 map drift 是否影响该文献（见 §23）。

---

## 21. ID 稳定性与 identity registry

ID 一旦写入，禁止静默重算。

`doc_id` 标识一篇文献，不标识网页抓取批次、附件、OCR 结果或内容 edition。相同 `doc_id` 的内容、元数据、OCR、排版或人工纠错变化必须按 PolicyBase_06 / PolicyBase_09 产生不可变 `edition_id`；只有 canonical identity 变化或碰撞迁移才触发本节的 ID 迁移。edition 回滚不得改变 `doc_id`（edition 合同见 PolicyBase_09）。

以下变化不得原地覆盖 `doc_id`：

- 机关注册表新增别名。
- 机关关系表修正。
- OpenCC、形近字或异体字映射变化。
- 标题清理规则变化。
- URL 规范化规则变化。
- Tier 5 文献获得更高 Tier 身份。
- hash 碰撞集合需要重写。

需要改变 ID 时，必须生成 identity migration batch；禁止重命名旧包或改写旧 edition。

### 21.1 registry 文件布局

包外 identity registry 是 canonical doc_id、别名、package locator 和消费可用性的唯一权威：

```text
data/identity/current.json
data/identity/generations/{registry_generation_id}.json
data/identity/events/{identity_event_id}.json
```

generation 与 event 均不可变，`current.json` 只原子指向一个完整 generation。entry 至少包含：

- `canonical_doc_id`
- `canonical_key_hash`
- `package_locator`
- `edition_id`
- `current_pointer_hash`
- `aliases`
- `availability` = `active|withdrawn|quarantined`
- `reason` / `evidence`

alias 必须无环且只能解析到一个 canonical ID。package locator 是存储定位，不授予内容消费权。默认消费者读取 entry 绑定的 immutable edition；package `current.json`（见 PolicyBase_09）是写入协调事实，二者 hash 不一致时必须拒绝或按旧 generation 显式读取其绑定旧 edition，不能猜测最新指针。

### 21.2 迁移事务

迁移必须在全局 identity lock 下：

1. 验证 expected registry generation。
2. stage 新 `doc_id` 的完整 confirmed package。
3. 生成包含 old/new ID、old/new canonical key/profile、旧/新 package locator、受影响关系/索引、原因和复核证据的 migration batch。
4. 验证全部成员。
5. 用 CAS 原子切换 registry generation。

切换前消费者只见旧集合，切换后只见完整新集合。失败或崩溃不切 generation；已 stage 的新包保持不可发现并可隔离。旧包和旧 edition 字节永久保留，旧 ID 作为 alias 显式解析到新 ID；默认 list/search/export 只消费 registry 中 `availability=active` 的 canonical entry。

### 21.3 撤回与隔离

撤回与隔离是 registry availability，不是法规 `validity`（见 PolicyBase_06）。`withdrawn/quarantined` 默认不得 show body、索引或导出，显式审计历史仍可按权限访问；恢复必须发布新的 registry generation 和 event，不改历史 edition。

---

## 22. registry_entry_semantic_hash 算法

> 本算法 owner 为本卷（PolicyBase_07）。PolicyBase_14 indexing `record_hash` frame 中 `registry_entry` 一项引用本算法，不重定义。

`registry_entry_semantic_hash` 是 identity registry 单个 entry 的语义 hash，作为该 entry 身份与可消费性的稳定指纹。它覆盖 entry 的 canonical 身份、存储定位、当前指针与可用性状态，不包含纯审计字段（时间、actor、log）。

### 22.1 framing 顺序

固定按以下字段名与顺序构造 frame 序列，再连接后取 SHA-256：

```text
frame("canonical_doc_id",  canonical_doc_id)
frame("package_locator",   package_locator)
frame("edition_id",        edition_id)
frame("current_pointer_hash", current_pointer_hash)
frame("availability",      availability)
```

字段名固定英文，不得增删、改序或重命名。字段缺失时 payload 用空串（不得省略 frame）。

### 22.2 frame 规则

`frame(name, payload)` 的固定形态为：

```text
utf8_byte_length(name):name utf8_byte_length(payload):payload
```

即 `<name_len>:<name><payload_len>:<payload>`，长度为 UTF-8 字节数，无分隔空白。该 frame 规则与 PolicyBase_09 / PolicyBase_14 的 frame 形态一致；本卷只规定字段顺序与字段名。

### 22.3 计算与稳定性

```python
def registry_entry_semantic_hash(entry) -> str:
    frames = b"".join(
        frame(name, entry.get(name, ""))
        for name in (
            "canonical_doc_id",
            "package_locator",
            "edition_id",
            "current_pointer_hash",
            "availability",
        )
    )
    return sha256(frames).hexdigest()
```

约束：

- 不得依赖文件遍历、manifest 顺序或 locale。
- `availability` 取值集合见 §21.1。
- 纯审计时间/actor/log 不进入 hash；会改变 canonical 身份、存储定位、current 指针或可消费性的字段必须进入。
- entry hash 在同一 registry generation 内对同一 `canonical_doc_id` 稳定；跨 generation 只在 entry 语义未变时复现同一 hash。
- alias 列表不进入本 hash（alias 唯一性/无环校验由 §21 与 PolicyBase_14 `projected_current_set_hash` 校验，不进默认 entry hash）。

### 22.4 引用方

- PolicyBase_14 `record_hash` 的 `frame("registry_entry", registry_entry_semantic_hash)` 一项引用本算法；该卷不重定义 framing。
- PolicyBase_14 `projected_current_set_hash` 在本算法之上对 canonical entries 按 `canonical_doc_id` Unicode code point 排序后逐项 `frame("entry", registry_entry_semantic_hash)` 并 SHA-256。

---

## 23. legacy 与 map drift

`id_quality=legacy` 表示当前 ID 是历史 ID。`legacy_reason` 必填。本卷定义：

| legacy_reason | 触发条件 |
|----------------|----------|
| `map_drift` | 归一化映射、OpenCC、机关/区划/职能码、关系或别名受控数据变化，且 snapshot 证明该文献受影响 |
| `url_tier_upgrade` | Tier 5 文献经人工核验升级到 Tier 0-4，新 ID 已生成，旧 ID 作为别名保留 |

map drift 流程：

1. 比较旧 snapshot 与新受控数据 manifest。
2. 只标记实际依赖变化的文献。
3. 在 identity migration event 中记录 `reason=map_drift`；不得修改旧 edition。
4. 进入人工复核队列。
5. 复核后按当前算法生成新 ID。
6. 保留旧 ID 与迁移审计。

map drift 不允许全库无差别重算。map drift 不允许自动改写既有 `org_id`、canonical key 或 `doc_id`。

---

## 24. Tier 5 URL 升级

Tier 5 是临时身份层。Tier 5 文献获得 Tier 0-4 身份字段后，必须生成新 ID。旧 Tier 5 ID 和旧包不得原地改写。新 ID 通过 §21 identity registry 发布，旧 ID 作为 registry alias 保留；新 package 的 frontmatter 可以摘要：

```yaml
id_quality: <new Tier 对应值>
historical_ids:
  - DIS-a1b2c3d4e5
```

Tier 5 升级不是 hash 碰撞。Tier 5 升级不定义去重或合并策略（去重见 PolicyBase_08）。

---

## 25. 碰撞算法

正常 ID 使用短 hash：

```text
TYPE-{sha256(canonical_key)[:10]}
```

同一 TYPE 下，同一短 hash 对应多个不同 canonical key 时，形成碰撞集合。碰撞集合的 canonical ID 必须使用：

```text
TYPE-{short_hash}-{full_hash[10:18]}
```

- 不保留裸短 hash 槽。
- 最早写入者的 canonical ID 也必须迁移为带后缀 ID，但其旧包和 edition 不得重写。
- 若后缀也被不同完整 hash 占用，拒绝写入并要求人工升级 hash 长度。
- 不得使用递增序号。

碰撞集合必须按 §21 在全局 identity lock 和单一 registry generation 中原子发布；每个新 ID 先 stage 新 package，裸短 ID 作为 alias/tombstone 保留且不得继续作为 canonical ID。事务必须保证增量运行和全量重建得到相同 canonical ID 集合。已写入 ID 不因默认 hash 长度变化自动重算。

---

## 26. 验收契约

ID golden 至少覆盖：Layer 0、Unicode、字段限定的形近字候选、标题禁止形近字替换、繁简异体、A/B/C/D、P1-P5、中文数字、两位年份、Tier 0-5、转义、标题、URL、99 域、map drift、Tier 5 升级、正式 doc 合并、碰撞集合、后缀碰撞、alias 环、并发 generation CAS、各 crash point、`registry_entry_semantic_hash` framing 顺序稳定性。

`policybase verify id` 或等价命令必须检查：

- canonical `doc_id` 与 canonical key 一致。
- `id_quality` 与 Tier 一致。
- `legacy_reason` 只在尚未迁移的 legacy candidate/record 中出现（其他对象不得存在该键）。
- Tier 0-2 不使用 99 域。
- 转义可逆。
- 同一 canonical key 分配同一 ID。
- 碰撞集合不保留 canonical 裸短 hash。
- registry alias 唯一无环。
- locator 存在。
- availability 有效且 current generation hash 匹配。
- `registry_entry_semantic_hash` 与 entry 实际字段按 §22 framing 顺序一致。

---

## 27. 红线

- 不得引入 v4 四段 ID 作为本阶段主键。
- 不得把 `source_id` 当作普通文献身份字段。
- 不得把 PDF hash 当作文献主 ID。
- 不得为提高 Tier 命中率猜测机关、文号、日期或标题。
- 不得在受控数据变化后静默重算 ID。
- 不得让 Tier 5 升级原地覆盖旧 ID。
- 不得用递增序号解决 hash 碰撞。
- 不得在本卷规定去重、ingest 合并或主来源选择策略（见 PolicyBase_08）。
- 不得改写 §22 `registry_entry_semantic_hash` 的 framing 字段名或顺序而不发布 identity migration event；该算法被 PolicyBase_14 引用，改写须同步引用方。
