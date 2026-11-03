# MiniMax H3 提示词参考

先确认文生视频、首帧、首尾帧、尾帧或多素材参考模式，并核对秘塔当前模式和素材限制。分别描述主体、场景、动作发展、镜头和声音；将对白及画面文字保留原语言，明确每个素材的作用，避免只写抽象风格词。首帧或首尾帧任务要交代画面如何延续或过渡。

如果需要结构化 H3 提示词，可用英文组织 `integrated_multimodal_description`、`overall_soundscape` 和 `non_diegetic_music`；多素材参考可进一步使用 `subject_definitions`、`summary`、`retention_analysis` 和 `detailed_description`，再写声音和音乐。保持图片、视频、音频引用标识一致，内容时长与请求时长一致。这些是提示词组织方式，不是 API JSON 的必填字段，也不是 Seedance 的通用规则。

以 [MiniMax 视频生成文档](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create)和[秘塔页面](https://metaso.cn/minimax-h3)当前支持情况为准。
