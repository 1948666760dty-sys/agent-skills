---
name: video-understanding
display_name: Video Understanding / 视频理解
description: 上传优先、长视频友好的多模态视频理解 Skill。支持当前聊天中的视频附件，以及 Bilibili/B站和 YouTube URL。默认 Deep/效果优先：字幕/ASR、PySceneDetect 场景检测、自适应关键帧、章节化长视频、Evidence Memory、音画时间轴、Agentic Rewatch、证据化总结与后续问答。快速模式仅在用户明确要求快速/字幕优先时启用。
version: 0.2.2
status: release-candidate
canonical_repository: 1948666760dty-sys/agent-skills
canonical_path: skills/video-understanding/SKILL.md
activation: semantic-auto-upload-or-url
supported_inputs: [video_attachment, bilibili, youtube]
---

# Video Understanding v0.2.2

## 0. 定位

v0.2.0 从“URL 解析器”升级为 **Upload-First Agentic Video Understanding**。

默认优先级：

```text
理解质量 > 证据完整 > 速度 > 资源节省
```

入口优先级：

```text
当前聊天已上传视频
> Bilibili URL
> YouTube URL
```

用户只需：
- 上传视频；或
- 发送一个支持的 URL。

不要求用户：
- 手动切视频；
- 手动抽帧；
- 自己跑 Whisper；
- 自己操作 job_id；
- 自己决定章节范围；
- 长视频手工分段后重复上传。

---

## 1. Canonical 与真实性边界

唯一规范主源：

- Repo: `1948666760dty-sys/agent-skills`
- Skill: `skills/video-understanding/SKILL.md`
- Runtime: `skills/video-understanding/runtime/`
- Runtime contract: `skills/video-understanding/references/runtime-contract.md`

必须区分：
1. Skill 规则存在；
2. Runtime 代码存在；
3. 当前宿主是否能访问视频附件/URL；
4. 某次 ASR/视觉/回看是否真实成功。

不得因为 Skill 已加载就声称“已经看完视频”。

---

## 2. 自动触发

### 2.1 上传视频强触发

当当前对话包含视频附件，且用户表达以下任一语义时自动触发：
- “看一下”
- “总结”
- “这个讲了什么”
- “深度看”
- “分析这个视频”
- “帮我理解”
- “试试看”
- 直接上传视频后继续询问其中内容

若用户只上传视频而无其他明显意图，默认解释为：
**请理解并概括这个视频。**

宿主已经能直接读取/挂载附件时，不得反过来要求用户提供 URL。

### 2.2 URL 强触发

Bilibili：
- bilibili.com
- b23.tv
- BV / av / ep / ss

YouTube：
- youtube.com/watch
- youtu.be
- youtube.com/shorts

单独一个支持 URL 默认视为视频理解请求。

### 2.3 后续问答

同一视频上下文中的：
- “19分钟那个表格”
- “第二种方法”
- “他这里说的靠谱吗”
- “前后有没有矛盾”

继续使用当前 Video Capsule / cache，不重新完整处理。

---

## 3. 默认模式

### Deep（默认）

```yaml
mode: deep
priority: quality
transcript: full
scene_detection: adaptive
visual_overview: true
host_vision_ocr: true
chapters: true
video_memory: true
agentic_rewatch: true
evidence_labels: true
```

### Quick（用户显式要求）

触发：
- “快速看”
- “简单总结”
- “只看字幕”
- “不用看画面”

Quick 可以减少视觉覆盖与二次回看，但仍必须如实标记证据来源。

---

## 4. 输入路由

### A. 当前聊天视频附件（Mobile / Native 优先）

若宿主直接提供可读视频文件：
1. 读取附件；
2. Preflight；
3. 有可信字幕则使用字幕；
4. 否则本地/宿主 ASR；
5. Deep 时执行场景分析和关键帧；
6. 建立 Chapters + Evidence Memory；
7. 全局理解后自动回看重点。

**手机端与电脑端在默认质量策略上平等。**  
不得仅因为附件来自 Android/iOS/移动端，就自动：
- 切 Quick；
- 降低 ASR 完整度；
- 显著减少场景覆盖；
- 跳过二次回看；
- 只做字幕摘要。

若移动端宿主能够持续执行当前任务，允许长视频使用接近或超过视频时长的处理预算。例如：
- 60 分钟视频可允许约 120 分钟甚至更久；
- 复杂、无字幕、重视觉内容允许超过 2× 播放时长。

“允许长时间处理”不等于“后台异步保证”。若当前宿主/会话不支持离开聊天后持续执行，不得承诺关闭 App 后仍会在两小时后自动交付。

若通过 MCP Runtime 处理上传文件：
- 只能使用宿主已 materialize 到受控 upload inbox 的文件；
- Runtime 不允许任意读取电脑文件；
- 默认允许目录是 `~/.video-understanding/inbox`；
- 额外目录必须显式配置 `VIDEO_UPLOAD_ROOTS`。

若宿主没有向 MCP 暴露视频附件字节或受控本地路径，不能虚构“已传给 Runtime”。

### B. Bilibili

```text
URL/短链/ID
→ 元数据/分P
→ 人工字幕
→ AI字幕
→ 无字幕本地 ASR
→ Deep 视觉
→ 可选弹幕
```

### C. YouTube

```text
URL/Shorts
→ 元数据
→ 人工字幕
→ 自动字幕
→ 无字幕本地 ASR
→ Deep 视觉
```

---

## 5. Preflight

上传/获取视频后先确认：
- 时长；
- 分辨率；
- FPS；
- 文件大小（若可得）；
- 字幕来源；
- ASR 是否需要；
- 是否可做视觉分析；
- 长视频 tier。

Preflight 不需要用户参与。

---

## 6. 长视频策略

长视频不是“把更多 token 一次塞进去”，而是**分层取证**。

### 6.1 自适应 Tier

参考 Runtime：

| 时长 | Tier | 全局 baseline | 章节窗口 | Memory 窗口 |
|---|---|---:|---:|---:|
| ≤5 min | short | ~6s | ~2min | ~90s |
| 5–30 min | standard | ~12s | ~4min | ~2min |
| 30–90 min | long | ~20s | ~6min | ~3min |
| 90–180 min | very_long | ~30s | ~10min | ~5min |
| >180 min | ultra_long | ~45s | ~15min | ~7min |

这些是 Runtime 默认策略，不是固定 SLA；场景切换仍会额外贡献代表帧。

### 6.2 长视频处理流程

```text
完整字幕/ASR
↓
结构章节 Chapters
↓
重叠 Evidence Memory
↓
PySceneDetect AdaptiveDetector
↓
自适应全局关键帧
↓
第一遍 Global Pass
↓
发现核心/可疑/低置信度区间
↓
Search Memory / Transcript Window
↓
Dense Agentic Rewatch
↓
最终综合
```

### 6.3 上下文保护

30 分钟以上默认不得把完整字幕和所有帧一次性注入模型。

先使用：
- Chapters；
- Evidence Memory；
- 主题/问题检索；
- 时间窗口。

再读取相关：
- transcript；
- overview frames；
- dense rewatch frames。

因此 1～3 小时视频在架构上可以处理，不依赖单次超长上下文。

### 6.4 超长视频

>3 小时仍允许处理，但应：
- 更稀疏全局覆盖；
- 更多依赖章节索引；
- 按问题/主题检索；
- 必要时多轮局部 rewatch。

不得承诺任意长度都能在固定时间完成。

真正上限仍受：
- 宿主上传大小；
- 本地磁盘；
- 下载速度；
- ASR速度；
- GPU/CPU；
- Runtime/会话超时。

---

## 7. ASR

优先级：

```text
人工字幕
> 平台自动/AI字幕
> faster-whisper
```

上传文件若宿主未提供可信字幕，默认 ASR。

参考 Runtime 使用 faster-whisper >=1.2.1。当前 faster-whisper 仍支持 batched inference、VAD 与本地运行；不得因为 CUDA 尝试失败就声称 GPU ASR 成功。

ASR 高风险：
- 人名；
- 型号；
- 数字；
- 缩写；
- 方言/口音；
- 多人重叠。

关键数字必须尽量结合画面复核。

---

## 8. 场景检测与全局视觉

v0.2.0 参考 Runtime 使用 **PySceneDetect AdaptiveDetector**，而不是 v0.1 的简单直方图阈值。

要求：
- 自动 downscale；
- 快运动场景尽量减少误切；
- scene representative frame；
- baseline frame；
- 长视频控制 overview 总帧预算；
- 不因场景过多而无限保存帧。

若 PySceneDetect 失败：
→ baseline fallback；
→ 明确 warning；
→ 不把 fallback 冒充 scene-aware 成功。

---

## 9. Evidence Timeline

每个证据尽量包含：
- timestamp/start/end；
- source；
- confidence；
- evidence type。

证据类型必须分离：

1. speaker/subtitle
2. visual
3. host-vision OCR
4. platform metadata
5. audience/danmaku
6. model inference
7. external verification

作者声称 ≠ 已证实事实。

---

## 10. Chapters

Runtime Chapters 默认只是**结构导航窗口**，不能把未经模型处理的固定时间窗伪装成“语义章节”。

结构章节可以包含：
- start/end；
- transcript segment count；
- preview；
- characters；
- title=null；
- summary=null。

宿主模型完成第一遍理解后，可以生成语义标题/摘要。

---

## 11. Video Memory

每个视频构建重叠 transcript Evidence Chunks。

后续问题：

```text
问题
→ search Video Memory
→ 得到候选时间窗口
→ transcript 验证
→ 重要视觉问题 dense rewatch
→ 回答
```

v0.2.0 参考 Runtime 使用免费本地 lexical/BM25-like 检索，不要求额外 embedding API。

检索结果只能作为候选证据，不能代替最终核验。

---

## 12. Agentic Rewatch

Deep 必须允许二次回看。

第一遍发现：
- 数字；
- 表格；
- 实验；
- 代码；
- 价格；
- 前后冲突；
- 字幕不确定；
- 画面信息明显高于口述；
- 用户直接问某个时间点。

则生成 rewatch window，再调用高密度帧。

例如：

```json
{
  "start_seconds": 1120,
  "end_seconds": 1270,
  "reason": "关键实验结果/图表",
  "density": "dense"
}
```

---

## 13. Video Capsule

分析完成后维护轻量 Capsule：

```text
Video ID
Input kind
Duration/Tier
Transcript source
Chapters
Topics
Claims
Important numbers
Important frames
Uncertainties
Rewatch history
Evidence memory
```

后续问答优先复用 Capsule/cache。

---

## 14. Runtime Tools v0.2

参考 MCP Runtime 当前工具：

1. `start_video_analysis` — B站/YouTube URL
2. `start_uploaded_video_analysis` — 受控 inbox 中的上传文件
3. `wait_video_analysis`
4. `get_video_manifest`
5. `get_video_transcript`
6. `get_video_chapters`
7. `search_prepared_video`
8. `inspect_video_window`

长任务内部 start/wait 不得交给用户操作。

推荐长视频宿主序列：

```text
start
→ wait
→ manifest
→ chapters
→ transcript/windows
→ overview frames
→ first-pass synthesis
→ search_prepared_video
→ dense rewatch
→ final synthesis
```

---

## 15. 默认输出

中文默认：

1. 30 秒摘要
2. 核心结论
3. 章节/完整时间轴
4. 关键画面
5. 重要数字、参数、专名
6. 作者观点与证据
7. 画面与口述是否一致
8. 矛盾/不确定/待核查
9. 最值得看的时间段
10. 后续可问方向

顶部必须真实标记：
- 输入：上传 / B站 / YouTube
- 时长/Tier
- transcript source
- visual success
- OCR = host_vision 或实际本地 OCR
- second-pass 是否真实执行

---

## 16. 性能策略

用户偏好：**速度不重要，效果优先；手机也一样。**

默认不再追求“60 分钟视频 5–15 分钟完成”。

允许：
- 60 分钟视频处理约 60–120 分钟；
- 如果证据覆盖明显受益，60 分钟视频允许超过 120 分钟；
- 无字幕、重视觉、复杂图表/代码/实验视频超过视频原始时长；
- 90–180 分钟视频按质量需要持续更久；
- >180 分钟视频采用章节化长任务，不设置固定完成时间目标。

这个策略对 **Mobile Native 上传** 和 Desktop/Runtime 输入一致；设备入口本身不是降质理由。

当“更慢”可以明显换来：
- 更完整 ASR；
- 更高场景覆盖；
- 更多关键帧；
- 更充分 OCR/画面阅读；
- 更多 Agentic Rewatch；
- 更可靠的专名/数字复核；
- 更低漏关键信息概率；

则优先选择更慢、更完整的路径。

只有用户明确说“快速看 / 尽快 / 简单总结”时，才主动压缩计算与视觉覆盖。

速度不是验收指标；**证据覆盖、准确性、可追溯性**才是默认验收重点。

---

## 17. 免费优先

默认：
- yt-dlp / Bilibili public APIs；
- faster-whisper；
- PySceneDetect；
- OpenCV；
- host ChatGPT vision；
- 本地 lexical Video Memory。

不得静默调用额外收费模型 API。

---

## 18. 隐私与本地文件安全

- 不要求用户在聊天粘 raw cookie；
- 读取浏览器登录态前必须明确授权；
- MCP 上传入口不得接受任意电脑路径；
- 默认仅 `~/.video-understanding/inbox`；
- `VIDEO_UPLOAD_ROOTS` 必须由用户/部署者显式设置；
- 不把本地视频公开上传到第三方，除非用户明确选择相关服务。

---

## 19. 失败降级

- 字幕失败 → ASR
- 场景检测失败 → baseline visual fallback
- 视觉失败但 transcript 成功 → transcript-only partial
- ASR失败但烧录字幕可视觉读取 → visual-caption partial
- 全部正文证据失败 → 不根据标题猜内容
- 上传文件被宿主删除 → follow-up visual rewatch 要求重新 materialize/re-upload
- 超长视频 → 内部分块，不要求用户手工切片

---

## 20. 与 No-Rush

```text
No-Rush
→ Upload/URL Router
→ Preflight
→ Runtime/Evidence Pipeline
→ Long-video Memory
→ Agentic Rewatch
→ Quality Gate
→ Final
→ No-Rush Closing Report
```

---

## 21. 验收标准

Stable 前至少：

1. 当前聊天上传短视频真实分析 >= 2
2. 上传 30–90 分钟视频 >= 1
3. 上传或 URL 90–180 分钟视频 >= 1
4. B站 >= 3
5. YouTube >= 3
6. 无人工字幕 >= 2
7. 视觉信息关键视频 >= 2
8. PySceneDetect 成功路径 >= 2
9. scene fallback >= 1
10. Video Memory 后续问答 >= 3
11. dense rewatch >= 3
12. 任意本地路径读取被拒绝测试 >= 1
13. inbox 上传成功 >= 1
14. 宿主无法 materialize attachment 时不假装 Runtime 已获取
15. 1～3 小时视频不一次性灌入完整 transcript + frames
16. 失败步骤不冒充成功
17. 不默认产生额外 API 费用

---

## 22. 当前状态

当前版本：`0.2.2 release-candidate`

已经实现到参考 Runtime：
- Bilibili / YouTube；
- uploaded-file inbox adapter；
- faster-whisper；
- PySceneDetect AdaptiveDetector；
- adaptive long-video sampling；
- structural chapters；
- overlapping Evidence Memory；
- local lexical retrieval；
- overview frames；
- dense rewatch；
- MCP ImageContent。

尚未声称：
- Windows 实机所有依赖已跑通；
- ChatGPT 自定义 MCP 自动获得手机/聊天附件字节；
- 1～3 小时端到端性能已经实测；
- Stable。

### Changelog

- **0.2.2（2026-09-22）**：新增 Mobile-Native Quality-First 契约；手机直接上传视频与电脑端享有同等默认质量策略；60 分钟视频可允许约 120 分钟甚至更久处理；明确“允许慢处理”不等于“后台异步保证”。
- **0.2.1（2026-09-22）**：性能策略改为 Quality-First 无硬时限；允许长视频处理时间接近或超过原视频时长，默认以证据覆盖和准确性优先，只有用户明确要求快速时才压缩流程。
- **0.2.0（2026-09-22）**：Upload-First；加入安全 upload inbox、本地视频 adapter、PySceneDetect AdaptiveDetector、自适应长视频 tier、结构章节、Evidence Memory、本地检索、长视频上下文保护与 8-tool MCP 编排。
- **0.1.1（2026-09-22）**：对齐首版 MCP Runtime。
- **0.1.0（2026-09-22）**：Bilibili + YouTube 首版。
