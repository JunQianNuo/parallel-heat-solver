# 二维热传导方程的串行与 MPI 求解

《并行与分布式计算》期末大作业，对应教师任务书第 4 题。采用显式五点有限差分，先建立串行基准，再实现 MPI 行分块与邻居通信。

技术选择：C++17、CMake/CTest。OpenMP 为待评估扩展，尚未纳入必做范围。

## 当前进度

M0 已获用户验收；M1 串行基准已实现并通过本轮构建与测试，等待用户验收。MPI 与正式性能实验尚未开始。真实检查输出见 [M1 验证记录](docs/validation/m1.log)。

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

`src/` 为串行实现，`tests/` 为基本回归；MPI、系统验证完善与性能实验按后续里程碑另行授权。

## 构建与运行

需要支持 C++17 的编译器、CMake ≥ 3.20；启用测试时需要 Python 3 标准库，无 GoogleTest 或联网下载依赖。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
./build/heat_serial --help
./build/heat_serial > build/solution.csv
./build/heat_serial --N 40 --M 1600 --T 0.1 --alpha 1 > build/solution-N40.csv
```

命名参数可独立覆盖，默认 `N=20 M=400 T=0.1 alpha=1`，此时 `r=0.1`。N 为每方向区间数（共 `(N+1)^2` 节点），M 为实际推进步数；程序计算 `dt=T/M`，不自动修改 M。要求 `N≥2,M≥1`、有限正 T 和 alpha、可表示的正 dt/r、`r≤1/4` 及可表示的双数组规模。内存须由实际机器提供，分配失败报错；大规模输入可能耗费大量内存和时间。

stdout 为最终时刻 T 的 CSV，首行为 `i,j,x,y,u_numeric,u_exact,abs_error`，按 `i*(N+1)+j` 顺序包含全部边界及内点；`x=i/N,y=j/N`，数值使用 17 位有效数字。stderr 单行记录 `N M T alpha h dt r E_inf`（`key=value`）。解析值仅用于验证；所有数值温度来自五点差分推进。退出码：0 成功，2 参数错误，1 分配/运行/输出失败；未知、重复、缺值选项均拒绝。仅单独的 `--help` 返回帮助。

基本测试阈值、手算及加密参数见 [DESIGN](docs/DESIGN.md)。这些是 M1 回归标准，不是任意输入的精度保证；本轮未做性能实验。
