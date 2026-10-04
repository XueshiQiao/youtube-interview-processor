# YouTube Interview Processor 🎙️⚡

> **A full-lifecycle AI Skill & toolkit for YouTube interviews, podcasts, and technical deep dives.**  
> 从 YouTube 视频与独立原声字幕抓取、双行滚动冗余消除与整句语法重构、上下文感知批量双语翻译，到基于【4维反共识探测框架】提炼颠覆性核心洞察，并一键生成沉浸式交互 HTML 精读网页。

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-indigo.svg)](https://github.com/google-deepmind)

---

## 🌟 核心特性 (Features)

1. **一步式视频与独立字幕下载 (Standalone Video & Subtitle Downloader)**：
   - 基于 `yt-dlp`，优先拉取未经二手机翻的原生语音转录字幕（`en-orig`）。
   - **严格保持独立外部 `.srt` 文件**，绝不封装或混流进视频容器内部。
   - 内置 `--cookies-from-browser chrome` 认证支持与友好的异常自诊断手册。

2. **数学级精度的滚动字幕去重与长句语义重构 (Deduplication & Sentence Restructuring)**：
   - 彻底过滤 YouTube 播放器特有的 $\le 50\text{ms}$ 动画闪烁刷新帧。
   - 采用双行滑动窗口 100% 精确去重，消除常见“A-B / B-C”双行滚动重叠。
   - **单词级字符加权时间戳内插算法**：根据词长比例精确分配毫秒级起止时间，断句后音画严丝合缝。
   - 智能识别说话人切换标志（`>>`）、排除小数点（`1.2`）与缩写（`Mr.`, `Dr.`），吸附小写从句与短确认词（如 `>> Exactly. Right.`）。

3. **上下文感知滑动窗口翻译 (Context-Aware Sliding Window Translation)**：
   - 彻底告别单句盲翻带来的代词指代混乱与断句割裂。
   - 分批翻译时携带前向上下文（已翻译中英对照）与后向预告，确保指代清晰、逻辑连贯。
   - 预设 AI / 科技商业领域专业术语表（Glossary）与角色口吻校准（信达雅）。

4. **4 维反共识探测框架 (Contrarian Disruption Detection Framework)**：
   - 告别平庸、流水账式的目录摘要，主动扫描并提炼全片最具冲击力的底层真相：
     * **大众常识反转 (Breaking Common Consensus)**：不是能力的差距，而是野心的差距；
     * **权威专家的反常行为 (Paradoxical Behavior)**：顶尖架构师公开“封笔”手写代码；
     * **瓶颈位移探测 (Bottleneck Inversion)**：技术实现商品化后，新瓶颈转移至何处；
     * **反套路与冷思考 (Anti-Hype & Reality Check)**：警惕无脑刷 Token，人工做满 5 次前严禁自动化。

5. **沉浸式交互 HTML 访谈精读网页 (Interactive Dialogue Reader & Dashboard)**：
   - **Tab 1: ⚡ 颠覆性核心洞察**：封面级核心总纲、反直觉认知矩阵卡片、分章节深度剖析与直达跳转。
   - **Tab 2: 📖 访谈对谈录**：将散碎字幕整合成高信息密度的**说话人回合自然大段落（Speech Turns）**，支持双视图切换、一键中英对照开关、实时关键词搜索与高亮定位。

---

## 📂 项目结构 (Repository Structure)

```text
youtube-interview-processor/
├── SKILL.md                          # Antigravity 标准 Skill 规范定义与 Agent 执行手册
├── README.md                         # 项目中文与英文说明文档
├── LICENSE                           # MIT 开源协议
├── .gitignore                        # Git 忽略规则 (过滤多媒体、缓存与秘钥)
└── scripts/
    ├── download_video_and_sub.py     # 视频与独立 en-orig 字幕下载器
    ├── clean_and_merge_srt.py        # 双行滚动去重与语义长句重构器
    └── generate_html_reader.py       # 沉浸式 HTML 对谈录与洞察仪表盘生成器
```

---

## 🚀 快速上手 (Quick Start)

### 1. 环境依赖 (Prerequisites)

```bash
# 安装 Python 依赖与 yt-dlp
brew install yt-dlp   # macOS 推荐
# 或
pip install -U yt-dlp
```

### 2. 标准工作流执行 (Step-by-Step)

#### 步骤 1：下载视频与独立原始字幕
```bash
python3 scripts/download_video_and_sub.py "<YouTube_URL>" [output_dir]
```

#### 步骤 2：字幕滚动去重与长句重构
```bash
python3 scripts/clean_and_merge_srt.py <input.en-orig.srt> [output.merged.srt]
# 示例：
python3 scripts/clean_and_merge_srt.py my_interview.en-orig.srt my_interview.merged.srt
```

#### 步骤 3：翻译与生成 HTML 交互精读网页
```bash
python3 scripts/generate_html_reader.py <input.merged.srt> <input.merged.zh-Hans.srt> [output.html]
# 生成的 output.html 可直接在任何浏览器中打开浏览，完全自包含、离线可用！
```

---

## 🤖 作为 Antigravity Skill 使用 (Agent Usage)

本项目原生支持作为 **Google DeepMind Antigravity** 及兼容 AI 编码助手的 Skill：

1. **全局安装**：
   ```bash
   mkdir -p ~/.gemini/config/skills/
   git clone https://github.com/XueshiQiao/youtube-interview-processor.git ~/.gemini/config/skills/youtube-interview-processor
   ```

2. **项目中调用**：
   向任何支持 Antigravity Customization 的 Agent 发送请求：
   > “*帮我处理这个 YouTube 访谈视频并提取核心洞察：`<URL>`*”

Agent 将自动发现并调用该 Skill，端到端完成下载、去重、长句重组、上下文翻译与 HTML 对话录生成。

---

## 📄 开源协议 (License)

本项目采用 [MIT License](LICENSE) 开源协议。
