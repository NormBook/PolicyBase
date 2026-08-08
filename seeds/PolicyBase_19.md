# PolicyBase CLI：索引、验证与全局行为

> 状态：主权威
> 分卷编号：PolicyBase_19
> 主题：cli-index-verify
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase

---

## 1. 定位与非职责边界

本卷是 `policybase index`、`policybase verify`、以及**所有顶层命令共享的 CLI 全局行为**的唯一参数权威。具体包括：

- **唯一 owner（本卷展开）**：`index`/`verify` 命令绑定；全局语法与全局参数；解析与早拒绝顺序；通用诊断码（含 `cli_*` 码）；统一退出码；依赖与安装行为；index/verify 测试矩阵。
- **非职责（一句引用，不展开）**：
  - 顶层命令面、命令域路由表、ID CLI 词法投影、`--dry-run` 适用矩阵路由 → 见 PolicyBase_15 §cli-topology。
  - `list`/`show`/`export`、`source`/`scrape`/`import`/`prepare`、`process` 11 子命令的绑定参数 → 见 PolicyBase_16 / PolicyBase_17 / PolicyBase_18。
  - DOC_ID 的生成语义与 canonical 形态 → 见 PolicyBase_07 §identifiers.doc-id；DOC_ID 的 CLI 词法投影（接受/拒绝/转义规则）→ 见 PolicyBase_15 §cli-topology.id-lexing。
  - 各 verify target 验证对象的业务语义（layout/spec/integrity/id/dedup/sources/acquisition/content/index/boundary/expiry/stats）→ 见 §7 表中对应业务卷。
  - candidate/ingest/index 三合规门的 PII/未确认文本/未授权文件判定 → 见 PolicyBase_04 §7。
  - 索引产物 schema、FTS5 analyzer、`record_hash` 全字段 frame、reindex 迁移规则 → 见 PolicyBase_14 §indexing。
  - Edition 文件权威、`current.json`、文件角色 → 见 PolicyBase_09 §storage.authority。

CLI 只编排业务模块、不改业务结论。`--help`、`--version` 与参数错误**不得联网、安装依赖、写文件或打开数据库**。参数校验必须先于业务初始化；明显无效输入不得在加载模型、打开数据库或发起网络请求后才失败。

本卷守护的不变量：

- **全局参数、解析序、通用诊断码、退出码、依赖加载语义在全 CLI 唯一。** PolicyBase_15/16/17/18 引用本卷这些权威，不得重列或改名。
- **`index` 默认是 current 增量投影；唯一全量重建语法是 `policybase index --rebuild`（不是 `index rebuild` 子命令）。**
- **`verify` 默认只读；`clean-workspace` 默认只输出计划，实际清理需显式 `--apply --plan-hash`。**

---

## 2. 全局语法与全局参数（唯一 owner）

### 2.1 全局语法

```text
policybase [--config PATH] [--workspace PATH] [--output text|json]
           [--log-level error|warning|info|debug] [--no-color]
           COMMAND ...

policybase --help
policybase --version
policybase COMMAND [SUBCOMMAND ...] --help
```

除层级 help 外，全局参数必须位于 `COMMAND` 之前；子命令同名参数由其子卷定义，解析器不得静默接受错误位置的全局参数。`--help` 是唯一的位置例外：

- 顶层 help 使用 `policybase --help`；
- 命令/子命令 help 使用 `policybase COMMAND [SUBCOMMAND ...] --help`，且 `--help` 必须是最后一个 token。

help 只解析到目标命令层级，不校验其他必填业务参数；`--version` 只允许顶层。

### 2.2 全局参数表

| 参数 | 类型/边界 | 默认 | 组合规则 |
|---|---|---|---|
| `--config` | 存在的普通 UTF-8 YAML 文件；绝对化后必须在允许配置根内；最大 1 MiB | workspace 配置 | 与 `--help`/`--version` 同用时只做语法校验，不读取文件 |
| `--workspace` | 存在目录；拒绝 NUL、设备路径和非预期 symlink | 当前发现的项目根 | 不得是 `/`、用户 home 或包含另一个不相关仓库的上级目录 |
| `--output` | 枚举 `text\|json` | TTY 为 text，非 TTY 仍为 text，除非显式 json | JSON 模式禁用颜色和进度动画 |
| `--log-level` | 固定枚举 `error\|warning\|info\|debug` | `info` | 即使 `debug` 也不得输出 secret、cookie、正文或完整 PII |
| `--no-color` | flag | false | JSON 隐含 true |
| `--help` | flag | false | 与 `--version` 互斥；按 §2.1 两种位置绑定；出现时不要求业务依赖 |
| `--version` | flag | false | 与命令、`--help` 互斥 |

### 2.3 配置优先级

固定为：**CLI 显式参数 > 允许的环境变量 > workspace config > schema 默认值**。安全门、授权和受控枚举**不能被环境变量放宽**。未知配置键默认拒绝，不得静默忽略拼写错误。

---

## 3. 解析与早拒绝顺序（唯一 owner）

所有命令按以下顺序解析，前阶段失败时不得进入后阶段：

1. token 数量、UTF-8 合法性、NUL/控制字符和最大长度；
2. 全局命令/参数是否已知、位置是否正确；
3. 子命令语法、类型、枚举、范围；
4. 互斥、依赖、条件必填和禁止组合；
5. 路径词法安全和 workspace 边界；
6. 读取配置并校验 schema；
7. 解析对象 ID、文件存在性和 runtime precondition；
8. 初始化实际需要的依赖/数据库/网络/backend；
9. 执行业务并写结构化结果。

**步骤 1-5 失败时不得产生 run、lock、candidate、临时索引或日志正文。** 步骤 6-7 失败时不得加载可选依赖或发起网络请求。本顺序是 PolicyBase_15/16/17/18 共享的早拒绝合同，引用方不得重排或放宽。

---

## 4. 通用诊断码与纠正提示（唯一 owner）

### 4.1 三段式诊断格式

文本诊断固定三段式：

```text
ERROR <diagnostic_code>: <事实说明>
hint: <一条可执行纠正方式>
usage: <最小合法语法>
```

JSON 诊断至少包含：

```json
{
  "command": "index",
  "status": "rejected",
  "exit_code": 2,
  "diagnostics": [
    {
      "code": "cli_mutually_exclusive",
      "parameter": "--check",
      "conflicts_with": ["--rebuild"],
      "hint": "choose exactly one mode",
      "usage": "policybase index [--check|--rebuild|--dry-run]"
    }
  ],
  "written_paths": []
}
```

不得用 traceback、`KeyError`、argparse 默认英文堆栈或模糊的 "invalid input" 代替稳定诊断。业务卷（16/17/18）只能新增业务事实 code，不能为同一通用事实改名或复用通用 code 表达业务语义。

### 4.2 通用 stable code 词表

通用 `cli_*` 码的唯一词表如下；子卷只能增加业务 code，不能为同一通用事实改名：

| code | 通用事实 | exit |
|---|---|---:|
| `cli_required_argument` | 缺少必填位置/option | 2 |
| `cli_unknown_argument` | 未知命令、参数或非法全局参数位置 | 2 |
| `cli_argument_format` | 词法、编码、ID、日期或表达式格式错误 | 2 |
| `cli_argument_range` | 长度、数值、数量或复杂度越界 | 2 |
| `cli_mutually_exclusive` | 互斥/禁止组合 | 2 |
| `cli_argument_dependency` | 条件必填或依赖未满足 | 2 |
| `cli_parameter_not_applicable` | 参数不适用于该命令/target/mode | 2 |
| `cli_path_unsafe` | 路径逃逸、设备、非预期 symlink 或受保护目标 | 2 |
| `cli_config_invalid` | 配置缺失、未知键或 schema 无效 | 2 |
| `cli_dependency_unavailable` | 所需 dependency group 不可用 | 2 |
| `cli_environment_invalid` | 运行环境或 credential precondition 使命令无法运行 | 2 |
| `cli_io_failed` | 读取、写入、fsync 或 rename 环境故障 | 2 |

业务诊断码（如 `index_scope_with_rebuild`、`index_rebuild_required`）由本卷 §6 或对应业务卷定义，不进 `cli_*` 词表。

---

## 5. 统一退出码（唯一 owner）

| exit | 含义 |
|---:|---|
| 0 | 请求完整成功，或只读检查确认无 finding |
| 1 | 业务数据、合规、完整性或验证 finding 导致拒绝 |
| 2 | CLI 用法、配置、依赖、路径、I/O 或运行环境错误 |
| 3 | 命令合同明确允许的部分批次成功；必须带逐项结果和 resume 信息 |

固定规则：

- 参数语法/组合错误固定 exit 2（不走 exit 1）。
- `verify` 发现被验证对象违规固定 exit 1；验证器自身无法运行固定 exit 2。
- 不能用 exit 0 表示只完成部分步骤；部分成功必须用 exit 3 并附逐项结果。
- PolicyBase_15/16/17/18 引用本表，不得自定义退出码语义。

---

## 6. `index` 命令绑定

### 6.1 语法

```text
policybase index [--check | --rebuild | --dry-run]
                 [--doc DOC_ID | --changed-since RFC3339]
                 [--include-history]
                 [--history-profile PROFILE_ID]
                 [--analyzer-profile PROFILE_ID]
                 [--lock-timeout SECONDS]
```

默认模式是 **current 增量索引**。唯一全量重建语法是 `policybase index --rebuild`（**不是** `index rebuild` 子命令——`rebuild` 在此是 flag，不是子命令）。

### 6.2 参数边界

| 参数 | 类型/边界 | 默认 | 规则 |
|---|---|---|---|
| `--check` | flag | false | 纯只读一致性检查；与 `--rebuild`、`--dry-run` 互斥 |
| `--rebuild` | flag | false | staging 全量构建并原子切换；与 `--doc`、`--changed-since`、`--dry-run` 互斥 |
| `--dry-run` | flag | false | 生成 plan，不写索引/current；与 `--check`、`--rebuild` 互斥 |
| `--doc` | DOC_ID（生成语义见 PolicyBase_07 §identifiers.doc-id；CLI 词法投影见 PolicyBase_15 §cli-topology.id-lexing） | 无 | 与 `--changed-since`、`--rebuild` 互斥 |
| `--changed-since` | 带时区 RFC3339 | 无 | 与 `--doc`、`--rebuild` 互斥；未来时间拒绝 |
| `--include-history` | flag | false | 只允许与 `--rebuild` + `--history-profile` 同用；不能混入 current FTS 表 |
| `--history-profile` | 已注册 history profile ID，1..128 ASCII | 无 | 与 `--include-history` 互为条件必填；仅允许 `--rebuild`，历史写入隔离结构 |
| `--analyzer-profile` | 已注册 profile ID，1..128 ASCII | current configured | profile/schema 不兼容时普通增量拒绝并提示 `--rebuild` |
| `--lock-timeout` | decimal 0..300 秒 | 30 | 0 表示不等待；负数、浮点溢出、超范围拒绝 |

### 6.3 禁止组合与诊断

| 输入 | 诊断码 | hint |
|---|---|---|
| `index rebuild`（误用为子命令） | `cli_unknown_argument` | `use: policybase index --rebuild` |
| `--check --rebuild` | `cli_mutually_exclusive` | `choose one of --check or --rebuild` |
| `--rebuild --doc DOC_ID` | `index_scope_with_rebuild` | `remove --doc or run incremental index --doc` |
| `--include-history` 缺 rebuild/profile | `cli_argument_dependency` | `use --rebuild --include-history --history-profile PROFILE_ID` |
| `--history-profile` 单独出现 | `cli_argument_dependency` | `add --rebuild --include-history or remove --history-profile` |
| analyzer profile 不兼容 | `index_rebuild_required` | `run policybase index --rebuild --analyzer-profile ...` |
| current 指针无效 | `current_pointer_invalid` | `run policybase verify integrity --doc ...; do not rebuild over invalid storage` |

### 6.4 副作用合同

- 默认增量只投影 confirmed current edition；历史必须进入隔离的历史结构，不污染 current FTS。
- `--check` 与 `--dry-run` 的 `written_paths` 必须为空数组。
- `--rebuild` 使用 staging 数据库，通过 schema/analyzer/count/hash 检查后**原子切换**；失败保留旧索引，不留下半成品。
- PII、未确认 artifact、无索引授权和失效 current 不得因 `--rebuild` 被纳入（合规门规则见 PolicyBase_04 §7；索引 schema 见 PolicyBase_14 §indexing）。

### 6.5 使用样例

```bash
policybase index
policybase index --doc REG-a1b2c3d4e5
policybase index --changed-since 2026-08-01T00:00:00+08:00 --dry-run
policybase --output json index --check
policybase index --rebuild --analyzer-profile zh-policy-v2
policybase index --rebuild --include-history --history-profile confirmed-history-v1
```

---

## 7. `verify` 命令绑定与 targets

### 7.1 语法

```text
policybase verify TARGET [TARGET_OPTIONS] [--fail-on warning|error]
                       [--max-findings N]
```

### 7.2 target 表

`TARGET` 固定为下列只读验证对象。本卷只定义 target 作为 verify 入口的参数合同；每个 target 验证对象的**业务语义**引用对应业务卷：

| target | 只读验证对象（业务语义引用） |
|---|---|
| `layout` | 仓库目录、忽略边界、受控路径 → 见 PolicyBase_13 §content.layout |
| `integrity` | 文献包、edition/current/switch/manifest → 见 PolicyBase_09 §storage.authority |
| `id` | 归一化、机关解析、canonical key、Tier、doc ID 与历史 ID → 见 PolicyBase_07 §identifiers |
| `dedup` | identity、update、reviewed decision 和 merge evidence → 见 PolicyBase_08 §dedup |
| `sources` | Source Registry、Profile/Recipe 引用、host alias 和来源状态 → 见 PolicyBase_10 §source-registry |
| `acquisition` | run/config snapshot/candidate/checkpoint/drift/handoff → 见 PolicyBase_11 §acquisition |
| `content` | artifact/geometry/diff/review/confirmation → 见 PolicyBase_13 §content |
| `index` | current/history/analyzer/SQLite/JSONL → 见 PolicyBase_14 §indexing |
| `boundary` | normal/edge/error/deny fixture（合规 deny 边界见 PolicyBase_04 §compliance） |
| `expiry` | 凭据、授权、来源和规则到期风险 → 见 PolicyBase_06 §metadata.validity |
| `stats` | 只读覆盖/质量统计；**不代表 Acceptance**（投影自 PolicyBase_14 §indexing） |
| `clean-workspace` | 临时区清理计划；默认只读，实际清理需显式参数（见 §10） |

未知 target 必须列出最接近的合法值，**不得自动选择**（`cli_unknown_argument`）。

---

## 8. `verify` 公共参数

| 参数 | 类型/边界 | 默认 | 规则 |
|---|---|---|---|
| `--fail-on` | 枚举 `warning\|error` | `error` | 只改变 warning 是否导致 exit 1，**不能降级 error/blocker** |
| `--max-findings` | integer 1..100000 | 1000 | 达上限必须标记 `truncated`，不能声称全量通过 |
| `--doc` | DOC_ID | 无 | 只对 `integrity`/`id`/`dedup`/`content`/`index` 有效 |
| `--run` | RUN_ID | 无 | 只对 `acquisition`/`content`/`clean-workspace` 有效；`clean-workspace` 语义见 §10 |
| `--fixture-root` | workspace 内普通目录 | target 默认 | 只对 `boundary`/`sources`/`acquisition`/`content` 有效 |

不适用于目标的参数必须拒绝 `cli_parameter_not_applicable`，**不得静默忽略**。

---

## 9. Target 专用参数

`id` 与 `sources` 的目标专用语法为：

```text
policybase verify id [--doc DOC_ID]
policybase verify sources [--registry PATH] [--source SOURCE_ID]
```

| 参数 | 适用 target | 规则 |
|---|---|---|
| `--registry` | `sources` | workspace 内普通 UTF-8 YAML 文件、最大 10 MiB；拒绝目录逃逸和非预期 symlink；默认使用配置中的唯一 registry |
| `--source` | `sources` | 只验证完整注册 SOURCE_ID，**不接受省名简称**（身份语义见 PolicyBase_10 §source-registry） |
| `--doc`（在 `id` 下） | `id` | 只读验证该文献的 canonical key/Tier/历史 ID；**不提供自动修复**（ID 语义见 PolicyBase_07 §identifiers） |

把这些参数用于其他 target 必须返回 `cli_parameter_not_applicable`。

---

## 10. `clean-workspace` 特殊边界

```text
policybase verify clean-workspace [--apply --plan-hash SHA256]
                                  [--older-than HOURS | --run RUN_ID]
                                  [--trash-dir PATH]
```

**默认只输出计划及 `plan_hash`，不移动/删除任何文件。** `--apply --plan-hash` 同时出现才允许按完全相同的计划移动临时文件到 workspace 内受控 trash；**不直接永久删除**。

`plan_hash` 覆盖：workspace identity、精确候选路径+inode/hash、scope、trash_dir、生成/到期时间和 tool revision。计划默认 15 分钟到期，任一候选或 scope 变化即失效。

| 参数 | 规则 |
|---|---|
| `--apply` | 才允许执行移动；必须与 `--plan-hash` 同时出现，**禁止单独出现** |
| `--plan-hash` | `sha256:` + 64 位小写 hex；`--apply` 时必填，不 apply 时禁止；必须匹配同一 workspace/scope/trash 的未过期只读 plan |
| `--older-than` | integer 1..8760 小时；与 `--run` 互斥 |
| `--run` | 精确 RUN_ID；只清理该 run 的临时产物 |
| `--trash-dir` | UTF-8 path 1..4096 bytes；默认配置的 runtime trash；父目录必须存在且为普通目录，不跟随 symlink；目标必须在 runtime trash 根内；禁止 `/`、home、workspace root、`data/documents` |

**永不移动或删除**：正式文献包、edition、current/switch、schema、golden、registry、Rule、manifest 和 Git 文件。

---

## 11. `verify` 使用样例

```bash
policybase verify integrity --doc REG-a1b2c3d4e5
policybase verify id --doc REG-a1b2c3d4e5
policybase verify sources --source cn-hubei-zcwjk
policybase verify acquisition --run run-20260803-001
policybase verify boundary --fixture-root tests/golden/boundary
policybase verify clean-workspace --older-than 168
policybase verify clean-workspace --apply \
  --plan-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --older-than 168
```

错误示例：

```text
input:  policybase verify index --run run-1
exit:   2
code:   cli_parameter_not_applicable
hint:   --run is valid for acquisition/content; use --doc for index
```

---

## 12. 测试矩阵

`index` 与 `verify` 的参数组合测试至少覆盖以下维度（golden 同时保存 text 和 JSON 诊断；错误用例必须断言稳定 code、exit、hint 和 `written_paths=[]`，不能只断言 "失败"）：

| 类别 | index | verify |
|---|---|---|
| normal | 默认增量、单 doc、`--check`、`--rebuild` | 每个 target 最小合法调用 |
| edge | `--lock-timeout` 0/300、当前时刻 `--changed-since`、最大长度 ID/profile | `--max-findings` 1/100000、warning/error 阈值 |
| type error | 浮点溢出 timeout、坏 RFC3339 | 非整数 finding、未知 target |
| mutual exclusion | `--check`+`--rebuild`、`--doc`+`--changed-since`、`--rebuild`+`--doc` | `--older-than`+`--run`、`--help`+`--version` |
| dependency | history 缺 profile、analyzer 需 rebuild | target 不支持 doc/run/fixture/remote、`--apply` 缺 `--plan-hash` |
| path security | staging/trash 逃逸、symlink/device | fixture/trash 逃逸、workspace root |
| side effect | `--check`/`--dry-run` 零写入、失败保留旧索引 | 默认 clean 零写入、`--apply` 只移 trash |
| diagnostic | 每个拒绝有 code/hint/usage 三段式 | 每个拒绝有 code/hint/usage 三段式 |

测试还必须断言在 §3 解析序的早拒绝阶段（步骤 1-5）**没有数据库、网络、模型、依赖安装或正式路径写入**。

---

## 13. 依赖与安装行为（唯一 owner）

命令只加载实际需要的 dependency group，不在启动时全量加载。固定组及用途为：

| group | 用途 |
|---|---|
| `core` | CLI、HTTP、HTML、YAML/frontmatter/schema |
| `normalize` | OpenCC、jieba、受控归一化 |
| `scrape` | Playwright 浏览器能力 |
| `attachment` | PyMuPDF、OOXML、OFD、RapidOCR/ONNX、基础 layout |
| `export` | CSV、Markdown/site 发布器 |
| `dev` | pytest、ruff、mypy、pip-tools |

固定规则：

- 缺依赖时输出固定 group、缺失包、允许的安装命令和当前模式，并使用 `cli_dependency_unavailable`（exit 2）。
- **CI、生产、批处理不得联网安装**；只有交互式开发模式且用户明确同意才允许提示安装命令。
- `--help`、`--version`、参数拒绝**不加载可选依赖**。
- 项目依赖只安装到项目 `.venv`。锁文件必须带 hash。
- 浏览器和模型 backend 另走明确安装/授权流程，**不由 `index`、`verify` 或 help 隐式下载**（外部模型 gate 业务规则见 PolicyBase_04 §8；OCR engine 枚举见 PolicyBase_13）。

本卷是全 CLI 依赖加载语义的唯一 owner；PolicyBase_15/16/17/18 引用本节，不得重列 group 表或自定义加载时机。

---

## 14. 与其他分卷接口

| 引用方/被引方 | 接口 |
|---|---|
| PolicyBase_15 cli-topology | 引本卷 §2 全局参数、§3 解析序、§4 通用诊断码、§5 退出码、§13 依赖加载；本卷不展开命令域路由 |
| PolicyBase_16 cli-query-export / PolicyBase_17 cli-source-ingest / PolicyBase_18 cli-process | 引本卷 §2-§5 与 §13 作为全 CLI 共享合同；业务诊断码各自定义，不复用 `cli_*` 码表达业务语义 |
| PolicyBase_07 identifiers | DOC_ID 生成语义、canonical 形态、Tier、历史 ID（本卷 §6.2 `--doc`、§9 `id` target 引用） |
| PolicyBase_09 storage | edition/current/switch/manifest 文件权威（本卷 §6.4 副作用、§7 `integrity` target 引用） |
| PolicyBase_14 indexing | 索引 schema、FTS5 analyzer、`record_hash`、reindex 迁移（本卷 §6 `index` 命令、§7 `index` target 引用） |
| PolicyBase_04 compliance | 合规门、外部模型 gate、deny 边界（本卷 §6.4 副作用、§7 `boundary` target 引用） |
| PolicyBase_10/11/13/06 | sources/acquisition/content/expiry 业务语义（本卷 §7 target 引用） |
