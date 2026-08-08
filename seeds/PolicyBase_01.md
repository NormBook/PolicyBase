# PolicyBase 分卷总纲与权威地图

> 状态：主权威
> 分卷编号：PolicyBase_01
> 主题：overview
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase

---

## 1. 本卷定位

本卷只定义项目范围、分卷权威地图、跨卷不变量、冲突处理与正式迁移顺序。字段、枚举、命令、算法与状态机必须由对应主题分卷唯一维护；本卷的摘要叙述不能替代它们。

非职责边界（本卷不展开，见对应 owner 卷）：

- 阶段定义、依赖图与当前实施清单：见 PolicyBase_02。
- 协作风格、命名、去重与引用约定：见 PolicyBase_03。
- 合规字段、`action` enum、`disclosure.mode`、密级、访问控制、外部模型 gate：见 PolicyBase_04。
正式业务文档最终进入 `docs/`、`src/policybase/`、`data/`、`scripts/` 与测试。

## 2. 产品范围

PolicyBase 建设中国政府制度性文献资产库，首要范围是政府主动公开的四类入口：

- 政策文件库 `zcwjk`；
- 规章库 `gz`；
- 法律法规库 `flk`；
- 政务公开 `xxgk`。

四库 slug 固定不变。系统处理的不是“网页”，而是可追溯的文献版本。主链路必须覆盖：

```text
registered source
  -> rule resolution
  -> acquisition run
  -> candidate
  -> compliance gate
  -> normalize / identify / deduplicate
  -> extract / OCR / layout / refine / review / confirm
  -> immutable document edition / current
  -> index / search / export
  -> refresh / correct / supersede / rollback / reprocess
```

主链路上每个环节的语义、产物与状态机由对应分卷权威定义；本卷只给链路总图。

范围边界：

- 党务与军事文献仅保留公开版分类与合规边界，来源矩阵不在当前首批 P0-P8 范围。
- 标准规范能力不在 P0-P8 范围。
- 同一字段在四库下取值域或来源差异显著时，由 owner 卷显式标注，不在本卷隐藏于通用描述。

## 3. 不可降低的跨卷不变量

以下 7 条是全系列硬约束。本卷是它们的索引；语义裁定与展开见对应 owner 卷。

1. `disclosure.mode=proactive` 是正文进入正式文献资产链的入口红线（枚举与判定见 PolicyBase_04）。
2. 不绕过 robots、条款、验证码、登录、付费墙、WAF 或其他访问控制；标准浏览器只可用于正常渲染与只读观察（访问控制合同见 PolicyBase_04）。
3. `fetch` 成功不等于获准 `transient_store/candidate`，candidate 合格不等于 `ingest`，ingest 不等于获准 `index/external_transfer/export/redistribute`；规范 `action` enum 由 PolicyBase_04 唯一维护。
4. Source Registry、Profile、Recipe、Rule 与 Adapter 只能进一步收紧权限，不能授予合规、外传、索引或发布权限（来源注册见 PolicyBase_10，Rule/Trait schema 见 PolicyBase_12（草案，实现后生效））。
5. 外部模型不参与公开性、密级或 PII 预检，不在 CI 中调用，不作为分类、去重、正文或验收的最终裁判（外部模型 gate 业务规则见 PolicyBase_04）。
6. 每次正式内容变化产生不可变 edition 与 operation 证据；不得以覆盖当前文件的方式伪造历史保留（edition/operation 合同见 PolicyBase_09）。
7. ID、去重、索引与导出必须确定、可复现、可版本化；降级路径必须可见（ID 见 PolicyBase_07，去重见 PolicyBase_08，索引见 PolicyBase_14）。

## 4. 主权威地图

共 **19 卷**，按 5 组递进。每行格式：`分卷 | 唯一主题权威`。任何概念有且仅有一个 owner；其余卷遇到该主题只能一句引用。

| 分卷 | 唯一主题权威 |
|---|---|
| PolicyBase_01 | 范围、分卷地图、跨卷不变量与冲突规则 |
| PolicyBase_02 | roadmap（P0-P8 阶段定义/依赖图/退出边界）与系统模块清单 |
| PolicyBase_03 | 协作风格、语言政策、命名、主权威去重与引用约定 |
| PolicyBase_04 | `action` enum + DAG、`disclosure.mode`、密级、访问控制、本地预检、三门与外部模型 gate |
| PolicyBase_05 | 分类树、TYPE 决定层、TYPE 前缀、公文文种与正交分类维度 |
| PolicyBase_06 | 通用 frontmatter 字段下限、edition_kind、spatial_scope、validity 与扩展 profile |
| PolicyBase_07 | 归一化、机关解析、canonical key、确定性 ID、历史 ID 与 `registry_entry_semantic_hash` |
| PolicyBase_08 | 去重、导入、多来源合并、更新判定与身份层 reviewed decision |
| PolicyBase_09 | 文献包、immutable edition、manifest、operations enum、current 与回滚 |
| PolicyBase_10 | Source Registry、来源矩阵治理、Profile/Recipe/Adapter 注册与配置组件发布状态机 |
| PolicyBase_11 | 采集引擎、candidate、checkpoint、增量、站点漂移与 handoff |
| PolicyBase_12 | 网站 Rule/Trait schema、匹配、合并、版本、canary 与回滚（主权威草案） |
| PolicyBase_13 | 内容生产状态机、统一内容工件、OCR 引擎合同、模型精修与内容层 review decision |
| PolicyBase_14 | SQLite/FTS、检索分析器、索引投影、record_hash、历史版与导出 |
| PolicyBase_15 | CLI 顶层命令面、跨命令标识、命令域路由与副作用分层 |
| PolicyBase_16 | `list/show/export` 绑定参数、组合、输出与诊断 |
| PolicyBase_17 | `source/scrape/import/prepare` 绑定参数、组合、诊断与路径安全 |
| PolicyBase_18 | `process` 内容生产命令绑定、序列图、engine/backend 绑定与诊断 |
| PolicyBase_19 | `index/verify` 绑定、全局参数、解析早拒绝序、通用诊断码、统一退出码与依赖安装 |

PolicyBase_12 在 Rule schema 实现完成前保持 `主权威草案`（见 §5）。

## 5. 草案晋升

PolicyBase_12 在 Rule schema、解析语义、deny 单调性、稳定匹配/合并、fixture、canary/rollback 与 CLI 入口全部实现前保持 `主权威草案`。

草案可以指导设计，但不得被实现、测试或其他正式文档当作已经生效的运行时合同。晋升必须在相关能力实现并验证后完成。

## 6. 冲突处理

发生跨卷冲突时：

1. 先按 §4 找到主题唯一主权威。
2. 安全与合规冲突采用更严格行为，但必须记录修正方案，不能长期依赖201c取严格者201d的口头解释。
3. 路线摘要与主题合同冲突时，主题合同决定语义，PolicyBase_02 必须同步修正阶段归属。
4. CLI 示例与绑定参数冲突时，先由 PolicyBase_15 路由到 PolicyBase_16~19 的唯一命令域 owner，以对应 owner 的矩阵为准并修正示例；**PolicyBase_15 不维护绑定参数矩阵**。
5. 规范无法同时满足时停止扩展实现，记录冲突、影响、最小裁决与迁移方案，不得削弱验收。

## 7. 业务主链路总图

以下链路各环节的语义、产物与状态机由对应分卷权威定义，本卷只给链路总图：

```text
source registration
  -> rule resolution
  -> acquisition snapshot/run
  -> candidate/compliance
  -> normalize/identity/dedup
  -> extract/OCR/layout/refine/review/confirm
  -> immutable edition/current
  -> index/search/export
  -> refresh/correct/supersede/reprocess/rollback
```

各环节内部状态机见对应业务卷（PolicyBase_04-14）。任一环节只有成功路径、没有失败或重入行为为严重缺陷。candidate 直接进入正式索引、模型输出直接覆盖 confirmed edition、更新覆盖历史文件，均为错误。

PolicyBase_12（Rule schema）在当前为草案，链路中 `rule resolution` 环节的可追踪性记录为 `planned`，不作为运行时可生效合同。

## 8. provinces 调研数据

`seeds/provinces/*.yaml`（31 省）与 `seeds/provinces/SUMMARY.md` 是来源调研材料 / proposed input，属于 PolicyBase_10（来源矩阵治理）的参考数据。不作为版本化 Registry、Recipe、Rule 或 Trait 的运行时来源。

## 9. 当前基线声明

截至 2026-08-04，本系列 19 卷为业务规格种子文档。"老 PB*.md（PB01~PB28）"是 legacy 知识输入，不作为当前权威引用。禁止让正式实现长期引用 `seeds/PolicyBase_*`。
