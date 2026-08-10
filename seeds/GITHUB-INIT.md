# GITHUB-INIT：Issue-First 治理基础设施初始化（通用模板）

> 类型：通用模板（种子提示词，可复用于任意 GitHub 项目）
> 阶段标识：`P0`（自指——P0 即本文件定义的 GitHub 初始化过程，对任意项目通用）
> 阶段名称：GitHub Initialization
> 优先级标识：使用 `priority:blocker|high|medium|low`，不使用裸 `P0/P1/P2/P3`
> 模板版本：3.0（2026-08-10 重构：拆出规格体系至项目文档，P0 自指纯通用化）
> 状态：通用模板

---

## 如何使用本模板

本文件是**可复用的通用模板**：定义任意 GitHub 项目「从零建立 issue-first 治理基础设施」所需的全部方法论——治理制度、状态机、门禁分层、CI 逻辑、自举流程、验收设计要求、设计原理 R1-R6。它**不含任何具体项目数值**，也不绑定任何特定的规格/文档体系。

**P0 自指原则**：P0 就是「本文件定义的 GitHub 初始化过程」。这对任意项目都成立——任何项目在写业务代码前都需要治理基础设施。因此本模板创建且仅创建一个 Milestone（`P0 GitHub Initialization`），不预设项目的后续路线。项目的 P1、P2… 阶段（roadmap）由项目自己的规划文档定义，在 P0 之后的规划阶段创建为 GitHub Milestone。

**使用方式**：

1. 本模板定义 §0.0 组 A 的身份参数契约（org/repo/owner 等）。
2. 执行时读本模板 §3-§6 的流程，用项目身份值替换 `${VAR}`（组 A）。
3. P0 完成后，项目在自己的规划文档中定义 P1+ 的 Milestone 与（若需要）规格治理扩展——这些**不属于**通用 P0，不由本模板承载。

> **职责边界**：本模板拥有 issue-first 的**通用方法论**；项目文档拥有**具体数值**（org/repo/owner、P1+ Milestone 列表、scope 集合）与**可选的项目特定扩展**（如规格卷体系及其 verify job、seed 修订流程）。任何具体数值或项目特定方法论出现在本模板中即为缺陷。边界详见 §11。

---

## 0. 执行须知

### 0.0 必需项目参数清单（项目参数化前必须全部提供）

本模板中所有 `${VAR}` 必须由项目绑定具体值。**未全部提供者不得启动 P0 执行**。参数分两组：

#### 组 A：核心身份（必填，无默认值）

| 参数 | 含义 | 示例值 | 被谁消费 |
|---|---|---|---|
| `${ORG}` | GitHub 组织或用户 login | `acme` | 全部远程命令、CI |
| `${REPO}` | 仓库名 | `my-project` | 全部远程命令、CI |
| `${OWNER_LOGIN}` | 仓库唯一所有者的 GitHub login | `your-login` | issue-triage、CODEOWNERS、AGENTS.md、G0 |
| `${REPO_VISIBILITY}` | `public` \| `private` | `public` | §1 现状、分支保护可选能力 |
| `${REPO_PREEXISTS}` | 仓库是否已存在（`true` 则用 `git remote add`，`false` 则用 `gh repo create`） | `true` | §4.2 |
| `${PLAN}` | 组织计划（`Free` \| `Team` \| ...），影响分支保护可用能力 | `Free` | §4.12 |

#### 组 B：Issue Types / Projects / Scope

| 参数 | 含义 | 示例值 |
|---|---|---|
| `${ISSUE_TYPES_PREEXIST}` | 组织级 Issue Types 是否已存在（`true` 则仅验证，`false` 则需创建） | `true` |
| `${ISSUE_TYPES}` | type→IssueType 映射列表（见 §2.1）；`Acceptance` 类型为**可选**项目特定项 | 见 §2.1 |
| `${SCOPES}` | scope 标签集合（项目通用范围） | `infra,ci,cli,data,docs,governance` |
| `${PROJECTS_V2_ENABLED}` | 是否启用 Projects v2 Status 同步（`true` \| `false`） | `true` |
| `${PROJECT_NUMBER}` | Projects v2 编号 | `1` |
| `${PROJECT_NAME}` | Projects v2 名称 | `My Project Development` |
| `${DISCUSSIONS_URL}` | Discussions 链接（Issue 模板 config.yml） | `https://github.com/${ORG}/${REPO}/discussions` |

> **派生量（无需填写，由上述参数计算）**：
> - `${LABEL_COUNT}` = 状态机标签(6) + 来源标签(2) + scope 标签(`${SCOPES}` 数量) + 优先级标签(4)
> - `${REPO_VISIBILITY_UPPER}` = `${REPO_VISIBILITY}` 大写（AC-P0-02 断言用）
> - `${ISSUE_TYPE_MIN}` = 组织级 Issue Type 总数（AC-P0-03b 断言用）
> - `${SCOPES_AS_JS_ARRAY}` = `${SCOPES}` 转为 JS 数组字面量（issue-triage.yml 的 `VALID_SCOPES` 用，如 `['infra','ci']`）

> **项目特定扩展（不属于通用 P0）**：若项目有版本化规格卷 + 校验脚本，其 verify job、seed 修订流程、`scope:spec` 标签、G0 读规格卷步骤属于**项目特定扩展**，由项目文档定义并在 P0 之后的规划阶段接入本模板的 CI 与 AGENTS.md。本模板不承载此类扩展。

### 角色分工

| 角色 | 身份 | 职责 |
|---|---|---|
| 用户 | `${OWNER_LOGIN}`（仓库唯一所有者） | Token/认证手动步骤；最终审核与 merge 决策；第三方 Issue 采纳决定 |
| AI | 当前会话模型 | 全自动执行开发/编写/审核/测试；受门禁约束；不自我批准 merge |

### 步骤标记

- `[MANUAL-AUTH]`：用户手动完成认证、组织创建等需浏览器/交互或明确授权的步骤，AI 只提供原始命令，不封装 Token 操作
- `[LOCAL-AUTO]`：AI 可在本地自动执行的文件编写、静态检查和测试命令
- `[REMOTE-AUTO]`：用户完成认证且明确授权后，AI 可自动执行的 GitHub/远程副作用操作
- `[MANUAL-REVIEW]`：必须由用户审核、批准或 merge 的步骤

### §0.1 P0 与项目 CLI 的关系

本文件是 P0 治理基础设施的任务定义，**不实现业务代码、不创建项目业务 CLI 入口**。业务 CLI 顶层命令是后续阶段（如 P1）的交付物。P0 期间外部 AC 命令均为治理基础设施验证（标签/Issue Type/Milestone/CI 门禁的实测），不含业务 lint。

阶段、检查点、验收与退出门标识：

- `P0`：自指阶段标识——P0 即本文件定义的 GitHub 初始化过程，对任意项目通用
- `CP-P0-01`：本地治理基础文件就绪（检查点，非 GitHub Milestone）
- `CP-P0-02`：远程仓库、分支保护和 CI 门禁就绪
- `CP-P0-03`：Issue-first 自动化验证完成（含门禁有效性实证）
- `AC-P0-*`：可执行验收项，格式见 §2.5；**未执行时不写 `exit code`**
- `GATE-P0-EXIT`：P0 阶段退出门；要求检查点完成、AC 全部有实际证据且用户确认

> **术语澄清**：`CP-P0-*` 是本文件定义的阶段内检查点（Checkpoint），不是 GitHub Milestone。GitHub Milestone 是平台原生功能，用于按能力窗口分组 Issue；通用 P0 只创建一个 Milestone（`P0 GitHub Initialization`），项目的后续阶段（P1…）由项目规划文档定义并各自创建为 Milestone，不使用 `phase:p*` 标签。

### Issue-First 豁免声明（两段式自举）

本文件定义的 P0 基础设施引导**部分豁免**于「无 Issue 不开发」铁律。豁免边界是**两段式**的：

**第 1 段（豁免，直推 main）——§4.1 ~ §4.3c**

范围：git init、首次提交、推送、创建标签/Milestone、验证 Issue Types。

理由（鸡生蛋）：Issue 流程的载体（仓库内容、标签、Milestone）此刻不存在，物理上无法 issue-first。

**第 2 段（不豁免，必须走 PR）——§4.4 ~ §4.11**

范围：Issue 模板、PR 模板、CODEOWNERS、CI workflows、AGENTS.md 及软链。

标签在第 1 段末尾已就绪，Issue 能力此刻已具备，因此**治理文件本身必须通过它们所定义的流程合入**（自举）。执行序列见 §4.4 开头的「自举流程」。

> **关键收益**：第 2 段的自举 PR 会触发它自己引入的 `pr-gates.yml`，这是 P0 期间**唯一**能证明门禁真实可用的机会。若跳过，P0 退出时你将拥有一套从未被验证过的门禁，缺陷会在下一个阶段的第一个真实任务上爆发。（此即根因 R2 的来源，详见附录 B §R2）

**共同约束**：

1. **豁免终止**：`GATE-P0-EXIT` 通过后，第 1 段豁免立即失效。后续一切变更（含对本文件的修订）必须遵循 issue-first 流程。
2. **豁免不等于无门禁**。第 1 段期间通过以下机制保证质量：
   - 本文件本身是「Issue 等价物」：定义了目标、范围、AC 和验证合同
   - `AC-P0-*` 必须全部有实际证据（未执行不得填 `exit code`）
   - 所有 `[REMOTE-AUTO]` 步骤需用户明确授权后方可执行
   - 所有 `[MANUAL-REVIEW]` 步骤需用户审核确认
   - `GATE-P0-EXIT` 要求用户最终确认
3. **豁免留痕**：第 2 段的自举 Issue 必须在描述中声明「本 Issue 是 P0 自举，第 1 段基础设施已完成，本 Issue 起遵循 issue-first」。

### §0.2 偏差处置原则（根因 R4 的通用化）

**偏差就地修正，不积累「延后偿还」清单。** P0 执行中发现的任何「文档说 A、代码做 B」或「门禁本应强制却放宽」的差异，必须在发现的当处直接修正文档或配置，不得登记到独立的「技术债/偏离表」中延后处理——延后清单会沦为不可追踪、不可排序、最终被遗忘的散文。

极少数情况下若偏差无法立即修正（如依赖尚未建成的下游能力），必须在**发生处以显式注释**标注，注释须包含：

- **影响**：不修正会发生什么
- **检测信号**：可执行的命令或可观察状态（如 `git grep "..."` 应返回 0），不可是「人工核对」
- **修正条件**：何种前提满足后立即就地修正

根因分析（R1-R6，为何反复出现这些偏差）见附录 B，它是设计原理总结，不是「待偿还条目清单」。

### §0.3 设计借鉴来源（通用设计依据，唯一权威位置）

> 本表是借鉴来源的唯一权威位置。下列设计决策的「为什么」均回溯到此处，不在其他章节重复。

| 借鉴要素 | 借鉴来源 | 借鉴方式 | 是否修改 | 偏差原因 |
|---|---|---|---|---|
| 标签状态机三段门控 | github/spec-kit | bug-assess->bug-fix->bug-test 标签触发 | 修改 | 用 `do:*` 5 状态而非 bug 三段；命名走 `do:` 前缀 |
| Issue#=ADR 文件名 | open-gsd/gsd-core | 一 issue 一文档一 PR | 沿用 | — |
| 审批标签门禁 | open-gsd/gsd-core | "No code before approval"，无标签 PR 自动关 | 修改 | 用 CI status check + 标签白名单（`do:in-progress` / `do:review`）替代"无标签自动关" |
| AI 连续披露 | github/spec-kit | AI-assisted trailer + 反模式清单 | 修改 | 改 `Assisted-by:` → `AI-assisted:`（中性形式），加品牌词禁令（§2.1 + 附录 B §R1）|
| 一份规则多处软链 | zed-industries/zed | 单一规范源防多 AI 漂移 | 修改 | 用 AGENTS.md 为源，CLAUDE.md / GEMINI.md 软链；未引入 `.rules` 文件 |
| Rules Hygiene | zed-industries/zed | 规则变更流程（补种子缺的演进机制）| 沿用 | §4.9 已定义三门槛 + no drive-by |
| 验收命令即门禁 | ultraworkers/claw-code | 可重放命令作为硬检查 | 沿用 | §2.5 AC 格式 |
| out-of-scope 留档 | open-gsd/gsd-core | 拒绝提案入库防重提 | 修改 | 用 `close --reason "not planned"` 替代"入库防重提" |

---

## 1. 现状与目标

### 现状

> **实例化要求**：本节的事实陈述（org 是否存在、repo 是否存在、Issue Types 是否存在、Milestone 数量、标签数量、Projects v2 状态、token scopes）**必须以执行前实测为准**（`gh api` 查询），项目文档登记实测结果。下表是模板，项目文档填入实测值。

| 对象 | 模板问题 | 对 §4 的影响 |
|---|---|---|
| `${ORG}` 组织 | 是否已存在？计划？ | §3.3 是否可跳过 |
| `${ORG}/${REPO}` 仓库 | 是否已存在？空仓库？admin？ | §4.2 用 `git remote add` 还是 `gh repo create` |
| Issue Types | `${ISSUE_TYPES}` 是否已存在？ | §4.3b 创建还是仅验证 |
| Milestones | 现有数量 | §4.3c 创建 P0 Milestone（1 个） |
| 标签 | 现有标签 | §4.3 需创建 `${LABEL_COUNT}` 个 |
| Projects v2 | `${PROJECT_NAME}` 是否存在？Status 选项？ | §2.2.5 映射是否匹配 |
| 当前 token scopes | 是否满足 §3.2 要求 | §3.2 全部检查能否通过 |

### P0 目标

建立 issue-first 开发基础设施，使 AI 能在门禁约束下全自动推进项目：
1. git 仓库初始化 + 推送至 `${ORG}/${REPO}`（`${REPO_VISIBILITY}`）
2. 治理元数据体系（`${LABEL_COUNT}` 标签 + Issue Types + 1 个 P0 Milestone）+ Issue/PR 模板 + CODEOWNERS + 分支保护
3. AGENTS.md（AI 开发指引 + 反模式清单）
4. CI 门禁（issue-triage 自动打标 + pr-gates 双重检查）
5. 自动化流程：owner Issue 主流程 + 第三方 Issue 分诊采纳流程
6. **门禁有效性实证**：通过自举 PR 证明 pr-gates 两个 check 真实可通过（见 §0 Issue-First 豁免声明）

---

## 2. 治理制度设计

### 2.1 Issue 标题前缀规范

格式：`<type>(<scope>): <subject>`

> **原生优先决策**：`type` 的权威存储是 GitHub 原生 **Issue Type**（非标签）。标题前缀是 CI 解析 type 并自动赋值 Issue Type 的输入源，同时为人类提供可读性。`scope` 无原生替代，仍由 CI 从标题解析为 `scope:*` 标签。

**类型枚举**（与 Issue Type 一一对应；`${ISSUE_TYPES}` 实例化）：

| 标题前缀 | Issue Type | 含义 | 示例 |
|---|---|---|---|
| `feat` | Feature | 新功能/新能力 | `feat(${SCOPE}): ...` |
| `fix` | Bug | 缺陷修复 | `fix(${SCOPE}): ...` |
| `docs` | Documentation | 文档 | `docs(${SCOPE}): ...` |
| `refactor` | Refactor | 重构（无行为变化） | `refactor(${SCOPE}): ...` |
| `gov` | Change | 治理/流程/CI 变更 | `gov(governance): ...` |
| `decision` | Decision | 架构决策（ADR） | `decision(${SCOPE}): ...` |
| `chore` | Task | 维护/依赖/工具 | `chore(deps): ...` |

> 第三方 Issue 无前缀，CI 赋 Issue Type `Intake`。
>
> **品牌词禁令（§2.1 核心约束）**：commit message、PR body、AI-assisted trailer **任何位置**不得出现 AI 模型品牌名（Claude / GLM / GPT / Gemini / Llama / Mistral / Qwen / DeepSeek / Anthropic / OpenAI 等）。AI 身份只通过 `AI-assisted: autonomous|supervised` trailer 表达「是否 AI 参与」，**禁止列品牌名、版本号、能力等级**。此禁令由 `ai-disclosure` job 逐 commit 强制（§4.8）。（根因 R1 的来源，详见附录 B §R1）

### 2.2 治理元数据体系

> 本节的 G0-G4 是治理门禁，统一称为 `GOV-G0`…`GOV-G4`，不等同于 `GATE-P0-EXIT`。
>
> **与项目业务命令面的关系**：本节状态机标签（`do:*` / `state:blocked`）是 P0 治理域的**自治约定**，与项目业务 CLI 无关。业务 CLI 不读这些标签；这些标签仅在 GitHub Issue 自动化（CI workflows）和维护者工作流（`gh issue edit`）中使用。

#### 2.2.1 状态机（标签）

```
  [新建 Issue]
      │
      ▼
  do:triage ──DoR通过──▶ do:ready ──AI领取──▶ do:in-progress ──开PR──▶ do:review
      │                      │                     │                       │
      │ 拒绝                  │ 阻塞                 │ 需改                  │ 审核+验收通过
      ▼                      ▼                     ▼                       ▼
  close:                state:blocked ◀──── do:in-progress            do:acceptance
  not planned                                               │            │
                                                             │ 验收失败     │ merge
                               state:blocked ◀─────────────────┘            │
                                                                           ▼
                                                                    close: completed
```

> **原生优先决策**：终态 `accepted`/`rejected` 改用 GitHub 原生 close reason（`completed` / `not planned`），不再使用 `state:accepted`/`state:rejected` 标签。`state:blocked` 保留为标签，因为 blocked Issue 仍处于 open 状态，close reason 不适用。`do:*` 状态机保留为标签，因为 `gh issue edit --add-label` / `gh issue list --label` 的 CLI 简单性优于 Projects v2 Status 字段操作（详见 §2.2.5）。

**状态转换矩阵**（解决根因 R3：状态空间双轨易混）：

| 当前状态 | 触发条件 | 动作 | 下一状态 | close reason |
|---|---|---|---|---|
| (新建) | gh issue create / issue-triage 自动 | 加 `do:triage` | `do:triage` | — |
| `do:triage` | DoR 通过 + 用户确认 | 移除 `do:triage` 加 `do:ready` | `do:ready` | — |
| `do:triage` | 拒绝（不通过 DoR） | `gh issue close --reason "not planned"` | (close) | `not planned` |
| `do:ready` | AI 领取（自检 DoR 后） | 加 assignee、移除 `do:ready` 加 `do:in-progress` | `do:in-progress` | — |
| `do:in-progress` | 用户拒绝开 PR 或代码不合规 | 加 `state:blocked`、移除 `do:in-progress` | `state:blocked` | — |
| `do:in-progress` | `gh pr create`（自动） | 移除 `do:in-progress` 加 `do:review` | `do:review` | — |
| `do:review` | 用户审核通过 | 加 `do:acceptance` | `do:acceptance` | — |
| `do:review` | 用户拒绝 / 需改 | 移除 `do:review` 加 `do:in-progress` | `do:in-progress` | — |
| `do:acceptance` | AI 跑 AC 通过 + `gh pr ready` | `gh pr merge --squash --delete-branch` + `gh issue close --reason completed` | (close) | `completed` |
| `state:blocked` | 阻塞解除（补 DoR 证据等） | 移除 `state:blocked` 加 `do:ready` | `do:ready` | — |
| `state:blocked` | 决定不做了 | `gh issue close --reason "not planned"` | (close) | `not planned` |

**强约束**：只有 `do:acceptance` 状态才能用 `close --reason completed`；其他状态 close 必须用 `not planned`。这条规则**没有 CI 强制**，依赖 §2.4.1 step 8 工作流纪律（自律性约束）；违反该约束属执行偏差，须在发现处就地修正（见 §0.2）。

#### 2.2.2 标签体系

> **原生优先决策**：能用 GitHub 原生功能替代的标签一律删除（type→Issue Types、phase→Milestones、终态→close reason）。保留的标签均为无原生替代或原生功能 CLI 支持不足的场景。

| 类别 | 标签 | 色值 | 用途 | 保留理由 |
|---|---|---|---|---|
| 状态机 | `do:triage` | FBCA04 | 新建待分诊 | CLI 可过滤；Projects v2 Status 字段操作更复杂 |
| | `do:ready` | 0E8A16 | DoR 通过，可领取 | 同上 |
| | `do:in-progress` | 1D76DB | 开发中 | 同上 |
| | `do:review` | 5319E7 | PR 已开，待审核 | 同上 |
| | `do:acceptance` | 004773 | 审核通过，待验收 | 同上 |
| | `state:blocked` | D93F0B | 阻塞（Issue 仍 open） | close reason 不适用于 open Issue |
| 来源 | `origin:owner` | 0052CC | 所有者创建（**自动化触发条件**） | CLI 可过滤；author 字段不可与其他 label 组合查询 |
| | `origin:external` | 57606A | 第三方创建 | 同上 |
| 范围 | `scope:${each of ${SCOPES}}` | E4E669 | 各通用范围（infra/ci/cli/data/docs/governance 等） | 无原生替代 |
| 优先级 | `priority:blocker` | B60205 | 紧急/阻塞 | Issue 模板下拉可设；Projects v2 Priority 字段无法在模板中设置 |
| | `priority:high` | D93F0B | 高 | 同上 |
| | `priority:medium` | FBCA04 | 中 | 同上 |
| | `priority:low` | 0E8A16 | 低 | 同上 |

> 项目文档登记最终的 `${LABEL_COUNT}` 与完整标签清单（含具体 scope 集合）。项目特定的 scope（如规格修订 scope）由项目扩展追加，不属于通用 P0。

#### 2.2.3 Issue Types（组织级）

Issue Type 是**组织级**配置（无硬上限；GraphQL 分页 `first` 上限 100，按需可建），仓库继承可见。CI 在 Issue 创建时根据标题前缀自动赋值（第三方 Issue 赋 `Intake`）。

赋值通过 GraphQL `updateIssueIssueType` mutation 实现（input：`issueId!` + `issueTypeId`）。REST 的 issue create/update 不支持写入 type，`gh issue create` 也无 `--type` flag。

> **API 暴露注意**（通用技术事实）：Issue Type **仅 GraphQL `updateIssueIssueType` mutation 可写**；REST 端点写入不支持。REST 读 Issue Type 时 `issue.type.name` 字段长期为 `null`，必须走 GraphQL `repository.issue.issueType.name`。本模板的 issue-triage.yml 与 AC-P0-07b 均走 GraphQL。

`${ISSUE_TYPES}` 实例化具体映射；第三方 Issue 统一赋 `Intake`。

> 若项目启用里程碑验收认证，可保留额外 Issue Type `Acceptance`（配合 Projects v2 的认证字段），**不参与**日常开发 Issue 的 type 分类。其他项目特定 Issue Type（如规格修订类）由项目扩展追加。

#### 2.2.4 Milestones（原生）

替代 `phase:*` 标签。`gh` CLI 完整支持创建、赋值（`gh issue create --milestone`）和过滤。

标题**不含逗号**：`gh` 多处按逗号分割列表参数，含逗号的名称在批量场景易被误切分。

**P0 只创建一个 Milestone**：`P0 GitHub Initialization`。这是通用 P0 的唯一 Milestone——P0 自指，任何项目都一样。项目的后续阶段（P1、P2…）由项目规划文档定义，在 P0 之后的规划阶段各自创建为 Milestone；通用 P0 不预设也不创建它们。

#### 2.2.5 Projects v2 同步（可选增强）

仅当 `${PROJECTS_V2_ENABLED}=true` 时启用。`do:*` / `state:blocked` 标签保留用于 CLI 自动化，CI 在切换标签时同步更新 Projects v2 `Status` 字段，供看板可视化。

| 标签 / 事件 | Projects v2 Status 选项 |
|---|---|
| `do:triage` | Triage |
| `do:ready` | Ready |
| `do:in-progress` | In progress |
| `do:review` | In review |
| `do:acceptance` | Acceptance |
| `state:blocked` | Blocked |
| close `completed` | Done |
| close `not planned` | Not planned |

> 项目文档须验证 project 现有 `Status` 选项与上表**完全匹配**；不匹配则需先在 project 中手工补齐选项。

**`priority:*` 同步**：project 的 `Priority` 字段若为 SINGLE_SELECT 且**选项为空**，同步会因找不到 option 而失败。在用户手工添加 blocker/high/medium/low 四个选项之前，**不要**在 `label-sync.yml` 中加入 `priority` 分支——找不到 option 会让每次标签变更都产生一条 warning 噪音。

> **权限前提（必读，通用技术约束）**：Projects v2 位于组织级别，**GitHub Actions 的 `GITHUB_TOKEN` 无任何 permissions 键可授予 org-level project 写权限**（`permissions:` 合法键中不存在 `organization`）。因此 `label-sync.yml` **必须**使用 PAT：
>
> 1. 创建 classic PAT，勾选 `project`（读写组织 project）与 `repo`
> 2. 存为仓库 secret：`gh secret set PROJECTS_TOKEN -R ${ORG}/${REPO}`
> 3. workflow 中通过 `github-token: ${{ secrets.PROJECTS_TOKEN }}` 传入
>
> 未配置 `PROJECTS_TOKEN` 时，`label-sync.yml` 必须**记录 warning 并跳过，不阻塞主流程**（标签是权威源，Projects v2 仅为展示镜像）。此「缺 token 时跳过而非报错」是硬性实现要求（根因 R5 的实证修复，详见附录 B §R5）。

### 2.3 治理门禁分层（GOV-G0～GOV-G4）

| 层 | 名称 | 时机 | 检查内容 | 执行方 |
|---|---|---|---|---|
| GOV-G0 | Session | AI 会话启动 | 读 AGENTS.md + 确认 origin:owner | AI 本地自检 |
| GOV-G1 | Admission | Issue 创建时 | 自动打 origin 标签 + 赋 Issue Type + 解析标题打 scope 标签 + 同步 Projects v2 | CI `issue-triage.yml` |
| GOV-G2 | DoR | Issue 分诊时 | 标题前缀合法 + AC 已定义 + 关联文档引用已填 + scope 有效 | AI 检查并评论 DoR 结论；**用户确认后** AI 执行 `do:ready` 标签切换 |
| GOV-G3 | PR/CI | PR 提交时 | ai-disclosure 通过（PR body 披露 **且每个 commit 带 trailer**）+ dor-check 通过 | CI `pr-gates.yml`（required status checks） |
| GOV-G4 | Acceptance | merge 前 | AC 命令全部通过 + `do:acceptance` 标签 | AI 运行 AC + 用户确认 merge |

### 2.4 自动化流程

#### 2.4.1 Owner Issue 主流程（所有者创建的 Issue）

```
1. 所有者创建 Issue（填模板，标题带前缀）
       │
2. [GOV-G1] CI 自动处理：打 origin:owner + do:triage + scope:* 标签 + 赋 Issue Type + 同步 Projects v2
       │
3. [GOV-G0+GOV-G2] AI 分诊 + 用户确认 Ready：
   - AI 检查 DoR（标题前缀、AC、关联文档引用），在 Issue 评论中给出分诊结论
   - 通过 -> 等用户回复确认后：
     gh issue edit <N> --remove-label "do:triage" --add-label "do:ready"
   - 不通过 -> 评论缺失项，打 state:blocked 并移除 do:triage
   - **注意**：AI 不得自行将 Issue 从 do:triage 切换到 do:ready（G2 门禁：Ready 转换需用户确认）
       │
4. [REMOTE-AUTO] AI 领取 do:ready Issue：
   gh issue edit <N> --add-assignee "@me"
   git checkout -b <type>/<N>-<slug>
   gh issue edit <N> --remove-label "do:ready" --add-label "do:in-progress"
   TDD 开发（写测试 -> 实现 -> 验证）
       │
5. [LOCAL-AUTO+REMOTE-AUTO] AI 自审 + 开 draft PR：
   - 运行所有 AC 命令，收集输出证据
   - git commit（带 AI-assisted trailer，不含品牌名）
   - git push -u origin <branch>
   - gh pr create --draft --title "<type>(<scope>): <subject> (#<N>)" --body "..."
   - gh issue edit <N> --remove-label "do:in-progress" --add-label "do:review"
   - **注意**：PR 创建瞬间 Issue 仍是 do:in-progress，因此 dor-check 白名单
     必须包含 do:in-progress（见 §4.8 pr-gates.yml）。标签切换不能提前到
     pr create 之前，否则 do:review 会在 PR 尚不存在时生效。
       │
6. [MANUAL-REVIEW] 用户审核 PR：
   - 通过 -> gh issue edit <N> --add-label "do:acceptance"
   - 需改 -> PR 评论反馈，AI 修复后 re-push（回到 step 5）
       │
7. [GOV-G4] AI 验收：
   - 重跑所有 AC 命令
   - 全通过 -> gh pr ready <PR#>（取消 draft），在 PR body 中贴 AC 证据
   - 失败 -> 评论失败项，回 do:in-progress
       │
8. [MANUAL-REVIEW] 用户 merge（注意 <PR#> 与 Issue <N> 是不同编号）：
   gh pr merge <PR#> --squash --delete-branch
   gh issue close <N> --reason completed
```

#### 2.4.2 第三方 Issue 分诊与采纳流程

```
1. 第三方用户创建 Issue
       │
2. [GOV-G1] CI 自动处理：打 origin:external + do:triage 标签 + 赋 Issue Type: Intake
   + 自动评论分诊通知（告知等待 AI 分析）
       │
3. [LOCAL-AUTO] AI 只读分析（不开发、不开分支）：
   - 读取 Issue 内容
   - 推断 type + scope（从标题或内容）
   - gh issue list --search "..." 检查重复
   - 生成结构化分诊评论：
     ## 分诊分析
     - 摘要：<issue 内容摘要>
     - 推断 Issue Type：Feature/Bug/Task/...
     - 推断范围：scope:xxx
     - 重复检查：无重复 / 重复 #NNN
     - 可行性评估：<评估>
     - 建议：adopt / reject / needs-clarification
     - 建议 Issue 标题：<proposed title>
     - 建议优先级：priority:blocker|high|medium|low
     - 理由：<reasoning>
       │
4. [MANUAL-REVIEW] 用户决定：
   │
   ├─ a) 采纳 -> 评论 "adopting"
   │   [REMOTE-AUTO] AI 创建新 Issue（作者=所有者 -> origin:owner）：
   │     gh issue create \
   │       --title "<proposed title>" \
   │       --body "采纳自 #<原#>\n\n<原始内容摘要>\n\n原始 Issue: #<原#>" \
   │       --label "do:ready,scope:xxx,priority:xxx"
   │   [REMOTE-AUTO] CI 自动补打 origin:owner + 赋 Issue Type
   │   [REMOTE-AUTO] AI 关闭原 Issue：
   │     gh issue close <原#> --comment "采纳 via #<新#>，本 Issue 关闭。后续开发在新 Issue 推进。" --reason "not planned"
   │   -> 新 Issue 进入 owner 主流程 step 4
   │
   ├─ b) 拒绝 -> 评论理由
   │   [REMOTE-AUTO] AI 执行：
   │     gh issue edit <原#> --remove-label "do:triage"
   │     gh issue close <原#> --reason "not planned" --comment "拒绝理由：..."
   │
   └─ c) 需澄清 -> 评论请求补充
       [REMOTE-AUTO] AI 执行：
         gh issue edit <原#> --add-label "state:blocked" --remove-label "do:triage"
         评论："请补充以下信息：..."
```

#### 2.4.3 AI 会话启动检查清单（G0 Session Gate）

AI 每次会话启动时必须执行：

1. 读取 `AGENTS.md`（本仓库根目录）
2. `gh auth status` 确认已认证为 `${OWNER_LOGIN}`
3. 查询可领取的 Issue：
   `gh issue list --label "origin:owner" --label "do:ready" --state open`
4. 若无 `do:ready` Issue，查询 `do:triage` + `origin:owner` 进行分诊
5. 若有 `origin:external` + `do:triage` Issue（Issue Type 为 Intake），进行只读分诊分析

> 项目特定扩展（如读取规格地图卷、运行规格校验脚本）由项目文档在 AGENTS.md 的 G0 中追加，不属于通用 P0。

### 2.5 验收设计要求

验收（Acceptance）是 GOV-G4 门禁的依据。AC（Acceptance Criteria，验收标准）的设计必须满足以下要求——这些是通用设计约束，适用于本模板定义的全部 `AC-*` 验收项：

```text
AC-<stable-id>
command: <exact executable command>
exit code: <integer, 仅在实际执行后填写>
assert: <observable assertion>
# 或
golden: <repository path>
evidence: <CI artifact / test output / command output>
```

**可执行性**：每条 AC 必须包含一条可在干净环境中原样执行的 `command`，不得含占位符。`<N>` / `<repo-root>` 等必须在实例化时绑定，或用命令组合解析（如 `N=$(gh issue list ... --jq '.[0].number')`）。

**可观察性**：`assert` 必须是可观察的输出断言（输出值、退出码、文件存在性、字符串包含、计数相等），不得是「测试通过」「行为正确」这类无锚点断言。`golden` 指向仓库内固定路径的期望输出文件，可逐字节或语义比对；`assert` 与 `golden` 二选一或并存。

**证据性**：`evidence` 必须是可点击/可复跑的锚点（CI 运行链接、命令输出粘贴、golden 路径）。聊天记录、口头确认、模型声明不是证据。

**退出码诚实性**：`exit code` 只在命令**实际执行后**填写真实整数。尚未执行时**省略 `exit code:` 行**并写 `evidence: planned`。未执行的 AC 不得标记为已验收。这是「命令未实际执行不得填退出码」的字面与精神合规（不是省略责任字段，而是诚实标注未执行）。

**进度三态**：任何阶段性工作只允许标注为以下三态之一：

- **已验收**：有可复核的完整验证证据（command + exit code + output/golden）。
- **做了未验收**：文件或实现存在，但验证证据不完整。
- **只是计划**：只有文档描述，无实现。

不得用单一「完成」标记掩盖细粒度差异；不得把「做了未验收」写成「已验收」。

**N/A 显式**：`N/A` 必须显式解释原因，不得静默省略。

**验收即门禁**：AC 命令本身即门禁——同一条命令在 CI（GOV-G3）与本地（GOV-G4）中原样重放，结果一致才通过。不得为通过验收而弱化断言、空化 golden 或放宽 `assert`。`assert` 一旦写入即视为合同，验收阶段不得反向修改 `assert` 以适配实际输出（实际输出不符应修代码，而非改 `assert`）。

**模板 AC 与实例 AC 的区别**：本模板 §5 的 `AC-P0-*` 是参数化合同（含 `${VAR}`，`evidence` 永远 `planned`）；项目执行时用绑定值替换 `${VAR}` 得到可原样执行命令，执行后回填真实 `exit code` 与 `evidence`。

---

## 3. 前置手动步骤 [MANUAL-AUTH]

### 3.1 安装 gh CLI（若未安装）

```bash
# Ubuntu/Debian
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y

# 验证
gh --version
```

### 3.2 认证

#### 方式 A：浏览器交互（推荐）

```bash
gh auth login
# 选择：GitHub.com -> HTTPS -> Yes (git credentials) -> Login with a web browser
# 复制 one-time code，在浏览器中粘贴授权
```

#### 方式 B：手动创建 Token

需要的 scopes（通用要求）：
- `repo`（仓库读写 + 分支保护）
- `workflow`（读写 .github/workflows/）
- `read:org`（读组织信息；Free 组织够用）
- 若 `${PROJECTS_V2_ENABLED}=true`：额外 `project`（读写组织 Projects v2）

```bash
# 在当前终端会话中设置（关闭终端后失效，不会持久化到磁盘）
export GH_TOKEN=<your_token>

# 验证认证状态和 scope
gh auth status
gh api user --jq .login   # 期望输出 ${OWNER_LOGIN}
```

**Token 权限验证脚本**（手动执行：`bash verify_github_token.sh`；兼容方式 A 与方式 B）：

> **实例化要求**：脚本中的 `OWNER`、scopes 列表须按 `${OWNER_LOGIN}` 与项目所需 scopes 实例化。下方是模板逻辑骨架。

```bash
#!/bin/bash
# verify_github_token.sh — 验证 GitHub 认证与权限是否满足 P0 执行要求
# 兼容方式 A（gh auth login 浏览器授权）与方式 B（GH_TOKEN 环境变量）
set -euo pipefail

OWNER="${OWNER_LOGIN}"   # 实例化：替换为 ${OWNER_LOGIN}

echo "=== 1. 认证状态 ==="
gh auth status || { echo "FAIL: 未认证"; exit 1; }

echo "=== 2. 用户身份 ==="
LOGIN=$(gh api user --jq .login)
[ "$LOGIN" = "$OWNER" ] || { echo "FAIL: 登录身份 $LOGIN != $OWNER"; exit 1; }
echo "OK: $LOGIN"

echo "=== 3. Token scopes ==="
SCOPES=$(gh api user --jq '.headers' 2>/dev/null || gh auth status 2>&1)
# 精确匹配 scopes（避免 repo 被 public_proxy/read:org 子串误命中，见根因 R5）
# 实例化：按项目所需 scopes 逐项校验

echo "=== 4. 组织访问 ==="
gh api orgs/${ORG} --jq .login >/dev/null && echo "OK: ${ORG}" || echo "WARN: 组织不可访问"

echo "=== 5. 仓库 admin 权限（分支保护必需）==="
PERM=$(gh api repos/${ORG}/${REPO} --jq '.permissions.admin' 2>/dev/null || echo "false")
[ "$PERM" = "true" ] && echo "OK: admin" || echo "WARN: 非 admin（分支保护可能受限）"

echo "=== 6. Issue Types 可读 ==="
COUNT=$(gh api repos/${ORG}/${REPO}/issue-types --jq 'length' 2>/dev/null || echo "0")
echo "Issue Types 数量: $COUNT"

echo "全部验证通过"
```

> **根因 R5 的通用教训（附录 B §R5）**：权限验证脚本中的 scope 匹配必须**精确**（逐项集合比对），不得用子串匹配（`repo` 会被 `public_repo` / `read:org` 的字符包含关系误命中）。bash 数组从命令替换读取时元素可能带前导空格，必须在 `read` 前 `tr -d ' '` 清理，否则 `has_scope()` 误判。这类「单看不致命、叠加后 AC 验证不可信」的脚本陷阱是 R5 的核心。

### 3.3 创建组织（若尚未创建）

> 若 `${ORG}` 已存在，跳过本节。项目文档登记实测结果。

### 3.4 环境验证

```bash
git --version
gh --version
gh auth status
gh api user --jq .login    # 期望 ${OWNER_LOGIN}
```

---

## 4. 自动初始化执行 [LOCAL-AUTO + REMOTE-AUTO]

### 4.1 git init + .gitignore

```bash
git init -b main
```

`.gitignore` 模板（项目文档按项目技术栈增删）：

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# 环境与密钥
.env
.env.*
*.key

# 系统
.DS_Store
```

### 4.2 首次提交 + 关联远程仓库

```bash
git add -A
git commit -m "chore(infra): 初始化仓库

- 治理基础设施（按 GITHUB-INIT.md 模板）

AI-assisted: supervised"
```

关联远程仓库（按 `${REPO_PREEXISTS}` 分支）：

```bash
# 若 ${REPO_PREEXISTS}=true（仓库已存在）：
git remote add origin https://github.com/${ORG}/${REPO}.git
git push -u origin main

# 若 ${REPO_PREEXISTS}=false（仓库不存在）：
gh repo create ${ORG}/${REPO} --${REPO_VISIBILITY} --source=. --remote=origin --push

# 验证
gh repo view ${ORG}/${REPO} --json url --jq .url
```

### 4.3 创建标签体系

```bash
# ============ 状态机标签（6 个）============
gh label create "do:triage"      --color FBCA04 --description "新建待分诊"      -R ${ORG}/${REPO}
gh label create "do:ready"       --color 0E8A16 --description "DoR 通过，可领取"  -R ${ORG}/${REPO}
gh label create "do:in-progress" --color 1D76DB --description "开发中"          -R ${ORG}/${REPO}
gh label create "do:review"      --color 5319E7 --description "PR 已开，待审核"   -R ${ORG}/${REPO}
gh label create "do:acceptance"  --color 004773 --description "审核通过，待验收"   -R ${ORG}/${REPO}
gh label create "state:blocked"  --color D93F0B --description "阻塞（Issue 仍 open）" -R ${ORG}/${REPO}

# ============ 来源标签（2 个，自动化触发依据）============
gh label create "origin:owner"    --color 0052CC --description "所有者创建" -R ${ORG}/${REPO}
gh label create "origin:external" --color 57606A --description "第三方创建" -R ${ORG}/${REPO}

# ============ 范围标签（无原生替代）============
# 通用 scope（实例化：遍历 ${SCOPES}）
for s in ${SCOPES}; do
  gh label create "scope:$s" --color E4E669 --description "$s 范围" -R ${ORG}/${REPO}
done

# ============ 优先级标签（4 个）============
gh label create "priority:blocker" --color B60205 --description "紧急/阻塞" -R ${ORG}/${REPO}
gh label create "priority:high"    --color D93F0B --description "高"       -R ${ORG}/${REPO}
gh label create "priority:medium"  --color FBCA04 --description "中"       -R ${ORG}/${REPO}
gh label create "priority:low"     --color 0E8A16 --description "低"       -R ${ORG}/${REPO}

# 验证
gh label list -R ${ORG}/${REPO} --limit 100 --json name --jq '[.[].name]|map(select(test("^(do|state|origin|scope|priority):")))|length'
# 期望输出 ${LABEL_COUNT}
```

> **已删除标签及替代方案**（原生优先决策的记录，供实例参考）：`type:*`(8)→Issue Types；`phase:*`→Milestones；`state:accepted/rejected`(2)→close reason；`origin:adopted`→Issue body；`needs-adoption`→Issue Type `Intake`；`ac-met`→PR body AC 证据。

### 4.3b 验证 / 创建 Issue Types（组织级）

```bash
# 验证（REST 仓库级端点可读，继承自组织）
gh api repos/${ORG}/${REPO}/issue-types --jq '.[].name'
# 期望包含 ${ISSUE_TYPES} 的全部 type 名

# 计数
gh api repos/${ORG}/${REPO}/issue-types --jq 'length'
```

> 若 `${ISSUE_TYPES_PREEXIST}=false`（缺失），需通过 GraphQL 在组织级创建。创建 Issue Type 是组织级 mutation（`createIssueType`），需组织 node_id。项目文档登记具体创建命令。`updateIssueIssueType` 写入只能走 GraphQL（见 §2.2.3 API 注意）。

### 4.3c 创建 P0 Milestone（原生）

```bash
# 通用 P0 只创建一个 Milestone：P0 GitHub Initialization（自指，见 §2.2.4）。
# 项目的 P1+ Milestone 不在此创建——由项目规划文档定义并在 P0 之后各自创建。
gh api repos/${ORG}/${REPO}/milestones -f title="P0 GitHub Initialization" -f state=open

# 验证
gh api repos/${ORG}/${REPO}/milestones --jq 'length'
# 期望输出 1
```

### 4.4 自举流程（§4.4 起不再豁免 issue-first）

> **关键时序**：第 1 段（§4.1~§4.3c）在 main 上直推；从 §4.4 起，治理文件必须通过它们自己定义的 PR 流程合入。标签在第 1 段末已就绪，故 Issue 能力此刻已具备。

```bash
# 步骤 1：创建自举 Issue（此时 CI 尚未部署，标签需手工指定）
gh issue create -R ${ORG}/${REPO} \
  --title "gov(governance): 初始化 issue-first 治理基础设施" \
  --milestone "P0 GitHub Initialization" \
  --label "do:triage,priority:blocker,scope:governance" \
  --body "## 目标
按 GITHUB-INIT.md 通用模板初始化 issue-first 治理基础设施。

## 范围
Issue/PR 模板、CODEOWNERS、CI workflows、AGENTS.md、分支保护配置。

## 说明
本 Issue 是 P0 自举，第 1 段基础设施已完成，本 Issue 起遵循 issue-first。

## 验收标准
见 GITHUB-INIT.md §5 的 AC-P0-04 / AC-P0-06 / AC-P0-08。"
# 记下 Issue 号，下称 <N>

# 步骤 2：手工设置 Issue Type 为 Change（CI 尚未部署）
# 用 GraphQL（REST 不支持写入 Issue Type，见 §2.2.3）

# 步骤 3：开分支
git checkout -b gov/<N>-governance-bootstrap

# 步骤 4：完成 §4.5 - §4.10 的所有文件编写，然后提交
#         （commit 命令见 §4.11）

# 步骤 5：推送并开 PR
git push -u origin gov/<N>-governance-bootstrap
gh pr create --draft \
  --title "gov(governance): 初始化 issue-first 治理基础设施 (#<N>)" \
  --body "Closes #<N>

## AI 披露
- [x] 本 PR 包含 AI 辅助生成的代码
- [x] 所有 commit 包含 AI-assisted: trailer
- [x] 未出现 AI 模型品牌名

## 验收标准
- [ ] AC-P0-04 治理文件齐全
- [ ] AC-P0-06 分支保护配置
- [ ] AC-P0-08 pr-gates 双 check 全绿" \
  --base main
gh issue edit <N> --remove-label "do:in-progress" --add-label "do:review"

# 步骤 6：观察 pr-gates 两个 check（这是门禁有效性的第一份真实证据）
gh pr checks --watch
```

### 4.5 创建 Issue 模板

创建 `.github/ISSUE_TEMPLATE/config.yml`：

```yaml
blank_issues_enabled: false
contact_links:
  - name: 讨论与提问
    url: ${DISCUSSIONS_URL}
    about: 问答与讨论请使用 Discussions，Issue 仅用于可追踪的变更
```

> **实例化要求**：以下每个 type 模板的 `scope` dropdown 的 options 须按 `${SCOPES}` 实例化；`doc_ref` 字段的 placeholder 按项目文档锚点格式自定义。下方给出 `feature.yml` 全文作模板，其余 type 同构。

创建 `.github/ISSUE_TEMPLATE/feature.yml`：

```yaml
name: "功能需求"
description: 提出新功能或能力
labels: ["do:triage"]
title: "feat(scope): "
body:
  - type: dropdown
    id: scope
    attributes:
      label: 影响范围
      description: 选择受影响的模块或范围
      options:
        # 实例化：按 ${SCOPES} 填写项目通用 scope
        - infra (基础设施)
        - ci (CI/CD)
        - cli (CLI 命令)
        - data (数据管线)
        - docs (文档系统)
        - governance (治理系统)
    validations:
      required: true
  - type: input
    id: doc_ref
    attributes:
      label: 关联文档
      description: 关联的设计/规格文档与章节（项目按需自定义锚点格式）
      placeholder: <doc-anchor> §section
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: 需求描述
      description: 要做什么、为什么、预期效果
    validations:
      required: true
  - type: textarea
    id: ac
    attributes:
      label: 验收标准（AC）
      description: |
        每条 AC 必须包含可原样执行的命令与可观察断言。
        未执行时省略 exit code 行，写 evidence: planned；执行后再填真实退出码。
    validations:
      required: true
  - type: dropdown
    id: priority
    attributes:
      label: 优先级
      options: ["priority:blocker", "priority:high", "priority:medium", "priority:low"]
    validations:
      required: true
```

> 其余 type 模板（`bug.yml` / `governance.yml` / `decision.yml` / `chore.yml` / `refactor.yml`）与 `feature.yml` 同构：改 `title` 前缀、`name`、`description`，body 结构一致（scope + doc_ref + description + ac + priority）。
>
> 项目特定的 Issue 模板（如规格修订模板）由项目扩展追加，不属于通用 P0。

### 4.6 创建 PR 模板

创建 `.github/PULL_REQUEST_TEMPLATE.md`：

```markdown
## 关联 Issue

Closes #

## 变更说明

<!-- 简述改了什么、为什么 -->

## AI 披露

- [ ] 本 PR 包含 AI 辅助生成的代码
- [ ] 所有 commit 包含 `AI-assisted:` trailer
- [ ] 未在 commit / PR body 中出现 AI 模型品牌名（按 §2.1 品牌词禁令）

> AI 披露：<!-- 如 AI-assisted: autonomous -->
> 披露是**连续的**：每轮 review 新增的 commit 和回复也需声明 AI 参与。**禁止列品牌名、版本号、能力等级**（仅"是否 AI 参与"）。

## 验收标准（从关联 Issue 复制，逐条勾选并附证据）

<!--
AC-1
command: <command>
exit code: 0
assert: <assertion>
evidence: <粘贴命令输出或 CI 链接>
-->

- [ ] AC-1
- [ ] AC-2

## 自检清单

- [ ] 无 TODO/FIXME/TBD/XXX 残留
- [ ] 分支命名符合 `<type>/<issue#>-<slug>`
- [ ] 未混合其他 Issue 的变更
```

### 4.7 创建 CODEOWNERS

> **当前无强制力，保留为协作期占位**：单人开发期，唯一 owner 同时是唯一 PR 作者。GitHub 规定「Pull request authors cannot approve their own pull requests」，且 §4.12 设 `required_pull_request_reviews: null`，因此 CODEOWNERS 此刻**既不会触发评审请求、也无任何阻塞力**。保留它的理由：一旦引入协作者或将 review 要求打开，该文件立即生效，无需再补建。**不要**把它当作 P0 期间的有效门禁写进验收依据。

创建 `.github/CODEOWNERS`：

```
# ${REPO} CODEOWNERS
# 单人开发期：所有路径归属 ${OWNER_LOGIN}；当前无强制力（见 §4.7 说明）。
# 引入协作者后可按子系统拆分归属。

* @${OWNER_LOGIN}

# 治理配置（门禁/CI/模板，修改须通过 gov 类型 Issue）
.github/                    @${OWNER_LOGIN}
AGENTS.md                   @${OWNER_LOGIN}
```

### 4.8 创建 CI Workflows

#### 4.8a `.github/workflows/issue-triage.yml`（G1 自动打标 + 赋 Issue Type）

```yaml
name: issue-triage
on:
  issues:
    types: [opened]
jobs:
  auto-label:
    name: auto-label-and-type
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            // 实例化：OWNER 按项目所有者绑定
            const OWNER = '${OWNER_LOGIN}';
            // 实例化：VALID_SCOPES 按 ${SCOPES} 绑定
            const VALID_SCOPES = [${SCOPES_AS_JS_ARRAY}];

            const issue = context.payload.issue;
            const login = issue.user.login;
            const title = issue.title || '';
            const existingLabels = issue.labels.map(l => l.name);

            const labels = [];

            // --- 来源标签（自动化触发依据）---
            const isOwner = login === OWNER;
            if (isOwner) {
              labels.push('origin:owner');
            } else {
              labels.push('origin:external');
            }

            // --- Triage 标签（已 do:ready 的采纳 Issue 跳过）---
            const hasActiveState = existingLabels.some(l =>
              l === 'do:ready' || l === 'do:in-progress' || l === 'do:review'
            );
            if (!hasActiveState) {
              labels.push('do:triage');
            }

            // --- 从标题解析 scope ---
            const m = title.match(/^(feat|fix|docs|refactor|gov|decision|chore)\(([^)]+)\)/);
            let scopeResolved = false;
            if (m) {
              const scope = m[2].toLowerCase();
              if (VALID_SCOPES.includes(scope)) {
                labels.push('scope:' + scope);
                scopeResolved = true;
              }
            }

            // --- 打标签（空数组会导致 422，必须守卫）---
            if (labels.length) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                labels: labels
              });
            }

            // --- 赋 Issue Type（GraphQL，REST 不支持写入）---
            const titlePrefixToType = {
              feat: 'Feature',
              fix: 'Bug',
              docs: 'Documentation',
              refactor: 'Refactor',
              gov: 'Change',
              decision: 'Decision',
              chore: 'Task'
            };

            let targetTypeName = null;
            if (isOwner && m && titlePrefixToType[m[1]]) {
              targetTypeName = titlePrefixToType[m[1]];
            } else if (!isOwner) {
              targetTypeName = 'Intake';
            }

            if (targetTypeName) {
              try {
                const typeQuery = await github.graphql(`
                  query($owner: String!, $repo: String!) {
                    repository(owner: $owner, name: $repo) {
                      issueTypes(first: 20) {
                        nodes { id name }
                      }
                    }
                  }
                `, { owner: context.repo.owner, repo: context.repo.repo });

                const typeNode = typeQuery.repository.issueTypes.nodes
                  .find(t => t.name === targetTypeName);

                if (typeNode) {
                  const issueQuery = await github.graphql(`
                    query($owner: String!, $repo: String!, $number: Int!) {
                      repository(owner: $owner, name: $repo) {
                        issue(number: $number) { id }
                      }
                    }
                  `, { owner: context.repo.owner, repo: context.repo.repo, number: issue.number });

                  await github.graphql(`
                    mutation($issueId: ID!, $typeId: ID!) {
                      updateIssueIssueType(input: {issueId: $issueId, issueTypeId: $typeId}) {
                        issue { issueType { name } }
                      }
                    }
                  `, {
                    issueId: issueQuery.repository.issue.id,
                    typeId: typeNode.id
                  });

                  core.info(`Issue Type set to: ${targetTypeName}`);
                } else {
                  core.warning(`Issue Type "${targetTypeName}" not found in repo`);
                }
              } catch (e) {
                core.warning(`Failed to set Issue Type: ${e.message}`);
                // 非阻塞：标签已打，Issue Type 赋值失败不影响主流程
              }
            }

            // --- scope 未解析时提醒 ---
            if (isOwner && !scopeResolved) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                body: [
                  '⚠️ **未能从标题解析出有效 scope**，因此未打 `scope:*` 标签。',
                  '',
                  '常见原因：使用模板时未把预填的 `scope` 占位符替换为真实取值。',
                  '',
                  '请修改标题为 `<type>(<scope>): <subject>` 格式，DoR 检查（GOV-G2）会复核此项。'
                ].join('\n')
              });
            }

            // --- 第三方 Issue 分诊通知 ---
            if (!isOwner) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                body: [
                  '## 第三方提交分诊通知',
                  '',
                  '本 Issue 由非所有者提交，Issue Type 已设为 `Intake`。',
                  '',
                  '**AI 将进行只读分析**：',
                  '1. 推断类型与范围',
                  '2. 检查是否与现有 Issue 重复',
                  '3. 给出采纳/拒绝建议',
                  '',
                  '**所有者审核后**：',
                  '- **采纳** -> 创建新的 owner Issue 关联本 Issue，关闭本 Issue',
                  '- **拒绝** -> 关闭并标记为 not planned',
                  '- **需补充** -> 评论请求澄清',
                  '',
                  '> 在采纳决定前，本 Issue 不会触发任何自动化开发。'
                ].join('\n')
              });
            }
```

#### 4.8b `.github/workflows/label-sync.yml`（Projects v2 同步，可选）

> 仅 `${PROJECTS_V2_ENABLED}=true` 时创建。

```yaml
name: label-sync
on:
  issues:
    types: [labeled, unlabeled, closed, reopened]
jobs:
  sync-projects:
    name: sync-projects-v2
    runs-on: ubuntu-latest
    # 注意：permissions 中不存在 `organization` 键，GITHUB_TOKEN 也无法访问
    # org-level Projects v2。写权限只能由 PROJECTS_TOKEN（PAT，含 project scope）提供。
    permissions:
      issues: read
    steps:
      - uses: actions/github-script@v7
        env:
          PROJECT_NUMBER: ${PROJECT_NUMBER}
        with:
          # 必须使用 PAT；未配置时下方脚本会跳过并记录 warning
          github-token: ${{ secrets.PROJECTS_TOKEN }}
          script: |
            if (!process.env.PROJECT_NUMBER) return;
            const PROJECT_NUMBER = parseInt(process.env.PROJECT_NUMBER);
            const issue = context.payload.issue;
            const action = context.payload.action;
            const labelName = context.payload.label?.name;

            // 缺 PROJECTS_TOKEN 时整 job 跳过，不报错（根因 R5 实证修复）
            if (!secrets.PROJECTS_TOKEN) {
              core.warning('PROJECTS_TOKEN 未配置，跳过 Projects v2 同步');
              return;
            }

            // 标签 -> Projects v2 Status 选项映射
            const labelToStatus = {
              'do:triage': 'Triage',
              'do:ready': 'Ready',
              'do:in-progress': 'In progress',
              'do:review': 'In review',
              'do:acceptance': 'Acceptance',
              'state:blocked': 'Blocked'
            };

            const statusPriority = ['state:blocked', 'do:acceptance', 'do:review', 'do:in-progress', 'do:ready', 'do:triage'];

            let targetStatus = null;
            if (action === 'closed') {
              targetStatus = issue.state_reason === 'completed' ? 'Done' : 'Not planned';
            } else if (action === 'reopened') {
              targetStatus = 'Triage';
            } else if (action === 'labeled' && labelName && labelToStatus[labelName]) {
              targetStatus = labelToStatus[labelName];
            } else if (action === 'unlabeled') {
              const { data: currentIssue } = await github.rest.issues.get({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number
              });
              const currentLabels = currentIssue.labels.map(l => l.name);
              for (const lbl of statusPriority) {
                if (currentLabels.includes(lbl)) {
                  targetStatus = labelToStatus[lbl];
                  break;
                }
              }
              if (!targetStatus) targetStatus = 'Triage';
            }

            if (!targetStatus) return;

            try {
              const projQuery = await github.graphql(`
                query($org: String!, $num: Int!) {
                  organization(login: $org) {
                    projectV2(number: $num) {
                      id
                      fields(first: 20) {
                        nodes {
                          ... on ProjectV2SingleSelectField {
                            id
                            name
                            options { id name }
                          }
                        }
                      }
                    }
                  }
                }
              `, { org: context.repo.owner, num: PROJECT_NUMBER });

              const project = projQuery.organization.projectV2;
              const statusField = project.fields.nodes
                .find(f => f.name === 'Status');
              if (!statusField) {
                core.warning('Status field not found in project');
                return;
              }

              const statusOption = statusField.options
                .find(o => o.name === targetStatus);
              if (!statusOption) {
                core.warning(`Status option "${targetStatus}" not found. Available: ${statusField.options.map(o => o.name).join(', ')}`);
                return;
              }

              // addProjectV2ItemById 是幂等的：content 已在 project 中时返回既有 item
              const addMutation = await github.graphql(`
                mutation($projectId: ID!, $contentId: ID!) {
                  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                    item { id }
                  }
                }
              `, { projectId: project.id, contentId: issue.node_id });

              const itemId = addMutation.addProjectV2ItemById.item.id;

              await github.graphql(`
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
                  updateProjectV2ItemFieldValue(input: {
                    projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: {singleSelectOptionId: $optionId}
                  }) {
                    projectV2Item { id }
                  }
                }
              `, {
                projectId: project.id,
                itemId: itemId,
                fieldId: statusField.id,
                optionId: statusOption.id
              });

              core.info(`Projects v2 Status synced to: ${targetStatus}`);
            } catch (e) {
              core.warning(`Projects v2 sync failed: ${e.message}`);
              // 非阻塞：标签是权威源，同步失败不影响主流程
            }
```

> **实例化注意**：上方脚本中 `if (!secrets.PROJECTS_TOKEN)` 在 github-script 中 `secrets` 不可直接访问，需改用 env 注入 `${{ secrets.PROJECTS_TOKEN != '' }}` 作为 job-level `if:` 守卫，或在 step env 中传入后判断。项目文档须给出经验证的写法（根因 R5：缺失守卫会导致缺 token 时 job 直接 error 而非 warning 跳过）。推荐用 job 级 `if: ${{ secrets.PROJECTS_TOKEN != '' }}`。

#### 4.8c `.github/workflows/pr-gates.yml`（G3 双重检查）

```yaml
name: pr-gates
on:
  pull_request:
    types: [opened, edited, synchronize]
jobs:
  # --- G3: AI 披露（PR body + 每个 commit 的 trailer）+ Issue 关联检查 ---
  ai-disclosure:
    name: ai-disclosure
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            const body = pr.body || '';
            // 收集全部问题后一次性 setFailed：连续两次调用会让后一条消息覆盖前一条
            const problems = [];

            // --- 1) PR body：AI 披露 + 关联 Issue ---
            if (!(/\[x\].*AI/i.test(body) || /AI-assisted/i.test(body))) {
              problems.push('PR body 缺少 AI 披露声明（勾选 AI-generated 复选框，或写入 AI-assisted trailer）');
            }
            if (!/(?:closes|fixes|resolves|refs)\s+#\d+/i.test(body)) {
              problems.push('PR body 缺少关联 Issue（使用 closes/fixes/resolves #NNN）');
            }

            // --- 2) 每个 commit 必须带 AI-assisted trailer ---
            const commits = await github.paginate(
              github.rest.pulls.listCommits,
              { owner: context.repo.owner, repo: context.repo.repo, pull_number: pr.number, per_page: 100 }
            );
            // trailer 必须独占一行（行首匹配），避免正文中偶然提及被误判为通过
            const TRAILER = /^AI-assisted:\s*\S+/im;
            const missing = commits
              .filter(c => (c.parents || []).length < 2)   // 跳过 merge commit
              .filter(c => !TRAILER.test(c.commit.message || ''))
              .map(c => `${c.sha.substring(0, 7)} ${(c.commit.message || '').split('\n')[0]}`);

            // --- 3) 每个 commit 禁止含 AI 模型品牌名（§2.1 品牌词禁令）---
            const BRAND_RE = /\b(Claude|GLM|GPT|Gemini|Llama|Mistral|Qwen|DeepSeek|Anthropic|OpenAI)\b/i;
            const brandOffenders = commits
              .filter(c => (c.parents || []).length < 2)
              .filter(c => BRAND_RE.test(c.commit.message || ''))
              .map(c => `${c.sha.substring(0, 7)} ${(c.commit.message || '').split('\n')[0]}`);

            if (brandOffenders.length) {
              problems.push(
                `以下 ${brandOffenders.length} 个 commit 含 AI 模型品牌名（违反 §2.1 品牌词禁令）：\n  - ` + brandOffenders.join('\n  - ')
              );
            }

            if (missing.length) {
              problems.push(
                `以下 ${missing.length} 个 commit 缺少 AI-assisted trailer：\n  - ` + missing.join('\n  - ')
              );
            }

            if (problems.length) {
              core.setFailed('AI 披露门禁未通过：\n- ' + problems.join('\n- '));
            } else {
              core.info(`OK: PR body 已披露；${commits.length} 个 commit 均含 AI-assisted trailer 且无品牌词`);
            }

  # --- G2/G3: DoR 门禁（关联 Issue 状态检查）---
  dor-check:
    name: dor-check
    runs-on: ubuntu-latest
    permissions:
      issues: read
      pull-requests: read
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            const body = pr.body || '';
            const match = body.match(/(?:closes|fixes|resolves|refs)\s+#(\d+)/i);
            if (!match) {
              core.setFailed('无法从 PR 提取关联 Issue 编号');
              return;
            }
            const issueNum = parseInt(match[1]);
            try {
              const { data: issue } = await github.rest.issues.get({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issueNum
              });
              const labels = issue.labels.map(l => l.name);
              // 白名单仅含 PR 创建瞬间的合法状态：do:in-progress（pr create 之前）
              // 和 do:review（pr create 之后）。见 §2.4.1 step 5 时序说明。
              const ALLOWED = ['do:in-progress', 'do:review'];
              const problems = [];
              if (!labels.some(l => ALLOWED.includes(l))) {
                problems.push('关联 Issue #' + issueNum + ' 缺少 ' + ALLOWED.join('/') + ' 之一');
              }
              if (labels.includes('origin:external')) {
                problems.push('关联 Issue #' + issueNum + ' 是第三方 Issue，禁止直接开发（采纳后应在新的 owner Issue 上开发）');
              }
              if (problems.length) {
                core.setFailed('DoR 门禁未通过：\n- ' + problems.join('\n- '));
              }
            } catch (e) {
              core.setFailed('获取 Issue #' + issueNum + ' 失败: ' + e.message);
            }
```

> **根因 R1/R3 的落点**：pr-gates.yml 的 `ALLOWED` 白名单必须与 §2.4.1 step 5 的时序声明、§2.2.1 状态转换矩阵**三者一致**（文档规范 / CI 部署 / 状态机；三者必须一致——根因 R1）。白名单过宽（含 `do:ready`/`do:acceptance`）会被静默绕过。
>
> **项目扩展 verify job**：项目可在 pr-gates 中追加自有 verify job（规格校验/lint/test）并加入分支保护 required_status_checks.contexts。通用 P0 不预设 verify job——pr-gates 仅 `ai-disclosure` + `dor-check` 两个门禁。

### 4.9 创建 AGENTS.md

创建仓库根目录 `AGENTS.md`。AGENTS.md 是 AI 会话入口指令，结构如下（项目文档按 `${VAR}` 绑定具体值）：

```markdown
# AGENTS.md - ${REPO} AI 开发指引

> 本文件是 AI 会话的入口指令。每次会话启动时必须首先读取本文件。
> 借鉴 zed-industries/zed：本文件为单一规范源，CLAUDE.md/GEMINI.md 可软链至此。

## 身份与权限

- **仓库所有者**：${OWNER_LOGIN}
- **AI 身份**：当前会话模型，必须在每个 commit 添加 `AI-assisted:` trailer（**禁止列品牌名、版本号、能力等级**——按 §2.1 品牌词禁令）
- **AI 可做**：自动开发、编写、审核、测试、创建分支/PR、运行验证命令、分诊第三方 Issue
- **AI 禁止**：
  1. 自我批准 merge（等用户显式指示或 `do:acceptance` 状态）
  2. 操作非 ${OWNER_LOGIN} 的 Issue
  3. 绕过门禁（CI status check / branch protection）
  4. 手改受治理保护的文件（门禁来源/模板/规格等，修改须通过 Issue + PR）
  5. 自行将 Issue 从 `do:triage` 切换到 `do:ready`（**G2 门禁**：Ready 转换需用户确认）
  6. **force-push 到 main**（分支保护 `allow_force_pushes: false` 实证生效）
  7. **删除 Issue / Milestone / 标签**
  8. **擅自修改 `.github/workflows/*.yml` 直推 main**（门禁唯一来源，修改走 `gov(governance)` Issue + PR）
  9. **未经用户确认合 PR**（AI 不得调用 `gh pr merge`；merge 是 [MANUAL-REVIEW]）

## 会话启动检查（G0 Session Gate）

1. 读取本文件
2. `gh auth status` 确认已认证为 ${OWNER_LOGIN}
3. 查询可领取的 Issue：`gh issue list --label "origin:owner" --label "do:ready" --state open`

> 项目特定扩展（如读取规格地图卷、运行规格校验）由项目文档在此追加。

## Issue-First 铁律
## 标题前缀规范（见 GITHUB-INIT.md §2.1）
## 分支与提交规范（见 GITHUB-INIT.md §2.4.1）
## 门禁分层（见 GITHUB-INIT.md §2.3）
## AC 验收格式（见 GITHUB-INIT.md §2.5）
## 第三方 Issue 分诊流程（见 GITHUB-INIT.md §2.4.2）
## 反模式清单（禁止）
## 会话结束协议
## 治理规则变更（Rules Hygiene）
```

> **AGENTS.md 内容原则（通用，源自 zed Rules Hygiene）**：
> - AGENTS.md 被每个 AI 会话读取，保持高信噪比
> - 规则是**要避开的坑**（traps to avoid），不是**照着走的地图**（maps to follow）
> - 架构描述（模块布局、数据流、关键类型）会快速过期，AI 可通过读代码获取，**不写入** AGENTS.md
> - 治理规则变更必须开 `gov(governance)` 类型 Issue + PR；**禁止在正常功能/修复工作中顺手修改 AGENTS.md**（no drive-by additions）
> - 新规则必须同时满足：非显而易见、反复遇到、具体可执行
> - 详细章节内容（Issue-First 铁律、标题前缀、分支提交、门禁分层、AC 格式、分诊流程、反模式清单、会话结束协议）从本模板 §2 填充，项目文档给出完整 AGENTS.md 全文。

### 4.10 创建 CLAUDE.md / GEMINI.md 软链

```bash
# 借鉴 zed-industries/zed：一份规则多处软链，避免多 AI 规则漂移
# 用 AGENTS.md 作为源文件（AI agent 发现优先级最高），CLAUDE.md/GEMINI.md 软链至它
cd <repo-root>
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md

# 验证软链
ls -la AGENTS.md CLAUDE.md GEMINI.md
# 期望：AGENTS.md 为普通文件，CLAUDE.md 和 GEMINI.md 为 -> AGENTS.md 的软链
```

> **设计说明**：不同 AI 工具读取的入口文件名不同，但规则内容必须一致。软链保证只有一份源文件，修改 AGENTS.md 即同步生效到所有 AI。

### 4.11 提交全部治理文件

```bash
git add .gitignore AGENTS.md CLAUDE.md GEMINI.md .github/
git commit -m "gov(governance): 初始化 issue-first 治理基础设施

- AGENTS.md: AI 开发指引 + 反模式清单 + 门禁分层 + Rules Hygiene
- .github/ISSUE_TEMPLATE/: type 类 Issue 模板 + config
- .github/PULL_REQUEST_TEMPLATE.md: AI 披露 + AC 证据
- .github/CODEOWNERS: 全路径归属 ${OWNER_LOGIN}
- .github/workflows/issue-triage.yml: G1 自动打标 + GraphQL 赋 Issue Type
- .github/workflows/label-sync.yml: Projects v2 Status 同步（若启用）
- .github/workflows/pr-gates.yml: G3 双重检查
- ${LABEL_COUNT} 个标签 + 1 个 P0 Milestone 已创建（第 1 段）

AI-assisted: supervised"
```

> **不要 `git push origin main`**：本节属第 2 段（自举期），变更在 `gov/<N>-governance-bootstrap` 分支上，须按 §4.4 步骤 5 推送分支并开 PR，由用户 merge 进 main。

### 4.12 配置分支保护

> **前置**：本节必须在 §4.4 自举 PR **merge 之后**执行。届时 pr-gates.yml 已在 main 上，且两个 check 已在自举 PR 上真实运行过（AC-P0-08 的证据），因此 required check 名称可被 GitHub 正常识别。若顺序颠倒（先设保护再开自举 PR），required checks 会阻塞该 PR 的 merge。

```bash
# 设置 main 分支保护（公共仓库 Free 可用）
gh api -X PUT "repos/${ORG}/${REPO}/branches/main/protection" --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ai-disclosure", "dor-check"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

> **说明与配置选择**：
> - `enforce_admins: true`：**强制配置**——admin 与普通用户同样受 status check / 分支保护约束，门禁是**强制性**而非**自律性**（根因 R2 的直接修正，见附录 B §R2）。紧急修复通过 GitHub Web UI 的 admin bypass 绕过（不在本地 `git push` 层面绕过），绕过行为在保护规则日志中可见可审计。
> - `required_pull_request_reviews`：按团队规模配置。单人开发设 `null`（GitHub 规定 PR 作者不能批准自己的 PR，单人期 review 无强制力，门禁靠 CI status check）；**引入第一个协作者时立即改为 `>=1` approving reviewer**——这是触发条件，不是「延后偿还的债」。
> - `required_status_checks.contexts`：2 个 check 名称必须与 pr-gates.yml 中 job 的 `name:` 完全匹配（`ai-disclosure` / `dor-check`）。项目追加自有 verify job 时，将其 job 名同步加入此 contexts。
> - `required_linear_history`：禁止 merge commit，保持线性历史（配合 `--squash` 合并）
> - `strict: true`：PR 必须基于最新 main 且 CI 通过

### 4.13 验证自动化

`CP-P0-03`：Issue-first 自动化验证。创建一个测试 Issue，验证 origin 标签、Issue Type、scope 标签与 Milestone 均由自动化正确处理。

> 本节须在自举 PR **merge 之后**执行——此时 `issue-triage.yml` 才在 main 上生效。

```bash
# 1. 创建测试 Issue（不手工打 origin:owner / scope:governance，交由 CI 自动处理）
gh issue create -R ${ORG}/${REPO} \
  --title "gov(governance): 验证 issue-triage 自动打标" \
  --milestone "P0 GitHub Initialization" \
  --label "priority:blocker" \
  --body "## 测试目的
验证 issue-triage.yml 正确执行：
- 作者为所有者 -> 自动打 origin:owner + do:triage
- 标题前缀 gov(governance) -> 自动赋 Issue Type: Change + 打 scope:governance

## 验收标准
见 GITHUB-INIT.md §5 的 AC-P0-07 与 AC-P0-07b。"

# 2. 等待 CI 完成
sleep 15

# 3. 解析测试 Issue 编号（后续命令复用，避免占位符）
N=$(gh issue list -R ${ORG}/${REPO} --state all \
      --search 'in:title 验证 issue-triage' --limit 1 --json number --jq '.[0].number')
echo "测试 Issue = #$N"

# 4. 检查标签（期望：origin:owner, do:triage, scope:governance, priority:blocker）
gh issue view "$N" -R ${ORG}/${REPO} --json labels --jq '[.labels[].name]|sort|join(", ")'

# 5. 检查 Issue Type（期望：Change）—— 必须走 GraphQL（REST issue.type.name 长期为 null，见 §2.2.3）
gh api graphql -F number=$N -f query='query($number:Int!){repository(owner:"${ORG}",name:"${REPO}"){issue(number:$number){issueType{name}}}}' --jq '.data.repository.issue.issueType.name'

# 6. 检查 Milestone（期望：P0 GitHub Initialization）
gh issue view "$N" -R ${ORG}/${REPO} --json milestone --jq '.milestone.title'
```

> **若 Issue Type 为 null**：说明 `updateIssueIssueType` 失败。issue-triage.yml 已将其设为非阻塞（`core.warning`），去 Actions 日志查看 warning 原因，常见为 Issue Type 名称不匹配或 token 权限不足。

---

## 5. P0 目标验收合同

以下 AC 均为**待执行的目标合同**。按 §2.5「命令未实际执行不得填退出码」，本节各条**刻意不写 `exit code` 行**；实际执行后，在该行补入真实退出码并把 `evidence: planned` 替换为可复核证据。

> **AC 格式对齐**：未执行时**省略 `exit code:` 行**并写 `evidence: planned`。执行后回填真实整数退出码并替换 `evidence:` 为可复核证据。

```
AC-P0-01
command: git -C <repo-root> status --short
assert: 输出为空（工作区干净，无未提交变更）
evidence: planned

AC-P0-02
command: gh repo view ${ORG}/${REPO} --json visibility --jq .visibility
assert: 输出 "${REPO_VISIBILITY_UPPER}"
evidence: planned

AC-P0-03
command: gh label list -R ${ORG}/${REPO} --limit 100 --json name --jq '[.[].name]|map(select(test("^(do|state|origin|scope|priority):")))|length'
assert: 输出 ${LABEL_COUNT}（只统计自建治理标签，排除 GitHub 默认标签）
evidence: planned

AC-P0-03b
command: gh api repos/${ORG}/${REPO}/issue-types --jq 'length'
assert: 输出 >= ${ISSUE_TYPE_MIN}（组织级 Issue Type）
evidence: planned

AC-P0-03c
command: gh api repos/${ORG}/${REPO}/milestones --jq 'length'
assert: 输出 1（通用 P0 只创建 P0 GitHub Initialization 一个 Milestone）
evidence: planned

AC-P0-04
command: test -f AGENTS.md && test -L CLAUDE.md && test -L GEMINI.md && test -f .github/CODEOWNERS && test -f .github/PULL_REQUEST_TEMPLATE.md && test -f .github/workflows/issue-triage.yml && test -f .github/workflows/pr-gates.yml && ([ "${PROJECTS_V2_ENABLED}" = "false" ] || test -f .github/workflows/label-sync.yml)
assert: 退出码 0（全部治理文件存在，且 CLAUDE.md/GEMINI.md 是软链）
evidence: planned

AC-P0-05（通用 P0 不适用）
assert: N/A —— 通用 P0 的 pr-gates 只有 ai-disclosure + dor-check 两个 job，不创建 verify job
evidence: N/A（项目在 P1+ 接入规格校验或自有 lint 后，由项目文档定义等价 AC；本条在通用 P0 留空）

AC-P0-06
command: gh api repos/${ORG}/${REPO}/branches/main/protection --jq '.required_status_checks.contexts|sort|join(",")'
assert: 输出 "ai-disclosure,dor-check"（项目追加 verify job 时，此输出随之扩展）
evidence: planned

AC-P0-07
command: gh issue list -R ${ORG}/${REPO} --label "origin:owner" --state all --json number --jq 'length'
assert: 输出 >= 1（CI 已为 owner Issue 自动打 origin:owner 标签）
evidence: planned

AC-P0-07b
command: N=$(gh issue list -R ${ORG}/${REPO} --state all --search 'in:title 验证 issue-triage' --limit 1 --json number --jq '.[0].number') && gh api graphql -F number=$N -f query='query($number:Int!){repository(owner:"${ORG}",name:"${REPO}"){issue(number:$number){issueType{name}}}}' --jq '.data.repository.issue.issueType.name'
assert: 输出 "Change"（CI 从 gov 前缀自动赋值 Issue Type，无占位符，可原样执行。注：REST `issues[].type` 长期为 null，必须走 GraphQL）
evidence: planned

AC-P0-08
command: gh pr checks $(gh pr list -R ${ORG}/${REPO} --state all --search 'in:title 初始化 issue-first 治理基础设施' --limit 1 --json number --jq '.[0].number') --json name,state --jq '[.[]|select(.state=="SUCCESS")|.name]|sort|join(",")'
assert: 输出包含 ai-disclosure、dor-check 两者（门禁有效性实证：自举 PR 上两个 check 真实通过，而非仅配置存在）
evidence: planned

AC-P0-09
command: git -C <repo-root> log --format=%B main | grep -cE "^AI-assisted:"
assert: 输出 == main commit 数（每个 commit 末尾都含 AI-assisted trailer，trailer 必在 commit 末尾独占）
evidence: planned

AC-P0-09b
command: python3 -c "import re; t=open('/dev/stdin').read(); print(len(re.findall(r'\b(Claude|GLM|GPT|Gemini|Llama|Mistral|Qwen|DeepSeek|Anthropic|OpenAI)\b(?!\.md)', t, re.I)))" < <(git -C <repo-root> log --format=%B main)
assert: 输出 0（main 上 commit message 任何位置无 AI 模型品牌名；`(?!\.md)` lookahead 排除软链文件名）
evidence: planned
```

> **AC-P0-09b 用 python 替代 grep 的原因（根因 R5）**：`(?!\.md)` lookahead 在 GNU grep / ugrep 上兼容性不一致（ugrep 不支持）；python `re.IGNORECASE` 行为跨工具一致。脚本/正则的「看起来能用」假象单看不致命，叠加后 AC 验证不可信。

---

## 6. 执行清单

**第 1 段：豁免期（直推 main）**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 1 | 安装 gh CLI | `[MANUAL-AUTH]` | `gh --version` 输出版本号 |
| 2 | gh auth login | `[MANUAL-AUTH]` | `gh api user --jq .login` 输出 ${OWNER_LOGIN} |
| 3 | 运行 Token 权限验证脚本（§3.2） | `[MANUAL-AUTH]` | 脚本输出「全部验证通过」，退出码 0 |
| 4 | 确认组织（若已存在可跳过） | `[MANUAL-AUTH]` | `gh api orgs/${ORG}` 不报错 |
| 5 | git init + .gitignore | `[LOCAL-AUTO]` | `git status` 可运行 |
| 6 | 首次提交 | `[LOCAL-AUTO]` | `git log --oneline` 显示 1 条提交 |
| 7 | 关联远程 + push（按 ${REPO_PREEXISTS} 分支） | `[REMOTE-AUTO]` | `gh repo view` 显示 URL |
| 8 | 创建治理标签 | `[REMOTE-AUTO]` | AC-P0-03 输出 ${LABEL_COUNT} |
| 8b | 验证/创建 Issue Types | `[REMOTE-AUTO]` | AC-P0-03b 通过 |
| 8c | 创建 P0 Milestone | `[REMOTE-AUTO]` | AC-P0-03c 输出 1 |

**第 2 段：自举期（必须走 PR，见 §4.4）**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 9 | 创建自举 Issue + 手工设 Issue Type + 开分支 | `[REMOTE-AUTO]` | Issue 为 `do:in-progress`，分支已创建 |
| 10 | 创建 Issue 模板（type 类 + config） | `[LOCAL-AUTO]` | `.github/ISSUE_TEMPLATE/` 下文件齐全 |
| 11 | 创建 PR 模板 | `[LOCAL-AUTO]` | `.github/PULL_REQUEST_TEMPLATE.md` 存在 |
| 12 | 创建 CODEOWNERS | `[LOCAL-AUTO]` | `.github/CODEOWNERS` 存在 |
| 13 | 创建 issue-triage.yml | `[LOCAL-AUTO]` | 文件存在 |
| 13b | 创建 label-sync.yml（若启用） | `[LOCAL-AUTO]` | 文件存在 |
| 14 | 创建 pr-gates.yml | `[LOCAL-AUTO]` | 文件存在 |
| 15 | 创建 AGENTS.md + 软链 | `[LOCAL-AUTO]` | AC-P0-04 退出码 0 |
| 16 | 提交 + push 分支 + 开 draft PR | `[REMOTE-AUTO]` | PR 已创建，Issue 切 `do:review` |
| 17 | **观察 pr-gates 两个 check** | `[REMOTE-AUTO]` | AC-P0-08：两个 check 全绿（门禁有效性实证） |
| 18 | 用户审核并 merge | `[MANUAL-REVIEW]` | PR 已 merge，Issue 以 `completed` 关闭 |

**第 3 段：收尾**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 19 | 配置分支保护（**必须在自举 PR merge 之后**） | `[REMOTE-AUTO]` | AC-P0-06 输出两个 check 名 |
| 20 | 创建测试 Issue 验证 CI 自动打标 + Issue Type | `[REMOTE-AUTO]` | AC-P0-07、AC-P0-07b 通过 |
| 21 | 执行并记录全部 AC，申请 `GATE-P0-EXIT` | `[LOCAL-AUTO+REMOTE-AUTO]` | 全部 AC 有实际 evidence；用户确认 |

---

## GATE-P0-EXIT

P0 退出需同时满足：`CP-P0-01`/`CP-P0-02`/`CP-P0-03` 完成、`AC-P0-01`…`AC-P0-09`（含各 b/c 子项；AC-P0-05 为 N/A）全部有可复核实际证据、用户最终确认。

**退出门映射到项目路线文档的阶段退出维度**（本门不替代路线文档的退出语义，只是其在 P0 的落地；通用维度措辞见 §2.5）：

| 阶段退出维度 | P0 的满足方式 | 实证引用 |
|---|---|---|
| 维度一：该阶段全部能力已实现并通过验证 | `CP-P0-01`/`02`/`03` 完成；AC-P0-01…09 有实际证据 | §5 AC 各条 |
| 维度二：依赖阶段能力已具备，前置未被绕过 | P0 是首阶段，无前置依赖；第 1 段豁免边界已在 §0 显式声明并限定 | §0 Issue-First 豁免声明 |
| 维度三：测试覆盖 normal/edge/error，golden 通过 | P0 无业务代码。normal＝AC-P0-08 两 check 全绿；error＝自举期任一 check 红灯并被修复的留痕；golden/校验由项目 P1+ 接入的 verify job 承担（通用 P0 无 verify job，AC-P0-05 为 N/A） | AC-P0-08 |
| 维度四：正式文档覆盖、风险和豁免可追溯 | AGENTS.md 已合入；§0 豁免声明已显式限定边界；§4.12 采用 `enforce_admins: true` 强制配置（无 admin 绕过残留）；根因 R1-R6 已在附录 B 落地为设计原理 | AGENTS.md；附录 B |
| 维度五：维护者确认能力达标 | 用户对 `GATE-P0-EXIT` 的最终确认 | （本门定义本身） |

> **GATE-P0-EXIT 无延后交付物**：P0 的所有已知偏差按 §0.2 原则就地修正（§4.12 强制配置、附录 B 根因落地），不向下一阶段移交「待偿还清单」。下一阶段直接以 P0 的强制门禁为前提启动。

---

## 附录 A：日常开发 gh 命令速查

```bash
# 查询可领取的 Issue
gh issue list --label "origin:owner" --label "do:ready" --state open

# 查询待分诊的 Issue
gh issue list --label "origin:owner" --label "do:triage" --state open

# 查询待分诊的第三方 Issue（Issue Type: Intake）
gh issue list --label "origin:external" --label "do:triage" --state open

# 领取 Issue
gh issue edit <N> --add-assignee "@me"
git checkout -b <type>/<N>-<slug>
gh issue edit <N> --remove-label "do:ready" --add-label "do:in-progress"

# 开 PR
gh pr create --draft \
  --title "<type>(<scope>): <subject> (#<N>)" \
  --body "Closes #<N>" \
  --base main
gh issue edit <N> --remove-label "do:in-progress" --add-label "do:review"

# 审核通过后打验收状态
gh issue edit <N> --add-label "do:acceptance"

# 验收通过后取消 draft（AC 证据贴在 PR body 中）
gh pr ready <PR#>

# 用户 merge
gh pr merge <PR#> --squash --delete-branch
gh issue close <N> --reason completed

# 第三方 Issue 采纳（创建新 owner Issue，CI 自动赋 Issue Type + origin:owner）
gh issue create \
  --title "<proposed title>" \
  --body "采纳自 #<原#>

<原始内容摘要>" \
  --label "do:ready,scope:xxx,priority:xxx"

# 关闭原第三方 Issue
gh issue close <原#> --comment "采纳 via #<新#>，本 Issue 关闭。" --reason "not planned"
```

---

## 附录 B：设计原理与已知陷阱（R1-R6 经验提炼）

> 本附录是 P0 方法论的**设计依据与已知陷阱**，提炼自首次实践的根因分析（根因 R1-R6）。它是**通用教训**（适用于任何采用本模板的项目），不含项目特定执行记录（SHA/Issue 号/Run ID 等执行实证由项目文档维护）。每条根因给出：是什么、为何反复出现、本模板如何防范。

### R1 文档与代码不同步

**是什么**：治理文档写了规范说明 + 嵌入代码示例，但代码示例是「参考性」而非「被引用」——读者无法判断「代码必须与文档一致」还是「代码只是示意」。

**为何反复出现**：P0 同时产出「规范文档」和「可部署代码」，二者天然有漂移压力；没有显式约束时，读者默认代码是示意。

**本模板如何防范**：§4 每段开头声明「X 规范 / Y 部署；二者必须一致」（如 pr-gates.yml 的 `ALLOWED` 白名单必须与 §2.4.1 step 5 时序、§2.2.1 状态矩阵三者一致）；任何「文档说 A、代码做 B」的差异按 §0.2 就地修正，不积累登记表。

### R2 自律性 vs 技术门禁失衡

**是什么**：豁免声明承诺「豁免不等于无门禁」，但关键行为门禁（状态机变更、资源操作、admin 绕过）仍依赖信任。治理基础设施不应用「治理信任」循环。

**为何反复出现**：单人开发 + Free 计划下，`enforce_admins`、`required_pull_request_reviews` 等强制项被迫放宽，门禁退化为自律。

**本模板如何防范**：§4.12 默认 `enforce_admins: true`（强制配置，admin 不绕过 status check，紧急修复走 GitHub UI 的可审计 bypass）；review 要求按团队规模配置（单人 `null`，引入协作者即 `>=1`，是触发条件而非延后债）。AGENTS.md 的 AI 禁止清单（9 条）补强关键操作约束。

### R3 状态空间双轨未充分文档化

**是什么**：`do:*` 标签 + GitHub 原生 close reason + Issue Types + Projects v2 Status 多源并存，**转换关系**没充分文档化。

**为何反复出现**：原生功能与标签并行使用是「原生优先决策」的必然结果，但转换关系若只在散落注释中提及，读者会混淆。

**本模板如何防范**：§2.2.1 提供完整「状态转换矩阵」（当前状态 / 触发条件 / 动作 / 下一状态 / close reason 五列）；§2.2.3 表覆盖所有 type。

### R4 偏差「记录为延后清单而非就地修正」

**是什么**：执行中发现偏差后，习惯登记到一张「技术债/偏离表」延后偿还，而不是在发现处直接修正。清单只列「是什么 + 何时偿还」，没列「不偿还会发生什么」+「如何检测」，且无优先级。

**为何反复出现**：就地修正需要立刻动文档/代码，登记到清单更省事；散文式清单便于一时记录，但不可追踪、不可排序，偿还时找不到入口，最终被遗忘。

**本模板如何防范**：§0.2 规定**偏差就地修正，不积累延后清单**；极少数无法立即修正者必须在发生处以显式注释标注（影响 + 可执行检测信号 + 修正条件），不得汇入独立登记表。

### R5 脚本/正则的「看起来能用」假象

**是什么**：权限验证脚本的 scope 子串误匹配、bash 数组元素未 trim、AC 正则的宽松分支与 `grep -c` 计数陷阱——单看不致命，叠加后 AC 验证不可信。

**为何反复出现**：shell/正则的跨工具行为差异（GNU grep vs ugrep 的 lookahead 支持）不易察觉；bash 命令替换的隐式空格污染数组。

**本模板如何防范**：§3.2 要求 scope 匹配精确（逐项集合比对，禁子串）；AC-P0-09b 用 python 替代 grep 处理 lookahead（跨工具一致）；§2.2.5 要求 label-sync 缺 token 时 warning 跳过而非 error。项目文档登记脚本的可移植性测试声明。

### R6 借鉴来源的「广撒网」未收敛

**是什么**：借鉴来源映射在多处重复（§0 借鉴表 + §4.10 软链说明 + 附录门禁对照表三处重叠 60%+）。

**为何反复出现**：写文档时在不同语境都需要解释「为什么这么设计」，若不强制单一权威位置，就会逐处复制。

**本模板如何防范**：§0.3 是借鉴来源的**唯一权威位置**；本附录与各章节引用它，不重复。这是「主权威去重」原则在元文档层面的应用。

---

## 附录 C：门禁设计借鉴对照表（速查）

> 本表是 §0.3 借鉴来源在「门禁要素」维度的速查视图，供快速定位各门禁的设计出处。详细借鉴方式与偏差原因见 §0.3。

| 门禁要素 | 本方案实现 | 借鉴方式 |
|---|---|---|
| 类型化 Issue | GitHub 原生 Issue Types | 原生优先：Issue Types（GraphQL 赋值） |
| 状态机 | do:* 标签前向推进 + close reason 终态 | 标签用于 CLI 自动化；close reason 替代 state:* 标签 |
| 阶段分组 | GitHub 原生 Milestones | 原生优先：Milestones 替代 phase:* 标签 |
| 看板可视化 | Projects v2 Status 字段（标签同步镜像） | 原生优先：标签驱动自动化，Projects v2 提供展示层 |
| DoR 门禁 | Issue 模板必填 + AI 检查 + CI dor-check | approved-* 标签是写码前置 |
| PR 门禁 | required status checks（2 个 job） | CI 状态检查即门禁 |
| 验收门禁 | AC 命令全通过 + do:acceptance 状态 | 可执行命令即验收 |
| AI 身份边界 | AI-assisted trailer + 品牌词禁令 + 反模式清单 | 连续披露（中性形式）|
| 来源控制 | origin:owner/external 标签 | 自动化触发依据（本方案原创） |
| 规则变更 | Rules Hygiene + gov 类型 Issue | 补演进机制 |
| 单一规范源 | AGENTS.md 软链 CLAUDE/GEMINI | 一份规则多处引用 |
| 拒绝留档 | close reason "not planned" + 评论 | out-of-scope 决策留档 |

---

## 11. 职责边界（通用模板与项目文档的分工）

本模板与项目文档的职责边界严格分离，避免方法论重复维护与具体数值泄漏：

### 本模板（GITHUB-INIT.md）拥有

| 类别 | 内容 |
|---|---|
| 通用方法论 | Issue-First 两段式自举原理、状态机设计、门禁分层 GOV-G0~G4、owner/第三方 Issue 流程、G0 会话启动检查（通用部分） |
| 通用模式 | 标题前缀规范、标签分类体系（原生优先决策）、Issue Type GraphQL 赋值机制、Projects v2 PAT 权限约束、分支保护配置权衡 |
| 通用模板 | CI workflows 逻辑骨架（issue-triage / label-sync / pr-gates）、Issue/PR 模板结构、AGENTS.md 结构、CODEOWNERS 模式、token 验证脚本骨架 |
| 通用合同 | AC 验收格式与验收设计要求（§2.5）、GATE-P0-EXIT 退出门结构、执行清单三段式结构 |
| 通用教训 | 设计借鉴来源（§0.3 唯一权威）、根因 R1-R6 设计原理（附录 B）、偏差就地修正原则（§0.2） |
| 参数契约 | §0.0 必需项目参数清单（定义所有 `${VAR}` 的含义与示例） |
| P0 Milestone | `P0 GitHub Initialization`——通用 P0 自指的唯一 Milestone |

### 项目文档拥有

| 类别 | 内容 |
|---|---|
| 身份绑定 | §0.0 组 A 全部 `${VAR}` 的具体值（org/repo/owner/visibility/plan 等） |
| roadmap | P1、P2… 阶段定义、依赖图、退出边界语义、系统模块清单；这些阶段的 GitHub Milestone 由项目在 P0 之后的规划阶段创建（通用 P0 不预设） |
| 项目数值 | scope 集合（`${SCOPES}`）的具体取值、Issue Type 映射、`${LABEL_COUNT}` |
| 可选扩展 | 项目特定的治理扩展——如版本化规格卷体系（verify job、seed 修订流程、`scope:spec` 标签、G0 读规格地图卷步骤）——由项目文档定义并接入本模板的 CI/AGENTS.md，**不属于通用 P0** |
| 执行状态 | `${REPO_PREEXISTS}` / `${ISSUE_TYPES_PREEXIST}` / `${PROJECT_NUMBER}` 等执行前实测确认项 |

### 对齐规则

1. **数值不进模板**：任何具体 org/repo/owner/roadmap 阶段名出现在本模板中即为缺陷。模板中只允许 `${VAR}` 与「示例值」（明确标注为示例，使用中性占位如 `acme`/`my-project`）。
2. **方法论不重复**：项目文档引用本模板的章节锚点（如「自举流程见 GITHUB-INIT.md §4.4」），不复述方法论细则。项目文档复述方法论即为冗余，会导致双主权威。
3. **P0 自指**：本模板创建且仅创建 `P0 GitHub Initialization` 一个 Milestone。项目的 P1+ Milestone 不在本模板中预设，由项目规划文档定义。
4. **扩展不入模板**：项目特定的治理扩展（规格体系等）由项目文档承载，不作为本模板的条件分支。本模板的 CI workflows、AGENTS.md、Issue 模板均为通用形态；项目扩展通过「在通用形态上叠加」的方式接入（如 pr-gates 增 verify job、G0 增读规格步骤、issue-triage 增 scope 正则），接入动作走项目 `gov(governance)` Issue。
5. **变更解耦**：本模板演进（通用方法论调整）走模板自身的版本管理；项目演进（数值/扩展变化）走项目 `gov(governance)` Issue。两者变更互不强制联动，但项目文档须标注所基于的模板版本。
6. **AC 实例化**：本模板 §5 的 AC 是参数化合同（含 `${VAR}`，`evidence` 永远 `planned`）；项目执行时用身份绑定值替换 `${VAR}` 得到可原样执行命令，执行后回填真实 `exit code` 与 `evidence`。
7. **借鉴与根因唯一权威**：§0.3（借鉴来源）与附录 B（根因 R1-R6）是通用教训的唯一权威位置；项目文档只引用，不复述，也不登记项目特定的「第 7 个根因」（项目特定问题按 §0.2 就地修正，不归根因 R-n）。
8. **偏差就地修正**：执行中发现的偏差按 §0.2 就地修正文档或配置，不向项目文档移交「待偿还清单」。无法立即修正者在发生处显式标注（影响 + 检测信号 + 修正条件）。

> **自检**：若发现本模板某处出现具体项目名/人名/编号/roadmap 阶段名，或项目文档复述了状态机/门禁定义，或本模板承载了项目特定扩展（如规格体系），即为边界违反，须立即修正。
