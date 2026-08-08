# 品牌词检测回归测试

本文件用于验证 pr-gates.yml ai-disclosure job 的品牌词禁令检测：

- 应被检测出的品牌词：Claude / GLM / GPT / Gemini / Llama / Mistral 等
- 应**不**被误判的合法用法：CLAUDE.md / GEMINI.md 等软链文件名引用

测试 commit message 故意含品牌词，验证 PR 红灯。