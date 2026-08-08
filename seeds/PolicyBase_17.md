# PolicyBase CLI：来源、采集、导入与预检绑定

> 状态：主权威
> 分卷编号：PolicyBase_17
> 主题：cli-source-ingest
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与权威边界

本卷是下列命令及其绑定参数的唯一权威：

```text
policybase source ...
policybase scrape ...
policybase import ...
policybase prepare ...
```

本卷展开：本卷专属词法格式、URL/日期/文本/预算数值约束、`source`（含 `rule` 子链）`scrape`/`import`/`prepare` 的绑定语法与参数合同、路径安全合同、本卷业务诊断码、JSON envelope namespaced 扩展、参数组合测试矩阵与验收。

本卷只引用、不复制下列 owner 卷的权威内容：

- 顶层命令面、跨命令标识（DOC/SOURCE/RULE/PACK/CANDIDATE/RUN/AUTH 等 ID 公共词法）、`AUTH_ID` scope 路由、副作用分层总图、`--dry-run` 适用规则路由 —— 见 PolicyBase_15 §跨命令标识、§副作用分层、§dry-run 路由。
- DOC_ID 等生成语义、canonical 形态、identity/Tier/registry 算法 —— 见 PolicyBase_07。
- reviewed decision schema 业务字段集（decision_domain/action 受控值/basis/evidence_refs/...）、身份层 identity/update 判定 —— 见 PolicyBase_08。
- Rule/Trait/Pack schema、匹配语言、fixture manifest schema、结构漂移分级、canary 晋升门、发布生命周期 —— 见 PolicyBase_12（主权威草案，P2 晋升后生效）。
- Source Registry schema、source_id 身份、host alias、Profile/Recipe/Adapter、来源生命周期、来源矩阵治理 —— 见 PolicyBase_10。
- acquisition 运行快照、Engine 职责、Adapter 运行接口、中间对象、robots/限流、redirect quarantine、增量 —— 见 PolicyBase_11。
- 全局参数位置与解析序、通用 `cli_*` 诊断码、统一退出码、依赖安装 —— 见 PolicyBase_19。
- 内容生产、edition/current 写入、索引投影 —— 见 PolicyBase_13、PolicyBase_09、PolicyBase_14。

若其他 active seed 中出现与本卷不同的本命令参数、组合或示例，以本卷为准，并按 `cli_contract_conflict` 报告。

阶段门：PolicyBase_12 Rule/Trait/Pack schema 尚未晋升期间，`source rule ...` 子链只属于目标合同，必须返回 `capability_not_active`，不得伪装执行成功；其余命令也只能在对应阶段 capability 已被验收后启用。

## 2. 副作用与联网边界

本卷为每个命令定义其读取、默认写入、真实网络与禁止直接写入对象（具体命令副作用表归本卷）。副作用分层总图见 PolicyBase_15 §副作用分层。

| 命令 | 读取 | 默认写入 | 真实网络 | 绝不直接写入 |
|---|---|---|---|---|
| `source list/show` | Registry 与本地 evidence | 无 | 否 | Registry、run、candidate、edition、index |
| `source rule validate/match/test/explain/drift/rollback-plan` | 本地 Registry、Rule、fixture、run snapshot | 无 | 否 | Rule/Pack、Registry、candidate、edition |
| `source rule pack build` | 本地 manifest、Rule、fixture | 忽略工作区中的 pack build artifact | 否 | 已发布 pack/index、Registry、正式数据 |
| `scrape` | Registry 与固定配置链 | run、observation、candidate、checkpoint、quarantine/handoff | 是；`--dry-run` 时否 | edition、current、index |
| `import` | 用户明确给出的本地文件 | candidate 与候选 manifest | 否 | edition、current、index |
| `prepare` | candidate、decision、正式包只读快照 | immutable decision/routing/hold 与 process-ready handoff | 否 | content confirmation、edition、switch event、current、index；正式 ingest action 只由 PolicyBase_18 `process confirm` 执行，rollback 只切既有 current |

只有以下两种 acquisition mode 可以联网：

1. 普通 `policybase scrape`，包括 discovery、定向获取和 `--update`；
2. 显式 `policybase scrape --canary ...`。

`source rule` 命名空间没有 `--live`、`--fetch`、`--capture-url` 或等价旁路。`rule match/test/explain` 接收的 URL 只是待匹配数据；post-fetch 事实只能来自本地脱敏 fixture。对本卷明确绑定 `--dry-run` 的写入/联网命令，它始终意味着不联网、不写文件、不更新 checkpoint/current/index，只输出确定性计划；只读命令不接受该参数（按 PolicyBase_19 `cli_parameter_not_applicable` 拒绝）。

## 3. 本卷专属词法、URL、日期与数值类型

CLI 使用 UTF-8。参数经 Unicode NFC 规范化后验证；NUL、C0/C1 控制字符、双向控制字符和未配对 surrogate 一律拒绝。值前后空白不静默修剪；诊断可以建议去除，但执行必须拒绝歧义输入。

### 3.1 本卷专属标识格式

公共跨命令标识（`SOURCE_ID`/`DOC_ID`/`CANDIDATE_ID`/`RUN_ID`/`AUTH_ID` 等）的生成语义与公共词法见 PolicyBase_15 §跨命令标识（CLI 词法投影）与 PolicyBase_07（生成语义）；本卷只追加本卷专属格式约束：

| 类型 | 本卷追加约束 |
|---|---|
| `RULE_ID` | 1..160 ASCII 字节；不得含 `/\\:@`、空白或路径片段 |
| `RULE_REF` | `RULE_ID@MAJOR.MINOR.PATCH`；SemVer 三段十进制、无前导零；生产/canary/test 必须精确版本 |
| `PACK_REF` | `PACK_ID@MAJOR.MINOR.PATCH`；`PACK_ID` 为 1..128 字节小写 kebab-case；不得使用 `latest/stable/*` 浮动引用 |
| `ENTRYPOINT_ROLE` | `[a-z][a-z0-9_-]{0,63}`；必须与当前 source Recipe 登记值精确相等 |
| `BUCKET_ID` | `[a-z0-9][a-z0-9._-]{0,159}`；必须在目标 run manifest 中登记 |

`RULE_ID`/`RULE_REF`/`PACK_REF` 的语义与 Rule/Pack schema 见 PolicyBase_12（草案）。`ENTRYPOINT_ROLE`/`BUCKET_ID` 的 Recipe/Registry 登记见 PolicyBase_10。

对象不存在与词法非法分开：词法非法返回 `invalid_*_id`（统一码见 PolicyBase_19）；词法有效但 Registry/索引中不存在返回 `*_not_found`。只有 Registry 明确登记的历史完整 source ID alias 可用于迁移解析且必须输出 canonical ID；省名、拼音简称等非完整/未登记 alias 不接受。

### 3.2 URL、日期与文本

| 类型 | 约束 |
|---|---|
| `URL` | 绝对 `http`/`https` URL，1..4096 UTF-8 字节；无 userinfo、fragment、控制字符；host 必须可 IDNA 规范化；最多 200 个 query pair |
| `--year` | 十进制四位数，`1900..UTC 当前年+5` |
| `--from-date/--to-date` | 严格 ISO `YYYY-MM-DD`，必须是真实公历日期；闭区间；`from <= to` |
| `--keyword` | NFC 后 1..200 字符；不能全为空白、含控制字符或被解释为查询语言 |
| `--request-role` | `listing|detail|attachment|api` |
| `--method` | `GET|HEAD|POST`；match/explain 默认 `GET`，再与 Registry/Recipe method 上限求交；用户不能借此扩大 method |

URL 通过词法验证后仍必须经 PolicyBase_07 canonicalization、PolicyBase_10 exact host/alias、longest allowed path 和 method 上限验证。`http` 只有 Registry 明确登记该 scheme 时可用；CLI 不自动升级/降级 scheme，不剥离 `www.`，不接受 `file:`、`data:`、相对 URL 或通配 host。

`--year` 与日期区间互斥。年份/日期是来源查询过滤器，不扩大允许 URL，也不保证目标站支持；Recipe 未声明该过滤能力时早拒绝 `filter_capability_unsupported`，不得下载后假装服务端已过滤。

### 3.3 预算与批量数值

所有整数只接受十进制 ASCII，禁止符号、指数、小数、千位分隔和前导 `+`。

| 参数 | 范围 | 语义 |
|---|---|---|
| `--max-pages` | 1..10000；canary 1..200 | 列表/分页获取硬上限 |
| `--max-urls` | 1..10000；canary 1..500 | 本 run 发起 URL 数硬上限 |
| `--max-candidates` | 1..10000；canary 1..200 | candidate 硬上限 |
| `--concurrency` | 1..16；canary 只能 1..2 | 请求任务上限；effective 取用户值与 Registry/Profile 上限的较小值 |
| `--min-delay-seconds` | 0.5..3600，最多三位小数 | 请求最小间隔；effective 取用户、Registry/Profile、robots 值的最大值 |
| `--batch-size` | 1..1000 | prepare 每批预检/路由上限，不是授权或自动确认开关 |
| `--max-files` | 1..100000 | import 枚举文件硬上限 |
| `--max-total-bytes` | 1..107374182400 | import 输入总字节上限（100 GiB） |

用户参数只能收紧 Registry、robots、Profile、Recipe、Rule/Pack 和系统预算。请求更高并发、更短间隔、更宽分页时，不静默采用更严格值后成功：校验阶段返回 `requested_limit_exceeds_policy`，同时报告允许上限和修正示例，避免用户误判实际行为。

## 4. 路径安全合同（本卷 owner）

路径先做字节长度（1..4096）、NUL/控制字符和平台设备名检查，再从当前工作目录解析绝对规范路径。所有路径操作必须使用文件描述符级防竞态或在打开后复核 inode/type；不能只做字符串前缀判断。

共同规则：

- 拒绝符号链接、junction、socket、FIFO、设备文件和 `/proc`、`/sys` 等虚拟文件系统对象；
- 读取时文件必须存在、为允许的普通文件/目录并可读；输出父目录必须已存在、不是 symlink 且在命令允许根内；
- `..` 经解析后若逃出允许根则拒绝；硬链接输入按实际 inode 和保留策略检查；
- glob 只由 import 的目录遍历内部实现；用户值不交给 shell；
- 不覆盖已有文件。需要相同目标时先比较 digest；不同内容返回 `output_exists`；
- 错误日志不得打印输入正文、token、cookie、完整 query secret 或任意文件内容。

命令特定允许根：

| 参数/对象 | 允许根 |
|---|---|
| Rule/Trait/Pack manifest | 仓库 `data/rules/` |
| `--response-fixture` | 仓库 `tests/fixtures/rules/` |
| `--run`/`--resume` | 只经 run registry 解析到 `data/runtime/work/runs/`，不接受任意路径替代 |
| pack build 输出 | `data/runtime/work/rule-packs/` |
| rollback plan 输出 | `data/runtime/work/rollback-plans/` |
| prepare 输入 | `data/runtime/work/candidates/` 或 run manifest 已登记的 candidate 路径 |
| decision 文件 | `data/runtime/work/decisions/`；正式测试 fixture 可来自 `tests/fixtures/decisions/` |
| import 输入 | 用户明确指定的普通文件或目录，可位于仓库外；仍执行上述类型、symlink、大小和合规检查 |
| import metadata | 用户明确指定的单个 YAML/JSON 普通文件，最大 1 MiB |

import 是唯一允许从仓库外读取用户文件的本卷命令。它不会把"用户可读"推定成 retain/index/external transfer/redistribute 授权。

## 5. 全局合同与本卷校验阶段

全局参数（`--config/--workspace/--output/--log-level/--no-color/--help/--version` 等）的位置、类型、组合和副作用见 PolicyBase_19 §2/§3，本卷不建立第二份全局参数表或解析序清单。下文绑定语法只列命令局部参数；需要机器输出时按 PolicyBase_19 将全局参数放在命令前，例如：

```bash
policybase --output json source show cn-hubei-zcwjk
```

`--dry-run` 是本卷对可能联网或写入命令定义的命令局部参数，不是全局参数；只读命令传入它时按 PolicyBase_19 `cli_parameter_not_applicable` 拒绝。

PolicyBase_19 的统一早拒绝完成后，本卷业务校验继续按以下顺序：

1. 本卷标识、日期、预算和路径细化约束；
2. 本卷必填、互斥、依赖、条件必填和禁止组合；
3. 本地对象存在、schema、capability 和固定配置解析；
4. Registry/合规/权限/预算 preflight；
5. 生成不可变 execution plan；
6. 仅在全部通过后执行网络或原子写入。

执行步骤之前不得创建 run 目录、临时文件或日志文件。一次调用可返回多个确定性 usage 诊断，按参数表顺序排列；不得因参数排列次序改变首个错误码。通用未知/重复/类型/组合错误码及纠正格式直接使用 PolicyBase_19，不在本卷另起枚举。

路由门链（candidate→identity→issuer/Tier→observation/update decision→…→process→edition→index）的副作用分层见 PolicyBase_15 §副作用分层；本卷 `prepare` 只覆盖其中由本卷执行的可本地判断的预检与 routing/hold 阶段，edition/current/index 写入不在本卷。

## 6. `source list` 与 `source show`

### 6.1 绑定语法

```bash
policybase source list [--state STATE] [--type SOURCE_TYPE] \
  [--jurisdiction CODE]

policybase source show SOURCE_ID [--resolved]
```

参数：

| 参数 | 必填 | 约束/行为 |
|---|---|---|
| `--state` | 否 | `proposed|reviewed|enabled|paused|retired`；单值 |
| `--type` | 否 | PolicyBase_10 source type 受控枚举；1..64 ASCII；未知值拒绝，不做 substring |
| `--jurisdiction` | 否 | PolicyBase_05/PolicyBase_06 受控行政区 code；大写 ASCII，2..16 字节 |
| `SOURCE_ID` | show 必填 | 完整、精确存在的 Registry ID |
| `--resolved` | 否 | 只展示本地 resolved 配置及各层 provenance/digest；不匹配响应 Rule、不联网 |

`source list/show` 始终只读，不接受 `--dry-run`、`--update`、`--live`、路径或 URL。默认输出不得泄漏凭据、cookie、PAT 或未经脱敏 evidence；Registry 若误含秘密，返回 `secret_material_detected` 而不是打印。

### 6.2 示例

```bash
# normal
policybase source list --state enabled --jurisdiction CN-HB
policybase --output json source show cn-hubei-zcwjk --resolved

# edge：合法但可能为空
policybase source list --type government_gazette --jurisdiction CN-XZ

# error：简称不是 source_id
# 禁止：policybase source show hubei
# exit 2: cli_argument_format；hint: 使用 policybase source list 查找完整 ID
```

## 7. `source rule validate`

### 7.1 绑定语法

```bash
policybase source rule validate (--all | --rule RULE_REF)
```

`--all` 与 `--rule` 恰好一个。validate 执行 schema、index 唯一性、精确版本/digest、Trait DAG、regex/rewrite 安全、permission/evasion lint、fixture manifest 引用和 Pack 引用静态验证；不执行 fixture parse，不写修正。Rule/Trait/Pack schema 见 PolicyBase_12（草案）。

禁止 `--source`、`--url`、`--response-fixture`、`--pack`、`--live`、`--dry-run`。`--rule` 必须是精确 `RULE_REF`，不能使用裸 ID 或浮动状态名。

```bash
# normal
policybase source rule validate --all
policybase --output json source rule validate --rule yn.gov.cn-zwgk-v1@1.1.0

# edge：deprecated 规则仍可验证历史不可变性
policybase source rule validate --rule yn.gov.cn-zwgk-v1@1.0.0

# error
policybase source rule validate --all --rule yn.gov.cn-zwgk-v1@1.1.0
# exit 2: cli_mutually_exclusive
```

## 8. `source rule match` 与 `explain`

### 8.1 绑定语法

```bash
policybase source rule match --source SOURCE_ID --url URL \
  [--method METHOD] [--request-role ROLE] [--pack PACK_REF] \
  [--response-fixture PATH]

policybase source rule explain --source SOURCE_ID --url URL \
  [--method METHOD] [--request-role ROLE] [--pack PACK_REF] \
  [--response-fixture PATH] [--field JSON_POINTER]
```

共同参数：

| 参数 | 必填 | 约束/行为 |
|---|---|---|
| `--source` | 是 | 提供 Registry 合规上下文；必须在本地 Registry 可解析；disabled/paused/过期仍可离线解释，但必须标记 `runtime_eligible=false` 及原因 |
| `--url` | 是 | 只作为离线匹配输入；必须处于该来源 host/path/method 上限，否则输出拒绝原因 |
| `--method` | 否 | 默认 `GET`；POST 还要求 Registry 和 Recipe 存在公开读取模板，但本命令不发送 body |
| `--request-role` | 否 | 默认由 entrypoint/Recipe 推导；无法唯一推导时条件必填 |
| `--pack` | 否 | 精确 `PACK_REF`；省略时使用本地 active phase 冻结的精确 pack，输出其 ref/digest；没有冻结值则拒绝 |
| `--response-fixture` | 否 | 启用 post-fetch 匹配；必须是完整 fixture manifest 或其登记路径，不接受裸网页 |
| `--field` | explain 否 | RFC 6901 JSON Pointer，0..512 字符；只缩小 provenance trace，不改变匹配 |

无 `--response-fixture` 时只执行 pre-fetch，JSON 必须输出 `post_fetch.status=not_evaluated`，不能把未执行写成 unmatched。fixture 的 source/request URL 与参数不一致时返回 `fixture_context_mismatch`；不能用命令行值覆盖 fixture 事实。

`match` 输出候选、优先级、deny、歧义和 resolved digest；`explain` 额外输出 Registry→Profile→Recipe→Trait→Rule→restriction intersection 的字段来源追踪。匹配语言语义见 PolicyBase_12（草案）。二者均禁止 `--live/--fetch/--dry-run`，禁止任何网络客户端初始化。

```bash
# normal：只做 pre-fetch
policybase source rule match --source cn-yn-zcwjk \
  --url 'https://www.yn.gov.cn/zwgk/123.html' --request-role detail

# normal：本地 post-fetch
policybase source rule explain --source cn-yn-zcwjk \
  --url 'https://www.yn.gov.cn/zwgk/123.html' \
  --response-fixture tests/fixtures/rules/yn.gov.cn/detail/manifest.yaml \
  --field /parse/selectors/body

# edge：paused 来源可解释但不能运行
policybase --output json source rule explain --source cn-paused-zcwjk \
  --url 'https://example.gov.cn/xxgk/a.html'

# error：rule 命令不联网
# 禁止：policybase source rule test --rule yn.gov.cn-zwgk-v1@1.1.0 --live
# exit 2: cli_unknown_argument；hint: 使用 policybase scrape --canary ...
```

## 9. `source rule test`

### 9.1 绑定语法

```bash
policybase source rule test (--rule RULE_REF | --pack PACK_REF) \
  [--fixture PATH]
```

`--rule` 与 `--pack` 恰好一个。`--fixture` 可重复 1..100 次，只能缩小被目标 manifest 已登记的 fixture 集合；省略则运行全部正、负及适用的分页/API/附件/redirect fixture。未被目标登记的 fixture 返回 `fixture_not_registered`。

test 必须在禁网测试环境运行：网络 socket 创建也算失败。它验证 fixture digest、pre/post 匹配、selector cardinality、expected fields、deny、rewrite、确定性和歧义。目标为 Pack 时还验证 Engine compatibility 和 Pack 内容 digest。`source rule test` 不提供 `--live`；真实网络只经 `scrape --canary`。

禁止 `--source`、`--url`、`--live`、`--update`、`--dry-run`。测试失败退出 1；CLI/路径/环境错误退出 2（退出码语义见 PolicyBase_19）。

```bash
# normal
policybase source rule test --pack core-government-v1@1.0.0

# edge：只复现一个已登记 negative fixture
policybase source rule test --rule yn.gov.cn-zwgk-v1@1.1.0 \
  --fixture tests/fixtures/rules/yn.gov.cn/login/manifest.yaml

# error：裸 rule ID 不可复现
policybase source rule test --rule yn.gov.cn-zwgk-v1
# exit 2: cli_argument_format
```

## 10. `source rule pack build`

### 10.1 绑定语法

```bash
policybase source rule pack build --manifest PATH \
  [--target-dir PATH] [--dry-run]
```

参数：

| 参数 | 必填 | 约束/行为 |
|---|---|---|
| `--manifest` | 是 | `data/rules/` 下 pack manifest；普通文件，最大 2 MiB，schema 有效 |
| `--target-dir` | 否 | 必须是 `data/runtime/work/rule-packs/` 下已存在空目录；默认按 pack ref/digest 生成新目录 |
| `--dry-run` | 否 | 完成全部读取、验证和 digest 计划，但不创建目录/文件 |

build 只创建不可变 build artifact，包含精确 Rule/Trait/schema/digest、fixture test summary、Engine compatibility 和 changelog digest；它不修改 `data/rules/index.yaml`、不发布、不晋升 stable。manifest 有浮动引用、目标已存在但 digest 不同、fixture 未通过或包含 permission/evasion 字段时拒绝。Rule-Pack 视角的发布生命周期状态机见 PolicyBase_12（草案，引用 PolicyBase_10 跨组件状态机）。

```bash
# normal
policybase source rule pack build --manifest data/rules/packs/core-government-v1.yaml

# edge：完整计划但零写入
policybase --output json source rule pack build \
  --manifest data/rules/packs/core-government-v1.yaml --dry-run

# error：不能输出到正式规则目录
policybase source rule pack build --manifest data/rules/packs/core-government-v1.yaml \
  --target-dir data/rules/releases/core-government-v1
# exit 2: cli_path_unsafe
```

## 11. `source rule drift`

### 11.1 绑定语法

```bash
policybase source rule drift --run RUN_ID [--bucket BUCKET_ID]
```

`--run` 必填，读取 run 固定 snapshot、fixture baseline 和 metrics；不访问原 URL。`--bucket` 可选，1..160 ASCII 字节，只能选择 run manifest 已登记的 source/template bucket。不能用 CLI 提供新 threshold、Rule 或 Pack 覆盖历史 run。结构漂移分级见 PolicyBase_12（草案）。

输出分为 `no_drift|item_anomaly|suspected_drift|confirmed_drift|insufficient_evidence`，包含 baseline/actual digest、版本化阈值、影响 URL 数和证据路径。`confirmed_drift`、`insufficient_evidence` 或 schema 断言失败退出 1；`suspected_drift` 是成功分析且退出 0，但诊断 severity=warning。

```bash
# normal
policybase --output json source rule drift --run run-20260803-cn-yn-001

# edge：旧 run 缺少完整指标
policybase source rule drift --run run-legacy-20240101
# exit 1, status=insufficient_evidence；不得伪造 no_drift 或让门禁放行

# error
policybase source rule drift --run ../../secrets
# exit 2: cli_argument_format
```

## 12. `source rule rollback-plan`

### 12.1 绑定语法

```bash
policybase source rule rollback-plan --from PACK_REF --to PACK_REF --run RUN_ID \
  [--target-file PATH] [--dry-run]
```

`from` 必须等于 run snapshot 的 Pack；`to` 必须是兼容 Engine 的既有 stable/deprecated rollback target，且不得等于 `from`。命令计算受影响 source/run/candidate、未 ingest candidate 的 discard/review/reprocess 建议和已 ingest 文献的 ReprocessHandoff；不执行回滚、不改 candidate/edition/current。回滚 reprocess 语义见 PolicyBase_12（草案）。

`--target-file` 只能在 `data/runtime/work/rollback-plans/` 下创建新 `.json`，最大路径 4096 字节；未给时只输出。`--dry-run` 与 `--target-file` 同时使用时不写文件，仅展示目标和 digest；未给 target 时 `--dry-run` 为冗余并拒绝。

```bash
# normal：只读计划
policybase --output json source rule rollback-plan \
  --from core-government-v1@1.2.0 --to core-government-v1@1.1.0 \
  --run run-20260803-cn-yn-001

# edge：验证落盘计划但不写
policybase source rule rollback-plan \
  --from core-government-v1@1.2.0 --to core-government-v1@1.1.0 \
  --run run-20260803-cn-yn-001 \
  --target-file data/runtime/work/rollback-plans/yn.json --dry-run

# error
policybase source rule rollback-plan --from core-government-v1@1.2.0 \
  --to core-government-v1@1.2.0 --run run-20260803-cn-yn-001
# exit 2: cli_mutually_exclusive
```

## 13. `scrape`：普通、更新与 canary

### 13.1 绑定语法

```bash
policybase scrape --source SOURCE_ID
  [--entrypoint ROLE | --url URL] [--year YYYY | --from-date DATE --to-date DATE]
  [--keyword TEXT] [--doc DOC_ID] [--update | --canary]
  [--rule RULE_REF | --pack PACK_REF]
  [--max-pages N] [--max-urls N] [--max-candidates N]
  [--concurrency N] [--min-delay-seconds N]
  [--dry-run]

policybase scrape --source SOURCE_ID --resume RUN_ID [--dry-run]
```

上面换行只为阅读，均为一个顶层命令。

### 13.2 模式

| 模式 | 触发 | 目的 | 规则要求 |
|---|---|---|---|
| discovery | 无 `--update/--canary/--resume` | 按受控入口发现并获取 candidate | active phase 冻结的 stable Pack |
| targeted | `--url` 或 `--doc` | 在同一来源边界内定向观测 | stable Pack；仍受 entrypoint/path/action 限制 |
| update | `--update` | 与已有 observation/current 比较并产生 update signal | stable Pack；不直接建 edition |
| canary | `--canary` | 限量验证 experimental/canary Rule/Pack | `--rule` 或 `--pack` 恰好一个；不 ingest |
| resume | `--resume` | 以完全相同 snapshot/checkpoint 恢复旧 run | 不接受新配置或过滤器 |

### 13.3 参数合同

| 参数 | 必填/默认 | 约束与副作用 |
|---|---|---|
| `--source` | 始终必填 | 完整 Registry ID；必须 enabled、未 paused、review 未过期且 action 有效 |
| `--entrypoint` | 否 | `ENTRYPOINT_ROLE`；Registry/Recipe 已登记角色；与 `--url` 互斥；省略使用唯一默认入口，多默认入口则条件必填 |
| `--url` | 否 | 单个明确 URL；与 entrypoint 互斥；必须属于 source 和请求角色上限 |
| `--year` | 否 | 与任一日期参数互斥；Recipe 必须声明过滤能力 |
| `--from-date/--to-date` | 成对条件必填 | 不能只给一个；与 year 互斥 |
| `--keyword` | 否 | 来源过滤文本，不是 SQL/正则；Recipe 不支持时拒绝 |
| `--doc` | 否 | 已存在 `DOC_ID`；只限定与该 source 有 provenance 的对象；与 discovery-only 的 `--entrypoint listing` 禁止组合 |
| `--update` | 否 | 与 canary/resume 互斥；允许与日期/year/keyword/doc 组合 |
| `--canary` | 否 | 与 update/resume 互斥；要求 rule/pack 恰好一个；强制 canary 预算 |
| `--rule` | canary 条件必填 | 与 pack 互斥；只有 experimental/canary 状态；必须精确版本 |
| `--pack` | canary 条件必填 | 与 rule 互斥；只有显式 canary pack；普通模式禁止覆盖 frozen pack |
| `--resume` | 否 | source 必须等于 run source；只允许 dry-run/output；snapshot digest 必须完全相同 |
| 预算参数 | 否 | 仅收紧解析值；任一缺省取固定 snapshot 上限 |
| `--dry-run` | 否 | 完成 Registry/Rule/robots 缓存/config/budget 解析；不联网、不建 run/checkpoint |

`--doc` 不允许 CLI 从文献来源 URL 猜测抓取范围。该 doc 无当前 source provenance 时返回 `doc_source_mismatch`。`--url` 不接受重定向后的目标作为预授权；运行中跨 host/path redirect 仍 quarantine（语义见 PolicyBase_11）。

筛选组合进一步固定：

- `--doc` 与 `--keyword/--year/--from-date/--to-date/--entrypoint` 互斥；它可以与 `--url` 同用，但 URL 必须已经登记在该 doc 的该 source provenance 中；
- `--url` 与 `--keyword/--year/--from-date/--to-date` 互斥，避免对单一详情请求伪装列表过滤；
- year/date/keyword 要求 Recipe 将所选 entrypoint 标为 `listing` 或 `api` filter-capable；detail/attachment entrypoint 禁止这些过滤；
- `--update --doc` 更新单一文献；`--update --url` 更新单一 observation；不带筛选的 `--update` 扫描该来源已登记增量范围；
- 没有 `--update/--canary/--resume` 且给出 `--doc` 或 `--url` 时是 targeted mode，不因为默认 discovery 而追加其他入口。

canary 默认硬预算为 pages=10、urls=50、candidates=20、concurrency=1；用户可以在 canary 范围内进一步收紧。canary 输出写隔离 candidate namespace，标记 `eligible_for_ingest=false`。任何 access control、规则歧义、未知 host、硬漂移或预算异常立即 blocked，不能返回 partial 后继续。canary 晋升门见 PolicyBase_12（草案）。

普通运行允许 PolicyBase_11 定义的逐项 fail-soft，最终 `partial` 退出 3；合规/访问控制/越界/歧义导致的 run blocked 退出 1。`--dry-run` 不读取实时 robots；只使用具有时间戳的本地审查/缓存，缺失或过期时返回 `robots_preflight_unavailable`，不得为了计划而联网。

### 13.4 示例

```bash
# normal：增量更新
policybase scrape --source cn-hubei-zcwjk --update \
  --year 2024 --max-pages 20 --max-candidates 100 \
  --concurrency 1 --min-delay-seconds 3

# normal：显式 canary，是真实联网入口
policybase scrape --source cn-yn-zcwjk --canary \
  --rule yn.gov.cn-zwgk-v1@1.2.0 \
  --entrypoint detail --max-urls 20 --max-candidates 10

# edge：只做可复现计划，无网络、零写入
policybase --output json scrape --source cn-hubei-zcwjk --update \
  --doc REG-a1b2c3d4e5 --dry-run

# error：resume 不能换预算
policybase scrape --source cn-hubei-zcwjk \
  --resume run-20260803-cn-hb-001 --max-pages 5
# exit 2: cli_parameter_not_applicable；hint: 使用原 snapshot 恢复，或不带 --resume 开新 run

# error：普通运行不能临时覆盖 Pack
policybase scrape --source cn-hubei-zcwjk \
  --pack core-government-v1@1.1.0
# exit 2: cli_argument_dependency
```

## 14. `import`

### 14.1 绑定语法

```bash
policybase import INPUT [INPUT ...]
  [--recursive] [--metadata PATH] [--source SOURCE_ID]
  [--authorization AUTH_ID] [--max-files N] [--max-total-bytes N]
  [--dry-run]
```

### 14.2 参数合同

| 参数 | 必填/默认 | 约束与行为 |
|---|---|---|
| `INPUT` | 1..1000 个 | 明确普通文件，或恰好一个目录；文件格式由 PolicyBase_13 sniff，不信扩展名 |
| `--recursive` | 否 | 只有输入恰好一个目录时允许；目录未给此参数只读取直接普通文件，不进入子目录 |
| `--metadata` | 否 | 只有单个文件 INPUT 时允许；YAML/JSON，最大 1 MiB，schema 严格、未知字段拒绝 |
| `--source` | 否 | 仅记录 enabled、未暂停、审查有效的已注册 import/authorized source provenance；不能为网页来源伪造下载事实 |
| `--authorization` | 条件必填 | 完整 `AUTH_ID`（scope 路由见 PolicyBase_15）；metadata/来源声明 retain 或后续处理需要显式授权时必填；授权必须覆盖本次 import 对象和动作且未过期 |
| `--max-files` | 默认 1000 | 目录枚举和展开后的硬上限 |
| `--max-total-bytes` | 默认 10 GiB | 打开后复核实际总字节；超过即在写 candidate 前拒绝 |
| `--dry-run` | 否 | 枚举、sniff、hash、metadata/授权 preflight；不复制、不建 candidate |

目录遍历按 NFC 相对路径的 UTF-8 字节序确定排序；隐藏文件、临时文件、VCS 目录、symlink 默认拒绝并报告，不能静默跟随。YAML 使用无对象构造的 safe loader，禁止自定义 tag，并限制 alias、节点数和嵌套深度；JSON 同样限制深度和节点数。一个非法输入默认使整个 import preflight 失败且零写入。执行阶段每个 candidate 原子创建；意外 I/O 导致已有部分成功时退出 3，并输出逐项 digest/candidate ID 和安全 resume 清单。

import 不接受 URL，不联网，不自动 OCR/layout/refine，不自动 ingest/index。文件名、目录名、导入顺序、附件 hash 或 `--source` 不能铸造普通 doc_id、自动 merge 或证明 publication 权限。

```bash
# normal
policybase import scan.pdf --metadata metadata.yaml --dry-run
policybase import ./incoming --recursive --max-files 500 --max-total-bytes 5368709120

# edge：无 source 的用户提供文件仍可生成 candidate，但 provenance.kind=user_supplied
policybase import ./notice.ofd

# error：批量输入不能共享单文献 metadata
policybase import a.pdf b.pdf --metadata metadata.yaml
# exit 2: cli_argument_dependency

# error：import 不接受网络 URL
policybase import 'https://example.gov.cn/a.pdf'
# exit 2: cli_argument_format；hint: 注册来源后使用 policybase scrape
```

## 15. `prepare` 与 reviewed decision 绑定

### 15.1 绑定语法

```bash
policybase prepare INPUT [INPUT ...]
  [--source SOURCE_ID] [--decisions PATH] [--batch-size N]
  [--dry-run]
```

### 15.2 输入和筛选

`INPUT` 为 1..100 个完整 `CANDIDATE_ID`、`RUN_ID`、candidate manifest 或 run candidate directory，必须经对象 registry 解析到受控候选根。目录必须有受信 manifest；不递归扫描任意目录。相同 candidate 经 ID/digest 去重；同 ID 不同 digest 是 `candidate_immutability_violation`。

`--source` 是过滤器：只选择 provenance 中精确包含该 source 的 candidate。它不补写 provenance、不授予权限。过滤后为空返回成功 0、status=`no_items`；source 不存在或不可解析仍是错误。

`--batch-size` 默认 50。所有 candidate 先完成 schema、来源、合规、identity 和 decision preflight，才允许写 immutable decision/routing/hold 或 process-ready handoff。`prepare` 不要求内容已经 review/confirmed，不执行 `ingest` action（action enum 见 PolicyBase_04），不创建内容 artifact、edition/current/index；跨 doc hash collision 只产生要求 PolicyBase_08 identity migration 事务处理的受控 handoff。若执行中后项失败且前项已经成功，退出 3 并列出 routed/held/failed 和 resume 信息；不得把 routed 伪称为已建 edition。

### 15.3 `--decisions` 绑定（schema 引用 PolicyBase_08）

`--decisions` 是单个严格 schema YAML/JSON/JSONL 文件，最大 10 MiB。

业务字段集（`decision_id`/`candidate_id`/`candidate_digest`/`decision_domain`/`action`/`basis[]`/`evidence_refs[]`/`reviewer`/`decided_at`/`notes`/`target_doc_id`/`target_edition_id`）、`decision_domain ∈ {identity, update}`、各 domain 的 action 受控值分别见 PolicyBase_08 §9（identity）与 §6（update），`basis`/`evidence_refs` 的受控值集、identity/update 判定规则与 reviewer 权限模型 —— **schema 引用 PolicyBase_08 reviewed decision**；本卷只定义 CLI 绑定与本地校验顺序，不重定义上述业务字段集。

本卷 CLI 绑定约束（在 PolicyBase_08 schema 之上收紧的 CLI 解析与格式边界）：

- `decision_id`：`dec-` 加 16..64 个小写 hex；
- `candidate_digest`：64 个小写 SHA-256 hex；
- `basis`：1..32 个 PolicyBase_08 受控值且去重；
- `evidence_refs`：1..64 个受控 evidence ID/路径引用，每项 1..1024 字节且不能逃出审计根；
- `reviewer`：治理身份 ID、1..128 ASCII 字节；
- `decided_at`：带时区 RFC 3339 且不能晚于当前时间五分钟以上；
- `notes`：0..4000 个 Unicode 字符，不可承载正文或秘密；
- 未知字段、重复 `decision_id` 和未规范化重复项均拒绝。

CLI 校验条件（业务判定与受控值见 PolicyBase_08）：

- Tier 3/4、issuer unresolved/mismatch、别名无闭环、identity conflict 必须有 identity decision；
- 相同 URL 内容变化、正文/身份差异或 update signal 必须有 update decision；
- 一个 candidate 可各有一条 identity/update decision，但同 domain 只能一条；
- action=`merge|create_edition|mark_identity_alias` 时 `target_doc_id` 与 `target_edition_id` 条件必填，以绑定审核时的 current；首次无 current 的合法目标必须用显式 null 和相应 schema basis；
- `create_document|keep_separate` 禁止 `target_doc_id`，新 ID 由 PolicyBase_07 计算；
- `manual_review_hold` 禁止正式写入，但成功记录 hold；
- decision 的 candidate digest、reviewer 权限、时间、evidence 和 target current 必须仍有效；过期/冲突不得让 CLI 询问后临时确认。
- decisions 文件必须声明其 candidate/run scope；不在 INPUT 范围内的 decision 返回 `decision_scope_mismatch`，不能静默忽略或应用到同名其他 candidate。

CLI 不提供 `--merge`、`--force`、`--yes`、`--skip-dedup`、`--skip-compliance`、`--accept-ocr`、`--overwrite-current` 或同义开关。缺少必要 decision 时对应 candidate 进入 hold；单项调用退出 1，多项调用无正式写入时退出 1，有其他项成功则退出 3。

### 15.4 写入门和结果

每个可能进入后续确认链的 candidate 必须依次通过：

```text
candidate schema/source/compliance
-> PolicyBase_07 identity
-> PolicyBase_08 issuer/Tier + identity decision
-> observation/update decision
-> immutable process-ready identity/update handoff
-> PolicyBase_18 extract/OCR/layout/refine/review/confirm
-> PolicyBase_09 storage/compliance preflight + edition/current/registry publish
-> PolicyBase_14 active index 投影（仅 P4 起且 index 已存在，并在 registry publish 前匹配）
```

`no_change` 不建 handoff、不切 current；`create_document/create_edition` 在本命令中只是 reviewed routing action，分别固定 proposed doc、target current 和后续 edition kind，不执行内容确认或 edition 写入；`manual_review_hold` 只写受控审计/候选状态。dry-run 执行全部可本地判断的门，计算 proposed doc/edition kind/action，但不创建 routing/hold/artifact/lock/current/index，也不预留 ID。

```bash
# normal：预演一整个 run
policybase --output json prepare run-20260803-cn-hb-001 --dry-run

# normal：带受控 reviewed decisions
policybase prepare run-20260803-cn-hb-001 \
  --decisions data/runtime/work/decisions/run-20260803-cn-hb-001.yaml \
  --batch-size 50

# edge：筛选后无 candidate
policybase prepare run-20260803-import-001 --source cn-hubei-zcwjk
# exit 0, status=no_items, written_paths=[]

# error：不能在命令行强制合并
policybase prepare cand-0123456789abcdef01234567 --merge REG-a1b2c3d4e5
# exit 2: cli_unknown_argument；hint: 提供通过 schema 和 reviewer gate 的 --decisions 文件
```

## 16. 命令专属诊断与纠正提示

退出码、通用 `cli_*`/路径/配置/依赖诊断、文本格式、JSON envelope 和 hint/usage 规则唯一引用 PolicyBase_19，本卷不复制其枚举。PolicyBase_19 的 exit 0/1/2/3 直接适用；本卷成功状态包括 `no_items/no_change`；`insufficient_evidence` 是业务 finding，固定 exit 1。允许 partial 的命令只有 scrape/import/prepare 批量执行。

ID/URL/ref 词法错误统一为 PolicyBase_19 `cli_argument_format`；单文件/条件参数缺失统一为 `cli_argument_dependency`；互斥值统一为 `cli_mutually_exclusive`；参数不适用某 mode 统一为 `cli_parameter_not_applicable`。本卷不得为这些通用事实另造同义 code。

本卷专属配置/fixture 诊断（均映射 PolicyBase_19 exit 2；普通路径、配置、依赖和 I/O 诊断直接使用 PolicyBase_19）：

```text
output_path_out_of_scope
capability_not_active
fixture_not_registered
fixture_context_mismatch
robots_preflight_unavailable
filter_capability_unsupported
requested_limit_exceeds_policy
```

本卷业务/安全门诊断（单项映射 PolicyBase_19 exit 1，允许 partial 的批量命令可能汇总为 3）：

```text
source_not_found
source_disabled
source_paused
source_review_expired
source_scope_denied
robots_disallowed
access_control_blocked
rule_unmatched
rule_ambiguous
fixture_assertion_failed
pack_incompatible
structure_drift
candidate_schema_invalid
candidate_immutability_violation
candidate_not_production_eligible
doc_source_mismatch
missing_reviewed_decision
invalid_reviewed_decision
decision_stale
decision_scope_mismatch
issuer_gate_failed
update_identity_ambiguous
process_handoff_invalid
compliance_gate_failed
authorization_gate_failed
secret_material_detected
```

每个专属诊断必须填入 PolicyBase_19 envelope 的 `code/parameter/hint/usage`；可以增加 `rejected_value_summary` 与 `constraint`。hint 只能建议缩小范围、补充证据或使用正确命令，不能建议关闭门禁、扩大 host/path、绕过 robots/challenge 或强制 merge。

## 17. JSON envelope 的命令扩展

全局 `policybase --output json ...` 使用 PolicyBase_19 唯一 envelope。本卷命令在其中增加 `mode/dry_run/network_performed/run_id/resolved/items`；这些扩展必须由公共 schema 的 namespaced/受控扩展点登记，不得建立另一种顶层响应。通用 envelope 字段（`schema_version`/`command`/`status`/`exit_code`/`diagnostics`/`written_paths`/时间/排序/路径脱敏等）见 PolicyBase_19，本卷示例只示意扩展点：

```json
{
  "schema_version": "1.0",
  "command": "scrape",
  "mode": "update",
  "status": "success",
  "exit_code": 0,
  "dry_run": true,
  "network_performed": false,
  "run_id": null,
  "resolved": {"source_id": "cn-hubei-zcwjk", "pack_ref": "core-government-v1@1.0.0"},
  "items": [],
  "diagnostics": [],
  "written_paths": []
}
```

字段不可因 text/json 模式改变业务语义。失败、最小 envelope、stdout/stderr、时间、排序、路径脱敏均遵守 PolicyBase_19。`--dry-run` 额外必须断言 `network_performed=false` 且 `written_paths=[]`。

## 18. 参数组合测试矩阵

最低组合测试：

| 编号 | 命令/组合 | 期望 |
|---|---|---|
| S01 | `source show` + 完整已注册 ID | 0，只读 |
| S02 | 禁止输入 `source show hubei` | 2 `cli_argument_format` |
| R01 | validate `--all` | 0 或规则断言 1；零网络/零写入 |
| R02 | validate `--all --rule X` | 2 互斥 |
| R03 | match 无 fixture | 0，只有 pre-fetch，post=`not_evaluated` |
| R04 | match fixture context 与 URL 不同 | 2 `fixture_context_mismatch` |
| R05 | test rule + pack | 2 互斥 |
| R06 | test 加 `--live` | 2 unknown；网络 mock 断言零调用 |
| R07 | pack build `--dry-run` | 0，digest 稳定、零写入 |
| R08 | drift 用路径冒充 RUN_ID | 2 `cli_argument_format`，打开文件前拒绝 |
| R09 | rollback from=to | 2 `cli_mutually_exclusive` |
| A01 | scrape 普通模式 + `--rule` | 2 `cli_argument_dependency`，要求 canary |
| A02 | scrape canary 无 rule/pack | 2 条件必填 |
| A03 | scrape canary 同时 rule+pack | 2 互斥 |
| A04 | scrape update+canary | 2 互斥，零网络/零写入 |
| A05 | scrape resume + 新预算 | 2 `cli_parameter_not_applicable` |
| A06 | scrape 单边日期 | 2 `cli_argument_dependency` |
| A07 | scrape year+日期 | 2 互斥 |
| A08 | scrape 并发高于 Registry | 2，并给允许上限 |
| A09 | scrape dry-run | 0，socket/run/checkpoint 写调用均为零 |
| A10 | scrape redirect 到未知 host | 1 blocked，quarantine 有证据，不抓目标正文 |
| A11 | canary 命中 challenge | 1 blocked，停止来源桶，不切换 transport |
| A12 | scrape doc+year 或 url+keyword | 2 `cli_mutually_exclusive`，零网络 |
| I01 | import 单文件+metadata | 0 candidate；dry-run 时零写入 |
| I02 | import 多文件+metadata | 2 `cli_argument_dependency` |
| I03 | import URL | 2 `cli_argument_format`，零网络 |
| I04 | import symlink/device/FIFO | 2 `path_type_forbidden` |
| I05 | import 超 max files/bytes | 2，在 candidate 写入前拒绝 |
| G01 | prepare Tier 0-2 + identity/update 门通过 | 0，process-ready handoff；artifact/edition/current/index 均不变 |
| G02 | prepare Tier 3/4 无 decision | 1 hold，current 不变 |
| G03 | prepare stale decision digest | 1 `decision_stale` |
| G04 | prepare CLI `--merge/--force` | 2 unknown，零写入 |
| G05 | prepare 输入为 canary/non-production-eligible candidate | 1 `candidate_not_production_eligible`，无 handoff |
| G06 | prepare dry-run | 0，proposed action 可复核、零 lock/ID 预留/写入 |
| G07 | prepare 后续 process/review/confirm 尚未运行 | 0，handoff 明示 pending；current/index 均不变 |
| G08 | decisions scope 超出 INPUT | 1 `decision_scope_mismatch`，零正式写入 |
| X01 | 任一 ID 含路径/控制/RTL/超长 | 2，在对象 lookup 前拒绝 |
| X02 | 任一只读 rule 命令初始化 socket | 测试失败，视为 blocker |
| X03 | `--help` 缺依赖/无配置环境 | 0，零读取业务配置、零网络、零写入 |

每项至少有 normal、edge、error fixture；错误测试同时断言退出码、稳定 diagnostic、无越权副作用和 hint 示例可通过 parser。

## 19. 实施验收

正式迁移资产：

```text
docs/specs/cli-source-ingest.md
src/policybase/commands/source.py
src/policybase/commands/scrape.py
src/policybase/commands/ingest.py
src/policybase/commands/prepare.py
src/policybase/commands/types.py
data/schemas/cli-diagnostic.schema.json
tests/golden/source/
tests/golden/scrape/
tests/golden/import/
tests/golden/prepare/
```

最低验收：

```bash
pytest tests/commands/test_source.py
pytest tests/golden/source/ tests/golden/scrape/
pytest tests/golden/import/ tests/golden/prepare/
pytest tests/commands/test_boundaries.py
policybase source rule test --pack core-government-v1@1.0.0
```

验收必须证明：help golden 与本卷一致；所有 invalid 参数在联网/写入前拒绝；Rule 命令禁网；scrape/canary 是唯一联网入口；dry-run 零副作用；prepare 只产 process-ready handoff，不能确认内容或写 edition/current/index；reviewed decision 不可由快捷参数绕过。

## 20. 不得降级的不变量

1. source 始终使用完整、已注册 ID；不接受未登记简称。
2. Rule 工具永远离线；真实网络只经 scrape 普通/canary run。
3. 用户参数只能收紧 Registry/robots/配置预算，不能扩大 host/path/method/action。
4. scrape/import 只产生 candidate/observation，不直接 ingest、confirm 或 index。
5. canary candidate 永远不具备 ingest 资格。
6. import 文件可读不等于 retain、index、external transfer 或 redistribution 获权。
7. Tier 3/4、issuer 或 update 冲突不能由 CLI flag 自动裁决（业务判定见 PolicyBase_08）。
8. 未确认 OCR/layout/model、合规失败或授权缺失内容不能成为 current。
9. `ingest` action 及 update/correction/reprocess edition 只能经 PolicyBase_18 `process confirm` 执行；`prepare` 不创建或覆盖 edition。
10. 无效参数必须在网络、run 创建、candidate 写入、lock 和 current/index 变化之前拒绝。
11. `--dry-run` 必须同时满足零网络、零写入和零 ID/锁预留。
12. 诊断和提示帮助用户修正输入，但绝不建议绕过安全、合规、review 或历史保留门。
