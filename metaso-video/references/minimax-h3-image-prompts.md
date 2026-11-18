# MiniMax H3 Image 提示词撰写

核对日期：2026-11-18。来源为[官方模型卡的Full Workflow](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image#full-workflow)、[官方PE说明](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image-PE)、[文生图扩写模板](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image-PE/blob/main/prompt/t2i/task_prompt.txt)、[编辑扩写模板](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image-PE/blob/main/prompt/edit/task_prompt.txt)。以下区分官方扩写契约、秘塔接口和本技能的组织建议，不把PE系统提示词原样作为生成请求。

## 1. 用户需求与最终生成描述不同

官方模型卡说明原始图像模型期望详细的英文整图描述；MiniMax官方API会用Context IR把任意语言的短需求转换成这种描述。PE仓库还公开了文生图权重和编辑任务模板；不能据此声称同一PE权重已完整支持图片编辑。

| 实际工作流 | 写法 |
|---|---|
| 秘塔 enhance_prompt=true（默认） | 可先用中文讲清目标、文字、素材职责和保持范围，查询后检查enhanced_prompt；秘塔内部是否完全使用相同PE实现未确认 |
| 秘塔 enhance_prompt=false | 为贴近官方原始模型输入，建议直接准备具体的英文描述；画面内中文文字仍原样保留。这是写作建议，不宣称中文会被API拒绝 |
| 本地/独立PE扩写 | PE返回扩写描述和画幅建议；生成时取描述字符串，并用最终确定的尺寸，不把整份PE JSON放进prompt |

官方T2I PE输出字段是expanded_caption、aspect_ratio；编辑PE是expanded_caption、target_aspect_ratio。这是扩写器输出，不是秘塔创建字段。秘塔仍发送prompt与size等，详见[图片API](image-generation.md)。明确选定的画幅优先于扩写建议；不要为扩写新增背景而擅改画幅。官方原始模型的4096-token截断也不能替代秘塔1–2000字符上限，提交前另检查长度。

## 2. 文生图：写最终画面，不写空泛质量标签

按任务选组织方式，而非强制每张图使用相同字段：

- 摄影/场景图：主体数量与特征、姿态和接触关系、前后左右位置、机位与构图，再写环境、光线、材质和媒介。动作只冻结一个可成立的瞬间，身体朝向、视线和运动方向一致。
- 海报/UI/图表/说明图：先确定完整的信息结构、区域层级和实际文字/数据，再安排视觉风格。不能只列“有图表、有按钮”，却没有标签、数值或按钮文案；没有事实依据时不编造真实数据。
- 原样保留用户指定的人名、数量、公式、左右顺序与可见文字；文字标明内容和所在表面。明确需要的留白可以保留，不为“丰富”擅自填满所有区域。
- 不增加独立negative_prompt字段：官方原始服务明确不支持，秘塔也未列出。需要排除内容时在正常prompt中说明，仍需看结果验证。

本技能原创、可直接作为英文描述的例子：

```text
A vertical product poster shows one cobalt-blue ceramic mug on a pale gray stone pedestal in the lower half of the frame. Soft light from the left reveals the glazed surface and the shape of the handle. A warm ivory background leaves generous empty space above the mug. The exact Chinese headline "慢下来" appears once at the upper center in dark blue type, clearly separated from the mug. The composition is a realistic studio still life with a restrained palette.
```

单独设置size为对应竖图尺寸；只在文字里写vertical不代替API尺寸。

## 3. 编辑：先定义引用，再判断保留关系，最后写变化

官方编辑PE使用一段英文描述，内部有三个逻辑部分，不输出“第一部分”等标题，也不借用H3视频的声音字段：

1. 用 `<Picture N>` 指代顺序输入的图片；只给后续需要独立追踪的源主体/属性分配 `<Subject N>`。新造内容、完全删除且不复用的对象无需硬编Subject。图中可辨文字和数据若涉及编辑或保留，应据实记录；看不清的不猜。
2. 概括目标图，并为每个已定义Subject分别判断：完整保留、部分保留、直接属性迁移、宽松参考。修改了姿态、位置、颜色等对应范围就不能同时声称完整保留；借色不等于借造型和材质。
3. 只展开修改与新增部分及其融合效果。已经完整保留的主体不再次重写外观，避免引入变化；修改文字时给出完整的新文字，保留原语言与标点。镜头/画幅变化如果实际改变构图，应明确反映，不能一边重构画面一边宣称整图不变。

这个结构是官方扩写模板，不代表所有普通编辑请求必须手写Subject标签。短指令交给增强流程时，至少明确“哪张图作基础、改哪里、保留什么、其他图只提供什么”。

本技能原创、采用上述结构的英文编辑例子（图2只提供杯身颜色）：

```text
The mug in <Picture 1> is <Subject 1>. The body color of the mug in <Picture 2> is <Subject 2>. The surrounding scene in <Picture 1> is <Subject 3>. The target image shows <Subject 1> with its body color matched to <Subject 2>. <Subject 1> is partially preserved: its shape, handle and placement remain, while its body color changes. <Subject 2> supplies only the body color transferred to <Subject 1>. <Subject 3> is fully preserved. The new glaze follows the existing highlights and shadows.
```

## 4. 素材、提交与验收

官方模型卡列出最多16图，秘塔当前最多3图，Design与CLI按秘塔限制执行。图片编号按reference_file_ids的顺序，不按文件名。官方本地部署的seed、sampling steps、guidance scale、multipart编辑路径不能直接套入秘塔。

提交前复核用户原文、主体数量、引用职责、保留范围、最终画幅、增强开关和2000字符限制。返回图片后检查文字错漏、构图、物体结构、身份及未编辑区域；“扩写完成”“返回PNG”“分辨率正确”均不证明内容符合要求。未进行本技能的真实生图实测。
