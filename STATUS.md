# 项目状态

当前状态（2026-11-13）：M4交付 `Evaluation@30c4a43` 已获用户验收；M5材料已在用户准备的M5分支完成，入口见 [最终材料](report/README.md)，待用户验收。以下原M4“待验收”及旧分支位置均保留为历史语境。

本轮当前任务（2026-11-13）：PPT v3已交审；按用户要求安装PaperBanana并调研项目制图。Skill、独立环境及检索数据就绪，CLI/导入/离线检查通过；三份输入样稿和调研已整理，未调用模型出图。

更新日期：2026-11-13（Asia/Shanghai）。

## 当前阶段

M0–M4均已获用户验收；M4交付为Evaluation@30c4a43。当前分支M5起于30c4a43，用户确认格式及AGENTS修改随阶段提交，并确认PPT自由组合设计；本地/远程main保持30c4a43，不操作main。

M5已生成报告Markdown/8页PDF，12页PPTX/PDF和全部备注、逐页讲稿、答辩问答及核查记录。源SVG最终12/12、0错误0警告；PPT包postflight通过，12页备注、1个原生公式、386个可编辑文本/图元。LibreOffice实际打开最终PPTX并转换12页PDF，完成渲染检查。表格/主图10点及10区间/链接/图表字节副本/资料保护通过；既有三批统计与九组图校验通过。详见report/REVIEW.md和material_checks.json。

M5待用户验收；姓名学号、真实口头演练及Microsoft PowerPoint本机人工显示/编辑待本人核实。讲稿预算280秒，假设语速估算258.9秒，不冒充实讲。本阶段未改求解器、未运行构建/数值回归、未增加性能采样。以下为各阶段历史记录。

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

真实配置、构建、CTest 和数值输出保存在 [validation/m1.log](results/validation/m1.log)。CTest 用时仅为检查日志，不作为性能测量。未运行 MPI 检查、正式性能实验或 M3 系统验证。分配失败有异常处理，但未故意耗尽机器内存；可表示的输入规模不保证实际可分配。

## 当前阻塞与下一步（M5）

无已知材料生成阻塞。课程任务书两页未指定的提交平台、命名和期限仍需用户自行核对其他通知；个人信息暂留待填写，真实人工演练待验证。完成暂存边界检查并提交推送同名origin/M5后，交用户审核材料和决定是否验收；不合并或推送main。

## M1 接口确认记录同步

用户于 2026-11-10 回复“采用建议：命名参数、20/400/0.1/1、全场 CSV”。本次仅同步 SPEC、STATUS、DECISIONS 和 AI_USAGE 的确认状态；未修改代码或数值参数，未重跑构建/数值测试（纯文档变更），执行差异及暂存检查。串行实现提交为 `d568e45`，已推送 `origin/feature/m1-Serial`；接口确认不等于 M1 整体验收。

## M1 验收与耗时显示补充

用户明确回复“暂无其他问题，审查通过”，随后指出精确小数位数尚未修改。本轮补齐 `cmake --build build --target check --parallel 2` 入口：执行 CTest 并从 XML 测量值按秒显示四位小数，保留原始输出与失败状态。未修改求解器或旧日志。

实际执行 `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug`、`cmake --build build --target check --parallel 2` 成功，6/6 通过；六项显示值与 XML `.4f` 结果逐项一致。另在 `/tmp/` 临时 CMake 项目构造 `cmake -E false` 测试，脚本显示真实失败诊断并返回 CTest 退出码 8。补充真实日志见 [m1-precision.log](results/validation/m1-precision.log)。本轮未重新运行 ASan/UBSan（求解器及数值测试未变）；未开展性能实验。文档同步验收事实，下一阶段仍由用户选择。

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

正式环境、命令、编译选项与原始输出见 [m2.log](results/validation/m2.log)；首轮失败见 [m2-initial.log](results/validation/m2-initial.log)。`check` 的原始终端文本与逐项输出来自同一次 CTest XML，显示耗时仍保留四位小数。

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

完整环境、真实命令、编译命令、调度探针、原始 CTest、同次 XML 耗时和 LastTest 完整数值/错误输出保存在 [m2b.log](results/validation/m2b.log)。Debug 和 Release 检查在墙钟时间上有重叠，结果按各自构建目录归属；测试耗时不作为性能数据。M1/M2 四份日志未改写。

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

全部加密记录观测 D_inf=0（判据≤1e-13），离散模态最大差约 7.267e-14（判据≤1e-13）。这表明所选矩阵的离散实现一致且呈联合二阶趋势，不是时间二阶、任意参数精度或性能保证。原始环境、命令、编译选项、CTest、同次 LastTest 全输出及代码哈希见 [m3.log](results/validation/m3.log)；全部逐配置 E/D/阈值/比值/阶数见 [m3-errors.csv](results/validation/m3-errors.csv)。CSV 由日志的 RESULT JSON 行提取并附 build 字段（90条/构建），不由解析公式预测填入。

未运行：P/Q>4、多机通信、真实主机内存耗尽/硬件或进程丢失、OpenMP 线程创建失败、额外 ASan/UBSan；未运行缩减资源后的额外数值矩阵。M4 正式计时、资源绑定与性能实验未开展。实施结束时无已知数值验证阻塞，M3 当时待用户验收；现已获用户验收，见末节。提交与同名功能分支推送结果以实际 Git 输出和最终汇报为准。

M3 收尾检查：2,564 个课程文件前后路径/SHA-256 一致、全部忽略且未跟踪；五份历史验证日志无改动。八份项目文档代码块闭合、30 个相对链接有效；四项系统 CTest 的命令、资源、标签和超时配置核对通过。源码/文档空白检查通过；日志原样保留 CMake 行尾空格，使用本次命令的 `core.whitespace=-blank-at-eol` 检查，不修改 Git 配置。明确逐项暂存并核对本轮12个文件，排除课程资料、构建产物及无关文件；提交推送仅针对 judge/m3。

## M3 用户验收记录同步（2026-11-10）

用户明确回复“通过”，据此记录 M3 系统验证提交 `cfffe71` 已获验收。同步开始位于 `judge/m3`，HEAD 与同名远程分支均为 `cfffe71`，工作区干净；本地 main/origin/main 仍为 `c1f34c1`。用户负责合并，M4–M5 未开始。

本次仅同步 AGENTS、SPEC、PLAN、STATUS、DESIGN、DECISIONS、AI_USAGE、README 八份文档的验收状态，保留历史实施事实及全部未验证项。不修改代码、构建配置、测试、课程资料、运行日志或误差数据；未重跑构建/数值测试（纯文档变更），既有 Debug/Release 各19/19仍以 m3.log 为据，不新增测试通过结论。文档链接/代码块、空白及完整暂存范围检查后提交推送同名功能分支，不合并 main，不进入 M4。

本次检查结果：八份文档代码块闭合、30个相对链接有效，`git diff --check` 和 `git diff --cached --check` 通过；完整暂存差异仅含上述八份文档。无新增构建或数值测试结果。


## M4 实施开始（2026-11-10）

用户已选择 M4 并授权在当前功能分支实现、检查、记录、提交推送。起始 `Evaluation`=`main`=`origin/main`=`origin/judge/m3`=`69fb1d0`，包含 `cfffe71` 与验收记录，工作区干净。重新读取任务书第 1/3 页文字及原页、OpenMP 性能评测讲义、MPI 第十一讲第 12–14 节及参考程序计时/统计方法，未发现范围冲突。课程资料只读、前置 2,564 文件 SHA-256 清单位于 `/tmp/heat-m4-sources-before.json`。

计时保留原数值算法，新增 loop_seconds 与 --summary-only，冻结 Release 配置、CPU 0/2/4/6 绑定、23 配置矩阵和五次重复方法，详见 [性能实验协议](results/performance/baseline/README.md)。OpenMP 团队进入/退出计入，MPI 用 rank 最大值；初始化、验证和输出不计入。正式采样尚未运行；Debug/Release 回归正在执行，不能据此预写通过。额外手动规模试跑仅用于核对稳定性与可执行性，不作为正式性能样本。


### 2026-11-11 接续事实

工作区与 Evaluation 分支保持，原 Debug CTest 20/20 已通过，包括新增 heat_timing；同次 XML、LastTest 与原始控制台输出已归档 m4.log。最初归档器查找 LastTest.log 而 Dashboard 实际使用 LastTest_<TAG>.log，导致归档中断；原始测试成功且完整证据保留，已补录，不伪称测试失败或重跑。恢复后 /tmp 辅助脚本及原资料哈希清单消失，无法完整核对最初开工到最终收尾的资料哈希；新 2,564 文件清单存于忽略的 build/m4-sources-resume.json，仅用于恢复后工作的一致性比较。

Release 完整回归继续顺序运行。新增计时脚本已加强超时后杀死整个进程组的清理，与统计脚本最终检查一并补录；该测试控制变更后 Debug 将单独重跑 heat_timing。统计合成单元检查通过，原始数字明确标为合成测试，不能作为性能测量。正式采样仍未开始。


### M4 计时实现验证完成，正式采样前冻结（2026-11-11）

- Debug/Release 真实完整回归各 20/20 通过（原 19 项 + heat_timing），源码构建无编译警告；`cmake --build build/m4-{debug,release} --target check --parallel 2`，原始控制台、XML 数值与同次完整 LastTest 输出在 m4.log；四位小数逐项与同次 XML 核对一致。
- 最终计时回归加入进程组超时清理后，Debug 单独 `ctest --test-dir build/m4-debug -V -R '^heat_timing$'` 1/1 再通过；Release 全套已使用该最终脚本。额外 CTest PROCESSORS 元数据只影响并行调度，本轮顺序执行。
- `python3 tests/check_statistics.py` 通过：合成测试检验中位数/范围、独立串行基线、工作量归一化与八类损坏记录拒绝；不作为性能数据。
- 恢复后 2,564 课程文件哈希一致；全部资料被忽略、未跟踪；历史验证日志无差异。源码/文档格式及相对链接检查通过。m4.log 原始 CMake 输出保留行末空格，只对日志在检查时忽略该类空白，不改写原始证据。

接下来在当前分支提交冻结计时实现、脚本、协议及上述证据；正式性能样本尚未运行，后续另提交原始测量与分析。M4 尚待完成和用户验收，M5 未进入。


## M4 实验完成（2026-11-11，待用户验收）

冻结计时/脚本/协议提交 `75cdaad`，提交后干净工作区开始采样；正式样本全部引用该确切代码版本，源码/协议/二进制哈希前后不变。未修改求解数值算法或更改冻结矩阵以追求加速。真实命令：

```bash
python3 scripts/benchmark.py --build build/m4-release --output results/performance/baseline/run-01
python3 scripts/analyze_performance.py results/performance/baseline/run-01 --output results/performance/baseline/derived
python3 scripts/analyze_performance.py results/performance/baseline/run-01 --output build/m4-recomputed --no-plots
cmp results/performance/baseline/derived/summary.csv build/m4-recomputed/summary.csv
```

- 23 配置、23 次全场验证预热、115 正式样本全部完成，无失败/重试/剔除。T=0.01、alpha=1；CPU 0/2/4/6，P/Q 请求与实际均为协议指定 1/2/4；MPI 逐样本绑定信息和 OpenMP Q=2/4 预热 affinity 诊断已保存。Q=1 运行时不打印 affinity，采样后独立 /proc 探针确认 CPU 0/单 task，记录 binding-probe.json，探针不纳入统计。
- 完整场验证观测 D_inf 全为 0，E_inf 在 8.314784308849354e-7 至 7.4838110496466825e-6，离散模态最大差 2.3381296898605797e-13；所有样本参数/稳定性/实际并行度和预热误差一致性检查通过。
- N=128/M=1024：MPI P=4 主基线 S=1.282、E=32.05%；OpenMP Q=4 S=0.681、E=17.03%。N=384/M=9216：MPI P=4 S=1.521、E=38.04%；OpenMP Q=4 S=0.976、E=24.39%。OpenMP 未在这些多线程配置取得主基线加速，不筛选掉慢样本。
- 扩大累计工作量 W/W1=1/1.991004/4.007846，W/p 取整偏差 −0.4498% 至 +0.1961%。p=4 时 MPI 自身基础网格吞吐增长 2.2053 倍（归一化 55.13%），OpenMP 0.8037 倍（20.09%），与同规模独立串行加速比明确区分。每 worker 最小/最大更新量保存在 CSV。
- 重新从原始 JSONL 计算的 summary.csv 逐字节一致；SVG/PNG 已目视检查。图中范围条为真实 min/max，不是置信区间；Amdahl 有效比例和 Gustafson 适用前提/未测 sigma 如实说明。统计合成单元检查仅验证方法，不充当性能数据。

完整证据与分析：[性能协议](results/performance/baseline/README.md)、[结果分析](results/RESULTS.md)、[原始样本](results/performance/baseline/run-01/samples.jsonl)、[环境](results/performance/baseline/run-01/environment.log)、[代码与编译配置](results/performance/baseline/run-01/metadata.json)、[统计表](results/performance/baseline/derived/summary.csv)。Debug/Release 各 20/20、最终 Debug heat_timing 1/1、统计单元检查原始证据为 results/validation/m4.log。

局限：非独占 WSL/虚拟拓扑，无宿主 P/E 核映射或频率控制证据；只测 P/Q≤4、单机、当前绑定与已验收调度，未运行多机、更大并行度、其他调度、端到端计时或分项瓶颈剖析，本轮未额外运行 Sanitizer。不能从样本范围给出未计算的统计显著性。最初 /tmp 课程哈希基线丢失，无法声称全程前后哈希比较；仅恢复后 2,564 文件一致，资料未跟踪，历史证据未修改。

后续只做提交边界/文档/资料保护核查和同名功能分支推送；M4 验收由用户决定。M5 未进入，不自行合并或推送 main。


M4 最终时钟审计补充（2026-11-11）：原始 UTC 时戳与 perf_counter 耗时存在两处不一致，其中一次 UTC 起点回退，全部样本/时戳原样保留。已核对本机 libmpi/libgomp/libstdc++ 实际二进制，三种求解器时钟正常路径均为 CLOCK_MONOTONIC；未用 UTC 计算推进耗时。原始反汇编/库哈希与异常记录在 results/performance/baseline/run-01/clock-audit.log，完整解释见 RESULTS 的时钟审计。顺序执行来自冻结脚本的阻塞等待结构，未保存单调起点时间线，不声称用 UTC 独立证明了无重叠；未推断具体校时原因或删除样本。最终核查以这些实际限制为准。


M4 收尾检查结果：源代码/协议/脚本及 Release 三个二进制与正式采样元数据 SHA-256 均一致；五轮种子顺序、23 个验证记录/138 次调用（115 正式样本）及 RESULTS 表格逐行与 CSV 核对通过。67 个本地文档链接和代码块闭合检查通过；16 个性能文件哈希清单复核通过。恢复后 2,564 个课程文件路径/内容未变，全部忽略且未跟踪，七份历史证据与起始 69fb1d0 逐字节相同。检查源码/实验提交范围后按授权推送同名 Evaluation；实际提交哈希及推送结果以 Git 输出和最终汇报为准。


提交格式检查补充：Matplotlib SVG、Python csv.writer 的 CRLF 以及原始系统/反汇编日志带有生成器空白；保留原始内容。手写文档/JSON/JSONL 单独严格空白检查通过，全暂存内容以本次命令级 core.whitespace=-blank-at-eol,cr-at-eol 检查通过，不修改仓库配置或原始数据。


## M4 交付状态核实（2026-11-11）

冻结实现/协议提交 `75cdaad`、原始性能证据/图表/分析提交 `d794a69` 均已推送 `origin/Evaluation`，远程引用已用 git ls-remote 核实。推送后工作区干净；本地 main 与远程 main 仍为 `69fb1d0`，课程资料及七份历史证据无差异。本节仅同步交付事实，不表示用户已验收 M4；当前下一步为用户审核，M5 未进入。

本次交付状态同步仅修改 STATUS/AI_USAGE，文档格式/暂存边界检查通过，未重复运行求解器构建或测试；源码/协议/原始样本与既有回归、哈希及统计证据保持不变。该文档提交继续推送同名功能分支，实际最新哈希以 Git 输出为准。


## M4 补充诊断范围与计划更新（2026-11-11，纯文档）

用户选择“诊断与对照实验、仅当前 WSL2、分阶段深入”，随后要求在现有文档中明确范围并更新计划；新增独立计划文档的建议已撤回。当前只修改既有 SPEC、PLAN、STATUS、README、DESIGN、DECISIONS、AI_USAGE 七份文件，未新增文件/目录，未修改正式实现或原 M4 证据。PLAN 记录阶段、触发与验收，DESIGN 第 11 节记录拟采用的测量/变体方法，其余文档同步边界与状态。

原 `75cdaad` 实现、`d794a69` 实验结果和 `1afc65f` 交付事实保留；20/20 回归、23 配置/115 正式样本仍为原 M4 证据，不是本次运行结果。此前规划中的只读编译检查显示三个内点循环均生成 16 字节向量化代码，原样本有早期偏慢/波动；这些仅为诊断线索，尚无新的受控对照或瓶颈归因。本次未运行构建、数值回归或新性能实验（纯文档变更），不新增运行 PASS。

后续允许隔离诊断与受控变体，正式程序及 CLI/API 保持，原 M4 数据/图/协议/分析/哈希清单不改；优化进入正式实现另行确认。不新增里程碑或计划文档，不预建诊断证据目录，不安装工具/调整系统权限，不进入 M5。文档核查和提交推送结果按本节收尾及实际 Git 输出记录。


本次文档收尾检查：`git diff --check` 通过；Python 检查七份文档代码块闭合、50 个相对文件链接有效，改动仅限上述七份既有文件且无新增未跟踪文件。`cd docs/performance && sha256sum -c SHA256SUMS`16 项全部通过；原源码/CMake/测试/脚本、AGENTS、性能目录及历史验证日志相对起始 1afc65f 无差异。2,564 份课程文件前后路径/内容合并 SHA-256 一致，全部被忽略且未跟踪。构建/数值测试/新性能实验未运行（纯文档）。审阅完整差异后逐项暂存、提交推送 Evaluation，实际哈希及远程状态以 Git 输出为准；本次任务到此结束，诊断实现尚未开始。


## M4 补充诊断实施启动记录（2026-11-11，历史过程）

用户明确要求实施完整诊断计划，并选择原始证据随 Git 保存在既有 docs/validation。起始 Evaluation/origin/Evaluation=7c9ea09，工作区干净；main/origin/main=69fb1d0。已新增隔离诊断公共头、三入口/公共行内核、采样/统计及检查，原 src 求解器和 docs/performance 未改。CMake 新选项默认 OFF；不新增 Markdown 文档或目录，不安装工具，不调整系统权限。

独立 Release 诊断初检 heat_diagnostics 已 1/1 通过，覆盖各变体全场、模态/解析参考、奇偶步、实际资源/行归属和非法组合；最终版又加强统计损坏输入检查，Debug/Release 全套正在独立构建目录并行执行。两套检查均结束后才开始性能测量；检查时间不作为性能数据。当前尚无正式新性能结论。

本轮读取了相关 MPI 计时及 OpenMP 屏障讲义；原任务书 PDF 无完整阅读工具，临时标准库/字体解析仅成功读取部分文本，未完整重读原页，不声称已重新完整核对。沿用既有任务书核对记录和未变的模型合同，无教师要求变更或已知冲突。原资料 2,564 文件前置哈希存于忽略的 build/m4-diagnostic-sources-before.json，后续核对内容一致性。


### 诊断代码验证与冻结前检查（2026-11-11）

Debug/Release 完整回归各 21/21 通过（保留原 20 项，新增 heat_diagnostics）；两套检查在独立构建目录重叠，仅作正确性证据，正式采样不与检查重叠。原始配置/构建/check 命令、同次完整 LastTest 和 XML/四位小数逐项核对分别见 results/validation/m4-diagnostic-debug-checks.log、m4-diagnostic-release-checks.log。无编译警告。默认关闭诊断选项的配置/发现检查仍为原 20 项、无诊断目标；该目录未实际执行测试，见 m4-diagnostic-default-checks.log。

新增真实检查覆盖所有诊断变体、profile/非 profile 全场、连续/离散解析参考、严格零边界、奇偶步、不均匀分块、每 rank 一行、Q>内部行、实际 P/Q、受限请求4/实际2及非法变体/参数。统计合成检查验证效果/无效果/变慢、非法耗时、缺样本/缺配对/重复配对及独立分组；额外合成端到端联调验证原始记录读取、warmup/参数/版本/单调时间线及 summary/worker CSV 写出，工件仅在忽略 build，不进入性能证据。

当时下一步为提交冻结诊断代码与配置，再运行 scripts/diagnose.py --build build/m4-diagnostic-release --run-id 01；该时点正式新测量仍未开始。原求解器与原性能目录未改，旧 M4 哈希清单通过。


## M4 补充诊断完成（2026-11-11，待用户验收）

诊断实现/测试/采样配置已先提交冻结为 `1e2fb5f`；随后真实执行：

```bash
python3 scripts/diagnose.py --build build/m4-diagnostic-release --run-id 01
python3 scripts/analyze_diagnostics.py results/performance/diagnostic-01/m4-diagnostic-01
python3 scripts/analyze_diagnostics.py results/performance/diagnostic-01/m4-diagnostic-01 --output build/m4-diagnostic-recomputed --no-plots
```

实际 2775 次调用（215 次完整场验证预热、2560 次正式计时），无失败、重试、删样本；原23配置复测230样本。源码/二进制哈希前后未变，每次参数、实际P/Q、绑定、稳定性及完整场参考核验通过；单调起止时间线无重叠。原始attempt和sample分开保存，统计只取正式sample。

主要证据支持MPI计算执行/编译上下文及OpenMP行划分的影响：核心MPI1公共行内核A/B约1.583，N384/Q4连续行分配约2.763，均为未插桩replica配对，不能冒充正式求解器优化后加速比。空邻居对照未满足影响判据，循环行划分下单独改变同步未得到同等收益，PASSIVE等待变慢。所选8个单CPU无可重复差异，CPU分组按触发规则未运行。部分旧吞吐下降幅度未稳定复现；环境波动、剩余差距及具体缓存/硬件机制保留为未确定。详细校准、区间、49组合粒度验证及逐异常结论见 [DESIGN第11节](docs/DESIGN.md)。

原始数据、环境、统计、图与审计见 [清单](results/performance/diagnostic-01/m4-diagnostic-01.json)、[样本](results/performance/diagnostic-01/m4-diagnostic-01.jsonl)、[统计](results/performance/diagnostic-01/m4-diagnostic-01.csv)、[审计](results/performance/diagnostic-01/m4-diagnostic-01-audit.log)、[哈希](results/performance/diagnostic-01/m4-diagnostic-01.sha256)。原20项加诊断各21/21的构建/check与完整输出已归档；默认OFF仅配置/发现检查，未在该目录执行回归。CSV在独立输出前缀重算逐字节一致；重复运行编号拒绝覆盖，原文件哈希未变。

正式求解器与原docs/performance全部内容未改，旧16项哈希通过；本轮前后2,564课程文件路径/内容哈希一致，全部忽略且未跟踪。没有安装工具、改变系统权限、增加Markdown文档或新受版本控制目录，未进入M5；优化采用和里程碑验收仍由用户决定。仅提交推送同名origin/Evaluation，main保持69fb1d0；实际结果提交和远程状态以Git输出为准。

本轮收尾：八份既有协议/项目文档代码块闭合，71个相对链接有效；DESIGN结果表与原始统计派生值一致，手写差异严格空白检查通过。12个诊断工件的SHA-256清单逐项通过，含原始样本、环境/控制台、统计、图、审计及三份检查日志；审计辅助源码保存在审计日志内，便于独立核查。没有修改冻结后的诊断源码或补做无关性能实验。


## M4 扩大网格数量与并行度实施开始（2026-11-11）

用户授权按已确认计划实施，起始Evaluation/origin/Evaluation=9983e4f，main/origin/main=69fb1d0，工作区干净。仅新增三个脚本，原源码、CMake、历史测试/脚本和全部已有证据保持。矩阵N=384/512/768/1024、M=N²/16、T=0.01、alpha=1；P/Q=1/2/4/8/16，仅原三程序，44配置、44预热+440正式样本，计划见PLAN及DESIGN第12节。

16逻辑CPU启动及实际绑定已在规划期小输入探针验证，不作为正式性能数据。新增检查初次发现MPI rank独立进程组的超时清理问题，已清理测试进程并修正新增采样器，后续检查通过；最终Debug/Release原21项及新增8/16/统计/流式检查正在执行。完整回归结束并提交冻结前不采样。代码和原资料保护基线已保存，M5未进入，M4仍待用户验收。


扩大规模实现的最终检查完成：Debug/Release原21项均通过，另执行check_large.py通过8/16资源、奇偶/并行边界、请求16实际8、流式字段损坏拒绝、同轮中位数之比及bootstrap/缺记录检查。普通子进程与独立MPI rank超时清理均通过；初次开发失败和后续原始输出单独归档，不混入性能样本。两套配置/构建/check、XML/四位小数和完整LastTest在m4-diagnostic-large-{debug,release}-checks.log，无编译警告。两套正确性作业曾重叠，正式采样等待全部结束。旧源码/CMake/脚本及全部历史证据与9983e4f逐字节相同，2,564课程文件前后路径/内容哈希一致。接下来先提交冻结，再运行02；当前尚无扩大矩阵的正式性能结论。


### 单rank绑定报告修正与失败留证（2026-11-11）

冻结e715560后，运行02在MPI P=1预热的绑定报告核查处停止：只有1条通过的串行预热、1条被拒绝的MPI attempt，正式样本为0。原始清单/环境/JSONL/控制台及失败调用完整CSV和stderr原样保留，不覆盖、不纳入后续统计。独立探针表明实际affinity=[0]，但本机Open MPI 4.1.6在--cpu-list 0时报告not bound (or bound to all available processors)。先前8/16检查未覆盖这一单rank报告行为。

修正仅为P=1使用候选列表0,2，仍只启动1个rank，明确报告rank0绑定CPU0；实际CPU集合、矩阵、计时和其余绑定不变。新增检查扩到全部P/Q=1/2/4/8/16；检查后另提交冻结，再以新运行编号02-r1从头采样，不重用02的预热或数据。本轮新增脚本的该报告兼容修正不改变正式程序，原Debug/Release21项证据保持，新增检查在两构建重跑。

绑定报告兼容修正后，Debug/Release新增检查均再次通过，包含全部P/Q=1/2/4/8/16与两类超时清理；新日志为m4-diagnostic-large-{debug,release}-binding-checks.log，原21项检查日志原样保留。失败02的完整CSV与原attempt哈希一致，正式样本确为0。接下来提交修正与失败留证，再从新编号02-r1开始。


## M4 扩大网格数量与P/Q完成（2026-11-11，待用户验收）

最终冻结版本 `646f7c460d5a2b409c1063face7e7ed7655db5fc`。真实完成命令：

```bash
python3 -u scripts/benchmark_large.py --build build/m4-large-release --run-id 02-r1
python3 scripts/analyze_large.py results/performance/large-02-r1/m4-diagnostic-02-r1
python3 scripts/analyze_large.py results/performance/large-02-r1/m4-diagnostic-02-r1 --output build/m4-large-recomputed --no-plots
```

完成44配置、44次完整场验证预热、440次正式样本，没有失败、重试或删样本；初次02的绑定报告检查拒绝另存，不纳入完成运行。源码/二进制前后哈希一致，UTC只追溯，单调调用区间无重叠；实际P/Q、每次绑定、稳定性、完整场离散/连续参考及独立串行一致性通过。16组的实际集合包含14个WSL可见core上的16逻辑CPU，原样标注，不推断宿主物理映射。

全部数值、区间及结论见[DESIGN第12节](docs/DESIGN.md)，证据见[原始记录](results/performance/large-02-r1/m4-diagnostic-02-r1.jsonl)、[清单](results/performance/large-02-r1/m4-diagnostic-02-r1.json)、[统计](results/performance/large-02-r1/m4-diagnostic-02-r1.csv)、[审计](results/performance/large-02-r1/m4-diagnostic-02-r1-audit.log)与[哈希清单](results/performance/large-02-r1/m4-diagnostic-02-r1.sha256)。CSV及逐轮CSV独立重算逐字节一致，三组SVG/PNG已核对；全部慢样本保留，没有把单点或区间当唯一根因证据。

Debug/Release原21项通过，无编译警告；绑定报告兼容修正后，两构建的新增全部资源/字段/统计/超时检查再次通过，原21日志保持，不声称重跑。最初开发超时清理失败和初次02的原始证据均留存。正式源码、CMake、既有脚本/测试、原性能目录及运行01全部证据与9983e4f逐字节相同，课程资料本轮前后2,564文件路径/内容一致且全部忽略未跟踪。没有新增Markdown文档或受版本控制目录，没有安装工具或调整系统权限。

本轮仅M4，待用户验收。结果与现有文档提交推送同名origin/Evaluation；不切换分支、不合并或推送main，main仍69fb1d0。实际结果提交/远程引用以Git输出及最终汇报为准。


扩大实验时钟/趋势审计补充：34/44配置的前3/末3中位数>1.1，所有样本保留。另有11处相邻UTC起点回退、146次UTC/单调区间差绝对值>1s；UTC结束含输出哈希后处理，因此后者不是精确校时次数。统计和顺序核查仅使用单调时钟；当前运行时哈希与原CLOCK_MONOTONIC正常路径反汇编一致。完整原始记录与新时钟审计保留，未独立校准外部物理时间、未确定宿主/虚拟机机制，不把结果作为已排除该影响的裸机结论。详见DESIGN第12节及m4-diagnostic-02-r1-clock-audit.log。


扩大实验收尾检查：八份既有协议/项目文档的94个相对链接及代码块通过，手写差异严格空白检查通过；19个完成运行/检查工件的SHA-256逐项通过。统计表来自已验证原始记录，三组图已目视核对；新增文件仅三份脚本与既有validation目录中的前缀化证据，没有新Markdown文档或受版本控制目录。提交前逐项暂存并核对本任务范围，实际提交及同名分支推送结果以Git输出为准。

## 本轮结果目录整理（2026-11-11）

起点Evaluation@320437c，工作区干净，main/origin/main=69fb1d0。用户授权统一迁移结果：67个原工件归入results；原始数据、日志、旧图及旧校验清单内容保留，两份原说明文档另存.original.txt。详细M4实测移至results/RESULTS.md，DESIGN保留方法。原日志中的旧路径/版本属于历史事实，迁移映射解释新位置。旧阶段“不改性能目录、不新增目录”限制已由本轮授权替代。

本轮未重新采样、未运行数值构建/回归，也不声称新增性能结果；正在核查迁移、统计复算与路径适配，之后更新新版图。M4仍待用户验收，M5未进入。

迁移验证已完成：`python3 scripts/check_results.py --course-baseline build/results-reorganization/course-before.json`通过。67个工件及两份快照、4份旧清单、4个历史提交的123项源码哈希均一致；三个完成批次5份CSV逐字节一致；原统计及诊断/扩大合成检查通过。文件链接及围栏通过，2,564份课程资料路径/内容未变且未跟踪。测试过程中校验入口曾误引用未独立提取的诊断合成函数，已提取原检查块并重跑通过；未执行其真实求解器检查。原求解器/CMake未修改。审计见results/validation/results-migration-checks.log。

## 新版全套对比图交付（2026-11-11）

目录迁移提交为7ff6adf。新增scripts/plot_results.py，在results/figures/large-02-r1-viz-01生成9组SVG/PNG、统计CSV副本、生成清单及SHA256SUMS；输入仅为646f7c4冻结的02-r1，44配置/440正式样本，无新测量。RESULTS统一入口整合三批完成实验与停止02，直接展示主要新图并解释全部9组；DESIGN保留方法，README明确docs/results/report分工。report仍为空，M5未开始。

实际执行 `python3 scripts/plot_results.py --output results/figures/large-02-r1-viz-01`；`python3 scripts/check_results.py --course-baseline build/results-reorganization/course-before.json` 全部通过。逐字节核对原67工件与起点Git库存、2快照、4旧清单、4版本123项采样源码哈希；从三批完成原始数据重算5份CSV完全一致，原统计及诊断/扩大合成检查通过。9组SVG/PNG及其脚本/输入/统计哈希、全44配置覆盖、原始样本SVG实际440个点、三个入口拒绝复用目录均通过。Python语法编译通过；暂存差异按允许CRLF规则检查通过（CSV副本保留原始CRLF字节，新SVG已去除生成器尾空格）。AI逐组目视检查中文、标签、坐标、范围与串行参考；不代表用户已验收。

课程资料2,564文件的路径/内容前后不变且未跟踪。正式src与CMake相对320437c无改动；未重新构建、未运行数值回归、未重新采样，不补写新的21/21通过结论。图表继续标明16逻辑CPU/14WSL可见core、M随N增加、UTC/轮次趋势及未校准外部物理时间；不称弱扩展、不剔除慢样本、不预设16优于8。完整本轮审计见results/validation/results-visualization-checks.log。仅提交推送同名origin/Evaluation，M4交用户验收，不操作main。

M5历史准备阶段实际检查（制作PPT之前）：`python3 scripts/check_results.py`退出0，67个原工件、2快照、4旧清单、123项历史源码哈希、三批5份统计CSV逐字节复算、九组图44配置/440点及拒绝覆盖检查均通过；只做证据/统计校验，没有调用求解器或新增性能采样。`git diff --check`通过。PPT尚未制作，渲染与讲述检查未运行。

## PPT设计第一步确认（2026-11-12，历史过程）

用户选择逐步确认设计并调用PPT Master，随后明确回复“确认定位，采用自由设计”。受众为课程教师，5分钟现场由本人主讲，会后备注/来源供审阅；核心信息“正确性有证据，并行收益有条件”。16:9、8页正文＋备份页，正文280秒；内容可为讲述精简重组，数字/结论口径保留。PPT Master已导入报告/讲稿/02-r1统计副本，课程原资料未导入；当前准备三套具体方案进入第二步确认，尚未锁定方案或制作页面。

## M5材料初版核查与交付准备（2026-11-12，配色修订前）

用户确认组合设计后已完成全部材料，文件入口和检查定义见report/README.md及REVIEW.md。PPT源最终12/12、零警告错误；12备注/213可编辑文本图元/1原生公式，LibreOffice实际打开并渲染12页，最终重渲染与检查图逐像素一致。报告8页已渲染。主图10点和10区间、M3误差比/观测阶、链接、统计CSV及PNG字节副本、2568课程文件本轮快照前后路径/内容校验通过；讲稿估算281.4秒，人工实讲待验证。

统一证据校验曾发现RESULTS说明也在冻结哈希中，已撤回标题/导航变更，保持全部results工件原字节；随后统一校验通过，真实输出存report/evidence-check.log。src/CMake/tests/scripts/results相对30c4a43无差异，本阶段未调用求解器、未新增性能采样。用户原AGENTS修改按明确授权纳入。当前仅M5交付，待用户验收；提交推送同名origin/M5，不操作main。

## M5模板配色修订（2026-11-12）

初版材料提交fd33b27已成功推送origin/M5；用户随后指出配色不合适，要求参考本地PPT模板。只读查看两份模板主题与实际页面后，以其实际深蓝#124C8D、白、浅蓝#EDF3FA和铜金#C38749重配，封面/结束页深蓝底，正文白底；备份原图保留已验收原色。12页正文文字和12备注与初版完全一致，数据/公式/预算不变。

修订后源SVG最终12/12、0错误0警告，导出包通过；LibreOffice实际打开新版PPTX并导出12页PDF，重新渲染检查全部页面与文本边界。更新report/presentation.pptx、PDF、总览及校验；工具检查通过后提交推送同名M5。材料待用户验收；个人信息、人工实讲及PowerPoint人工显示/编辑仍待本人核实。不改求解器、results或课程资料，不采样、不操作main。


## M5 PaperBanana安装与制图调研（2026-11-13）

用户要求安装指定官方Skill并调研项目配图。已用skill-installer安装paperbanana到本机技能目录，固定上游9ceea039；完整运行库/独立Python/91依赖包和diagram数据集放项目外。CLI与模块导入通过，20项上游离线检查通过；ref298/test292及全部引用图像存在。具体版本/位置/验证见report/paperbanana/installation-check.json，方案和三份输入见report/paperbanana/README.md。

推荐先试五点与双缓冲、MPI halo、OpenMP同步机理图，PNG候选与可编辑PPT重建分别处理；正式统计图保留原证据。生成密钥未配置，真实生成、API连通性和图像质量未运行/待验证；不把调研当作完成出图。当前PPT、最终报告、求解器和数据未修改，M5仍待验收。
