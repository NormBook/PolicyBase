# AGENTS.md - PolicyBase AI 开发指引

> 本文件是 AI 会话的入口指令。每次会话启动时必须首先读取本文件。
> 借鉴 zed-industries/zed：本文件为单一规范源，CLAUDE.md/GEMINI.md 可软链至此。

## 身份与权限

- **仓库所有者**：@janssenkm（GitHub: janssenkm）
- **AI 身份**：当前会话模型，必须在每个 commit 添加 `AI-assisted:` trailer（**禁止列品牌名、版本号、能力等级**——按 §2.1 品牌词禁令）
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
| Trailer | `AI-assisted: autonomous\|supervised`（不列品牌名） | 见下 |

提交示例：
```
feat(PB10): Source Registry 注册接口

- 实现 register-source 命令
- 添加 frontmatter 校验
- 关联 Issue #42

AI-assisted: autonomous
```

PR body 必须包含：`Closes #<issue#>` + AI 披露复选框 + AC 逐条证据

## 门禁分层

| 层 | 检查 | 失败动作 |
|---|---|---|
| GOV-G0 Session | 本文件 + verify_seed_set.py | STOP，不继续 |
| GOV-G1 Admission | CI 自动打 origin/scope 标签 + 赋 Issue Type + 同步 Projects v2 | 自动执行 |
| GOV-G2 DoR | 标题前缀 + AC + 规格引用 | AI 评论结论，用户确认后切 do:ready；不通过则 state:blocked |
| GOV-G3 PR/CI | verify-seeds + ai-disclosure（含逐 commit trailer + 品牌词检测）+ dor-check | CI 红灯，PR 阻塞 |
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
| commit 含 AI 品牌词（违反 §2.1 禁令）| 每个 commit 必带 `AI-assisted:` trailer 且不含 AI 模型品牌名（由 `ai-disclosure` job 逐 commit 强制） |
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
2. 确认所有 commit 包含 `AI-assisted:` trailer（且不含 §2.1 禁止的 AI 品牌词）
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