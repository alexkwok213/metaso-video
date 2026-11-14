# MiniMax Design 接入核对表

依据 2026-11-14 本机 Design 随应用打包的自定义模型 setup guide、模型输入 schema，以及秘塔页面/API 示例整理。Design 版本更新后先重新读取 `design.media-models/get_setup_guide`、`get_settings`、`get_model`；本文件不是应用所有未来字段的保证。秘塔模型参数以 https://metaso.cn/minimax-h3 和 https://metaso.cn/api/video-generation/models 为准。

## 1. 三层必须分别填写

技能是 agent 的操作说明；Design 的 spec 决定可选输入；adapter 决定实际发送内容。修改文档不会自动更新 spec 或 adapter。可选项出现、离线请求正确和真实生成成功分别验收。

| 配置层 | 可填写内容 | METASO 接入要求 |
|---|---|---|
| 供应商 | 名称、类型、base URL、认证/固定/动态 headers、并发、签名字段、资产库 | 复用现有供应商；base URL 为 `https://metaso.cn/api/minimax`；Bearer key 由用户通过密钥卡或设置输入。没有公开限制时不编造并发值，也不添加无依据的 headers、签名或资产库 |
| 模型身份 | name、type、provider、upstreamModel、enabled | type=`video`；展示名称与请求 model 分开；upstreamModel 使用主技能表里的精确 ID；编辑保留原 ID 和供应商 |
| 规格来源 | preset 或 own spec；builtin 或 own adapter | 先比对内置适配器。秘塔的模型/时长/参数与预设不同则不能直接沿用预设限制；自有适配器须有可读源码 |
| 提示词 | prompt.use=`required/optional/none`、maxLength | 视频描述使用 required。长度上限需按模型/API 确认；网页编辑器显示 10000 不足以证明每个上游模型均接受此长度，不设猜测上限 |
| 素材 | image/video/audio 各自 min/max、references.maxMB、description | 主技能列出的服务数量上限与 Design 自身上限取较小值。`maxMB` 是应用通用字段；秘塔单视频 50MiB 不能无依据套作所有图片/音频的共同限制 |
| 参数 | key、type、title、description、enum、default、min/max、step、required | 类型为 string/number/integer/boolean；时长 integer、step=1；默认必须落在允许范围。title/description 写明中文含义、模式行为及额外费用 |
| 使用指南 | guide（Markdown） | 写明提示词、素材顺序、每种 mode 的角色与数量、画幅覆盖、模型限制、未验证项；guide 是 spec 同级字段，不放到 spec 内 |
| 任务调度 | pollIntervalSec、timeoutMin、outputsPerTask | Design 接受轮询 1–60 秒、超时 1–180 分钟、单任务输出 1–16。建议轮询 15 秒、超时 30 分钟；单个秘塔视频任务按一个结果处理，不把画布批量数量写成 outputsPerTask |
| 资产组 | 跟随供应商、显式无组、指定模型自己的组 | 仅在服务要求且适配器支持资产库时配置。编辑须保留已有资产选择；省略可能恢复跟随供应商，不能当作“不修改” |

## 2. 参数映射与模式

| Design 输入 | 秘塔实际字段/行为 | 注意 |
|---|---|---|
| upstreamModel | body.model | 五款分别处理，不用展示名称代替 |
| prompt | content 中 type=text 的 text | 原样保留用户要求的对白和文字 |
| resolution | body.resolution | 大小写按主技能表；H3 512p 仅配置接口列出，报价未确认 |
| duration | body.duration | H3 非2K、2.5 为4–30秒；H3 2K及2.0系列为4–15秒。跨参数限制须在 adapter 检查，不能仅用通用 max=30 |
| aspect_ratio | body.ratio | 固定值21:9、16:9、4:3、1:1、3:4、9:16；默认16:9。adaptive 另核对任务模式。不能硬编码覆盖选择后仍声称支持 |
| mode | 本地选择 content.role，不直接当作秘塔同名参数发送 | 同样两张图可作首尾帧或两张普通参考，故需要明确模式；无素材的 reference 可用于文生视频 |
| 图片/视频/音频 | image_url/video_url/audio_url 对象及其 role | 普通素材用 reference_image/reference_video/reference_audio；首帧用 first_frame，尾帧用 last_frame。图片顺序不得擅自重排 |
| fast_mode（H3） | body.fast_mode | 秘塔示例表示优先通道；会影响费用，默认不开启；不要把 Seedance Fast 的模型名误认为该开关 |
| context_ir_enabled（H3） | body.context_ir_enabled | boolean；省略沿用秘塔控制台，可能收费。显式 false 才是关闭；若要提供跟随/开/关三态，adapter 应分别省略/true/false |

H3 可区分普通参考、仅首帧、仅尾帧、首尾帧；官网还有首尾帧加参考图混合示例。当前本机 H3 适配器在帧模式固定使用 adaptive，且不接受额外参考素材，这是当前适配选择，并非证明秘塔强制如此。界面枚举显示英文时不得只凭标题判断请求角色。

四款 Seedance 的秘塔图生示例已确认 first_frame。当前本机只接入普通参考和首帧；未接入尾帧/首尾帧不等于服务端不支持。模型方文档的能力还须与秘塔接口逐项核对；不应将“未验证”写成“不支持”。

水印、回调、随机种子、原生音频开关等字段，只有当前秘塔对应模型文档明确规定时才暴露，逐项记录类型、默认和作用。Seedance 示例要求 aigc_watermark 省略或 false；H3 再生成示例列出 callback_url、aigc_watermark。这些证据不能直接推广到所有创建请求。未查到的默认值不要自行补写。

## 3. 适配器与错误处理

- `apiVersion=1`；buildSubmit 组装请求，parseSubmit 读取 task_id；buildPoll 使用 `/v2/query/video_generation/{task_id}`；parsePoll 处理 succeeded、failed、cancelled。读取 base_resp 和 error，不把失败当作持续运行。
- succeeded 时读取 task.content.url；缺失地址须报错。授权只发给供应商域名，不向结果 CDN 转发密钥。服务需要认证获取结果时按 Design 的 fetch 输出契约实现，不手工拼接密钥 URL。
- 超时或网络中断后任务可能已创建；保存已知 task_id，不自动重新提交收费任务。恢复时先查原任务；生成失败时先读 get_model.recentFailures 和 modelRevision，不能猜原因。
- 超过模型时长、错误角色/数量、混用不支持素材时在提交前报错。素材 fps、总时长、尺寸、编码和体积若不能离线确认，写明需额外检查，不能用数量校验冒充完整验证。

## 4. 保存与验收

1. 读取完整旧配置，保留所有未改字段、资产选择和 revision；编辑用真实 expectedRevision。不要直接改应用内部配置文件来代替保存和运行验收。
2. 每个模型单独运行 check_adapter，传 spec/type/upstream_model/provider_id；检查 samples、poll、unreadParams、providerIssues。共用源码也须逐模型检查。
3. 默认 samples 未必覆盖非默认 mode；额外覆盖：文生、普通参考、首帧、尾帧/首尾帧（已接入时）、9:16、1:1、H3 2K 15秒通过及16秒拒绝。检查 body 内容，而非只看 ok:true。
4. 保存后 get_model 和 capability_get 读回；再检查画布选项。模式标签、默认值和请求字段一致才算配置验收。
5. 报告：已保存、离线已检验的组合、尚未线上验证的组合。收费实测须按用户授权执行；不能为了接入测试自行生成。

## 5. 功能覆盖记录

接入 agent 应逐模型记录“官方证据 / spec已暴露 / adapter已映射 / 离线已验 / 线上已验”，不得仅写“全部支持”。至少覆盖：模型与分辨率、画幅、时长、素材角色和组合、各素材限制、费用开关、水印/回调、轮询/失败/下载。

`regenerate`、`upload`、`balance` 是本技能独立 CLI 功能；现有 Design 五个生成模型的 buildSubmit 仍调用 video_generation，不自动获得这三个能力。Design 自带 H3 超分工具也不能据名称断言适用于秘塔自定义任务。要在 Design 接入再生成，须另核实工具/适配器如何传原任务或源视频及原素材，并保留白名单与源视频限制。
