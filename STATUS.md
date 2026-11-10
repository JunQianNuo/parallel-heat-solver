# 项目状态

更新日期：2026-11-10（Asia/Shanghai）。

## 当前阶段

- M0：用户已验收通过（2026-11-10）。M1：串行基准已获用户审查通过（2026-11-10），测试耗时四位小数显示补充已实现并验证；M2–M5 尚未开始。
- 当前功能分支：`feature/m1-Serial`（用户准备）；本轮开始 HEAD 为 `6889fb0`，工作区干净、无合并冲突。M0 文档建立提交为 `0dbd3a5`。
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

无已知 M1 实现阻塞。M1 串行基准已获用户验收；MPI 接口/限制、系统验证、实验资源/矩阵及报告/PPT 分别留待 M2–M5。资料不随 Git 分发，新克隆须由使用者补齐。M1 提交与同名远程推送以实际 Git 结果和本轮最终汇报为准；不在提交正文中自引用尚未生成的哈希。

## 下一步

由用户合并 `feature/m1-Serial`。用户另行选择 M2 并准备对应功能分支后，再开始 MPI；当前不进入 M2，不开展正式性能实验。

## M1 接口确认记录同步

用户于 2026-11-10 回复“采用建议：命名参数、20/400/0.1/1、全场 CSV”。本次仅同步 SPEC、STATUS、DECISIONS 和 AI_USAGE 的确认状态；未修改代码或数值参数，未重跑构建/数值测试（纯文档变更），执行差异及暂存检查。串行实现提交为 `d568e45`，已推送 `origin/feature/m1-Serial`；接口确认不等于 M1 整体验收。

## M1 验收与耗时显示补充

用户明确回复“暂无其他问题，审查通过”，随后指出精确小数位数尚未修改。本轮补齐 `cmake --build build --target check --parallel 2` 入口：执行 CTest 并从 XML 测量值按秒显示四位小数，保留原始输出与失败状态。未修改求解器或旧日志。

实际执行 `cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug`、`cmake --build build --target check --parallel 2` 成功，6/6 通过；六项显示值与 XML `.4f` 结果逐项一致。另在 `/tmp/` 临时 CMake 项目构造 `cmake -E false` 测试，脚本显示真实失败诊断并返回 CTest 退出码 8。补充真实日志见 [m1-precision.log](docs/validation/m1-precision.log)。本轮未重新运行 ASan/UBSan（求解器及数值测试未变）；未开展性能实验。文档同步验收事实，下一阶段仍由用户选择。
