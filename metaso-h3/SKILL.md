---
name: metaso-h3
description: 使用用户的 METASO（metaso.cn）账号调用 MiniMax H3、Seedance 2.0 Mini 或 Seedance 2.0 标准版生成视频、查询任务和下载结果时使用。
---

# METASO 视频生成

使用 METASO 的 API 余额生成视频，与其他平台账号余额独立。脚本 `scripts/metaso.py` 仅依赖 Python 3 标准库。模型和限制可能变化，使用前查看 https://metaso.cn/minimax-h3 的当前 API 示例及报价。

## 首次配置密钥

预览请求不需要密钥。需要提交、查询或下载前，先检查用户是否已配置 `METASO_API_KEY` 或 `~/.config/metaso-h3/credentials.json`，只检查是否存在，不读取或输出完整密钥。没有配置时，告诉用户在秘塔控制台获取自己的 API Key，并引导用户在自己的终端运行以下命令；不要让用户把密钥粘贴到聊天中：

```sh
python3 -c 'import getpass,json,os,pathlib; p=pathlib.Path.home()/".config/metaso-h3/credentials.json"; p.parent.mkdir(mode=0o700,parents=True,exist_ok=True); k=getpass.getpass("METASO API Key: "); fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.write(fd,json.dumps({"api_key":k}).encode()); os.close(fd); print("凭据已保存")'
```

命令不会覆盖已有凭据；已有文件需要处理时由用户决定。不要把密钥放入项目、提示词、版本库或发往秘塔以外的站点。凭据失效时引导用户在秘塔控制台检查，不擅自新建、撤销或修改密钥和账号设置。

## 模型与请求

| 模型 | 请求中的 `model` | 分辨率 | 时长 |
|---|---|---|---|
| MiniMax H3 | `MiniMax-H3` | `480p`、`768P`、`1080p`、`2K` | 4–30 整数秒；2K 最长 15 秒 |
| Seedance 2.0 Mini | `seedance-2.0-mini` | `480p`、`720p` | 4–15 整数秒 |
| Seedance 2.0 标准版 | `seedance-2.0` | `480p`、`720p`、`1080p`、`4k` | 4–15 整数秒 |

秘塔实时模型配置可能有变化，以页面和服务校验为准。以上是脚本当前允许的配置，并非完整参数验证。H3 的 `fast_mode`、`context_ir_enabled` 不套用到 Seedance。素材方式和模型提示词分别按需读取 [H3 规则](references/minimax-h3-prompts.md) 或 [Seedance 规则](references/seedance-2-prompts.md)，并核对秘塔当前 API 示例的 `content` 类型、`role` 和素材限制；普通参考图不能当作首帧。

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

脚本可发送文档规定的完整 JSON，支持文档允许的素材 URL；没有独立文件上传功能。素材数量、有效 URL、参考素材费用及组合限制以秘塔当前页面为准。网页模型配置列出最多 9 张图、3 段视频、3 段音频；提示词优化、参考视频及额外图片可能产生费用，按当前报价核对。

## 文档与边界

- [秘塔页面与 API 示例](https://metaso.cn/minimax-h3)
- [秘塔模型实时配置](https://metaso.cn/api/video-generation/models)
- [MiniMax H3 提示词基础指南（官方）](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
- [MiniMax H3 提示词参考指南（官方）](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
- [Seedance 2.0 创作指南（Runway，提示词写法最具体）](https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2.0)
- [Seedance 2.0 官方介绍](https://seed.bytedance.com/en/seedance2_0)
- [MiniMax 多模态请求规范](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create)
- API 地址固定为 `https://metaso.cn/api/minimax`；网页内部接口与公开 API 不是同一套协议。

Seedance 接口依据秘塔公开网页示例及模型配置编写，未以付费生成实测；遇到服务报错应保留原始信息并核对当前文档，不猜测重试。
