# PolicyBase URL 规则、Trait 与 Rule Pack 发布

> 状态：主权威草案
> 晋升：实现后成为运行时迁移源
> 分卷编号：PolicyBase_12
> 主题：url-rule-trait
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase
---

## 1. 定位与阶段归属

本卷是 **Rule / Trait schema、匹配语言、fixture、结构漂移分级、canary 晋升门、Rule Pack 发布与回滚 reprocess** 视角的唯一 owner 草案。Rule 保存可执行的解析知识；Trait 保存显式复用的声明片段；Rule Pack 把不可变版本化的 Rule/Trait 集合冻结为生产可引用单元。

统一配置链（概念，跨组件命名权见 PolicyBase_10）：

```text
Source Registry → Profile → Recipe → Rule/Trait → Adapter → AcquisitionEngine
```

非职责边界（一句引用，不展开）：

- 来源身份、host alias、Adapter 注册与跨组件发布状态机：见 PolicyBase_10 §13。
- Engine 执行、两阶段匹配的运行时语义、run/candidate 写入：见 PolicyBase_11。
- 合规与访问控制高于一切技术规则：见 PolicyBase_04。
- canonical URL 归一化：见 PolicyBase_07。

**若未实现，本卷所有 CLI、目录和 schema 只是目标合同，不得声称运行时存在。**

## 2. 权威与不变量

1. PolicyBase_10 的 Registry 是来源准入和 host alias 唯一权威。
2. PolicyBase_04 的合规与访问边界高于一切技术规则。
3. PolicyBase_11 定义 Engine、两阶段匹配、run/candidate/漂移执行语义。
4. PolicyBase_07 定义 canonical URL；本卷只定义匹配所需的额外表示。
5. Rule/Trait 不授予 `discover/fetch/transient_store/candidate/ingest/index/external_transfer/export/redistribute` 权限。
6. Rule 只能解析、限制或拒绝；不得出现 `allowed: true`、`bypass`、`stealth`、`fingerprint spoof` 等许可/规避语义。
7. deny 在任何合并顺序中不可被撤销。
8. host 精确匹配；不使用 `*.gov.cn`，不隐式继承父域/子域或 `www.`。
9. host alias 只能来自 Registry 的显式、已审查映射；Rule 只匹配 alias 归一化后的 canonical host。
10. 运行快照固定后不得热更新规则。

## 3. 迁移资产（目标合同）

```text
data/rules/
├── index.yaml
├── schema/
│   ├── rule.schema.json
│   ├── trait.schema.json
│   ├── pack.schema.json
│   └── fixture-manifest.schema.json
├── _traits/
├── _deny/
├── national/
├── provincial/
├── municipal/
├── ministry/
└── manual/

tests/fixtures/rules/
tests/golden/rules/
src/policybase/pipeline/acquisition/rules/
docs/specs/domain-rules.md
```

目录只供人类管理。机器注册权威是 `data/rules/index.yaml`；未注册 YAML 不参与匹配。实现前上述路径均为目标合同。

## 4. schema 与版本

Rule、Trait、Pack、fixture manifest 分别有 schema version。每个 Rule 还有行为语义版本：

- `patch`：注释、经验或不改变输出的修正；
- `minor`：向后兼容的新 selector/模板；
- `major`：匹配范围、字段语义、URL rewrite、分页或输出发生不兼容变化。

生产 run 必须记录 `rule_id`、version、文件 digest、pack digest 与 schema version。schema major 未识别时 fail-closed，不得最佳努力解析。

规则 ID 格式：`{canonical-host}-{section}-v{major}`。同 ID/version 的内容 digest 不得变化；修订必须升版本。**Rule/Trait/Pack 内容文件不包含可变 `status` 字段**；发布状态属于 §14 的 append-only release metadata，避免暂停或弃用破坏内容 digest。

## 5. Rule v1 概念 schema

```yaml
schema_version: "1.0"
rule:
  id: yn.gov.cn-zwgk-v1
  version: "1.1.0"
  phase: [pre_fetch, post_fetch]
  priority: 100
  replaces: yn.gov.cn-zwgk-v1@1.0.0

  match:
    canonical_hosts: [yn.gov.cn]
    methods: [GET]
    request_roles: [listing, detail]
    path_regex:
      - '^/zwgk/(?:.*)$'
    query_keys_any: []
    response:
      content_types: [text/html]
      status: [200]
      dom_signatures:
        - selector: 'main .TRS_Editor'
          min_count: 1

  extends:
    - trait: gov-html-detail-v1@1.0.0

  constraints:
    deny_paths: ['^/zwgk/(?:login|apply)/']
    max_depth: 3
    max_response_bytes: 20971520
    timeout_seconds_max: 30
    retries_max: 2
    browser: standard_only

  transport:
    kind: http
    wait: dom_ready
    charset: auto

  parse:
    page_type: detail
    selectors:
      title: {css: 'h1', cardinality: one}
      document_number: {css: '.doc-number', cardinality: zero_or_one}
      body: {css: '.TRS_Editor', cardinality: one}
      attachments: {css: '.attachments a[href]', attr: href, cardinality: many}
    fields:
      issue_date:
        from: {css: '.pub-date', cardinality: zero_or_one}
        transforms: [trim, parse_cn_date]
    pagination: {kind: none}

  url_rewrite:
    - id: detail-relative-v1
      pattern: '^/zwgk/(\\d+)\\.html$'
      replacement: '/zwgk/detail.html?id=\\g<1>'
      apply_to: discovered_link

  quality:
    required_fields: [title, body]
    thresholds:
      required_field_failure_rate: 0.05
      empty_body_rate: 0.01
      redirect_out_of_scope_count: 0

  testing:
    fixtures:
      - manifest: tests/fixtures/rules/yn.gov.cn/detail/manifest.yaml
    negative_fixtures:
      - manifest: tests/fixtures/rules/yn.gov.cn/login/manifest.yaml
    last_verified_at: 2026-08-03

  notes:
    experiences: ['普通 SSR 详情页']
    pitfalls: ['历史页面使用另一正文容器，须独立 Rule']
```

Schema 必须拒绝未知字段；扩展字段使用显式 namespaced `extensions`，不能静默忽略拼写错误。

## 6. 匹配语言

### 6.1 URL 表示

URL 先按 PolicyBase_07 canonicalization，再通过 Registry alias 映射 canonical host。匹配对象保留 scheme、host、port、path、规范化 query keys 与 method；fragment 不参与匹配。

Rule 不得自行剥离 `www.` 或推断 alias。未匹配、alias 冲突或 canonicalization 非唯一时进入 PolicyBase_10 / PolicyBase_11 quarantine。

### 6.2 正则

v1 使用 Python `re` 兼容语法并要求全模式锚定 `^...$`。replacement 使用 Python `\g<name>` / `\g<1>`，不允许 `$1` 混用。

验证器必须限制 pattern 长度、嵌套量词与已知灾难性回溯结构；匹配必须有实现级时间/输入长度预算。规则不得执行任意表达式或脚本。

### 6.3 selector 与结构查询

- HTML v1：CSS selector；
- JSON v1：受限 JSONPath 子集，必须在 schema 中枚举支持操作；
- XML v1：受限 XPath 子集；
- 文本字段：受控 transform enum；
- 禁止 JavaScript / eval / Jinja / 任意 Python 表达式。

每个 selector 必须声明 cardinality：`one`、`zero_or_one`、`many`。`one` 的零命中或多命中是结构错误，不能任取第一个。

### 6.4 URL rewrite

每条 rewrite 必须有 ID、输入角色、锚定 pattern、replacement、host-preservation 断言与 golden。默认只允许改 path/query，不允许改变 scheme/host；跨 host 结果必须进入 Registry handoff。

rewrite 链最多执行一次每 ID，并检测循环。rewrite 不能生成未注册 method/path。

## 7. pre-fetch 与 post-fetch 能力边界

### 7.1 pre-fetch

只能匹配请求前事实：canonical host、path、query keys、method、request role。允许输出：

- deny / 限制 path、method、depth、bytes、timeout、retry、transport；
- 普通 HTTP/API/标准浏览器的技术选择；
- URL rewrite、请求角色与解析候选集。

不得依赖 Content-Type、DOM 或响应正文，也不得增加 Registry 范围。

### 7.2 post-fetch

在重新验证 final URL 后，匹配 HTTP status、Content-Type、charset、DOM/API signature 与页面类型。允许选择 selector、field extractor、pagination parser、attachment discovery 与质量阈值。

post-fetch Rule 只能在 pre-fetch 上限内工作。响应若是 challenge、登录、付费或未识别类型，先由 PolicyBase_04 / PolicyBase_11 阻断，不进入「兼容性 workaround」。

### 7.3 多模板

同一路径可能有历史/当前模板。多个 post-fetch Rule 必须由互斥 signature 区分；同时命中同 priority 的不兼容解析规则返回 `rule_ambiguous`。不得以文件顺序取胜。

## 8. Trait

Trait 是版本化声明片段，只能被 Rule 的精确 `trait_id@version` 引用。Trait 不能引用 Rule，依赖图必须无环，最大深度由 schema 固定。

适合 Trait 的内容：通用 selector 片段、分页类型、编码、标准渲染等待、质量阈值。不适合 Trait：host/path 范围、来源许可、条款、凭据、WAF 绕过、单站临时 workaround。

Trait 升 major 不自动影响引用者；Rule 必须显式升级引用并重新验证 fixture。

## 9. 配置解析与合并

配置加载顺序遵守统一链：Registry → Profile → Recipe 上下文 → Rule/Trait 匹配 → Adapter capability。最终 resolved technical config 的合并顺序：

```text
system defaults
  < Profile defaults
  < Trait fragments
  < domain base Rule
  < path/template Rule
  < Recipe allowlisted technical overrides
  < deny/restriction intersection
```

Recipe 在 Rule 匹配前提供 source/entrypoint/request-role 上下文，其覆盖 patch 在规则链确定后应用。Adapter 只能消费 resolved config，不能再修改权限或范围（Adapter 注册与 capability 见 PolicyBase_10）。

字段合并：

- map：按 key 合并，类型冲突报错；
- ordered list：显式 `replace` 或 `append_unique`，默认不猜；
- selector：同字段多定义必须有明确优先级或互斥 signature；
- 数值限制：取更严格值，如更小 bytes/concurrency/retry、更大 delay；
- deny：集合并集，不可删除；
- permission：不属于 Rule schema，若出现即校验失败。

每个 resolved config 必须输出来源追踪，说明每个值来自哪一层、哪个版本与 digest。

## 10. deny 规则

`data/rules/_deny/` 保存可机器匹配的技术拒绝：登录/申请入口、账号页面、非正文下载、已知无限循环、challenge signature、受限 path。

deny 优先于所有 include/parse 配置，不能被 Recipe 或 Adapter 撤销。deny 命中必须输出稳定 reason code。合规拒绝仍由 PolicyBase_04 判定，不能因为尚无 deny Rule 而放行。

## 11. transport 能力边界

Rule v1 可声明：

- `http`：普通 GET/HEAD；
- `public_api`：已登记公开 JSON/XML API；
- `standard_browser`：普通公开 SPA 的标准浏览器只读渲染；
- `manual_handoff`：停止自动获取。

Rule 不得声明反检测 UA、cookie/session 复用、TLS 指纹、webdriver 隐藏、鼠标轨迹、验证码识别或 challenge 求解。WAF/challenge 不是 transport profile；命中必须 `manual_handoff` 与 `pause_recommended`。

## 12. fixture manifest schema

fixture manifest 必须记录：

```yaml
fixture_schema_version: "1.0"
fixture_id: yn-detail-20260803
source_id: cn-yn-zwgk
rule: yn.gov.cn-zwgk-v1@1.1.0
request: {url: ..., method: GET, role: detail}
response:
  status: 200
  final_url: ...
  content_type: text/html
  charset: utf-8
  headers_file: headers.json
  body_file: body.html
  body_sha256: ...
capture: {tool: ..., version: ..., captured_at: ...}
redaction: {applied: true, record: redaction.json}
expected:
  page_type: detail
  required_fields: [title, body]
  attachments: 1
```

每个 stable Rule 至少有正 fixture 与适用的 negative fixture；分页/API/附件/redirect 必须各有覆盖。fixture 必须脱敏、无凭据、可离线复现。sample URL 只是人工提示，不替代 fixture。

## 13. 结构基线与漂移分级

Rule 的测试输出生成 `structure_baseline`，至少包括 DOM/API signature、selector cardinality、字段成功率、列表数量范围、正文长度范围、附件/分页特征与 redirect 范围。

运行指标由 PolicyBase_11 采集，并用 Rule/Pack 中版本化阈值比较。漂移分级（本卷为分级 owner；运行时采集见 PolicyBase_11）：

- `item_anomaly`：单对象异常，进入 review；
- `suspected_drift`：连续异常但未越硬阈值，限制 canary/建议复核；
- `confirmed_drift`：硬阈值越界、必填结构失效或范围变化，停止相关桶并建议暂停。

漂移不能自动改 selector、生成 stable Rule 或覆盖 fixture。自动生成的规则候选只能是 `placeholder/experimental`，必须经 Issue/PR 审阅。

## 14. Rule Pack 发布生命周期（Rule-Pack 视角）

本节只定义 **Rule-Pack 视角特有的发布事件字段与 `index.yaml` 写入规则**。配置组件发布的跨组件统一状态机（状态枚举、流转条件、placeholder 裁定）唯一 owner 是 PolicyBase_10 §13；本卷不重列状态枚举，引用其状态机描述 Rule Pack 的发布事实。

### 14.1 Rule Pack 与发布状态的关系

Rule Pack 是把若干 Rule/Trait 的精确版本与 digest 冻结在一起的不可变集合（详见 §16）。Pack 自身的发布状态、流转条件和 placeholder 裁定见 PolicyBase_10 §13（草案，实现后生效）；本节只记录 Rule-Pack 视角的 release event 与 `index.yaml` 事实。

发布状态**不写回**不可变 Rule/Trait/Pack 内容文件；它保存在本卷权威的 `data/rules/index.yaml`（或后继 release registry）的 append-only release 事件流里。

### 14.2 Rule-Pack 视角特有的 release event 字段

每条 release event 至少记录以下 Rule-Pack 视角字段（跨组件通用字段如 actor/time/reason/evidence 见 PolicyBase_10 §13；此处只列 Rule-Pack 特有补充）：

| 字段 | 含义 |
|---|---|
| `pack_id` | 关联的 Rule Pack ID 与版本（如 `core-government-v1@1.2.0`） |
| `rule_refs` | 此事件影响的 Rule/Trait 精确版本与 digest 列表 |
| `schema_versions` | 涉及的 rule/trait/pack/fixture schema version |
| `release_bundle_refs` | 关联的 Profile/Recipe/Adapter 精确版本（与 PolicyBase_10 release bundle 对齐） |
| `rollback_target` | 暂停或回滚时指向的历史已验证 digest（详见 §17） |
| `effective_at` | 发布生效时间（与 `actor/time` 区分：后者为事件记录时间） |

### 14.3 `index.yaml` 写入规则

`data/rules/index.yaml` 是 Rule Pack 发布事件的机器注册权威，写入规则：

1. **append-only**：事件只能追加，不得改写或删除历史事件；恢复或回滚必须遵守 PolicyBase_10 §13（草案，实现后生效）的版本与发布条件，只追加新事件。
2. **内容/发布分离**：Rule/Trait/Pack 内容文件的 digest 必须与 release event 中记录的 digest 一致；内容修订必须升版本并追加新事件，不得改动已发布版本。
3. **状态变更须 Delivery 证据**：任何状态变更（特别是 stable 晋升、suspended、deprecated、回滚）必须关联 Delivery Issue/PR 与 reviewer 证据；Engine 的暂停建议不能自行改变发布状态。
4. **deprecated 不直接生产**：deprecated 内容只能作为审计或受控再发布的内容来源；rollback 必须按 §17 生成新版本与新发布证据。

## 15. canary 晋升门

experimental 发布进入 canary 前（状态机见 PolicyBase_10 §13）必须：schema 通过、正/负 fixture 通过、deny/权限 lint 通过、离线预期字段通过、无规则歧义。experimental 本身不得用于真实网络；只有完成状态事件后的 canary 发布可进入 PolicyBase_11 的显式 canary run。

canary 必须限定 source、入口、URL/页数、请求预算、并发、candidate 数与持续时间。任何合规/访问控制、越界 redirect、规则歧义或硬漂移立即停止。

晋升 stable 至少要求：

- fixture 全部通过且 digest 固定；
- canary 输出经人工复核；
- 必填字段、空正文、重复、附件、分页指标在阈值内；
- 无 host/path/method 越界；
- resolved config 追踪可复现；
- 明确上一 stable / rollback target；
- Rule Pack 版本与 changelog 已生成，并按 §14.3 追加 release event。

## 16. Rule Pack

生产只能冻结 Pack，不得引用浮动「所有 stable 规则」。Pack manifest 包含 pack ID/version、rule/trait 精确版本与 digest、schema versions、发布日期、兼容 Engine 范围与 rollback pack。

应交付最小 `core-government-v1`，覆盖一个 SSR 来源、一个公开 API/SPA fixture、deny 示例、附件 handoff 与未匹配隔离。P3 首来源以该 pack 的已发布版本为下限。

Pack 发布后内容不可变；变更必须升版并按 §14.3 追加 release event。Engine 不兼容时 fail-closed。Pack 自身的发布状态流转（stable/suspended/deprecated 等）遵循 PolicyBase_10 §13 状态机。

## 17. 回滚与 reprocess（Rule-Pack 视角）

回滚不删除坏版本或历史 run，也不改写 §14.3 的 append-only 事件流。维护者选择上一已验证 stable 内容 digest，按 §14 生成具有新版本/发布证据的 pack，并与 PolicyBase_10 的 Profile/Recipe/Adapter 精确版本一起形成新 stable release bundle，再创建新 run。记录：触发事件、from/to version/digest、所有组件版本、影响窗口、受影响 source/run/candidate 与批准证据。

分类：

- 尚未 ingest 的 candidate：`discard`、`review` 或用回滚 pack `reprocess`；
- 已 ingest 文献：生成 `ReprocessHandoff`，不得由 Rule 工具直接覆盖；
- 仅索引受影响：交给索引重建合同（见 PolicyBase_14）；
- OCR/版面受影响：交给内容处理合同（见 PolicyBase_13）。

reprocess 必须保留旧输出 hash、规则版本、差异与决定，不得伪装成原始首次采集。

## 18. CLI 目标合同

PolicyBase_12 实现后，来源命令下应提供一致的 rule 子域；CLI 总表与解析序由 PolicyBase_15 / PolicyBase_19 负责，本卷只列 rule 子域目标语义：

```bash
policybase source rule validate [--all|--rule ID]
policybase source rule match --source SOURCE_ID --url URL [--response-fixture PATH]
policybase source rule test [--rule ID|--pack ID@VERSION]
policybase source rule explain --source SOURCE_ID --url URL
policybase source rule pack build --manifest PATH
policybase source rule drift --run RUN_ID
policybase source rule rollback-plan --from PACK --to PACK --run RUN_ID
```

`match/explain` 必须输出 pre/post 区分、匹配候选、排序、Trait 展开、Recipe overrides、deny、resolved config 来源追踪与最终 digest。任何真实网络 fetch 仍由 `policybase scrape` 执行，rule 命令默认离线。以下命令为子域目标语义占位；精确参数形式（如 `RULE_REF`/`PACK_REF` 的 SemVer 强制、`SOURCE_ID` 词法）以 PolicyBase_17 绑定为准，本卷不重列。

## 19. 验证与稳定诊断码

静态验证：schema、ID/version/digest、索引唯一性、Trait DAG、host 精确性、正则安全、selector cardinality、rewrite 循环、permission/规避字段、Pack 完整性。

动态验证：fixture parse、pre/post 匹配、相同输入确定性、规则歧义、deny 不可覆盖、Recipe override 白名单、漂移阈值、canary stop、回滚计划与 reprocess handoff。

最低诊断码（Rule-Pack 视角专用；通用 cli_* 诊断码见 PolicyBase_19）：

- `rule_schema_invalid`
- `rule_version_immutable_violation`
- `rule_unmatched`
- `rule_ambiguous`
- `trait_cycle`
- `regex_unsafe`
- `selector_cardinality_violation`
- `rewrite_out_of_scope`
- `permission_field_forbidden`
- `access_evasion_forbidden`
- `fixture_digest_mismatch`
- `pack_incompatible`
- `structure_drift`
- `rollback_target_invalid`

## 20. 不得降级的边界

- Rule 不授予任何动作权限；
- 不使用通配 host 或隐式子域继承；
- 不把 `www.` 静默当成同一 host；
- 不在 Rule 中保存凭据、cookie 或访问 token；
- 不使用 WAF、验证码、TLS/浏览器指纹规避 Trait；
- 不让 experimental/canary 默认生产运行；
- 不热更新 Pack；
- 不改写 `index.yaml` 的历史 release event；
- 不用回滚删除历史或覆盖已入库文献；
- 不以在线 sample URL 替代离线 fixture 与可审计证据。
