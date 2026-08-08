# PolicyBase 路线与实施清单

> 状态：主权威
> 分卷编号：PolicyBase_02
> 主题：roadmap-and-implementation
> 重构日期：2026-08-08
> 仓库：NormBook/PolicyBase

---

## 1. 本卷定位与非职责边界

本卷是 PolicyBase 路线、系统模块与 GITHUB-INIT 项目参数的唯一权威，三重职责：

- **roadmap（§3-§15）**：定义 P0-P8 阶段、阶段依赖图、各阶段能力目标与阶段退出边界语义。
- **GITHUB-INIT 项目参数（§2）**：本卷是 `seeds/GITHUB-INIT.md`（通用 GitHub 治理初始化模板）在本项目的参数绑定文档。§2 提供该模板全部 `${VAR}` 的具体值；GITHUB-INIT.md 消费这些值完成 P0 治理基础设施初始化。
- **系统模块清单（§16）与变更原则（§17）**。

GITHUB-INIT.md 的通用方法论（状态机、门禁分层 GOV-G0~G4、CI 逻辑、自举流程、验收设计要求、设计借鉴、根因 R1-R6）不在本卷复述；本卷只提供项目数值与路线。二者职责边界见 GITHUB-INIT.md §11。

本卷只描述前向能力顺序，不定义具体实施流程。阶段表示可验收能力，不表示目录、团队或发布时间。各阶段内部的技术规格由对应业务卷（PolicyBase_04-19）定义。

## 2. GITHUB-INIT 项目参数绑定

本节绑定 `seeds/GITHUB-INIT.md` §0.0「必需项目参数清单」的全部 `${VAR}`。这些值是 PolicyBase 正式开始 P0 执行的前提。执行状态类参数（标 `*`）须在执行前以 `gh api` 实测确认。

### 2.1 核心身份

| 参数 | 绑定值 |
|---|---|
| `${ORG}` | `NormBook` |
| `${REPO}` | `PolicyBase` |
| `${OWNER_LOGIN}` | `janssenkm` |
| `${REPO_VISIBILITY}` | `public` |
| `${REPO_PREEXISTS}` | `*` 执行前实测（重建后用 `gh repo create` 或 `git remote add`，取决于仓库是否已建） |
| `${PLAN}` | `Free` |
| `${DISCUSSIONS_URL}` | `https://github.com/NormBook/PolicyBase/discussions` |

### 2.2 路线与 Milestone

| 参数 | 绑定值 |
|---|---|
| `${ROADMAP_DOC}` | `PolicyBase_02 §5-§14`（阶段依赖图与各阶段能力目标） |
| `${MILESTONE_COUNT}` | `9` |
| `${FIRST_MILESTONE}` | `P0 Repository Governance Bootstrap` |
| `${MILESTONES}` | §6-§14 各阶段标题（不含逗号；`gh` 按逗号分割列表参数） |

9 个 Milestone 与阶段一一对应：

| Milestone 标题 | 阶段 | 定义章节 |
|---|---|---|
| `P0 Repository Governance Bootstrap` | P0 | §6 |
| `P1 Project Skeleton and Contract Foundation` | P1 | §7 |
| `P2 Identity Dedup and Versioned Ingest` | P2 | §8 |
| `P3 First Source and Content Closure` | P3 | §9 |
| `P4 Index Search and Export` | P4 | §10 |
| `P5 Editorial and CLI Completion` | P5 | §11 |
| `P6 Authorized Model Refinement` | P6 | §12 |
| `P7 Advanced Attachment and Layout` | P7 | §13 |
| `P8 Source and Data Expansion` | P8 | §14 |

### 2.3 规格体系

PolicyBase 有版本化规格卷体系与校验脚本，P0 的「规格校验」门禁与 G0 会话启动检查依赖它。

| 参数 | 绑定值 |
|---|---|
| `${SPEC_ENABLED}` | `true` |
| `${SPEC_VOLUME_PREFIX}` | `PolicyBase` |
| `${SPEC_VOLUME_COUNT}` | `19` |
| `${SPEC_FILE_PATTERN}` | `PolicyBase_NN.md`（NN 为两位连续编号 01-19） |
| `${SPEC_VERIFY_SCRIPT}` | `seeds/verify_seed_set.py` |
| `${SPEC_VERIFY_OK_OUTPUT}` | `OK seed_set_verified: 19 volumes verified` |
| `${SPEC_VERIFY_COMMAND}` | `python3 seeds/verify_seed_set.py` |
| `${SPEC_MAP_DOC}` | `seeds/PolicyBase_01.md`（权威地图） |
| `${SPEC_CONVENTIONS_DOC}` | `seeds/PolicyBase_03.md`（协作约定，含验收证据格式） |
| `${SPEC_SCOPE_TOKEN}` | `spec` |
| `${SPEC_SCOPE_REGEX}` | `pb\d{2}`（标题中 `PB01`-`PB19` 映射 `scope:spec`） |

19 卷主权威地图见 PolicyBase_01 §4。`seeds/verify_seed_set.py` 校验 frontmatter、分卷编号一致、围栏配对、H2 无重复、无 legacy `PB\d{2}` 引用、无 TODO/FIXME/TBD 等占位符、无悬空 `PolicyBase_NN` 引用。

> **`seeds/` 运行时引用**：P0 把 `seeds/` 钉进 pr-gates.yml 的 verify-seeds job 与 AGENTS.md G0 启动检查，与 PolicyBase_01 §9（禁止长期引用 `seeds/PolicyBase_*`）+ PolicyBase_03 §8（seed 非长期运行时权威）存在张力。按 GITHUB-INIT.md §0.2 偏差处置原则：此张力无法在 P0 消除（`docs/` 正式文档体系是 P1 交付物），在此处显式标注--影响：CI 与会话启动依赖 seeds 路径；检测信号：`git grep "seeds/PolicyBase_"`；修正条件：P1 `docs/` 建成后，校验脚本迁至 `scripts/verify_spec_set.py`，pr-gates job 改名 `verify-specs`，AGENTS.md G0 改读 `docs/`。附加调研数据 `seeds/provinces/*.yaml`（31 省）是来源调研 proposed input（PolicyBase_10 §14.2），非运行时 registry。

### 2.4 Issue Types / Projects / Scope / 标签

| 参数 | 绑定值 |
|---|---|
| `${ISSUE_TYPES_PREEXIST}` | `*` 执行前实测（Issue Type 是组织级；NormBook 组织可能已存在） |
| `${SCOPES}` | `infra,ci,cli,data,docs,governance`（6 个通用 scope） |
| `${PROJECTS_V2_ENABLED}` | `true` |
| `${PROJECT_NUMBER}` | `*` 执行前实测（重建后确认 project 编号） |
| `${PROJECT_NAME}` | `PolicyBase Development` |
| `${LABEL_COUNT}` | `19` |

Issue Type 映射（`${ISSUE_TYPES}`）：`feat`->Feature、`fix`->Bug、`docs`->Documentation、`refactor`->Refactor、`gov`->Change、`decision`->Decision、`chore`->Task、`seed`->Seed Revision（规格卷修订 PB01-19）、第三方无前缀->Intake。另保留 `Acceptance` 类型用于里程碑验收认证，不参与日常开发 type 分类。通用方法论见 GITHUB-INIT.md §2.2.3。

标签 19 个 = 状态机(6: do:triage/ready/in-progress/review/acceptance + state:blocked) + 来源(2: origin:owner/external) + 范围(7: scope:spec + 6 通用 scope) + 优先级(4: priority:blocker/high/medium/low)。通用分类与色值见 GITHUB-INIT.md §2.2.2。

派生量：`${REPO_VISIBILITY_UPPER}`=`PUBLIC`、`${ISSUE_TYPE_MIN}`=`10`、`${SCOPES_AS_JS_ARRAY}`=`['infra','ci','cli','data','docs','governance']`。

## 3. 产品目标

PolicyBase 应使维护者能够：

1. 注册并审查政府四库（`zcwjk` / `gz` / `flk` / `xxgk`）来源。
2. 用声明式规则适配 SSR、SPA/API、分页、附件和站点差异。
3. 合规下载网页和附件，并保留来源证据。
4. 把 HTML、PDF、OFD、Office、图片转换为可审计 Markdown edition。
5. 使用本地提取/OCR、人工校订以及受授权的模型命令完成版面重建和精修。
6. 对文献进行确定性标识、分类、去重、更新和历史版本管理。
7. 在 SQLite FTS5 中检索正文、元数据、关系、版本和来源证据。
8. 发现来源或内容变化后增量更新、重新处理、回滚和重新索引。

## 4. 非目标

P0-P8 不建设 Web GUI、移动应用或公共服务 API；不采集非主动公开或需绕过访问控制的正文；不在 CI 中调用外部模型；不让模型作最终事实或验收裁决；不把 candidate、未确认 OCR、未授权全文或失效规则伪装为正式资产。党务/军事文献与标准规范能力不在 P0-P8 范围。

## 5. 阶段依赖图

```text
P0 Repository Governance Bootstrap
  -> P1 Project Skeleton and Contract Foundation
      -> P2 Identity Dedup and Versioned Ingest
          -> P3 First Source and Content Closure
              -> P4 Index Search and Export
                  -> P5 Editorial and CLI Completion
                      -> P6 Authorized Model Refinement
                          -> P7 Advanced Attachment and Layout
                              -> P8 Source and Data Expansion
```

阶段按主路径串行验收，但后续阶段的研究、fixture 准备和非交付调研可以提前进行。**不得以提前研究证明前置能力已经完成。**

## 6. P0 Repository Governance Bootstrap

目标：建立可审计、可门禁、由用户控制远程授权边界的 issue-first 治理基础设施（详细任务定义见 `seeds/GITHUB-INIT.md` 通用模板，项目参数见本卷 §2）。P0 阶段不等同于优先级；Issue 优先级由治理文档的 `priority:blocker|high|medium|low` 标签表达。

范围：本地仓库治理文件、GitHub 公共仓库初始化、Issue/PR 模板、CODEOWNERS、分支保护、CI 门禁、Issue-first 自动化及其可复核验收证据。P0 不实现完整采集、去重、索引、OCR 或模型调用。

## 7. P1 Project Skeleton and Contract Foundation

目标：建立可运行的最小 Python 工程骨架，并建立承载业务合同的最小 schema 和正式文档体系。

范围：Python >=3.12 项目骨架和依赖组；CLI shell 与 minimal `verify` 命令（`layout`）；schema/taxonomy、source/rule、manifest/edition 的下限骨架；golden/fixture 基础；spec-manifest。P1 不实现完整采集、去重、索引、OCR 或模型调用。

## 8. P2 Identity Dedup and Versioned Ingest

目标：让 candidate 能安全、确定地成为带历史版本的正式文献包。

范围：归一化、机关解析、canonical key、确定性 ID、分类/metadata 全字段、去重、reviewed decision、外部导入、immutable edition、current 指针、correction/update/supersede/rollback operation 和原子写入。

basic rule schema 的实现是 P2 的前置工作；它必须在 P3 启动前完成。P2 不扩大真实来源范围。

## 9. P3 First Source and Content Closure

目标：以 `cn-npc-flk` 完成第一个真实来源从注册到 confirmed edition 的闭环。

P3 必须具备：Source Registry、Profile、Recipe 和已实现 basic Rule；列表/详情采集、checkpoint、增量和站点漂移诊断；HTML->Markdown；PDF 文本层提取；当首来源材料需要时的最小本地图片/PDF OCR 和基础阅读顺序；compliance、candidate、ingest、edition、current 和回滚；normal/edge/error/deny fixture 与真实场景证据。

P3 止于 `data/documents/` 中的 confirmed current edition。外部模型、高级 OFD/WPS、多引擎版面恢复不阻塞 P3。

## 10. P4 Index Search and Export

目标：对 confirmed/current 且获准消费的文献建立确定、可重建的索引和导出。

范围：版本化中文 analyzer、SQLite FTS5、结构化过滤、文号/机关别名、关系索引、来源/页码证据、current/history 查询、增量索引、JSONL/CSV/Markdown/site export 和 publication gate。candidate、未确认输出和历史 edition 默认不得进入 current 全文索引；历史查询必须显式请求。

## 11. P5 Editorial and CLI Completion

目标：提供稳定的维护者工作台和普通查询入口。

范围：稳定查询、来源、采集、导入、`prepare`、索引、导出、`process` 和 `verify` 入口；review queue；`process correct -> review -> confirm`，其中 confirm 执行正式 ingest action；update/correction；edition diff；reprocess；rollback；重新索引和批量诊断。模型只是 `process ocr/refine --engine model` 的受控 backend，不建立绕过内容状态机的顶层入口。P5 只完成已成熟能力的入口，不用占位命令伪装未来能力。

## 12. P6 Authorized Model Refinement

目标：在本地合规预检和人工授权之后，用外部模型辅助 OCR、版面、结构抽取和 Markdown 精修。

范围：backend capability contract、prompt/version hash、最小子进程环境、脱敏日志、外传授权、候选 diff、人工接受/部分接受/拒绝和审计。模型输出仍是 candidate，不直接替换 confirmed edition。

## 13. P7 Advanced Attachment and Layout

目标：完善复杂附件和高保真内容处理。

范围：OFD、OOXML、受控 WPS 人工转换、多栏阅读顺序、表格、页眉页脚、脚注、图片块、页面坐标、多 OCR/backend 对比、批量 reprocess、质量评估和回滚。专有格式、签章和法律效力不得由模型猜测恢复。

## 14. P8 Source and Data Expansion

目标：在稳定规则和内容管线之上扩展国家、省、市和专题来源。每个来源都需要独立注册、公开性/robots/条款审查、fixture、canary、稳定规则、回滚点和来源验收。P8 不允许用一个通配规则隐式授权新域名。来源可按 S-series 建立独立 Acceptance 窗口；单个后续来源失败不应破坏既有来源能力认证。

## 15. 阶段退出边界语义

阶段退出的语义同时满足以下维度：

- 退出维度一：该阶段全部能力已实现并通过验证。
- 退出维度二：依赖阶段的能力已具备，前置能力未被绕过。
- 退出维度三：测试覆盖 normal/edge/error，golden 通过。
- 退出维度四：正式文档覆盖、风险和豁免可追溯。
- 退出维度五：维护者确认能力达标。

P0 退出门（`GATE-P0-EXIT`）是上述维度在 P0 的落地，定义见 GITHUB-INIT.md。

## 16. 系统模块清单

以下为 PolicyBase 系统功能域模块名称，供跨卷引用：

Governance, Schema, Classifier, Normalizer, Identity, Dedup, Storage, Compliance, Source, Acquisition, Indexer, CLI, Attachment, Model, Dependencies, Docs, Test Infrastructure, Security

## 17. 变更原则

路线阶段边界变化需记录变更理由、影响和迁移方案。变更使旧能力失效时，建立后继验证，不重写旧证据。本卷只声明路线，任何能力完成必须由实际测试和验证证明。

本卷 §2 参数绑定变更（如 org/repo/owner 变化）须同步更新 GITHUB-INIT.md 消费侧；GITHUB-INIT.md 通用方法论变更不强制联动本卷，但本卷须标注所基于的 GITHUB-INIT.md 版本。
