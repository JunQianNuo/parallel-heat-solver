# 二维热传导方程的串行与 MPI 求解

《并行与分布式计算》期末大作业，对应教师任务书第 4 题。采用显式五点有限差分，先建立串行基准，再实现 MPI 行分块与邻居通信。

技术选择：C++17、CMake/CTest。OpenMP 为待评估扩展，尚未纳入必做范围。

## 当前进度

M0：文档已建立，待用户验收。求解器、构建配置和数值测试尚未实现，当前没有可执行的项目构建或运行命令。M0 文档检查不代表数值算法已验证。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 工作流程、资料优先级与 Git 权限 |
| [SPEC.md](SPEC.md) | 题目要求、项目范围与验收标准 |
| [PLAN.md](PLAN.md) | M0–M5 阶段、进入条件与交付物 |
| [STATUS.md](STATUS.md) | 当前事实、验证记录和下一步 |
| [DESIGN.md](docs/DESIGN.md) | 数学模型、数值算法与 MPI 设计 |
| [DECISIONS.md](docs/DECISIONS.md) | 已确认选择及理由 |
| [AI_USAGE.md](docs/AI_USAGE.md) | AI 使用与人工核查记录 |

## 本地课程资料

教师任务书位于 `docs/sources/final.pdf`，第 1 页为通用要求，第 3 页为本题要求；讲义位于 `docs/sources/lectures/`，参考代码位于 `docs/sources/examples/`。

这些资料仅在本地只读使用，不随 Git 仓库分发。新克隆需要使用者从课程提供的原始资料中补齐上述路径；不要将资料加入提交。资料缺失时，应明确记录缺项，并暂停依赖原文核对的工作。课程示例的运行输出不能作为本项目的验证结果。

`src/`、`tests/`、`scripts/`、`results/`、`report/` 预留给后续阶段；空目录不会被 Git 保存。具体接口、默认参数、测试阈值及实验方案在相应阶段确定。
