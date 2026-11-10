# 二维热传导方程的串行、MPI 与 OpenMP 求解

《并行与分布式计算》期末大作业，对应教师任务书第 4 题。采用显式五点有限差分，以独立串行程序为基线，采用 MPI 行分块与邻居通信，并计划在 M2b 增加独立 OpenMP 求解进行比较。

技术选择：C++17、CMake/CTest。必做范围为独立串行、MPI、OpenMP；暂不引入混合并行。OpenMP 尚未实现。

## 当前进度

M0、M1 串行基准已获用户验收（2026-11-10）；测试耗时四位小数显示已补齐并验证。M2 MPI 提交 `34cdd73` 已获用户验收，既有 Debug/Release 回归各 10/10 通过。M2b OpenMP 范围已确认，尚未实现；未进入 M3/M4。真实检查输出见 [M1 验证记录](docs/validation/m1.log)。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 工作流程、资料优先级与 Git 权限 |
| [SPEC.md](SPEC.md) | 题目要求、项目范围与验收标准 |
| [PLAN.md](PLAN.md) | M0–M5（含 M2b）阶段、进入条件与交付物 |
| [STATUS.md](STATUS.md) | 当前事实、验证记录和下一步 |
| [DESIGN.md](docs/DESIGN.md) | 数学模型、数值算法、MPI 实现与 OpenMP 设计基线 |
| [DECISIONS.md](docs/DECISIONS.md) | 已确认选择及理由 |
| [AI_USAGE.md](docs/AI_USAGE.md) | AI 使用与人工核查记录 |

## 本地课程资料

教师任务书位于 `docs/sources/final.pdf`，第 1 页为通用要求，第 3 页为本题要求；讲义位于 `docs/sources/lectures/`，参考代码位于 `docs/sources/examples/`。

这些资料仅在本地只读使用，不随 Git 仓库分发。新克隆需要使用者从课程提供的原始资料中补齐上述路径；不要将资料加入提交。资料缺失时，应明确记录缺项，并暂停依赖原文核对的工作。课程示例的运行输出不能作为本项目的验证结果。

`src/` 当前包含独立串行与 MPI 实现，`tests/` 为基本回归。计划中的 `heat_openmp` 尚不存在可运行程序；M2b 实现由用户准备独立功能分支后开展，随后 M3 系统验证三种实现，M4 正式比较性能。

## 构建与运行

需要支持 C++17 的编译器、CMake ≥ 3.20 和 MPI 开发环境/启动器（本轮 Open MPI 4.1.6）；启用测试时需要 Python 3 标准库，无 GoogleTest 或联网下载依赖。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --parallel 2
cmake --build build --target check --parallel 2
./build/heat_serial --help
./build/heat_serial > build/solution.csv
./build/heat_serial --N 40 --M 1600 --T 0.1 --alpha 1 > build/solution-N40.csv
```

命名参数可独立覆盖，默认 `N=20 M=400 T=0.1 alpha=1`，此时 `r=0.1`。N 为每方向区间数（共 `(N+1)^2` 节点），M 为实际推进步数；程序计算 `dt=T/M`，不自动修改 M。要求 `N≥2,M≥1`、有限正 T 和 alpha、可表示的正 dt/r、`r≤1/4` 及可表示的双数组规模。内存须由实际机器提供，分配失败报错；大规模输入可能耗费大量内存和时间。

stdout 为最终时刻 T 的 CSV，首行为 `i,j,x,y,u_numeric,u_exact,abs_error`，按 `i*(N+1)+j` 顺序包含全部边界及内点；`x=i/N,y=j/N`，数值使用 17 位有效数字。stderr 单行记录 `N M T alpha h dt r E_inf`（`key=value`）。解析值仅用于验证；所有数值温度来自五点差分推进。退出码：0 成功，2 参数错误，1 分配/运行/输出失败；未知、重复、缺值选项均拒绝。仅单独的 `--help` 返回帮助。

基本测试阈值、手算及加密参数见 [DESIGN](docs/DESIGN.md)。这些是 M1 回归标准，不是任意输入的精度保证；本轮未做性能实验。

`check` 目标先确保测试程序已构建，再执行同一组 CTest 测试，逐项耗时按秒保留 **4 位小数**。也可直接运行 `python3 scripts/check.py --test-dir build`。耗时读取 CTest 的较高精度 XML 测量值；原始控制台输出保留在 `build/ctest-raw.log`，XML 位于 `build/Testing/<TAG>/Test.xml`。若测试失败，显示原始失败诊断并返回非零退出码。直接运行 `ctest --test-dir build --output-on-failure` 仍使用 CTest 默认的两位小数显示。

四位小数表示显示分辨率为 0.1 ms，不代表计时具有相同准确度。测试耗时包含测试进程开销，不作为求解器性能数据。原 M1 日志保持原样，补充验证见 [四位小数显示记录](docs/validation/m1-precision.log)。

## MPI 构建、运行与检查

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4
cmake --build build --target check --parallel 2
mpiexec -n 3 ./build/heat_mpi --N 20 --M 400 --T 0.1 --alpha 1 > build/mpi-p3.csv
mpiexec -n 3 ./build/heat_mpi --help
```

MPI 与串行采用相同命名参数、默认值、全场 CSV 和参数/E_inf 摘要；仅 rank 0 输出。要求 `1≤P≤N-1`，以及 `(N-1)(N+1)≤INT_MAX`，当前 int 范围对应 N≤46340；这是经典 MPI count/displacement 的保守输入限制，并非内存容量保证。分块、halo 通信表和错误路径见 [DESIGN 第 7 节](docs/DESIGN.md)。独立 `heat_serial` 继续作为正确性及后续性能基线，MPI 程序不内嵌串行复算。

帮助成功返回 0；非法输入、不稳定参数、超限 P/计数统一返回 2；可检测的分配失败或 root 输出失败统一返回 1，所有 rank 正常 Finalize。通信错误报告操作名并 MPI_Abort，以非零状态结束整个作业；具体启动器诊断可能不同。调用者必须检查退出码，输出失败可能留下部分 CSV。真实进程丢失、外部强制终止或 OOM killer 不属于此错误协调保证。

默认 CTest 包含原 6 项串行检查和 P=1/2/3/4 四项 MPI 检查，每项 MPI 超时 120 秒，内部每个启动器子进程超时 15 秒。资源较少的机器可配置 `-DHEAT_MPI_TEST_MAX_PROCS=1`（允许 1..4），减少实际运行矩阵；减少后不能宣称未运行的 P 已通过。测试尊重 CMake FindMPI 的 MPIEXEC 参数，可按集群配置 `MPIEXEC_PREFLAGS`/`MPIEXEC_POSTFLAGS`；默认不添加超额订阅或 root 运行绕过选项。

每项 MPI 检查逐点对照独立串行场，并核查连续解析误差及离散模态、全场/边界/最终层；覆盖每 rank 一行、P>1 不均匀分块、奇偶步、超限 P 和非法/不稳定输入。小规模逐点容差为 1e-13，不要求逐位相同。Linux/GNU 兼容链接器另运行测试专用分配和通信错误注入；其他平台明确记录注入未运行。`/dev/full` 在 rank 内重定向以验证输出失败。

正式记录见 [M2 验证日志](docs/validation/m2.log)，其中包含环境、真实命令、编译选项、原始 CTest 和同一次 XML 捕获的逐项数值/错误测试结果。首轮错误测试方法的失败输出另存 [首轮记录](docs/validation/m2-initial.log)，M1 历史日志未改写。M2 的测试耗时仍由 `check` 从 XML 按四位小数显示，不作为 M4 性能数据。

## M2b OpenMP 计划（尚未实现）

独立 `heat_openmp` 将沿用相同数学模型、命名参数、默认 `N=20 M=400 T=0.1 alpha=1`、全场 CSV 及解析误差摘要；具体线程控制接口、构建依赖和运行命令在 M2b 实施前确定。本节不提供尚未验证的运行命令，现有构建流程仍仅生成串行/MPI 程序及其测试。

设计采用共享全场双缓冲、内部行静态分配，各线程更新不同内点；整层完成后统一交换缓冲并同步进入下一步。MPI 并行度记为进程数 P，OpenMP 记为线程数 Q，记录请求值与实际使用值。OpenMP 允许线程多于内部行，MPI 的 P≤N-1 限制不套用到 OpenMP。

M2b 将加入单/多线程、行不能均分、线程多于内部行、奇偶步、零边界、逐点串行对照、解析误差及非法输入的基本回归，并保留既有串行/MPI 检查与四位小数显示。M4 将以同一独立串行基线、相同问题和可比计时范围比较 MPI/OpenMP，实验规模、绑定和重复次数届时冻结；当前没有 OpenMP 运行或性能结果。
