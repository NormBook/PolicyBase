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

- [ ] `python3 seeds/verify_seed_set.py` 通过
- [ ] 无 TODO/FIXME/TBD/XXX 残留
- [ ] 分支命名符合 `<type>/<issue#>-<slug>`
- [ ] 未混合其他 Issue 的变更