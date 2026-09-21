# Video Understanding Runtime Contract v0.1.0

## 1. 目的

本文件定义 ChatGPT/Agent Skill 与真实视频处理后端之间的最小契约。

目标用户体验只有一个入口：

```text
<video URL>
```

内部可以多阶段执行，但不得要求用户参与任务编排。

## 2. 支持平台

v0.1：
- Bilibili
- YouTube

规范化后必须得到：

```json
{
  "platform": "bilibili|youtube",
  "canonical_id": "...",
  "canonical_url": "...",
  "part": null
}
```

## 3. 推荐 MCP Tool

### 3.1 首选：analyze_video

```json
{
  "name": "analyze_video",
  "input": {
    "url": "string",
    "mode": "deep|quick",
    "question": "string|null",
    "language": "zh-CN"
  }
}
```

返回完整 `VideoAnalysisResult`。

若宿主允许足够长的工具调用，这是最简单路径。

### 3.2 长任务 fallback

若单次工具调用不能覆盖长视频处理时间，可实现：

```text
start_video_analysis
get_video_analysis
```

Skill/宿主负责自动完成：
- start；
- 状态获取；
- 最终结果获取。

用户不得被要求输入 job_id。

## 4. VideoAnalysisResult

```json
{
  "schema_version": "0.1",
  "status": "complete|partial|failed",
  "source": {
    "platform": "youtube",
    "canonical_id": "...",
    "canonical_url": "...",
    "title": "...",
    "author": "...",
    "duration_seconds": 3600,
    "part": null,
    "fetched_at": "ISO-8601"
  },
  "acquisition": {
    "transcript_source": "human|platform_auto|asr|none",
    "visual": true,
    "ocr": true,
    "second_pass": true,
    "audience": false
  },
  "transcript": [],
  "frames": [],
  "ocr": [],
  "chapters": [],
  "rewatch_windows": [],
  "analysis": {},
  "warnings": []
}
```

## 5. TranscriptSegment

```json
{
  "start_ms": 1000,
  "end_ms": 5300,
  "text": "...",
  "source": "human|platform_auto|asr",
  "confidence": 0.94
}
```

ASR 无可靠 confidence 时允许 null。

## 6. FrameRecord

```json
{
  "timestamp_ms": 812000,
  "path_or_asset_id": "...",
  "reason": "scene_cut|baseline|semantic_anchor|rewatch",
  "visual_summary": "...",
  "confidence": 0.9
}
```

## 7. OCRRecord

```json
{
  "timestamp_ms": 812000,
  "text": "...",
  "bbox": null,
  "confidence": 0.91
}
```

## 8. RewatchWindow

```json
{
  "start_ms": 1120000,
  "end_ms": 1270000,
  "reason": "critical_chart",
  "sampling": "dense"
}
```

## 9. Bilibili Adapter

推荐能力：
- b23.tv 跳转解析；
- BV/av；
- ep/ss；
- 分P；
- 元数据；
- 人工字幕；
- AI字幕；
- 可选弹幕；
- 无字幕音频 fallback。

匿名优先。

不得在日志返回原始 cookie。

## 10. YouTube Adapter

推荐能力：
- youtube.com/watch；
- youtu.be；
- shorts；
- metadata；
- manual captions；
- auto captions；
- audio/video fallback。

建议用 yt-dlp 或等价适配器，但 Skill 不绑定具体实现。

## 11. ASR

免费优先：
- faster-whisper；
- 本地模型缓存。

Runtime 应允许：
```yaml
asr_model: configurable
device: auto
compute_type: auto
```

不得把“模型下载成功”当作“视频转写成功”。

## 12. Scene / Frame Pipeline

Deep 推荐：

```text
probe
→ scene detection
→ baseline sampling
→ semantic anchors
→ dedupe
→ visual pass 1
→ rewatch planning
→ dense local resample
→ visual pass 2
```

关键目标是覆盖信息，而不是固定帧数。

## 13. OCR

默认免费本地 OCR。

OCR 重点对象：
- slides；
- charts；
- tables；
- code；
- UI；
- prices；
- specs；
- labels。

低价值 talking-head 画面不应大量 OCR。

## 14. 缓存

缓存 key 至少：

```text
platform + canonical_id + part + content_revision
```

建议分层：
- raw metadata；
- subtitles；
- ASR；
- frames；
- OCR；
- final analysis。

Follow-up 优先复用。

## 15. 临时文件

默认写入独立工作目录。

任务结束：
- 保留结构化缓存；
- 可删除大体积原始音视频；
- 不留下散乱文件到桌面/用户目录；
- 可配置保留策略。

## 16. 错误码

至少定义：
- UNSUPPORTED_URL
- VIDEO_NOT_FOUND
- AUTH_REQUIRED
- SUBTITLE_UNAVAILABLE
- MEDIA_DOWNLOAD_FAILED
- ASR_FAILED
- FRAME_EXTRACTION_FAILED
- OCR_FAILED
- VISUAL_ANALYSIS_FAILED
- RUNTIME_TIMEOUT
- INTERNAL_ERROR

允许 partial success。

## 17. 性能遥测

返回：
- total_ms；
- acquire_ms；
- asr_ms；
- frame_ms；
- ocr_ms；
- reasoning_ms；
- frame_count；
- rewatch_frame_count。

用于之后优化“60 分钟视频约 5–15 分钟”目标，但不得对用户伪装固定 SLA。

## 18. 安全与隐私

- 不回传 raw cookie；
- 不将私有视频缓存为公共资源；
- 浏览器 cookie 读取必须有显式授权；
- 日志避免敏感 token；
- 下载内容仅用于用户请求的理解任务；
- 遵守平台和宿主能力边界。

## 19. Stable 门槛

Runtime 达到 stable 前至少完成：
- B站 3 个公开视频；
- YouTube 3 个公开视频；
- 其中至少 2 个无人工字幕；
- 至少 2 个画面信息明显高于口述的信息型视频；
- 至少 1 个 45–90 分钟长视频；
- 裸链接端到端；
- follow-up 局部回看；
- 错误降级测试。
