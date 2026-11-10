# 项目状态

更新日期：2026-11-10（Asia/Shanghai）。

## 当前阶段

- M0：用户已验收通过（2026-11-10）。M1：串行基准已获用户审查通过（2026-11-10），含测试耗时四位小数显示补充的整个分支已获用户再次确认审查通过；M2 实现及 Debug/Release 基本回归已完成、待用户验收；M3–M5 未开始。
- 当前功能分支：`feature/m2-mpi`（用户准备）；本轮开始 HEAD 为 `edeff61`，工作区干净、无合并冲突。本地 `main` 和 `origin/main` 同指 `edeff61`，M1 已合并。M0 文档建立提交为 `0dbd3a5`。
- 已确认：任务书第 4 题，C++17 + CMake/CTest，串行基准 + MPI，先验证串行；OpenMP 为待评估扩展。
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

无已知资料或环境阻塞。M2 接口/限制见 DESIGN 第 7 节及 DECISIONS D013–D018；系统验证、正式实验资源/矩阵及报告/PPT 仍留待 M3–M5。课程资料仅本地存在，新克隆须由使用者补齐。

## 下一步

完成本轮 M2 验证、文档及提交推送后由用户验收；不自行进入 M3 或 M4，后续由用户决定合并和准备下一功能分支。下文 M1 收尾为历史记录，不代表当前仍未授权 M2。

## M1 接口确认记录同步

用户于 2026-11-10 回复“采用建议：命名参数、20/400/0.1/1、全场 CSV”。本次仅同步 SPEC、STATUS、DECISIONS 和 AI_USAGE 的确认状态；未修改代码或数值参数，未重跑构建/数值测试（纯文档变更），执行差异及暂存检查。串行实现提交为 `d568e45`，已推送 `origin/feature/m1-Serial`；接口确认不等于 M1 整体验收。

## M1 验收与耗时显示补充

用户明确回复“暂无其他问题，审查通过”，随后指出精确小数位数尚未修改。本轮补齐 `cmake --build build --target check --parallel 2` 入口：执行 CTest 并从 XML 测量值按秒显示四位小数，保留原始输出与失败状态。未修改求解器或旧日志。

实际执行 `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug`、`cmake --build build --target check --parallel 2` 成功，6/6 通过；六项显示值与 XML `.4f` 结果逐项一致。另在 `/tmp/` 临时 CMake 项目构造 `cmake -E false` 测试，脚本显示真实失败诊断并返回 CTest 退出码 8。补充真实日志见 [m1-precision.log](docs/validation/m1-precision.log)。本轮未重新运行 ASan/UBSan（求解器及数值测试未变）；未开展性能实验。文档同步验收事实，下一阶段仍由用户选择。

## M1 分支最终验收

2026-11-10，用户在澄清 CTest 原始文本与 XML 四位小数摘要的关系后，明确回复“该分支审查通过”。验收对应 `feature/m1-Serial` 的 `7dd9329`，包含串行基准、基本测试与四位小数显示补充。此次仅同步 STATUS 和 AI_USAGE 的最终验收记录，检查文档差异和暂存范围；未重跑构建或数值测试（无代码变更）。由用户负责合并，M2 尚未授权开始。

## M2 实现与验证（2026-11-10，待用户验收）

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

未运行：P>4、多机通信、真实内存耗尽/进程丢失、ASan/UBSan（本轮未重跑）、M3 系统化验证及 M4 正式性能实验。测试专用受控错误注入不能替代这些未运行项。M2 尚待用户验收，不自动进入下个里程碑；提交及同名分支推送结果以实际 Git 输出及最终汇报为准。

提交前审阅：按文件明确暂存并检查完整差异；源码/文档空白检查通过，日志保留 CMake 原始的 3 行末尾空格，使用仅本次命令的 `core.whitespace=-blank-at-eol` 检查。最后仅把测试汇总文案缩为“help checked”，避免其他平台缺少 /dev/full 时与明确未运行提示冲突；测试逻辑未变，此文案修改未重跑数值检查。
