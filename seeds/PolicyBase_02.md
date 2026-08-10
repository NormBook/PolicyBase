# PolicyBase 路线与实施清单

> 状态：主权威
> 分卷编号：PolicyBase_02
> 主题：roadmap-and-implementation
> 重构日期：2026-08-04
> 仓库：NormBook/PolicyBase

---

## 1. 本卷定位与非职责边界

本卷是 PolicyBase 路线与系统模块的唯一权威，分为三部分：

- **roadmap（§2-§14）**：定义 P0-P8 阶段、阶段依赖图、各阶段能力目标和阶段退出边界语义。
- **系统模块清单（§15）**：定义系统各功能域模块名称，供跨卷引用。
- **阶段变更原则（§16）**：路线变更的处理规则。

阶段语义、能力目标和依赖图见本卷；各阶段内部的技术规格由对应业务卷（PolicyBase_04-19）定义。

本卷只描述前向能力顺序，不定义具体实施流程。阶段表示可验收能力，不表示目录、团队或发布时间。

## 2. 产品目标

PolicyBase 应使维护者能够：

1. 注册并审查政府四库（`zcwjk` / `gz` / `flk` / `xxgk`）来源。
2. 用声明式规则适配 SSR、SPA/API、分页、附件和站点差异。
3. 合规下载网页和附件，并保留来源证据。
4. 把 HTML、PDF、OFD、Office、图片转换为可审计 Markdown edition。
5. 使用本地提取/OCR、人工校订以及受授权的模型命令完成版面重建和精修。
6. 对文献进行确定性标识、分类、去重、更新和历史版本管理。
7. 在 SQLite FTS5 中检索正文、元数据、关系、版本和来源证据。
8. 发现来源或内容变化后增量更新、重新处理、回滚和重新索引。

## 3. 非目标

P0-P8 不建设 Web GUI、移动应用或公共服务 API；不采集非主动公开或需绕过访问控制的正文；不在 CI 中调用外部模型；不让模型作最终事实或验收裁决；不把 candidate、未确认 OCR、未授权全文或失效规则伪装为正式资产。党务/军事文献与标准规范能力不在 P0-P8 范围。

## 4. 阶段依赖图

```text
P0 GitHub Initialization
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

> **GitHub Milestone 绑定**：§4-§13 的阶段标题即 GitHub Milestone 列表。`P0 GitHub Initialization`（§5）由通用模板 `seeds/GITHUB-INIT.md` §4.3c 创建——P0 自指（P0 即 GitHub 初始化过程），对任意项目通用；P1-P8（§6-§13）由本卷定义，在 P0 完成后的规划阶段各自创建为 GitHub Milestone。不使用 `phase:p*` 标签。

## 5. P0 GitHub Initialization

目标：建立可审计、可门禁、由用户控制远程授权边界的 issue-first 治理基础设施。P0 的通用初始化流程见 `seeds/GITHUB-INIT.md`（通用模板；P0 自指——P0 即 GitHub 初始化过程，对任意项目通用）。P0 阶段不等同于优先级；Issue 优先级由治理文档的 `priority:blocker|high|medium|low` 标签表达。

范围：本地仓库治理文件、GitHub 公共仓库初始化、Issue/PR 模板、CODEOWNERS、分支保护、CI 门禁、Issue-first 自动化及其可复核验收证据。P0 不实现完整采集、去重、索引、OCR 或模型调用。

### 5.1 规格治理扩展（PolicyBase 在通用 P0 之上的叠加）

`seeds/GITHUB-INIT.md` 是纯通用模板，不承载 PolicyBase 的规格卷体系（见 GITHUB-INIT.md §11 职责边界）。PolicyBase 在通用 P0 初始化之上叠加下列规格治理扩展，在 P0 期间（通用基础设施就绪后）接入：

- **CI 验证 job**：在通用 pr-gates.yml（`ai-disclosure` + `dor-check`）之上追加 `verify-seeds` job，运行 `python3 seeds/verify_seed_set.py`，期望输出 `OK seed_set_verified: 19 volumes verified`；同步加入分支保护 `required_status_checks.contexts`。
- **G0 会话启动**：在 AGENTS.md G0（通用：读 AGENTS.md + 认证 + 查 ready Issue）之上追加——读权威地图 `seeds/PolicyBase_01.md` + 协作约定 `seeds/PolicyBase_03.md`，并运行 `python3 seeds/verify_seed_set.py` 确认输出。
- **规格修订流程**：Issue 标题前缀增 `seed`（→ 组织级 Issue Type `Seed Revision`）；Issue 模板增 `.github/ISSUE_TEMPLATE/seed-revision.yml`（标题 `seed(PolicyBase_NN): `）。
- **scope 识别**：issue-triage.yml 增 scope 正则 `pb\d{2}` → 打 `scope:spec` 标签；标签集增 `scope:spec`。

> **已知偏离（按 GITHUB-INIT.md §0.2 就地标注，非延后清单）**：上述扩展把 `seeds/` 钉进 CI 与 G0 运行时路径，与 PolicyBase_01 §9（禁止让正式实现长期引用 `seeds/PolicyBase_*`）、PolicyBase_03 §8（seed 文档是迁移源，不是长期运行时权威）暂时冲突。这是有意识的早期偏离：P1 正式文档体系（`docs/`）建立前，规格校验脚本无其他落点。**检测信号**：`git grep -nE 'seeds/(PolicyBase_|verify_seed)' .github/ AGENTS.md` 应返回上述扩展点。**修正条件**：P1 `docs/` 与 `scripts/verify_spec_set.py` 就绪后，CI job 改名 `verify-specs` 指向新路径，G0 改读 `docs/`，`seeds/` 降级为迁移源；该迁移走 `gov(governance)` Issue 并引用本节。

## 6. P1 Project Skeleton and Contract Foundation

目标：建立可运行的最小 Python 工程骨架，并建立承载业务合同的最小 schema 和正式文档体系。

范围：Python >=3.12 项目骨架和依赖组；CLI shell 与 minimal `verify` 命令（`layout`）；schema/taxonomy、source/rule、manifest/edition 的下限骨架；golden/fixture 基础；spec-manifest。P1 不实现完整采集、去重、索引、OCR 或模型调用。

## 7. P2 Identity Dedup and Versioned Ingest

目标：让 candidate 能安全、确定地成为带历史版本的正式文献包。

范围：归一化、机关解析、canonical key、确定性 ID、分类/metadata 全字段、去重、reviewed decision、外部导入、immutable edition、current 指针、correction/update/supersede/rollback operation 和原子写入。

basic rule schema 的实现是 P2 的前置工作；它必须在 P3 启动前完成。P2 不扩大真实来源范围。

## 8. P3 First Source and Content Closure

目标：以 `cn-npc-flk` 完成第一个真实来源从注册到 confirmed edition 的闭环。

P3 必须具备：Source Registry、Profile、Recipe 和已实现 basic Rule；列表/详情采集、checkpoint、增量和站点漂移诊断；HTML->Markdown；PDF 文本层提取；当首来源材料需要时的最小本地图片/PDF OCR 和基础阅读顺序；compliance、candidate、ingest、edition、current 和回滚；normal/edge/error/deny fixture 与真实场景证据。

P3 止于 `data/documents/` 中的 confirmed current edition。外部模型、高级 OFD/WPS、多引擎版面恢复不阻塞 P3。

## 9. P4 Index Search and Export

目标：对 confirmed/current 且获准消费的文献建立确定、可重建的索引和导出。

范围：版本化中文 analyzer、SQLite FTS5、结构化过滤、文号/机关别名、关系索引、来源/页码证据、current/history 查询、增量索引、JSONL/CSV/Markdown/site export 和 publication gate。candidate、未确认输出和历史 edition 默认不得进入 current 全文索引；历史查询必须显式请求。

## 10. P5 Editorial and CLI Completion

目标：提供稳定的维护者工作台和普通查询入口。

范围：稳定查询、来源、采集、导入、`prepare`、索引、导出、`process` 和 `verify` 入口；review queue；`process correct -> review -> confirm`，其中 confirm 执行正式 ingest action；update/correction；edition diff；reprocess；rollback；重新索引和批量诊断。模型只是 `process ocr/refine --engine model` 的受控 backend，不建立绕过内容状态机的顶层入口。P5 只完成已成熟能力的入口，不用占位命令伪装未来能力。

## 11. P6 Authorized Model Refinement

目标：在本地合规预检和人工授权之后，用外部模型辅助 OCR、版面、结构抽取和 Markdown 精修。

范围：backend capability contract、prompt/version hash、最小子进程环境、脱敏日志、外传授权、候选 diff、人工接受/部分接受/拒绝和审计。模型输出仍是 candidate，不直接替换 confirmed edition。

## 12. P7 Advanced Attachment and Layout

目标：完善复杂附件和高保真内容处理。

范围：OFD、OOXML、受控 WPS 人工转换、多栏阅读顺序、表格、页眉页脚、脚注、图片块、页面坐标、多 OCR/backend 对比、批量 reprocess、质量评估和回滚。专有格式、签章和法律效力不得由模型猜测恢复。

## 13. P8 Source and Data Expansion

目标：在稳定规则和内容管线之上扩展国家、省、市和专题来源。每个来源都需要独立注册、公开性/robots/条款审查、fixture、canary、稳定规则、回滚点和来源验收。P8 不允许用一个通配规则隐式授权新域名。来源可按 S-series 建立独立 Acceptance 窗口；单个后续来源失败不应破坏既有来源能力认证。

## 14. 阶段退出边界语义

阶段退出的语义同时满足以下维度：

- 退出维度一：该阶段全部能力已实现并通过验证。
- 退出维度二：依赖阶段的能力已具备，前置能力未被绕过。
- 退出维度三：测试覆盖 normal/edge/error，golden 通过。
- 退出维度四：正式文档覆盖、风险和豁免可追溯。
- 退出维度五：维护者确认能力达标。

## 15. 系统模块清单

以下为 PolicyBase 系统功能域模块名称，供跨卷引用：

Governance, Schema, Classifier, Normalizer, Identity, Dedup, Storage, Compliance, Source, Acquisition, Indexer, CLI, Attachment, Model, Dependencies, Docs, Test Infrastructure, Security

## 16. 变更原则

路线阶段边界变化需记录变更理由、影响和迁移方案。变更使旧能力失效时，建立后继验证，不重写旧证据。本卷只声明路线，任何能力完成必须由实际测试和验证证明。
