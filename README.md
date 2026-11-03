# METASO 视频生成技能

使用自己的秘塔 METASO API 余额，通过支持技能的 AI 助手调用 MiniMax H3、Seedance 2.0 Mini 和 Seedance 2.0 标准版生成视频、查询任务并下载结果。脚本默认预览请求，只有明确提交才创建付费任务。

## 安装

[下载技能 ZIP](packages/metaso-video.zip)，解压后将 `metaso-video` 文件夹放入 AI 助手的技能目录。也可以让支持 GitHub 安装技能的助手安装本仓库中的 `metaso-video` 目录。

需要 Python 3、自己的 METASO API Key 和可用的 METASO 余额。凭据配置与调用方法见[技能说明](metaso-video/SKILL.md)，请勿将密钥提交到仓库。

## 使用

在支持技能的助手中说：

> 使用 $metaso-video，帮我准备一段 4 秒、768P 的视频请求，先预览参数。

确认模型、素材、时长、分辨率、数量与费用后，再按需要提交。生成费用以秘塔当前页面及账户实际扣费为准。

Seedance 2.0 的接口根据秘塔公开 API 示例接入；尚未进行付费生成实测。支持的模型参数和提示词规则见[技能说明](metaso-video/SKILL.md)。提交、查询或下载时如未配置 API Key，助手会引导用户在本机配置，无需把密钥发到聊天中；预览无需密钥。

脚本支持提供符合 API 文档的素材 URL，但不提供独立文件上传。详细参数、任务查询和下载命令见[技能说明](metaso-video/SKILL.md)。

## 许可证

本仓库暂未提供许可证。
