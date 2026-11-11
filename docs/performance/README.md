# M4 性能实验协议与复现

本轮仅开展 M4。协议在正式采样前写入 [protocol.json](protocol.json)，不以获得加速为规模选择条件。权威依据是本地只读 `docs/sources/final.pdf` 第 1、3 页；方法参考 OpenMP《03-性能评测标准》、MPI 第十一讲第 12–14 节和 `11_heat_mpi/程序详解.md` 第 9、11 节。任务书文本和原页均已重新核对；一维示例的边界、稳定性和数据不用于本项目。

## 机器与构建

单机 WSL2、Intel i7-14700HX，来宾暴露 28 逻辑 CPU/14 核、约 7.6 GiB 内存；仅使用暴露核心 0–3 的首个硬件线程，即 Linux CPU 0/2/4/6，不使用其 SMT 同胞。虚拟拓扑不能证明宿主物理核独占或 P/E 核映射。cgroup `/init.scope` 的 cpu.max=`max 100000`、memory.max=`max`，主机非独占。GNU C++ 13.3.0、Open MPI 4.1.6、GNU OpenMP 4.5/libgomp；精确版本、限制、链接及编译命令在每次运行环境中归档。

三种实现均 C++17 Release `-O3 -DNDEBUG`，无 fast-math、无 march=native、无 LTO；只对 OpenMP 目标添加 `-fopenmp`。独立串行与 MPI 不链接 OpenMP。编译警告选项保持原配置。

```bash
cmake -S . -B build/m4-release -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHEAT_MPI_TEST_MAX_PROCS=4 -DHEAT_OPENMP_TEST_MAX_THREADS=4
cmake --build build/m4-release --parallel 2
cmake --build build/m4-release --target check --parallel 2
python3 scripts/benchmark.py --build build/m4-release --output docs/performance/run-01
python3 scripts/analyze_performance.py docs/performance/run-01 --output docs/performance/derived
```

脚本要求已提交的源码/脚本/协议以及符合冻结选项的 Release 构建，确保样本中的代码提交有确切含义。重新采样必须选择新的输出目录，不覆盖既有证据。采样脚本限于本轮 Linux/Open MPI 环境；迁移机器须先更新协议并重新核查 CPU 列表、绑定、资源和 MPI 参数，不能直接沿用。统计只需 Python 标准库（`--no-plots`），绘图使用 Matplotlib（本机 3.6.3），图为独立 SVG/PNG 文件。

串行 `taskset -c 0`；MPI `--map-by core --bind-to hwthread --report-bindings`，本机 rank 0/1/2/3 对应 CPU 0/2/4/6，逐次保存启动器绑定信息。OpenMP `OMP_PLACES='{0},{2},{4},{6}' OMP_PROC_BIND=close OMP_WAIT_POLICY=ACTIVE OMP_THREAD_LIMIT=4`，显式请求 Q 并关闭动态调整。脚本清除继承的 OMP/GOMP/KMP/OMPI/PMI/PMIX 调优变量后设置协议环境；预热用 `OMP_DISPLAY_AFFINITY=TRUE` 保存实际线程绑定，正式样本关闭诊断。无超额订阅。实际 P/Q 必须等于请求值，否则终止采样。

## 计时合同

所有入口额外输出 stderr `loop_seconds`，17 位有效数字、秒。默认全场 CSV 保留；无值标志 `--summary-only` 只省略 stdout CSV，仍真实推进、收集并验证 E_inf。重复该选项报输入错误。不能用 `/dev/null` 输出的端到端耗时替代推进时间。

| 实现 | 时钟与边界 | 包含 |
| --- | --- | --- |
| serial | 初始化之后、M 次 step 之前到最后一次 swap 之后；steady_clock | 已验收 step 的参数/缓冲检查、边界清零、内点更新、双缓冲交换 |
| MPI | 初始化后 Barrier（不计时）；各 rank 自己的 MPI_Wtime 差，MPI_Reduce MAX 到 root | 全部 M 步两次 halo Sendrecv/通信等待、物理 halo 清零、局部边列/内点更新、交换 |
| OpenMP | omp_set_dynamic 后、进入 parallel 之前到离开 parallel 之后；同一主线程 omp_get_wtime 差 | 一次团队进入/退出、实际团队查询、M 步 static,1 更新、for 屏障、single 交换及屏障 |

三者均排除参数解析、分配、初始化、解析误差验证和输出；MPI 还排除 MPI_Init/Finalize、参数广播、计时前 Barrier、计时归约、误差归约及 Gatherv。MPI 不跨 rank 相减绝对时钟，不在循环中增加全局 Barrier。OpenMP 包含进入/退出的成本；运行时可能复用工作线程，因此不将其解释为每次必然创建和销毁操作系统线程。团队内所有必要同步和交换均计入。

保留各实现原有边界策略与内核检查，以已验收独立串行为主基线。这些固有成本、MPI 通信和 OpenMP 同步是比较对象的一部分，不据此声称测量的是纯算术吞吐或端到端性能。计时只有循环首尾读钟，没有逐步读钟。额外记录的 Python wall_seconds 包含启动、验证和输出，只用于追溯。

## 矩阵、工作量与验证

全部固定单位区域、零边界、正弦初值、T=0.01、alpha=1。每配置先完整场预热一次（排除其耗时），然后五次独立新进程采样。预热可热身缓存/CPU，但新进程正式样本仍包含自己的首次团队进入；不能称为持久进程的稳态计时。每轮按种子 20261110 打乱全部配置，逐个运行，不与构建/CTest 或其他本项目性能作业重叠；宿主其他活动不能排除。不剔除离群值、不自动重试失败样本。

强扩展两组 N/M：128/1024 和 384/9216，r=0.16；每组 serial×1、MPI P=1/2/4、OpenMP Q=1/2/4。比较中固定 N/M/T/alpha，以相同独立 serial 中位数作 Ts。P=1/Q=1 只是各自实现的补充数据，不能替换 Ts。

扩大工作量实验针对每种并行方式，目标 p=1/2/4 分别采用 N/M=256/4096、304/5776、362/8191；每种规模均额外运行独立 serial 作为相同问题基线。共有 23 个配置、23 次全场预热及 115 次正式样本。

定义累计有效内点更新量 `W=M(N−1)²`，不计初始化、halo 和边界。固定 T 与 r 近似不变要求 M∝N²，而二维内点约∝N²，故 W∝N⁴。为 W≈pW1，取 N≈256*p^(1/4)，M≈0.01*N²/0.16，再取整；实际参数与 r 必须逐次核查。W/p 为平均值；MPI 连续余数划分和 OpenMP 循环整行划分产生的最小/最大工作行数分别为 floor((N−1)/p)、ceil((N−1)/p)，每工作行累计更新 M(N−1)。线程多于行数的情形由正确性回归覆盖，不出现在性能矩阵。扩大网格不改变题设物理域或终点。

| 目标 p | N | M | 实际 W | 平均 W/p | W/W1 | W/(pW1)−1 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 256 | 4096 | 266342400 | 266342400 | 1 | 0 |
| 2 | 304 | 5776 | 530288784 | 265144392 | 1.991004 | −0.4498% |
| 4 | 362 | 8191 | 1067459311 | 266864827.75 | 4.007846 | +0.1961% |


完整场预热逐点验证最终离散正弦模态 `U0*(1−8r*sin²(pi/(2N)))^M`（差<2e-11）、独立连续解析误差（E_inf≤2e-5，摘要差<1e-14）、严格零边界、有限值和排序；同规模串并行 D_inf≤1e-12。阈值适用于本矩阵：N≥128、r≈0.16，主截断误差约 0.123/N²，小于选定上限；较多时间步的模态浮点参考给额外舍入余量，仍远小于截断误差。所有正式样本检查参数、稳定性、实际团队与 E_inf。保留 M1–M3 全部正确性回归，新增 M4 计时接口/摘要/输出失败检查；不设耗时必须随 p 下降的断言。

## 统计与解释

每次 MPI 样本先取 rank 内循环耗时的最大值，再在五个作业样本上计算中位数、最小/最大；不能交换顺序。三种程序一律同样统计。`S=median(Ts)/median(Tp)`，`E=S/actual_p`，不取配对比率的中位数或最快样本。图中时间误差条是样本范围，不是置信区间。效率>1 或 S<1 如实保留。

强扩展结合 `S=1/[f+(1−f)/p]` 讨论固定工作量；可由测量反推有效值 `f_eff=(p/S−1)/(p−1)`，它包含同步、通信、缓存、频率和负载效应。负值或不同 p 下不一致意味着常数串行比例模型不充分，不能当真实代码串行比例，也不外推无限并行加速。

扩大工作量不能因每 worker 节点数接近称为弱扩展：记录实际 W、W/p、W/W1 和负载取整偏差。相同规模串行的 S/E 仍按上式；另外定义相对各实现 p=1 基础网格的吞吐增长 `R=(W/W1)*Tp1/Tp`，归一化指标 `R/target_p`，只有 W/W1 恰等于 p 时才退化为常见弱扩展效率 Tp1/Tp。serial 在这组始终仅用一个 CPU，其归一化指标只作参照，不称 serial 并行效率。

Gustafson `S_G=p−sigma(p−1)` 针对扩大并行工作且串行时间占比 sigma 较小的情形。这里 W 随 p 近似增长，但实际时间未必不变；没有单独计时串行部分，因此不拟合或虚构 sigma，不把公式预测曲线当实测。结合实际吞吐、同规模 S/E、同步/通信开销及工作量约束讨论本机有限规模的表现。

## 证据

`run-01/metadata.json` 包含代码提交、源码/协议/二进制 SHA-256、完整编译命令、运行环境；`environment.log` 为真实系统/运行时/资源输出，`matrix.json` 为矩阵。`samples.jsonl` 保存每次请求、实际摘要、命令、时间戳、退出码、完整 stderr、stdout 哈希，另存逐配置全场验证指标。stdout 全场仅用于即时独立逐点检查，保留哈希与指标，不将大网格 CSV 当性能样本上传。`complete.json` 仅在全部检查完成且源码/二进制哈希未变化时生成。任何失败都会先保存原始结果并停止。

`derived/summary.csv` 与图由分析脚本从原始 JSONL 重算，拒绝缺样本、重复、参数/资源/版本不一致或未完成记录。图表和最终分析在正式采样完成后生成，不覆盖原始样本。环境/回归日志不等于性能结果；本轮回归日志为 [m4.log](../validation/m4.log)。


资料保护核查的限制：本轮跨环境恢复，最初 `/tmp` 哈希清单丢失，不能完成最初开工至收尾的全程哈希对照；恢复后新建忽略的 `build/m4-sources-resume.json`，核查 2,564 个资料文件的后续路径与内容一致。资料始终仅用只读命令访问，未跟踪、暂存或上传。
