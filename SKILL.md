---
name: youtube-interview-processor
description: >-
  全自动处理 YouTube 采访与技术长视频：包含通过 yt-dlp 下载视频与独立 en-orig 原始字幕、
  消除 YouTube 双行滚动冗余并重构成语义长句、基于滑动窗口上下文翻译为纯中文/双语字幕、
  基于4维反共识探测框架深度提炼访谈核心洞察，并生成包含逐字对话精读与洞察仪表盘的交互式 HTML 网页。
  当用户要求处理、下载、整理、翻译或总结 YouTube 视频/访谈字幕时使用此技能。
---

# YouTube 访谈视频全流程处理与精读精翻技能 (YouTube Interview Processor)

本技能为各类 AI Agent 提供标准化的 YouTube 长视频与访谈处理工作流，将杂乱、重复滚动的机翻字幕转化为高质量的语义长句、专业中文/双语字幕、深度反共识观点提炼与可沉浸式阅读的 HTML 网页。

---

## 前置依赖与自动自愈机制 (Prerequisites & Auto-Healing)

本技能具备**全自动依赖检测与自愈能力**：
- 当运行 `scripts/download_video_and_sub.py` 时，脚本会自动检测系统是否安装了 `yt-dlp`。
- **若未检测到 `yt-dlp`，脚本将自动尝试通过 `pip install -U yt-dlp`（或 macOS 下的 `brew install yt-dlp`）进行静默自愈安装**，无需人工干预。
- 若调用本 Skill 的 AI Agent 处于特定限制环境，Agent 亦可主动执行 `pip install yt-dlp` 确保环境就绪。

---

## 核心工作流步骤

### 步骤 1：视频与独立字幕下载 (基于 yt-dlp)
运行脚本下载视频源文件与独立的原始英文转录字幕（`-orig`），确保字幕为外部独立 `.srt` 文件，不封装入视频容器。

```bash
python3 scripts/download_video_and_sub.py "<YouTube_URL>" [output_dir]
```
- **核心逻辑**：优先获取 `en-orig` 语音原声转录，避免二手翻译；使用 `--cookies-from-browser chrome` 保证高清画质与权限；下载失败时提供明确的诊断排查说明。自动检测并自愈安装缺失依赖。

---

### 步骤 2：滚动字幕去重与长句语义重构
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

### 步骤 3：上下文感知滑动窗口翻译 (Context-Aware Translation)
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

### 步骤 4：4维反共识探测框架（核心洞察提炼方法论）
严禁做信息等权、温吞水平铺的流水账总结！必须启动【4维反共识探测器】挖掘全片最具穿透力的反直觉真相：

1. **大众常识反转探测 (Breaking Common Consensus)**：
   - 扫描嘉宾明确打破大众预设或提出对立对比的论断（`It's not about X, but actually Y`）。
   - 思考：在这场访谈中，大众通常认为决定胜负的因素是什么，而嘉宾指出的真正决定性变量是什么？（例如：能力 vs 野心、模型规模 vs 场景密度）。
2. **权威专家的反常行为 (Paradoxical Behavior of Top Experts)**：
   - 寻找作为顶级专家的嘉宾，做出了严重违背其原有工种或常理的行为（例如：顶级程序员彻底放弃手写代码、AI巨头警告不要盲目做Agent）。
3. **瓶颈位移探测 (Bottleneck Inversion)**：
   - 当原本的旧技术瓶颈（如编程能力、算力成本、信息获取）被解决后，新的瓶颈转移到了哪个意想不到的维度？
4. **反套路与痛点警示 (Anti-Hype & Reality Check)**：
   - 嘉宾对当前狂热趋势（如盲目刷Token、做晨报玩具、复杂界面堆砌）提出了哪些尖锐批评和冷思考？

---

### 步骤 5：生成交互式 HTML 对话精读与深度总结网页
不仅产出字幕，更生成开箱即用、免看视频即可沉浸式阅读的现代化 HTML 网页：

```bash
python3 scripts/generate_html_reader.py
```
- **Tab 1: ⚡ 颠覆性核心洞察与全局总结**：
  - **核心灵魂总纲**：基于步骤 4 提炼出的全片最关键反共识洞见；
  - **5大反常识卡片**：【大众共识】vs【颠覆真相】对比矩阵；
  - **6大章节深度大纲**：带发言篇章一键跳转链接；
  - **行动指南**：为从业者量身打造的落地实操建议。
- **Tab 2: 📖 访谈对谈录 (Interactive Dialogue Stream)**：
  - 按说话人回合聚合成自然长段落（告别散碎字幕感）；
  - 角色专属徽章与时间跨度标注；
  - 实时关键词搜索与高亮；
  - 说话人筛选过滤；
  - 支持中英双语与纯中文一键切换。

---

## 异常排查与自诊断手册 (Troubleshooting)

| 异常现象 | 根本原因 | 推荐解决操作 |
| :--- | :--- | :--- |
| `yt-dlp: command not found` | 缺少下载工具依赖 | 执行 `brew install yt-dlp` 或 `pip install -U yt-dlp` |
| `Chrome cookie DB is locked` | Chrome 浏览器正在占用数据库 | 完全退出 Google Chrome 后重试，或改用 Safari / Firefox 选项 |
| `en-orig subtitle not available` | 视频作者关闭了原声自动识别或仅提供了普通字幕 | 运行 `yt-dlp --list-subs <URL>` 查看可用语言，降级采用 `en` |
| `JSON Decode Error in Translation` | 大模型批次输出被截断 | 将批次由 25 句缩减至 15 句，并在 Prompt 中强化“仅输出合法 JSON 数组”指令 |
| `Timecode mismatch` | 翻译过程中丢失了某些条目 | 严格使用已规整的 `.merged.srt` 编号，通过缓存字典补全缺失的 ID 重新请求 |
