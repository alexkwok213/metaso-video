# MiniMax H3 提示词官方指南（要点摘编）

本文件把 MiniMax 官方提示词文档的结构与硬性规则整理成中文，便于写 H3 请求时使用。完整英文原文见下方来源；字段名、标签和示例一律保留英文，因为 H3 实际接受的就是这种格式。

- 官方基础指南（T2VA / I2VA / FL2VA / L2VA）：https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- 官方参考指南（Full-Reference 六段式）：https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md

## 1. 任务模式

- **T2VA**：纯文本生成完整音视频时间线。
- **I2VA**：T2VA 主体 + 首帧指令 + 从首帧向前发展的视觉路径。
- **FL2VA**：T2VA 主体 + 首尾帧指令 + 从首帧连续过渡到尾帧。
- **L2VA**：T2VA 主体 + 尾帧指令 + 从合理的前置状态收束到尾帧。

## 2. 最终提示词结构

### 2.1 第一部分是指令（仅含图任务需要）

- T2VA 没有图对齐指令，直接以三个核心字段开头。
- I2VA 固定首行：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA 固定首行：`How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA 固定首行：`How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`

其中 `N` 是实际最后一镜的序号，`S.SS` 是精确到两位小数的视频时长。指令必须是提示词的第一行，后面空一行再写核心字段。

### 2.2 第二部分含三个核心字段

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

- `integrated_multimodal_description`：沿时间线描述画面、动作、镜头、说话人、对白、歌唱和画面内声音。
- `overall_soundscape`：汇总整段的环境声、物理动作声和非语言人声。
- `non_diegetic_music`：描述角色听不到、只有观众能听到的背景音乐。

## 3. 关键帧如何融入描述

- **I2VA**：`<Picture 1>` 是 0.00 秒的实际首帧，属于 `[Shot 1]`。先确立图里的风格、主体、构图、场景锚点，再描述后续动作；人物身份、衣着、颜色、关键物体、空间关系保持一致。推荐结构：首帧锚点 → 动作起始 → 连续展开 → 结果或反应。
- **FL2VA**：图 1 是开头，图 2 是结尾，重点描述主体如何移动、姿态如何变化、物体如何被操作、构图如何演变、场景或光线如何过渡。一般偏好单镜连续插值，仅在明确指定时才用多镜。推荐结构：首帧状态 → 可见的中间变化 → 差异逐步收窄 → 尾帧状态。
- **L2VA**：`<Picture 1>` 是尾帧、属于最后一个 `[Shot N]`，并非天然属于 Shot 1。从用户意图和尾帧推断合理的前置状态，再让人物、物体、镜头、场景逐步逼近参考图。推荐结构：合理前置状态 → 明确动作与过渡路径 → 末镜逐步收束 → 尾帧落定。

## 4. 三个核心段落的写法

- **沿时间线展开描述**：`[Shot 1]` 开头先写整体风格和初始构图，常见风格有 `Cinematic`、`live-action`、`2D-animated`、`3D CG`、`claymation`、`watercolor`、`vintage film`。每个细节都要对应可见或可听的内容。
- **镜头与切**：首镜不加时间戳；后续镜用递增的切镜时间，落在视频时长内，如 `[Shot 2] At 00:03.500, the camera cuts to...`。普通切用 `the camera cuts to` 等；仅距离或轻微角度变化时优先用运镜而非切镜。
- **运镜**：完整运镜 = 运动类型 + 幅度 + 速度，作为镜头内的自然英文动作写出，不要堆在句尾当标签。类型含 `Zoom In/Out`、`Push In/Pull Out`、`Pan Left/Right`、`Truck Left/Right`、`Tilt Up/Down`、`Pedestal Up/Down`、`Arc Shot`、`Tracking Shot`、`Static Shot`、`Shake Slightly/Strongly`、`POV`、`Roll Clockwise/Counterclockwise`；幅度用 `with small/large amplitude`；速度用 `at slow/fast speed`。
- **说话人、对白、歌唱**：用稳定 ID 如 `(S1)`、`(S2)`，多人同说用 `(S1,S2)`。人物首次出现时给出身份、年龄、性别、是否出镜、音高、音色、语速或口音；ID、动作、语气写在 `<d>` 外面，里面只放语言标签和原话，逐字保留、不翻译也不改写，如 `<d>[English] I get off at the next station.</d>`。画外音用 `says in an off-screen voiceover` 并紧接着说明对应角色嘴唇保持闭合。跨镜对白用 `<scenetrans>`，结尾被截断用 `<cutoff>`。
- **屏幕文字**：画面中真正可见的横幅、招牌、字幕、霓虹字用英文双引号原样保留，如 `A red neon sign reading "营业中" glows above the doorway.`
- **overall_soundscape**：1–4 句英文连续段落，汇总环境声、物理动作声、非语言人声（风、雨、交通、脚步、布料、撞击、呼吸、笑、喘息）；对白/歌唱/画面内乐已在描述里，不要重复；仅当用户要求全程静音时才写 `N/A`。
- **non_diegetic_music**：1–3 句英文，描述乐器、速度、节奏、动态变化，不用抽象情绪词；角色能听到的音乐属于画面内事件，应写进描述；没有就写 `N/A`。

## 5. Full-Reference 模式（六段式）

适用于带参考素材的重写，输出全部用英文，仅在 `<d>` 内和画面可见文字保留原文语言。完整输出按以下顺序六段：

| 段落 | 作用 |
| --- | --- |
| `subject_definitions` | 定义被引用的内容与引用标签 |
| `summary` | 概括任务类型、目标视频与主要引用关系 |
| `retention_analysis` | 描述引用内容如何被保留、转移或复用 |
| `detailed_description` | 按播放顺序描述画面、动作、镜头、声音、对白 |
| `overall_soundscape` | 汇总环境与物理声音 |
| `non_diegetic_music` | 描述只有观众能听到的背景音乐 |

引用标签四类：`<Subject N>`（可复用/可修改的可见内容）、`<Picture N>`（作为具体目标帧或构图锚点的参考图）、`<Video N>`（提供剪辑源、续写起点或整段时间结构的参考视频）、`<Audio N>`（被复制或引用的音频信号）。标签一旦分配，在六个段落中含义保持不变。`detailed_description` 生成任务一般 350–500 英文词；镜头格式、运镜、说话人 ID、`<d>`、`<scenetrans>`/`<cutoff>` 规则与基础指南一致。`summary` 用方括号任务类型前缀，如 `[reference generation]`、`[video editing + reference generation + audio reuse]`。关系标记：`fully_preserved`/`partially_preserved`/`attribute_transfer`/`weak_reference`（可见内容），`fully_copy`/`partially_copy`/`reference`/`weak_reference`（音频）。

## 6. 与 Seedance 的区别

H3 的这一套三段/六段英文结构、`<d>`/`<Subject N>`/`<Picture N>` 标签是 H3 专属的提示词组织方式，不是 Seedance 的通用格式，也不要把它当作 API JSON 的必填字段。Seedance 用自然语言描述期望画面，参考素材按角色逐一说明即可，见 [Seedance 2.0 提示词指南](seedance-2-prompts.md)。
