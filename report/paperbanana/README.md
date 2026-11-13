# PaperBanana 安装与本项目制图方案

调研日期：2026-11-13。范围：安装、运行环境与用法核对、三份制图输入样稿；当次未生成图片或修改PPT。M5材料仍待用户验收。

2026-11-14更新：按用户新要求，已用PaperBanana提示中的规划/审图方法指导GPT-6.1-sol直接绘制[五点显式机理图](stencil-sol-v1/README.md)，包含SVG/PNG/PDF。该路径不调用PaperBanana原模型API，与下述API调用方案分开记录。

## 安装位置与版本

| 项目 | 位置 / 事实 |
| --- | --- |
| 官方仓库 | [dwzhu-pku/PaperBanana](https://github.com/dwzhu-pku/PaperBanana) |
| 固定源码 | `9ceea039be86dd40294361856a4b7bf097d9e2b7` |
| Codex Skill | `/home/nuo/.codex/skills/paperbanana/SKILL.md` |
| 完整运行库 | `/home/nuo/.local/share/paperbanana` |
| 独立Python | `/home/nuo/.local/share/paperbanana/.venv/bin/python`，Python 3.12.3 |
| 本机入口 | `/home/nuo/.codex/skills/paperbanana/run-local.sh` |
| 原始入口 | 完整运行库中的`skill/run.py` |
| 检索数据 | diagram/ref 298份、test 292份，所有引用图像存在；数据集固定于`2ac62aa3e9118d0ea8d169d00a8c3b0f05b9cb09` |

通过skill-installer从官方仓库的`skill/`安装。上游`run.py`依赖仓库父目录下的`utils/`、`agents/`、配置和风格资料，因此还在项目外安装了完整库及独立虚拟环境。Skill内增加本机入口和LOCAL_INSTALL说明；上游run.py未改。uv虚拟环境没有pip模块是正常状态，包由uv管理。

本项目Git中只记录调研、样稿和验证摘要，不纳入第三方完整库、虚拟环境、密钥、检索数据集或课程原件。安装源与运行源码版本一致，机器路径仅为本机使用说明。

## 能力及边界

它将“方法正文＋图意/图注”交给Retriever、Planner、Stylist、Visualizer、Critic组成的生成流程；可检索参考、规划构图并迭代图片。具体CLI及默认值见[官方Skill](https://github.com/dwzhu-pku/PaperBanana/blob/9ceea039be86dd40294361856a4b7bf097d9e2b7/skill/SKILL.md)。

源码核对结果：

- Skill入口最后保存PNG；不直接输出SVG或可编辑PPTX。不能因为图像看似矢量就宣称原生可编辑。
- 默认`--num-candidates 10`、`--max-critic-rounds 3`、`--exp-mode demo_full`，会涉及多次模型调用。试图建议显式改为1个候选、1轮Critic；实际费用和耗时未测量，不给出虚构估算。
- `demo_full`包含Stylist；源码会读取NeurIPS 2025风格指南。现有PPT要求蓝白、黑体/楷体和较大字号，建议先试`demo_planner_critic`，通过输入约束风格，避免Stylist另行改成论文图风格。这是针对本项目的建议，尚无图像效果验证。
- `--figure-size 10-13cm`在共享配置中映射为`2k`层级；`14-17cm`映射为`4k`。这是发送给支持该参数的提供商的请求，不保证所有提供商的实际输出尺寸。见[尺寸映射源码](https://github.com/dwzhu-pku/PaperBanana/blob/9ceea039be86dd40294361856a4b7bf097d9e2b7/utils/legacy_generation_options.py)。
- 保留`--retrieval-setting auto`。Skill在进入生成前会调用数据集准备，首次可能下载diagram任务的test/ref两份Parquet，即使选择none也会走准备逻辑；不能把none当作完全离线开关。见[入口源码](https://github.com/dwzhu-pku/PaperBanana/blob/9ceea039be86dd40294361856a4b7bf097d9e2b7/skill/run.py)。
- 参数解析器虽接受`--task plot`，当前最终图片提取仍按diagram键处理；本轮未验证plot端到端，不依赖它重画正式性能图。
- 文字、上下标、邻接关系和箭头仍可能出错，Critic不等于数学正确性证明；生成结果须按事实检查，而非只看美观。

默认模型名来自安装版本配置：`gemini-3.1-pro-preview`与`gemini-3.1-flash-image-preview`。配置中有这些名称，不代表本机已验证它们当前可用、价格或额度。实际生成前应按所用提供商确认并显式记录模型名。

## 本项目优先做的三张图

| 顺序 / 对应页面 | 输入样稿 | 图的任务 | 必须保留的事实 |
| --- | --- | --- | --- |
| 1 / P03 | [五点格式与双缓冲](01-stencil.md) | 把五个旧值、权重、写入和整层换层回路连成机理图 | 中心1−4r、四邻居r；只读old；next同坐标写；整层后交换；恰好M步 |
| 2 / P04 | [MPI halo](02-mpi-halo.md) | 展示全局拥有行、局部halo副本与两个方向的交换 | N8/P3分3/2/2；owned与ghost不同；两次Sendrecv；物理端部清零；无每步全局屏障 |
| 3 / P05 | [OpenMP划分与同步](03-openmp-sync.md) | 用线程泳道解释行分配与两道同步屏障 | static,1循环分行；共享双缓冲；单线程swap；两道全团队屏障；Q大于行数合法 |

样稿由本项目`src/heat.cpp`、`src/heat_mpi.cpp`、`src/heat_openmp.cpp`和[设计文档](../../docs/DESIGN.md)提炼，不发送教师任务书、讲义、参考模板或个人信息。全部是方法示意，不冒充真实温度场或实验截图。性能曲线继续复用已验收的原CSV/SVG/PNG及探索性区间。

三份英文样稿包含科学约束、构图要求和生成后审查点。风格统一为白底、#115EA2蓝、#092F51深蓝、#C9D7E3网格、黑色正文；避免长公式、小中文段落及多色装饰。短标签仍须检查，不能把英文输入当作正确性的保证。

## 建议调用方法

先在本机安全配置`GOOGLE_API_KEY`或`OPENROUTER_API_KEY`，不要把密钥放在项目、样稿或聊天里。当前没有配置生成密钥，也没有发起真实生成。两者都配置时默认路由优先OpenRouter；支持的模型名和计费以提供商为准。

现有幻灯片为16:9，但扣除页眉页脚后的内容区约为1200×520，更接近21:9。P03首图建议21:9以填满横向流程区；P04/P05若采用较高的泳道/分块图，可再选16:9或3:2，不把幻灯片比例强套到每幅插图。

在本项目根目录运行以下命令。它是后续生成命令示例，本轮未执行：

```bash
/home/nuo/.codex/skills/paperbanana/run-local.sh \
  --content-file "$PWD/report/paperbanana/01-stencil.md" \
  --caption 'Five-point old-layer stencil to next-layer update and full-layer buffer swap; clear large geometry, minimal labels, blue and white, scientifically exact.' \
  --task diagram \
  --aspect-ratio 21:9 \
  --figure-size 10-13cm \
  --exp-mode demo_planner_critic \
  --retrieval-setting auto \
  --num-candidates 1 \
  --max-critic-rounds 1 \
  --output "$PWD/build/paperbanana-candidates/stencil-trial-01.png"
```

命令先将候选保存到忽略的build目录，避免把未经审阅的图混入最终交付。为另两张图更换content-file、caption和output；caption明确想强调的流程，不能只写“漂亮”。未运行时不预先填写结果路径、生成时间、费用或合格结论。

## 与PPT Master配合

1. 从P03开始试一张，审查五点、权重、层次与换层关系；不正确则修改输入或反馈重做，保留真实失败和版本。
2. 把生成结果作为构图候选。若直接用于PPT，应按图片属性交付，不能承诺每条箭头都可编辑。若沿用当前可编辑算法图要求，可参考其布局，由PPT Master手写原生SVG图元重建，重建结果再单独验证。
3. 长公式、中文标题、边界说明和关键标注优先用PPT的可编辑文本/原生公式覆盖或重建；为防标签重复，先确保候选图上对应区域可用，不能用不透明文字框随意遮盖错误机理。
4. 插入内容区而非整张幻灯片，保留现有页眉页脚；若图内字在投影上仍小，拆解/删减说明，不靠提高分辨率解决字号问题。
5. 每张获选素材记录来源版本、模型、输入、参数、原输出、SHA-256及核查意见，进入`report/`素材目录；不修改`results/`证据。
6. 再导出PPTX，实际渲染检查中文、公式、图内标签、箭头和裁切；更新逐页讲稿。生成模型的自评不代替答辩者理解与人工演练。

## 本轮验证

安装及检查摘要见[installation-check.json](installation-check.json)。真实图像生成、API连通性、候选美观性、PPT集成与生成图语义验证均未运行；这份方案不宣称已经得到更好的图片。环境验证与求解器数值验证分开记录。
