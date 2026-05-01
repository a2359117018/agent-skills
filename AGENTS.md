# AGENTS.md — Agent 工作约定

## 项目概述

这是一个 AI agent 技能集合项目。每个 skill 是独立的能力模块，供 coding agent 加载使用。

## 目录约定

- 技能按**工具/服务提供商**组织为顶层目录（如 `minimax-cli-skills/`）
- 每个技能一个子目录，目录名即技能名
- 每个技能必须包含 `SKILL.md`

## SKILL.md 规范

- 必须包含 YAML frontmatter，含 `name` 和 `description` 字段
- `description` 是 agent 自动匹配的依据，需覆盖典型触发场景
- 正文包含：核心规则（Critical Rule）、陷阱（Gotchas）、输出约定（Output Contract）
- 引用脚本使用相对路径（如 `scripts/describe.py`），绝不使用绝对路径

## 脚本约定

- 所有可执行脚本放在 `scripts/` 目录
- 脚本需有明确的退出码规范（0=成功，非零=错误）
- 错误输出使用结构化 JSON（含 `error` 和 `message` 字段）
- 脚本应自行处理前置检查（如 CLI 安装、认证状态），不依赖 agent 预先运行

## 参考文档

- 放在 `references/` 目录
- 仅用于 agent 运行时查阅的辅助信息（如错误码说明）
- 不要放冗余内容，保持精简

## 技能评估（Evals）

每个技能应包含 `evals/evals.json`，用于系统化测试技能输出质量。

### 评估流程

1. **编写测试用例**：每条包含 `prompt`、`expected_output`、`assertions`（可选 `files`）
2. **双轨运行**：每个用例分别运行 `with_skill/` 和 `without_skill/`（基线），隔离上下文
3. **评分（Grading）**：逐条断言判定 PASS/FAIL，必须附具体证据，不给"友情通过"
4. **聚合（Benchmark）**：计算通过率、耗时、token 消耗的均值和 delta
5. **人工审查**：逐条查看实际输出，记录可操作的反馈到 `feedback.json`
6. **迭代改进**：根据失败断言 + 人工反馈 + 执行日志修改 SKILL.md，开启新一轮 iteration

### 断言编写原则

- **具体且可验证**：`"输出包含 results 数组，每个元素有 title 和 link"` — 好
- **测试技能特有价值**：不写 `"输出是有效 JSON"` 这种无技能也能通过的断言
- **涵盖边界条件**：空结果、错误恢复、非英语查询等
- **不过于脆弱**：不要求精确措辞，允许合理的表述变化

### 工作区结构

```
<skill>-workspace/
└── iteration-N/
    ├── eval-<name>/
    │   ├── with_skill/       # 使用技能运行
    │   │   ├── outputs/
    │   │   ├── timing.json   # { "total_tokens": ..., "duration_ms": ... }
    │   │   └── grading.json  # 断言评分结果
    │   └── without_skill/    # 不使用技能的基线
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── benchmark.json        # 聚合统计（通过率、耗时、token delta）
    ├── feedback.json         # 人工审查反馈
    └── analysis.json         # 迭代分析（可选）
```

### 关键规则

- **按需设置基线**：如果技能提供的是 agent 本身不具备的新能力（如网络搜索），`without_skill` 基线无意义，可省略；如果技能改善的是 agent 已有行为（如代码风格），则需要基线对比
- **移除永远通过的断言**：两边都通过的断言不提供有用信号
- **调查永远失败的断言**：可能是断言本身有问题或测试用例太难
- **关注 pass_with_skill && fail_without_skill 的断言**：这是技能真正创造价值的地方
- **捕获 timing 数据**：记录 token 和耗时，评估技能的代价是否值得
- **停止条件**：通过率不再提升、人工反馈持续为空、迭代无实质改善

## 禁止事项

- 不要提交 `evals/` 或 `evals-workspace/` 目录（已在 .gitignore 中）
- 不要在 SKILL.md 中硬编码绝对路径
- 不要在脚本中暴露或日志记录 API key
