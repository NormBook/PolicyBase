# PolicyBase 来源注册、配置分层、来源矩阵治理与跨组件发布状态机

> 状态：主权威
> 分卷编号：PolicyBase_10
> 主题：source-registry
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责边界

本卷是**来源身份、来源准入、配置分层注册、外链路由、来源生命周期、跨配置组件发布状态机、来源矩阵治理**的唯一 owner。

分层模型（唯一权威）：

```text
Source Registry → Profile → Recipe → Rule/Trait → Adapter → AcquisitionEngine
   准入身份          族默认     单来源覆盖    URL 解析      代码例外     统一执行
```

各层不得重复维护同一权威：Registry 不存 selector；Rule 不授予许可；Adapter 不写正式数据；Engine 不发明来源配置。

**本卷不定义**（一句引用 owner 卷）：

- Rule/Trait 的 schema、匹配语言、deny、fixture、回滚 reprocess —— 见 PolicyBase_12 §2~§9（草案，P2 晋升后生效）。
- 采集运行时：版本化运行快照、robots 限流执行、redirect quarantine、checkpoint、增量、canary stop 运行时、退出码 —— 见 PolicyBase_11。
- Adapter 运行接口（`SourceAdapter` 接口的具体调用合同、超时预算执行、capability 宣告如何被 Engine 调度）—— 见 PolicyBase_11 §3。
- 来源级合规动作枚举与单调收紧、`disclosure.mode` 文献级枚举、外部模型 gate 业务规则 —— 见 PolicyBase_04。
- CLI 入口（`source`/`scrape`/`import` 子命令绑定、`--decisions`、路径安全）—— 见 PolicyBase_17。

## 2. 不变量与冲突规则

1. 只有已注册、`lifecycle_state=enabled` 且审查有效的来源才能进入普通自动采集。
2. 来源注册只授予已审查 host/path/action 的上限，不保证每份文献合规（文献级合规见 PolicyBase_04）。
3. 运营方、发现来源、获取来源和发文机关必须分别记录，不得互相推导（见 §4）。
4. 独立 host、子域和业务系统不隐式继承主站许可（见 §5）。
5. Profile、Recipe、Rule/Trait、Adapter 只能在 Registry 和 PolicyBase_04 边界内工作，不能放宽任一限制。
6. 任一配置冲突按更严格值处理；无法确定时 fail-closed。
7. Source Registry 是外链路由唯一权威；未命中 URL 不自动注册、不自动抓正文（见 §11）。
8. host 精确匹配与未知 host 隔离是**不变量**：不存在「近似 host 自动归一」的回退路径（见 §5）。
9. 实际来源 URL、可达状态、审查时间属于版本化 registry 数据，不得复制成静态「现状表」作为第二权威。
10. `lifecycle_state` 是来源唯一持久状态；不得再用 `enabled`/`paused` 布尔组合表达（见 §12）。

## 3. Source Registry 最小 schema

正式位置 `data/sources/registry.yaml`，schema 必须版本化。概念结构：

```yaml
schema_version: "1.0"
sources:
  - source_id: cn-yn-zcwjk
    display_name: 云南省政策文件库
    operator_org_id: org-cn-yn-government
    source_type: policy_library
    authority_level: provincial
    jurisdiction: CN-YN
    entrypoints:
      - https://www.yn.gov.cn/...
    canonical_hosts: [yn.gov.cn]
    host_aliases:
      - host: www.yn.gov.cn
        canonical_host: yn.gov.cn
        evidence_ref: evidence/source-cn-yn-zcwjk-host-alias.json
        reviewed_at: 2026-08-03
    allowed_paths: [/zwgk/]
    methods: [GET, HEAD]
    profile_id: local-government-v1
    recipe_id: cn-yn-zcwjk
    adapter_id: configured
    disclosure_scope: proactive
    lifecycle_state: enabled
    terms:
      reviewed_at: 2026-08-03
      evidence_ref: evidence/source-cn-yn-zcwjk-terms.json
      actions:
        discover: allow
        fetch: allow
        transient_store: allow
        candidate: unknown
        ingest: unknown
        index: unknown
        external_transfer: unknown
        export: unknown
        redistribute: unknown
    robots_url: https://www.yn.gov.cn/robots.txt
    min_interval_seconds_override: 2.0
    concurrency_limit: 1
    external_links: handoff_only
    review_expires_at: 2027-02-03
```

字段约束：

- 必填：`schema_version`、`source_id`、`entrypoints`、`canonical_hosts`、`allowed_paths`、`profile_id`、`recipe_id`、`disclosure_scope`、`lifecycle_state`、`terms`。
- `canonical_hosts` 必须是规范化精确 host，不允许 `*.gov.cn` 通配。
- `allowed_paths` 必须非空且不能等价于无界 `/`，除非有专门审查证据。
- `methods` 默认仅 `GET`、`HEAD`；POST API 必须显式注册且证明是公开读取接口。
- `disclosure_scope` 只表达来源可发现主动公开材料，不替代文献级 `disclosure.mode`（见 PolicyBase_04 §4）。
- `authorized` 或人工导入类来源必须另有动作授权引用。
- `terms.actions` 的键只允许 PolicyBase_04 规范动作枚举；`store`、`retain`、`publish` 或未知动作必须 schema fail；缺失动作按 `unknown`。
- `review_expires_at` 到期、证据缺失或 schema 不识别时来源不可自动运行。
- `min_interval_seconds_override` 单位固定为秒，必须是 schema 规定范围内的有限正数；最终请求间隔取它、Profile/system 下限与 robots `Crawl-delay` 的最大值，任何覆盖不得加快请求（执行见 PolicyBase_11）。

`registry_entry_semantic_hash` 的算法与生成语义见 PolicyBase_07；本卷只引用，不重定义。

## 4. source_id 与身份分离

`source_id` 使用小写 ASCII kebab-case，格式：

```text
cn-{org-or-region}[-{subregion}]-{function}
```

常用功能后缀：`zcwjk`、`gz`、`flk`、`xxgk`、`zfgb`、`gfxwj`、`import`。功能后缀表达入口用途，不决定文献最终分类（分类见 PolicyBase_05）。

示例：`cn-npc-flk`、`cn-gov-zcwjk`、`cn-yn-zcwjk`、`cn-yn-km-xxgk`。

`source_id` 被 candidate、manifest 或 checkpoint 引用后不得静默重命名；迁移必须保留 alias 与生效时间（身份稳定性与 legacy/map drift 见 PolicyBase_07）。

身份四元必须分离记录，任何一个都不能自动推导另一个：

- `operator_org_id`：平台运营方（运行来源的组织）；
- `discovered_by_source_id`：发现外链的来源；
- `fetched_by_source_id`：实际获取来源；
- `issuers[].org_id`：文献发文机关。

来源功能（如 `zcwjk`）不得等同于发文机关，也不得等同于运营方。

## 5. host alias 与来源边界（不变量：精确匹配 + 未知隔离）

host alias 必须显式登记，不能由 DNS、重定向或相似域名自动推断。每个 alias 必须包含 `host`、`canonical_host`、`evidence_ref`、`reviewed_at` 与有效范围。

`www.` 不全局静默剥离；它只能通过显式 alias 归一化。这样既兼容常见主站，又不会错误继承独立子站许可。

运行时遇到以下情况必须进入 `unmatched_url_quarantine`（执行细节见 PolicyBase_11）：

- host 未命中 canonical host 或有效 alias；
- host 命中但 path 未进入 `allowed_paths`；
- 重定向跨到未注册 host；
- 页面或 API 返回未登记的附件 host；
- URL 规范化结果不唯一。

隔离记录保留发现来源、原始/规范化 URL、重定向链、时间和证据位置。它只能生成人工 triage 或来源变更提案，**不得**自动创建 alias、扩展 path 或抓取正文。

> 不变量：精确匹配 + 未知隔离没有「软匹配」回退。任何放宽都是对本卷权威边界的违反。

## 6. Profile

Profile 表达多个来源共享的技术族默认值，正式位置 `data/sources/profiles/`。

Profile 可以定义：

- transport：普通 HTTP、标准浏览器渲染、公开 JSON/XML API；
- 默认超时、保守速率、编码策略；
- 受控分页能力；
- 默认页面类型和字段下限；
- 附件发现和 URL 规范化默认值；
- 允许 Recipe 覆盖的字段白名单。

Profile **不包含**：来源准入、条款结论、具体 selector、凭据、可执行代码。只有两个以上来源确实共享的行为才能上升为 Profile。

建议初始族：`gov-ssr-v1`、`gov-spa-v1`、`gov-public-api-v1`、`local-government-v1`、`disclosure-page-v1`、`manual-import-v1`。名称不是兼容性保证，行为由 schema 版本与 fixture 证明（fixture schema 见 PolicyBase_12（草案，实现后生效））。

Profile 作为配置组件，其发布生命周期状态机见 §13。

## 7. Recipe

Recipe 是一个 `source_id` 的声明式覆盖，正式位置 `data/sources/overrides/{source_id}.yaml`。

Recipe 可以定义：

- entrypoint 角色和列表/详情/API 入口；
- 受控分页参数、停止条件、最大页数和重复检测；
- 来源特有字段映射和附件发现；
- 规则链的技术覆盖白名单；
- 页面类型提示、渲染等待条件和 API 响应映射；
- 允许的 POST 读取请求体模板，前提是 Registry 已允许 POST。

Recipe **不得包含**：任意代码、凭据、来源授权结论、跨域许可、合规豁免。Recipe override 只能覆盖 Profile/Rule 标明可覆盖的技术字段，且不能降低限制。

Recipe 作为配置组件，其发布生命周期状态机见 §13。

## 8. Rule 与 Trait（仅注册引用）

Rule 是按规范化 URL 和响应特征匹配的版本化解析知识；Trait 是可显式复用的声明式片段。**完整 schema、匹配语言、deny、pre-fetch/post-fetch 能力边界、fixture、回滚 reprocess 见 PolicyBase_12（草案，P2 晋升后生效）**。

本卷仅规定注册层约束：

- Source Registry 不直接绑定 `rule_id`；Rule 与 source 弱关联。
- Rule 不绑定 `source_id`，但匹配结果必须仍在当前来源的 host/path 边界内（边界由本卷 §5 强制）。
- Rule/Trait 只能禁止或收紧 `fetch`、link follow、`transient_store` 等动作，不能设置「允许抓取/保存/发布」（动作语义见 PolicyBase_04）。
- Rule-Pack 作为配置组件的发布生命周期见 §13；Rule-Pack 特有事件字段（如 selector 命中/未命中、结构基线漂移分级）由 PolicyBase_12（草案，实现后生效）定义，状态机本身引用本卷。

## 9. Adapter（注册 + capability 边界）

Adapter 只处理声明式配置无法表达的公开页面例外：公开 API 的动态但非认证 token、多轮公开读取、历史模板分支、复杂响应组装。

**注册层约束（本卷 owner）**：

- Adapter 必须在 Registry 中显式登记 `adapter_id`，并声明 capability（`discover`、`parse` 等可声明能力子集）。
- Adapter 必须有独立 fixture、威胁边界和审阅记录。
- Adapter 仅产出中间对象（Stub/Draft/CandidateRecord 见 PolicyBase_11）；不得写正式文献或索引。
- Adapter 由 Engine 统一执行网络、robots、限流、checkpoint 和合规门（运行接口见 PolicyBase_11 §3）。
- Adapter 必须有超时、请求预算和确定性错误码。

**capability 边界（本卷 owner）**：

- Adapter 不得持有登录凭据。
- Adapter 不得绕过 challenge（验证码、登录、付费墙、WAF 一律视为访问控制事件，阻断并 handoff）。
- Adapter 不得自行扩大 host/path 范围。
- 当声明式配置（Rule/Recipe）能够表达某例外后，对应 Adapter 代码例外必须退回 Rule/Recipe 并废弃（配置优先原则）。

Adapter 作为配置组件，其发布生命周期状态机见 §13。

## 10. 站点形态准入能力索引

下表是**准入能力索引**：声明各类站点形态在本分层模型中的首选机制与边界。运行规则（SSR/SPA/API/分页的运行时处理、redirect quarantine 执行、robots 限流执行）见 PolicyBase_11 §8；Rule 表达（selector、API 路径、分页、URL rewrite、附件发现）见 PolicyBase_12（草案，实现后生效）。

| 形态 | 首选机制 | 准入边界 |
|---|---|---|
| SSR HTML | Profile + Rule selector | 普通 HTTP，只读 GET/HEAD |
| SPA | 标准浏览器或公开 API Profile | 不隐藏自动化身份；challenge 即停止 |
| JSON/XML API | API Profile + Recipe/Rule mapping | 只用公开、已登记 method/path |
| 多分页 | 受控 pagination enum | 必须有停止条件、预算和重复检测 |
| 附件型正文 | Rule 发现附件，正文处理见 PolicyBase_13 | 附件 host/path 仍须注册或 handoff |
| 多模板历史页 | 多条版本化 Rule 或 Adapter | 以 fixture 和 post-fetch 特征区分 |
| 外链转载/原文 | Registry longest match handoff（见 §11） | 不继承发现来源许可 |

WAF、验证码、登录/付费墙**不是一种「抓取等级」**，而是访问控制事件，必须阻断并 handoff。TLS/浏览器指纹规避不属于支持能力（访问控制边界见 PolicyBase_04 §5）。

## 11. 外链路由

路由是 Registry 的派生函数，不是第二份权威。规则：

1. 先按规范化精确 host/alias 匹配（精确匹配不变量见 §5）；
2. 再按允许 path 最长匹配；
3. 同长度冲突必须隔离，不得猜测。

只有目标来源满足以下全部条件时，才能创建 HandoffTask：

- `lifecycle_state=enabled`；
- 审查未过期（`review_expires_at` 未到期）；
- 动作范围有效（`terms.actions` 覆盖目标动作）。

目标来源必须使用自己的 Registry、Profile、Recipe、Rule、robots、条款和限流——**不继承发现来源的任何许可或配置**。

`disabled`、`paused`、过期或未匹配目标只记录 provenance/triage。外链发现不得自动下载、注册、扩权或改变来源优先级。

## 12. 来源生命周期与持久状态

```text
proposed → reviewed → enabled ↔ paused → retired
```

状态语义：

- `proposed`：只有调查材料，不可自动运行；
- `reviewed`：身份、host/path、robots、条款和证据齐全；
- `enabled`：允许在动作上限内运行；
- `paused`：由维护者或受审查治理流程持久设置；
- `retired`：不再运行，保留历史引用。

转换约束：

- Engine 只能记录 run 内阻断和 `pause_recommended`，不能自行持久暂停；
- host 迁移、条款变化、robots 实质变化、连续结构漂移或访问控制事件都应触发复核；
- 每次状态转换必须记录 actor、time、reason、evidence 和前后 registry revision；
- 只有 `enabled` 可进入普通自动 run；
- `paused` 恢复必须回到已重新审查的 `enabled`；
- `retired` 不可直接恢复。

`lifecycle_state` 是来源**唯一持久状态**。兼容导入若遇到旧 `enabled`/`paused` 布尔字段，只能由显式 migration 一次性转换；矛盾或不能唯一映射时拒绝。

> 注意区分：本节是**来源**生命周期（per-source 持久状态）；§13 是**配置组件**发布生命周期（per-release 持久状态）。两者不混用。

## 13. 配置组件发布生命周期状态机（跨组件统一 owner）

本节是 **Profile / Recipe / Adapter / Rule-Pack 的统一发布状态机 owner**。所有配置组件的发布生命周期均引用本节；PolicyBase_12（草案，实现后生效）只追加 Rule-Pack 特有事件字段，状态机本身引用本卷。

### 13.1 状态枚举

发布状态与不可变组件内容分离。组件内容（schema、selector、代码、默认值）一经发布即不可变；同一 ID/version 的内容不得变化。发布状态枚举：

```text
experimental → canary → stable → suspended → deprecated
                                      ↓
                                   rejected（终态，可从任一前置态进入）
```

状态语义：

- `experimental`：仅离线 fixture 验证；不可触网；
- `canary`：仅限量网络 run，且产物不可 ingest；
- `stable`：可进入普通生产 run；
- `suspended`：维护者持久暂停（含安全/合规原因）；不可进入新 run，已发布 bundle 中的引用按各组件 suspend 合同处理；
- `deprecated`：仍可被现存 bundle 引用，但不得被新 bundle 选中；后继者须迁移；
- `rejected`：审阅拒绝的终态；不可进入任何 run。

只有 `stable` 可进入普通生产。`suspended`/`deprecated` 的恢复路径：必须以新 version 重新走 `experimental → canary → stable`。

### 13.2 组件类型与必备 fixture

| 组件 | 必备 fixture 覆盖 | 备注 |
|---|---|---|
| Profile | transport 默认的正/负 fixture | 越权 fixture：企图声明准入/条款结论时 fail |
| Recipe | 字段映射、分页/API 覆盖的正/负 fixture | 越权 fixture：企图持代码/凭据时 fail |
| Adapter | discover/parse capability 的正/负 fixture | 越权 fixture：企图持凭据/绕 challenge 时 fail |
| `Rule-Pack` | selector/API/分页/rewrite 的正/负 fixture（schema 见 PolicyBase_12（草案，实现后生效）） | 越权 fixture：企图设「允许」动作时 fail |

fixture manifest schema 见 PolicyBase_12（草案，实现后生效）。所有 fixture 必须有版本化质量阈值。

### 13.3 发布条目最小合同

每个发布条目至少包含：

- 组件 ID（`profile_id` / `recipe_id` / `adapter_id` / rule-pack ID）；
- 语义版本；
- 不可变内容 digest；
- schema version；
- 兼容 Engine 范围；
- 发布状态（§13.1 枚举）；
- fixture 清单；
- 前一 stable / rollback target；
- 审阅证据。

生产 run 只冻结精确发布版本，**不读取浮动 latest**。

### 13.4 resolved release bundle

任一配置组件变化必须生成新的 resolved release bundle，包含：

- Registry revision；
- Profile、Recipe、Rule Pack、Adapter 的精确版本/digest；
- 整体 digest。

drift 事件必须列出可疑组件；canary stop 后维护者只能选择已验证 rollback target 创建新 bundle 和新 run。旧 candidate 按 `discard | review | reprocess` 处理；已 ingest 对象只生成 `ReprocessHandoff`，**不得由配置回滚直接覆盖**。

组件恢复、暂停、弃用及回滚的 `actor` / `evidence` / `effective_at` 写入 append-only release metadata。

### 13.5 placeholder 适用性裁定（统一 owner）

**裁定**：`experimental` 状态（即「调查阶段」）适用于所有组件类型（Profile / Recipe / Adapter / Rule-Pack）的 placeholder 发布。

具体规则：

- placeholder 组件必须以 `experimental` 发布，明确标注「placeholder: true」与调查来源（如 `seeds/provinces/*.yaml`，见 §14）；
- placeholder 组件不得晋升 `canary`，除非其 host/path/action 已在 Registry 中正式注册且通过审查；
- placeholder 组件不得被任何生产 bundle 引用；
- placeholder Rule-Pack 的额外约束（如 fixture 最小集）见 PolicyBase_12（草案，实现后生效）。

此裁定统一适用于所有组件类型，PolicyBase_12（草案，实现后生效）不重复定义。

## 14. 来源矩阵治理 ＋ provinces 性质声明

### 14.1 来源矩阵是 registry 派生视图

国家、省、市、县来源矩阵是 registry 数据视图（按 `authority_level`、`jurisdiction`、`source_type` 等字段生成的派生表），**不是第二份 URL 权威**。任何调研报告中的 URL 都只是 proposed input；进入 registry 前必须重新验证并保存正式证据快照。

来源建设优先级不改变合规、分类或合并规则。政府四库可由同一入口发现，也可拆成多个 source；拆分依据是 host/path、运营方、条款、Profile/Recipe 或公开证据是否不同。

政府信息公开子栏目（`guide` / `regime` / `proactive_catalog` / `annual_report` / `upon_request`）是发现语义，**不授予正文许可**；`upon_request` 只允许公开说明。

### 14.2 `seeds/provinces/*.yaml`（31 省）+ `SUMMARY.md` 性质声明

**性质裁定**：`seeds/provinces/*.yaml`（31 省）与 `seeds/provinces/SUMMARY.md` 是**来源调研材料 / proposed input**，具备以下性质：

- **不是 registry**：不含 `source_id`、`terms`、`lifecycle_state`、不可变 digest、registry revision；
- **不是 fixture**：不构成任何 Profile/Recipe/Adapter/Rule-Pack 的覆盖证据；
- **不是正式证据快照**：调研日期（2026-07-22）的可达性、HTTP 状态、HTML 树结构均为观察性事实，不是审查证据；
- **不是第二权威**：本卷不描述其字段 schema，避免与 Registry schema（§3）形成双权威。

**进入 registry 的强制条件**：

- 每条 URL 必须逐条重新验证 host/path/method/action 准入；
- 每个独立子域（如 `xxgk.{省}.gov.cn`、`ysqgk.{省}.gov.cn`、`zfgb.{省}.gov.cn`）必须独立注册，**不继承主站许可**（精确匹配不变量见 §5）；
- 必须保存正式证据快照（robots、条款、审查记录），写入 `evidence/`；
- 调研材料中标注的「WAF 顽固」「SPA shell」「域名访问失败」等观察性事实必须经复核后才能决定是否进入 `proposed` 或直接放弃。

调研材料的门禁处理（如何对 proposed input 做准入审查）不在本卷范围。

### 14.3 调研观察性事实的引用方式

本卷在举例（如 §3 的 `cn-yn-zcwjk`）时引用调研材料的事实，仅作 illustrative 用途，不构成对该 URL 的注册授权。注册授权必须以 registry.yaml 中的正式条目为准。

## 15. 迁移目标

正式资产（desired 视角）：

- `data/sources/registry.yaml` 与 versioned schema；
- `data/sources/profiles/`；
- `data/sources/overrides/`；
- `data/runtime/quarantine/unmatched_urls.jsonl`；
- `docs/specs/source-registry.md`；
- 来源校验与矩阵生成测试。

## 16. 验收契约

机器验收至少覆盖（脚本「待实现，重构期不执行」）：

1. `source_id` 唯一、稳定并与 Recipe 对齐；
2. host 精确匹配，显式 alias 有证据且不隐式继承子域；
3. path/method/action 均在准入上限内；
4. 未匹配、跨 host redirect 和冲突最长匹配进入隔离；
5. operator、discovered_by、fetched_by、issuer 不混用；
6. Profile/Recipe/Rule/Adapter 不能放宽 Registry 或 PolicyBase_04；
7. 审查过期、证据缺失、`disabled`/`paused` 来源 fail-closed；
8. Adapter 已注册并有 capability/fixture；
9. WAF、验证码、登录和付费墙没有自动绕过配置；
10. 来源矩阵可由 registry 确定生成，不维护第二份 URL 表；
11. §13 状态机闭环：`experimental → canary → stable` 唯一晋升路径；`rejected` 终态不可恢复；`suspended`/`deprecated` 必须以新 version 重新晋升。

```bash
policybase verify sources --registry data/sources/registry.yaml  # 待落地
pytest tests/golden/sources/                                      # 待落地
```

## 17. 不得降级的边界

- 未注册 host/path 不抓正文；
- 不隐式继承子域、redirect 或发现来源的许可（精确匹配不变量）；
- 不把来源功能当作文献分类或发文机关；
- 不让 Rule/Adapter 授予动作许可；
- 不把 WAF/challenge 作为可自动攻克的适配级别；
- 不以静态调研 URL 表（含 `seeds/provinces/*.yaml`）替代版本化 Registry 和证据；
- 不以浮动 `latest` 引用运行生产 bundle；
- 不以配置回滚直接覆盖已 ingest 对象（只生成 `ReprocessHandoff`）。

## 18. 与其他分卷的接口

- PolicyBase_04：合规动作枚举、`disclosure.mode`、外部模型 gate 业务规则、访问控制边界、本地预检。
- PolicyBase_05：文献分类树、TYPE 决定层（来源功能后缀不决定分类）。
- PolicyBase_07：`source_id` 身份稳定性、`registry_entry_semantic_hash` 算法、legacy/map drift。
- PolicyBase_11：采集运行时（Engine 职责、Adapter 运行接口、redirect quarantine 执行、checkpoint、canary stop 运行时、退出码、SSR/SPA/API/分页运行规则）。
- PolicyBase_12（草案）：Rule/Trait schema、匹配语言、deny、pre-fetch/post-fetch 能力边界、fixture manifest schema、结构基线漂移分级、Rule-Pack 特有发布事件字段、canary 晋升门。
- PolicyBase_13：附件正文处理、OCR 引擎合同（附件 host/path 边界仍由本卷强制）。
- PolicyBase_17：CLI 入口（`source`/`scrape`/`import` 子命令绑定、`--decisions`、路径安全）。

