# 项目状态

更新日期：2026-11-11（Asia/Shanghai）。

## 当前阶段

- M0：用户已验收通过（2026-11-10）。M1：串行基准已获用户审查通过（2026-11-10），含测试耗时四位小数显示补充的整个分支已获用户再次确认审查通过；M2 MPI 提交 `34cdd73` 已获用户验收通过；独立 M2b OpenMP 提交 `17925a9` 已于 2026-11-10 获用户验收通过；M3 系统验证提交 `cfffe71` 已获用户验收通过；M4 已由用户选择，正在 `Evaluation` 开展性能实验；M5 未开始。
- 当前功能分支：`Evaluation`（用户准备）；本轮开始 HEAD、本地 main、origin/main、judge/m3 均为 `69fb1d0`，工作区干净，远程 main 已核实包含 M3 实现和验收记录。仅在当前分支提交推送同名远程，不创建/切换分支、不合并 main。下文旧分支状态均为历史事实。
- 已确认：任务书第 4 题，C++17 + CMake/CTest，独立串行 + MPI + OpenMP；串行、MPI 与 M2b OpenMP 均已验收，暂不引入混合并行。
- 课程资料位于 `docs/sources/`，仅本地只读，不纳入 Git；目录与现有文件均保留。

## M0 文档建立记录

补全 SPEC、PLAN、DESIGN、DECISIONS、AI_USAGE、README 与本状态文件；修正 AGENTS 的资料路径、Markdown 转义和必做范围；添加忽略规则。本轮不新增求解器、构建配置或实验数据。

## M0 验证记录

教师任务书第 1、3 页已在 M0 规划中查看原页，确认模型、五点显式格式、解析解、稳定性与交付要求；实施时读取课程第十、十一讲及参考 CMake 配置。本轮检查结果如下；文档检查不代表求解器实现已验证。

| 检查 | 命令或方法 | 状态 |
| --- | --- | --- |
| 分支、工作区与历史 | `git branch --show-current`、`git status --short`、`git log -5 --oneline` | 已确认位于用户指定分支；开始时文档与课程资料未跟踪，无已跟踪文件改动或合并冲突 |
| 文档链接与参考路径 | Python 检查 Markdown 相对文件链接、本地设计参考路径及公式/代码块闭合 | 通过：11 个相对文件链接有效，设计参考路径存在，8 份 Markdown 文档结构检查通过 |
| 课程资料只读 | 对 `docs/sources/` 全部 2,564 个文件的 SHA-256 内容清单作前后比较，清单存于仓库外 | 通过：文件路径清单与全部内容哈希一致，资料未被修改 |
| 忽略与提交边界 | `git check-ignore -z --stdin`、`git status --short --untracked-files=all`、`git diff --cached --name-only` | 通过：2,564 个资料文件与空白临时文件均被忽略，工作区与暂存清单仅含本任务的 9 个文档/配置文件 |
| 差异格式检查 | `git diff --check`、`git diff --cached --check`、`git diff --cached` | 通过：无空白格式错误，已审阅完整暂存差异 |
| 项目构建、数值测试与性能实验 | 不适用于本轮文档建立 | 未运行：尚未实现代码 |

## M1 实现与验证记录

重新核对任务书第 1、3 页文本及原页图像，阅读第九、十讲及串行示例 CMake 配置。未发现影响 M1 的资料冲突；一维示例的非零边界、参数和稳定性上限均未沿用。M1 新增 C++17 五点差分串行求解器、双缓冲、完整参数校验、全场 CSV 与参数/解析误差摘要，以及独立 C++/Python 基本检查。接口偏好回复到达前按已提出方案实施；用户随后明确确认命名参数、默认 20/400/0.1/1 和全场 CSV，与实现一致。容差方案见 DESIGN 第 6 节及 DECISIONS D007–D011，用户随后回复“暂无其他问题，审查通过”，M1 串行基准验收通过。

| 检查 | 实际命令或方法 | 本轮结果 |
| --- | --- | --- |
| 配置 | `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug` | 成功，CMake 3.28.3、GNU C++ 13.3.0、Python 3.12.3；无第三方测试依赖 |
| 构建 | `cmake --build build --parallel 2` | 成功，求解器及 CLI 开启 `-Wall -Wextra -Wpedantic`，无警告 |
| 基本回归 | `ctest --test-dir build --output-on-failure` | 6/6 通过：initial、hand、parity、validation、analytic、cli |
| 内存/未定义行为检查 | ASan/UBSan 配置及 `cmake --build build/sanitize --parallel 2`、`ctest --test-dir build/sanitize --output-on-failure` | 6/6 通过，完整配置命令见原始日志 |
| 解析误差原始输出 | `build/heat_tests analytic` | T=0.1、alpha=1，N/M=20/400、40/1600、80/6400，E_inf 分别为 `0.0001126210917414272`、`2.8181351120953879e-05`、`7.0469626000380092e-06`；阈值及基本加密比通过 |
| CLI 原始输出 | `python3 tests/check_cli.py build/heat_serial` | 6 组合法输入全场核对、30 组非法输入、帮助及 `/dev/full` 输出失败检查通过 |
| 课程资料保护 | 前后路径/SHA-256 清单对照；`git check-ignore -z --stdin` | 2,564 个文件路径/内容一致，全部被忽略；清单与 PDF 临时图像在 `/tmp/`，不提交 |

真实配置、构建、CTest 和数值输出保存在 [validation/m1.log](docs/validation/m1.log)。CTest 用时仅为检查日志，不作为性能测量。未运行 MPI 检查、正式性能实验或 M3 系统验证。分配失败有异常处理，但未故意耗尽机器内存；可表示的输入规模不保证实际可分配。

## 阻塞与待定事项

当前无已知 M4 实施阻塞。M3 已验收并合并，三种求解器数值合同保持原约定。M4 实验协议见 docs/performance/README.md；报告/PPT 留待用户选择 M5；课程资料仅本地存在，新克隆须由使用者补齐。M3 证据、覆盖和未验证项见末节。

## 下一步

完成 M4 计时回归、正式采样、统计绘图及分析，提交推送 `Evaluation` 交用户验收；不进入 M5。下文保留历史事实，本轮状态见末节。

## M1 接口确认记录同步

用户于 2026-11-10 回复“采用建议：命名参数、20/400/0.1/1、全场 CSV”。本次仅同步 SPEC、STATUS、DECISIONS 和 AI_USAGE 的确认状态；未修改代码或数值参数，未重跑构建/数值测试（纯文档变更），执行差异及暂存检查。串行实现提交为 `d568e45`，已推送 `origin/feature/m1-Serial`；接口确认不等于 M1 整体验收。

## M1 验收与耗时显示补充

用户明确回复“暂无其他问题，审查通过”，随后指出精确小数位数尚未修改。本轮补齐 `cmake --build build --target check --parallel 2` 入口：执行 CTest 并从 XML 测量值按秒显示四位小数，保留原始输出与失败状态。未修改求解器或旧日志。

实际执行 `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug`、`cmake --build build --target check --parallel 2` 成功，6/6 通过；六项显示值与 XML `.4f` 结果逐项一致。另在 `/tmp/` 临时 CMake 项目构造 `cmake -E false` 测试，脚本显示真实失败诊断并返回 CTest 退出码 8。补充真实日志见 [m1-precision.log](docs/validation/m1-precision.log)。本轮未重新运行 ASan/UBSan（求解器及数值测试未变）；未开展性能实验。文档同步验收事实，下一阶段仍由用户选择。

## M1 分支最终验收

2026-11-10，用户在澄清 CTest 原始文本与 XML 四位小数摘要的关系后，明确回复“该分支审查通过”。验收对应 `feature/m1-Serial` 的 `7dd9329`，包含串行基准、基本测试与四位小数显示补充。此次仅同步 STATUS 和 AI_USAGE 的最终验收记录，检查文档差异和暂存范围；未重跑构建或数值测试（无代码变更）。由用户负责合并，M2 尚未授权开始。

## M2 实现与验证（2026-11-10，历史实施记录）

本轮实现 MPI 内部行不均匀分块、局部双缓冲、两次旧层整行 Sendrecv、PROC_NULL 物理边界、Gatherv 全场重建及解析误差最大值归约。保留独立串行内核和程序，共用命名参数/CSV 逻辑。错误路径、MPI 计数限制、测试容差及资源配置见 DESIGN 第 7 节和 DECISIONS D013–D018。

重新查看任务书第 1、3 页原页，第十、十一讲与 MPI 示例源码、测试及 CMake；未发现影响 M2 的资料冲突。环境为 WSL2 Linux、Intel i7-14700HX、28 个可见逻辑 CPU（亲和性 0–27）、约 7.6 GiB 系统内存、GNU C++ 13.3.0、CMake 3.28.3、Python 3.12.3、Open MPI 4.1.6（FindMPI 报告支持 MPI 3.1）。启动器默认 14 slot，当前 /init.scope 的 cpu.max=`max 100000`、memory.max=`max`；根路径的 quota 文件不存在，不据此推断独占资源。本轮只实际验证 P=1/2/3/4，无超额订阅。

| 检查 | 实际命令/方法 | 结果 |
| --- | --- | --- |
| Debug 配置/构建 | `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`；`cmake --build build --parallel 2` | 成功，-g、C++17、-Wall/-Wextra/-Wpedantic；无编译警告 |
| Debug 检查及四位小数 | `cmake --build build --target check --parallel 2` | 10/10 通过，原 6 项串行及 P=1/2/3/4 MPI；同次 XML 记录逐项数值及错误检查输出；两种构建显示的四位小数逐项与各自 XML 核对一致 |
| Release 配置/构建/检查 | 将上述构建目录改为 `build/m2-release`，类型改为 Release | 成功，-O3 -DNDEBUG；无编译警告，10/10 通过（含 P=1/2/3/4） |
| 数值检查 | 每个 P 的默认场、每 rank 一行、P>1 不均匀分块、奇偶步，P=1 稳定性端点；逐点 CSV/模态/连续解析核查 | Debug/Release 全部通过；观测 D_inf 均为 0（采用容差≤1e-13，不要求逐位相同）；默认场 E_inf=`0.0001126210917414272`，小于 2e-4 |
| 退出路径 | 参数/稳定性/计数/P 限制、帮助、rank 内 /dev/full、测试专用 root/worker bad_alloc 及 Sendrecv 错误注入 | Debug/Release P=1..4 全部通过，无超时；通信错误经 MPI_Abort 返回非零；分块遍历及大计数边界无需分配大场 |
| 首轮失败及修正 | 最初把启动器而非 rank 的 stdout 接到 /dev/full | 首轮 6/10 通过、4 项 MPI 输出失败断言不通过；改为 rank 内重定向，保留真实首轮日志，不改写 M1 日志 |
| 资料与文档边界 | 全部课程文件前后路径/SHA-256 对照及 git check-ignore，文档相对链接/代码块检查 | 2,564 个资料文件一致、全被忽略且无跟踪资料；文档检查通过 |

正式环境、命令、编译选项与原始输出见 [m2.log](docs/validation/m2.log)；首轮失败见 [m2-initial.log](docs/validation/m2-initial.log)。`check` 的原始终端文本与逐项输出来自同一次 CTest XML，显示耗时仍保留四位小数。

未运行：P>4、多机通信、真实内存耗尽/进程丢失、ASan/UBSan（本轮未重跑）、M3 系统化验证及 M4 正式性能实验。测试专用受控错误注入不能替代这些未运行项。实施完成时 M2 尚待用户验收；后续已验收通过，见末节。不自动进入下个里程碑；提交及同名分支推送结果以实际 Git 输出及最终汇报为准。

提交前审阅：按文件明确暂存并检查完整差异；源码/文档空白检查通过，日志保留 CMake 原始的 3 行末尾空格，使用仅本次命令的 `core.whitespace=-blank-at-eol` 检查。最后仅把测试汇总文案缩为“help checked”，避免其他平台缺少 /dev/full 时与明确未运行提示冲突；测试逻辑未变，此文案修改未重跑数值检查。

## M2 验收与 M2b OpenMP 范围确认（2026-11-10）

用户明确确认 MPI 提交 `34cdd73` 已验收通过，并选择独立 M2b OpenMP，安排在 M3 之前；暂不引入 MPI+OpenMP 混合并行。保留 M2 已验收基线，M2b 计划提供独立 `heat_openmp`，沿用数学模型、命名参数、默认值、CSV 和精度标准；线程控制接口在实施前确定。进程数记为 P、线程数记为 Q，记录请求值与实际使用值，MPI 的 P≤N-1 不套用于 OpenMP。

本次仅更新 AGENTS、SPEC、PLAN、STATUS、DESIGN、DECISIONS、AI_USAGE 和 README 八份文档，追加范围和验收记录，保留原有历史决策背景及全部验证日志；未实现 OpenMP，未更改源码、CMake 或测试。M3 将系统验证三种实现，M4 使用同一独立串行基线分别比较 MPI/OpenMP，实验规模、绑定、重复次数待 M4 冻结。

本轮验证限于文档链接、代码块/阶段依赖、范围表述、资料保护及完整差异/暂存边界检查。未运行构建、数值测试、OpenMP 环境探测或性能实验（纯文档变更）；M2 既有运行证据仍以 m2.log 为准，不新增通过结论。检查结果与提交/推送状态在本节及最终汇报记录，不自引用尚未生成的提交哈希。

本次检查结果：8 份指定文档结构检查通过，21 个相对链接有效，M2b→M3 阶段依赖及范围检查通过；`git diff --check` 通过。2,564 个课程文件前后路径/SHA-256 一致、全部被忽略且未跟踪；源码、CMake、测试、脚本与全部历史日志相对 HEAD 无差异。提交前按文件暂存并审阅完整暂存差异，仅包含上述八份文档；提交和同名分支推送结果以实际 Git 输出及最终汇报为准。


## M2b 独立 OpenMP 实施与验证（2026-11-10，历史实施记录）

新增 `heat_openmp` 独立入口及共享双缓冲内核，保留独立串行、MPI 数值代码；仅在共用 CLI 中为 OpenMP 入口启用 `--threads Q`。用户了解默认行为差异后明确选择默认 1、显式 `--threads`。采用持续团队、内部行 `schedule(static,1)`、for 隐式屏障、single 交换及其隐式屏障；循环索引/临时变量私有，共享 old/next 的读取和交换严格分层。两份数组边界初始化为零后不再改写；Q>内部行数合法。无 MPI+OpenMP 混合、halo 或收集扩展。

重新读取任务书第 1/3 页文字与原页图像，发现并查阅 OpenMP 第 5/6 讲及 01/04/06b/07/09 示例/Makefile。未发现影响 M2b 的冲突；仅参考线程控制、共享/私有、同步、双缓冲方法，不移植其他模型参数或停止条件。独立调度探针实际核对 N=2/7、Q=1..4 的行归属，记录于 m2b.log。

环境：WSL2 Linux 6.18.33.2，i7-14700HX，亲和性 0–27、可见 28 逻辑 CPU，约 7.6 GiB 内存，/init.scope cpu.max=`max 100000`、memory.max=`max`，非独占环境。GNU C++ 13.3.0，CMake 3.28.3，Python 3.12.3；FindOpenMP=4.5，`_OPENMP=201511`，实际链接 libgomp.so.1（Ubuntu libgomp1 包 14.2.0-4ubuntu2~24.04.1），Open MPI 4.1.6。探针及求解器均实际形成 Q=1/2/3/4 团队，不据可见 CPU 推断其他并行度已通过。

| 检查 | 真实命令/方法 | 结果 |
| --- | --- | --- |
| Debug 配置/构建 | `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4 -DHEAT_OPENMP_TEST_MAX_THREADS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`；`cmake --build build --parallel 2` | 成功；C++17、-g、OpenMP 内核/入口 -fopenmp、-Wall/-Wextra/-Wpedantic，无编译警告 |
| Debug 完整回归 | `cmake --build build --target check --parallel 2` | 15/15 通过；原 6 项串行、P=1..4 MPI、Q=1..4 OpenMP、受限团队各项通过 |
| Release 配置/构建/检查 | 上述命令将目录改为 `build/m2b-release`，类型改为 Release | -O3 -DNDEBUG；无编译警告，15/15 通过 |
| 实际线程/数值 | 每项都核对团队 Q；小网格、奇偶步、不能均分、Q>行数、r=1/4；逐点全场/CSV/边界/模态/连续解析核查 | Q_requested=Q_actual=1/2/3/4；全部观测 D_inf=0（判据≤1e-13），默认 E_inf=`0.0001126210917414272`<2e-4 |
| 资源限制 | `OMP_THREAD_LIMIT=2` 请求 4；测试设置 NUM_THREADS=3、DYNAMIC=TRUE | 实际 Q=2，完整数值检查通过；默认入口仍请求/实际 1；显式请求生效且动态调整已关闭 |
| 输入/错误路径 | 复用全部 30 组数值非法/不稳定输入，14 组线程错误；帮助、stdout/stderr /dev/full；Linux 子进程 RLIMIT_AS=256 MiB 请求约 800 MB 首个数组 | 按合同返回 2/0/1，无超时；分配失败在并行区前真实抛 bad_alloc，未耗尽主机内存 |
| 四位小数 | 从两种构建各自同次 XML 读取 15 项状态/耗时，并逐项与 check 输出对照 | 各 15/15 一致；check 构建依赖包含 heat_openmp，无需先单独构建 |

完整环境、真实命令、编译命令、调度探针、原始 CTest、同次 XML 耗时和 LastTest 完整数值/错误输出保存在 [m2b.log](docs/validation/m2b.log)。Debug 和 Release 检查在墙钟时间上有重叠，结果按各自构建目录归属；测试耗时不作为性能数据。M1/M2 四份日志未改写。

未运行：Q>4、ASan/UBSan（本轮未重跑）、真实主机内存耗尽、第二个缓冲分配失败单独注入、运行时线程创建失败、M3 系统化联合加密或 M4 正式性能实验。受限地址空间检查不代替这些未验证项。实施完成时用户仅确认接口和本轮授权，M2b 当时尚待验收；后续已验收通过，见末节。不补写人工审核活动。

提交边界与资料保护结果在本轮日志记录：全部 2,564 个课程文件前后路径/SHA-256 一致、全部被忽略且没有已跟踪资料；旧日志与串行/MPI 数值源码未变。逐项暂存并审阅完整暂存差异后提交推送同名功能分支，实际哈希和推送结果由最终汇报提供；不自引用尚未生成的提交哈希。

暂存审阅补充：源码及文档空白检查通过；m2b.log 保留 CMake 原始输出的 5 处行尾空格，对该日志使用单次 `core.whitespace=-blank-at-eol` 检查，不修改仓库配置。完整暂存差异仅含本轮 15 个文件，未纳入资料、构建产物或个人配置。


## M2b 验收记录同步（2026-11-10）

用户先回复“已核验”，经明确询问验收结论后回复“通过”；据此记录独立 OpenMP 提交 `17925a9` 已获用户验收。验收记录同步开始时位于 `feature/m2b-openmp`，HEAD=`17925a9`，与同名远程分支一致，工作区干净。M3–M5 尚未开始，合并与下一阶段选择仍由用户负责。

本次仅同步 AGENTS、SPEC、PLAN、STATUS、DESIGN、DECISIONS、AI_USAGE 和 README 八份文档中的当前状态及验收记录，保留历史实施记录。未修改源码、CMake、测试、课程资料或任何运行日志；未重新核对任务书、重跑构建/数值测试或开展性能实验（纯文档变更）。既有 Debug/Release 各 15/15 结果仍以 m2b.log 为据，不新增运行通过结论，也不补写用户未说明的人工检查步骤。

检查文档状态、Markdown 相对链接与代码块、空白格式及完整暂存差异，仅提交上述八份文档，按授权推送同名功能分支；实际检查与提交/推送结果由最终汇报提供。

本次检查结果：8 份文档代码块闭合，25 个相对链接有效，`git diff --check` 与 `git diff --cached --check` 通过；完整暂存差异仅含上述八份文档。无新增构建或数值测试结果。

## M3 系统正确性验证（2026-11-10，历史实施记录，现已验收）

本轮用户选择 M3 并准备 `judge/m3`。起始 HEAD、本地 main、origin/main 均为 `c1f34c1`，远程 main 经 ls-remote 核对一致；包含 M2b 实现 `17925a9` 和用户验收记录。工作区起始干净；不创建/切换分支，不合并 main。重新查看任务书第 1/3 页文本及原页图像、第十讲第 12 节和第十一讲第 11 节，未发现冲突。课程资料继续只读。

新增 `tests/check_system.py` 和四项 LABELS=M3 的 CTest，保留原 15 项基本回归；MPI 成功摘要新增实际 communicator 进程数 `P_actual`，没有修改串行/MPI/OpenMP 差分内核。矩阵、阈值推导及要求到测试的覆盖表见 DESIGN 第 9 节与 D027–D030。

环境实测：WSL2 Linux 6.18.33.2，Intel i7-14700HX，亲和性 0–27、可见 28 逻辑 CPU、约 7.6 GiB 内存；/init.scope cpu.max=`max 100000`、memory.max=`max`，非独占环境。GNU C++ 13.3.0、CMake 3.28.3、Python 3.12.3、Open MPI 4.1.6、FindOpenMP 4.5/libgomp1 14.2 包。启动器实际报告默认 14 slot；本轮仅实测 P/Q=1..4，无超额订阅。OpenMP 限制组请求4/实际2得到每次输出核验。

| 检查 | 真实命令/方法 | 结果 |
| --- | --- | --- |
| Debug 配置 | `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DHEAT_MPI_TEST_MAX_PROCS=4 -DHEAT_OPENMP_TEST_MAX_THREADS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` | 成功，C++17、-g、警告选项，OpenMP 内核/入口 -fopenmp |
| Debug 构建及完整检查 | `cmake --build build --parallel 2`；`cmake --build build --target check --parallel 2` | 成功，无编译警告；19/19 通过 |
| Release 配置、构建及检查 | 同上，目录 `build/m3-release`，类型 Release | 成功，-O3 -DNDEBUG，无编译警告；19/19 通过 |
| 系统加密 | 每构建3组×3层×10种配置，真实 CSV 逐点独立核查 | 各90条，共180条误差记录；每配置分别满足解析界、模态、一致性、误差比及全场检查 |
| 并行度与边界 | 每次核对实际 P/Q；单进程、不均匀分块、每 rank 一行、Q>行、请求4/实际2、奇偶步、MPI 超限拒绝 | 均通过；不以请求数冒充实际数，所有进程正常完成，未超时 |
| 稳定性 | r=1/4 精确二进制端点、向下/向上相邻浮点输入和2倍T | 端点与下方接受，上方及2倍T拒绝，退出2且无CSV；两种构建全部配置通过 |
| 既有错误路径 | 原串行/MPI/OpenMP CLI、帮助、输出失败、分配和通信受控失败回归 | 全部保留并通过，不视为真实硬件/进程丢失验证 |
| 耗时显示 | 19项×2套 check 与各自同次 XML Execution Time 对照 | 全部四位小数一致；日志记录完整 LastTest 输出，测试耗时不作性能数据 |

以下是实际 Debug 串行摘要；同一构建中各并行配置数值相同，Release 对应记录见 CSV，不由此要求其他平台逐位相同。

| 固定条件 | N / M | E_inf（逐次加密） | 相邻误差比 | 观测阶 |
| --- | --- | --- | --- | --- |
| T=0.1，alpha=1，r=0.1 | 20/400 → 40/1600 → 80/6400 | 1.126210917414272e-4 → 2.818135112095388e-5 → 7.046962600038009e-6 | 3.996299 / 3.999078 | 1.998664 / 1.999667 |
| T=0.2，alpha=0.25，r≈0.05 | 12/144 → 24/576 → 48/2304 | 8.451943320902933e-4 → 2.103985203901204e-4 → 5.254348922212326e-5 | 4.017112 / 4.004274 | 2.006159 / 2.001541 |
| T=0.125，alpha=1，r=0.25 | 12/72 → 24/288 → 48/1152 | 2.400264738606481e-3 → 5.981926582010466e-4 → 1.494309814035338e-4 | 4.012528 / 4.003137 | 2.004511 / 2.001131 |

全部加密记录观测 D_inf=0（判据≤1e-13），离散模态最大差约 7.267e-14（判据≤1e-13）。这表明所选矩阵的离散实现一致且呈联合二阶趋势，不是时间二阶、任意参数精度或性能保证。原始环境、命令、编译选项、CTest、同次 LastTest 全输出及代码哈希见 [m3.log](docs/validation/m3.log)；全部逐配置 E/D/阈值/比值/阶数见 [m3-errors.csv](docs/validation/m3-errors.csv)。CSV 由日志的 RESULT JSON 行提取并附 build 字段（90条/构建），不由解析公式预测填入。

未运行：P/Q>4、多机通信、真实主机内存耗尽/硬件或进程丢失、OpenMP 线程创建失败、额外 ASan/UBSan；未运行缩减资源后的额外数值矩阵。M4 正式计时、资源绑定与性能实验未开展。实施结束时无已知数值验证阻塞，M3 当时待用户验收；现已获用户验收，见末节。提交与同名功能分支推送结果以实际 Git 输出和最终汇报为准。

M3 收尾检查：2,564 个课程文件前后路径/SHA-256 一致、全部忽略且未跟踪；五份历史验证日志无改动。八份项目文档代码块闭合、30 个相对链接有效；四项系统 CTest 的命令、资源、标签和超时配置核对通过。源码/文档空白检查通过；日志原样保留 CMake 行尾空格，使用本次命令的 `core.whitespace=-blank-at-eol` 检查，不修改 Git 配置。明确逐项暂存并核对本轮12个文件，排除课程资料、构建产物及无关文件；提交推送仅针对 judge/m3。

## M3 用户验收记录同步（2026-11-10）

用户明确回复“通过”，据此记录 M3 系统验证提交 `cfffe71` 已获验收。同步开始位于 `judge/m3`，HEAD 与同名远程分支均为 `cfffe71`，工作区干净；本地 main/origin/main 仍为 `c1f34c1`。用户负责合并，M4–M5 未开始。

本次仅同步 AGENTS、SPEC、PLAN、STATUS、DESIGN、DECISIONS、AI_USAGE、README 八份文档的验收状态，保留历史实施事实及全部未验证项。不修改代码、构建配置、测试、课程资料、运行日志或误差数据；未重跑构建/数值测试（纯文档变更），既有 Debug/Release 各19/19仍以 m3.log 为据，不新增测试通过结论。文档链接/代码块、空白及完整暂存范围检查后提交推送同名功能分支，不合并 main，不进入 M4。

本次检查结果：八份文档代码块闭合、30个相对链接有效，`git diff --check` 和 `git diff --cached --check` 通过；完整暂存差异仅含上述八份文档。无新增构建或数值测试结果。


## M4 实施开始（2026-11-10）

用户已选择 M4 并授权在当前功能分支实现、检查、记录、提交推送。起始 `Evaluation`=`main`=`origin/main`=`origin/judge/m3`=`69fb1d0`，包含 `cfffe71` 与验收记录，工作区干净。重新读取任务书第 1/3 页文字及原页、OpenMP 性能评测讲义、MPI 第十一讲第 12–14 节及参考程序计时/统计方法，未发现范围冲突。课程资料只读、前置 2,564 文件 SHA-256 清单位于 `/tmp/heat-m4-sources-before.json`。

计时保留原数值算法，新增 loop_seconds 与 --summary-only，冻结 Release 配置、CPU 0/2/4/6 绑定、23 配置矩阵和五次重复方法，详见 [性能实验协议](docs/performance/README.md)。OpenMP 团队进入/退出计入，MPI 用 rank 最大值；初始化、验证和输出不计入。正式采样尚未运行；Debug/Release 回归正在执行，不能据此预写通过。额外手动规模试跑仅用于核对稳定性与可执行性，不作为正式性能样本。


### 2026-11-11 接续事实

工作区与 Evaluation 分支保持，原 Debug CTest 20/20 已通过，包括新增 heat_timing；同次 XML、LastTest 与原始控制台输出已归档 m4.log。最初归档器查找 LastTest.log 而 Dashboard 实际使用 LastTest_<TAG>.log，导致归档中断；原始测试成功且完整证据保留，已补录，不伪称测试失败或重跑。恢复后 /tmp 辅助脚本及原资料哈希清单消失，无法完整核对最初开工到最终收尾的资料哈希；新 2,564 文件清单存于忽略的 build/m4-sources-resume.json，仅用于恢复后工作的一致性比较。

Release 完整回归继续顺序运行。新增计时脚本已加强超时后杀死整个进程组的清理，与统计脚本最终检查一并补录；该测试控制变更后 Debug 将单独重跑 heat_timing。统计合成单元检查通过，原始数字明确标为合成测试，不能作为性能测量。正式采样仍未开始。


### M4 计时实现验证完成，正式采样前冻结（2026-11-11）

- Debug/Release 真实完整回归各 20/20 通过（原 19 项 + heat_timing），源码构建无编译警告；`cmake --build build/m4-{debug,release} --target check --parallel 2`，原始控制台、XML 数值与同次完整 LastTest 输出在 m4.log；四位小数逐项与同次 XML 核对一致。
- 最终计时回归加入进程组超时清理后，Debug 单独 `ctest --test-dir build/m4-debug -V -R '^heat_timing$'` 1/1 再通过；Release 全套已使用该最终脚本。额外 CTest PROCESSORS 元数据只影响并行调度，本轮顺序执行。
- `python3 tests/check_statistics.py` 通过：合成测试检验中位数/范围、独立串行基线、工作量归一化与八类损坏记录拒绝；不作为性能数据。
- 恢复后 2,564 课程文件哈希一致；全部资料被忽略、未跟踪；历史验证日志无差异。源码/文档格式及相对链接检查通过。m4.log 原始 CMake 输出保留行末空格，只对日志在检查时忽略该类空白，不改写原始证据。

接下来在当前分支提交冻结计时实现、脚本、协议及上述证据；正式性能样本尚未运行，后续另提交原始测量与分析。M4 尚待完成和用户验收，M5 未进入。
