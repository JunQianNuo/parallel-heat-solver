# 二维热传导方程的串行、MPI 与 OpenMP 求解

《并行与分布式计算》期末大作业，对应教师任务书第 4 题。采用显式五点有限差分，以独立串行程序为基线，采用 MPI 行分块与邻居通信，并提供独立 OpenMP 求解器进行比较。

技术选择：C++17、CMake/CTest。必做范围为独立串行、MPI、OpenMP；暂不引入混合并行。

## 当前进度

M0、M1 串行基准已获用户验收（2026-11-10）；测试耗时四位小数显示已补齐并验证。M2 MPI 提交 `34cdd73` 已获用户验收，既有 Debug/Release 回归各 10/10 通过。M2b OpenMP 提交 `17925a9` 已于 2026-11-10 获用户验收，既有 Debug/Release 各 15/15 通过；M3 系统验证提交 `cfffe71` 已获用户验收，证据见下节；M4 已在 `Evaluation` 完成计时、23 配置/115 样本的真实实验与分析，待用户验收；Debug/Release 各 20/20 通过。结果见 [M4 实验分析](docs/performance/RESULTS.md)，M5 未开始。M2b 检查输出见 [M2b 验证记录](docs/validation/m2b.log)，历史证据保留在各阶段日志中。

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

`src/` 包含独立串行、MPI 和 OpenMP 实现，`tests/` 为基本回归。M2b 已获用户验收；`judge/m3` 的 M3 系统验证提交 `cfffe71` 已获用户验收，M4 正式性能实验已按冻结协议完成，结果见末节。

## 构建与运行

需要支持 C++17 的编译器、CMake ≥ 3.20、MPI 开发环境/启动器（本轮 Open MPI 4.1.6）和 OpenMP C++ 支持（本轮 GNU OpenMP 4.5/libgomp）；启用测试时需要 Python 3 标准库，无 GoogleTest 或联网下载依赖。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --parallel 2
cmake --build build --target check --parallel 2
./build/heat_serial --help
./build/heat_serial > build/solution.csv
./build/heat_serial --N 40 --M 1600 --T 0.1 --alpha 1 > build/solution-N40.csv
```

命名参数可独立覆盖，默认 `N=20 M=400 T=0.1 alpha=1`，此时 `r=0.1`。N 为每方向区间数（共 `(N+1)^2` 节点），M 为实际推进步数；程序计算 `dt=T/M`，不自动修改 M。要求 `N≥2,M≥1`、有限正 T 和 alpha、可表示的正 dt/r、`r≤1/4` 及可表示的双数组规模。内存须由实际机器提供，分配失败报错；大规模输入可能耗费大量内存和时间。

stdout 为最终时刻 T 的 CSV，首行为 `i,j,x,y,u_numeric,u_exact,abs_error`，按 `i*(N+1)+j` 顺序包含全部边界及内点；`x=i/N,y=j/N`，数值使用 17 位有效数字。stderr 参数行记录 `N M T alpha h dt r E_inf`（`key=value`）。解析值仅用于验证；所有数值温度来自五点差分推进。退出码：0 成功，2 参数错误，1 分配/运行/输出失败；未知、重复、缺值选项均拒绝。仅单独的 `--help` 返回帮助。

基本测试阈值、手算及加密参数见 [DESIGN](docs/DESIGN.md)。这些是 M1 回归标准，不是任意输入的精度保证；M1 当时未做性能实验。

`check` 目标先确保测试程序已构建，再执行同一组 CTest 测试，逐项耗时按秒保留 **4 位小数**。也可直接运行 `python3 scripts/check.py --test-dir build`。耗时读取 CTest 的较高精度 XML 测量值；原始控制台输出保留在 `build/ctest-raw.log`，XML 位于 `build/Testing/<TAG>/Test.xml`。若测试失败，显示原始失败诊断并返回非零退出码。直接运行 `ctest --test-dir build --output-on-failure` 仍使用 CTest 默认的两位小数显示。

四位小数表示显示分辨率为 0.1 ms，不代表计时具有相同准确度。测试耗时包含测试进程开销，不作为求解器性能数据。原 M1 日志保持原样，补充验证见 [四位小数显示记录](docs/validation/m1-precision.log)。

## MPI 构建、运行与检查

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4
cmake --build build --target check --parallel 2
mpiexec -n 3 ./build/heat_mpi --N 20 --M 400 --T 0.1 --alpha 1 > build/mpi-p3.csv
mpiexec -n 3 ./build/heat_mpi --help
```

MPI 与串行采用相同命名参数、默认值、全场 CSV 和参数/E_inf 摘要；仅 rank 0 输出，成功求解后 stderr 另记录 `P_actual`（来自 MPI_Comm_size）；请求 P 来自启动命令，M3 核对请求/实际一致。要求 `1≤P≤N-1`，以及 `(N-1)(N+1)≤INT_MAX`，当前 int 范围对应 N≤46340；这是经典 MPI count/displacement 的保守输入限制，并非内存容量保证。分块、halo 通信表和错误路径见 [DESIGN 第 7 节](docs/DESIGN.md)。独立 `heat_serial` 继续作为正确性及后续性能基线，MPI 程序不内嵌串行复算。

帮助成功返回 0；非法输入、不稳定参数、超限 P/计数统一返回 2；可检测的分配失败或 root 输出失败统一返回 1，所有 rank 正常 Finalize。通信错误报告操作名并 MPI_Abort，以非零状态结束整个作业；具体启动器诊断可能不同。调用者必须检查退出码，输出失败可能留下部分 CSV。真实进程丢失、外部强制终止或 OOM killer 不属于此错误协调保证。

MPI 基本回归包含原 6 项串行检查和 P=1/2/3/4 四项 MPI 检查（另有 OpenMP/M3 测试），每项 MPI 超时 120 秒，内部每个启动器子进程超时 15 秒。资源较少的机器可配置 `-DHEAT_MPI_TEST_MAX_PROCS=1`（允许 1..4），减少实际运行矩阵；减少后不能宣称未运行的 P 已通过。测试尊重 CMake FindMPI 的 MPIEXEC 参数，可按集群配置 `MPIEXEC_PREFLAGS`/`MPIEXEC_POSTFLAGS`；默认不添加超额订阅或 root 运行绕过选项。

每项 MPI 检查逐点对照独立串行场，并核查连续解析误差及离散模态、全场/边界/最终层；覆盖每 rank 一行、P>1 不均匀分块、奇偶步、超限 P 和非法/不稳定输入。小规模逐点容差为 1e-13，不要求逐位相同。Linux/GNU 兼容链接器另运行测试专用分配和通信错误注入；其他平台明确记录注入未运行。`/dev/full` 在 rank 内重定向以验证输出失败。

正式记录见 [M2 验证日志](docs/validation/m2.log)，其中包含环境、真实命令、编译选项、原始 CTest 和同一次 XML 捕获的逐项数值/错误测试结果。首轮错误测试方法的失败输出另存 [首轮记录](docs/validation/m2-initial.log)，M1 历史日志未改写。M2 的测试耗时仍由 `check` 从 XML 按四位小数显示，不作为 M4 性能数据。

## OpenMP 构建、运行与检查

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_OPENMP_TEST_MAX_THREADS=4
cmake --build build --target check --parallel 2
./build/heat_openmp --help
./build/heat_openmp --threads 4 --N 20 --M 400 --T 0.1 --alpha 1 > build/openmp-q4.csv
# 实际团队可能受限，摘要会同时记录请求 4、实际 2：
OMP_THREAD_LIMIT=2 ./build/heat_openmp --threads 4 > build/openmp-limited.csv

cmake -S . -B build/m2b-release -DCMAKE_BUILD_TYPE=Release
cmake --build build/m2b-release --target check --parallel 2
```

用户已确认 OpenMP 专用选项 `--threads Q`，默认 1，接受 1..INT_MAX 的十进制整数；零、负数、溢出、重复、缺值和残余文本均报输入错误（退出 2）。数值参数、默认值、CSV 与 E_inf 摘要沿用前述合同；成功输出前另在 stderr 一行记录 `Q_requested`、`Q_actual`。MPI 继续用 P 表示进程数。

程序显式请求 Q 并关闭动态调整，覆盖 `OMP_NUM_THREADS`/`OMP_DYNAMIC`；`OMP_THREAD_LIMIT` 等运行时限制仍可能使实际团队变小。实际 Q 来自推进团队内的查询，不能用请求值或 CPU 数代替。Q>N-1 合法，部分线程无行可更新但仍参与同步。`schedule(static,1)` 按整行循环分配：线程 t 得到 `1+t,1+t+Q_actual,...<N`；每步更新完成后统一交换共享双缓冲，再同步进入下一步，详见 [DESIGN 第 8 节](docs/DESIGN.md)。

独立 `--help` 成功退出 0，帮助输出失败退出 1。可捕获的分配/运行/输出错误退出 1，输入错误退出 2；输出失败可能留下部分 CSV，须检查退出码。网格在进入并行区前分配；不保证任意正 Q 都可创建，OpenMP 运行时创建失败可能自行非零终止。无效 OpenMP 环境变量的诊断由运行时负责。构建缺少 OpenMP 时明确失败，不生成伪并行替代程序；串行/MPI 不链接 OpenMP。

M2b 新增 `heat_openmp_q1..q4` 和 `heat_openmp_limited`，与原 10 项合计 15 项基本回归（M3 另加 4 项系统测试）；每项新增测试 TIMEOUT=60 秒，子进程 10 秒。`HEAT_OPENMP_TEST_MAX_THREADS=1..4` 可缩减请求矩阵（≥2 时保留请求 4/实际限制 2 的检查），但缩减后不能声称被省略的 Q 已验证。测试隔离继承的 OpenMP 调优环境，逐项核对实际团队数；资源不足导致团队不符会失败，不静默按多线程通过。check 依赖全部所需程序，仍按同次 XML 的真实耗时显示四位小数。

基本回归逐点对照独立串行并核对离散模态最终层、连续解析误差、CSV 和严格零边界，涵盖奇偶步、小网格、不能均分、线程多于行、稳定性端点、全部既有数值非法输入及线程接口错误。逐点绝对容差 1e-13，沿用 M1/M2 的小规模双精度标准；默认解析误差上限 2e-4。另实测 stdout/stderr/帮助输出失败及 Linux 子进程受限地址空间的分配失败；这不等于真实主机内存耗尽。

环境、构建选项、Debug/Release 结果及逐项请求/实际 Q、D_inf/E_inf 见 [M2b 日志](docs/validation/m2b.log)。M2b 基本实现与验证已获用户验收；M2b 实施时未运行 Q>4、线程创建失败、M3 系统实验或 M4 正式性能比较。本轮 M3 见下节，测试耗时不作为求解器性能数据。

## M3 系统正确性验证

M3 提交 `cfffe71` 已获用户验收；既有 Debug/Release 各 19/19 通过，原始证据保持不变；M3 当时未开展 M4，本轮性能结果见末节。复现全部基本回归及四项 M3 系统测试：

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4 -DHEAT_OPENMP_TEST_MAX_THREADS=4
cmake --build build --target check --parallel 2
cmake -S . -B build/m3-release -DCMAKE_BUILD_TYPE=Release -DHEAT_MPI_TEST_MAX_PROCS=4 -DHEAT_OPENMP_TEST_MAX_THREADS=4
cmake --build build/m3-release --target check --parallel 2
# 已构建后，仅重现 M3（CTest 默认耗时格式）：
ctest --test-dir build -L M3 --output-on-failure
```

`tests/check_system.py` 以 Python 标准库逐点解析三种独立程序的真实 CSV，分别检查连续解析误差、离散模态与串并行一致性。三组联合加密覆盖 r=0.05/0.1/0.25，输出每组 E_inf、阈值、D_inf、误差比和观测阶；稳定性端点及相邻浮点输入单独核查。默认每组实际 P/Q=1..4，另含请求 Q=4/实际 2；每 rank 一行、超限 P、Q>内部行及奇偶步纳入边界组。不均匀 MPI 分块由加密组和原回归覆盖。完整参数、阈值推导及覆盖表见 [DESIGN 第 9 节](docs/DESIGN.md)。

可降低既有两个资源配置值（1..4），脚本仅核验所选矩阵，不将缺失资源标为通过。每个系统测试 TIMEOUT=240 秒，子进程 25 秒，超时杀死启动器进程组。没有大于 4 的资源或多机验证结论。原始环境/命令/构建/检查及完整逐项输出见 [m3.log](docs/validation/m3.log)，加密数据见 [m3-errors.csv](docs/validation/m3-errors.csv)；CSV 来自该次 CTest 实际输出，不是解析预测值。测试用时不作为性能数据。


## M4 性能计时与实验

详细资源、计时边界、矩阵、统计和复现方法见 [性能实验协议](docs/performance/README.md)。三种程序 stderr 均增加 `loop_seconds`，仅测时间推进；MPI 含 halo 通信并取 rank 最大值，OpenMP 包括团队进入/退出、逐层同步与交换。初始化、收集、验证和输出在计时外。默认 CSV 合同保持，新增无值 `--summary-only` 省略 CSV，仍真实验证 E_inf。

```bash
./build/m4-release/heat_serial --N 128 --M 1024 --T .01 --summary-only
mpiexec --map-by core --bind-to hwthread -n 4 ./build/m4-release/heat_mpi --N 128 --M 1024 --T .01 --summary-only
OMP_PLACES='{0},{2},{4},{6}' OMP_PROC_BIND=close ./build/m4-release/heat_openmp --threads 4 --N 128 --M 1024 --T .01 --summary-only
```

本机实验使用 CPU 0/2/4/6；迁移机器先核查可用 CPU 与绑定。正式数据采样、统计与图表命令见协议，不将上述单次示范或 CTest 时间作为性能结论。新增 `heat_timing` 检查计时字段、摘要/全场一致及错误路径；`python3 tests/check_statistics.py` 使用合成数据独立核查统计方法。M4 实施完成，待用户验收，不进入 M5。


实测证据与 Amdahl/Gustafson 分析见 [RESULTS.md](docs/performance/RESULTS.md)，完整统计见 [summary.csv](docs/performance/derived/summary.csv)。两组强扩展固定 T=0.01、alpha=1；N=384/M=9216 下 MPI P=4 主基线加速比为 1.521、效率 38.04%，OpenMP Q=4 加速比为 0.976。扩大累计工作量组 p=4 的自身基础网格吞吐增长分别为 MPI 2.205、OpenMP 0.804；不将不同基线的指标混用。原始 23 次完整场验证观测 D_inf 全为 0。源码版本为 `75cdaad`，测量期间源码和二进制哈希未变；原始样本、环境、绑定、编译命令、图表与复现方法均已保留。
