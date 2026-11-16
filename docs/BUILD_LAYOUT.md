# 本地build目录

2026-11-15整理。`build/`全部为本地生成物，继续由`.gitignore`排除；提交的是使用说明及工具路径适配，不提交二进制、环境或历史临时脚本。

## 当前结构（2026-11-16中间产物清理后）

```text
build/
├── debug/、release/               当前构建
├── tools/python/                  报告工具环境
├── tools/libreoffice/              解包运行环境与配置，deb下载缓存已清理
├── tools/font-preview/             保留字体选择记录，生成字体缓存已清理
├── logs/                          保留过程日志/JSON/CSV，渲染图片已清理
├── archive/work/                  保留历史脚本、记录，图像/预览副本已清理
├── archive/layout-20261115/        旧整理映射及哈希
├── m5-tools -> tools/python       兼容链接
├── m5-lo -> tools/libreoffice     兼容链接
└── README.md                      当前导航
```

规范构建目录固定为`build/debug`与`build/release`。`archive/cmake`中的CMakeCache/Makefile含原绝对路径，属于历史归档，不在其中继续构建，也没有通过替换缓存文本伪装成可搬移构建。

## 原来有哪些内容

整理前build根部89项，合计约808.82MiB，13套CMake构建树包含根部旧Debug、M2/M2b/M3 Release、M4普通/诊断/扩大矩阵及sanitize。其他内容包括：M4一次性核查/写文档脚本、日志/CSV复算；M5材料导入/图片/PDF预览；Python依赖与LibreOffice运行环境；公式缓存；两个示例解CSV。

正式证据已在[results/RESULTS.md](../results/RESULTS.md)。build中的旧复算、console、metrics、临时脚本不能替代正式结果，也不会自动成为新样本。原始课程资料仍只读保留于docs/sources，未迁入本目录或Git。

## 构建与检查

```bash
cmake -S . -B build/debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug --target check --parallel 2
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
```

`check`显式使用当前构建目录；手动调用`python3 scripts/check.py`时传`--test-dir build/debug`。不修改其历史默认值，也不改求解器或CMakeLists。

示例输出另放：

```bash
mkdir -p build/outputs/examples
./build/debug/heat_serial --N 40 --M 1600 --T 0.1 --alpha 1 > build/outputs/examples/solution-N40.csv
```

示例命令供后续使用，不表示本轮新增数值/性能采样。Debug回归、Release构建的本轮实际状态以STATUS及logs/layout-20261115为准；CTest耗时不作为性能测量。

## 报告工具与兼容路径

报告工具使用`build/tools/python/bin/python`，例如：

```bash
build/tools/python/bin/python report/check_report.py
```

原Python环境的命令入口可能含绝对shebang；LibreOffice配置也有旧路径。因此保留`build/m5-tools`与`build/m5-lo`两个兼容链接，没有全局改写虚拟环境或第三方安装文件。它们并非重复环境，暂不单独删除；换机器需重新准备工具，不能把本机环境当成可移植安装包。

报告缓存寻址已改为build/cache/report-math；PPT运行配置指向build/tools/libreoffice，既有PPT检查的课程快照指向archive/work/m5-v4-annotations。这里只适配路径，本轮不继续制作报告/PPT。

## 追溯与保护

移动映射和旧文件哈希保留在本地`build/archive/layout-20261115/before.json`，其old/new字段按整理前89个顶层条目定位。`preservation.json`记录逐文件哈希/软链接检查；本轮没有删除旧工件，没有执行归档中的一次性update.py或其他写文档脚本。

历史文档、原始日志、JSON及校验清单中的旧build路径是当时事实，未批量修改；旧报告目录整理的before快照现在位于`build/archive/work/report-organization`。正式results、报告正文/PDF、PPT成品、教师资料不因本轮build整理而变化。


## 本轮实际验证

| 检查 | 2026-11-15结果 |
| --- | --- |
| 新Debug | 配置/编译成功，`check`的20/20通过，含串行/MPI/OpenMP/M3及计时回归 |
| 新Release | 配置/编译成功；Release CTest未运行，本轮未重复两套数值回归 |
| 原生成物保护 | 13,479个普通文件SHA-256及301个软链接目标保持；一处第三方文档链接原快照即缺失目标，无新增断链 |
| Python与LibreOffice | 新Python路径及旧路径兼容导入通过；LibreOffice24.2.7.2版本入口通过，未生成PDF/PPT |
| 报告与课程资料 | 独立报告检查通过；2,570课程文件路径/内容不变 |

本轮不改源码、CMakeLists、测试或实验脚本、results与报告正文/PDF，未新增正式性能采样。Debug CTest的计时回归和耗时输出只验证程序/检查入口，不进入M4统计。详见本地logs/layout-20261115；它们是新构建验证，不覆盖results中原阶段日志。


## 2026-11-16旧版本清理

用户新要求覆盖上述“全部旧工件保留”的工作区策略：build中的临时PPTX、旧presentation/report PDF和报告Markdown快照已清理，源码构建、运行日志、工具环境和正式results证据保留。所有移除文件先备份到仓库外，详见report/records/workspace-cleanup-20261116.json；历史layout清单描述的是当时状态。


## 2026-11-16删除中间产物

用户明确授权删除中间产物。archive/cmake、outputs和cache已移除；后续命令会按需重新建立输出/缓存目录。logs及archive/work中的渲染图片、预览PDF/SVG已清理，文本日志、JSON、CSV等追溯记录保留。tools中的Python、LibreOffice解包运行环境及兼容链接保留，仅清理deb下载包及字体网页生成缓存。上文原文件保护、旧目录及测试描述均为历史状态。清单见report/records/intermediate-cleanup-20261116.json。
