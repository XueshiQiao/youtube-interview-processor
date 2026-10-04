import json
import re

speaker_map = {
    (1, 2): 'Greg Brockman',
    (3, 3): '主持人 (Host)',
    (4, 7): 'Greg Brockman',
    (8, 10): '主持人 (Host)',
    (11, 11): 'Greg Brockman',
    (12, 13): '主持人 (Host)',
    (14, 14): 'Greg Brockman',
    (15, 18): '主持人 (Host)',
    (19, 25): 'Greg Brockman',
    (26, 28): '主持人 (Host)',
    (29, 36): 'Greg Brockman',
    (37, 38): '主持人 (Host)',
    (39, 41): 'Greg Brockman',
    (42, 42): '主持人 (Host)',
    (43, 68): 'Greg Brockman',
    (69, 73): '主持人 (Host)',
    (74, 78): 'Greg Brockman',
    (79, 79): '主持人 (Host)',
    (80, 82): 'Greg Brockman',
    (83, 83): '主持人 (Host)',
    (84, 85): 'Greg Brockman',
    (86, 87): '主持人 (Host)',
    (88, 94): 'Greg Brockman',
    (95, 96): '主持人 (Host)',
    (97, 99): 'Greg Brockman',
    (100, 100): '主持人 (Host)',
    (101, 102): 'Greg Brockman',
    (103, 117): '主持人 (Host)',
    (118, 126): 'Greg Brockman',
    (127, 127): '主持人 (Host)',
    (128, 142): 'Greg Brockman',
    (143, 146): '主持人 (Host)',
    (147, 159): 'Greg Brockman',
    (160, 169): '主持人 (Host)',
    (170, 192): 'Greg Brockman',
    (193, 196): '主持人 (Host)',
    (197, 197): 'Greg Brockman',
    (198, 205): '主持人 (Host)',
    (206, 211): 'Greg Brockman',
    (212, 225): '主持人 (Host)',
    (226, 226): '主持人 (Host)',
    (227, 235): 'Greg Brockman',
    (236, 238): '主持人 (Host)',
    (239, 246): 'Greg Brockman',
    (247, 264): '主持人 (Host)',
    (265, 267): 'Greg Brockman',
    (268, 280): '主持人 (Host)',
    (281, 281): '主持人 (Host)',
    (282, 282): 'Greg Brockman',
    (283, 286): '主持人 (Host)',
    (287, 295): 'Greg Brockman',
    (296, 296): '主持人 (Host)',
    (297, 315): 'Greg Brockman',
    (316, 316): '主持人 (Host)',
    (317, 321): 'Greg Brockman',
    (322, 328): '主持人 (Host)',
    (329, 329): '主持人 (Host)',
    (330, 330): 'Greg Brockman',
    (331, 331): '主持人 (Host)',
    (332, 332): 'Greg Brockman',
}

def get_speaker(idx):
    for (start, end), spk in speaker_map.items():
        if start <= idx <= end:
            return spk
    return 'Greg Brockman'

import sys
import glob
import os

# Resolve input and output file paths dynamically
if len(sys.argv) >= 3:
    en_path = sys.argv[1]
    zh_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(zh_path)[0] + '.html'
else:
    # Auto-detect in current directory
    merged_ens = glob.glob('*.merged.srt')
    merged_zhs = glob.glob('*.merged.zh-Hans.srt')
    if merged_ens and merged_zhs:
        en_path = merged_ens[0]
        zh_path = merged_zhs[0]
        out_path = os.path.splitext(zh_path)[0] + '.html'
    else:
        en_path = 'OpenAI Co-Founder： Start Building With AI Before You Feel Ready ｜ Greg Brockman [qy8Gr27yLMk].merged.srt'
        zh_path = 'OpenAI Co-Founder： Start Building With AI Before You Feel Ready ｜ Greg Brockman [qy8Gr27yLMk].merged.zh-Hans.srt'
        out_path = '访谈精读与核心总结.html'

if not os.path.exists(en_path) or not os.path.exists(zh_path):
    print(f"Error: Missing input SRT files: {en_path} or {zh_path}")
    sys.exit(1)

with open(en_path, 'r', encoding='utf-8') as f:
    en_blocks = f.read().strip().split('\n\n')

with open(zh_path, 'r', encoding='utf-8') as f:
    zh_blocks = f.read().strip().split('\n\n')

single_sentences = []
for eb, zb in zip(en_blocks, zh_blocks):
    e_lines = eb.strip().split('\n')
    z_lines = zb.strip().split('\n')
    idx = int(e_lines[0])
    tc = e_lines[1]
    e_text = '\n'.join(e_lines[2:]).strip()
    z_text = '\n'.join(z_lines[2:]).strip()
    clean_e = re.sub(r'^>>\s*', '', e_text)
    clean_z = re.sub(r'^>>\s*', '', z_text)
    start_t = tc.split(' --> ')[0]
    end_t = tc.split(' --> ')[1]
    
    start_short = start_t.split(',')[0]
    if start_short.startswith('00:'): start_short = start_short[3:]
    
    single_sentences.append({
        'id': idx,
        'tc': tc,
        'short_time': start_short,
        'start_t': start_t,
        'end_t': end_t,
        'speaker': get_speaker(idx),
        'zh': clean_z,
        'en': clean_e
    })

# Merge consecutive sentences by the same speaker into speech turns
speech_turns = []
for s in single_sentences:
    if not speech_turns or speech_turns[-1]['speaker'] != s['speaker']:
        speech_turns.append({
            'turn_id': len(speech_turns) + 1,
            'speaker': s['speaker'],
            'start_t': s['start_t'],
            'end_t': s['end_t'],
            'first_id': s['id'],
            'last_id': s['id'],
            'sentences': [s]
        })
    else:
        speech_turns[-1]['sentences'].append(s)
        speech_turns[-1]['end_t'] = s['end_t']
        speech_turns[-1]['last_id'] = s['id']

for t in speech_turns:
    s_m = t['start_t'].split(',')[0]
    if s_m.startswith('00:'): s_m = s_m[3:]
    e_m = t['end_t'].split(',')[0]
    if e_m.startswith('00:'): e_m = e_m[3:]
    t['time_range'] = f'{s_m} ~ {e_m}'
    
    zh_sents = [s['zh'] for s in t['sentences']]
    en_sents = [s['en'] for s in t['sentences']]
    
    zh_paragraphs = []
    en_paragraphs = []
    chunk_size = 4
    for i in range(0, len(zh_sents), chunk_size):
        zh_paragraphs.append(''.join(zh_sents[i : i + chunk_size]))
        en_paragraphs.append(' '.join(en_sents[i : i + chunk_size]))
        
    t['zh_paragraphs'] = zh_paragraphs
    t['en_paragraphs'] = en_paragraphs
    t['sentence_count'] = len(t['sentences'])

turns_json = json.dumps(speech_turns, ensure_ascii=False)
sentences_json = json.dumps(single_sentences, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenAI 联合创始人 Greg Brockman 深度访谈精读与反共识核心洞察</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              500: '#10b981',
              600: '#059669',
              700: '#047857',
            }},
            darkBg: '#0b0f19',
            darkCard: '#131b2e',
            darkBorder: '#1f293d',
          }}
        }}
      }}
    }}
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
    body {{
      font-family: 'Inter', 'Noto Sans SC', sans-serif;
      background-color: #0b0f19;
      color: #e2e8f0;
    }}
    .text-gradient {{
      background: linear-gradient(135deg, #34d399 0%, #60a5fa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .text-gradient-amber {{
      background: linear-gradient(135deg, #fbbf24 0%, #f87171 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .turn-card:hover {{
      border-color: #3b82f6;
      background-color: #151f36;
    }}
    .highlight-match {{
      background-color: #854d0e;
      color: #fef08a;
      padding: 0 2px;
      border-radius: 2px;
    }}
  </style>
</head>
<body class="min-h-screen bg-[#0b0f19] text-slate-200 antialiased selection:bg-emerald-500 selection:text-white">

  <!-- Header / Navigation -->
  <header class="sticky top-0 z-50 backdrop-blur-xl bg-[#0b0f19]/90 border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center space-x-3">
          <span class="p-2 bg-gradient-to-tr from-emerald-600 to-teal-500 rounded-xl text-white font-bold text-sm shadow-lg shadow-emerald-500/20">AI</span>
          <div>
            <h1 class="font-bold text-slate-100 text-sm sm:text-base leading-tight">Greg Brockman 访谈精读与全景洞察</h1>
            <p class="text-xs text-slate-400">OpenAI 联合创始人兼总裁 · 30分钟长访谈精读</p>
          </div>
        </div>

        <!-- Tab Controls -->
        <div class="flex p-1 bg-slate-900 border border-slate-800 rounded-xl text-xs sm:text-sm font-medium">
          <button id="tab-btn-summary" onclick="switchTab('summary')" class="px-4 py-1.5 rounded-lg transition-all duration-200 bg-emerald-600 text-white shadow-sm flex items-center space-x-1.5">
            <span>⚡</span>
            <span>颠覆性核心洞察</span>
          </button>
          <button id="tab-btn-dialogue" onclick="switchTab('dialogue')" class="px-4 py-1.5 rounded-lg transition-all duration-200 text-slate-400 hover:text-slate-200 flex items-center space-x-1.5">
            <span>📖</span>
            <span>访谈对谈录</span>
            <span class="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded-full text-slate-400">57段</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- ========================================== -->
    <!-- TAB 1: SUMMARY & DEEP CONTRARIAN INSIGHTS -->
    <!-- ========================================== -->
    <div id="section-summary" class="space-y-12 block">

      <!-- Hero Mega Insight Card -->
      <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#131b2e] via-[#0f172a] to-[#111827] border border-emerald-500/30 p-8 sm:p-10 shadow-2xl">
        <div class="absolute -right-20 -top-20 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -left-20 -bottom-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10">
          <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <span>🔥 全片颠覆性总纲（The Mega Insight）</span>
          </div>

          <h2 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-white mb-4 leading-tight">
            做 AI 最大的差距：<span class="text-gradient">不是能力的差距，而是野心的差距！</span>
          </h2>

          <p class="text-base sm:text-lg text-slate-300 leading-relaxed max-w-4xl mb-6">
            在这场访谈中，Greg Brockman 指出了一个震撼行业的心智颠覆：过去做产品，阻碍我们的是技术能力、资金规模与人力门槛；而今天，<strong>AI 已经把“全世界最顶尖的程序员、博士级智囊团”送到了每个人的指尖</strong>。能力的供给端已经被完全拉平并极度溢出，真正拉开人与人、产品与产品差距的唯一瓶颈，是<strong>创作者敢不敢挑战更大构想的“野心天花板”（Ceiling of Ambition）</strong>。
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-800">
            <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div class="text-xs text-emerald-400 font-semibold mb-1">01 / 能力白菜化</div>
              <p class="text-xs text-slate-300">“如果世界上最优秀的程序员随时为你工作，你会让他们做什么？而现在你确实可以做到。”</p>
            </div>
            <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div class="text-xs text-blue-400 font-semibold mb-1">02 / 野心的自我阉割</div>
              <p class="text-xs text-slate-300">大多数人只敢让 AI 写一封邮件、改一段文案，把博士级智能当成打字机，这是对 AI 潜能的最大浪费。</p>
            </div>
            <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div class="text-xs text-purple-400 font-semibold mb-1">03 / 提高野心上限</div>
              <p class="text-xs text-slate-300">“退一步想一想：我能不能要求 AI 去做一件稍微比它过去为我做过的更有野心的事情？”</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 5 Core Contrarian Insights -->
      <div>
        <div class="flex items-center space-x-3 mb-6">
          <h3 class="text-xl font-bold text-white">⚡ 深度扫描：5 大反常识与颠覆性动作</h3>
          <span class="text-xs text-slate-400">穿透表面流水账，直击行业底层真相</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          <!-- Contrarian 1 -->
          <div class="bg-[#131b2e] border border-blue-500/20 p-6 rounded-2xl space-y-3 hover:border-blue-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-blue-500/10 text-blue-400 rounded-md text-xs font-bold">反常识 01</span>
              <button onclick="jumpToTurn(3)" class="text-[11px] text-slate-400 hover:text-blue-400 font-mono">⏱️ 00:14 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">顶尖程序员的自杀式剥离：手写代码已死</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：初级码农被替代，但顶级架构师靠深厚技术底蕴依然不可替代，依然要亲自写核心底层。</p>
              <p><strong>【颠覆真相】</strong>：作为全美顶尖工程师（Stripe 前 CTO、OpenAI 联合创始人），Greg 亲口坦言：“我写代码很厉害，但我<strong>彻底不再自己写代码了</strong>”。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-blue-500">
                <strong>核心洞见</strong>：在 AI 时代，继续死守“手写代码”只是一种低效的工匠自嗨。人类在软件开发中的唯一合法身份，只剩下战略意图输入、边界限制与结果评审（Feedback & Guidance）。
              </p>
            </div>
          </div>

          <!-- Contrarian 2 -->
          <div class="bg-[#131b2e] border border-rose-500/20 p-6 rounded-2xl space-y-3 hover:border-rose-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-rose-500/10 text-rose-400 rounded-md text-xs font-bold">反常识 02</span>
              <button onclick="jumpToTurn(33)" class="text-[11px] text-slate-400 hover:text-rose-400 font-mono">⏱️ 14:36 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">对抗模型碾压法则：别去弥补模型的愚蠢</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：创业者整天提心吊胆，生怕 OpenAI 升级新模型把自己的产品碾死（Model Cannibalization）。</p>
              <p><strong>【颠覆真相】</strong>：Greg 直言，市场上的 AI 应用只有两类：一类是“弥补当前模型愚蠢与短板的创可贴”；另一类是“随着模型变聪明能呈指数级扩展的系统”。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-rose-500">
                <strong>核心洞见</strong>：帮模型擦屁股的必死无疑（新模型一出立即失效）；真正的护城河是把身家押在“下一代模型越聪明，我的壁垒反而越厚”的深层业务闭环上。
              </p>
            </div>
          </div>

          <!-- Contrarian 3 -->
          <div class="bg-[#131b2e] border border-amber-500/20 p-6 rounded-2xl space-y-3 hover:border-amber-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-amber-500/10 text-amber-400 rounded-md text-xs font-bold">反常识 03</span>
              <button onclick="jumpToTurn(47)" class="text-[11px] text-slate-400 hover:text-amber-400 font-mono">⏱️ 25:48 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">“5次重复”铁律：人工肉身跑通前，严禁自动化</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：搞 Agent 的人热衷于一上来就搞全自动多智能体编排，把一切流程自动化。</p>
              <p><strong>【颠覆真相】</strong>：Greg 在访谈中提出了一条极为朴素却价值千金的硬性法则：“一项任务，必须人类自己肉身完整地手工操作 5 次以上，彻底踩平所有细节与痛点，才允许写 Agent 来接管它”。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-amber-500">
                <strong>核心洞见</strong>：没有经过人工验证闭环的自动化，只是在全速放大混乱（Automating Chaos）。绝大多数 Agent 项目的暴毙，都是死于过早自动化。
              </p>
            </div>
          </div>

          <!-- Contrarian 4 -->
          <div class="bg-[#131b2e] border border-purple-500/20 p-6 rounded-2xl space-y-3 hover:border-purple-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-purple-500/10 text-purple-400 rounded-md text-xs font-bold">反常识 04</span>
              <button onclick="jumpToTurn(11)" class="text-[11px] text-slate-400 hover:text-purple-400 font-mono">⏱️ 02:11 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">产品溢价法则：用户极度讨厌“模型选择器”</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：AI 软件界面越花哨、参数滑块越多、支持切换的模型越多，越显得功能强大、专业。</p>
              <p><strong>【颠覆真相】</strong>：Greg 痛批：凡是让用户去调 Temperature、选择模型下拉框的，都是在把研发的偷懒和认知成本转嫁给用户。用户极度厌恶复杂界面。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-purple-500">
                <strong>核心洞见</strong>：真正的溢价来自极致简约与“主动多想一步（Proactive）”。AI 知道自己能做什么，直接主动为用户交付成套结果，这才是唯一值得付费的体验。
              </p>
            </div>
          </div>

          <!-- Contrarian 5 -->
          <div class="bg-[#131b2e] border border-emerald-500/20 p-6 rounded-2xl space-y-3 hover:border-emerald-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-md text-xs font-bold">反常识 05</span>
              <button onclick="jumpToTurn(9)" class="text-[11px] text-slate-400 hover:text-emerald-400 font-mono">⏱️ 01:18 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">深度用户的“3个场景法则”与留存陷阱</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：只要把用户引流进来体验一次对话，就能自然留存并产生高粘性。</p>
              <p><strong>【颠覆真相】</strong>：ChatGPT 虽然每周有超 10 亿用户，但绝大多数停留在单一场景，留存极其脆弱。内部数据铁律表明：用户必须在 <strong>3 个完全不同的独立业务场景</strong>中体会到 AI 的价值，才会跃升为不可逆的高粘性深度用户（Power User）。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-emerald-500">
                <strong>核心洞见</strong>：创业者的全副精力，不该花在单点炫技上，而应该全力为用户铺设“跨过第 2 和第 3 个场景”的无摩擦通路。
              </p>
            </div>
          </div>

          <!-- Contrarian 6 -->
          <div class="bg-[#131b2e] border border-teal-500/20 p-6 rounded-2xl space-y-3 hover:border-teal-500/40 transition">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 bg-teal-500/10 text-teal-400 rounded-md text-xs font-bold">反常识 06</span>
              <button onclick="jumpToTurn(49)" class="text-[11px] text-slate-400 hover:text-teal-400 font-mono">⏱️ 26:26 ↗</button>
            </div>
            <h4 class="font-bold text-slate-100 text-base">自动化的终极底线：人类主导权不可让渡</h4>
            <div class="text-xs text-slate-400 leading-relaxed space-y-2">
              <p><strong>【大众共识】</strong>：AI 发展到终局，人类应该完全躺平，让 AGI 接管全公司的战略决策与自动化运转。</p>
              <p><strong>【颠覆真相】</strong>：当被问到“哪些东西永远不该自动化”时，Greg 斩钉截铁：在最终使命、伦理治理和价值裁决上，<strong>人类必须拥有绝对的控制权与主导地位（Human-in-the-loop）</strong>。</p>
              <p class="text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border-l-2 border-teal-500">
                <strong>核心洞见</strong>：AI 是放大人类雄心的杠杆，而不是代替人类思考的大脑。放弃最终决策权，等于放弃了人类存在的全部价值。
              </p>
            </div>
          </div>

        </div>
      </div>

      <!-- 6 Chapters Timeline Deep Dive -->
      <div class="space-y-6">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h3 class="text-xl font-bold text-white">📑 访谈 6 大主题全景深度拆解</h3>
            <p class="text-xs text-slate-400">时间轴覆盖 · 核心矛盾探讨 · 关键结论 · 对应发言篇章一键跳转</p>
          </div>
        </div>

        <div class="space-y-6">

          <!-- Chapter 1 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-bold">第 1 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">创业复兴与“应用缺口”困境</h4>
              </div>
              <button onclick="jumpToTurn(1)" class="text-xs text-slate-400 hover:text-emerald-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 00:00 - 03:08</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心矛盾</strong>：诺贝尔经济学奖得主向主持人发问：基座模型已经如此强大，为什么实际落地的爆款应用依然匮乏？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>ChatGPT 每周已有超 10 亿活跃用户，3 亿人用于健康咨询，但绝大部分仅仅是“触碰到了皮毛”。</li>
                <li>留存拐点在“3 个独立用例”：创业者的最大机会在于填补从通用大模型到特定极简任务之间的空白，让用户无需摸索就能解决实际痛点。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-emerald-500 text-xs text-slate-300 italic">
                “我们将迎来一场创业的复兴。我认为这即将到来，在未来一到两年内会真正爆发。”
              </div>
            </div>
          </div>

          <!-- Chapter 2 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-lg text-xs font-bold">第 2 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">软件工程范式颠覆：从写代码到指导代码</h4>
              </div>
              <button onclick="jumpToTurn(3)" class="text-xs text-slate-400 hover:text-blue-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 03:08 - 07:56</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心矛盾</strong>：新模型每半年升级一次，开发者如何构建软件才不会被下一代模型淘汰（Obsolete）？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>Greg 个人工作流转变：自己不再写代码，完全变为指导 AI、审查代码、提供战略指引。</li>
                <li>如何抗击模型淘汰：不要构建薄如蝉翼的模型 API 套壳（Wrapper）。必须把 AI 深度嵌入到具备真实用户数据、业务闭环和高粘性流程的系统中；底层模型越聪明，你的系统越强大。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-blue-500 text-xs text-slate-300 italic">
                “我编写软件的能力还不错。但我现在不再自己写代码了，我指导 AI 来编写软件，我会提供大量的反馈和指导。”
              </div>
            </div>
          </div>

          <!-- Chapter 3 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-purple-500/10 border border-purple-500/30 text-purple-400 rounded-lg text-xs font-bold">第 3 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">小微企业赋能与“野心的天花板”</h4>
              </div>
              <button onclick="jumpToTurn(26)" class="text-xs text-slate-400 hover:text-purple-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 07:56 - 10:48</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心矛盾</strong>：没有技术背景、资金有限的普通小企业和创作者，如何借助 AI 重塑自己的商业模式？现在的瓶颈究竟在哪里？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>顶级智力资产平民化：原本大企业高薪聘请的博士级专家、顾问与开发团队，现在直接向每一个人开放。</li>
                <li>瓶颈是野心，而不是能力：很多人只把 AI 当成帮自己写文案的助手，而不敢去设想重塑整条生产线。“我们真正需要做的是提高野心的上限”。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-purple-500 text-xs text-slate-300 italic">
                “我完全同意，我认为这真正关乎我们所有人都可以去抬高我们野心的天花板（Raise the ceiling of ambition）！”
              </div>
            </div>
          </div>

          <!-- Chapter 4 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-lg text-xs font-bold">第 4 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">什么样的 AI 应用值得付费？极简主义即溢价</h4>
              </div>
              <button onclick="jumpToTurn(29)" class="text-xs text-slate-400 hover:text-amber-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 10:48 - 16:28</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心矛盾</strong>：OpenAI 官方在生产力领域做了这么多，初创公司到底能靠什么让用户心甘情愿掏钱？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>用户对复杂工具感到疲惫：不要让用户去调节 temperature、选择模型分支、处理繁琐参数。</li>
                <li>价值在于“预判与主动性”（Proactive）：AI 知道自己的能力，并能在对话中主动提议：“你让我做这件事，其实我可以直接为你生成全套汇报和表格”，这种省心体验最具商业价值。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-amber-500 text-xs text-slate-300 italic">
                “你希望从 AI 中得到的是简单易用。你不想看到一个满是按钮、滑块和模型选择器的界面。”
              </div>
            </div>
          </div>

          <!-- Chapter 5 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-lg text-xs font-bold">第 5 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">智能体（Agent）范式与自动化的边界</h4>
              </div>
              <button onclick="jumpToTurn(35)" class="text-xs text-slate-400 hover:text-rose-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 16:28 - 27:04</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心矛盾</strong>：如何避免把 Agent 做成毫无实用价值的玩具？在全面自动化的浪潮中，底线是什么？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>告别玩具型 Agent：单纯抓取新闻给总结的“晨报 Agent”是浅层的，真正有价值的 Agent 必须具备工具调用与环境交互能力，能自主解决复杂工程问题。</li>
                <li>人类控制权不容动摇：在涉及战略、价值观、伦理和责任归属的终极决策上，人类必须拥有完全控制权（Human-in-the-loop）。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-rose-500 text-xs text-slate-300 italic">
                “人类必须始终保持控制和主导地位。自动化是为了赋能人类，让人类按照想要的方式生活，而不是剥夺决策权。”
              </div>
            </div>
          </div>

          <!-- Chapter 6 -->
          <div class="bg-[#131b2e] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-teal-500/10 border border-teal-500/30 text-teal-400 rounded-lg text-xs font-bold">第 6 章</span>
                <h4 class="text-base sm:text-lg font-bold text-white">给普通开发者的周末行动指南</h4>
              </div>
              <button onclick="jumpToTurn(50)" class="text-xs text-slate-400 hover:text-teal-400 font-mono bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 flex items-center space-x-1">
                <span>⏱️ 27:04 - 30:15</span>
                <span>查看对话篇章 ↗</span>
              </button>
            </div>

            <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2">
              <p><strong>核心提问</strong>：如果一个人只有周末 1 小时的时间，想提升自己的 Agent 能力，应该从何处着手？</p>
              <p><strong>Greg Brockman 核心结论</strong>：</p>
              <ul class="list-disc list-inside text-slate-400 space-y-1 pl-1">
                <li>挑一个本周真正在工作中让你头疼、重复、枯燥的具体小痛点。</li>
                <li>不要等到看完全部文档或感觉准备好才开始动手。利用现成的 LLM 搭建一个哪怕只有 3 个步骤的自动化闭环。</li>
                <li>当你的小工具第一次为你节省了 10 分钟，你的“野心”就会被瞬间点燃。</li>
              </ul>
              <div class="p-3 bg-slate-900/80 rounded-xl border-l-4 border-teal-500 text-xs text-slate-300 italic">
                “这个周末我们的作业，不仅要在智能体（Agent）上下功夫，更要在我们的野心（Ambition）上下功夫！”
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>

    <!-- ========================================== -->
    <!-- TAB 2: INTERACTIVE DIALOGUE STREAM         -->
    <!-- ========================================== -->
    <div id="section-dialogue" class="space-y-6 hidden">
      
      <!-- Sticky Filter & View Mode Toolbar -->
      <div class="sticky top-20 z-40 bg-[#0f172a]/95 backdrop-blur border border-slate-800 p-4 rounded-2xl shadow-xl space-y-3">
        <div class="flex flex-col lg:flex-row gap-3 items-center justify-between">
          <!-- Search input -->
          <div class="relative w-full lg:w-80">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">🔍</span>
            <input type="text" id="dialogue-search" oninput="filterDialogue()" placeholder="搜索关键词（如：野心, 博士, 代码, 5次, 愚蠢）..." class="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition">
          </div>

          <!-- Controls: View Mode & Speaker & English Toggle -->
          <div class="flex flex-wrap items-center gap-2 text-xs w-full lg:w-auto">
            <!-- View Mode Switcher -->
            <div class="flex p-0.5 bg-slate-900 border border-slate-800 rounded-lg">
              <button onclick="setViewMode('turns')" id="btn-mode-turns" class="px-2.5 py-1 rounded-md bg-emerald-600 text-white font-medium">📖 对话篇章 (57段)</button>
              <button onclick="setViewMode('sentences')" id="btn-mode-sentences" class="px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200">🎬 逐句单行 (332句)</button>
            </div>

            <!-- English Display Toggle -->
            <button onclick="toggleEnglish()" id="btn-toggle-en" class="px-2.5 py-1 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-700 flex items-center space-x-1">
              <span>🌐</span>
              <span id="text-toggle-en">显示英文对照</span>
            </button>

            <!-- Speaker Filter -->
            <div class="flex p-0.5 bg-slate-900 border border-slate-800 rounded-lg">
              <button onclick="setSpeakerFilter('all')" id="filter-btn-all" class="px-2.5 py-1 rounded-md bg-emerald-600 text-white font-medium">全部</button>
              <button onclick="setSpeakerFilter('greg')" id="filter-btn-greg" class="px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200">仅看 Greg</button>
              <button onclick="setSpeakerFilter('host')" id="filter-btn-host" class="px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200">仅看主持人</button>
            </div>
          </div>
        </div>

        <!-- Quick Anchor Badges -->
        <div class="flex items-center space-x-2 text-[11px] overflow-x-auto text-slate-400 pt-1 border-t border-slate-800/80">
          <span class="whitespace-nowrap font-semibold text-slate-500">速通索引：</span>
          <button onclick="jumpToTurn(1)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 开场复兴 [00:00]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(3)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 指挥AI写代码 [00:14]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(9)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 3个用例法则 [01:18]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(27)" class="whitespace-nowrap text-emerald-400 font-medium bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/50">🔥 野心的天花板 [09:54]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(33)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 别弥补模型的愚蠢 [14:36]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(47)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 5次重复法则 [25:48]</button>
          <span class="text-slate-700">•</span>
          <button onclick="jumpToTurn(50)" class="whitespace-nowrap hover:text-emerald-400">⏱️ 周末1小时起步 [27:04]</button>
        </div>
      </div>

      <!-- Dialogue List Container -->
      <div id="dialogue-container" class="space-y-4">
        <!-- Rendered by JavaScript -->
      </div>

    </div>

  </main>

  <!-- Back to top button -->
  <button id="back-to-top" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})" class="fixed bottom-6 right-6 p-3 bg-emerald-600 text-white rounded-full shadow-2xl hover:bg-emerald-500 transition opacity-0 pointer-events-none z-50">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>
  </button>

  <script>
    const turnsData = {turns_json};
    const sentencesData = {sentences_json};
    let viewMode = 'turns';
    let showEnglish = true;
    let currentSpeakerFilter = 'all';
    let searchQuery = '';

    function switchTab(tab) {{
      const summarySec = document.getElementById('section-summary');
      const dialogueSec = document.getElementById('section-dialogue');
      const btnSummary = document.getElementById('tab-btn-summary');
      const btnDialogue = document.getElementById('tab-btn-dialogue');

      if (tab === 'summary') {{
        summarySec.classList.remove('hidden');
        dialogueSec.classList.add('hidden');
        btnSummary.className = "px-4 py-1.5 rounded-lg transition-all duration-200 bg-emerald-600 text-white shadow-sm flex items-center space-x-1.5";
        btnDialogue.className = "px-4 py-1.5 rounded-lg transition-all duration-200 text-slate-400 hover:text-slate-200 flex items-center space-x-1.5";
      }} else {{
        summarySec.classList.add('hidden');
        dialogueSec.classList.remove('hidden');
        btnDialogue.className = "px-4 py-1.5 rounded-lg transition-all duration-200 bg-emerald-600 text-white shadow-sm flex items-center space-x-1.5";
        btnSummary.className = "px-4 py-1.5 rounded-lg transition-all duration-200 text-slate-400 hover:text-slate-200 flex items-center space-x-1.5";
        renderDialogue();
      }}
    }}

    function setViewMode(mode) {{
      viewMode = mode;
      document.getElementById('btn-mode-turns').className = mode === 'turns' ? "px-2.5 py-1 rounded-md bg-emerald-600 text-white font-medium" : "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200";
      document.getElementById('btn-mode-sentences').className = mode === 'sentences' ? "px-2.5 py-1 rounded-md bg-emerald-600 text-white font-medium" : "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200";
      renderDialogue();
    }}

    function toggleEnglish() {{
      showEnglish = !showEnglish;
      document.getElementById('text-toggle-en').innerText = showEnglish ? "隐藏英文对照" : "显示英文对照";
      renderDialogue();
    }}

    function setSpeakerFilter(filter) {{
      currentSpeakerFilter = filter;
      ['all', 'greg', 'host'].forEach(f => {{
        const btn = document.getElementById('filter-btn-' + f);
        if (btn) {{
          btn.className = f === filter ? "px-2.5 py-1 rounded-md bg-emerald-600 text-white font-medium" : "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200";
        }}
      }});
      renderDialogue();
    }}

    function filterDialogue() {{
      searchQuery = document.getElementById('dialogue-search').value.trim().toLowerCase();
      renderDialogue();
    }}

    function highlightText(text, query) {{
      if (!query) return text;
      const regex = new RegExp(`(${{query.replace(/[-\\/\\\\^$*+?.()|[\\]{{}}]/g, '\\\\$&')}})`, 'gi');
      return text.replace(regex, '<span class="highlight-match">$1</span>');
    }}

    function renderDialogue() {{
      const container = document.getElementById('dialogue-container');

      if (viewMode === 'turns') {{
        const filteredTurns = turnsData.filter(turn => {{
          if (currentSpeakerFilter === 'greg' && !turn.speaker.includes('Greg')) return false;
          if (currentSpeakerFilter === 'host' && !turn.speaker.includes('Host') && !turn.speaker.includes('主持人')) return false;
          if (searchQuery) {{
            const inZh = turn.zh_paragraphs.some(p => p.toLowerCase().includes(searchQuery));
            const inEn = turn.en_paragraphs.some(p => p.toLowerCase().includes(searchQuery));
            if (!inZh && !inEn) return false;
          }}
          return true;
        }});

        if (filteredTurns.length === 0) {{
          container.innerHTML = `<div class="text-center py-16 text-slate-500">没有找到匹配的对话篇章。</div>`;
          return;
        }}

        container.innerHTML = filteredTurns.map(turn => {{
          const isGreg = turn.speaker.includes('Greg');
          const badgeColor = isGreg ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-blue-500/10 border-blue-500/30 text-blue-400';
          const speakerIcon = isGreg ? '🤖' : '🎙️';
          const roleTitle = isGreg ? 'OpenAI 联合创始人兼总裁' : '科技访谈主持人';

          const zhHtmls = turn.zh_paragraphs.map(p => `<p class="mb-3 last:mb-0 leading-relaxed text-slate-100 text-sm sm:text-base font-normal tracking-wide">${{highlightText(p, searchQuery)}}</p>`).join('');
          
          let enHtmlSection = '';
          if (showEnglish) {{
            const enHtmls = turn.en_paragraphs.map(p => `<p class="mb-2 last:mb-0 leading-relaxed text-slate-400 text-xs sm:text-sm font-light italic">${{highlightText(p, searchQuery)}}</p>`).join('');
            enHtmlSection = `<div class="mt-4 pt-3 border-t border-slate-800/80 bg-slate-900/40 -mx-5 -mb-5 p-5 rounded-b-2xl border-dashed">${{enHtmls}}</div>`;
          }}

          return `
            <div id="turn-${{turn.turn_id}}" class="turn-card bg-[#131b2e] border border-slate-800 rounded-2xl p-6 transition-all duration-200">
              <div class="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-800/70">
                <div class="flex items-center space-x-2.5">
                  <span class="text-xl">${{speakerIcon}}</span>
                  <div>
                    <div class="flex items-center space-x-2">
                      <span class="font-bold text-sm sm:text-base text-slate-100">${{turn.speaker}}</span>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${{badgeColor}}">${{isGreg ? '嘉宾' : '主持人'}}</span>
                    </div>
                    <div class="text-[11px] text-slate-400">${{roleTitle}}</div>
                  </div>
                </div>

                <div class="flex items-center space-x-2 text-xs font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800">
                  <span>⏱️ ${{turn.time_range}}</span>
                  <span>•</span>
                  <span class="text-slate-500">${{turn.sentence_count}} 句整句</span>
                </div>
              </div>

              <div class="text-slate-100">
                ${{zhHtmls}}
              </div>

              ${{enHtmlSection}}
            </div>
          `;
        }}).join('');

      }} else {{
        const filteredSentences = sentencesData.filter(item => {{
          if (currentSpeakerFilter === 'greg' && !item.speaker.includes('Greg')) return false;
          if (currentSpeakerFilter === 'host' && !item.speaker.includes('Host') && !item.speaker.includes('主持人')) return false;
          if (searchQuery) {{
            const inZh = item.zh.toLowerCase().includes(searchQuery);
            const inEn = item.en.toLowerCase().includes(searchQuery);
            if (!inZh && !inEn) return false;
          }}
          return true;
        }});

        if (filteredSentences.length === 0) {{
          container.innerHTML = `<div class="text-center py-16 text-slate-500">没有找到匹配的单句字幕。</div>`;
          return;
        }}

        container.innerHTML = filteredSentences.map(item => {{
          const isGreg = item.speaker.includes('Greg');
          const badgeColor = isGreg ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-blue-500/10 border-blue-500/30 text-blue-400';
          const speakerIcon = isGreg ? '🤖' : '🎙️';
          const zhHtml = highlightText(item.zh, searchQuery);
          const enHtml = highlightText(item.en, searchQuery);

          let enBlock = '';
          if (showEnglish) {{
            enBlock = `<p class="text-xs text-slate-400 font-light leading-relaxed border-t border-slate-800/80 pt-2 italic">${{enHtml}}</p>`;
          }}

          return `
            <div id="dlg-${{item.id}}" class="turn-card bg-[#131b2e] border border-slate-800 rounded-xl p-4 transition-all duration-200">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <span class="text-sm">${{speakerIcon}}</span>
                  <span class="font-bold text-xs text-slate-200">${{item.speaker}}</span>
                  <span class="text-[10px] font-mono px-1.5 py-0.2 rounded-full border ${{badgeColor}}">${{isGreg ? '嘉宾' : '主持'}}</span>
                </div>
                <div class="flex items-center space-x-2 text-xs font-mono text-slate-500">
                  <span>#${{item.id}}</span>
                  <span>•</span>
                  <span class="text-slate-400">${{item.short_time}}</span>
                </div>
              </div>
              <p class="text-sm text-slate-100 font-normal leading-relaxed mb-2">${{zhHtml}}</p>
              ${{enBlock}}
            </div>
          `;
        }}).join('');
      }}
    }}

    function jumpToTurn(turnId) {{
      switchTab('dialogue');
      setViewMode('turns');
      setSpeakerFilter('all');
      document.getElementById('dialogue-search').value = '';
      searchQuery = '';
      renderDialogue();

      setTimeout(() => {{
        const el = document.getElementById('turn-' + turnId);
        if (el) {{
          el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
          el.classList.add('ring-2', 'ring-emerald-400', 'bg-emerald-950/40');
          setTimeout(() => {{
            el.classList.remove('ring-2', 'ring-emerald-400', 'bg-emerald-950/40');
          }}, 3000);
        }}
      }}, 150);
    }}

    window.addEventListener('scroll', () => {{
      const btn = document.getElementById('back-to-top');
      if (window.scrollY > 400) {{
        btn.classList.remove('opacity-0', 'pointer-events-none');
        btn.classList.add('opacity-100');
      }} else {{
        btn.classList.add('opacity-0', 'pointer-events-none');
        btn.classList.remove('opacity-100');
      }}
    }});
  </script>
</body>
</html>'''

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'Successfully generated: {out_path}')
