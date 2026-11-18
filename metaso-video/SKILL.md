---
name: metaso-video
description: 使用 METASO（metaso.cn）账号生成或编辑图片、生成视频、上传参考素材、将 H3 视频再生成 2K、查询余额或任务及下载结果时使用。
---

# METASO 图片与视频生成

使用 METASO 生成图片或视频；图片使用账号生图额度，视频使用 API 积分，与其他平台账号余额独立。脚本 `scripts/metaso.py` 仅依赖 Python 3 标准库。模型和限制可能变化，使用前查看 https://metaso.cn/minimax-h3 的当前 API 示例及报价。

## 首次配置密钥

预览请求不需要密钥。需要提交、查询或下载前，先检查用户是否已配置 `METASO_API_KEY` 或 `~/.config/metaso-video/credentials.json`，只检查是否存在，不读取或输出完整密钥。没有配置时，告诉用户在秘塔控制台获取自己的 API Key，并引导用户在自己的终端运行以下命令；不要让用户把密钥粘贴到聊天中：

```sh
python3 -c 'import getpass,json,os,pathlib; p=pathlib.Path.home()/".config/metaso-video/credentials.json"; p.parent.mkdir(mode=0o700,parents=True,exist_ok=True); k=getpass.getpass("METASO API Key: "); fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.write(fd,json.dumps({"api_key":k}).encode()); os.close(fd); print("凭据已保存")'
```

命令不会覆盖已有凭据；已有文件需要处理时由用户决定。不要把密钥放入项目、提示词、版本库或发往秘塔以外的站点。凭据失效时引导用户在秘塔控制台检查，不擅自新建、撤销或修改密钥和账号设置。已存在旧路径 `~/.config/metaso-h3/credentials.json` 的仍会被脚本读取作为回退，无需重新配置。

## 图片生成与编辑

图片任务先读[H3 Image提示词规则](references/minimax-h3-image-prompts.md)，再读[图片 API 参数、完整尺寸表和 Design 接入规则](references/image-generation.md)。支持 `MiniMax-H3-Image` 文生图、单图编辑和最多3图参考编辑，每任务一张图；提示词最多2000字符。图片请求使用 `prompt`、`size`、`reference_file_ids`、`enhance_prompt`，不套用下方视频参数。

`image-create request.json` 默认预览，用户授权消耗生图额度后加 `--submit`；`image-status TASK_ID` 查询，`image-download TASK_ID /绝对路径/result.png` 下载。上传复用 `upload`，将返回的 `file_id` 放入图片请求。默认图片尺寸2560x1440、增强开启；可自定义尺寸。创建时CLI记录幂等UUID，提交结果未知时保留原参数和键，先查账户任务再决定重试；不自动重复消耗额度。

## 模型与请求

| 模型 | 请求中的 `model` | 分辨率 | 时长 |
|---|---|---|---|
| MiniMax H3 | `MiniMax-H3` | `480p`、`512p`、`768P`、`1080p`、`2K` | 4–30 整数秒；2K 最长 15 秒 |
| Seedance 2.0 Mini | `seedance-2.0-mini` | `480p`、`720p` | 4–15 整数秒 |
| Seedance 2.0 Fast | `seedance-2.0-fast` | `480p`、`720p` | 4–15 整数秒 |
| Seedance 2.0 标准版 | `seedance-2.0` | `480p`、`720p`、`1080p`、`4k` | 4–15 整数秒 |
| Seedance 2.5 | `seedance-2.5` | `480p`、`720p`、`1080p` | 4–30 整数秒 |

秘塔实时模型配置可能有变化，以页面和服务校验为准。以上来自模型配置接口，页面可见选项可能不同（例如 H3 512p）；脚本仅做基础验证。H3 的 `fast_mode`、`context_ir_enabled` 不套用到 Seedance。写提示词或准备参考素材前，按下表读取相应规则；先区分任务类型，再组装参数，不能只看分辨率和数量。核对秘塔当前 API 示例的 `content` 类型、`role` 和素材限制；普通参考图不能当作首帧。

### 生成规则索引（2026-11-18核对）

| 模型 | 必读规则 | 覆盖与边界 |
|---|---|---|
| MiniMax H3 视频 | [H3指南](references/minimax-h3-prompts.md) | 文生、首帧、尾帧、首尾帧、全参考；镜头、对白与声音格式；不是JSON必填字段 |
| Seedance 2.0 标准版 | [2.0系列指南](references/seedance-2-prompts.md) | 主体绑定、分镜、动作、声音；模型方编辑/延长与秘塔接入分开核验 |
| Seedance 2.0 Mini | [2.0系列指南](references/seedance-2-prompts.md) | 共用写作方法，使用Mini自己的参数限制 |
| Seedance 2.0 Fast | [2.0系列指南](references/seedance-2-prompts.md) | 共用写作方法，使用Fast自己的参数限制；不推断效果或功能完全相同 |
| Seedance 2.5 | [2.5独立指南](references/seedance-2.5-prompts.md) | 时间戳、素材职责、长片段、编辑/延长参数锁定；秘塔未验证能力明确标注 |
| MiniMax H3 Image | [提示词指南](references/minimax-h3-image-prompts.md) + [图片API](references/image-generation.md) | 英文最终描述与增强流程、文生/编辑保留关系、文字与构图；不套H3视频格式 |

这些规则分别记录模型方写法、秘塔参数与已验证范围。`create`只做基础JSON校验，不验证故事逻辑、素材像素、角色组合或所有提示词规则；通过dry-run不代表这些规则都已检查。具体参数仍以当前秘塔配置和示例为准。

### 画幅与接入参数

在 MiniMax Design 中新增、修改或排查模型接入时，先读 [Design 完整接入核对表](references/minimax-design-integration.md)。该表区分应用配置、秘塔请求字段和尚未验证的能力，不能只照模型与分辨率表填写。

- 秘塔视频页面列出固定画幅 `21:9`、`16:9`、`4:3`、`1:1`、`3:4`、`9:16`；火山方舟的视频生成文档也列出这些值及 `adaptive`。这是页面与模型方文档的证据，并非每个秘塔模型和素材组合均已实测。根据当前秘塔示例及服务校验确认适用性，不可把第三方参数直接当作秘塔保证。
- 秘塔 API 请求字段是 `ratio`。若接入应用使用 `aspect_ratio` 命名，适配器须将所选值传到 `ratio`；仅给界面添加选项不足以证明请求生效。对文生、普通参考、首帧和首尾帧分别检查实际请求，保留 `adaptive` 跟随素材与固定比例的区别。秘塔 H3 首尾帧混合示例使用 `adaptive`；这不证明所有图生模式必须强制使用它。
- 生成请求的核心参数为 `model`、`content`、`resolution`、`duration`、`ratio`。`content` 的素材类型与角色见下文；H3 可用 `fast_mode` 控制优先通道，`context_ir_enabled` 可覆盖控制台 H3 Context IR 设置，省略时沿用账户设置并可能收费。Seedance 不传 H3 专属开关。按当前秘塔示例核对水印、回调及其模型限制；不要把生成数量误当作单个任务参数。
- 修改第三方自定义模型后，分别核验默认值、可选值、模式约束和组装后的请求，例如 `9:16`、`1:1`；保留原供应商、凭据和参考模式。离线检查、界面显示、线上实际生成分别报告，未验证不得声称已生效。

Seedance Mini 文生视频示例，标准版将 `model` 改为 `seedance-2.0`：

```json
{
  "model": "seedance-2.0-mini",
  "content": [{"type": "text", "text": "雨夜街道，一只橘猫缓步走过，镜头低位跟随，雨声清晰。"}],
  "resolution": "480p",
  "duration": 4,
  "ratio": "16:9"
}
```

## 调用

1. 根据用户要求确认模型、素材方式、时长、分辨率和数量，准备 JSON；在技能目录运行 `python3 scripts/metaso.py create /绝对路径/request.json`。这是不需密钥的预览，仅检查基础参数，不提交。
2. 生成会扣 METASO 积分；确认当前报价，在用户已授权的消费范围内追加 `--submit` 提交一条任务。仅配置接入时不自行生成收费测试视频。
3. 立即记录实际返回的 `task_id`。HTTP 超时后提交结果未知，先到网页请求管理核查，不能直接重复创建。
4. 用 `python3 scripts/metaso.py status TASK_ID` 查询；网页示例使用 `task.status` 和 `task.content.url`。约每 15 秒查询并向用户更新；30 分钟无结果时保留任务 ID 并说明情况。
5. 用 `python3 scripts/metaso.py download TASK_ID /绝对路径/result.mp4` 保存，不覆盖已有文件。检查视频时长、分辨率和实际画面；下载完成和画面符合要求分别说明。

脚本可发送文档规定的完整 JSON。图片、视频、音频素材可使用 API 支持的 URL 或上传后的 `mm_file://`；先确认用户授权将指定文件发送至秘塔。模型配置列出 H3 和 Seedance 2.0 系列最多 9 张图、3 段视频、3 段音频，Seedance 2.5 最多 30 张图、10 段视频、10 段音频；具体组合与时长限制仍须核对当前 API 示例。提示词优化、参考视频及额外图片可能产生费用，按当前报价核对。

## 素材上传和余额

`python3 scripts/metaso.py upload /绝对路径/素材.png` 只预览本地文件信息；确认用户同意把该文件上传秘塔后加 `--submit`，返回的 `url` 可填入 `content` 相应的 `image_url.url`、`video_url.url` 或 `audio_url.url`。上传实现参照秘塔发布的 ComfyUI 节点，尚未对每种模型和素材格式实测；请勿输出文件内容或凭据。

`python3 scripts/metaso.py balance` 查询 API Key 所属账户积分；同一账户串行查询。余额不是任务报价。

H3 的素材项示例：首帧用 `{"type":"image_url","image_url":{"url":"素材URL"},"role":"first_frame"}`，尾帧的 role 为 `last_frame`；普通参考素材分别使用 `reference_image`、`reference_video`、`reference_audio`，类型和 URL 字段分别为 `image_url`、`video_url`、`audio_url`。官网还列出首尾帧与参考图混合示例。其他模型及素材组合必须先核对官网 API 示例，勿推断完全兼容。

秘塔当前 API 的图生视频示例中，Seedance 2.0 Mini、Fast、标准版和 Seedance 2.5 也将图片设为 `role: "first_frame"`，不能误发为 `reference_image`。这些示例仅证明首帧请求格式；尾帧、首尾帧及其混合组合要逐模型另行核实。脚本透传 `content`，不会自动从素材顺序判断帧角色。接入 MiniMax Design 等应用时，技能文档不会自动修改其自定义模型适配器：须逐模型检查模式选择、实际 `role` 映射、参数及请求预览，并明确区分离线检查与真实生成。

## H3 视频再生成 2K

- `python3 scripts/metaso.py regenerate --task-id 任务ID` 预览；授权费用后加 `--submit` 创建任务。秘塔示例说明该方式需要白名单，源任务必须属于当前账户、状态为 `succeeded` 且在 7 天查询窗口内。
- 源视频方式：准备 JSON，包含 `model: "MiniMax-H3"`、`resolution: "2K"` 和 `content`。`content` 必须原样包含源视频生成时最终提示词、全部原始素材，并且恰好包含一个 `type: "video_url"`、`role: "base_video"` 的源视频项。用 `python3 scripts/metaso.py regenerate --request /绝对路径/request.json` 预览，再按授权加 `--submit`。可选 `callback_url`、`aigc_watermark`。不得同时提供 `source_task_id` 和 `content`。
- 源视频必须符合 H3 768P 输出规格：有音轨、24 fps、宽高均可被 32 整除、像素面积介于 768×768 和 768×1344；总帧数 107–362，按 17 帧递增；请求体不超过 64 MB。它不是任意视频的通用超分。脚本只检查基础结构，无法确认源任务归属、白名单、视频规格或原始素材完整性。
- 创建后使用原有 `status` 和 `download` 命令。当前网页标示标准通道输出参考价 6.80 积分/秒，原素材可能另收费；提交前核对当前报价。再生成和上传均尚未用真实任务实测。

## 文档与边界

- [秘塔页面与 API 示例](https://metaso.cn/minimax-h3)
- [秘塔模型实时配置](https://metaso.cn/api/video-generation/models)
- [秘塔 ComfyUI API 节点（含上传接口）](https://github.com/meta-sota/ComfyUI-MiniMaxH3-API)
- [MiniMax H3 视频再生成 API](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-regeneration)
- [MiniMax H3 提示词基础指南（官方）](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
- [MiniMax H3 提示词参考指南（官方）](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
- [Seedance 2.0 系列 API 教程](https://console.volcengine.com/ark/region:cn-beijing/docs/seedance-2-0)
- [Seedance 2.0 系列提示词指南（火山方舟官方，首选）](https://docs.volcengine.com/docs/ark/seedance-2-0-prompt-guide?lang=zh)
- [Seedance 2.5 官方提示词指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh)
- [Seedance 2.5 小云雀官方教程](https://xyq.jianying.com/tutorials/seedance-2-5-prompt-guide)
- [Seedance 2.0 创作指南（Runway，可作补充参考）](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2.0)
- [Seedance 2.0 官方介绍](https://seed.bytedance.com/en/seedance2_0)
- [MiniMax 多模态请求规范](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create)
- API 地址固定为 `https://metaso.cn/api/minimax`；网页内部接口与公开 API 不是同一套协议。

Seedance 接口依据秘塔公开网页示例及模型配置编写；新增 Fast、2.5 和 H3 512p 配置尚未以付费生成实测，不能据模型列表推断素材角色或请求协议完全相同。遇到服务报错应保留原始信息并核对当前文档，不猜测重试。
