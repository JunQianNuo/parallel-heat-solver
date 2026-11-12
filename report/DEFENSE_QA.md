# 答辩问题与回答

以下是基于仓库证据的准备答案；本人需理解后用自己的话回答。没有记录的人工操作不作为个人贡献。源码位置以函数名定位，避免材料行号随文档变化失效。

| 问题 | 回答要点 | 证据 |
| --- | --- | --- |
| 为什么选这个模型？ | 零边界和正弦初值有连续解析解，可同时验证推进精度与并行一致性；模型来自题目，不用课程一维参数替代。 | [SPEC](../SPEC.md) |
| N是节点数吗？ | 每方向N个区间、N+1节点；内部(N−1)²；M是时间步数，MPI为P、OpenMP为Q。 | [DESIGN](../docs/DESIGN.md) |
| 五点格式怎么来？ | 时间向前差分，x/y各用二阶中心差分，整理为中心权重1−4r和四邻居权重r。时间一阶、空间二阶。 | [报告第2节](FINAL_REPORT.md#2-数学模型离散与稳定性) |
| 为什么r≤1/4？ | 误差模态放大因子1−4r(sin²θx/2+sin²θy/2)，最坏和为2，要求绝对值≤1；二维上限1/4。一维1/2不可套用。 | [报告](FINAL_REPORT.md) |
| 稳定就准确吗？ | 不等同。稳定限制误差放大，截断误差仍依赖h/dt；同T解析误差和加密趋势单独验证。 | [系统测试](../tests/check_system.py) |
| 为什么两个数组？ | 新层只能读同一旧层；原地更新会把已经更新的邻居混进右端，改变算法并引入依赖。每层swap，M奇偶不影响终层选择。 | [heat.cpp：step/solve](../src/heat.cpp) |
| 解析解是否用于偷算终值？ | 没有。每步真实五点更新；连续解析解、离散模态只用于验证，初值计算空间正弦形状。 | [heat.cpp](../src/heat.cpp) |
| 联合二阶等于时间二阶吗？ | 不是。dt∝h²时O(dt+h²)都随h²缩小；N加倍、M四倍才观察约4倍误差比，且需避开特殊误差抵消。 | [M3数据](../results/validation/m3-errors.csv) |
| E_inf与D_inf有何不同？ | E是离散结果对连续解析解误差；D是并行对独立串行差。并行完全复现同一个错误仍可能D=0，因此两者都测。 | [系统测试](../tests/check_system.py) |
| 为什么需要离散模态？ | 连续解析误差包含截断误差；g^M模态直接检查离散算法的最终时间层，配合非对称手算减少仅正弦对称测试漏错的风险。 | [DESIGN第6/9节](../docs/DESIGN.md) |
| MPI怎么处理不均匀行？ | q=floor((N−1)/P)，余数s分给前s个rank；offset=pq+min(p,s)。例N8/P3分3/2/2行。 | [mpi_block](../src/heat_mpi.cpp) |
| halo与物理边界有何区别？ | halo存邻居拥有的旧层行，物理边界由题设固定零；端部PROC_NULL接收不会自动清零，代码显式维护。 | [solve_mpi](../src/heat_mpi.cpp) |
| 为什么用两次Sendrecv？ | 首行向上/收下halo，末行向下/收上halo，用标签71/72区分方向；避免朴素全体先阻塞send的死锁风险。 | [solve_mpi](../src/heat_mpi.cpp) |
| MPI每步有全局屏障吗？ | 没有。计时前一次Barrier在计时外；每步通过邻居Sendrecv完成数据依赖。 | [solve_mpi](../src/heat_mpi.cpp) |
| P≤N−1是MPI限制吗？ | 是本实现确保每rank至少一行的约束；MPI本身可支持空任务rank，当前没实现。还检查经典int计数/位移范围。 | [mpi_block](../src/heat_mpi.cpp) |
| MPI错误会挂死吗？ | 可捕获分配/输入/输出错误通过集体状态协调；通信错误Abort，测试设超时。真实进程丢失/OOM killer不在保证范围。 | [main_mpi](../src/main_mpi.cpp)、[错误测试](../tests/check_mpi.py) |
| OpenMP怎么划分行？ | 正式static,1：线程t取1+t、1+t+A…，A为实际团队；MPI则连续分块。诊断block连续划分未进入正式程序。 | [solve_openmp](../src/heat_openmp.cpp) |
| OpenMP变量哪些共享/私有？ | old/next/actual_threads共享；N/M/w/r firstprivate只读副本；n/i/j/k私有；各线程只写自己行的新层内点。 | [solve_openmp](../src/heat_openmp.cpp) |
| 能删single屏障吗？ | 共享vector角色交换需要发布；for屏障保证新层写完，single屏障保证所有线程看到交换。直接nowait不安全。私有指针替代属于另一个已隔离诊断设计。 | [OpenMP源码](../src/heat_openmp.cpp) |
| Q可以超过内部行数吗？ | 可以，空闲线程仍参加屏障；MPI每rank一行的约束不套用OpenMP。线程请求可很大，但实际创建不保证成功。 | [OpenMP测试](../tests/check_openmp.py) |
| 请求/实际P/Q怎么记？ | P请求来自mpiexec命令，实际来自Comm_size；Q请求来自--threads，实际在推进团队中get_num_threads。运行时限制可使Q缩小。 | [入口](../src/main_mpi.cpp)、[OpenMP源码](../src/heat_openmp.cpp) |
| 为什么不拿MPI1作Ts？ | 教师/项目比较独立串行与并行。同算法不代表实现成本相同。N1024 MPI1=48.3156s、serial=35.3892s，换基线会明显改变S的含义。 | [结果](../results/RESULTS.md) |
| 计时到底包括什么？ | serial含step检查/边界/更新/swap；MPI含halo/等待/局部更新/swap并取rank最大；OpenMP含一次团队进出/查询/逐层同步交换。初始化、收集、归约、验证、输出在外，MPI开始Barrier也在外。 | [计时协议](../results/performance/baseline/README.md) |
| MPI各rank时钟需要同步吗？ | 各rank只取自身起止差，再max，不跨rank相减绝对时刻；但max归约本身不计入推进。 | [MPI源码](../src/heat_mpi.cpp) |
| CTest时间为什么不用于加速比？ | 它包括测试组织、启动、输出、验证等，范围与loop_seconds不同。 | [协议](../results/performance/baseline/README.md) |
| 两种“中位数”有何区别？ | median(Ts)/median(Tp)不一定等于median(Ts_i/Tp_i)。原M4/02-r1用前者；诊断配对对照用后者，各有对应重采样。 | [DESIGN](../docs/DESIGN.md) |
| min/max是置信区间吗？ | 只是本批样本极值。bootstrap95%区间是有限重复、特定重采样模型下的探索性结果，未多重校正，不能去除趋势或证明根因。 | [结果](../results/RESULTS.md) |
| 16是16个物理核心吗？ | 16逻辑CPU，覆盖14个WSL可见core，含兄弟硬件线程；不能证明宿主物理独占或P/E核映射。 | [02-r1元数据](../results/performance/large-02-r1/m4-diagnostic-02-r1.json) |
| 强扩展与扩大工作量怎么区分？ | 同一N/M/T/alpha改变p为强扩展；跨N同时改变M是联合加密。W=M(N−1)²，固定T/r时W约N⁴；不能仅用节点/worker相似称弱扩展。 | [报告第5/6节](FINAL_REPORT.md) |
| Amdahl能反推出真实串行比例吗？ | f_eff包含通信同步、实现与环境影响，同规模不同p不恒定，甚至>1，不能当代码串行百分比或外推无限核上限。 | [原M4分析](../results/RESULTS.md) |
| 实验验证了Gustafson吗？ | 只能讨论适用前提。原扩大实验W约随p增长，但时间未保持相近、sigma未单测，不能虚构sigma或宣称线性加速实证。 | [原协议](../results/performance/baseline/README.md) |
| 为什么OpenMP16更慢？ | N1024中位数21.4382s比Q8的19.6692s长；16还改变同core线程共享。没有独立分离共享/带宽/同步/宿主，不能指定唯一原因。8/16直接比率没有另建区间。 | [02-r1](../results/RESULTS.md) |
| 为什么不简单说问题太小？ | N1024串行推进数十秒，MPI1仍慢；诊断支持计算上下文与行划分影响，每步粒度/同步和环境也需区分。 | [结果](../results/RESULTS.md) |
| 诊断究竟证明了什么？ | 未插桩replica对照支持MPI公共内核及OpenMP连续行影响；不证明唯一缓存机制。baseline/replica/插桩两层校准限制分项，收益不能直接冒充正式S。 | [诊断结果](../results/RESULTS.md#补充诊断运行01) |
| 为什么不把优化合入？ | 本阶段授权是最终材料，正式优化另需用户确认；保持正式数据对应原程序和冻结源码。 | [DECISIONS](../docs/DECISIONS.md) |
| UTC回退会令全部结果无效吗？ | 不能用UTC计算耗时。正常路径用单调时钟，有库身份/反汇编审计；但未外部物理校准，仍保留虚拟机影响限制，不宣称已完全排除。 | [时钟审计](../results/performance/large-02-r1/m4-diagnostic-02-r1-clock-audit.log) |
| 早期慢样本为什么不删？ | 34/44配置有趋势，删除会改变冻结口径；保留全部轮次并披露，bootstrap也不能消除全部时变影响。 | [逐轮图](../results/figures/large-02-r1-viz-01/08-rounds-mpi.svg) |
| 失败02怎样处理？ | 预热报告检查停止，0正式样本，全部留证；修正后用02-r1重新冻结运行，不混合或伪装重试。 | [失败证据](../results/performance/large-02/m4-diagnostic-02-failure.log) |
| 你本人和AI各做了什么？ | 本人负责范围、管理、审核与答辩；Codex辅助实现、验证、采样分析和材料。不声称本人独立手写AI代码；具体人工核查只按已记录事实回答。 | [AI_USAGE](../docs/AI_USAGE.md) |
| 如何核查AI输出？ | 示例：MPI错误测试首轮4项失败，修正rank内重定向并留日志；数值靠独立解析/模态/串行全场，统计从原始样本重算；阶段验收不冒充人工复现。 | [首轮失败](../results/validation/m2-initial.log)、[修正](../results/validation/m2.log) |

现场定位顺序：题设与公式→对应solve函数→测试判据→原始数据/统计CSV→图表。答不确定机制时明确说“当前证据未分离”，不要临场补造实验。最终文件中的待填写个人信息和人工演练记录须本人完成。
