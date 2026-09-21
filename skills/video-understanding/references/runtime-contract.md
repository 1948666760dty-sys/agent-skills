# Video Understanding Runtime Contract v0.1.1

## 1. 目的

本文件描述当前已经写入仓库的参考 Runtime 与 Video Understanding Skill 之间的真实接口。

目标用户体验：

```text
用户只发送 B站/YouTube URL
→ 宿主自动调用工具
→ 宿主内部处理长任务和回看
→ 当前聊天返回最终理解
```

用户不得被要求操作 job_id、轮询、下载器或帧文件。

## 2. 当前 Runtime

路径：

`skills/video-understanding/runtime/`

MCP transport：
- Streamable HTTP
- 默认本地地址：`127.0.0.1:8765/mcp`
- ChatGPT 不能直接连接 localhost；实际接入需 Secure MCP Tunnel 或远程部署。

当前工具均按 read/fetch 语义设计，不修改源平台内容。

## 3. Tool Contract

### 3.1 start_video_analysis

输入：

```json
{
  "url": "Bilibili or YouTube URL",
  "mode": "deep",
  "include_audience": false,
  "force": false
}
```

输出初始 `job_id` 与 `running`。

宿主必须自己保存 job_id，不得要求用户复制或再次输入。

### 3.2 wait_video_analysis

输入：
- job_id
- wait_seconds（0–30）

若仍在运行，宿主继续内部调用。

若 complete，返回 `session_id` 等 prepare 结果。

若 failed，返回明确 error code/message。

### 3.3 get_video_manifest

输入：
- session_id

返回：
- 平台；
- canonical id/url；
- 标题/作者；
- 时长；
- transcript source；
- visual readiness；
- frame count；
- warnings。

### 3.4 get_video_transcript

输入：
- session_id；
- start_seconds；
- end_seconds；
- max_chars。

长视频应按时间窗口分页读取，不必一次把整个字幕塞入上下文。

### 3.5 inspect_video_window

输入：
- session_id；
- start_seconds；
- end_seconds；
- max_frames（Runtime 上限 20）；
- density = overview | dense。

输出为混合 MCP content blocks：
- 时间戳 TextContent；
- 实际 JPEG ImageContent。

`overview`：用于第一遍全局粗看。

`dense`：用于重点区间二次回看。

## 4. 推荐宿主执行顺序

```text
start_video_analysis
→ wait_video_analysis until complete
→ get_video_manifest
→ get_video_transcript in windows
→ inspect_video_window overview
→ model identifies 1..N important/uncertain intervals
→ inspect_video_window dense for those intervals
→ final synthesis
```

Quick 模式可跳过视觉或减少视觉调用。

Deep 模式不能在 visual_ready=true 时完全忽略视觉证据。

## 5. Bilibili Adapter

参考 Runtime vendoring 了：

AntaresGG/BiliBiliVideoParser 的 Bilibili-native extractor（MIT）。

负责：
- b23.tv；
- BV/av；
- ep/ss；
- 分P元数据；
- 官方字幕；
- AI字幕；
- 可选弹幕信号。

MIT 原许可保存在 Runtime vendor 目录。

## 6. YouTube Adapter

当前使用 yt-dlp：
- watch URL；
- youtu.be；
- Shorts；
- metadata；
- manual subtitles；
- automatic captions。

字幕优先级仍由 Skill 解释：
人工 > 平台自动 > ASR。

## 7. ASR

当无可用字幕：
- 下载 audio-only；
- 使用本地 faster-whisper；
- 默认 model = small；
- 默认 device = auto；
- auto 先尝试 CUDA，失败再回退 CPU int8。

环境变量：
- VIDEO_WHISPER_MODEL
- VIDEO_WHISPER_DEVICE

不得把 CUDA 尝试失败隐藏成“GPU 已成功运行”。

## 8. Visual Pipeline

Deep：
- 下载不高于约 720p 的 video-only stream（可用时）；
- 每 3 秒做一次场景差异 probe；
- 每 12 秒保底一个 baseline；
- scene-aware 候选与 baseline 合并；
- 最多保留约 600 个 overview frame record；
- 保存为最大宽度约 960px 的 JPEG。

第一次视觉理解由宿主调用 overview。

第二次回看由宿主根据第一次结果决定时间窗，再调用 dense。

## 9. OCR

v0.1：
- Runtime 不要求 PaddleOCR/Tesseract；
- 通过 `inspect_video_window` 把真实帧发给宿主 ChatGPT；
- OCR/图表/参数/代码阅读由宿主视觉能力完成；
- manifest 中标记 `ocr = host_vision`。

未来可增加本地 OCR，但不能在未执行时标记 local OCR success。

## 10. Cache

默认：

`~/.video-understanding/<session_id>/`

缓存：
- manifest；
- transcript；
- video-only；
- scene frames；
- dense rewatch frames；
- 必要时 audio。

Follow-up 应复用 session/cache。

## 11. 错误码

至少：
- UNSUPPORTED_URL
- VIDEO_NOT_FOUND
- AUTH_REQUIRED（后续登录路径）
- MEDIA_DOWNLOAD_FAILED
- ASR_FAILED
- FRAME_EXTRACTION_FAILED
- VISUAL_ANALYSIS_FAILED
- INTERNAL_ERROR

允许 partial/fallback，但不得把失败步骤说成成功。

## 12. 免费优先

当前不要求额外模型 API Key。

使用：
- 平台字幕；
- Bilibili 公共 API；
- yt-dlp；
- faster-whisper；
- OpenCV；
- ChatGPT 当前宿主视觉理解。

首次下载 Whisper 模型会产生网络流量和本地模型占用，但不是额外按次 API 费用。

## 13. 真实性与 Stable 门槛

当前 Runtime 已有代码，不代表已经在目标 Windows 机器真实运行成功。

Stable 前至少完成：
- B站公开视频 >= 3；
- YouTube公开视频 >= 3；
- 无人工字幕 >= 2；
- 视觉信息关键视频 >= 2；
- 45–90 分钟长视频 >= 1；
- follow-up dense rewatch >= 1；
- Secure MCP Tunnel/ChatGPT 实际 tool scan 与调用 >= 1。

在这些 smoke test 完成前维持 release-candidate。
