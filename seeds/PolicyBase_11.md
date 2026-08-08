# PolicyBase 采集引擎运行时、candidate 与变化闭环

> 状态：主权威
> 分卷编号：PolicyBase_11
> 主题：acquisition
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷定义已注册来源如何从入口、列表、详情、公开 API 和附件入口产生可供 ingest 消费的 candidate。本卷是 **采集运行时（Engine、Adapter 运行接口、中间对象、robots/限流、访问控制事件、quarantine 运行时记录、checkpoint、增量、漂移运行时指标、canary stop、采集退出码）** 的唯一 owner。

采集阶段只交付：run 记录、DocumentStub、DocumentDraft、CandidateRecord、checkpoint、quarantine 运行时记录、handoff、漂移事件和暂停建议。它不得写 `data/documents/`、索引、正式去重结论或发布物。

非职责边界（一句引用）：

- 来源 Registry schema、source_id 身份、host alias、Profile、Recipe、Adapter 注册、外链路由、来源生命周期、**配置组件 release bundle 回滚** 见 PolicyBase_10 §13。
- Rule v1 schema、Trait、pre-fetch/post-fetch **能力边界**、deny、transport、fixture manifest schema、结构基线与三级分级、canary 晋升门、Rule Pack 发布生命周期（Rule-Pack 视角，草案）见 PolicyBase_12（草案，P2 Decision 晋升后生效）。
- 站点形态分类索引（SSR/SPA/API/分页/附件归属判定）见 PolicyBase_10 §10。
- compliance 三门（action enum + DAG、主动公开门、敏感性预检、PII 限制、密级检测、外部模型 gate 业务规则）见 PolicyBase_04。
- candidate → edition 正式入库、合并、文献版本裁决见 PolicyBase_08 / PolicyBase_09。
- 正文 OCR/版面/精修见 PolicyBase_13。

## 2. 配置链与权限边界

```text
Source Registry
  → Profile
  → Recipe
  → pre-fetch Rule/Trait
  → Adapter capability
  → AcquisitionEngine fetch
  → post-fetch Rule/Trait
  → parse
  → compliance gate
  → candidate
  → ingest
```

Engine 是网络请求、限流、队列、快照、合规和错误处理的唯一调度者。Adapter 只能提供受控 discover/parse 行为，不能代替 Engine。

所有有效行为都受 Registry、PolicyBase_04、robots、条款和 Rule 限制。配置无法解析、版本未知或匹配歧义时 fail-closed。

## 3. 版本化运行快照（resolved_config_snapshot）

每个 run 开始前必须解析并冻结 `resolved_config_snapshot`：

```yaml
snapshot_schema_version: "1.0"
source_id: cn-yn-zcwjk
registry_revision: sha256:...
release_bundle_digest: sha256:...
profile: {id: local-government-v1, version: "1.0.0", digest: sha256:...}
recipe: {id: cn-yn-zcwjk, version: "1.2.0", digest: sha256:...}
rule_pack: {id: core-government, version: "1.0.0", digest: sha256:...}
adapter: {id: configured, version: "1.0.0", digest: sha256:...}
schema_versions: {candidate: "1.0", rule: "1.0", checkpoint: "1.0"}
terms_evidence_ref: ...
robots_snapshot_ref: ...
started_at: ...
```

运行中不得热替换 Profile、Recipe、Rule、Adapter 或 schema。配置变更必须开启新 run。candidate、错误、fixture 捕获和 handoff 都必须引用 snapshot digest。

无法加载精确版本或 digest 不一致时返回 `config_unresolved`，不得回退到「最新配置」。

## 4. 两阶段匹配 · Engine 执行序

本节只定义 Engine 在 pipeline 中执行 pre-fetch 与 post-fetch 的**顺序与运行时职责**。pre-fetch/post-fetch 的 Rule 匹配能力、deny、transport、Trait 合并等能力边界见 PolicyBase_12 §7（草案，P2 晋升后生效）。

### 4.1 pre-fetch 执行序

发出请求前只使用可知事实：`source_id`、规范化 URL、精确 host/alias、path、query key、method、request role 和 Registry 范围。

Engine 顺序：

1. URL 规范化；
2. Registry 精确 host/alias 与 longest allowed path（路由表见 PolicyBase_10）；
3. 按 PolicyBase_04 执行 robots bootstrap/快照验证，再检查条款、method 和动作范围；
4. deny Rule；
5. pre-fetch Rule/Trait；
6. Recipe 允许的技术覆盖；
7. 计算超时、速率、预算、transport 和请求参数。

未匹配 host/path、跨域 redirect、规则冲突或非唯一来源进入 quarantine，不请求正文。HTTP 客户端必须关闭自动 redirect；每个响应的 `Location` 都作为新的 PageRequest 候选，在发出下一跳前重新执行完整 pre-fetch gate。

### 4.2 post-fetch 执行序

响应后可以使用：最终 URL/redirect 链、HTTP status、Content-Type、charset、DOM/API signature、页面类型、响应头和正文结构 fingerprint。

Engine 顺序：

1. 验证当前响应 URL，并把 redirect `Location` 交逐跳 pre-fetch gate；
2. 检查 access-control/challenge（见 §10）；
3. 匹配 post-fetch deny；
4. 选择内容类型和页面模板 Rule；
5. 合并 Trait 与 Recipe 技术覆盖；
6. 验证 selector/API mapping 唯一性；
7. 解析或产生 drift/quarantine。

Content-Type 不得用于 pre-fetch 授权。post-fetch Rule 不能扩大 pre-fetch 已允许的 host、path、method、深度或动作。

## 5. Engine 职责与对象流

```text
entrypoint/list/API
  → PageRequest queue
  → DocumentStub
  → detail/attachment request
  → DocumentDraft
  → local compliance gate
  → CandidateRecord
  → prepare handoff（正式 ingest action 尚未发生）
```

Engine 负责：

- 配置快照、pre/post matching 执行序；
- robots 缓存、条款引用、速率、并发、重试和请求预算；
- PageRequest/Stub 队列及同 run 去重；
- redirect、外链、附件路由；
- checkpoint 和原子写入；
- 本地合规门执行和临时文件删除；
- fixture snapshot 捕获、结构指标、漂移事件；
- candidate、quarantine、handoff、暂停建议和稳定退出状态。

Engine 不负责正式 ID、合并、文献版本裁决、OCR 精修、索引或发布。

## 6. Adapter 运行接口

Adapter 必须声明版本和 capability，Engine 只调用声明过的方法：

```python
class SourceAdapter:
    def capabilities(self) -> AdapterCapabilities: ...
    def discover_entrypoints(self, context) -> list[EntryPoint]: ...
    def build_listing_requests(self, context) -> list[PageRequest]: ...
    def parse_listing(self, response, resolved_rule) -> list[DocumentStub]: ...
    def next_pages(self, response, resolved_rule) -> list[PageRequest]: ...
    def build_detail_request(self, stub, context) -> PageRequest: ...
    def parse_detail(self, response, resolved_rule) -> DocumentDraft: ...
    def discover_links(self, draft, resolved_rule) -> list[DiscoveredLink]: ...
```

Adapter 不直接发送网络请求、访问凭据、写 checkpoint/candidate、调用合规门或扩展 URL 范围。动态公开 token 只能在 Engine 管控的同一公开会话内使用，不能成为绕过登录或 challenge 的手段。

这里的动态公开 token 仅指普通公开页面直接下发、无身份/授权含义、同 origin、短寿命且只在内存中保存的请求相关值。需要客户端秘密、签名计算、设备证明、反自动化交互或 challenge 求解的值不是公开 token，必须 `access_control_blocked`。日志、checkpoint 与 fixture 只保存不可逆 hash 或占位符，不保存 token 值。

## 7. 中间对象

### 7.1 DocumentStub

至少包含 `source_id`、规范化 URL、标题/日期 hint、发现入口、request role、`run_id` 和 snapshot digest。Stub 只是队列线索，不含可信正文、最终分类、最终 issuer 或公开结论。

### 7.2 DocumentDraft

至少包含 source、原始/最终/canonical URL、redirect 链、采集时间、元数据草稿、Markdown 草稿或附件引用、外链、provenance、解析 Rule 链、响应 fingerprint 与 field confidence。

所有字段仍待校验。附件只位于 run 临时区。Draft 不得写正式目录。

### 7.3 CandidateRecord

candidate 位于 `data/runtime/work/runs/{run_id}/candidates/`，至少包含：

- `candidate_schema_version`、`candidate_id`、`run_id`、`source_id`；
- 原始/最终/canonical URL；
- resolved snapshot digest 和各组件版本；
- Draft 的业务内容与 provenance；
- compliance gate 每步结果；
- 内容/响应/附件 hash；
- 解析质量、漂移状态和 `needs_review`；
- `run_mode=production|canary`、所用组件 release status 和 `production_eligible`；
- 可迁移 operation 与去重信号。

candidate 不能宣称正式 `doc_id`、merge、relation 或索引结果。ingest 必须独立重验 schema、snapshot 与合规记录。

任何 `run_mode=canary`、任一组件非 `stable` 或 `production_eligible=false` 的 candidate 都不得进入 ingest；该限制不能由 CLI、人工备注或 Recipe 覆盖。ingest 必须验证 resolved release bundle digest 和上述字段，而不是只查看 run 名称。

### 7.4 compliance gate 执行

Engine 必须按 PolicyBase_04 固定顺序执行三门（文献级主动公开门、敏感性预检、PII 本地预检），Adapter 和 Rule 不得自报或覆盖结果。三门定义、action enum 与外部模型 gate 业务规则见 PolicyBase_04。

扫描 PDF、图片正文及无可信文本层附件必须调用 PolicyBase_04 的 `local_preflight_extract`；Engine 负责临时输入/输出生命周期、hash 绑定和 deletion event，PolicyBase_13 的正式 OCR/layout 不得复用临时文本冒充正式 artifact。主动公开失败、敏感性命中、预检失败或临时删除无法证明时不写正文 candidate；PII 命中只允许写隔离的 `restricted_review_record`，不得进入普通 candidate/ingest 队列。外部模型不得参与采集期 gate。

ingest 必须重新验证 gate 记录、输入 hash 和 snapshot digest；记录缺失、版本不兼容或硬门失败时拒绝。

## 8. SSR / SPA / API / 附件 / 分页 · 运行规则

本节只定义每形态的**运行时规则**。站点形态分类索引（一来源属 SSR/SPA/API/混合的归属判定）见 PolicyBase_10 §10；Rule 表达与匹配见 PolicyBase_12（草案，实现后生效）。

### 8.1 SSR

优先使用普通 HTTP 和 HTML parser。HTML→Markdown 只产生 Draft。容器冲突或必填字段缺失不得猜测。

### 8.2 SPA

优先使用页面公开调用的已登记 API；否则允许标准 Playwright browser 对普通公开页面做只读渲染。只能使用项目支持的标准 channel 和最小、可审计设置。

不得隐藏 webdriver、模拟真人反检测、复用登录态、识别验证码或规避 WAF。出现 challenge 立即 `access_control_blocked`（见 §10）。

等待条件必须受控：`dom_ready`、`selector_present`、`response_pattern`、`network_idle`；每项必须有超时和请求预算，不得无限等待。

### 8.3 公开 API

只允许 Registry 登记的 host/path/method。JSONPath 或字段映射由 versioned Rule 定义（schema 见 PolicyBase_12（草案，实现后生效））。POST 读取接口必须有固定请求模板、无身份凭据、分页预算和 fixture；不得探测隐藏参数。

### 8.4 附件

附件链接先按 Registry 路由（PolicyBase_10）。已登记范围内可下载到临时区并执行 PolicyBase_04 预检；未登记 host/path 只生成 handoff/quarantine。附件正文、OCR 和版面处理交给 PolicyBase_13，不在采集期伪造 Markdown。

### 8.5 多分页与多段正文

分页只允许受控枚举：`page_number`、`next_link`、`cursor`、`date_window`、`api_offset`、`none`。必须有停止条件、最大页数/请求数、重复页 fingerprint 和循环检测。

多段正文必须记录每段 URL、顺序和 hash；缺页、循环或顺序冲突产生 `needs_review`，不能静默拼接。

## 9. robots、限流和网络失败

resolved 配置的基础间隔取 Registry `min_interval_seconds_override`、Profile `min_interval_seconds` 和系统默认的最大值，再与 robots `Crawl-delay` 取最大值并加非负有界 jitter。所有数值单位均为秒；默认系统间隔为 2 秒，来源并发默认 1。旧字段 `rate_limit_override` 不得被静默解释。

应使用稳定、诚实、可识别的项目 User-Agent。不得要求 UA 轮换池；UA 或请求头变化只能用于普通协议兼容并进入快照，不能用于规避封禁。

429 遵守 `Retry-After` 并指数退避；403 不反复请求；5xx/超时可按预算重试；TLS 失败只记录并复核，不伪造指纹。重试不得跨越 run 的规则和请求预算。

## 10. 访问控制事件

验证码、challenge、WAF、登录、付费、受控下载和设备完整性检查统一归类为 `access_control_event`。访问控制不绕过的红线见 PolicyBase_04 §5。

Engine 处理必须：

1. 停止当前对象和相关 source/host 桶；
2. 写入事件、证据路径和 `pause_recommended`；
3. 保留最后成功快照；
4. 不自动修改 Registry `paused`；
5. 不继续切换浏览器、UA、TLS 或交互策略试探；
6. 只产生人工 review/handoff，不产生正文 candidate。

## 11. 外链、redirect 与 quarantine 运行时记录

外链和 redirect 使用 PolicyBase_10 的精确 host/alias + longest allowed path 路由。客户端必须使用 `redirect_mode=manual`，每一跳先规范化并检查 scheme、精确 host/alias、longest allowed path、method、robots、条款、动作、来源状态和预算，之后才能请求。跨 source 的 `Location` 即使目标已注册也只创建 HandoffTask，由目标来源新 run 独立处理；不得在当前会话继续跟随。

redirect 最大 hop 数必须由 schema 有界固定并进入 snapshot；重复 URL/Location 形成循环并阻断。相对 `Location` 按当前响应 URL 解析后再规范化；HTTPS 降级、非 HTTP(S) scheme、userinfo、歧义 URL 一律隔离。301/302/303/307/308 的 method 变化必须按明确枚举处理，任何将已登记 GET/HEAD 变为未登记 method 的跳转都拒绝。

`unmatched_url_quarantine` 运行时记录至少包含：run/source、发现 URL、规范化结果、redirect 链、发现位置、候选目标、诊断码和 snapshot digest。人工接受 alias/path 变更后必须形成新 Registry revision（PolicyBase_10）和新 run；旧 run 不热恢复扩权。

## 12. run、checkpoint 与恢复

run 路径：`data/runtime/work/runs/{run_id}/`。保存 config snapshot、请求/响应证据引用、Stub/Draft、候选、错误、quarantine、handoff、fixture capture、metrics 与 checkpoint 引用。

checkpoint 路径：`data/runtime/checkpoints/{source_id}.json`，按 source 隔离、schema versioned、临时文件 + rename 原子写入。至少记录配置 digest、状态、last fetch、ETag、Last-Modified、队列、已完成页、失败项和时间水位。

恢复仅允许 snapshot digest 完全相同。配置已变更时旧 checkpoint 转为 `superseded`，创建新 run；不得用新规则继续旧队列。checkpoint 损坏时从最后可信水位重建，不能删除已有文献。

## 13. 增量采集与来源变化

增量不能只依赖发布时间。至少组合：ETag、Last-Modified、列表 fingerprint、详情 content hash、附件 hash 和周期性回查水位。

变化只产生 candidate/update signal，不直接覆盖文献。404、410、redirect、正文变化和附件替换分别记录；正式的更新、撤稿、版本关系由 ingest/storage 合同裁决（PolicyBase_08 / PolicyBase_09）。

若新内容与已入库来源对象关联，candidate 应包含 `possible_update_of`、旧/新 hash、观测时间和来源证据。

## 14. fixture snapshot 捕获

本节定义 Engine 在运行时对 fixture 的**捕获行为**。fixture manifest schema（字段清单、脱敏记录、expected fields 等）见 PolicyBase_12 §12（草案，P2 晋升后生效）。

每个 stable Rule 至少捕获 list/detail；适用时还需 API、分页、附件、redirect 和 negative fixture。运行时捕获内容至少包括：

- 脱敏后的响应 body 或 DOM/API 快照；
- status、headers 子集、final URL、Content-Type、charset；
- capture tool/version、capture time、source/rule/version；
- body hash 和明确的脱敏记录；
- expected fields、links、pagination 和诊断码。

fixture 不得包含凭据、cookie、token、PII 或受限原文。真实页面不适合保存时，使用最小合成 fixture，并保留人工可复核证据引用。

生产采集不得自动把未知响应写入 Git。fixture 晋升必须经审阅记录。

## 15. 结构漂移 · 运行时指标

本节定义 Engine 在每次解析时**计算的运行时指标**与 `structure_drift` 事件记录。baseline fixture、三级分级阈值与 Rule/Pack 版本化基准见 PolicyBase_12 §13（草案，P2 晋升后生效）。

每次解析至少计算：

- HTTP/Content-Type/redirect 变化；
- DOM/API signature；
- 主容器和必填 selector 命中率；
- 列表条目数、详情成功率、空正文率；
- 字段缺失/多值冲突率；
- 附件发现率和分页重复率；
- 正文长度分布与模板噪声指标。

单对象异常可标 `needs_review`；涉及来源结构的连续异常产生 `structure_drift`。阈值必须由 Rule/Pack 版本化，不得隐藏在代码中。

漂移事件至少包含 baseline fixture/rule、实际 fingerprint、指标、受影响 URL 数量、首次/最后观测和证据位置。

## 16. canary stop · 运行时

本节定义 Engine 在 canary run 中的**运行时停止阈值**与暂停建议。canary 晋升门、Rule Pack 发布生命周期（Rule-Pack 视角，草案）见 PolicyBase_12 §15（草案，P2 晋升后生效）。

只有 release status=`canary` 的 Rule Pack/Profile/Recipe/Adapter 可用于显式 canary run；`experimental` 仅允许离线 fixture，不得发出网络请求。canary 限定 source、入口、URL/页数、并发、candidate 上限和持续时间，所有输出强制 `production_eligible=false`，不写正式入库。

满足任一版本化阈值时 Engine 必须停止 canary 或来源桶并建议暂停：

- 合规或访问控制事件；
- 必填字段/正文失败率超过阈值；
- redirect 越界或未知 host；
- 规则匹配歧义；
- candidate 数量或重复率异常；
- 内容类型或页面签名发生未接受漂移。

### 16.1 回滚 handoff

组件 release bundle 回滚由 PolicyBase_10 §13 管理；Rule-Pack 视角见 PolicyBase_12（草案）。Engine 接收已审查 `rollback_to` 后必须开启新 run，使用上一已验证 stable bundle，并输出：

- 受影响的 run/candidate 清单；
- `discard/review/reprocess` 建议；
- 旧/新规则版本和 hash；
- 重跑范围与原因。

Engine 不直接重写已入库文献。已入库对象需要重新解析、OCR 或精修时，只生成 `ReprocessHandoff`，交给存储/内容处理流程决定新版本和 current 指针（PolicyBase_09 / PolicyBase_13）。

## 17. Markdown 草稿下限

HTML 清洗必须：

- 只从唯一主内容容器提取；
- 移除 script/style/form/nav/footer/广告/分享/统计等模板噪声；
- 按 HTTP charset、meta、受控检测顺序解码 GBK/GB2312/UTF-8；
- 保留标题层级、段落、列表、表格、引用、链接和图片引用；
- 不内联 base64，不残留大量 HTML/脚本；
- 记录清洗规则版本和输入/输出 hash。

主容器缺失/多重冲突、乱码、模板残留、阅读顺序不可靠或大量图片正文时不得猜测，应 `needs_review` 或转 PolicyBase_13。

## 18. 退出状态与采集维度错误码

run 状态：`success`、`partial`、`blocked`、`failed`。

- `success`：预算内任务完成且无阻断；
- `partial`：允许的局部 fail-soft，候选与错误均可审计；
- `blocked`：合规、访问控制、未匹配范围或规则歧义；
- `failed`：配置、schema、checkpoint 或引擎错误。

CLI 统一退出码（0 success / 1 业务·合规·blocked 拒绝 / 2 用法·配置·环境错误 / 3 合同明确允许的 partial）见 PolicyBase_19 §5。所有机器调用同时输出结构化 summary，不能只依赖文本日志。

采集维度最低错误码包括：`config_unresolved`、`source_unmatched`、`redirect_out_of_scope`、`rule_ambiguous`、`content_type_unmatched`、`structure_drift`、`access_control_blocked`、`robots_disallowed`、`candidate_schema_invalid`、`checkpoint_corrupt`。

## 19. 不得降级的边界

- 不热替换运行配置；
- 不从列表/详情/附件直接写正式文献；
- 不请求未注册 host/path/method；
- 不自动接受 redirect/alias；
- 不绕过 challenge、登录、付费或验证码；
- 不把结构漂移当成空结果静默成功；
- 不让回滚覆盖审计记录或直接重写正式文献。
