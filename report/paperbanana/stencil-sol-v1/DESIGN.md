# 绘图说明

完成日期：2026-11-14。用户指定的GPT-6.1-sol绘图代理自行编写SVG；采用主代理从PaperBanana Planner / Stylist / Critic提示中提炼的方法指导，没有调用PaperBanana的Gemini/OpenRouter模型API或imagegen工具。依据SPEC第2节、DESIGN第1节及src/heat.cpp的initial_field / step / solve核查。

上部左侧是局部旧层网格，仅五个轴向输入被突出。节点内标的是乘法权重，而非温度：中心 1-4r，四邻点各 r。整组输入经 Σ 加权求和，写入独立 next 缓冲的同坐标。蓝色箭头表示计算依赖，并非热流方向。局部网格边缘没有标成物理零边界。图中文字、网格、圆、箭头均为原生 SVG 可编辑元素；U 的上标 0/M 与 h 的上标 2 使用同组原生 SVG text 的明确坐标偏移与较小字号排版，规避机器字体缺少 Unicode 上标。

底部是整层推进控制流：初始化 → 更新全部内部点且物理四边零 → 整层完成 → 交换缓冲并累加 n → 判断 n<M。是分支回到更新，下一步读取交换后的 old；否分支输出 old=U^M。M>=1，因而第一次更新前不需额外判定。控制回路不表示本时间步中 next 数值回流输入，不添加串行屏障。

复现：在仓库根目录运行 `build/m5-tools/bin/python report/paperbanana/stencil-sol-v1/render.py --fontconfig build/m5-lo/fonts.conf`。脚本仅本地生成 SVG 并使用 CairoSVG 导出 3600×2160 PNG 和矢量 PDF，不复制字体。完整 overview 画布1800×1080，仅用于总览。PPT建议分开插入 mechanism-wide（1800×650）和 time-loop-wide（1800×550）：在1200×520内容区可按宽度缩放，主标题约27–29px，机制图最小标注24px，流程主字约27–29px、最小标注约23px。

真实检查：已实际渲染并查看 PNG，修正初版缺字与上下标渲染问题，最终使用同组原生文本偏移上标；核对五点数量、轴向索引、权重、缓冲读写方向、零边界说明和 M 步控制流。未修改求解器，未运行数值构建/回归，未测性能。未在 Microsoft PowerPoint 实机验证字体与 SVG 拆分编辑；可用 PNG/PDF 保持当前外观。

第二轮审图修正：补充两个大字号宽幅版本；修正否分支为连接结束框右侧中点，否标签离开竖线。已再次真实渲染查看宽幅PNG。SVG含old-layer、weighted-sum、next-layer、time-loop语义组；五个旧层节点带data-site/data-weight/data-layer，供独立结构核查。
