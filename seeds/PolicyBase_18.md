# PolicyBase CLI：内容生产 `process` 子命令

> 状态：主权威
> 分卷编号：PolicyBase_18
> 主题：cli-process
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与非职责

本卷是 `policybase process` 子命令、子命令参数绑定、参数组合、process 专用诊断和 CLI 验收的唯一权威。命令域路由、顶层命令面、ID CLI 词法投影、`--dry-run` 适用规则路由见 PolicyBase_15 §命令域路由；内容生产状态机（raw→…→edition_created 的节点语义）见 PolicyBase_13 §内容生产状态机；engine 业务枚举 `{local,model}` 见 PolicyBase_13 §10；外部模型 gate 业务规则见 PolicyBase_04 §8；review decision 内容层枚举见 PolicyBase_13 §5；`confirm --kind` 取值域（`edition_kind`）见 PolicyBase_06 §4；全局参数、解析早拒绝序、通用诊断码（含 `cli_*`）和统一退出码见 PolicyBase_19；ID 生成语义见 PolicyBase_07。其他分卷的 process 命令示例若与本卷冲突，以本卷为准并必须在内容门禁中修正。

本卷不授权采集、外传、发布或覆盖历史文件，不定义 OCR/layout/refine 算法（归 PolicyBase_13），也不允许 CLI 参数放宽 PolicyBase_04 合规硬门。任何成功命令只证明该次命令合同成功，不自动证明内容正确、可确认、可索引或可发布。

## 2. 命令面与闭环

绑定命令面（11 个子命令）：

```text
policybase process inspect
policybase process extract
policybase process ocr
policybase process layout
policybase process refine
policybase process correct
policybase process review
policybase process confirm
policybase process diff
policybase process reprocess
policybase process rollback
```

命令序列图（**各阶段语义见 PolicyBase_13 §内容生产状态机**；本卷只画 CLI 命令序列，不重画状态机节点名）：

```text
candidate/file
  -> inspect
  -> extract
  -> ocr             # 条件阶段
  -> layout
  -> refine          # 可选 local/model
  -> review
  -> confirm
  -> immutable edition + atomic current switch

current edition -> correct   -> review -> confirm(kind=correction|redaction)
edition         -> reprocess -> review -> confirm(kind=reprocess)
current         -> rollback  -> 已存在的 confirmed edition 成为 current
```

`diff` 是任意两个兼容 artifact/edition 之间的只读证据命令。没有 `process edit`、`process publish`、`process index`、`process model` 或 `--auto-confirm`。

## 3. 统一副作用模型

| 命令 | 正式数据副作用 | 成功产物 |
|---|---|---|
| `inspect` | 无 | stdout/JSON 能力报告 |
| `extract` | 无 | immutable extracted artifact |
| `ocr` | 无 | immutable OCR candidate |
| `layout` | 无 | immutable geometry + Markdown candidate + diff |
| `refine` | 无 | immutable refined candidate + diff |
| `correct` | 无 | 从固定 edition 派生的 correction candidate + diff |
| `review`（无 decision） | 无 | 只读审阅报告 |
| `review`（有 decision） | 无 | immutable review decision；partial 时另建 candidate + diff |
| `confirm` | 有 | immutable edition、switch event、原子 current 切换 |
| `diff` | 无 | stdout/JSON diff |
| `reprocess` | 无 | reprocess candidate 链和变更报告 |
| `rollback` | 有 | switch event、原子 current 切换和索引重投影 |

artifact、review、edition 和 switch event 一旦成功落盘不得原地修改。失败不得留下可被发现为成功对象的目录、空 Markdown、半写 manifest 或变更后的 current。候选工作区被 `.gitignore` 排除，不等于可以保存未授权或被 PolicyBase_04 拒绝的内容。

`confirm` 是整个公开 CLI 执行 PolicyBase_04 `ingest` action、创建 edition/current 并调用 PolicyBase_09 consumption-state publish coordinator 的唯一入口；`rollback` 只对已有 edition 写 switch 并同样发布新 registry generation。PolicyBase_17 `prepare` 只能产生 process-ready identity/update handoff。二者必须使用 compare-and-switch；前置 current 与命令声明不一致时拒绝，不得悄悄改用最新 current。

## 4. 词法、类型与通用参数

### 4.1 标识符

CLI 在读取文件或查数据库前完成语法校验。本卷使用的 ID 类型（`DOC_ID`/`EDITION_ID`/`CANDIDATE_ID`/`ARTIFACT_ID`/`REVIEW_ID`/`AUTH_ID`/`FILE_ID`/`PROFILE_ID`/`BACKEND_ID`）的 CLI 词法投影见 PolicyBase_15 §ID CLI 词法投影（生成语义见 PolicyBase_07）。本卷不再重列词法表。

拒绝大写 hex、前后空白、路径分隔符、`.`/`..`、控制字符、双向文本控制符和 Unicode 近似替换。不存在对象属于对象解析错误，不得降级为路径输入。

### 4.2 路径

输入路径使用 UTF-8，相对当前工作目录解析；参数字符串最长 4096 bytes。拒绝 NUL、设备文件、FIFO/socket、意外 symlink、解析后逃出允许输入根的路径，以及通过 `/proc`、`/sys`、`/dev` 读取。目录只在命令明确允许时接受。

`--prompt-file`、`--reason-file`、`--select-file` 必须是普通文件，不跟随 symlink，读取前后验证 inode/size/hash 未变化：

| 文件 | 格式 | 大小上限 |
|---|---|---:|
| prompt | UTF-8 YAML | 256 KiB |
| reason | UTF-8 YAML/JSON | 64 KiB |
| selection | UTF-8 YAML/JSON | 1 MiB |

这些文件禁止 NUL 和无效 UTF-8。prompt 必须通过版本化 schema；reason 必须含 1..2000 Unicode scalar 的 `reason`。命令行不接受裸 prompt 或内联正文。

### 4.3 页与文件范围

`--pages PAGE_SPEC` 语法为逗号分隔的正整数或闭区间，例如 `1,3-5,9`：

- 页码范围 `1..100000`；
- 展开后最多 10000 页；
- 必须严格递增；重叠、重复、倒序、空段、开放区间和空格均拒绝；
- 对无页概念的输入拒绝，而不是忽略；
- 超过实际页数在 preflight 拒绝。

`--file-id FILE_ID` 可重复 1..256 次，顺序保留但值不得重复。它只从 manifest 已登记文件中选择输入；与裸文件路径输入互斥。未指定时只允许对象 manifest 能唯一确定默认主输入，否则以 `input_ambiguous` 拒绝。

### 4.4 全局参数接口

全局参数（`--output text|json`、workspace/config/log/color、诊断外层、stdout/stderr 分离、全局参数位置）见 PolicyBase_19 §2。需要 JSON 时使用 PolicyBase_19 绑定形式，例如：

```bash
policybase --output json process inspect art-raw-web-0123456789abcdef01234567
```

process JSON 的 `items[]` 额外包含 artifact/review/edition/switch 的 ID、stage、hash 和副作用；不适用值为 null。正文、prompt、PII、授权 payload 和密钥不得进入诊断。

`--dry-run` 只绑定 `confirm/reprocess/rollback`。其他命令产生的都是可丢弃 immutable candidate，使用 `--dry-run` 属无效用法；不得假装支持后忽略。`--dry-run` 适用规则的路由见 PolicyBase_15。

## 5. Engine、backend、prompt 与授权

`--engine` 的 CLI 绑定：取值为 `local|model`（**业务枚举唯一权威见 PolicyBase_13 §10**），省略时该命令按其合同决定默认值（见各子命令 §6-§10）。CLI 在 `--engine model` 参数解析后、backend 启动前调用 PolicyBase_04 §8 的外部模型 gate 业务规则（**model gate 触发点本卷只声明这一处**）。

`--backend BACKEND_ID` 只选择安装且登记在 capability registry 中、与当前 stage/engine/input media type 兼容的 backend；它不是可执行文件、包名、URL 或 shell 命令。省略时必须由锁定 pipeline/profile 唯一解析，无法唯一解析则 `backend_unresolved`。实际 backend、版本、配置 hash 和代码 revision 写 operation。

组合规则：

| 条件 | `--backend` | `--prompt-file` | `--authorization` |
|---|---|---|---|
| `--engine local` | 可选 | 禁止 | 禁止 |
| `--engine model` | 可选 | 显式提供，或由锁定 profile 唯一解析 | 必填 |
| 命令无 `--engine` | 禁止 | 禁止 | 禁止 |

`--authorization AUTH_ID` 的 scope 路由见 PolicyBase_15；`AUTH_ID` 必须来自当前 candidate manifest，API key 或旧 edition 中类似授权不能替代。命令行显式 prompt 与 profile prompt 同时存在但 hash 不同，拒绝为 `prompt_conflict`。prompt 或授权缺失不得回退 local，也不得把 model 失败解释为 local 成功。

## 6. `inspect`

```text
policybase process inspect INPUT [--file-id FILE_ID]... [--pages PAGE_SPEC]
```

`INPUT` 恰好一个，为 `ARTIFACT_ID`、`CANDIDATE_ID` 或普通文件路径。标识符使用 PolicyBase_15 公共词法；匹配后只按对象 registry 解析，不再尝试同名文件。目录禁止。

`inspect` 只读取 magic/header、容器结构和已登记 metadata，输出格式、页数、文本层、图像覆盖、加密/损坏状态、可用 stage/backend 和建议下一命令。不得执行宏、脚本、外链、模型、网络或安装依赖；不得创建 artifact。

有效示例：

```bash
policybase process inspect ./incoming/scan.pdf --pages 1-3
policybase --output json process inspect art-raw-web-0123456789abcdef01234567
```

拒绝示例：

```bash
policybase process inspect ./incoming               # directory_not_allowed
policybase process inspect scan.pdf --file-id file-main # input_selector_conflict
```

## 7. `extract`

```text
policybase process extract INPUT [--file-id FILE_ID]... [--pages PAGE_SPEC]
                           [--profile PROFILE_ID]
```

支持 candidate/artifact 或普通 HTML/PDF/OFD/OOXML 文件；图片必须走 `ocr`。`--profile` 选择已登记 extraction profile，不接受任意配置路径。`--pages` 只适用于分页格式。成功生成新的 extracted artifact、tool/config/hash 和 diagnostics；即使输入 hash 与已有 artifact 相同，也只能验证并返回同 ID，不得覆盖。

边界：

- 加密 PDF、损坏容器、空提取和未知格式非零退出；
- OFD fallback 的 partial 输出必须 `needs_review`；
- 网页 raw 未获 retain 授权时不得借 extract 持久化 raw；
- `--profile` 词法见 §4.1，profile 不支持当前格式时早拒绝。

```bash
policybase process extract art-raw-web-0123456789abcdef01234567 --profile gov-html-v1
policybase process extract ./incoming/text.pdf --pages 1-20
```

## 8. `ocr`

```text
policybase process ocr INPUT [--file-id FILE_ID]... [--pages PAGE_SPEC]
                       [--engine local|model] [--backend BACKEND_ID]
                       [--profile PROFILE_ID] [--prompt-file PATH]
                       [--authorization AUTH_ID]
```

`--engine` 默认 `local`。INPUT 支持图片、扫描 PDF、页图 artifact 或具有可渲染页的 candidate；HTML/纯文本/可信文本 artifact 默认拒绝为 `ocr_not_applicable`。显式 OCR 复核已有文本层时，profile 必须声明 `allow_text_layer_review=true`，结果仍只是 candidate。

model OCR 的授权 task scope 必须覆盖 `ocr`，vision 输入必须逐 file/page/hash 覆盖。没有 `--engine both`；对比 local/model 必须运行两次并使用 `diff`。

成功不等于可确认。空输出、低置信度、关键数字/日期/文号分歧、页缺失、表格或阅读顺序不确定均进入 `needs_review`，而不是自动采用 model 结果。

```bash
policybase process ocr ./incoming/scan.pdf --pages 1-8 --engine local --backend rapidocr-v1
policybase process ocr art-pages-scan-0123456789abcdef01234567 --engine model \
  --backend vision-layout-v2 --prompt-file ./prompts/ocr-v1.yaml \
  --authorization auth-0123456789abcdef01234567
```

以下均在调用 backend 前拒绝：

```bash
# 禁止：policybase process ocr scan.pdf --engine local --authorization auth-0123456789abcdef01234567
# 禁止：policybase process ocr scan.pdf --engine model --prompt-file p.yaml
# 禁止：policybase process ocr scan.pdf --engine both
```

## 9. `layout`

```text
policybase process layout ARTIFACT_ID [--pages PAGE_SPEC]
                          [--profile PROFILE_ID] [--backend BACKEND_ID]
```

输入必须为 extracted/OCR artifact，不能是裸路径、edition 或 model 输出。layout 是确定性本地阶段，因此没有 `--engine`；`--backend` 必须属于 local layout capability。成功生成 geometry、Markdown candidate 和相对直接父 artifact 的 diff。

`--pages` 只能在输入 geometry/page manifest 完整时使用。选择部分页面产生 `scope=partial` candidate，后续 `confirm` 默认拒绝；只有 correction/reprocess manifest 明确证明未选页面由已确认父 edition 原样继承且 provenance 完整时才能确认。

```bash
policybase process layout art-ocr-scan-0123456789abcdef01234567 --profile basic-layout-v1
```

多栏、跨页表格、脚注、印章或阅读顺序不确定必须输出 warning/needs_review，不能用静默猜测换取成功。

## 10. `refine`

```text
policybase process refine ARTIFACT_ID [--pages PAGE_SPEC]
                          [--engine local|model] [--backend BACKEND_ID]
                          [--profile PROFILE_ID] [--prompt-file PATH]
                          [--authorization AUTH_ID]
```

输入必须为 layout/refined/correction candidate；默认 `--engine local`。local 只执行 profile 锁定的确定性 Markdown 清洗，不允许 prompt 或授权。model 只产生新 candidate 和 diff，不能直接修改文号、机关、日期或补写缺失条文；这些变化必须标为 critical change 并要求人工逐项接受。

`--pages` 选择只适用于保留 page/block provenance 的 artifact。model 授权 scope 必须覆盖 `text`，包含页面图时还必须覆盖 `vision`；授权只覆盖 text 时 CLI 必须剔除图片输入并在调用前证明实际 payload 不含图片。

```bash
policybase process refine art-layout-gov-0123456789abcdef01234567 --engine local
policybase process refine art-layout-gov-0123456789abcdef01234567 --engine model \
  --backend text-refine-v1 --prompt-file ./prompts/refine-v3.yaml \
  --authorization auth-0123456789abcdef01234567
```

## 11. `correct`

```text
policybase process correct DOC_ID --from-edition EDITION_ID
                          --reason-file PATH [--kind correction|redaction]
                          [--pages PAGE_SPEC]
```

`--from-edition` 和 `--reason-file` 均必填。reason 文件 schema 至少包含：

```yaml
schema_version: "1"
reason: 修正文号中的 OCR 错字
changes:
  - change_id: c001
    block_id: p1-b003
    expected_text_hash: "sha256:..."
    replacement: 国发〔2024〕1号
```

`changes` 为 1..10000 项；`change_id` 唯一；内联 `replacement` 单项最大 32 KiB。更大替换使用已登记在同一 candidate manifest 的 `replacement_file_id` 与 sha256，二者互斥；CLI 不接受任意替换文件路径。每项必须有 expected hash，防止把纠错应用到不同 base。禁止指定命令、URL、prompt 或 current 切换指令。

`--kind` 默认 `correction`。`redaction` 只允许删除或以版本化占位符替换已由 PolicyBase_04 finding/evidence 精确定位的 block/span；reason schema 条件必填 `redaction_finding_refs[]`（1..100，去重）和每项预期 hash，禁止新增正文或借遮蔽改变法律含义。两种 kind 都只产生 candidate+diff，必须 review 后以相同 kind confirm；kind 不一致固定拒绝 `confirmation_mismatch`。

base edition 必须属于 DOC_ID 且 integrity/confirmation 通过。它不必是 current，以便从历史版本派生，但命令输出明确标记 `base_is_current`；后续 confirm 必须再次 compare-and-switch。correct 只生成 correction candidate 和 diff，不创建 edition、不切 current。

```bash
policybase process correct REG-a1b2c3d4e5 \
  --from-edition ed-0123456789abcdef01234567 --reason-file ./review/correction.yaml
```

## 12. `review`

只读审阅：

```text
policybase process review ARTIFACT_ID
```

记录决策：

```text
policybase process review ARTIFACT_ID --decision DECISION --if-hash SHA256
                         [--select-file PATH] [--reason-file PATH]
```

`DECISION` 的取值域见 PolicyBase_13 §5（内容层唯一权威）。

本卷只定义 CLI 绑定矩阵，不重列枚举语义。

组合矩阵：

| decision | `--select-file` | `--reason-file` | 结果 |
|---|---|---|---|
| 无 | 禁止 | 禁止 | 只读报告 |
| `accept_all` | 禁止 | 可选 | confirmation-ready immutable review decision |
| `accept_selected` | 必填 | 必填 | 新 partial-accepted candidate + diff + review decision |
| `reject` | 禁止 | 必填 | rejected review decision |
| `hold` | 禁止 | 必填 | hold review decision |

有 decision 时 `--if-hash` 必填，格式为 `sha256:` 加 64 个小写 hex，且必须等于 artifact content hash。reviewer 从受信本地身份配置取得并写入 decision；CLI 不接受可伪造的 `--reviewer`。

selection 文件必须列出 1..10000 个唯一 `change_id` 或 block decision，只能引用输入 artifact 的 diff；未知、重复、互相冲突或遗漏依赖的 change ID 拒绝。partial accept 不是原地修改输入，而是从父 artifact 构造新 candidate；该命令整体成功退出 0，不使用 PolicyBase_19 的部分批次成功语义。

```bash
policybase process review art-model-gov-0123456789abcdef01234567
policybase process review art-model-gov-0123456789abcdef01234567 \
  --decision accept_selected --if-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --select-file ./review/selected.yaml --reason-file ./review/reason.yaml
```

同一 artifact 允许有多个 immutable decision，但 confirm 必须显式选择一个；互相冲突的最新决策不会被 CLI 自行猜测。

## 13. `confirm`

```text
policybase process confirm ARTIFACT_ID --doc DOC_ID --review REVIEW_ID
                          --kind KIND --if-current CURRENT
                          [--parent-edition EDITION_ID] [--dry-run]
```

`KIND`：

```text
initial | source_update | correction | reprocess | redaction
```

上述取值与 PolicyBase_06 §4 `edition_kind`（5 值）同名同语义对齐；新增 edition_kind 须同步本参数取值域。

`CURRENT` 为字面量 `none` 或 `EDITION_ID`。组合规则：

| kind | `--if-current` | `--parent-edition` |
|---|---|---|
| `initial` | 必须为 `none` | 禁止 |
| 其他 | 必须为 edition ID | 必填，且等于 `--if-current` |

不支持从非 current 历史版直接覆盖 current。若确需从历史版恢复，使用 `rollback`；若要以历史版为处理 base，先产生 candidate，但 confirm 时必须以 current 为 parent 并完整记录 source/base provenance，避免切断 edition 链。

confirm preflight 必须验证：

1. artifact、review 和 DOC_ID 一致，review 为 `accept_all` 或 partial accept 产生的新 artifact 的接受决策；
2. selected Markdown 非空，hash 与 review/diff 一致；
3. PolicyBase_04 合规三门、local storage access 和必要授权有效；local indexing access 不作为确认门，而由 PolicyBase_14 决定 indexed/metadata_only/excluded 投影；
4. critical change 均有显式人工接受；
5. parent/current、identity、manifest、provenance 和 edition payload 可确定；
6. edition 目录、switch event、current 指针具备原子/恢复条件；P4 active index 已存在时还须具备索引重投影恢复条件。

`--dry-run` 运行全部只读 preflight、计算计划 edition ID、switch 和 registry generation plan，但不得创建 edition/event、改变 current/registry 或索引。非 dry-run 把 selected immutable review decision 物化为 PolicyBase_09 `content_confirm` operation，计算 edition payload/ID，再调用 PolicyBase_09 publish coordinator；P4 active index 存在时在 registry CAS 前完成匹配投影，不存在时记录 `index_not_yet_applicable`。失败时旧 registry/current 保持或恢复。

```bash
policybase process confirm art-layout-gov-0123456789abcdef01234567 \
  --doc REG-a1b2c3d4e5 --review rev-0123456789abcdef01234567 \
  --kind initial --if-current none --dry-run
```

## 14. `diff`

```text
policybase process diff LEFT RIGHT [--format summary|unified|json]
                       [--pages PAGE_SPEC]
```

LEFT/RIGHT 各为一个 `ARTIFACT_ID` 或 `EDITION_ID`。两者不能相同；必须具有可比较 Markdown，且属于同一 DOC_ID，或具有明确共同 provenance。`--format` 默认 `summary`。`--format json` 与 PolicyBase_19 全局 `--output json` 的区别是前者选择 diff payload 详细度，后者选择外层诊断封装；全局 text 输出配合 `--format json` 时 stdout 仍为单个合法 JSON，不混入说明文字。

`--pages` 要求两侧都有 page/block provenance；缺失时拒绝，不退化为全局文本 diff。diff 只读，不把结果自动登记到 manifest。

```bash
policybase process diff ed-0123456789abcdef01234567 ed-89abcdef0123456701234567 --format unified
policybase process diff art-ocr-scan-0123456789abcdef01234567 \
  art-model-scan-89abcdef0123456701234567 --pages 1-5 --format json
```

## 15. `reprocess`

```text
policybase process reprocess DOC_ID --from-edition EDITION_ID
                            --pipeline PROFILE_ID [--steps STEP_LIST]
                            [--file-id FILE_ID]... [--pages PAGE_SPEC]
                            [--max-change-percent PERCENT] [--dry-run]
```

`STEP_LIST` 是逗号分隔且无空格的 `extract,ocr,layout,refine` 子序列，不能重复、倒序或为空；默认使用锁定 pipeline 的完整本地序列。reprocess 命令只允许 pipeline 解析为 local backend。包含 model stage 的 profile 以 `batch_model_forbidden` 拒绝；需要模型时，对单个 reprocess artifact 显式运行 `ocr/refine --engine model` 并独立授权、审阅。

`--max-change-percent` 为十进制定点数 `0..100`，最多两位小数，默认 `20.00`。定义为变更 block 数除可比较 block 总数乘 100；超过阈值时停止后续 stage，保留 needs_review candidate 并退出 1，不创建 current。阈值不是内容正确性或自动确认许可。

base 必须属于 DOC_ID 并保有执行所选 steps 所需的原始/上游工件和权限。`--file-id/--pages` 的局部 reprocess 必须能够从 base edition 无损继承未选范围并保存 provenance，否则拒绝。即使成功也只产生 candidate 链，仍须 review + confirm(kind=reprocess)。

`--dry-run` 只解析对象、范围、pipeline、backend、依赖、权限和预计 stage，不读取全文调用处理 backend，不创建 candidate。

```bash
policybase process reprocess REG-a1b2c3d4e5 \
  --from-edition ed-0123456789abcdef01234567 --pipeline local-layout-v2 \
  --steps extract,layout,refine --max-change-percent 15 --dry-run
```

本命令一次只处理一个 DOC_ID，因此没有部分批次成功退出码、`--continue-on-error` 或隐式批量 glob。批量编排由上层受控任务逐文献调用，每个文献独立原子。

## 16. `rollback`

```text
policybase process rollback DOC_ID --to-edition EDITION_ID
                           --if-current EDITION_ID --reason-file PATH
                           [--dry-run]
```

三个命名参数均必填。目标必须属于 DOC_ID、不是 current、是已确认且 integrity 完整的历史 edition。执行时重新验证当前有效合规、local storage access 和撤下约束；旧时曾可用不代表现在可重新选择。rollback 不创建内容 edition、不复制或改写目标，只创建 immutable rollback switch event 并原子切换 current；P4 active index 存在时同步重投影，不存在时记录 `index_not_yet_applicable`。local indexing 不获准时由 PolicyBase_14 投影为 `metadata_only/excluded`，不能反向伪装成全文 indexed。

`--if-current` 必须等于执行瞬间 current；不一致以 stale 拒绝。reason 文件只记录理由和证据引用，不能包含 `force/skip_gate/delete/rewrite` 等动作字段。`--dry-run` 输出 switch/index/recovery plan，不写任何正式状态。

```bash
policybase process rollback REG-a1b2c3d4e5 \
  --to-edition ed-0123456789abcdef01234567 \
  --if-current ed-89abcdef0123456701234567 \
  --reason-file ./review/rollback.yaml --dry-run
```

目标因现行 PII/sensitivity/publication policy 被拒绝时，不得通过 `--force`、关闭索引或只切 pointer 绕过。需要产生安全修订时走 correct/redaction edition。

## 17. 参数组合总矩阵

`R` 必填，`O` 可选，`C` 条件必填，`F` 禁止：

| 命令 | input | file-id | pages | engine | backend | profile/pipeline | prompt | auth | reason | select | review | parent | if-current | dry-run |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| inspect | R | O | O | F | F | F | F | F | F | F | F | F | F | F |
| extract | R | O | O | F | F | O | F | F | F | F | F | F | F | F |
| ocr | R | O | O | O | O | O | C | C | F | F | F | F | F | F |
| layout | R | F | O | F | O | O | F | F | F | F | F | F | F | F |
| refine | R | F | O | O | O | O | C | C | F | F | F | F | F | F |
| correct | R | F | O | F | F | F | F | F | R | F | F | F | F | F |
| review view | R | F | F | F | F | F | F | F | F | F | F | F | F | F |
| review decide | R | F | F | F | F | F | F | F | C | C | F | F | F | F |
| confirm | R | F | F | F | F | F | F | F | F | F | R | C | R | O |
| diff | R+R | F | O | F | F | F | F | F | F | F | F | F | F | F |
| reprocess | R | O | O | F | F | R | F | F | F | F | F | F | F | O |
| rollback | R | F | F | F | F | F | F | F | R | F | F | F | R | O |

`ocr/refine` 的 prompt/auth 只在 engine=model 时为 C，否则为 F；prompt 可由锁定 profile 唯一解析。`review decide` 的 reason/select 细分见 §12。未知参数、重复 singleton 参数、互斥组合和缺失条件参数按照 PolicyBase_19 解析顺序，在正文读取、backend 启动或写入前拒绝，并显示稳定 code、最短正确用法及一个安全示例。

`correct --kind` 为可选枚举、默认 `correction`；`redaction` 条件依赖 PolicyBase_04 finding refs。`confirm --kind` 必须与 artifact kind 相同。pairwise/条件测试必须覆盖 correction 默认、显式 redaction、缺 finding refs 和 kind mismatch。

## 18. Process 专用诊断码

退出码、`ERROR/code/hint/usage` 文本和 JSON 外层格式唯一引用 PolicyBase_19，不在本卷另建枚举。**通用 CLI/词法/未知参数/互斥/配置/路径/依赖/I-O/运行环境 code（含 `cli_dependency_unavailable`、`cli_mutually_exclusive`、`cli_unknown_argument` 等）见 PolicyBase_19 §4**。本卷只列 process 事实的最低稳定 code；相同事实返回相同 code，人类文案可改进但不改变机器语义。

### 18.1 Process 参数与对象事实

```text
input_selector_conflict
input_ambiguous
page_spec_invalid
page_out_of_range
profile_unresolved
backend_unresolved
backend_incompatible
prompt_unresolved
prompt_conflict
input_format_unsupported
directory_not_allowed
```

这些 code 映射 PolicyBase_19 的 CLI/config/object/environment 类退出语义。

### 18.2 Process 内容与业务门事实

```text
extract_empty
pdf_encrypted
input_corrupt
ocr_not_applicable
ocr_no_output
ocr_low_confidence
layout_ambiguous
partial_scope_unresolved
critical_change_unreviewed
review_selection_invalid
review_conflict
confirmation_missing
confirmation_mismatch
model_gate_denied
authorization_invalid
authorization_scope_mismatch
model_output_invalid
compliance_denied
current_stale
edition_not_confirmed
rollback_target_invalid
change_threshold_exceeded
batch_model_forbidden
```

这些 code 映射 PolicyBase_19 的业务/合规/完整性拒绝语义。一个主诊断可附多个 details。安全拒绝不回显正文、PII、token、prompt 内容或授权 payload。本卷命令均为单对象合同，不使用 PolicyBase_19 的部分批次成功语义；partial accept 是一次完整成功的 review operation。

## 19. 正常、边界、错误与安全拒绝示例

正常链：

```bash
policybase process extract ./incoming/doc.pdf --pages 1-12
policybase process ocr art-extract-pdf-0123456789abcdef01234567 --engine local
policybase process layout art-ocr-pdf-0123456789abcdef01234567
policybase process refine art-layout-pdf-0123456789abcdef01234567 --engine local
policybase process review art-refine-pdf-0123456789abcdef01234567 \
  --decision accept_all --if-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
policybase process confirm art-refine-pdf-0123456789abcdef01234567 \
  --doc REG-a1b2c3d4e5 --review rev-0123456789abcdef01234567 \
  --kind initial --if-current none
```

边界但有效：

```bash
policybase process ocr scan.pdf --pages 100000 --engine local
policybase process review art-model-pdf-0123456789abcdef01234567 \
  --decision hold --if-hash sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --reason-file ./review/hold.yaml
policybase process reprocess REG-a1b2c3d4e5 \
  --from-edition ed-0123456789abcdef01234567 --pipeline local-v2 \
  --max-change-percent 0.00 --dry-run
```

用法错误，均 exit 2 且不读正文：

```bash
# 禁止：policybase process ocr scan.pdf --engine both
# 禁止：policybase process ocr scan.pdf --engine local --prompt-file p.yaml
# 禁止：policybase process refine ART --engine model --authorization AUTH
# 禁止：policybase process review art-layout-pdf-0123456789abcdef01234567 --decision accept_selected
# 禁止：policybase process confirm art-layout-pdf-0123456789abcdef01234567 --kind initial --if-current none
# 禁止：policybase process rollback REG-a1b2c3d4e5 --to-edition ed-0123456789abcdef01234567
# 禁止：policybase process extract scan.pdf --pages 1-3,3-5
```

安全/业务拒绝，均 exit 1 且 current 不变：

```text
model authorization 已撤销                 -> authorization_invalid
授权只含 text，实际 payload 包含页面图       -> authorization_scope_mismatch
review 未接受关键文号变化                    -> critical_change_unreviewed
confirm 声明的 current 已被另一会话切换       -> current_stale
rollback 目标当前被 PII gate 撤下            -> compliance_denied
reprocess 结构变化 35%，阈值为 20%           -> change_threshold_exceeded
```

错误提示必须采用：事实 + code + 最短修正 + 安全示例。例如：

```text
ERROR cli_mutually_exclusive: --authorization is forbidden with --engine local.
hint: remove --authorization or choose --engine model with all model gates.
usage: policybase process ocr INPUT --engine local [--backend BACKEND_ID]
example: policybase process ocr scan.pdf --engine local
```

（`cli_mutually_exclusive` 本身属通用码，定义见 PolicyBase_19 §4。）

## 20. 参数组合与副作用测试矩阵

最低 golden：

| 类别 | 必测断言 |
|---|---|
| help | 11 个子命令存在；help/version 无网络、写入和安装 |
| lexical | 每种 ID 正反边界、超长、控制字符、路径字符、大写 hex |
| page | 1、100000、10001 页展开、重复、交叠、倒序、越实际页数 |
| file selection | manifest 唯一默认、歧义、重复 file-id、裸路径冲突 |
| engine | local 默认；model；both/具体 provider 作为 engine 被拒绝 |
| backend | 未登记、stage 不兼容、media 不兼容、唯一 profile 解析 |
| prompt/auth | model 缺失/过期/撤销/scope/hash/provider 不符；local 携带时拒绝 |
| extract | HTML、文本 PDF、OFD partial、图片拒绝、空输出、损坏/加密 |
| OCR | 扫描 PDF、PNG、可信文本拒绝、空结果、低置信、页缺失 |
| layout | geometry、阅读顺序、简单表格、多栏/跨页歧义、局部 provenance |
| refine | local 确定性；model candidate/diff；关键字段变化必须 review |
| correct | base/doc 不符、expected hash stale、历史 base、无 reason/changes |
| review | view 零写入；四 decision；partial selection 依赖/冲突；actor 可信 |
| confirm | 五 kind；initial/noninitial 参数矩阵；stale current；dry-run 零写入 |
| diff | artifact/artifact、edition/edition、同对象、无共同 provenance、页证据缺失 |
| reprocess | steps 顺序/重复、局部范围、阈值边界、model profile 拒绝、dry-run |
| rollback | same-current、跨 doc、未确认/损坏/现行 gate 拒绝、索引失败恢复 |
| atomicity | 每个故障注入点只见旧 current 或完整新 current；无半 edition |
| logs | stdout schema、stderr 分离、PII/prompt/key/正文不泄露 |

组合测试必须使用 pairwise 覆盖所有可选参数，并对 §17 每个 F/C 格至少有一个 negative/conditional test。安全 gate 使用离线 fixture 和假 backend，不接真实网络、外部模型或真实密钥。

建议验收入口：

```bash
pytest tests/commands/test_process.py
pytest tests/golden/process/
pytest tests/golden/content_pipeline/
policybase verify boundary --fixture-root tests/golden/content_pipeline/
```

在命令尚未实现的阶段，上述命令必须明确标记 `planned`，不能以跳过或空测试伪装成功。

## 21. 不变量

1. `process` 所有正文变换只产 immutable candidate；只有 confirm 创建 edition，rollback 只选择已有 edition。
2. current 切换必须 compare-and-switch、可恢复并留下 immutable event。
3. `local|model` 是唯一公开 engine（业务枚举见 PolicyBase_13 §10）；backend 只能从 capability registry 选择，不能执行用户字符串。
4. model 调用需要本次对象和任务的有效授权、版本化 prompt 与本地合规门（业务规则见 PolicyBase_04 §8，触发点见 §5）。
5. review partial accept 产生新 candidate，不修改模型/OCR/layout 输出。
6. 无效参数在读取正文、启动 backend、联网或写入前拒绝，并给出正确用法和安全示例。
7. candidate、未确认文本、diff、prompt、日志和未授权内容不得进入 current、索引或发布。
8. reprocess/correct 不覆盖历史；rollback 不复制、删除或修改 edition。
