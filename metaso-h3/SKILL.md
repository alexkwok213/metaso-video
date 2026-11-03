---
name: metaso-h3
description: 使用用户的 METASO（metaso.cn）账号调用 MiniMax H3 生成视频、查询任务和下载结果。用户提到用秘塔 H3、METASO 生成视频或查询其生成进度时使用。
---

# METASO H3

使用 METASO 的 API 余额生成视频。此服务与 MiniMax 官方账号余额独立。
凭据通过环境变量 `METASO_API_KEY` 或用户自行配置的 `~/.config/metaso-h3/credentials.json` 提供，JSON 格式为 `{"api_key":"你的密钥"}`；凭据文件仅限本人读取（权限 0600）。不要读取或输出完整密钥，不要将凭据放入项目、提示词或版本库。

## 调用

脚本路径以本技能目录为根：`scripts/metaso.py`。仅依赖 Python 标准库。

1. 按用户要求准备 JSON 请求，先运行 `python3 scripts/metaso.py create /绝对路径/request.json` 检查请求。此命令默认预览，不提交。
2. 生成会扣除 METASO 积分。明确用户需要的模型、素材方式、时长、分辨率和数量；在用户已授权的消费范围内，追加 `--submit` 提交一条任务。仅要求配置接入时，不自行生成收费测试视频。
3. 立即记录接口返回的真实 `task_id`，避免超时后重复提交收费任务。HTTP 超时结果未知时先到网页请求管理核查，不能直接重试创建。
4. 用 `python3 scripts/metaso.py status TASK_ID` 查询任务。以 `task.status` 和 `task.content.url` 判断进度；间隔约 15 秒查询，等待期间向用户更新。30 分钟仍无结果则保留任务 ID 并说明情况。
5. 用 `python3 scripts/metaso.py download TASK_ID /绝对路径/result.mp4` 保存结果，不覆盖已有文件。检查视频时长、分辨率和实际画面后交付；下载完成和画面符合要求分别说明。

最小文生视频请求：

```json
{
  "model": "MiniMax-H3",
  "content": [{"type": "text", "text": "用户确认的视频描述"}],
  "resolution": "768P",
  "duration": 4,
  "ratio": "16:9",
  "fast_mode": false,
  "context_ir_enabled": false
}
```

支持分辨率 `480p`、`768P`、`1080p`、`2K`。时长为 4–30 整数秒，2K 最长 15 秒。超过 15 秒或优先通道会影响费用。Context IR 是额外付费优化，示例明确关闭；根据用户要求选择。

图片、视频和音频参考：先阅读当前 API 文档的 content 类型、role 和素材限制，再构造请求，不能把普通参考图当首帧。脚本可直接发送文档规定的完整 JSON。公开 URL、`mm_file://` 或文档允许的 data URI 可以用于素材；本脚本没有实现独立文件上传。最多 9 张图片、3 个视频、3 段音频，视频与音频分别合计不超过 15 秒；以当前服务校验为准。

## 文档与复核

- METASO 页面及 API 示例：https://metaso.cn/minimax-h3
- 提供方示例客户端：https://github.com/meta-sota/ComfyUI-MiniMaxH3-API/blob/main/api_client.py
- 当前多模态请求规范：https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create
- 实际调用域名固定为 `https://metaso.cn/api/minimax`。不能把 METASO 凭据发送到 MiniMax 官方域名或其他站点。

若凭据失效，用 Tabbit 打开用户已登录的 METASO 控制台→请求管理。复用已有密钥；不擅自新建、撤销或更改账号设置。仅在内存中读取密钥并直接写入权限为 0600 的本机凭据文件，不回显密钥。账号密码和短信验证由用户在浏览器完成。
