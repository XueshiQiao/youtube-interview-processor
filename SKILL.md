---
name: youtube-interview-processor
description: >-
  全自动处理 YouTube 采访与技术长视频：包含通过 yt-dlp 下载视频与独立 en-orig 原始字幕、
  消除 YouTube 双行滚动冗余并重构成语义长句、基于滑动窗口上下文翻译为纯中文/双语字幕、
  基于4维反共识探测框架深度提炼访谈核心洞察，并生成包含逐字对话精读与洞察仪表盘的交互式 HTML 网页。
  当用户输入 YouTube 链接或要求处理、下载、整理、翻译、总结 YouTube 访谈时触发此技能。
---

# YouTube 访谈视频全流程处理与精读精翻技能 (YouTube Interview Processor)

本技能为各类 AI Agent 提供标准化的 YouTube 长视频与访谈处理工作流，将杂乱、重复滚动的机翻字幕转化为高质量的语义长句、专业中文/双语字幕、深度反共识观点提炼与可沉浸式阅读的 HTML 网页。

---

## ⚠️ Agent 交互执行关键铁律 (CRITICAL: Interactive Output Rules)

为彻底杜绝“黑盒执行”和连续静默调用工具导致的盲等，Agent 在执行本技能时，**必须严格遵循以下交互规范**：

1. **绝对禁止连续静默调用底层命令而不给用户任何文字反馈！**
2. **第一步（预检与确认）必须向用户输出结构化看板**：
   - 必须先输出全流程 5 步看板，让用户清晰看到所有阶段与当前进度；
   - 执行 `python3 scripts/download_video_and_sub.py --check-only` 预检环境并展示结果（Python、yt-dlp、检测到的浏览器如 Chrome / Safari）；
   - **前置确认决策**：向用户明确汇报当前选用的浏览器 Cookie 策略，并告知用户可选择是否只下载字幕（`--sub-only`）；
3. **进入后续每一步时，必须实时更新状态并播报量化指标**：
   - 步骤 2：更新为 `[2/5] 正在下载媒体与字幕`，完成后汇报捕获的字幕语言；
   - 步骤 3：更新为 `[3/5] 正在去重与长句重构`，汇报去重条数与长句统计；
   - 步骤 4：更新为 `[4/5] 正在进行上下文滑动翻译`，按批次播报进度；
   - 步骤 5：更新为 `[5/5] 正在提炼 4 维反共识洞察与生成 HTML 网页`；
4. **最终交付报告**：
   - 统一给出生成文件的本地路径与离线 HTML 网页预览指引。

---

## 核心工作流步骤

### 步骤 1：环境预检与多源配置确认 (Pre-flight Check)
在正式处理前，运行预检程序检测本地环境并确定参数：

```bash
python3 scripts/download_video_and_sub.py --check-only
```
- **核心逻辑**：
  * 检测 Python 版本与 `yt-dlp` 状态（缺失时自动自愈安装）；
  * 自动发现系统安装的所有浏览器（Chrome, Safari, Firefox, Edge, Arc, Brave）；
  * 确定 Cookie 认证策略（支持通过 `--browser safari/chrome/none` 自由指定）。

---

### 步骤 2：视频与独立字幕下载 (Media Download)
运行脚本下载视频源文件与独立的原始英文转录字幕（`-orig`），确保字幕为外部独立 `.srt` 文件，不封装入视频容器。

```bash
python3 scripts/download_video_and_sub.py "<YouTube_URL>" [output_dir] [--browser auto/chrome/safari/none] [--sub-only]
```
- **核心逻辑**：优先获取 `en-orig` 语音原声转录，避免二手翻译；Cookie 锁死时自动降级无 Cookie 重试；可加 `--sub-only` 仅抓字幕。

---

### 步骤 3：滚动字幕去重与长句语义重构 (Deduplication & Restructuring)
YouTube 的自动字幕存在“双行滚动重叠（A-B / B-C）”与“10ms 动画刷新帧”。运行通用脚本将其规整为结构完整、时间轴严密的语义长句。

```bash
python3 scripts/clean_and_merge_srt.py <input.en-orig.srt> [output.merged.srt]
```
- **技术要点**：
  1. 过滤 $\le 50\text{ms}$ 播放器刷新帧；
  2. 双行滑动窗口 100% 精确去重；
  3. 单词级字符长度加权时间戳内插算法；
  4. 遇到 `>>` 说话人标记强制分段；
  5. 依据句终标点（`.`, `?`, `!`）断句，严格排除小数（`1.2`）与缩写（`Mr.`, `Dr.`）；
  6. 智能吸附小写从句与连词，合并短确认词（如 `>> Exactly. Right.`）；
  7. 专有名词规范化（`OpenAI`, `ChatGPT`, `GitHub` 等）。

---

### 步骤 4：上下文感知滑动窗口翻译 (Context-Aware Translation)
严禁单句隔离直译！长篇访谈中包含大量代词（it, they, that thing）与跨句逻辑，必须采用滑动窗口批量翻译：

- **输入文件**：步骤 2 产出的 `.merged.srt`
- **批次大小**：每批 20~25 句
- **上下文参考**：每次输入必须携带**前批结尾 3~5 句（中英对照）**作为逻辑衔接，并附带**后向 2~3 句预告**；
- **科技访谈术语表 (Glossary)**：
  - `Agent` -> 智能体 / Agent（结合语境自然使用，如 agent game 译为智能体开发/玩法）
  - `Foundation Model` -> 基座模型
  - `Power User` -> 深度用户 / 高级用户
  - `Use Cases` -> 应用场景 / 用例
  - `Entrepreneurship` -> 创业 / 创业生态
  - `Retain / Retention` -> 留存
- **产出文件**：
  - 纯中文字幕：`<原名>.merged.zh-Hans.srt`
  - 双语字幕：`<原名>.merged.bilingual.srt`

---

### 步骤 5：4维反共识探测框架与交互 HTML 网页生成
严禁做信息等权、流水账式的目录总结！启动【4维反共识探测器】挖掘全片最具穿透力的反直觉真相，并生成交互 HTML 网页：

```bash
python3 scripts/generate_html_reader.py <input.merged.srt> <input.merged.zh-Hans.srt> [output.html]
```
- **4 维反共识雷达**：
  1. **大众常识反转**：寻找嘉宾打破行业共识的核心变量（如：野心差距 vs 能力差距）；
  2. **权威专家的反常行为**：顶尖架构师公开“封笔”手写代码；
  3. **瓶颈位移探测**：技术商品化后，新的核心阻力转移至何处；
  4. **反套路与冷思考**：警惕盲目刷 Token，做满 5 次前严禁自动化。
- **产出网页规格**：
  - **Tab 1: ⚡ 颠覆性核心洞察**：封面级核心总纲、反直觉认知矩阵卡片、分章节深度剖析与直达跳转。
  - **Tab 2: 📖 访谈对谈录**：将散碎字幕整合成高信息密度的**说话人回合自然大段落（Speech Turns）**，支持双视图切换、一键中英对照开关、实时关键词搜索与高亮定位。

---

## 异常排查与自诊断手册 (Troubleshooting)

| 异常现象 | 根本原因 | 推荐解决操作 |
| :--- | :--- | :--- |
| `yt-dlp: command not found` | 缺少下载工具依赖 | 脚本内置自愈功能，会自动尝试 `pip` / `brew` 安装；亦可手动执行 `brew install yt-dlp` |
| `Chrome cookie DB is locked` | Chrome 浏览器正在占用数据库 | 脚本已支持自动降级重试；亦可通过 `--browser safari` 或 `--browser none` 运行 |
| `en-orig subtitle not available` | 视频作者关闭了原声自动识别或仅提供了普通字幕 | 运行 `yt-dlp --list-subs <URL>` 查看可用语言，降级采用 `en` |
| `JSON Decode Error in Translation` | 大模型批次输出被截断 | 将批次由 25 句缩减至 15 句，并在 Prompt 中强化“仅输出合法 JSON 数组”指令 |
| `Timecode mismatch` | 翻译过程中丢失了某些条目 | 严格使用已规整的 `.merged.srt` 编号，通过缓存字典补全缺失的 ID 重新请求 |
