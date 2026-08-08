# PolicyBase 公开性、访问与处理合规边界

> 状态：主权威
> 分卷编号：PolicyBase_04
> 主题：compliance
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与权威边界

本卷是 action 级授权、主动公开入口门、访问控制、敏感性/PII 预检、外部模型 gate 与稳定诊断码的**唯一业务 owner**。它回答同一份材料能否被发现、请求、临时保存、正式入库、索引、外传处理和再分发：各动作必须分别获得允许，前一动作成功不授予后一动作。

本卷是 Source Registry、采集、人工导入、附件/OCR、模型、存储、索引与导出的共同硬门。来源定义见 PolicyBase_10，运行时采集见 PolicyBase_11，Rule/Trait 技术行为见 PolicyBase_12（草案），元数据见 PolicyBase_06，内容生产与 OCR 见 PolicyBase_13，存储与 edition 见 PolicyBase_09，CLI 入口与命令矩阵见 PolicyBase_15。

本卷 owner 主题（唯一权威，他卷一句引用）：

- action enum（9 动作）+ DAG（本卷 §3）；
- disclosure.mode 完整枚举（本卷 §4）；
- classification_level 枚举 + 与密级 sensitivity 维度的区分（本卷 §4）；
- 单调收紧原则（本卷 §2）；
- 访问控制不绕过（本卷 §5）；
- 本地预检三序（本卷 §6）；
- candidate/ingest/index 合规三门（本卷 §7）；
- 外部模型 gate 业务规则（本卷 §8）；
- fail-soft/fail-closed（本卷 §9）；
- 合规维度稳定诊断码（本卷 §10）；
- 不可降级边界（本卷 §12）。

冲突时采用更严格结果。任何 Profile、Recipe、Rule、Trait、Adapter、CLI 参数或人工说明都不得放宽本卷。

## 2. 单调收紧原则

每个动作的有效结论是所有适用约束的逻辑与：

```text
effective(action) =
  registry_scope
  ∧ robots
  ∧ site_terms
  ∧ access_state
  ∧ document_disclosure
  ∧ sensitivity_gate
  ∧ pii_policy
  ∧ action_authorization
  ∧ runtime_rule_restrictions
```

任一必要结论为 `deny`、`unknown`、缺失或已过期时，该动作必须拒绝。下游层只能增加限制，不能将拒绝改成允许。这是 PolicyBase_01 §3 跨卷不变量之一。

必须区分：

- 可公开访问不等于可自动采集；
- 可采集不等于可保存；
- 可保存不等于可全文索引；
- 可索引不等于可外传给模型；
- 可外传处理不等于可再分发；
- 来源级声明不等于文献级公开证据；
- 浏览器能够加载不等于获准绕过访问控制。

## 3. action enum 与 DAG（唯一 owner）

机器合同只使用下列规范动作枚举及依赖 DAG；它不是一条把所有动作串联的流水线：

```text
discover -> fetch
fetch -> transient_store
transient_store -> candidate
candidate -> ingest
candidate -> external_transfer -> new candidate
ingest -> index
ingest -> export -> redistribute
```

九个动作逐值定义：

- `discover`：判定来源范围内一个目标是否可被发现、可发起请求；
- `fetch`：发起并接收一次网络请求的字节；
- `transient_store`：仅保存完成当前 run 的下载、解码和本地预检所需临时字节；不授予 candidate 或长期保留；
- `candidate`：写入受控 candidate 队列；
- `ingest`：创建正式、可审计且不可变的文献包/edition；
- `index`：创建本地检索投影；
- `external_transfer`：把最小必要内容传给获授权的外部处理方；
- `export`：生成离开内部文献包边界的导出物；
- `redistribute`：向第三方发布或再分发导出物。

`external_transfer` 是把 eligible local object 交给外部处理方的独立支路，不依赖已有 ingest：输入可以是已过 candidate 三门的工件，或从 confirmed edition 派生且重新通过三门的 reprocess candidate；两者都必须另有对象级外传授权。外部结果只能成为 new candidate，再走 review/confirm/ingest，不能直接写 edition。它不是本地 `export` 的前置。`index` 也不是直接从 confirmed package 生成本地 export 的前置。

拒绝只沿真实依赖边传播：`external_transfer=deny` 不影响合法本地 `export`，`index=deny` 不自动禁止直接导出，`redistribute=deny` 不抹去合法本地 export 工件。

`store`、`retain`、`publish` 只能出现在解释性文字中，不能成为 schema 值；迁移时必须分别映射到上述精确动作，映射不唯一即 `unknown` 并拒绝。PolicyBase_10 Registry 的 `terms.actions` 和所有 action authorization 必须引用本枚举，不得自建别名。某动作缺失、结论未知或证据过期时只拒绝该动作及 DAG 定义的后继，不把上游成功升级为下游许可。

### 3.1 合规判定对象

判定必须至少携带：`source_id`、规范化 URL、动作、来源配置版本、robots 快照、条款审查引用、访问状态、文献级公开证据、输入对象 hash、判定时间、组件版本与诊断码。

证据必须区分四类：

- `source_evidence`：来源身份、入口功能、运营方、公开性审查与站点条款；
- `document_evidence`：该文献主动公开的页面、栏目、标题、正文或附件关联证据；
- `action_authorization`：外传、再分发等特定动作授权；
- `runtime_observation`：robots、HTTP、challenge、登录墙、付费墙和结构漂移观测。

不得以栏目名称、搜索结果摘要、运营方、文号或来源优先级单独证明主动公开。

## 4. 公开性门：disclosure.mode 与 classification_level

### 4.1 disclosure.mode 完整枚举（唯一 owner）

`disclosure.mode` 描述一份文献在公开性维度上的状态。完整取值域如下；PolicyBase_05（taxonomy 体系引用）与 PolicyBase_06（metadata 字段引用）均引用本表，不得新增第五值。

| 取值 | 定义 | 入库门控语义 |
|---|---|---|
| `proactive` | 该文献已被运营方主动公开：存在可验证的、面向不特定公众的发布页面/栏目/正文/附件关联证据 | 唯一允许进入正式正文库与 FTS 索引的取值；附件、OCR 结果、人工导入同此要求 |
| `upon_request` | 该文献属依申请公开范围：运营方按申请向特定申请人提供 | **不得进入正文库**；仅允许采集其公开的指南、流程、受理机关、空白表单等说明信息；个案答复、申请人提交内容、申请附件与身份信息一律不采集正文 |
| `not_disclosable` | 该文献依法/依规不可公开（涉密、内部传达、第三方秘密等） | 一律不得入库、不得索引、不得外传、不得导出；命中即转入 §6.1 敏感性硬拦截链路或直接拒绝 |
| `unknown` | 证据不足、未审查、配置缺失或审查结论已过期 | 一律拒绝该文献的 `candidate` 及 DAG 后继；不得默认升级为 `proactive` |

来源注册时的 `disclosure_scope=proactive` 只是可发现范围，不替代文献级证据；文献级 `document_evidence` 必须独立成立。党内法规、党政联合文件、军事法规公开版不享有豁免，仍需文献级 `proactive` 证据。`PRC` 的分类含义由 PolicyBase_05 定义，不得解释为「党内法规许可」或「公开性已确认」。

### 4.2 classification_level 枚举（公开性层级）

`classification_level` 描述一份文献**作为候选入库对象的公开性层级**，由本卷 owner。它与 §6.1 的密级 sensitivity 维度是**两个正交维度**，不得混用、不得用一个推导另一个。

| 取值 | 定义 | 与本卷门的关系 |
|---|---|---|
| `public` | 已主动公开、面向不特定公众 | 满足 §4.1 `proactive` 文献级证据时可进入此层级 |
| `restricted_public_candidate` | 来源主张公开或限公开，但文献级证据尚未独立成立 | 必须补足文献级证据后方可升级；未补足前按 §4.1 `unknown` 处理 |
| `audit_internal` | 仅用于内部审计/复核保留，不进入正文库或公开投影 | 不授予 `index`/`export`/`external_transfer`/`redistribute` |

`classification_level` 由 PolicyBase_06 的 metadata 字段引用；元数据字段定义与写入流程见 PolicyBase_06。

### 4.3 classification_level 与密级 sensitivity 的区分（裁定 M2）

| 维度 | owner | 回答的问题 | 取值来源 |
|---|---|---|---|
| `classification_level`（本卷 §4.2） | PolicyBase_04 | 这份文献作为候选对象处于哪一**公开性层级**？ | 文献级公开证据 + 来源声明 |
| 密级 sensitivity（本卷 §6.1） | PolicyBase_04 §6.1 | 这份文献的**文本内容**是否命中涉密/工作秘密/内部资料？ | 本地文本扫描检测枚举 |

判定顺序固定（见 §6）：先密级 sensitivity 硬拦截，再 PII；二者都不命中后，`classification_level` 才在 candidate/ingest 阶段作为公开性层级写入。`classification_level=public` 不豁免密级扫描；密级命中一定压低公开性层级，反向不成立。

## 5. 访问控制与站点约束

除下述 robots bootstrap 外，首次自动正文/列表/API 请求前必须解析并缓存 robots；无法解析适用 robots 或站点条款审查结论时按动作 fail-closed。必须遵守 `Disallow`、`Crawl-delay`、站点明确限制以及来源级速率下限。

robots bootstrap 只有两种合法输入：未过期且 hash 可验证的离线快照，或对 PolicyBase_10 Registry 显式登记 `robots_url` 的一次受控 `GET/HEAD`。在线 bootstrap 必须在站点条款已预审、精确 host/path/method 已登记后执行，使用诚实 User-Agent、独立请求预算和 PolicyBase_11 的逐跳 redirect gate；不得借 bootstrap 请求正文、探测 alternate path 或跨来源继承许可。响应、超时、解析失败、越界 redirect 或快照过期都产生稳定证据并保持后续 `fetch=deny`；缓存必须记录获取时间、TTL、URL、redirect 链、status、内容 hash 和解析器版本。

以下情况不得自动绕过：

- 登录、身份认证或付费墙；
- 图形、滑块、短信或其他验证码；
- WAF、JS challenge、设备/浏览器完整性检查；
- 下载权限、临时凭据或受控 API；
- TLS/浏览器指纹识别、反自动化检测；
- 参数猜测、隐藏接口探测、凭据复用或会话窃取。

禁止隐藏 webdriver、伪造 TLS 指纹、模拟真人轨迹、破解验证码、构造反检测请求头或利用非公开接口。标准浏览器只允许在普通公开页面上执行可审计的只读渲染、DOM 观察和截图；一旦出现 challenge 或访问控制，必须停止自动化并转 `blocked/handoff`。

403、429、challenge、登录墙、付费墙或条款变化必须产生稳定事件。采集组件可阻断本次 run 并提出暂停建议，但不得自动改写 Source Registry 的持久 `paused` 状态。

### 5.1 四库差异标注

合规门在四库下规则一致（不降级），但观测形态有差异：

- `zcwjk`（政策文件库）：常见栏目分页与附件下载，登录墙罕见；重点核验栏目级主动公开证据；
- `gz`（规章库）：国务院公报与部门规章门户多静态 SSR，robots 一般宽松；重点核验「现行/废止」状态与正文一致性；
- `flk`（法律法规库）：国家法律法规数据库多有公开 API 与分页，需遵守分页速率；
- `xxgk`（政务公开）：依申请公开入口、个人信息填报页与 case 答复高发，必须严格区分 `upon_request` 说明信息与个案正文，不得采集个案正文。

## 6. 本地内容预检

写 candidate 前的顺序固定为：

1. 文献级主动公开（§4.1 `proactive`）；
2. 密级、工作秘密和内部资料（§6.1 sensitivity）；
3. PII（§6.2）。

扫描件必须先通过本地文本提取或本地 OCR 产生预检文本。该步骤是 `local_preflight_extract`：只消费获准 `transient_store` 的 run 临时字节，只输出绑定输入 hash 的临时预检文本、工具/版本、退出码和审计摘要；它不是 PolicyBase_13 的内容 candidate、正式 OCR artifact 或 edition。外部模型不得参与这三道门（红线；详见 §8）。

预检通过后，普通 candidate 只引用预检证据和 input/output hash；PolicyBase_13 仍须从原始输入独立产生正式可追溯的 OCR/layout candidate，不能把临时预检文本直接晋升。主动公开失败、敏感性命中、OCR/提取失败或删除器失败时不得写普通 candidate；必须删除临时正文、附件、页图和预检文本并记录不含原文的 deletion event。PII 命中只进入受控复核记录。无法证明临时材料已删除时按硬门失败处理。

### 6.1 敏感性硬拦截（密级 sensitivity 维度）

检测对象包括正文、标题、文件名、附件文本、页眉页脚、水印和 OCR 文本。检测枚举（密级 sensitivity）至少覆盖：

- 绝密；
- 机密；
- 秘密；
- 工作秘密；
- 内部资料（含「内部参阅」「内部传达」及常见空白/期限变体）。

命中后必须：

- 立即停止该对象及其派生处理；
- 删除临时正文和附件；
- 不写 candidate，不进入 PII，不调用外部模型；
- 阻断本次 run 的相关 source/host 桶并生成暂停建议；
- 仅记录必要分类、对象引用和 hash，不保存命中原文。

只有人工复核可解除误报，并记录复核人、时间、理由和影响范围。

### 6.2 PII 发布限制

PII 至少覆盖身份证号、手机号、邮箱、护照号和银行卡号。命中不是涉密结论，但必须阻止正式新入库、FTS、公开 JSONL、外传和公开发布，直到完成受审查的脱敏。

既有正式文献重扫命中时，可保留受控包以维持审计，但必须立即撤下索引与公开投影。脱敏版本必须保留来源 hash、差异和人工复核记录。

## 7. candidate、正式入库与索引合规三门

candidate、ingest、index 是合规维度的三道门，每道门独立判定，不沿用上游自报结论。

- **candidate 门**：采集只写 run 区 candidate。candidate 必须包含三道预检结果（§6）、配置快照引用与稳定诊断码（§10）。主动公开失败或敏感性命中不得写 candidate；PII 命中只能写受控拒绝/复核记录，不得形成新的正式包。
- **ingest 门**：规范 action `ingest` 是正式文献包唯一创建入口。ingest 必须重新验证证据完整性和配置版本，不得相信 Adapter 或 candidate 自报的通过结论。
- **index 门**：`index` 是索引唯一写入 action。文献包存在不自动授予索引、外传、导出或再分发权限。

三道门的具体 CLI 子命令绑定、参数合同与命令序列见 PolicyBase_15 命令矩阵及 PolicyBase_17（cli-source-ingest）、PolicyBase_18（cli-process）、PolicyBase_19（cli-index-verify）的子命令绑定；本卷不重复 CLI 命令名。

## 8. 外部模型 gate 业务规则（唯一业务 owner）

本卷是外部模型 gate 的**唯一业务规则 owner**。PolicyBase_13（content）只写「触发时机」（在内容生产状态机的哪一步可调用模型），PolicyBase_18（cli-process）只写「CLI 参数解析阶段的触发点」（哪个子命令的哪个参数解析阶段会进入此门），二者均引用本卷 §8。这是 PolicyBase_01 §3 跨卷不变量「外部模型不参与公开性/密级/PII 终审」的落地。

### 8.1 调用前提（必须同时满足）

外部模型只能在本地交互会话按明确授权调用；CI 和默认批处理不得调用。模型不得执行公开性、敏感性或 PII 预检，也不得推翻这三道门的结论。

调用前必须同时满足：

- 文献级主动公开已确认（§4.1 `proactive`）；
- 敏感性预检通过（§6.1 未命中）；
- PII 未命中或已人工确认脱敏（§6.2）；
- `manifest.json.external_transfer_authorizations[]` 中存在未过期、未撤销且覆盖当前对象、字段、模型提供方和任务的授权；
- 只发送任务所需最小内容，不含凭据、个人信息或受限附件。

### 8.2 授权权威与密钥

授权唯一权威在 manifest（见 PolicyBase_09）。操作日志只能引用授权 ID，不得内联授权内容。API Key 不得进入仓库、日志、fixture 或模型输入；密钥日志由 PolicyBase_13 规定。

### 8.3 失败与边界

外部模型 gate 的任一前提未满足时按 §9 fail-closed：不调用、不写 edition、不外传、不保留外传字节。模型返回结果不授予下游动作权限，下游仍按 DAG 与三门独立判定。

## 9. fail-soft 与 fail-closed

网络瞬时失败、单页解析失败、未知外链和非关键字段缺失可以 fail-soft，但不得伪造内容、扩大范围或覆盖最后成功版本。

以下必须 fail-closed：

- 来源、host 或 path 未注册；
- robots、条款或动作授权未知/拒绝；
- challenge、验证码、登录墙、付费墙；
- 主动公开证据不足；
- 敏感性命中；
- PII 对正式入库、索引、外传和发布；
- 外传或再分发授权无效；
- 配置/schema 版本未知或规则解析失败。

fail-soft 只能产生错误、checkpoint、quarantine、暂停建议或 handoff；不能把失败对象升级为 candidate。

## 10. 审计与稳定诊断码（合规维度）

每次判定记录输入对象、来源、URL、动作、配置快照、规则链、执行组件、时间、结果和理由。日志不得保存敏感正文、PII 值、密钥或登录材料。

合规维度最低稳定诊断码（通用 `cli_*` 诊断码与统一退出码见 PolicyBase_19）：

| 诊断码 | 含义 |
|---|---|
| `source_scope_denied` | 来源或路径未准入 |
| `robots_disallowed` | robots 拒绝 |
| `terms_denied` | 条款拒绝当前动作 |
| `access_control_blocked` | 登录、付费、challenge 或验证码 |
| `disclosure_not_proactive` | 文献级主动公开门失败（含 `upon_request`/`not_disclosable`/`unknown`） |
| `sensitivity_block` | 密级/工作秘密/内部资料命中 |
| `pii_excluded` | PII 阻止正式处理或发布 |
| `authorization_invalid` | 外传或再分发授权无效 |
| `config_unresolved` | schema 或配置链不能确定 |

## 11. 迁移目标与验收

正式资产应包括：

- `docs/specs/compliance-boundary.md`；
- `src/policybase/pipeline/acquisition/compliance.py`；
- `data/schemas/compliance_decision.schema.json`；
- `tests/golden/compliance/`；
- manifest 中的外传授权 schema（与 PolicyBase_09 对齐）。

机器验收至少覆盖：主动公开正反例、依申请公开正文拒绝、`not_disclosable`/`unknown` 拒绝、敏感性临时文件删除、PII 投影撤下、robots/条款拒绝、challenge 阻断、外部模型授权缺失/过期/scope 不符，以及 Rule/Recipe 不能放宽上游拒绝。

```bash
policybase verify boundary --fixture-root tests/golden/compliance/  # 待落地
pytest tests/golden/compliance/                                    # 待落地
```

退出码：0 全部断言通过；1 合规断言失败；2 fixture、schema 或环境错误。统一退出码定义见 PolicyBase_19。

## 12. 不可降级的边界

- 不采集依申请公开个案正文；
- 不绕过访问控制、验证码、WAF 或付费墙；
- 不伪造 TLS/浏览器指纹；
- 不把来源级声明当作文献级证据；
- 不把本地预检通过当作外传或再分发授权；
- 不让模型参与本地合规门（公开性/密级/PII 终审）；
- 不让技术规则授予权限；
- 不以「先入库后补证据」绕过硬门；
- 不把 `classification_level` 与密级 sensitivity 混用或互相推导；
- 不在 `disclosure.mode` 之外新增第五值。
