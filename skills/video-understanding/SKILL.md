---
name: video-understanding
display_name: Video Understanding / 视频理解
description: 面向 ChatGPT 的统一长视频理解 Skill。用户只需发送 Bilibili/B站或 YouTube 链接（包括 b23.tv、BV/av/ep/ss、youtube.com、youtu.be、YouTube Shorts），即可自动识别平台并进入视频理解流程。默认 Deep/效果优先：字幕优先、无字幕本地 ASR、场景检测、关键帧、OCR、音画时间轴对齐、重点区间二次回看、证据化总结与后续问答。快速模式仅在用户明确说“快速看/简单总结”时启用。
version: 0.1.0
status: release-candidate
canonical_repository: 1948666760dty-sys/agent-skills
canonical_path: skills/video-understanding/SKILL.md
activation: semantic-auto-url
supported_platforms: [bilibili, youtube]
---

# Video Understanding v0.1.0

## 0. 目标

用户体验必须尽量接近：

```text
用户：<一个 B站或 YouTube 链接>
→ 自动识别
→ 自动分析
→ 当前聊天直接返回结果
```

用户不需要：
- 指定平台；
- 写命令；
- 选择字幕工具；
- 手动下载视频；
- 手动上传帧；
- 提供 job_id；
- 再发一句“开始”。

默认优先级：**理解质量 > 处理速度 > 资源节省**。

---

## 1. Canonical 与真实性边界

唯一规范主源：

- Repo: `1948666760dty-sys/agent-skills`
- Path: `skills/video-understanding/SKILL.md`

本 Skill 是路由、分析与交付规范，不等于可执行的视频 Runtime。

真正完成以下动作需要宿主 Runtime/MCP：
- 获取视频元数据；
- 获取字幕；
- 下载或读取音视频；
- Whisper/faster-whisper；
- FFmpeg/OpenCV 场景检测；
- 关键帧；
- OCR；
- 缓存；
- 长任务状态管理。

若 Runtime 未接入，不得声称“已经看完视频”。应明确区分：
- Skill 已加载；
- URL 已识别；
- Runtime 是否真正成功执行；
- 哪些证据实际取得。

Runtime 契约见：
`skills/video-understanding/references/runtime-contract.md`

---

## 2. 自动触发

### 2.1 裸链接强触发

用户消息只包含或主要包含以下任一种内容时，默认自动触发：

Bilibili：
- `bilibili.com/video/...`
- `b23.tv/...`
- `BV...`
- `av...`
- `ep...`
- `ss...`

YouTube：
- `youtube.com/watch?v=...`
- `youtu.be/...`
- `youtube.com/shorts/...`
- 合法的 YouTube share URL

即使用户没有写“总结”“分析”“帮我看”，**单独一个支持的视频地址也视为“请理解这个视频”**。

### 2.2 语义触发

以下语义同样触发：
- “看一下这个视频”
- “这个讲了什么”
- “帮我总结”
- “深度看”
- “视频里他说的靠谱吗”
- “帮我看 18 分钟那里”
- “这个 B站/YouTube 视频什么意思”
- 在同一视频上下文中的后续问题

### 2.3 不触发

以下情况不自动把链接当视频分析任务：
- 用户明确说“只帮我复制/改写这个链接”；
- 用户仅询问该网站本身；
- 链接不是支持平台的视频；
- 用户明确要求其他操作且视频理解与任务无关。

---

## 3. 默认模式

### 3.1 Deep（默认）

除非用户明确要求快，否则：

```yaml
mode: deep
priority: quality
visual_analysis: true
ocr: true
second_pass: true
timestamps: true
evidence_labels: true
audience_signals:
  bilibili: optional
```

### 3.2 Quick（显式）

只有用户明确说：
- “快速看一下”
- “简单总结”
- “不用看画面”
- “只读字幕”

才使用 Quick。

Quick 优先字幕，减少视觉抽帧与二次回看。

---

## 4. 平台路由

### 4.1 Bilibili

优先链：

```text
规范化 URL / BV / av / ep / ss / b23
→ 元数据与分P
→ 人工字幕
→ AI字幕
→ 无字幕则本地 ASR
→ 视频视觉分析
→ 可选弹幕热点
```

设计参考 BiliLens 思路，但本 Skill 不复制外部实现代码。

必须保留：
- canonical video id；
- 当前分P；
- 视频长度；
- 标题/作者；
- 字幕来源；
- 获取时间；
- 弹幕若参与分析，必须和作者观点分开。

### 4.2 YouTube

优先链：

```text
规范化 URL / video id / Shorts
→ 元数据
→ 人工字幕
→ 自动字幕
→ 无字幕则本地 ASR
→ 视频视觉分析
```

不得因为自动字幕存在就默认视为高可信文本；专名、数字、型号、外语、口音仍需交叉检查。

---

## 5. 音频与字幕

字幕优先级：

```text
人工字幕
> 平台 AI/自动字幕
> 本地 ASR
```

若使用 ASR：
- 默认本地 `faster-whisper` 或兼容实现；
- 不因免费目标自动调用收费 ASR API；
- 标注 ASR 风险：人名、品牌、型号、数字、缩写、多人重叠、方言/口音；
- 对重要数字和专名优先结合画面 OCR 复核。

不得把标题、简介或评论猜成视频正文。

---

## 6. Deep 视觉流程

目标不是逐帧暴力读取，而是“先粗看全片，再回看重点”。

### 6.1 第一遍：全局覆盖

```text
场景切换检测
+ 基础时间采样
+ 字幕语义锚点
→ 候选关键帧
```

建议初始策略（Runtime 可动态调整）：
- 明显 scene cut：取代表帧；
- 长时间无 scene cut：每 8–15 秒补一张；
- PPT / 网页 / 代码 / 表格 / 商品参数 / 游戏 UI / 数据图：提高采样密度；
- 单纯 talking head：可降低采样密度。

禁止写死“固定每 N 秒”作为唯一规则。

### 6.2 OCR

对可能承载事实信息的画面执行 OCR：
- PPT；
- 图表；
- 参数；
- 价格；
- 代码；
- 网页；
- UI；
- 字幕外文字；
- 标题卡；
- 数据表。

OCR 文本必须携带时间戳和帧来源。

### 6.3 第一轮理解

综合：
- 完整字幕/ASR；
- 第一遍关键帧；
- OCR；
- 元数据。

找出：
- 核心段落；
- 高信息密度段落；
- 关键实验/演示；
- 重要数据；
- 视觉与口述可能冲突的位置；
- 需要回看的不确定点。

### 6.4 第二遍：Agentic Rewatch

Deep 默认启用。

模型为每个重点区间生成 rewatch window，例如：

```json
{
  "start": "18:40",
  "end": "21:10",
  "reason": "核心实验结果与关键图表",
  "sampling": "dense"
}
```

Runtime 对这些区间：
- 提高抽帧密度；
- 重新 OCR；
- 必要时局部音频重转写；
- 重新综合。

第二遍结束后才能形成最终 Deep 结论。

---

## 7. 音画时间轴对齐

统一内部模型：

```text
NormalizedVideo
├─ source
├─ metadata
├─ transcript[]
├─ frames[]
├─ ocr[]
├─ audience[]
├─ chapters[]
├─ rewatch_windows[]
└─ analysis
```

所有重要元素尽量携带：
- start/end 或 timestamp；
- source；
- confidence；
- platform-specific id。

重要结论尽量能追溯到：
- 字幕时间戳；
- 画面时间戳；
- OCR 时间戳；
- 元数据。

---

## 8. 证据类型必须分开

最终分析不可混为一谈：

1. **视频作者口述/字幕**
2. **视频画面直接展示**
3. **平台元数据**
4. **观众弹幕/互动信号**
5. **模型综合推断**
6. **外部事实核查**（若用户要求且宿主允许）

例如：

“作者声称 X” ≠ “X 是事实”。

“弹幕大量质疑 X” ≠ “X 已被证伪”。

---

## 9. 默认输出

默认中文。

### 9.1 顶部状态

至少包含：
- 标题；
- 平台；
- 时长；
- 内容来源：人工字幕 / 自动字幕 / ASR；
- 视觉分析是否成功；
- OCR 是否使用；
- 是否完成二次回看。

### 9.2 正文

默认结构：

1. **30 秒摘要**
2. **核心结论**
3. **完整时间轴**
4. **关键画面/演示**
5. **重要数字、参数、专名**
6. **作者观点与证据**
7. **画面与口述是否一致**
8. **不确定、矛盾或值得核查的点**
9. **最值得看的原视频时间段**
10. **可继续问的问题方向**

“这个视频值不值得完整看”只能基于用户目的作条件化说明，不应伪装成普遍客观结论。

---

## 10. 后续问答与缓存

同一 canonical video 应尽量缓存：
- metadata；
- transcript；
- frame index；
- OCR；
- rewatch windows；
- analysis summary。

用户后续问：
- “19 分钟那个表格什么意思？”
- “第二个方法靠谱吗？”
- “作者有没有前后矛盾？”

优先复用已缓存视频模型，不从头完整跑一遍。

如果问题需要原先未采样画面，可局部 rewatch。

---

## 11. 性能目标

目标示例：

> 常规 60 分钟视频，在已有可用字幕、网络和 Runtime 正常时，Deep 尽量在约 5–15 分钟量级内完成。

这是**性能目标，不是 SLA**。

不得保证“60 分钟视频一定 10 分钟完成”。

影响因素包括：
- 字幕是否存在；
- 下载速度；
- 视频码率/分辨率；
- 是否需要完整 ASR；
- scene 数量；
- OCR 数量；
- rewatch 次数；
- 宿主视觉分析吞吐。

用户当前偏好：慢一点可以，效果优先。

---

## 12. 免费优先

默认不要求额外付费 API Key。

优先：
- 平台字幕；
- yt-dlp / 平台公开接口或兼容提取器；
- FFmpeg；
- OpenCV；
- faster-whisper；
- 本地 OCR（如 PaddleOCR）；
- 宿主 ChatGPT 已有的理解能力。

若某项必须调用额外付费服务，必须先说明，不能静默产生额外费用。

---

## 13. 登录、Cookie 与隐私

默认匿名提取。

若登录内容/字幕必须依赖本地浏览器 Cookie：
1. 先说明原因；
2. 只有用户明确同意才读取；
3. 不在聊天中要求粘贴原始 Cookie；
4. 不打印/保存完整 Cookie；
5. 缓存和临时文件遵守最小化原则。

---

## 14. Runtime / MCP 对外体验

即使后端内部实现采用：

```text
start_analysis
→ poll/status
→ get_result
```

对用户必须保持：

```text
贴一次 URL
→ 系统自动完成内部流程
→ 返回结果
```

不得要求用户：
- 再输入 job id；
- 自己轮询；
- 自己运行 ffmpeg；
- 自己下载字幕；
- 自己选择解析器。

若宿主环境支持单个阻塞式工具，可使用 `analyze_video`。

若宿主工具有时长限制，可内部自动使用任务式 API，但对用户隐藏任务编排细节。

---

## 15. 与 No-Rush

No-Rush 是上层控制层：

```text
No-Rush
→ Video Understanding Router
→ Runtime
→ Evidence/Quality Gate
→ Final Delivery
→ No-Rush Closing Report
```

不得因为视频任务较长而绕开 No-Rush 的真实性检查。

---

## 16. Quality Gate

最终交付前至少检查：

- URL 是否解析到正确视频；
- B站分P是否正确；
- 视频时长是否合理；
- 字幕来源是否标注；
- Deep 模式是否真正尝试视觉分析；
- 关键数字是否有来源；
- ASR 高风险专名是否复核；
- 重要结论是否可追溯；
- 画面/作者/观众/模型推断是否分层；
- second pass 状态是否真实；
- 缓存是否对应 canonical video；
- 不得把失败的视觉/ASR说成成功。

---

## 17. 失败降级

### A. 字幕失败但视频可取
→ 本地 ASR。

### B. 视频视觉下载失败但字幕成功
→ 可以输出“字幕理解版”，明确视觉未完成。

### C. ASR 与视觉都失败
→ 不得根据标题猜正文。

### D. 登录限制
→ 说明需要授权；没有授权就保持匿名降级。

### E. 超长视频或宿主执行限制
→ 允许分段内部处理与合并，但不要求用户手工分段。

---

## 18. 验收标准

正式稳定版至少要求：

1. 裸 B站 URL 自动触发；
2. 裸 YouTube URL 自动触发；
3. b23.tv 可规范化；
4. YouTube Shorts 可规范化；
5. 默认 Deep；
6. “快速看”切 Quick；
7. 人工字幕优先；
8. 自动字幕次优先；
9. 无字幕自动 ASR；
10. Deep 有真实视觉帧；
11. OCR 有时间戳；
12. 有 scene-aware 抽帧；
13. 有重点区间二次回看；
14. 重要结论有 evidence type；
15. follow-up 可复用缓存；
16. 用户不需要 job id；
17. 用户不需要二次发送“开始”；
18. 失败时不假装成功；
19. 不默认产生额外 API 费用；
20. 用真实 B站和 YouTube 视频各完成至少 3 个端到端 smoke test 后，才能从 release-candidate 升为 stable。

---

## 19. 当前发布状态

当前版本：`0.1.0 release-candidate`

已经定义：
- 自动触发；
- 双平台路由；
- Deep/Quick；
- 字幕/ASR；
- scene-aware 视觉；
- OCR；
- Agentic Rewatch；
- evidence model；
- 缓存；
- MCP/Runtime 边界；
- 质量门与验收标准。

尚未因为“规范文件已存在”而宣称 Runtime 已可用。

### Changelog

- **0.1.0（2026-09-22）**：首个 Bilibili + YouTube 统一视频理解候选版；裸链接自动触发；默认 Deep/效果优先；加入字幕→ASR fallback、场景关键帧、OCR、音画时间轴对齐、Agentic Rewatch、缓存和 MCP Runtime 契约。
