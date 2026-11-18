# METASO 图片与视频生成技能

使用自己的秘塔 METASO API 余额，通过支持技能的 AI 助手调用 MiniMax H3、Seedance 2.0 Mini、Fast、标准版和 Seedance 2.5 生成视频、查询任务并下载结果。脚本默认预览请求，只有明确提交才创建付费任务。

新增 **MiniMax-H3-Image**：文生图、单图编辑、最多三图参考编辑、自定义尺寸、提示词增强、幂等提交、任务查询与图片下载。完整参数及十种比例的1K/2K/4K尺寸见[图片接入说明](metaso-video/references/image-generation.md)。图片使用账号生图额度，与视频积分区分；默认预览，尚未真实生成实测。

## 安装

[下载技能 ZIP](packages/metaso-video.zip)，解压后将 `metaso-video` 文件夹放入 AI 助手的技能目录。也可以让支持 GitHub 安装技能的助手安装本仓库中的 `metaso-video` 目录。

需要 Python 3、自己的 METASO API Key 和可用的 METASO 余额。凭据配置与调用方法见[技能说明](metaso-video/SKILL.md)，请勿将密钥提交到仓库。

## 使用

在支持技能的助手中说：

> 使用 $metaso-video，帮我准备一段 4 秒、768P 的视频请求，先预览参数。

确认模型、素材、时长、分辨率、数量与费用后，再按需要提交。生成费用以秘塔当前页面及账户实际扣费为准。

Seedance 接口根据秘塔公开 API 示例及模型配置接入；新增模型和 H3 512p 尚未进行付费生成实测。支持的模型参数和提示词规则见[技能说明](metaso-video/SKILL.md)。提交、查询或下载时如未配置 API Key，助手会引导用户在本机配置，无需把密钥发到聊天中；预览无需密钥。

脚本支持上传本地素材、查询余额，以及按源任务 ID 或源视频再生成 H3 2K。上传默认预览，再生成默认预览；实际上传需用户授权，生成和再生成需在用户授权的费用范围内提交。再生成、上传及新增模型尚未真实任务实测，限制和命令见[技能说明](metaso-video/SKILL.md)。

## 各模型生成规则

2026-11-18已核对六款已接入模型；参数与写作规则分开记录，未实测能力不标为已接入：

| 模型 | 规则 |
|---|---|
| MiniMax H3 视频 | [文生/首尾帧/全参考、镜头与声音](metaso-video/references/minimax-h3-prompts.md) |
| Seedance 2.0 标准版、Mini、Fast | [共用写作方法与逐款参数边界](metaso-video/references/seedance-2-prompts.md) |
| Seedance 2.5 | [独立指南：时间戳、任务锁定、素材映射与编辑/延长门槛](metaso-video/references/seedance-2.5-prompts.md) |
| MiniMax H3 Image | [文生图、编辑、文字与构图、尺寸及素材限制](metaso-video/references/image-generation.md) |

完整索引在[主技能](metaso-video/SKILL.md)。模型方能力不等于秘塔已开放；例如2.5严格编辑所需的自动时长目前不在CLI已支持范围。文档更新不会自动修改MiniMax Design中已保存的模型guide或adapter。

## 许可证

本仓库暂未提供许可证。
