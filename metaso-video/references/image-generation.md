# METASO H3 图片生成

核对日期：2026-11-18（重新核对秘塔图片文档及MiniMax官方模型卡）。依据[秘塔图片 API 文档](https://metaso.cn/minimax-h3/image-api-guide)。此处是秘塔接入规范；MiniMax 官方 API 其他字段不自动适用于秘塔。

## 提示词与编辑规则

秘塔请求规则来自下面的API文档；写作建议参照[MiniMax官方模型卡与文生/编辑示例](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image/blob/main/README.md)，以下模板是本技能的实用组织方式，不是模型硬性语法。

- 文生图写清主体、空间关系、构图、光线、材质和画风；有海报/文字需求时逐字列出文字、位置与层级，不用“好看、高级”替代具体画面。画幅用size参数决定，不只写在提示词里。
- 单图编辑明确以哪张图为基础、修改对象与范围、必须保留的外观/布局；多图编辑逐一指定 `<Picture N>` 的职责，例如图1是产品、图2只提供场景、图3只提供色调，不让多个素材同时争夺同一主体身份。
- 参考顺序依据reference_file_ids数组，不能用文件名或画布ID代替Picture编号。编辑要求不等于像素级不变保证；检查产品结构、人物身份、文字与布局是否真的保留。
- enhance_prompt默认开启；精确修改或排查增强偏离时可按用户要求关闭。查询的enhanced_prompt用于复核服务实际增强内容；不把H3视频的英文三段/六段、<d>对白或声音字段塞进图片提示词。
- MiniMax官方示例有自部署/官方API多图能力，秘塔仍只允许最多3图；不把官方multipart /v1/images/edits协议替换掉秘塔的file_id流程。

原创文生图示例：

```text
竖版产品海报，一只钴蓝色陶瓷杯放在画面下半部的浅灰石台上，杯口朝上，左侧柔光照亮釉面，背景为纯米白。上方保留宽阔留白，居中只写“慢下来”，深蓝色粗体字，杯子与文字互不遮挡。写实静物摄影，杯沿和把手结构清晰。
```

原创编辑示例：

```text
以 <Picture 1> 为基础，只把杯身颜色改成钴蓝色，保留杯子形状、把手、桌面、拍摄角度与光线。<Picture 2> 只提供蓝色参考，不采用其中的物品或背景。保留图1原有文字及其位置，不增加其他文字。
```

提交前核对文字原文、编辑/保持范围、素材顺序、尺寸和增强开关；完成后看实际画面，不能把返回PNG或尺寸正确当作编辑成功。

## 请求、额度与结果

- POST `https://metaso.cn/api/minimax/v2/image_generation`；Bearer 使用已有 H3 API Key。每任务一张 PNG，支持文生图、单图编辑、多图参考编辑。
- `model` 可省略，默认 `MiniMax-H3-Image`；`prompt` 必填，1–2000 字符。
- `size` 可省略，默认 `2560x1440`，格式为宽x高。宽高为正整数，面积 655360–20000000 像素、宽高比 1:3–3:1，含边界；无需擅加32整除限制。低于4194304像素时上游可能先用更大画布生成再缩放。
- `reference_file_ids` 可省略或空数组；最多3个字符串ID，按顺序对应提示词里的 `<Picture 1>`、`<Picture 2>`、`<Picture 3>`。不使用视频的 content、role 或 mm_file:// URL。
- `enhance_prompt` boolean，默认 true；false 使用原始提示词。查询返回的 `seed`、`enhanced_prompt` 是结果字段，文档未列为创建参数。不要擅自添加 n、seed、视频参数、aspect_ratio 或 area；后两项只在文档的 MiniMax 官方 API 说明中出现，秘塔当前请求字段表未列出。
- `Idempotency-Key` 请求头可用 UUID。同一次不确定提交重试必须复用键及原参数；更改参数复用旧键返回409。CLI提交前向stderr记录键，成功输出也保留；默认不会自动重试。
- 创建返回 `task_id`。GET `/v2/query/image_generation/{task_id}`；状态 queued/running/succeeded/failed，失败读 `task.error_message`。成功读 `task.content.url`、`file_id`、`filename`。历史结果可能是其他扩展名，不硬改为PNG。
- 下载签名URL不发送Bearer；过期但文件仍可用时重新查询取新链接。下载后核对实际格式、宽高及画面。
- 网页/API共用账号试用额度和UID并发；文档默认4并发，以账户配置为准，排队也占名额。402/image_trial_exhausted 表示额度用尽；429/image_concurrency_limit 表示并发满；503表示图片暂未开放。失败任务释放本次试用名额。不要用视频余额推断生图权限，不擅自购买或反复提交。

## 输出尺寸预设

API的默认横图2560x1440与网页2K横图预设2720x1536不同，应明确所选值。自定义尺寸在上述范围内也可用。

| 比例 | 1K | 2K | 4K |
|---|---|---|---|
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1376x768 | 2720x1536 | 5472x3072 |
| 9:16 | 768x1376 | 1536x2720 | 3072x5472 |
| 4:3 | 1184x896 | 2368x1760 | 4736x3552 |
| 3:4 | 896x1184 | 1760x2368 | 3552x4736 |
| 3:2 | 1248x832 | 2496x1664 | 5024x3360 |
| 2:3 | 832x1248 | 1664x2496 | 3360x5024 |
| 21:9 | 1568x672 | 3136x1344 | 6272x2688 |
| 3:1 | 1728x576 | 3552x1184 | 7104x2368 |
| 1:3 | 576x1728 | 1184x3552 | 2368x7104 |

## 素材和CLI

参考图支持 PNG/JPEG/WebP，每张<=30MiB；宽和高各256–5760px，比例0.4–2.5。输出允许的尺寸不代表可直接作为下一次参考图；重新核对素材限制。CLI只检查文件存在与请求结构，图像格式、像素、大小需另检。

上传复用 POST `/v1/files/upload`，multipart字段 `purpose=video_generation_input` 与 `file`（图片接口也使用这个purpose）。取得 `file.file_id`，CLI upload输出新增 `file_id`；不要把它的 `url` 字段放入 reference_file_ids。

```sh
python3 scripts/metaso.py upload /绝对路径/reference.png
# 用户授权上传后追加 --submit，记录返回的 file_id
python3 scripts/metaso.py image-create /绝对路径/image.json
# 按授权追加 --submit；可带 --idempotency-key UUID
python3 scripts/metaso.py image-status TASK_ID
python3 scripts/metaso.py image-download TASK_ID /绝对路径/result.png
```

预览不访问网络或消耗额度。任务ID对应的图片/视频查询路径不同，不混用status与image-status。

参考编辑请求（将示例ID替换成真实上传结果；文生图删掉reference_file_ids）：

```json
{
  "model": "MiniMax-H3-Image",
  "prompt": "保留 <Picture 1> 中产品的形状，参考 <Picture 2> 的暖色灯光，把产品放在木桌上。",
  "size": "2720x1536",
  "reference_file_ids": ["424010985738628", "424010985738627"],
  "enhance_prompt": true
}
```

## MiniMax Design 图片接入

先读[通用接入核对表](minimax-design-integration.md)。新增独立type=image模型，复用原供应商/凭据，upstreamModel=`MiniMax-H3-Image`；不覆盖已有H3视频模型。prompt required/maxLength=2000，image最多3、video/audio为0，单任务输出1。明确参考图的格式/像素/30MiB上限。

参数至少包括size（默认2560x1440，允许自定义）、enhance_prompt（boolean默认true）；若界面提供比例+分辨率档位，adapter按上表转换为唯一size，须说明自定义size与预设的优先关系，不同时发官方的aspect_ratio/area。应用界面不能表达的素材或跨字段限制由adapter校验。

adapter须上传本地参考图，保留顺序，使用原始file_id组装reference_file_ids；明确应用临时上传与供应商file_id不是同一个ID。为每个新任务建立并保存独立幂等键，在同任务重试时复用；不能在每次buildSubmit时无条件换键。parseSubmit读取task_id，buildPoll使用图片路径，parsePoll按上述状态解析URL与错误。下载不携带Bearer到其他域。

逐项离线检查文生、1图、3图、第4图拒绝、2001字符拒绝、竖图、自定义尺寸边界、关闭增强、默认值和失败状态。保存后读回spec/adapter并检查界面；未实际保存不得把文档更新说成Design已接入，未生成不得说线上验证完成。
