# 五点显式机理图：PaperBanana方法指导＋GPT-6.1-sol绘制

交付日期：2026-11-14（Asia/Shanghai）。本轮只制作独立图，尚未替换现有PPT。待用户审阅。

## 图片入口

| 用途 | PNG | 可编辑SVG | 矢量PDF |
| --- | --- | --- | --- |
| 完整机理与时间循环总览 | [完整图](diagram.png)，3600×2160 | [图源](diagram.svg) | [PDF](diagram.pdf) |
| PPT五点读写主图 | [宽幅主图](mechanism-wide.png)，3600×1300 | [图源](mechanism-wide.svg) | [PDF](mechanism-wide.pdf) |
| PPT整层时间推进 | [宽幅流程](time-loop-wide.png)，3600×1100 | [图源](time-loop-wide.svg) | [PDF](time-loop-wide.pdf) |

完整图适合审阅和说明。PPT建议把两张宽图分开展示；不要把完整总览强行压入一个1200×520内容区。两张宽图分别缩到1200px宽时，高约433/367px，能保留较大的标注。SVG中的文字、网格、点、箭头和上标都可编辑；SVG可编辑不等于已经转换为PowerPoint原生公式或形状。

## 图的读法与公式

左侧五个突出节点内部是权重，不是温度：中心为1−4r，四个轴向邻居各为r。它们全部属于旧层n，只读old；加权结果写入独立next数组的同一坐标、层n+1。箭头表示数值计算依赖，不表示物理热流。局部网格边沿不被当作物理边界。

$$
U_{ij}^{n+1}=(1-4r)U_{ij}^{n}
+r\left(U_{i-1,j}^{n}+U_{i+1,j}^{n}+U_{i,j-1}^{n}+U_{i,j+1}^{n}\right),
\qquad r=\frac{\alpha\Delta t}{h^2}\le\frac14.
$$

h=1/N，Δt=T/M。图中i为行、j为列；均匀网格用作结构示意，不按图上像素量取物理距离。方法时间一阶、空间二阶。

时间循环从old=U⁰、next=0、n=0开始，更新本层全部内部点并保持四条物理边界为零；整层完成才交换old/next并令n增1。n<M时回到更新，n=M时从old取最终Uᴹ。M≥1，恰好推进M步。此为串行算法的完成先后关系，没有添加线程屏障；MPI/OpenMP的同步不在本图范围。

## 如何制作、如何核查

主代理实际读取已安装PaperBanana的Planner、Stylist、Critic提示，形成[指导规格](GUIDANCE.md)，由用户指定的GPT-6.1-sol绘图代理直接编写SVG及[本地渲染脚本](render.py)。没有运行PaperBanana的Gemini/OpenRouter生成接口、自动Retriever或原API多代理流水线，也没有调用imagegen工具。不能将此记录为“PaperBanana已成功运行原生成流程”。

源码依据为[heat.cpp](../../../src/heat.cpp)、[设计文档](../../../docs/DESIGN.md)和[项目规格](../../../SPEC.md)。图不是实验温度场、性能结果或测试截图。

主代理实际检查了最终总览、两张宽幅PNG，以及两张1200px宽预览；五点数量、轴向位置、可见权重、读写层元数据和PDF页边界作了结构核查。初版幂次改为原生文本定位上标，否分支箭头修正至结束框边界；完整图较高，另做宽幅版本保留字号。结果见[checks.json](checks.json)、[文件清单](manifest.json)和[绘图说明](DESIGN.md)。

本轮未运行求解器构建、数值回归、性能采样或PPT集成检查；Microsoft PowerPoint本机显示、SVG拆分编辑与用户验收仍待验证。现有PPT、最终报告、讲稿和results证据未改。

## 复现

本机在仓库根目录执行：

```bash
build/m5-tools/bin/python report/paperbanana/stencil-sol-v1/render.py \
  --fontconfig build/m5-lo/fonts.conf \
  --font /mnt/c/Windows/Fonts/simhei.ttf
```

依赖CairoSVG和Pillow。脚本只做本地矢量绘制与导出，不调用网络或模型。--font指定本机已有中文TrueType字体用于上标度量，--fontconfig应能将SimHei映射到相同字体；在其他机器需调整字体配置，不能直接宣称外观完全相同。字体文件不随Git分发。脚本重跑会重新生成本目录三组图；PDF可能因生成元数据而有不同哈希。
