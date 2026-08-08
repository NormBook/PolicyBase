# PolicyBase 内容生产、版面、OCR 与模型精修

> 状态：主权威
> 分卷编号：PolicyBase_13
> 主题：content
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase


---

## 1. 定位与权威边界

本卷是从获授权原始材料到确认 Markdown 的**内容生产状态机**、统一内容工件 schema、坐标工件、内容层 review decision、格式识别安全、HTML/图片、PDF、OFD/WPS、OCR 引擎合同、Layout/Markdown、模型精修合同（backend capability 接口）、外部模型 gate 触发时机（业务规则归本卷、gate 业务规则归 04）、密钥日志、Reprocess/回滚（内容域）与错误边界的**唯一 owner**。

非本卷职责（一句引用）：

- **外部模型 gate 业务规则**（前提清单、密钥隔离、失败语义）见 PolicyBase_04 §8；本卷只写内容生产在哪个 stage 触发该 gate。
- **engine 的 CLI 绑定**（`--engine` 字面、参数解析、诊断码归属）见 PolicyBase_18；本卷只定义业务枚举 `{local, model}`。
- **edition manifest、operations 枚举、文件角色、atomic 切换、reprocess edition_kind** 见 PolicyBase_09。
- **索引投影（`indexed` 状态、record_hash、analyzer）** 见 PolicyBase_14。
- **内容生产 ARTIFACT_ID 的生成语义**（canonical 形态、稳定性）见本卷 §4；CLI 词法投影见 PolicyBase_15。
- **身份层 reviewed decision** 见 PolicyBase_08 §9（判断两份 candidate 是否同一文献）；本卷 §5 是**内容层** review decision，二者不得混用。
- **本地预检**（敏感性 sensitivity 硬拦截、PII 限制、`classification_level` 公开性层级）见 PolicyBase_04 §4 / §6；本卷从预检通过的输入独立产出可追溯 candidate，不把预检文本直接晋升为正式 candidate。

处理成功不等于确认，确认不等于允许索引；允许本地索引不等于允许发布。外部模型永远是可选增强，不是入库或 CI 必需依赖。PolicyBase_01 §3 跨卷不变量在本卷的落地：外部模型不参与公开性/密级/PII 终审、原件和历史 edition 不被派生输出覆盖、内容生产确定性可复现。

## 2. 阶段边界

### 2.1 P3 最小可用能力

首来源闭环必须能在无外部模型时处理：

- HTML 主正文到 Markdown；
- PDF 文本层提取；
- JPEG/PNG 与扫描 PDF 的本地 OCR；
- 基础页/块坐标、阅读顺序与标题/段落/列表/简单表格 layout；
- 人工 diff、确认与 immutable edition；
- confirmed Markdown 满足 PolicyBase_14 的可消费前置条件（P4 active index 存在后才投影）。

因此本地 OCR 与最小 layout 属 P3 首来源闭环，不等到附件高级阶段。

### 2.2 后期增强

P6/P7 可增加外部模型精修、复杂表格、多栏、印章/图注、OFD/WPS、高级 layout、多本地引擎交叉验证和批量 reprocess。后期能力不得改变 P3 数据合同，只能产生新 candidate 或 `reprocess` edition。

## 3. 内容生产状态机（唯一 owner）

唯一状态序列：

```text
raw
  -> extracted
  -> ocr_candidate          # 仅无可信文本层或显式复核时
  -> layout_candidate
  -> model_refined_candidate # 可选，外部模型 gate 后
  -> human_confirmed
  -> edition_created
```

状态机终止于 `edition_created`。`indexed` 是 PolicyBase_14 对 confirmed/current edition 的**下游索引投影结果**，不是内容生产状态机节点；索引状态、record_hash 与 analyzer 见 PolicyBase_14。

旁路状态：`needs_review | rejected | failed | superseded_candidate`。

规则：

1. `raw` 保存获授权的原始字节与 provenance；网页 raw 未获保存授权时只保存允许的摘要/hash。
2. `extracted` 是确定性本地提取，不补写原文没有的信息。
3. `ocr_candidate` 永远是候选，不得直接晋升为 main Markdown。
4. `layout_candidate` 将文本块组织成 Markdown，但不能把推测当原文。
5. `model_refined_candidate` 只能改善识别或排版，不能裁决合规、分类或法律效力；外部模型 gate 见 §13。
6. `human_confirmed` 必须指向具体候选、diff 和 reviewer；可以是维护者确认，也可以是满足受控低风险规则的规则确认。
7. 只有 `human_confirmed` 可进入新 edition；只有 current edition 可默认被索引（投影动作归 PolicyBase_14）。
8. 任一阶段重跑产生新 ARTIFACT_ID（生成语义见本卷 §4），不覆盖旧 artifact。

允许跳过阶段：可信 HTML 可 `raw -> extracted -> layout`；优质 PDF 文本层可跳过 OCR；不使用模型可 `layout -> human_confirmed`。**禁止跳过 confirmation**。

## 4. 统一内容工件 schema（唯一 owner）

每个文本/版面 candidate 至少保存：

```yaml
artifact_id: art-layout-...      # 生成语义见本卷 §4
stage: layout_candidate
input_file_ids: [file-pdf]
output_file_id: file-layout-md
geometry_file_id: file-geometry-json
tool:
  name: policybase-layout
  version: 1.2.0
  config_hash: sha256:...
created_at: 2026-08-04T03:15:00Z
content_hash: sha256:...
quality:
  coverage: 0.98
  confidence: 0.91
  warnings: [table_needs_review]
```

坐标工件固定使用页坐标系：

```yaml
coordinate_system: normalized_page_v1
pages:
  - page: 1
    width: 1.0
    height: 1.0
    blocks:
      - block_id: p1-b001
        bbox: [0.08, 0.10, 0.92, 0.16]  # x0, y0, x1, y1
        order: 1
        kind: heading
        text: 第一章 总则
        confidence: 0.99
        source_span: {file_id: file-page-1, page: 1}
```

`kind` 至少支持 `heading | paragraph | list_item | table | table_cell | image | caption | footnote | header | footer | unknown`。同页 `order` 必须唯一、正整数、形成明确阅读顺序。表格必须有 row/column/span；无法可靠还原时保留图片/文本与 warning，不伪造单元格。

`tool` 字段的版本维度按**操作类别**取最小必填集，闭合门要求（OCR / layout / model refine / correction 四类操作的版本维度必须可机械判）。`<absent>` 表示该维度对此类操作**声明不适用**，而非缺失：

| 操作类别 | `schema_version` | `backend_version` | `prompt_version` | `config_hash` |
|---|---|---|---|---|
| OCR（local/model） | required | required（local 亦标 backend，如 `rapidocr@<version>`；model 见 §12） | `<absent>`（local OCR 无 prompt） / required（model OCR，按 §12） | required |
| Layout | required | required（layout renderer/engine 标识 + version） | `<absent>` | required |
| Model refine | required | required（见 §12 backend/model/adapter version） | required（prompt schema version + 模板 hash，禁止裸 prompt） | required |
| Correction（人工 / 受控规则） | required | required（correcting tool 标识 + version；纯人工标 `human@<actor_id>` 或规则 engine + version） | `<absent>` | required |

要求：

1. `schema_version` 对四类全强制（即本 artifact schema 自身版本）。
2. `backend_version`：OCR/layout/model refine 强制；correction 强制标 correcting tool/version（纯人工修改亦须标 actor 或受控规则 engine/version，不留空）。`backend` 字段不得冒充 §10 engine 业务枚举 `{local,model}`（归属见 §10）。
3. `prompt_version`：model refine 强制；local OCR 与 layout 标 `<absent>`，显式声明该维度对此类操作不适用，而非省略。model OCR 按 §12（model OCR 是 model operation，prompt_version required）。
4. `config_hash`：四类全强制（已存在）。
5. 每次内容变化产生新 artifact 与 §5.1 直接父 artifact 的机器可读 diff；§5.1 diff 合同覆盖 layout / OCR / model refine / 人工修改 / reprocess 五类内容变化操作。

本卷 §4 统一内容工件 schema 同时约束 `ARTIFACT_ID` 与 `file_id` 的 canonical 形态和稳定性；CLI 词法投影见 PolicyBase_15。

## 5. Diff、确认与内容层 review decision（唯一 owner）

### 5.1 Diff 合同

每个 OCR、layout、model refine、人工修改与 reprocess 必须针对**直接父 artifact** 产生机器可读 diff，至少包含：

- before/after artifact 与 hash；
- 按 block 的 `inserted | deleted | reordered | text_changed | type_changed`；
- Markdown unified diff；
- 表格结构变化；
- 低置信块与人工决策；
- 生成工具或 actor。

### 5.2 内容层 review decision

内容层 review decision 取值域（唯一 owner，CLI 绑定见 PolicyBase_18）：

```text
accept_all
accept_selected
reject
hold
```

`accept_selected` 必须列出 block/change ID；系统据此产生**新的** confirmed artifact，不可原地编辑模型输出。确认 operation 记录 reviewer、time、reason、selected artifact、diff 与来源证据。

本卷 review decision 是**内容层**判定（哪一份 candidate 的文本/版面被接受为 confirmed 正文），与 PolicyBase_08 §9 的**身份层** reviewed decision（判定两份 candidate 是否同一文献）正交，不得混用、不得互相推导。

### 5.3 Partial scope 确认规则（＋补，本卷 owner）

当 layout_candidate 或 model_refined_candidate 标记 `partial_extract`（§9 OFD/WPS fallback、§11 跨页表格/多栏/印章 warning 等）时，后续 `confirm` 操作**默认拒绝**，除非同时提交以下 correction/reprocess manifest 证据之一：

- `correction_manifest`：列出未覆盖的页/块、原因、人工补充的文本或图注来源，且补充文本标注 `source_kind=human_transcription` 与 actor；
- `reprocess_manifest`：声明继承自已确认的上游 artifact，并附 base edition 引用、差异范围与重跑工具/version/config_hash。

确认 operation 必须把所选 manifest 的 hash 写入 audit；系统据此生成 `confirmed_with_partial` 标记的新 artifact。无 manifest 或 manifest hash 不匹配时返回 `partial_extract_requires_review`（见 §16），不得静默晋升。

partial 确认规则只约束**内容层**晋升，不影响身份层同一性判断（PolicyBase_08）与合规三门（PolicyBase_04 §7）。

## 6. 格式识别与安全

格式依据 magic/header 与容器结构识别，**不信任扩展名或 MIME**。至少覆盖 HTML、PDF、OFD、OOXML、专有 WPS、JPEG、PNG。未知格式只保留获授权原件并进入 review；不得执行宏、脚本、嵌入对象或外链。

临时页图、缓存与失败残留在忽略工作区；正式保留的原件、确认派生物与必要审计工件均登记 PolicyBase_09 manifest。

## 7. HTML 与图片正文

网页正文、网页内作为正文的图片与附件链接都必须成为 source observation 的一部分。HTML 本地提取规则：

- 保留标题层级、段落、列表、链接、简单表格与图注；
- 去掉导航、广告、分享、推荐与重复页眉页脚；
- 对正文图片登记来源 URL、alt、hash 与页面位置；
- 图片含实质正文时进入本地 OCR；装饰图片不得 OCR 混入正文；
- 多页正文保持页面/分段 provenance；
- 提取规则/profile/version/hash 写入 operation。

## 8. PDF

PDF 文本层使用 PyMuPDF 本地提取。逐页记录文本覆盖率、字符异常率与图片覆盖率；不能只以"非空"认定可信。

下列情况进入本地 OCR：无文本层、覆盖率低、乱码超过阈值、文本与页面图显著不一致或维护者显式复核。空输出返回稳定错误，不生成空 Markdown。加密、损坏、无图无文本或解析失败均记录 `error_code`（见 §16）。

## 9. OFD 与 WPS

OFD 优先 `easyofd`；ZIP/XML fallback 只能标记 `partial_extract`，不宣称版式、签章或批注完整。失败不生成空文件。`partial_extract` 触发 §5.3 partial 确认规则。

可验证为 OOXML 的新版 WPS 按对应 Office 容器处理。专有 WPS 不自动解析、不调用宿主 WPS/Office/LibreOffice；只能人工受控转换，保留原件、工具/version/actor/time 与确认；转换件未确认不得继续。

## 10. OCR 引擎合同与业务枚举（唯一 owner）

OCR engine 业务枚举（唯一 owner；CLI 绑定见 PolicyBase_18）：

```text
{local, model}
```

- `local` 是默认安全路径。P3 基线 backend 为 RapidOCR；实现内部记录实际 backend（如 `rapidocr`）与 version。CLI 不把 backend 名冒充 engine 业务枚举。未来本地 backend 通过 capability 接口扩展：

```text
recognize(images, language, geometry=true) -> blocks + confidence + diagnostics
```

- `model` 是外部模型增强，只能在 §13 外部模型 gate 通过后使用。不得公开 `both`；对比须分两次独立运行，各自产生 artifact，再由 §5 diff/review 连接。

OCR 不一致不能默认采用模型结果。低置信、关键数字/文号/日期差异、阅读顺序差异与表格结构差异必须 `needs_review`。OCR candidate 默认不可索引、不可发布。

本卷只定义业务枚举语义与 backend capability 接口；`--engine` 字面值、参数解析阶段、早拒绝顺序与 engine 相关 CLI 诊断码归属 PolicyBase_18（引用本枚举）。

## 11. Layout 与 Markdown

最小 layout 必须：

- 根据 geometry 产生确定性阅读顺序；
- 保留页边界 provenance；
- 将标题、段落、列表与简单表格渲染为 CommonMark/GFM；
- 页眉页脚只在有重复证据时剔除；
- 不把视觉接近自动解释为同一段；
- 对跨页表格、多栏、脚注与印章设置 warning（warning 触发 §5.3 partial 确认规则）；
- 输出必须可由 geometry 追溯到原页块。

Markdown 规范版本、渲染器版本与 config hash 必须记录。纯格式变化也产生 reprocess candidate，不静默改 current。

## 12. 模型精修合同（backend capability 接口）

模型能力用 backend capability 描述，不把 `stepfun text chat` 或 `mmx vision describe` 等临时 CLI 语法写成永久机器合同。适配器至少声明：

- backend / model / capability / version；
- text / vision 输入类型；
- prompt schema version；
- timeout / size / page limits；
- structured output schema；
- redaction / logging behavior。

每次调用记录 backend、model、adapter version、prompt file path/hash、system/user template hash、脱敏 input hash、output hash、参数、退出码与授权 ID。**禁止裸 prompt**；prompt 必须来自版本化文件。模型只生成 candidate，不直接写 current edition。

模型可以：纠正明显 OCR 错位、建议标题/段落/列表/表格结构、生成 diff。模型不得：补造缺失条文、裁决公开性/密级/PII（红线，见 PolicyBase_04）、自动改变文号/机关/日期、覆盖原始证据或直接确认。

## 13. 外部模型 gate 触发时机（业务规则归本卷；gate 规则归 04）

内容生产在 **`model_refined_candidate` stage** 触发外部模型 gate：即在 `layout_candidate` 之后、`human_confirmed` 之前。模型只消费已通过 PolicyBase_04 §6 本地预检并已确认上游 artifact 的 candidate，不接受 raw、未确认转换件或未授权原件作为输入。

**外部模型 gate 业务规则（前提清单、密钥隔离、scope 校验、fail-closed 语义）见 PolicyBase_04 §8**；本卷不重列。红线：外部模型不参与公开性/密级/PII 终审（PolicyBase_01 §3 不变量；落地见 PolicyBase_04）。gate 任一前提未满足时按 PolicyBase_04 §9 fail-closed：不调用、不写 candidate、不外传、不保留外传字节。CLI 参数解析阶段的触发点（哪个子命令的哪个参数解析进入此门）见 PolicyBase_18。

## 14. 密钥与日志

密钥只来自进程环境、系统 keyring 或被忽略的加密 secrets；不得进 Git、manifest、prompt、命令参数或日志。模型子进程使用最小环境。

stdout / stderr / traceback 必须脱敏。日志只记录 ID、hash、工具/模型 version、状态、错误码与时间；不记录未授权全文、完整 PII、密级正文或 key。脱敏器不可用时拒绝调用或持久化。

## 15. Reprocess 与回滚（内容域）

工具、OCR backend、layout config、prompt 或模型升级时，内容域执行：

1. 选择明确 base edition；
2. 读取其 raw/original 或已确认上游工件；
3. 产生新 artifact 链与 §5 diff；
4. 人工确认（§5 review decision）；
5. 建 PolicyBase_09 `edition_kind=reprocess` edition；
6. PolicyBase_09 atomic 切换 current；
7. PolicyBase_14 增量投影（索引动作归索引卷）；
8. 若结果不佳，PolicyBase_09 rollback 选择旧 edition。

不得批量原地改历史 edition。批量任务必须支持 dry-run、范围清单、失败隔离、最大变更率与中止；每个 doc 独立 atomic 切换。edition manifest、operations 枚举与 switch_kind 见 PolicyBase_09。

## 16. 错误边界（内容维度）

稳定诊断码至少包括：

```text
unsupported_attachment_format
pdf_encrypted
pdf_corrupt
empty_extraction
ocr_no_output
ocr_low_confidence
layout_reading_order_ambiguous
table_structure_ambiguous
partial_extract_requires_review
model_gate_denied
model_gate_scope_mismatch
external_transfer_authorization_invalid
model_backend_unavailable
model_output_schema_invalid
confirmation_missing
reprocess_base_missing
```

`model_gate_denied` / `model_gate_scope_mismatch` / `external_transfer_authorization_invalid` 的判定前提与 fail-closed 语义见 PolicyBase_04 §8 / §9；本卷只列内容维度诊断面。通用 `cli_*` 诊断码与统一退出码见 PolicyBase_19。

错误不产生成功 operation、不留下正式空文件、不改变 current、不泄露内容或凭据。

## 17. 验收合同

P3 golden 必须离线覆盖：HTML、文本 PDF、扫描 PDF→local OCR、JPEG/PNG 正文、基础 layout/geometry、简单表格、diff、人工确认、edition 与 rollback。`indexed` 是 PolicyBase_14 对 confirmed/current edition 的下游投影；P3 只需证明输出满足 PolicyBase_14 的可消费前置条件，不要求 P3 交付索引器。

后期 golden 覆盖 OFD、OOXML/专有 WPS、复杂版面、外部模型 gate、prompt/model/version 审计、模型输出拒绝与批量 reprocess。

```bash
pytest tests/golden/content_pipeline/
pytest tests/golden/attachments/
pytest tests/golden/model_gate/
policybase verify boundary --fixture-root tests/golden/content_pipeline/
```

测试不得依赖真实外部模型、网络、敏感材料或真实 key。

## 18. 不变量

1. P3 本地链路不依赖外部模型。
2. raw、candidate、confirmed、edition 状态不可混用；`indexed` 是下游投影，不是内容生产状态机节点。
3. 页/块/坐标与阅读顺序可追溯。
4. 所有精修都有 version、diff、确认与回滚。
5. 模型只产候选；CI 不调用模型。
6. 原件与历史 edition 永不被派生输出覆盖。
7. partial candidate 的 confirm 默认拒绝，除非 correction/reprocess manifest 证据闭合。
