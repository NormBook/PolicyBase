# PolicyBase CLI 顶层拓扑、命令域路由与跨命令标识

> 状态：主权威
> 分卷编号：PolicyBase_15
> 主题：cli-topology
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase

---

## 1. 定位与非职责边界

本卷是 **CLI 顶层命令面、命令域路由、跨命令标识投影、副作用分层原则、阶段演进** 的唯一 owner。顶层入口固定为 `policybase`。

业务语义（合规、身份、去重、存储、来源、Rule、内容、索引、导出）由 PolicyBase_04-14 维护；CLI 只决定如何**表达**这些语义并**早拒绝**非法输入，不另造分类、合规、存储、Rule 或索引语义。

非职责（一句引用，不展开）：

- 各子命令的逐项参数、组合、诊断码、退出码、示例 → 见 PolicyBase_16~19 对应卷。
- ID 的**生成语义与 canonical 形态** → 见 PolicyBase_07；本卷只定义 ID 在 CLI 上的 **token 词法投影**，不重新定义生成规则、长度收紧或碰撞算法。
- 通用全局参数、解析早拒绝顺序、通用诊断码（含 `cli_*`）、统一退出码、依赖安装 → 见 PolicyBase_19 §2/§3/§4/§5/§13。
- 早拒绝提示的稳定格式（`ERROR <stable_code>` + hint + usage）与解析序 → 见 PolicyBase_19 §3/§4，本卷不重述。
- 业务 schema（action enum、edition 文件、compliance gate、content 状态机等）→ 见 PolicyBase_04/08/09/13 对应章节。

**本卷不维护子命令完整参数表，也不维护绑定参数矩阵**（自检断言见 §11）。

### 1.1 命令域路由表

| 命令域 | 唯一参数权威子卷 |
|---|---|
| `list`、`show`、`export` | PolicyBase_16 |
| `source`（含 `source rule` 子树）、`scrape`、`import`、`prepare` | PolicyBase_17 |
| `process` | PolicyBase_18 |
| `index`、`verify`、全局参数、诊断、退出码、`help`、依赖 | PolicyBase_19 |

参数、组合、输出、禁止参数、稳定诊断码、退出码、示例、最小 usage 全部归入对应子卷。任何子卷不得在本卷之外重新定义顶层命令面或跨命令标识。

## 2. 顶层命令面

顶层恰好暴露 **10 个命令**，分两组。

普通用户第一屏（4 命令）：

```text
policybase list
policybase show
policybase scrape
policybase import
```

维护者与高级入口（6 命令）：

```text
policybase source
policybase prepare
policybase process
policybase index
policybase verify
policybase export
```

**不暴露**顶层 `search`、`stats`、`normalize`、`relations`、`attach`、`model`：

- 搜索属于 `list/show` 的过滤与投影（参数权威 PolicyBase_16）；
- 统计属于 `verify stats` 的只读聚合（参数权威 PolicyBase_19）；
- `normalize`、`relations` 属于内容/索引生产侧能力，不作为顶层动词；
- `attach` 不是顶层动词；附件作为 edition 内部文件角色处理（业务权威 PolicyBase_09/13）；
- `model` 不是顶层命令，只是 `process ocr`/`process refine` 在 `--engine model` 下的受控 backend（engine 枚举权威 PolicyBase_13，CLI 绑定权威 PolicyBase_18）。

未来命令必须先修改对应子卷与参数组合测试，再进入顶层 `help`。占位命令必须返回明确 unavailable（非 0 退出），不得静默退出 0。

## 3. 跨命令标识

本卷维护公共标识在 **CLI 上的 token 词法投影**——即子卷在解析位置参数与 option 时唯一接受的字符串形式。**ID 的生成语义、canonical 形态、长度收紧、碰撞算法、稳定性规则一律以 PolicyBase_07 §5（含 §5.1 ID 生成权威表）为权威**；本表只投影这些规则到 CLI 词法，不重新定义。

| 类型 | CLI 词法投影 | 生成语义与业务存在性权威 |
|---|---|---|
| `DOC_ID` | 已注册大写 TYPE 前缀 + `-` + 小写 hex；总长上限以 PolicyBase_07 碰撞集合规则为准 | PolicyBase_07 identity registry |
| `SOURCE_ID` | `cn-{org-or-region}[-{subregion}]-{function}` 小写 ASCII kebab-case，3..96 bytes；省名简称不接受为 `SOURCE_ID` | PolicyBase_10 Source Registry（仅已登记的完整历史 alias 可迁移解析） |
| `EDITION_ID` | `ed-` + 小写 hex，固定 27 ASCII bytes | PolicyBase_09 edition manifest |
| `CANDIDATE_ID` | `cand-` + 小写 hex，固定 29 ASCII bytes | PolicyBase_11 candidate manifest/registry |
| `ARTIFACT_ID` | `art-{stage}-` + 小写 hex；`stage` 为 1..32 位小写 kebab-case；形态与稳定性见 PolicyBase_13 §4 | PolicyBase_13 内容工件 schema |
| `RUN_ID` | `run-` + 小写 ASCII 字母、数字或 `-`，长度范围以 PolicyBase_11 为准 | PolicyBase_11 run manifest/registry |
| `AUTH_ID` | `auth-` + 小写 hex，固定 29 ASCII bytes | 见 §3.1 scope 路由 |
| `SWITCH_EVENT_ID` | `sw-` + 小写 hex，固定 27 ASCII bytes | PolicyBase_09 §4.5 switch event |
| `REVIEW_ID` | `rev-` + 小写 hex，固定 28 ASCII bytes | PolicyBase_13 §5 内容层 review decision |
| `FILE_ID` | `file-` + 小写 hex，固定 29 ASCII bytes（内容寻址） | PolicyBase_09 manifest `files[]` |
| `PROFILE_ID` | 小写 kebab-case slug（如 `local-government-v1`），1..96 bytes | PolicyBase_10 Profile 注册 |
| `BACKEND_ID` | 小写 kebab-case slug（如 `rapidocr`），1..64 bytes | PolicyBase_13 §10 backend capability |

CLI 不接受模糊前缀、显示名称、自由路径或自定义别名作为标识替代。任何兼容迁移形式必须先由对应业务 owner 登记为**完整 alias**；CLI 不做"宽松匹配"或前缀补全。

子卷（PolicyBase_16~19）定义位置参数与 option 时必须引用本表，不得重新声明长度或正则。同一概念不得同时存在位置参数与 option 两套可互换语法，除非对应子卷明确规定一个为兼容输入并标注退休版本与拆除里程碑。

公共形式跨命令统一：

- JSON 输出统一为全局 `--output json`；子卷不得另造 `--json`（路由到 PolicyBase_19 §2 全局参数）。
- 索引重建统一为 `policybase index --rebuild`（绑定权威 PolicyBase_19）。
- 内容 engine 统一为 `--engine local|model`（枚举权威 PolicyBase_13，CLI 绑定权威 PolicyBase_18）。
- 无副作用预演统一为 `--dry-run`（适用规则见 §6.1）。

### 3.1 AUTH_ID scope 路由

`AUTH_ID` 指向授权记录或当前对象 manifest，按 **action scope** 决定：

- `import` 动作 → 指向 PolicyBase_04 授权 registry 中的授权记录；
- 模型调用场景 → 必须来自当前 candidate manifest（业务存在性见 PolicyBase_11），不得由 CLI 参数自由指定任意 backend 凭证。

业务存在性、合规授权确认与 PII/密级判定归 PolicyBase_04/09/11；本卷只规定 `AUTH_ID` 在 CLI 上的词法与 scope 路由原则，不重述授权记录的业务字段。

## 4. 参数合同最低要求

PolicyBase_16~19 中每个命令和子命令必须逐项定义（具体由各子卷落实，本卷不复制）：

1. 位置、名称与是否可重复；
2. 类型、编码、最大长度、格式与数值范围；
3. 默认值及默认值是否产生副作用；
4. 必填、互斥、依赖与条件必填；
5. 禁止组合及最早拒绝阶段；
6. workspace/path/URL/SQL/shell 安全边界；
7. 成功、拒绝与部分成功的副作用；
8. 稳定诊断码、退出码、纠正 hint 与最小 usage；
9. normal、edge、type error、range error、安全拒绝与组合矩阵；
10. 可直接复制的合法示例与至少一个纠错示例。

没有进入某子卷参数矩阵的示例不是绑定命令。实现不得"宽松接受"该子卷未声明的别名或参数组合。

## 5. 早拒绝与提示原则

所有命令复用 PolicyBase_19 §3 的解析早拒绝顺序：类型、格式、范围、互斥、依赖、路径词法错误必须在加载数据库、网络、浏览器、OCR 或模型之前失败。稳定错误格式（`ERROR <stable_code>` + hint + usage）与通用 `cli_*` 诊断码见 PolicyBase_19 §4。

提示可以建议合法参数，但不得**猜测** source、doc、edition、授权 ID、review decision 或目标路径后自动执行。模型密钥、Project token、cookie 与浏览器 profile 不得由 CLI 参数直接接收（避免进入 shell history）；需要的授权只接受受控记录 ID（`AUTH_ID`，scope 见 §3.1）。

## 6. 副作用分层原则

命令成功只证明本命令合同完成，**不证明** candidate 已入库、edition 已索引、内容可发布或 Milestone 已 Accepted。本卷只定义**分层原则**；**每个具体命令归属哪一层、其副作用表与回滚语义归对应子卷**（PolicyBase_16~19）。

| 层级 | 原则 |
|---|---|
| read-only | 不产生任何写入；只读投影可随时重放 |
| run-only | 仅写运行/候选对象（run/candidate），不触及 confirmed edition、current、index |
| process-ready handoff | 产出经审查的 identity/update decision 路由与可进入 process 的交接，不进行内容确认、edition 创建、current 切换或索引写入 |
| confirmed edition | 创建不可变 edition（业务权威 PolicyBase_09），不切换 current、不写 index |
| current switch | 切换 current 投影（业务权威 PolicyBase_09），不直接写发布产物 |
| publication-gated export | 外部输出受发布门约束（合规/PII/授权见 PolicyBase_04），未过门不得产出外部文件 |

层级之间显式分离是 CLI 不变量：本卷定义"哪几层存在、各层语义边界"，子卷定义"哪些命令落在哪一层、其副作用与回滚"。例如 `process confirm` 同时触发 confirmed edition 与 current switch 两层，但其完整副作用表、CAS 参数与回滚语义归 PolicyBase_18。

### 6.1 `--dry-run` 适用规则路由

各命令的 `--dry-run` 适用性（哪些写命令支持、支持时验证到哪一层、返回什么）由对应子卷 PolicyBase_16~19 定义。本卷不列笼统清单；子卷必须明确标注每条 `--dry-run` 的早拒绝深度与是否触发只读校验。

## 7. 内容处理与网站规则命令边界

`process` 是 extract、OCR、layout、refine、correct、review、confirm、diff、reprocess、rollback 的**唯一 CLI 命名空间**（子命令绑定权威 PolicyBase_18）。不存在平行的顶层 `model` 或 `attach`。外部模型只能作为 `process` 子命令的 backend，必须保留 candidate、diff、授权与人工确认（外部模型 gate 业务规则见 PolicyBase_04，触发时机见 PolicyBase_13/18）。`show` 是只读命令，不提供 `--edit`。

`source rule` 子树（match/test/explain/validate/pack build/drift/rollback-plan）的参数权威归 PolicyBase_17，Rule/Trait 语义权威归 PolicyBase_12（草案）。该子树必须满足：`match` 同时提供完整 source 与 URL；`test` 使用离线 Rule/Pack + fixture；不提供 `--live`；真实网络只经注册来源的 scrape/canary；explain/validate/pack/drift/rollback-plan 不修改正式 Registry/Rule/current。PolicyBase_12 Rule-Pack 晋升前，相关命令只能标记为 unavailable/pending capability，不得返回伪成功。

## 8. 依赖与环境

依赖组、配置优先级、`help`/`version` 无副作用、CI/生产禁止动态安装等公共行为由 PolicyBase_19 §13 唯一定义。本地 OCR/layout 依赖必须可在无外部模型环境安装和验证（业务能力见 PolicyBase_13）。本卷不重述依赖清单与加载顺序。

## 9. 阶段演进

CLI 顶层拓扑随阶段逐步稳定，但 10 命令面自 P1 起固定（即使部分为 unavailable 占位）：

- **P1**：命令注册骨架、PolicyBase_19 minimal `verify` 与 `help` 结构；10 命令面占位（未实现命令返回 unavailable 非 0）。
- **P2**：`prepare`、identity/dedup 路由、不可变 storage/current schema 与恢复下限；正式 `ingest` action 由 `process confirm` 执行（业务权威 PolicyBase_04/09，绑定权威 PolicyBase_18）。
- **P3**：`source`/`scrape`、本地 extract/OCR/layout/review/confirm（绑定权威 PolicyBase_17/18）。
- **P4**：`list`/`show`/`index`/`export`（绑定权威 PolicyBase_16/19）。
- **P5**：全部 CLI 参数、组合、诊断与维护者工作台稳定。
- **P6/P7**：在不改变公共状态机的前提下增加 model backend 与高级附件能力。

阶段退出边界（CLI 视角）= 对应子卷参数矩阵达到该阶段要求的最小子集且占位命令语义正确。整体阶段定义与依赖图见 PolicyBase_02。

## 10. 总体验收

目标验收合同（以下命令均为目标合同，重构期未实现、不构成已执行证据）：

```text
command: pytest tests/commands/test_topology.py
expected exit code: 0
evidence: planned（待实现，重构期不执行）
assert: PolicyBase_15 contains no binding parameter matrix duplicated
        from PolicyBase_16..19

command: pytest tests/golden/help/
expected exit code: 0
evidence: planned（待实现，重构期不执行）
assert: top-level help exposes exactly the ten commands in §2,
        and exposes no top-level search/stats/normalize/relations/attach/model

command: pytest tests/commands/test_ownership.py
expected exit code: 0
evidence: planned（待实现，重构期不执行）
assert: every command and parameter has exactly one owner
        among PolicyBase_16..19; PolicyBase_15 only owns topology,
        routing, cross-command identifier projection, and side-effect
        layering principles
```

跨卷 CLI 审核还必须执行 CLI 一致性门。重构期上述脚本未实现，按 PolicyBase_02 阶段 C 执行模型处理（脚本"待实现，重构期不执行"）。

### 10.1 本卷不变量

1. 一个参数事实只有一个子卷权威（PolicyBase_16~19 之一）；本卷不持有任何绑定参数。
2. 无效参数在副作用前拒绝，并给稳定 code、hint、usage（格式与解析序见 PolicyBase_19）。
3. source 始终使用完整注册 `SOURCE_ID`；不接受省名简称或自由别名。
4. candidate、confirmed edition、current、index、export 五类副作用显式分层；本卷定义层，子卷定义命令归属。
5. CLI 不提供绕过合规、去重、确认、授权、安全或历史保留的开关。

## 11. v3 CLI 拆分迁移裁决（历史附录）

> 性质：迁移期记录（historical migration notes）。本节只记 v3 相对历史 CLI 的处置事实，不授权新行为；裁决生效以对应子卷绑定为准。

历史单卷 CLI 的能力在 v3 全部有明确 disposition，但命令名不承诺全部兼容。下列语义由 v3 显式收紧：

- **顶层 `ingest` 退役**：因名称与 PolicyBase_04 正式写入 action 冲突，预检/identity/update routing 改名 `prepare`（绑定权威 PolicyBase_17）；正式 `ingest` action 只由 `process confirm` 执行（绑定权威 PolicyBase_18）。旧 `ingest` 命令必须返回 unknown-command 并提示两步替代，不得作为 alias 静默接受。
- **`source list --filter` 退役**：以 PolicyBase_17 的 `--state/--type/--jurisdiction` 结构化过滤替代；未知 `--filter` 必须拒绝。
- **`scripts/verify.py` thin wrapper**：只能委托与 `policybase verify` 相同模块、schema、诊断与退出码；不得形成第二套参数面（绑定权威 PolicyBase_19）。
- **宽泛 `--limit` 收紧**：历史 `--limit 1..10000` 由各命令 owner 的逐命令范围替代（PolicyBase_16/19）。
- **`process confirm/correct/rollback` 完整语法**：历史省略 review/current CAS 参数的示例不是兼容语法；PolicyBase_18 的完整绑定语法（含 CAS 参数）是唯一有效形式。

固定依赖组及加载规则由 PolicyBase_19 §13 唯一维护。
