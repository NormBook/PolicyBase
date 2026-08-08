# PolicyBase P0 种子提示词：治理初始化与 Issue-First 自动化

> 类型：种子提示词（P0 任务定义）
> 阶段标识：`P0`（阶段定义见 PolicyBase_02 §5）
> 阶段名称：Repository Governance Bootstrap
> 优先级标识：使用 `priority:blocker|high|medium|low`，不使用裸 `P0/P1/P2/P3`
> 创建日期：2026-08-07
> 仓库：NormBook/PolicyBase（公共仓库，Free 组织）
> 状态：待执行

---

## 0. 执行须知

### 角色分工

| 角色 | 身份 | 职责 |
|---|---|---|
| 用户 | @janssenkm（GitHub: janssenkm） | 仓库唯一所有者；Token/认证手动步骤；最终审核与 merge 决策；第三方 Issue 采纳决定 |
| AI | 当前会话模型 | 全自动执行开发/编写/审核/测试；受门禁约束；不自我批准 merge |

### 步骤标记

- `[MANUAL-AUTH]`：用户手动完成认证、组织创建等需浏览器/交互或明确授权的步骤，AI 只提供原始命令，不封装 Token 操作
- `[LOCAL-AUTO]`：AI 可在本地自动执行的文件编写、静态检查和测试命令
- `[REMOTE-AUTO]`：用户完成认证且明确授权后，AI 可自动执行的 GitHub/远程副作用操作
- `[MANUAL-REVIEW]`：必须由用户审核、批准或 merge 的步骤

### §0.1 P0 与 `policybase` CLI 的关系

本文件是 P0 治理基础设施的任务定义，**不实现业务代码、不创建 `policybase` CLI 入口**。`policybase` 顶层命令是 PolicyBase_15 §2 的唯一业务入口，将在 P1 由 `python -m policybase` 引入并按 PolicyBase_19 §2 全局语法生效。P0 期间唯一外部 AC 命令是 `python3 seeds/verify_seed_set.py`（同时按 PolicyBase_03 §9 与 §0 Issue-First 豁免声明的已知技术债执行）。P0 任何代码/脚本/命令均不与 PolicyBase 业务命令面耦合——本任务只搭治理基础设施，CLI 顶层命令面是 P1 范围。

阶段、检查点、验收与退出门标识：

- `P0`：roadmap 阶段标识，由 PolicyBase_02 §5 定义；本文件是其任务分解，不重新定义阶段语义
- `CP-P0-01`：本地治理基础文件就绪（检查点，非 GitHub Milestone）
- `CP-P0-02`：远程仓库、分支保护和 CI 门禁就绪
- `CP-P0-03`：Issue-first 自动化验证完成（含门禁有效性实证）
- `AC-P0-*`：可执行验收项，格式见 PolicyBase_03 §9；**未执行时不写 `exit code`**
- `GATE-P0-EXIT`：P0 阶段退出门；要求检查点完成、AC 全部有实际证据且用户确认

> **与 PolicyBase_02 §14 的关系**：`GATE-P0-EXIT` 不替代 PolicyBase_02 §14 的五个退出维度，而是它们在 P0 的具体落地。映射见本文件 `GATE-P0-EXIT` 一节。

> **术语澄清**：`CP-P0-*` 是本文件定义的阶段内检查点（Checkpoint），不是 GitHub Milestone。GitHub Milestone 是平台原生功能，用于按能力窗口分组 Issue；roadmap 阶段 `P0`…`P8` 对应 GitHub Milestone，不使用 `phase:p*` 标签。

### Issue-First 豁免声明

本文件定义的 P0 基础设施引导**部分豁免**于 AGENTS.md 中的「无 Issue 不开发」铁律。豁免边界是**两段式**的：

**第 1 段（豁免，直推 main）——§4.1 ~ §4.3c**

范围：git init、首次提交、推送、创建标签/Milestone、验证 Issue Types。

理由（鸡生蛋）：Issue 流程的载体（仓库内容、标签、Milestone）此刻不存在，物理上无法 issue-first。

**第 2 段（不豁免，必须走 PR）——§4.4 ~ §4.11**

范围：Issue 模板、PR 模板、CODEOWNERS、三个 workflow、AGENTS.md 及软链。

标签在第 1 段末尾已就绪，Issue 能力此刻已具备，因此**治理文件本身必须通过它们所定义的流程合入**（自举）。执行序列见 §4.4 开头的「自举流程」。

> **关键收益**：第 2 段的自举 PR 会触发它自己引入的 `pr-gates.yml`，这是 P0 期间**唯一**能证明门禁真实可用的机会。若跳过，P0 退出时你将拥有一套从未被验证过的门禁，缺陷会在 P1 第一个真实任务上爆发。

**共同约束**：

1. **豁免终止**：`GATE-P0-EXIT` 通过后，第 1 段豁免立即失效。后续一切变更（含对本文件的修订）必须遵循 issue-first 流程。
2. **豁免不等于无门禁**。第 1 段期间通过以下机制保证质量：
   - 本文件本身是「Issue 等价物」：定义了目标、范围、AC 和验证合同
   - `AC-P0-*` 必须全部有实际证据（未执行不得填 `exit code`）
   - 所有 `[REMOTE-AUTO]` 步骤需用户明确授权后方可执行
   - 所有 `[MANUAL-REVIEW]` 步骤需用户审核确认
   - `GATE-P0-EXIT` 要求用户最终确认
3. **豁免留痕**：第 2 段的自举 Issue 必须在描述中声明「本 Issue 是 P0 自举，第 1 段基础设施已完成，本 Issue 起遵循 issue-first」。

### 已知技术债：`seeds/` 运行时依赖（P1 偿还）

**冲突事实**：本文件把 `seeds/` 钉进了两条永久路径——

| 位置 | 依赖形式 |
|---|---|
| `pr-gates.yml` 的 `verify-seeds` job | 每个 PR 运行 `python3 seeds/verify_seed_set.py` |
| AGENTS.md 会话启动检查（GOV-G0） | 每次会话读 `seeds/PolicyBase_01.md` + `seeds/PolicyBase_03.md`，并运行同一脚本 |

这与两条 owner 卷规定冲突：

- PolicyBase_01 §9：「禁止让正式实现长期引用 `seeds/PolicyBase_*`」
- PolicyBase_03 §8：「seed 文档是迁移源和进度追踪，不是长期运行时权威」

**P0 的处置：接受为显式技术债，不在 P0 偿还**。理由是 P0 阶段 `docs/` 正式文档体系尚不存在
（按 PolicyBase_02 §6，它是 P1 的交付物）；此刻迁移只会造出空壳目录，且会让 P0 唯一可用的
校验脚本失去落点，反而削弱验收。

**偿还合同（P1 必须完成，不得顺延至 P2）**：

1. 正式文档体系在 `docs/` 建立后，把校验脚本迁至 `scripts/verify_spec_set.py`（**与 PolicyBase_03 §8 文档目录正交**：`scripts/` 为运行时执行入口，与 `docs/` 内容层分离；不放在 `docs/` 下避免把运行时脚本与人类阅读文档混在一起。P1 spec-manifest 如指定其他位置，可调整但必须显式说明），`pr-gates.yml` 的 `verify-seeds` job 改名为 `verify-specs`，路径指向 `scripts/verify_spec_set.py`。
2. AGENTS.md 的 GOV-G0 启动检查改读 `docs/` 正式文档，不再读 `seeds/PolicyBase_*`。
3. `seeds/` 降级为迁移源与历史留档，不再出现在任何 CI 或会话启动路径中。
4. 偿还本身走 `gov(governance)` 类型 Issue，并在该 Issue 中引用本节。

> 在偿还完成前，`seeds/` 的运行时引用是**已知且已记录**的偏离，不得被解读为「PolicyBase_01 §9
> 已被本文件推翻」。owner 卷语义不变，本文件只是暂时不满足它。

### 借鉴来源映射

| 借鉴要素 | 借鉴来源 | 借鉴方式 |
|---|---|---|
| 标签状态机三段门控 | github/spec-kit | bug-assess->bug-fix->bug-test 标签触发 |
| Issue#=ADR 文件名 | open-gsd/gsd-core | 一 issue 一文档一 PR |
| 审批标签门禁 | open-gsd/gsd-core | "No code before approval"，无标签 PR 自动关 |
| AI 连续披露 | github/spec-kit | Assisted-by trailer + 反模式清单 |
| 一份规则多处软链 | zed-industries/zed | 单一规范源防多 AI 漂移 |
| Rules Hygiene | zed-industries/zed | 规则变更流程（补种子缺的演进机制） |
| CLI 唯一写入口 | MrLesk/Backlog.md | 不手改文件，工具代劳校验 |
| 验收命令即门禁 | ultraworkers/claw-code | 可重放命令作为硬检查 |
| out-of-scope 留档 | open-gsd/gsd-core | 拒绝提案入库防重提 |
| 反合理化表格 | obra/superpowers | Excuse|Reality 对照 |

---

## 1. 现状与目标

### 现状

本节事实以 2026-08-08 实测为准（`gh api` 查询结果），执行前应重新核对。

**本地**：
- `seeds/`：19 卷 PolicyBase 种子规格（7,231 行）+ 31 省调研 + `verify_seed_set.py`（77 行校验脚本）+ 本文件
  > **注**：按 PolicyBase_10 §14.2，`seeds/provinces/*.yaml` 是 proposed input，不是 registry / fixture / 正式证据快照。31 省数据是来源调研的输入候选，进入 registry 须逐条重新验证（见 PolicyBase_10 §14.2 强制条件）。
- `tmp/`：12 个高星仓库治理分析（参考素材，**不入库**）
- **尚未初始化 git 仓库**，无 `.github/`，无 `AGENTS.md`

**远程（已存在，非待创建）**：

| 对象 | 实测状态 | 对 §4 的影响 |
|---|---|---|
| `NormBook` 组织 | 已存在（Free 计划） | §3.3 可跳过 |
| `NormBook/PolicyBase` 仓库 | **已存在**，public，空仓库（无 commit），当前账号 admin=true | §4.2 不可用 `gh repo create`，改为 `git remote add` |
| Issue Types | **10 个已全部存在**：Task/Bug/Feature/Intake/Change/Decision/Acceptance/Documentation/Refactor/Seed Revision | §4.3b 无需创建，仅验证 |
| Milestones | **0 个** | §4.3c 需创建 9 个 |
| 标签 | 仅 9 个 GitHub 默认标签 | §4.3 需创建 19 个 |
| Projects v2 | 「PolicyBase Development」（number=1）已存在 | §2.2.5 可用 |
| Projects v2 `Status` 字段 | 已有选项：Triage/Ready/In progress/In review/Acceptance/Done/Blocked/Not planned/Duplicate/Unreproducible | 与 §2.2.5 映射**完全匹配** |
| Projects v2 `Priority`/`Phase` 字段 | 存在但**选项为空**（SINGLE_SELECT，0 options） | `priority:*` 同步**暂不可用**，见 §2.2.5 |
| 当前 token scopes | `admin:org, gist, project, repo, workflow` | 满足 §3.2 全部要求 |

### P0 目标
建立 issue-first 开发基础设施，使 AI 能在门禁约束下全自动推进项目：
1. git 仓库初始化 + 推送至已存在的 GitHub NormBook/PolicyBase（公共）
2. 治理元数据体系（19 标签 + 10 Issue Types（组织级，已存在）+ 9 Milestones）+ Issue/PR 模板 + CODEOWNERS + 分支保护
3. AGENTS.md（AI 开发指引 + 反模式清单）
4. CI 门禁（issue-triage 自动打标 + pr-gates 三重检查）
5. 自动化流程：owner Issue 主流程 + 第三方 Issue 分诊采纳流程
6. **门禁有效性实证**：通过自举 PR 证明 pr-gates 三个 check 真实可通过（见 §0 Issue-First 豁免声明）

---

## 2. 治理制度设计

### 2.1 Issue 标题前缀规范

格式：`<type>(<scope>): <subject>`

> **原生优先决策**：`type` 的权威存储是 GitHub 原生 **Issue Type**（非标签）。标题前缀是 CI 解析 type 并自动赋值 Issue Type 的输入源，同时为人类提供可读性。`scope` 无原生替代，仍由 CI 从标题解析为 `scope:*` 标签。

**类型枚举**（8 种，与 Issue Type 一一对应）：

| 标题前缀 | Issue Type | 含义 | 示例 |
|---|---|---|---|
| `feat` | Feature | 新功能/新能力 | `feat(PB10): Source Registry 注册接口` |
| `fix` | Bug | 缺陷修复 | `fix(PB14): FTS 索引重复键问题` |
| `docs` | Documentation | 文档（非种子规格） | `docs(infra): 补充 README 安装说明` |
| `refactor` | Refactor | 重构（无行为变化） | `refactor(cli): 拆分 list 子命令` |
| `gov` | Change | 治理/流程/CI 变更 | `gov(governance): 初始化 issue-first 流程` |
| `decision` | Decision | 架构决策（ADR） | `decision(PB04): action enum 增加 archive` |
| `chore` | Task | 维护/依赖/工具 | `chore(deps): 升级 typer 0.12` |
| `seed` | Seed Revision | 种子规格修订（PB01-19） | `seed(PB12): Rule schema 草案转主权威` |
| `（无前缀）` | Intake | 第三方提交，无标题前缀 | 由 CI 根据作者自动赋 Issue Type |

第三方 Issue 不使用标题前缀，CI 根据作者自动赋 Issue Type `Intake`。

> **8 + 1 = 9**：本表 8 个 owner 标题前缀（feat/fix/docs/refactor/gov/decision/chore/seed）+ 第三方无前缀赋 `Intake` Issue Type = 9 个日常开发 Issue Type。P0 §2.2.3 表中的"9 个用于日常开发"包含这 8 + Intake；第 10 个 `Acceptance` 是里程碑验收认证，不进入日常开发。

**范围枚举**（无原生替代，保留为标签）：

| scope | 含义 | 映射标签 |
|---|---|---|
| `PB01`-`PB19` | 种子分卷 | `scope:spec` |
| `infra` | 仓库基础设施 | `scope:infra` |
| `ci` | CI/CD | `scope:ci` |
| `cli` | CLI 命令 | `scope:cli` |
| `data` | 数据管线 | `scope:data` |
| `docs` | 文档系统 | `scope:docs` |
| `governance` | 治理系统 | `scope:governance` |

**衍生命名约定**：

| 对象 | 格式 | 示例 |
|---|---|---|
| Issue 标题 | `<type>(<scope>): <subject>` | `feat(PB10): Source Registry 注册接口` |
| 分支名 | `<type>/<issue#>-<slug>` | `feat/42-source-registry` |
| Commit | `<type>(<scope>): <subject>` + trailer | 见下方提交规范 |
| PR 标题 | `<type>(<scope>): <subject> (#<issue#>)` | `feat(PB10): Source Registry (#42)` |
| ADR 文件 | `docs/architecture/decisions/<issue#>-<slug>.md` | `docs/architecture/decisions/57-action-enum-archive.md` |

> **ADR 目录依据**：PolicyBase_03 §8 授权的 `docs/` 子目录为 product / architecture / specs /
> operations / development / governance（及条件性的 contracts）。**`docs/adr/` 不在其中**，
> 故 ADR 归入已授权的 `docs/architecture/` 之下，不新增顶层子目录、不需修改 PolicyBase_03。

**提交 trailer 格式**：
```
Assisted-by: Claude (model: glm-5.2, autonomous)
```
- `autonomous`：AI 自主完成（用户仅发起）
- `supervised`：用户深度参与指导

> **维度区分**：本节 trailer 是**治理层** AI 身份连续披露（P0 期间）；业务执行追溯（模型 backend/version、prompt hash、input/output hash、授权 ID 等）归 PolicyBase_13 §12 与 §4 统一内容工件 schema，**两者不重叠**——治理层回答"谁写了这段"，业务层回答"这个 candidate 怎么生成的"。本 trailer 不承担业务执行追溯责任。

### 2.2 治理元数据体系

> `P0-P8` 是 roadmap 阶段标识，不是优先级。Issue 优先级使用 `priority:blocker|high|medium|low` 标签；阶段使用 GitHub Milestone。本节的 G0-G4 是治理门禁，统一称为 `GOV-G0`…`GOV-G4`，不等同于 `GATE-P0-EXIT`。
>
> **与 PolicyBase 业务命令面的关系**：本节状态机标签（`do:*` / `state:blocked`）是 P0 治理域的**自治约定**，与 PolicyBase 业务命令面（`policybase` CLI）无关。P1 起交付的 `policybase` CLI 不读这些标签；这些标签仅在 GitHub Issue 自动化（CI workflows）和维护者工作流（`gh issue edit`）中使用。

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

#### 2.2.2 标签体系（19 个）

> **原生优先决策**：原方案 41 个标签中有 22 个可被 GitHub 原生功能替代或属于纯冗余，已删除。保留的 19 个标签均为无原生替代或原生功能 CLI 支持不足的场景。

| 类别 | 标签 | 色值 | 用途 | 保留理由 |
|---|---|---|---|---|
| 状态机 | `do:triage` | FBCA04 | 新建待分诊 | CLI 可过滤；Projects v2 Status 字段操作更复杂 |
| | `do:ready` | 0E8A16 | DoR 通过，可领取 | 同上 |
| | `do:in-progress` | 1D76DB | 开发中 | 同上 |
| | `do:review` | 5319E7 | PR 已开，待审核 | 同上 |
| | `do:acceptance` | 004773 | 审核通过，待验收 | 同上 |
| | `state:blocked` | D93F0B | 阻塞（Issue 仍 open） | close reason 不适用于 open Issue |
| 来源 | `origin:owner` | 0052CC | janssenkm 创建（**自动化触发条件**） | CLI 可过滤；author 字段不可与其他 label 组合查询 |
| | `origin:external` | 57606A | 第三方创建 | 同上 |
| 范围 | `scope:spec` | E4E669 | 种子规格修订 PB01-19 | 无原生替代 |
| | `scope:infra` | E4E669 | 仓库基础设施 | 同上 |
| | `scope:ci` | E4E669 | CI/CD | 同上 |
| | `scope:cli` | E4E669 | CLI 命令 | 同上 |
| | `scope:data` | E4E669 | 数据管线 | 同上 |
| | `scope:docs` | E4E669 | 文档系统 | 同上 |
| | `scope:governance` | E4E669 | 治理系统 | 同上 |
| 优先级 | `priority:blocker` | B60205 | 紧急/阻塞 | Issue 模板下拉可设；Projects v2 Priority 字段无法在模板中设置 |
| | `priority:high` | D93F0B | 高 | 同上 |
| | `priority:medium` | FBCA04 | 中 | 同上 |
| | `priority:low` | 0E8A16 | 低 | 同上 |

**已删除标签及替代方案**：

| 已删除标签 | 数量 | 替代方案 | 删除理由 |
|---|---|---|---|
| `type:feat/fix/docs/refactor/gov/decision/chore/seed` | 8 | GitHub Issue Types | 原生功能；type 标签从未被任何门禁消费 |
| `phase:p0`…`phase:p8` | 9 | GitHub Milestones | 原生功能；CLI 完整支持；有进度条/截止日期 UI |
| `state:accepted` | 1 | close reason `completed` | 原生功能；工作流已在 close 同时打标签，纯重复 |
| `state:rejected` | 1 | close reason `not planned` | 同上 |
| `origin:adopted` | 1 | Issue body 记录采纳来源 | 与 `origin:owner` 叠加冗余 |
| `needs-adoption` | 1 | Issue Type `Intake` | 原生功能；Intake 描述即「待采纳」 |
| `ac-met` | 1 | PR body AC 证据 | 生命周期过短；证据已强制在 PR 模板中 |
| **合计** | **22** | | |

#### 2.2.3 Issue Types（组织级共 10 个，其中 9 个用于日常开发）

Issue Type 是**组织级**配置（`NormBook` 组织，无硬上限；GraphQL 分页 `first` 上限100，按需可建），仓库继承可见。CI 在 Issue 创建时根据标题前缀自动赋值（第三方 Issue 赋 `Intake`）。

赋值通过 GraphQL `updateIssueIssueType` mutation 实现（input：`issueId!` + `issueTypeId`）。REST 的 issue create/update 不支持写入 type，`gh issue create` 也无 `--type` flag。

> **API 暴露注意**：Issue Type **仅 GraphQL `updateIssueIssueType` mutation 可写**；REST 端点（`GET /repos/{owner}/{repo}/issue-types`、`GET /repos/{owner}/{repo}/issues/{n}`）**写入不支持**。REST 读 Issue Type 时 `issue.type.name` 字段长期为 `null`，必须走 GraphQL `repository.issue.issueType.name`。本文件 issue-triage.yml 与 AC-P0-07b 均走 GraphQL，AC-P0-07b 已用变量传 `number`。

| Issue Type | 标题前缀 | 含义 | 实测状态 |
|---|---|---|---|
| Feature | `feat` | 新功能/新能力 | 已存在 |
| Bug | `fix` | 缺陷修复 | 已存在 |
| Documentation | `docs` | 文档（非种子规格） | 已存在 |
| Refactor | `refactor` | 重构（无行为变化） | 已存在 |
| Change | `gov` | 治理/流程/CI 变更 | 已存在 |
| Decision | `decision` | 架构决策（ADR） | 已存在 |
| Task | `chore` | 维护/依赖/工具 | 已存在 |
| Seed Revision | `seed` | 种子规格修订（PB01-19） | 已存在 |
| Intake | （第三方，无前缀） | 外部报告待采纳 | 已存在 |

> 第 10 个 Issue Type `Acceptance` 已存在，但用于里程碑验收认证（配合 project 的 `Certification State` 字段），**不参与**日常开发 Issue 的 type 分类，故不在上表 9 行内。
>
> **术语对齐**：本 Issue Type `Acceptance`（GitHub 组织级原生字段）与 PolicyBase_02 §15 模块清单中的 `Acceptance` 模块同名同义——后者指"里程碑/能力认证窗口"的业务模块，前者是该业务模块在 GitHub 平台上的原生表达载体。二者非两个概念，业务 owner 仍是 PolicyBase_02 模块。
>
> 2026-08-08 实测：以上 10 个 Issue Type 在 `NormBook` 组织中**已全部存在**，§4.3b 无需创建，仅需验证。

#### 2.2.4 Milestones（9 个，原生）

替代 `phase:p0`…`phase:p8` 标签。`gh` CLI 完整支持创建、赋值（`gh issue create --milestone`）和过滤。

标题**不含逗号**：`gh` 多处按逗号分割列表参数，含逗号的名称在批量场景易被误切分。阶段名称以 PolicyBase_02 §4 为准，逗号替换为空格。

| Milestone 标题 | 对应 PolicyBase_02 阶段 |
|---|---|
| `P0 Repository Governance Bootstrap` | P0 |
| `P1 Project Skeleton and Contract Foundation` | P1 |
| `P2 Identity Dedup and Versioned Ingest` | P2 |
| `P3 First Source and Content Closure` | P3 |
| `P4 Index Search and Export` | P4 |
| `P5 Editorial and CLI Completion` | P5 |
| `P6 Authorized Model Refinement` | P6 |
| `P7 Advanced Attachment and Layout` | P7 |
| `P8 Source and Data Expansion` | P8 |

#### 2.2.5 Projects v2 同步（可选增强）

仓库已有 Projects v2「PolicyBase Development」（number=1，org 级）。`do:*` / `state:blocked` 标签保留用于 CLI 自动化，CI 在切换标签时同步更新 Projects v2 `Status` 字段，供看板可视化。

| 标签 / 事件 | Projects v2 Status 选项 | 实测存在 |
|---|---|---|
| `do:triage` | Triage | 是 |
| `do:ready` | Ready | 是 |
| `do:in-progress` | In progress | 是 |
| `do:review` | In review | 是 |
| `do:acceptance` | Acceptance | 是 |
| `state:blocked` | Blocked | 是 |
| close `completed` | Done | 是 |
| close `not planned` | Not planned | 是 |

> 以上 8 个映射经 2026-08-08 实测，与 project 现有 `Status` 选项**完全匹配**，无需新建选项。

**`priority:*` 同步暂不实现**：project 的 `Priority` 字段虽为 SINGLE_SELECT，但**实测选项为空**（0 options）。在用户手工添加 blocker/high/medium/low 四个选项之前，同步会因找不到 option 而失败。`Phase` 字段同样为空选项，且阶段已由 Milestone 表达，不纳入同步。

> **启用 `priority:*` 同步的前置步骤**（可选，P0 不要求）：
> 1. 在 Projects v2「PolicyBase Development」的 `Priority` 字段中手工添加四个选项：`blocker`、`high`、`medium`、`low`
> 2. 验证：
>    ```bash
>    gh api graphql -f query='{organization(login:"NormBook"){projectV2(number:1){fields(first:30){nodes{... on ProjectV2SingleSelectField{name options{name}}}}}}}' \
>      --jq '.data.organization.projectV2.fields.nodes[]|select(.name=="Priority")|[.options[].name]|join(", ")'
>    # 期望输出：blocker, high, medium, low
>    ```
> 3. 在 `label-sync.yml` 中把 `Status` 的同步逻辑复制一份指向 `Priority` 字段，标签名去掉 `priority:` 前缀即为选项名
>
> 未完成上述步骤时，不要在 `label-sync.yml` 中加入 `priority` 分支——找不到 option 会让每次标签变更都产生一条 warning 噪音。

> **权限前提（必读）**：Projects v2 位于组织级别，**GitHub Actions 的 `GITHUB_TOKEN` 无任何 permissions 键可授予 org-level project 写权限**（`permissions:` 合法键中不存在 `organization`）。因此 `label-sync.yml` **必须**使用 PAT：
>
> 1. 创建 classic PAT，勾选 `project`（读写组织 project）与 `repo`
> 2. 存为仓库 secret：`gh secret set PROJECTS_TOKEN -R NormBook/PolicyBase`
> 3. workflow 中通过 `github-token: ${{ secrets.PROJECTS_TOKEN }}` 传入
>
> 未配置 `PROJECTS_TOKEN` 时，`label-sync.yml` 会记录 warning 并跳过，**不阻塞主流程**（标签是权威源，Projects v2 仅为展示镜像）。

### 2.3 治理门禁分层（GOV-G0～GOV-G4）

| 层 | 名称 | 时机 | 检查内容 | 执行方 |
|---|---|---|---|---|
| GOV-G0 | Session | AI 会话启动 | 读 AGENTS.md + `verify_seed_set.py` 通过 + 确认 origin:owner | AI 本地自检 |
| GOV-G1 | Admission | Issue 创建时 | 自动打 origin 标签 + 赋 Issue Type + 解析标题打 scope 标签 + 同步 Projects v2 | CI `issue-triage.yml` |
| GOV-G2 | DoR | Issue 分诊时 | 标题前缀合法 + AC 已定义 + 规格引用已填 + scope 有效 | AI 检查并评论 DoR 结论；**用户确认后** AI 执行 `do:ready` 标签切换 |
| GOV-G3 | PR/CI | PR 提交时 | verify-seeds 通过 + ai-disclosure 通过（PR body 披露 **且每个 commit 带 trailer**）+ dor-check 通过 | CI `pr-gates.yml`（required status checks） |
| GOV-G4 | Acceptance | merge 前 | AC 命令全部通过 + `do:acceptance` 标签 | AI 运行 AC + 用户确认 merge |

### 2.4 自动化流程

#### 2.4.1 Owner Issue 主流程（janssenkm 创建的 Issue）

```
1. janssenkm 创建 Issue（填模板，标题带前缀）
       │
2. [GOV-G1] CI 自动处理：打 origin:owner + do:triage + scope:* 标签 + 赋 Issue Type + 同步 Projects v2
       │
3. [GOV-G0+GOV-G2] AI 分诊 + 用户确认 Ready：
   - AI 检查 DoR（标题前缀、AC、规格引用），在 Issue 评论中给出分诊结论
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
   - git commit（带 Assisted-by trailer）
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

> **维度区分**：`--squash` 仅影响 Git 分支图（commit 历史线性化，配合 §4.12 的 `required_linear_history: true`）；业务写入锁归 PolicyBase_09 §11 固定顺序（global identity registry lock → doc lock → P4 索引事务）。P0 阶段不涉及 edition 写入，二者正交；`--squash` 不绕过也不授权任何业务门禁。

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
   │   [REMOTE-AUTO] AI 创建新 Issue（作者=janssenkm -> origin:owner）：
   │     gh issue create \
   │       --title "<proposed title>" \
   │       --body "采纳自 #<原#>\n\n<原始内容摘要>\n\n原始 Issue: #<原#>" \
   │       --label "do:ready,scope:xxx,priority:xxx"
   │   [REMOTE-AUTO] CI 自动补打 origin:owner + 赋 Issue Type（因为作者是 janssenkm）
   │   [REMOTE-AUTO] AI 关闭原 Issue：
   │     gh issue close <原#> --comment "采纳 via #<新#>，本 Issue 关闭。后续开发在新 Issue 推进。" --reason "not planned"
   │   -> 新 Issue 进入 owner 主流程 step 4
   │
   │   > **与 PolicyBase_08 §9 身份层 reviewed decision 的关系**：本流程的采纳新 Issue 是**治理层决策**（确定开发入口），不触发 PolicyBase_08 §9 身份层 reviewed decision（判定两份 candidate 是否同一文献）。二者正交，参见 PolicyBase_08 §16 不变量 6（身份层与内容层 reviewed decision 不得混用）与不变量 7（§6 observation 更新状态机与 §9 身份层 reviewed decision 不得同时取值）。第三方 Issue 采纳**不写 `alias_of` 关系**，关系索引表归 PolicyBase_06 §10 / PolicyBase_14 §12。
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
2. 读取 `seeds/PolicyBase_01.md`（权威地图）+ `seeds/PolicyBase_03.md`（协作约定）
3. 运行 `python3 seeds/verify_seed_set.py`，确认输出 `OK seed_set_verified: 19 volumes verified`
4. `gh auth status` 确认已认证为 janssenkm
5. 查询可领取的 Issue：
   `gh issue list --label "origin:owner" --label "do:ready" --state open`
6. 若无 `do:ready` Issue，查询 `do:triage` + `origin:owner` 进行分诊
7. 若有 `origin:external` + `do:triage` Issue（Issue Type 为 Intake），进行只读分诊分析

---

## 3. 前置手动步骤 [MANUAL-AUTH]

> 以下步骤需用户在终端中手动执行。AI 不封装脚本，仅提供原始命令。

### 3.1 安装 gh CLI（若未安装）

```bash
# Ubuntu/Debian
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# 验证
gh --version
```

### 3.2 认证

> **执行时提示**：AI 在到达此步骤时必须暂停，向用户输出以下引导：
>
> ```
> [MANUAL-AUTH] 需要你完成 GitHub 认证。请选择以下方式之一：
>
> 方式 A（推荐）：浏览器交互
>   gh auth login
>   选择 GitHub.com -> HTTPS -> Yes -> Login with a web browser
>
> 方式 B：手动创建 Token
>   访问 https://github.com/settings/tokens/new
>   勾选 scope: repo, workflow, read:org
>   详见下方「Token 权限清单」
>
> 完成后请回复「已认证」，我会继续验证。
> ```

#### 方式 A：浏览器交互（推荐）

```bash
gh auth login
# 选择：GitHub.com -> HTTPS -> Yes (git credentials) -> Login with a web browser
# 复制 one-time code，在浏览器中粘贴授权
```

浏览器方式授权的 scope 由 `gh` 自动请求，通常包含 `repo`、`workflow`、`read:org`。如果后续操作遇到权限不足，改用方式 B 重新认证。

#### 方式 B：手动创建 Token

**步骤 1：创建 Classic PAT**

浏览器访问 `https://github.com/settings/tokens/new`（或 Settings -> Developer settings -> Personal access tokens -> Tokens (classic) -> Generate new token (classic)）

**Token 权限清单**：

| Scope | 必需 | 用途 | P0 中使用的命令 |
|---|---|---|---|
| `repo` | 是 | 仓库完全控制；推送代码、创建标签/Issue/PR/Milestone、分支保护 | `git push`、`gh label create`、`gh issue create`、`gh api .../branches/main/protection` |
| `workflow` | 是 | 创建/更新 GitHub Actions 工作流文件 | 推送 `.github/workflows/*.yml` |
| `read:org` | 是 | 读取组织信息；读取组织级 Issue Types | `gh api orgs/NormBook`、读 `issue-types` |
| `project` | 是 | 读写组织级 Projects v2 | `label-sync.yml` 的 `PROJECTS_TOKEN` |
| `admin:org` | 条件 | **仅当需要新建 Issue Type 时**。本方案 10 个 Issue Type 已全部存在，正常执行**不需要**；若组织被重建或类型被删除，则必需 | `createIssueType` mutation |
| `delete_repo` | 否 | 删除仓库（仅清理时需要） | — |

> **实测参考**：当前会话 token 的 scopes 为 `admin:org, gist, project, repo, workflow`，满足全部要求。用 `gh auth status` 或下方脚本自查。

> **细粒度 PAT（Fine-grained PAT）路径**：若使用细粒度 Token 而非 classic PAT，需在 **Resource owner 选择 `NormBook` 组织**（否则无法操作组织仓库），并授予：
>
> | 权限 | 级别 | 用途 |
> |---|---|---|
> | Administration | Read and write | 分支保护 |
> | Contents | Read and write | 推送代码 |
> | Issues | Read and write | Issue、标签、Milestone |
> | Pull requests | Read and write | PR |
> | Workflows | Read and write | `.github/workflows/*` |
> | Metadata | Read | 必选基础权限 |
> | Organization permissions → Projects | Read and write | Projects v2 同步 |

> **Fine-grained PAT 的 `Projects` 权限层级说明**：
> - **Organization permissions → Projects**：Read and Write（控制 organization-level projects，即本方案 project "PolicyBase Development" 所需的权限）
> - **Repository permissions → Projects**：Read and Write（控制 repository-level projects，独立可设；本方案不涉及，但若同时使用需另开）
>
> 两者**独立可设**，互不蕴含。label-sync.yml 必须勾选 **Organization permissions → Projects: Read and Write**。
>
> **组织策略拦截**：NormBook 组织若在 Settings → Personal access tokens 中未批准 classic PAT 或未启用细粒度 PAT，即使权限齐全也会返回 403。这是新建组织最常见的失败原因，遇 403 先查组织 PAT 策略。

> **安全警告**：
> - Token 等同于你的账户密码，拥有 `repo` scope 的 Token 可读写你所有仓库
> - **不要**将 Token 写入任何文件、commit、日志或聊天记录
> - **不要**将 `export GH_TOKEN=ghp_...` 命令保存到 `.bashrc`/`.zshrc`（会持久化到磁盘）
> - 建议设置 Token 过期时间（建议 30 天），到期后重新生成
> - AI 不得代为创建、存储或传输 Token

**步骤 2：设置环境变量并认证**

```bash
# 在当前终端会话中设置（关闭终端后失效，不会持久化到磁盘）
export GH_TOKEN=ghp_在此粘贴你的token

# 验证认证状态和 scope
gh auth status
```

期望输出包含：
```
github.com
  ✓ Logged in to github.com account janssenkm
  - Active account: true
  - Git operations protocol: https
  - Token: ghp_****************************
  - Token scopes: repo, workflow, read:org
```

**步骤 3：权限验证脚本**

```bash
#!/bin/bash
# verify_github_token.sh — 验证 GitHub 认证与权限是否满足 P0 执行要求
# 手动执行：bash verify_github_token.sh
# 兼容方式 A（gh auth login 浏览器授权）与方式 B（GH_TOKEN 环境变量）

set -uo pipefail

FAILED=0
note_fail() { echo "  FAIL: $*"; FAILED=1; }

echo "=== GitHub 认证与权限验证 ==="

# 1. 认证状态（不强制要求 GH_TOKEN：方式 A 用 keyring，无此环境变量）
echo ">>> 检查认证状态..."
if ! gh auth status >/dev/null 2>&1; then
  echo "FAIL: 未认证"
  echo "  方式 A: gh auth login"
  echo "  方式 B: export GH_TOKEN=<your token>"
  exit 1
fi
echo "OK: 已认证"

# 2. 用户身份
echo ">>> 检查用户身份..."
GH_LOGIN=$(gh api user --jq .login 2>/dev/null || echo "")
if [ "$GH_LOGIN" != "janssenkm" ]; then
  echo "FAIL: 认证用户为 '$GH_LOGIN'，期望 'janssenkm'"
  exit 1
fi
echo "OK: 认证用户 = janssenkm"

# 3. Token scopes（精确匹配，避免 repo 被 public_repo/read:org 子串误命中）
echo ">>> 检查 Token scopes..."
SCOPE_HEADER=$(gh api user -i 2>/dev/null | tr -d '\r' | grep -i "^x-oauth-scopes:" | cut -d: -f2- || echo "")
if [ -z "$SCOPE_HEADER" ]; then
  echo "  WARN: 无法读取 x-oauth-scopes 头"
  echo "        细粒度 PAT 与部分 OAuth 流程不返回该头，属正常情况。"
  echo "        将改用能力探测（步骤 4-6）判定权限是否足够。"
else
  echo "  Token scopes:$SCOPE_HEADER"
  # 逗号分隔后逐项精确比对
  IFS=',' read -ra HAVE <<< "$(echo "$SCOPE_HEADER" | tr -d ' ')"
  # GitHub scope 是分层的：admin:org 蕴含 read:org/write:org；repo 蕴含 public_repo。
  has_scope() {
    local want="$1" s
    for s in "${HAVE[@]}"; do
      [ "$s" = "$want" ] && return 0
      case "$want" in
        read:org)  { [ "$s" = "admin:org" ] || [ "$s" = "write:org" ]; } && return 0 ;;
        project)   [ "$s" = "read:project" ] && continue ;;
      esac
    done
    return 1
  }
  for REQUIRED in repo workflow read:org project; do
    if has_scope "$REQUIRED"; then
      echo "  OK: $REQUIRED"
    else
      note_fail "缺少 scope '$REQUIRED'（访问 https://github.com/settings/tokens 重新生成）"
    fi
  done
fi

# 4. 组织访问
echo ">>> 检查 NormBook 组织..."
if gh api orgs/NormBook --jq .login >/dev/null 2>&1; then
  echo "  OK: NormBook 组织可访问"
else
  note_fail "无法访问 NormBook 组织（确认组织已创建、Token 有 read:org、组织 PAT 策略已放行）"
fi

# 5. 仓库 admin 权限（分支保护必需）
echo ">>> 检查仓库管理权限..."
IS_ADMIN=$(gh api repos/NormBook/PolicyBase --jq .permissions.admin 2>/dev/null || echo "")
if [ "$IS_ADMIN" = "true" ]; then
  echo "  OK: 对 NormBook/PolicyBase 有 admin 权限（可配置分支保护）"
elif [ -z "$IS_ADMIN" ]; then
  note_fail "仓库 NormBook/PolicyBase 不可访问（确认仓库存在且 Token 有 repo scope）"
else
  note_fail "对 NormBook/PolicyBase 无 admin 权限，无法配置分支保护（§4.12）"
fi

# 6. Issue Types 可读（组织级，日常开发需 9 个 + Acceptance）
echo ">>> 检查 Issue Types..."
TYPE_COUNT=$(gh api repos/NormBook/PolicyBase/issue-types --jq 'length' 2>/dev/null || echo "0")
if [ "$TYPE_COUNT" -ge 10 ] 2>/dev/null; then
  echo "  OK: Issue Types 可读，共 $TYPE_COUNT 个"
else
  echo "  WARN: Issue Types 数量为 $TYPE_COUNT（期望 >= 10）"
  echo "        若需新建类型，Token 还需 admin:org scope（见 §4.3b）"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "=== 全部验证通过 ==="
  exit 0
else
  echo "=== 存在 FAIL 项，请修复后重试 ==="
  exit 1
fi
```

> **执行时机**：AI 在执行 §4 之前必须运行此验证脚本（或逐条手动执行上述检查）。任何一项 FAIL 都必须暂停，等待用户修复后继续。

### 3.3 创建 NormBook 组织（若尚未创建）

```
浏览器访问 https://github.com/organizations/new
- 组织名：NormBook
- 计划：Free
- 联系邮箱：可选
- 完成创建
```

### 3.4 环境验证

```bash
gh auth status                         # 已认证
gh api user --jq .login               # 输出 janssenkm
gh api orgs/NormBook --jq .login      # 输出 NormBook
```

---

## 4. 自动初始化执行 [LOCAL-AUTO + REMOTE-AUTO]

> 以下步骤按本地与远程副作用分别授权。执行前确认 3.4 环境验证通过；远程操作需用户已认证并明确授权。

### 4.1 git init + .gitignore

```bash
cd /home/yangsen/Dropbox/workspaces/NormBook/PolicyBase.git
git init -b main
```

创建 `.gitignore`：

```gitignore
# 分析素材（不入库）
tmp/

# 备份
seeds-backup-before-cleanup.tar.gz

# Python
*.pyc
__pycache__/
*.egg-info/

# 环境与密钥
.env
.env.*

# 系统
.DS_Store
*.log
```

### 4.2 首次提交 + 关联远程仓库

> **注意**：`NormBook/PolicyBase` 仓库**已存在**（public，空仓库）。不要使用 `gh repo create`，它会因仓库已存在而失败。改用 `git remote add`。

```bash
git add .
git commit -m "chore(infra): 初始化仓库，导入 19 卷种子规格

- seeds/PolicyBase_01-19.md（19 卷业务规格，唯一主权威）
- seeds/P0-GITHUB-INIT.md（P0 治理引导任务定义）
- seeds/provinces/（31 省调研数据，proposed input）
- seeds/verify_seed_set.py（种子校验脚本）
- tmp/ 已 gitignore（分析素材不入库）

Assisted-by: Claude (model: glm-5.2, supervised)"
```

```bash
# 关联已存在的远程仓库并推送
git remote add origin https://github.com/NormBook/PolicyBase.git
git push -u origin main

# 验证
gh repo view NormBook/PolicyBase --json url,visibility --jq '.url, .visibility'
git remote -v
```

> 若 `git remote add` 报 `remote origin already exists`，用 `git remote set-url origin https://github.com/NormBook/PolicyBase.git` 替代。
>
> 若仓库意外不存在（例如在全新组织中重放本文件），才使用：
> `gh repo create NormBook/PolicyBase --public --source=. --remote=origin --push`

### 4.3 创建标签体系

```bash
# ============ 状态机标签（6 个）============
# state:accepted/state:rejected 已删除，改用 GitHub 原生 close reason
gh label create "do:triage"      --color FBCA04 --description "新建待分诊" --force
gh label create "do:ready"       --color 0E8A16 --description "DoR通过可领取" --force
gh label create "do:in-progress" --color 1D76DB --description "开发中" --force
gh label create "do:review"      --color 5319E7 --description "PR已开待审核" --force
gh label create "do:acceptance"  --color 004773 --description "审核通过待验收" --force
gh label create "state:blocked"  --color D93F0B --description "阻塞需解除" --force

# ============ 来源标签（2 个，自动化触发依据）============
# origin:adopted 已删除（与 origin:owner 叠加冗余，采纳来源记入 Issue body）
# needs-adoption 已删除（改用 Issue Type: Intake）
gh label create "origin:owner"    --color 0052CC --description "janssenkm创建可触发自动化" --force
gh label create "origin:external" --color 57606A --description "第三方创建需分诊" --force

# ============ 范围标签（7 个，无原生替代）============
gh label create "scope:spec"       --color E4E669 --description "种子规格修订PB01-19" --force
gh label create "scope:infra"      --color E4E669 --description "仓库基础设施" --force
gh label create "scope:ci"         --color E4E669 --description "CI/CD" --force
gh label create "scope:cli"        --color E4E669 --description "CLI命令" --force
gh label create "scope:data"       --color E4E669 --description "数据管线" --force
gh label create "scope:docs"       --color E4E669 --description "文档系统" --force
gh label create "scope:governance" --color E4E669 --description "治理系统" --force

# ============ 优先级标签（4 个）============
# Projects v2 有 Priority 字段，但 Issue 模板无法设置 Projects v2 字段，保留标签
gh label create "priority:blocker" --color B60205 --force
gh label create "priority:high" --color D93F0B --force
gh label create "priority:medium" --color FBCA04 --force
gh label create "priority:low" --color 0E8A16 --force

# type:* 标签（8 个）已删除，改用 GitHub 原生 Issue Types
# phase:p0-p8 标签（9 个）已删除，改用 GitHub 原生 Milestones
# ac-met 标签（1 个）已删除，AC 证据在 PR body 中

# 验证
gh label list --limit 50 --json name --jq 'length'   # 期望 >= 19（自建 19 + GitHub 默认标签）
```

### 4.3b 验证 Issue Types（组织级，已存在）

> **2026-08-08 实测：10 个 Issue Type 已在 `NormBook` 组织中全部存在，本节只需验证，无需创建。**
>
> Issue Type 是**组织级**配置，仓库继承可见。因此可用仓库级端点读取，但创建/修改必须在组织级进行，且需 `admin:org` 权限。

```bash
# 验证（REST 仓库级端点可读，继承自组织）
gh api repos/NormBook/PolicyBase/issue-types --jq '[.[].name] | sort | join(", ")'
# 期望包含：Acceptance, Bug, Change, Decision, Documentation, Feature, Intake, Refactor, Seed Revision, Task

gh api repos/NormBook/PolicyBase/issue-types --jq 'length'
# 期望：10
```

<details>
<summary>仅当 Issue Type 缺失时展开（需 <code>admin:org</code> scope）</summary>

创建走 GraphQL `createIssueType`（input：`ownerId!`、`name!`、`isEnabled!`、`description`、`color`）。
`color` 合法枚举值：`GRAY | BLUE | GREEN | YELLOW | ORANGE | RED | PINK | PURPLE`。

```bash
# 取组织 node_id（注意：ownerId 必须是组织的 ID，不是仓库的）
ORG_ID=$(gh api graphql -f query='{ organization(login: "NormBook") { id } }' --jq '.data.organization.id')

# 示例：创建 Documentation
gh api graphql -f query="
mutation {
  createIssueType(input: {
    ownerId: \"$ORG_ID\",
    name: \"Documentation\",
    description: \"Documentation changes (non-seed-spec)\",
    color: BLUE,
    isEnabled: true
  }) { issueType { id name } }
}"
```

同理创建 `Refactor`（`color: YELLOW`）与 `Seed Revision`（`color: PURPLE`）。

</details>

### 4.3c 创建 Milestones（9 个，原生）

```bash
# 替代 phase:p0-p8 标签。标题不含逗号（见 §2.2.4）。
for M in \
  "P0 Repository Governance Bootstrap" \
  "P1 Project Skeleton and Contract Foundation" \
  "P2 Identity Dedup and Versioned Ingest" \
  "P3 First Source and Content Closure" \
  "P4 Index Search and Export" \
  "P5 Editorial and CLI Completion" \
  "P6 Authorized Model Refinement" \
  "P7 Advanced Attachment and Layout" \
  "P8 Source and Data Expansion" ; do
  gh api repos/NormBook/PolicyBase/milestones -X POST -f title="$M" -f state="open" \
    --jq '"created: \(.title)"' || echo "skip (already exists): $M"
done

# 验证
gh api repos/NormBook/PolicyBase/milestones --jq 'length'   # 期望 9
```

### 4.4 自举流程（§4.4 起不再豁免 issue-first）

> 第 1 段（§4.1–§4.3c）已完成：仓库有内容、19 标签、9 Milestone、10 Issue Type 就绪。
> Issue 能力此刻已具备，因此 §4.5–§4.10 的治理文件**必须通过 PR 合入**，不得直推 main。

**自举执行序列**：

```bash
# 步骤 1：创建自举 Issue（此时 CI 尚未部署，标签需手工指定）
gh issue create \
  --title "gov(governance): 初始化 issue-first 治理基础设施" \
  --milestone "P0 Repository Governance Bootstrap" \
  --label "do:ready,origin:owner,scope:governance,priority:blocker" \
  --body "本 Issue 是 P0 自举，第 1 段基础设施（仓库/标签/Milestone/Issue Type）已完成，本 Issue 起遵循 issue-first。

## 范围
§4.5-§4.10：Issue 模板、PR 模板、CODEOWNERS、三个 workflow、AGENTS.md 及软链。

## 说明
本 Issue 创建时 issue-triage.yml 尚未部署，故 origin:owner / scope:governance
标签为手工指定，Issue Type 需手工设置为 Change。此为自举期一次性例外，
后续 Issue 均由 CI 自动处理。

## 验收标准
见 seeds/P0-GITHUB-INIT.md §5 的 AC-P0-08（门禁有效性实证）。"

# 记下 Issue 号，下称 <N>

# 步骤 2：手工设置 Issue Type 为 Change（CI 尚未部署）
ISSUE_ID=$(gh api graphql -f query="{repository(owner:\"NormBook\",name:\"PolicyBase\"){issue(number:<N>){id}}}" --jq '.data.repository.issue.id')
TYPE_ID=$(gh api graphql -f query='{repository(owner:"NormBook",name:"PolicyBase"){issueTypes(first:20){nodes{id name}}}}' --jq '.data.repository.issueTypes.nodes[]|select(.name=="Change")|.id')
gh api graphql -f query="mutation{updateIssueIssueType(input:{issueId:\"$ISSUE_ID\",issueTypeId:\"$TYPE_ID\"}){issue{issueType{name}}}}"

# 步骤 3：开分支
git checkout -b gov/<N>-governance-bootstrap
gh issue edit <N> --remove-label "do:ready" --add-label "do:in-progress"

# 步骤 4：完成 §4.5 - §4.10 的所有文件编写，然后提交
#         （commit 命令见 §4.11）

# 步骤 5：推送并开 PR
git push -u origin gov/<N>-governance-bootstrap
gh pr create --draft \
  --title "gov(governance): 初始化 issue-first 治理基础设施 (#<N>)" \
  --base main \
  --body "Closes #<N>

## AI 披露
- [x] 本 PR 包含 AI 辅助生成的代码
- [x] 所有 commit 包含 Assisted-by trailer

AI 模型：Claude (model: glm-5.2, supervised)"
gh issue edit <N> --remove-label "do:in-progress" --add-label "do:review"

# 步骤 6：观察 pr-gates 三个 check（这是门禁有效性的第一份真实证据）
gh pr checks <PR#> --watch
```

> **预期与排障**：本 PR 会触发它自己引入的 `pr-gates.yml`（`pull_request` 事件从 merge ref 读取 workflow，新增 workflow 在引入它的 PR 上即生效）。
> - `verify-seeds` 应绿
> - `ai-disclosure` 应绿（PR body 含 `Closes #` 与已勾选的 AI 复选框）
> - `dor-check` 应绿（Issue 此时为 `do:review`，在白名单内）
>
> 任一红灯都必须修复后 re-push，**不得绕过**。三个 check 全绿即为 `AC-P0-08` 的实际证据。

> **步骤 7（merge 后）**：回到 §4.12 配置分支保护。**顺序不可颠倒**——若先设分支保护再开自举 PR，required checks 尚未有历史记录，可能阻塞该 PR。

### 4.5 创建 Issue 模板

创建 `.github/ISSUE_TEMPLATE/config.yml`：

```yaml
blank_issues_enabled: false
contact_links:
  - name: 💬 讨论与提问
    url: https://github.com/NormBook/PolicyBase/discussions
    about: 问答与讨论请使用 Discussions，Issue 仅用于可追踪的变更
```

创建 `.github/ISSUE_TEMPLATE/feature.yml`：

```yaml
name: "\U0001F680 功能需求"
description: 提出新功能或能力
labels: ["do:triage"]
title: "feat(scope): "
body:
  - type: dropdown
    id: scope
    attributes:
      label: 影响范围
      description: 选择受影响的模块或种子分卷
      options:
        - spec (种子规格 PB01-19)
        - infra (基础设施)
        - ci (CI/CD)
        - cli (CLI 命令)
        - data (数据管线)
        - docs (文档系统)
        - governance (治理系统)
    validations:
      required: true
  - type: input
    id: spec_ref
    attributes:
      label: 规格引用
      description: 关联的 PolicyBase 分卷与章节（如 PolicyBase_10 §source-registry）
      placeholder: PolicyBase_NN §section
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
        每条 AC 必须包含可原样执行的命令与可观察断言（格式见 PolicyBase_03 §9）。
        未执行时省略 exit code 行，写 evidence: planned；执行后再填真实退出码。
        格式示例（尚未执行）：
        AC-1
        command: python3 seeds/verify_seed_set.py
        assert: 输出包含 "OK seed_set_verified: 19 volumes verified"
        evidence: planned
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

创建 `.github/ISSUE_TEMPLATE/bug.yml`：

```yaml
name: "\U0001F41E 缺陷报告"
description: 报告缺陷或异常行为
labels: ["do:triage"]
title: "fix(scope): "
body:
  - type: dropdown
    id: scope
    attributes:
      label: 影响范围
      options:
        - spec (种子规格 PB01-19)
        - infra (基础设施)
        - ci (CI/CD)
        - cli (CLI 命令)
        - data (数据管线)
        - docs (文档系统)
        - governance (治理系统)
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: 缺陷描述
      description: 现象、复现步骤、预期 vs 实际
    validations:
      required: true
  - type: textarea
    id: ac
    attributes:
      label: 验收标准（AC）
      description: 修复后应满足的可执行验收命令
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

创建 `.github/ISSUE_TEMPLATE/governance.yml`：

```yaml
name: "\U0001F527 治理变更"
description: 治理流程、CI、门禁、模板变更
labels: ["do:triage"]
title: "gov(governance): "
body:
  - type: textarea
    id: description
    attributes:
      label: 变更描述
      description: 改什么、为什么改、影响哪些现有规则
    validations:
      required: true
  - type: textarea
    id: ac
    attributes:
      label: 验收标准（AC）
      description: 变更后应满足的可执行验收命令
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

创建 `.github/ISSUE_TEMPLATE/decision.yml`：

```yaml
name: "\U0001F4DC 架构决策（ADR）"
description: 记录架构或设计决策
labels: ["do:triage"]
title: "decision(scope): "
body:
  - type: input
    id: scope
    attributes:
      label: 决策范围
      description: 关联的 PolicyBase 分卷（如 PB04）
      placeholder: PolicyBase_NN
    validations:
      required: true
  - type: textarea
    id: context
    attributes:
      label: 背景
      description: 为什么需要这个决策、面临什么问题
    validations:
      required: true
  - type: textarea
    id: decision
    attributes:
      label: 决策内容
      description: 决定了什么、备选方案是什么、为什么选这个
    validations:
      required: true
  - type: textarea
    id: ac
    attributes:
      label: 验收标准（AC）
      description: 决策落地后应满足的可执行验收命令
    validations:
      required: true
```

创建 `.github/ISSUE_TEMPLATE/seed-revision.yml`：

```yaml
name: "\U0001F4DA 种子规格修订"
description: 修订 PolicyBase_NN 种子分卷内容
labels: ["do:triage"]
title: "seed(PBNN): "
body:
  - type: input
    id: volume
    attributes:
      label: 分卷编号
      description: 要修订的种子分卷（如 PolicyBase_12）
      placeholder: PolicyBase_NN
    validations:
      required: true
  - type: textarea
    id: changes
    attributes:
      label: 修订内容
      description: 改什么、为什么改、影响哪些跨卷引用
    validations:
      required: true
  - type: textarea
    id: ac
    attributes:
      label: 验收标准（AC）
      description: |
        修订后必须通过种子校验（格式见 PolicyBase_03 §9）。
        未执行时省略 exit code 行，写 evidence: planned。
        AC-1
        command: python3 seeds/verify_seed_set.py
        assert: 输出包含 "OK seed_set_verified: 19 volumes verified"
        evidence: planned
    validations:
      required: true
```

### 4.6 创建 PR 模板

创建 `.github/PULL_REQUEST_TEMPLATE.md`：

```markdown
## 关联 Issue

Closes #

## 变更说明

<!-- 简述改了什么、为什么 -->

## AI 披露

- [ ] 本 PR 包含 AI 辅助生成的代码
- [ ] 所有 commit 包含 `Assisted-by:` trailer
- [ ] 已披露 AI 模型名称与自主级别

> AI 模型：<!-- 如 Claude (model: glm-5.2, autonomous) -->
> 披露是**连续的**：每轮 review 新增的 commit 和回复也需声明 AI 参与。

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

- [ ] `python3 seeds/verify_seed_set.py` 通过
- [ ] 无 TODO/FIXME/TBD/XXX 残留
- [ ] 分支命名符合 `<type>/<issue#>-<slug>`
- [ ] 未混合其他 Issue 的变更
```

### 4.7 创建 CODEOWNERS

> **当前无强制力，保留为协作期占位**：本仓库当前是单人开发，唯一 owner 同时是唯一 PR 作者。
> GitHub 明确规定「Pull request authors cannot approve their own pull requests」，且 §4.12 设的是
> `required_pull_request_reviews: null`，因此 CODEOWNERS 此刻**既不会触发评审请求、也无任何阻塞力**。
>
> 保留它的理由：一旦引入协作者或将 `required_pull_request_reviews` 打开，该文件立即生效，
> 无需再补建。**不要**把它当作 P0 期间的有效门禁写进验收依据。

创建 `.github/CODEOWNERS`：

```
# PolicyBase CODEOWNERS
# 单人开发期：所有路径归属 janssenkm；当前无强制力（见 §4.7 说明）。
# 引入协作者后可按分卷/子系统拆分归属。

* @janssenkm

# 种子规格（唯一主权威，修改须通过 Issue + PR）
seeds/                      @janssenkm

# 治理配置（门禁/CI/模板，修改须通过 gov 类型 Issue）
.github/                    @janssenkm
AGENTS.md                   @janssenkm

# 正式文档目录（子目录划分依据 PolicyBase_03 §8）
docs/product/               @janssenkm
docs/architecture/          @janssenkm
docs/specs/                 @janssenkm
docs/operations/            @janssenkm
docs/development/           @janssenkm
docs/governance/            @janssenkm
docs/contracts/             @janssenkm
```

### 4.8 创建 CI Workflows

创建 `.github/workflows/issue-triage.yml`：

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
            const OWNER = 'janssenkm';
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
            const VALID_SCOPES = ['infra','ci','cli','data','docs','governance'];
            const m = title.match(/^(feat|fix|docs|refactor|gov|decision|chore|seed)\(([^)]+)\)/);
            let scopeResolved = false;
            if (m) {
              const scope = m[2].toLowerCase();
              if (/^pb\d{2}$/.test(scope)) {
                labels.push('scope:spec');
                scopeResolved = true;
              } else if (VALID_SCOPES.includes(scope)) {
                labels.push('scope:' + scope);
                scopeResolved = true;
              }
            }

            // --- 打标签（空数组会导致 422，必须守卫）---
            // 模板已预置 do:triage，addLabels 对重复标签幂等，无需去重。
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
              chore: 'Task',
              seed: 'Seed Revision'
            };

            let targetTypeName = null;
            if (isOwner && m && titlePrefixToType[m[1]]) {
              targetTypeName = titlePrefixToType[m[1]];
            } else if (!isOwner) {
              targetTypeName = 'Intake';
            }

            if (targetTypeName) {
              try {
                // 查询 repo 的 Issue Types 获取 node_id
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
                  // 获取 Issue 的 node_id
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

            // --- scope 未解析时提醒（模板预填 "feat(scope):" 未替换是常见原因）---
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
                  '合法 scope：`PB01`-`PB19`（映射 `scope:spec`）、' + VALID_SCOPES.map(s => '`' + s + '`').join('、'),
                  '',
                  '请修改标题为 `<type>(<scope>): <subject>` 格式，DoR 检查（GOV-G2）会复核此项。'
                ].join('\n')
              });
            }

            // --- 第三方 Issue 分诊通知 ---
            if (!isOwner) {              await github.rest.issues.createComment({
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
                  '**所有者 @janssenkm 审核后**：',
                  '- **采纳** -> 创建新的 owner Issue 关联本 Issue，关闭本 Issue',
                  '- **拒绝** -> 关闭并标记为 not planned',
                  '- **需补充** -> 评论请求澄清',
                  '',
                  '> 在采纳决定前，本 Issue 不会触发任何自动化开发。'
                ].join('\n')
              });
            }
```

创建 `.github/workflows/label-sync.yml`（Projects v2 同步）：

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
          PROJECT_NUMBER: 1
        with:
          # 必须使用 PAT；未配置时下方脚本会跳过并记录 warning
          github-token: ${{ secrets.PROJECTS_TOKEN }}
          script: |
            if (!process.env.PROJECT_NUMBER) return;
            const PROJECT_NUMBER = parseInt(process.env.PROJECT_NUMBER);
            const issue = context.payload.issue;
            const action = context.payload.action;
            const labelName = context.payload.label?.name;

            // 标签 -> Projects v2 Status 选项映射
            const labelToStatus = {
              'do:triage': 'Triage',
              'do:ready': 'Ready',
              'do:in-progress': 'In progress',
              'do:review': 'In review',
              'do:acceptance': 'Acceptance',
              'state:blocked': 'Blocked'
            };

            // 优先级：state:blocked > do:* 前向状态
            const statusPriority = ['state:blocked', 'do:acceptance', 'do:review', 'do:in-progress', 'do:ready', 'do:triage'];

            // close reason -> Status 映射
            let targetStatus = null;
            if (action === 'closed') {
              targetStatus = issue.state_reason === 'completed' ? 'Done' : 'Not planned';
            } else if (action === 'reopened') {
              targetStatus = 'Triage';
            } else if (action === 'labeled' && labelName && labelToStatus[labelName]) {
              targetStatus = labelToStatus[labelName];
            } else if (action === 'unlabeled') {
              // 移除标签时，根据剩余标签重算 Status（不使用被移除的标签名）
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
              if (!targetStatus) targetStatus = 'Triage'; // 无状态标签时回退
            }

            if (!targetStatus) return;

            try {
              // 获取 org project 的 Status 字段 ID 和选项 ID
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

              // 将 issue 加入 project 并取得 item id。
              // addProjectV2ItemById 是幂等的：content 已在 project 中时返回既有 item，
              // 因此无需分页遍历 items（items(first:100) 在 Issue 数超 100 后会漏查并重复添加）。
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
              // 常见原因：未配置 PROJECTS_TOKEN secret，或该 PAT 缺少 project scope
            }
```

创建 `.github/workflows/pr-gates.yml`：

```yaml
name: pr-gates
on:
  pull_request:
    types: [opened, edited, synchronize]
jobs:
  # --- G3: 种子校验 ---
  verify-seeds:
    name: verify-seeds
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Run verify_seed_set.py
        run: python3 seeds/verify_seed_set.py

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
            if (!(/\[x\].*AI/i.test(body) || /Assisted-by:/i.test(body))) {
              problems.push('PR body 缺少 AI 披露声明（勾选 AI-generated 复选框，或写入 Assisted-by trailer）');
            }
            if (!/(?:closes|fixes|resolves|refs)\s+#\d+/i.test(body)) {
              problems.push('PR body 缺少关联 Issue（使用 closes/fixes/resolves #NNN）');
            }

            // --- 2) 每个 commit 必须带 Assisted-by trailer ---
            // AGENTS.md 反模式清单要求「每个 commit 必带 Assisted-by trailer」。
            // 只校验 PR body 无法强制该约束，故在此逐 commit 复核（同一合同的两个落点）。
            const commits = await github.paginate(
              github.rest.pulls.listCommits,
              { owner: context.repo.owner, repo: context.repo.repo, pull_number: pr.number, per_page: 100 }
            );
            // trailer 必须独占一行（行首匹配），避免正文中偶然提及被误判为通过
            const TRAILER = /^Assisted-by:\s*\S+/im;
            const missing = commits
              .filter(c => (c.parents || []).length < 2)   // 跳过 merge commit
              .filter(c => !TRAILER.test(c.commit.message || ''))
              .map(c => `${c.sha.substring(0, 7)} ${(c.commit.message || '').split('\n')[0]}`);

            if (missing.length) {
              problems.push(
                `以下 ${missing.length} 个 commit 缺少 Assisted-by trailer：\n  - ` + missing.join('\n  - ')
              );
            }

            if (problems.length) {
              core.setFailed('AI 披露门禁未通过：\n- ' + problems.join('\n- '));
            } else {
              core.info(`OK: PR body 已披露；${commits.length} 个 commit 均含 Assisted-by trailer`);
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
              // 和 do:review（pr create 之后）。标签切换发生在 gh pr create 之后，
              // 见 §2.4.1 step 5。
              // do:ready 与 do:acceptance 阶段 PR 不应为 draft（前者是已领取未开 PR，
              // 后者是 merge 前验收阶段）；白名单过宽会被静默绕过。
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

### 4.9 创建 AGENTS.md

创建仓库根目录 `AGENTS.md`：

```markdown
# AGENTS.md - PolicyBase AI 开发指引

> 本文件是 AI 会话的入口指令。每次会话启动时必须首先读取本文件。
> 借鉴 zed-industries/zed：本文件为单一规范源，CLAUDE.md/GEMINI.md 可软链至此。

## 身份与权限

- **仓库所有者**：@janssenkm（GitHub: janssenkm）
- **AI 身份**：当前会话模型，必须在每个 commit 添加 `Assisted-by:` trailer
- **AI 可做**：自动开发、编写、审核、测试、创建分支/PR、运行验证命令、分诊第三方 Issue
- **AI 禁止**：自我批准 merge、操作非 janssenkm 的 Issue、绕过门禁、手改 seeds/ 文件、自行将 Issue 从 `do:triage` 切换到 `do:ready`（G2 门禁：Ready 转换需用户确认）

## 会话启动检查（G0 Session Gate）

1. 读取本文件
2. 读取 `seeds/PolicyBase_01.md`（权威地图）+ `seeds/PolicyBase_03.md`（协作约定）
3. 运行 `python3 seeds/verify_seed_set.py`，确认输出 `OK seed_set_verified: 19 volumes verified`
4. `gh auth status` 确认已认证为 janssenkm
5. 查询可领取的 Issue：
   `gh issue list --label "origin:owner" --label "do:ready" --state open`

## Issue-First 铁律

1. **无 Issue 不开发**：一切变更始于 Issue
2. **无 do:ready 不领取**：只领取 `origin:owner` + `do:ready` 的 Issue
3. **不自封 Ready**：AI 可检查 DoR 并评论结论，但 `do:triage` -> `do:ready` 的标签切换必须等用户确认后执行
4. **第三方 Issue 只读**：`origin:external` 的 Issue 只做分诊分析，不开发
5. **一 Issue 一分支一 PR**：不混合多个 Issue 的变更

## 标题前缀规范

格式：`<type>(<scope>): <subject>`

- type: feat | fix | docs | refactor | gov | decision | chore | seed
  - type 的权威存储是 GitHub 原生 Issue Type；CI 从标题前缀解析后自动赋值
  - 第三方 Issue 无前缀，CI 赋 Issue Type `Intake`
- scope: PB01-PB19 | infra | ci | cli | data | docs | governance（无原生替代，标签）

## 分支与提交规范

| 对象 | 格式 | 示例 |
|---|---|---|
| 分支 | `<type>/<issue#>-<slug>` | `feat/42-source-registry` |
| Commit | `<type>(<scope>): <subject>` | `feat(PB10): Source Registry 注册接口` |
| PR 标题 | `<type>(<scope>): <subject> (#<issue#>)` | `feat(PB10): Source Registry (#42)` |
| Trailer | `Assisted-by: <model> (model: <id>, autonomous\|supervised)` | 见下 |

提交示例：
```
feat(PB10): Source Registry 注册接口

- 实现 register-source 命令
- 添加 frontmatter 校验
- 关联 Issue #42

Assisted-by: Claude (model: glm-5.2, autonomous)
```

PR body 必须包含：`Closes #<issue#>` + AI 披露复选框 + AC 逐条证据

## 门禁分层

| 层 | 检查 | 失败动作 |
|---|---|---|
| GOV-G0 Session | 本文件 + verify_seed_set.py | STOP，不继续 |
| GOV-G1 Admission | CI 自动打 origin/scope 标签 + 赋 Issue Type + 同步 Projects v2 | 自动执行 |
| GOV-G2 DoR | 标题前缀 + AC + 规格引用 | AI 评论结论，用户确认后切 do:ready；不通过则 state:blocked |
| GOV-G3 PR/CI | verify-seeds + ai-disclosure（含逐 commit trailer 校验）+ dor-check | CI 红灯，PR 阻塞 |
| GOV-G4 Acceptance | AC 命令全通过 + do:acceptance | 回 do:in-progress |

## AC 验收格式

格式对齐 PolicyBase_03 §9（该卷是唯一 owner，本节不得改写其字段语义）：

```text
AC-<stable-id>
command: <exact executable command>
exit code: <实际执行得到的整数>
assert: <observable assertion>
evidence: <CI artifact / test output / command output>
```

- `command` 必须在干净环境中原样执行，**不得含 `<占位符>`**
- `exit code` 只在命令**实际执行后**填写。PolicyBase_03 §9 原文：「命令未实际执行不得填退出码」
- 尚未执行时：**省略 `exit code` 行**，写 `evidence: planned`
- 未执行的 AC 不得标记为已验收
- 聊天记录/模型声明不是验收证据
- 进度三态：已验收 / 做了未验收 / 只是计划

## 第三方 Issue 分诊流程

1. 读取 `origin:external` Issue（Issue Type: Intake）（**只读，不开发**）
2. 分析并发布结构化评论：
   ```
   ## 分诊分析
   - 摘要：<内容摘要>
   - 推断 Issue Type：Feature/Bug/Task/...
   - 推断范围：scope:xxx
   - 重复检查：无 / 重复 #NNN
   - 可行性：<评估>
   - 建议：adopt / reject / needs-clarification
   - 建议 Issue 标题：<proposed title>
   - 建议优先级：priority:blocker|high|medium|low
   - 理由：<reasoning>
   ```
3. 等待 @janssenkm 决定
4. 若采纳：创建新 Issue（`do:ready`，CI 自动补 `origin:owner` + Issue Type），关闭原 Issue（`--reason "not planned"`）
5. 若拒绝：关闭原 Issue（`--reason "not planned"`）

## 反模式清单（禁止）

| 反模式 | 正确做法 |
|---|---|
| "我测过了"不附证据 | 附 command + exit code + output |
| 秒回 commit（无思考痕迹） | 每轮 review 注明 SHA + 摘要 |
| 隐藏 AI 身份的 commit | 每个 commit 必带 Assisted-by trailer（由 `ai-disclosure` job 逐 commit 强制，非自证） |
| 手改 seeds/PolicyBase_NN.md | 通过 Issue + PR 修改 |
| 绕过 verify_seed_set.py | commit 前必须运行 |
| 在第三方 Issue 上直接开发 | 只做分诊分析，等采纳后在新 Issue 开发 |
| 自我批准 merge | 等用户显式指示或 do:acceptance 状态 |
| 静默扩大 Issue 范围 | 发现范围外工作 -> STOP，开新 Issue |
| 自作主张加功能/抽象/配置项 | 只做 Issue 明确请求的变更；无关问题记录风险，不顺手改 |

## 编码规范

> 本节在 P1（Project Skeleton）启动后填充 Python >=3.12 编码规则。
> P0 阶段无代码，此为占位。
>
> 规则应是「容易踩的坑」，不是「架构地图」。模块布局、数据流、关键类型等描述会随代码变化而过期，AI 可以通过读代码获取，不需要写在这里。
>
> 填写时每条规则须满足：非显而易见（熟悉代码库的人仍会踩错）、反复遇到（不止一次）、具体可执行（能直接照做）。

## 会话结束协议

每次 AI 会话结束前：

1. 确认所有 AC 证据已记录（command + exit code + output），未执行的标记为 `planned`
2. 确认所有 commit 包含 `Assisted-by:` trailer
3. 如果在会话中发现了非显而易见的模式或坑，在 PR 描述中添加 **"Suggested AGENTS.md additions"** 段落，写出建议的规则文本
4. **不要**在正常功能/修复工作中直接编辑 AGENTS.md（规则变更走 `gov(governance)` Issue + PR）
5. 如有未完成的工作，在 Issue 或 PR 中评论说明当前进度和下一步

## 治理规则变更（Rules Hygiene）

> 借鉴 zed-industries/zed 的 Rules Hygiene（.rules:166-188）。

### 基本原则

- AGENTS.md 被每个 AI 会话读取，保持高信噪比
- 规则是**要避开的坑**（traps to avoid），不是**照着走的地图**（maps to follow）
- 架构描述（模块布局、数据流、关键类型）会快速过期，AI 可通过读代码获取，**不写入** AGENTS.md
- 适用于单个模块的规则放入该模块自己的 `.rules` 文件，不放仓库根目录

### 变更流程

1. 治理规则变更必须开 `gov(governance)` 类型 Issue
2. 变更必须通过 PR + 用户审核
3. 变更 PR 必须说明：改了什么、为什么改、影响哪些现有规则
4. 合并后在 Issue 中记录变更留痕
5. **禁止在正常功能/修复工作中顺手修改 AGENTS.md**（no drive-by additions）

### 新规则门槛

新规则必须**同时满足**以下三条（澄清已有规则不受此限）：

1. **非显而易见**：熟悉代码库的人没有这条规则仍会踩错
2. **反复遇到**：不止一次碰到（同一次会话多次命中也算）
3. **具体可执行**：是一条具体指令，不是模糊原则

### 规则演进工作流

1. AI 在会话中发现模式 -> 在 PR 描述中建议（"Suggested AGENTS.md additions"）
2. 用户在 code review 中验证该模式
3. 单独的 commit 添加规则，并在 commit message 中说明*为什么*需要这条规则
```

### 4.10 创建 CLAUDE.md / GEMINI.md 软链

```bash
# 借鉴 zed-industries/zed：一份规则多处软链，避免多 AI 规则漂移
# Zed 用 .rules 作为源文件，AGENTS.md/CLAUDE.md/GEMINI.md 均软链至它
# 本项目用 AGENTS.md 作为源文件（AI agent 发现优先级最高），CLAUDE.md/GEMINI.md 软链至它
cd /home/yangsen/Dropbox/workspaces/NormBook/PolicyBase.git
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md

# 验证软链
ls -la AGENTS.md CLAUDE.md GEMINI.md
# 期望：AGENTS.md 为普通文件，CLAUDE.md 和 GEMINI.md 为 -> AGENTS.md 的软链
```

> **设计说明**：不同 AI 工具（Claude Code、Gemini、Copilot 等）读取的入口文件名不同，但规则内容必须一致。软链保证只有一份源文件，修改 AGENTS.md 即同步生效到所有 AI。如后续需要添加 AI 特定指令，可在 AGENTS.md 中用条件区块或单独的 `.rules` 文件扩展，不走软链。
>
> **与正式文档目录的关系**：软链在仓库根是为 AI 工具自动发现（CLAUDE.md / GEMINI.md 是各 AI CLI 的标准入口名）；正式用户文档按 PolicyBase_03 §8 仍在 `docs/` 子目录下（`docs/product/`、`docs/specs/` 等），二者职责不重叠——根目录的 AGENTS.md / 软链是 AI 入口，`docs/` 下是人类阅读入口。

### 4.11 提交全部治理文件

```bash
git add .gitignore AGENTS.md CLAUDE.md GEMINI.md .github/
git commit -m "gov(governance): 初始化 issue-first 治理基础设施

- AGENTS.md: AI 开发指引 + 反模式清单 + 门禁分层 + 会话结束协议 + Rules Hygiene（三门槛/禁止架构地图/no drive-by）
- .github/ISSUE_TEMPLATE/: 5 类 Issue 模板 + config
- .github/PULL_REQUEST_TEMPLATE.md: AI 披露 + AC 证据
- .github/CODEOWNERS: 全路径归属 janssenkm
- .github/workflows/issue-triage.yml: G1 自动打标（origin/scope）+ GraphQL 赋 Issue Type
- .github/workflows/label-sync.yml: Projects v2 Status 字段同步
- .github/workflows/pr-gates.yml: G3 三重检查（verify-seeds/ai-disclosure[含逐 commit trailer]/dor-check）
- 19 个标签 + 9 个 Milestones 已创建（第 1 段）；10 个 Issue Type 组织级已存在
- CLAUDE.md/GEMINI.md 软链至 AGENTS.md

Assisted-by: Claude (model: glm-5.2, supervised)"
```

> **不要 `git push origin main`**：本节属第 2 段（自举期），变更在 `gov/<N>-governance-bootstrap`
> 分支上，须按 §4.4 步骤 5 推送分支并开 PR，由用户 merge 进 main。

### 4.12 配置分支保护

```bash
# 前置：本节必须在 §4.4 自举 PR **merge 之后**执行。
# 届时 pr-gates.yml 已在 main 上，且三个 check 已在自举 PR 上真实运行过
# （AC-P0-08 的证据），因此 required check 名称可被 GitHub 正常识别。
# 若顺序颠倒（先设保护再开自举 PR），required checks 会阻塞该 PR 的 merge。

# 设置 main 分支保护（公共仓库 Free 可用）
gh api -X PUT "repos/NormBook/PolicyBase/branches/main/protection" --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["verify-seeds", "ai-disclosure", "dor-check"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

> **说明与限制**：
> - `enforce_admins: false`：单人开发，保留紧急绕过能力。**注意**：这意味着 admin（janssenkm）可绕过所有门禁直接 push/merge，门禁对 admin 是**自律性**而非**强制性**。如需强制，改为 `true`（但紧急修复时无法绕过）。
> - `required_pull_request_reviews: null`：单人开发无代码审查要求，门禁靠 CI 状态检查。**注意**：这意味着 PR 可在无审查的情况下合并，G4 验收门禁是**流程约束**而非**平台强制**。
> - `required_status_checks.contexts`：3 个 check 名称必须与 pr-gates.yml 中 job 的 `name:` 完全匹配（`verify-seeds` / `ai-disclosure` / `dor-check`）。这些 job 仅在 `pull_request` 事件触发，不会在 `push` 到 main 时运行。
> - `required_linear_history`：禁止 merge commit，保持线性历史（配合 `--squash` 合并）
> - `strict: true`：PR 必须基于最新 main 且 CI 通过

### 4.13 验证自动化

`CP-P0-03`：Issue-first 自动化验证。创建一个测试 Issue，验证 origin 标签、Issue Type、scope 标签与 Milestone 均由自动化正确处理。

> 本节须在自举 PR **merge 之后**执行——此时 `issue-triage.yml` 才在 main 上生效。

```bash
# 1. 创建测试 Issue（不手工打 origin:owner / scope:governance，交由 CI 自动处理）
gh issue create -R NormBook/PolicyBase \
  --title "gov(governance): 验证 issue-triage 自动打标" \
  --milestone "P0 Repository Governance Bootstrap" \
  --label "priority:blocker" \
  --body "## 测试目的

验证 issue-triage.yml 正确执行：
- 作者为 janssenkm -> 自动打 origin:owner + do:triage
- 标题前缀 gov(governance) -> 自动赋 Issue Type: Change + 打 scope:governance

## 验收标准

见 seeds/P0-GITHUB-INIT.md §5 的 AC-P0-07 与 AC-P0-07b。"

# 2. 等待 CI 完成
sleep 15

# 3. 解析测试 Issue 编号（后续命令复用，避免占位符）
N=$(gh issue list -R NormBook/PolicyBase --state all \
      --search 'in:title 验证 issue-triage' --limit 1 --json number --jq '.[0].number')
echo "测试 Issue = #$N"

# 4. 检查标签（期望：origin:owner, do:triage, scope:governance, priority:blocker）
gh issue view "$N" -R NormBook/PolicyBase --json labels --jq '[.labels[].name]|sort|join(", ")'

# 5. 检查 Issue Type（期望：Change）
gh api "repos/NormBook/PolicyBase/issues/$N" --jq '.type.name'

# 6. 检查 Milestone（期望：P0 Repository Governance Bootstrap）
gh issue view "$N" -R NormBook/PolicyBase --json milestone --jq '.milestone.title'
```

> **若 Issue Type 为 null**：说明 `updateIssueIssueType` 失败。issue-triage.yml 已将其设为非阻塞（`core.warning`），去 Actions 日志查看 warning 原因，常见为 Issue Type 名称不匹配或 token 权限不足。

---

## 5. P0 目标验收合同

以下 AC 均为**待执行的目标合同**。按 PolicyBase_03 §9「命令未实际执行不得填退出码」，
本节各条**刻意不写 `exit code` 行**；实际执行后，在该行补入真实退出码并把 `evidence: planned`
替换为可复核证据（命令输出或 CI 链接）。

> **AC 格式对齐 PolicyBase_03 §9**：未执行时**省略 `exit code:` 行**并写 `evidence: planned`——这是 PolicyBase_03 §9 「命令未实际执行不得填退出码」的字面与精神合规实现（不是省略责任字段）。执行后回填真实整数退出码并替换 `evidence:` 为可复核证据。

```
AC-P0-01
command: git -C /home/yangsen/Dropbox/workspaces/NormBook/PolicyBase.git status --short
assert: 输出为空（工作区干净，无未提交变更）
evidence: planned（P0 尚未执行）

AC-P0-02
command: gh repo view NormBook/PolicyBase --json visibility --jq .visibility
assert: 输出 "PUBLIC"
evidence: planned（P0 尚未执行）

AC-P0-03
command: gh label list -R NormBook/PolicyBase --limit 100 --json name --jq '[.[].name]|map(select(test("^(do|state|origin|scope|priority):")))|length'
assert: 输出 19（只统计自建的 19 个治理标签，排除 GitHub 默认的 9 个）
evidence: planned（P0 尚未执行）

AC-P0-03b
command: gh api repos/NormBook/PolicyBase/issue-types --jq 'length'
assert: 输出 >= 10（组织级 Issue Type，实测已存在 10 个）
evidence: planned（P0 尚未执行）

AC-P0-03c
command: gh api repos/NormBook/PolicyBase/milestones --jq 'length'
assert: 输出 9
evidence: planned（P0 尚未执行）

AC-P0-04
command: test -f AGENTS.md && test -L CLAUDE.md && test -L GEMINI.md && test -f .github/CODEOWNERS && test -f .github/PULL_REQUEST_TEMPLATE.md && test -f .github/workflows/issue-triage.yml && test -f .github/workflows/pr-gates.yml && test -f .github/workflows/label-sync.yml
assert: 退出码 0（全部治理文件存在，且 CLAUDE.md/GEMINI.md 是软链）
evidence: planned（P0 尚未执行）

AC-P0-05
command: python3 /home/yangsen/Dropbox/workspaces/NormBook/PolicyBase.git/seeds/verify_seed_set.py
assert: 输出包含 "OK seed_set_verified: 19 volumes verified"
evidence: planned（P0 尚未执行）

AC-P0-06
command: gh api repos/NormBook/PolicyBase/branches/main/protection --jq '.required_status_checks.contexts|sort|join(",")'
assert: 输出 "ai-disclosure,dor-check,verify-seeds"
evidence: planned（P0 尚未执行）

AC-P0-07
command: gh issue list -R NormBook/PolicyBase --label "origin:owner" --state all --json number --jq 'length'
assert: 输出 >= 1（CI 已为 owner Issue 自动打 origin:owner 标签）
evidence: planned（P0 尚未执行）

AC-P0-07b
command: N=$(gh issue list -R NormBook/PolicyBase --state all --search 'in:title 验证 issue-triage' --limit 1 --json number --jq '.[0].number') && gh api graphql -F number=$N -f query='query($number:Int!){repository(owner:"NormBook",name:"PolicyBase"){issue(number:$number){issueType{name}}}}' --jq '.data.repository.issue.issueType.name'
assert: 输出 "Change"（CI 从 gov 前缀自动赋值 Issue Type，无占位符，可原样执行。注：REST `issues[].type` 长期为 null，必须走 GraphQL，详见 §2.2.3 末注）
evidence: planned（P0 尚未执行）

AC-P0-08
command: gh pr checks $(gh pr list -R NormBook/PolicyBase --state all --search 'in:title 初始化 issue-first 治理基础设施' --limit 1 --json number --jq '.[0].number') --json name,state --jq '[.[]|select(.state=="SUCCESS")|.name]|sort|join(",")'
assert: 输出包含 ai-disclosure、dor-check、verify-seeds 三者（门禁有效性实证：自举 PR 上三个 check 真实通过，而非仅配置存在）
evidence: planned（P0 尚未执行）

AC-P0-09
command: git -C /home/yangsen/Dropbox/workspaces/NormBook/PolicyBase.git log --format=%B main | grep -c "^Assisted-by:"
assert: 输出 >= 2（main 上每个 commit 均含 Assisted-by trailer）
evidence: planned（P0 尚未执行）
```

---

## 6. 执行清单

**第 1 段：豁免期（直推 main）**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 1 | 安装 gh CLI | `[MANUAL-AUTH]` | `gh --version` 输出版本号 |
| 2 | gh auth login | `[MANUAL-AUTH]` | `gh api user --jq .login` 输出 janssenkm |
| 3 | 运行 Token 权限验证脚本（§3.2 步骤 3） | `[MANUAL-AUTH]` | 脚本输出「全部验证通过」，退出码 0 |
| 4 | 确认 NormBook 组织（**已存在，通常可跳过**） | `[MANUAL-AUTH]` | `gh api orgs/NormBook` 不报错 |
| 5 | git init + .gitignore | `[LOCAL-AUTO]` | `git status` 可运行 |
| 6 | 首次提交 | `[LOCAL-AUTO]` | `git log --oneline` 显示 1 条提交 |
| 7 | `git remote add` + push（**仓库已存在，勿用 repo create**） | `[REMOTE-AUTO]` | 用户已授权；`gh repo view` 显示 URL |
| 8 | 创建 19 个治理标签 | `[REMOTE-AUTO]` | AC-P0-03 输出 19 |
| 8b | 验证 Issue Types（**已存在，仅验证**） | `[REMOTE-AUTO]` | AC-P0-03b 输出 >= 10 |
| 8c | 创建 9 个 Milestone | `[REMOTE-AUTO]` | AC-P0-03c 输出 9 |

**第 2 段：自举期（必须走 PR，见 §4.4）**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 9 | 创建自举 Issue + 手工设 Issue Type + 开分支 | `[REMOTE-AUTO]` | Issue 为 `do:in-progress`，分支已创建 |
| 10 | 创建 Issue 模板（5+config） | `[LOCAL-AUTO]` | `.github/ISSUE_TEMPLATE/` 下 6 个文件 |
| 11 | 创建 PR 模板 | `[LOCAL-AUTO]` | `.github/PULL_REQUEST_TEMPLATE.md` 存在 |
| 12 | 创建 CODEOWNERS | `[LOCAL-AUTO]` | `.github/CODEOWNERS` 存在 |
| 13 | 创建 issue-triage.yml | `[LOCAL-AUTO]` | 文件存在 |
| 13b | 创建 label-sync.yml | `[LOCAL-AUTO]` | 文件存在 |
| 14 | 创建 pr-gates.yml | `[LOCAL-AUTO]` | 文件存在 |
| 15 | 创建 AGENTS.md + 软链 | `[LOCAL-AUTO]` | AC-P0-04 退出码 0 |
| 16 | 提交 + push 分支 + 开 draft PR | `[REMOTE-AUTO]` | PR 已创建，Issue 切 `do:review` |
| 17 | **观察 pr-gates 三个 check** | `[REMOTE-AUTO]` | AC-P0-08：三个 check 全绿（门禁有效性实证） |
| 18 | 用户审核并 merge | `[MANUAL-REVIEW]` | PR 已 merge，Issue 以 `completed` 关闭 |

**第 3 段：收尾**

| # | 步骤 | 标记 | 完成条件 |
|---|---|---|---|
| 19 | 配置分支保护（**必须在自举 PR merge 之后**） | `[REMOTE-AUTO]` | AC-P0-06 输出三个 check 名 |
| 20 | 创建测试 Issue 验证 CI 自动打标 + Issue Type | `[REMOTE-AUTO]` | AC-P0-07、AC-P0-07b 通过 |
| 21 | 执行并记录全部 AC，申请 `GATE-P0-EXIT` | `[LOCAL-AUTO+REMOTE-AUTO]` | 全部 AC 有实际 evidence；用户确认 |

## GATE-P0-EXIT

P0 退出需同时满足：`CP-P0-01`/`CP-P0-02`/`CP-P0-03` 完成、`AC-P0-01`…`AC-P0-09`（含 03b/03c/07b）全部有可复核实际证据、用户最终确认。

**与 PolicyBase_02 §14 五个退出维度的映射**（本门不替代该卷，只是其在 P0 的落地）：

| PolicyBase_02 §14 退出维度 | P0 的满足方式 |
|---|---|
| 维度一：该阶段全部能力已实现并通过验证 | `CP-P0-01`/`02`/`03` 完成；AC-P0-01…09 有实际证据 |
| 维度二：依赖阶段能力已具备，前置未被绕过 | P0 是首阶段，无前置依赖；第 1 段豁免边界已在 §0 显式声明并限定 |
| 维度三：测试覆盖 normal/edge/error，golden 通过 | P0 无业务代码。normal＝AC-P0-08 三 check 全绿；error＝自举期任一 check 红灯并被修复的留痕；golden 由 `verify_seed_set.py`（AC-P0-05）承担 |
| 维度四：正式文档覆盖、风险和豁免可追溯 | AGENTS.md 已合入；§0 豁免声明与 §4.12 的 admin 绕过风险已书面留档 |
| 维度五：维护者确认能力达标 | 用户对 `GATE-P0-EXIT` 的最终确认 |

> **已知残留风险（显式接受，非缺陷）**：`enforce_admins: false` 且 `required_pull_request_reviews: null`，因此唯一 admin（janssenkm）可绕过全部门禁直推 main。GOV-G3/G4 对 owner 是**自律性**约束而非平台强制。P0 接受该风险以保留单人开发的紧急修复能力；若后续引入协作者，应重新评估并考虑改为 `enforce_admins: true`。

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

## 附录 B：门禁设计借鉴对照表

| 门禁要素 | 本方案实现 | 借鉴仓库 | 借鉴方式 |
|---|---|---|---|
| 类型化 Issue | GitHub 原生 Issue Types（10 个：9 日常开发 + Acceptance） | spec-kit/gsd-core | 原生优先：Issue Types（GraphQL 赋值） |
| 状态机 | do:* 标签前向推进 + close reason 终态 | spec-kit | 标签用于 CLI 自动化；close reason 替代 state:* 标签 |
| 阶段分组 | GitHub 原生 Milestones（9 个） | — | 原生优先：Milestones 替代 phase:* 标签 |
| 看板可视化 | Projects v2 Status 字段（标签同步镜像） | — | 原生优先：标签驱动自动化，Projects v2 提供展示层 |
| DoR 门禁 | Issue 模板必填 + AI 检查 + CI dor-check | gsd-core | approved-* 标签是写码前置 |
| PR 门禁 | required status checks（3 个 job） | spec-kit/uv | CI 状态检查即门禁 |
| 验收门禁 | AC 命令全通过 + do:acceptance 状态 | claw-code/uv | 可执行命令即验收 |
| AI 身份边界 | Assisted-by trailer + 反模式清单 | spec-kit | 连续披露制度 |
| 来源控制 | origin:owner/external 标签 | 本方案原创 | 自动化触发依据 |
| 规则变更 | Rules Hygiene + gov 类型 Issue | zed | 补种子缺的演进机制 |
| 单一规范源 | AGENTS.md 软链 CLAUDE/GEMINI | zed | 一份规则多处引用 |
| 拒绝留档 | close reason "not planned" + 评论 | gsd-core | out-of-scope 决策留档 |
