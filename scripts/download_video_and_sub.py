#!/usr/bin/env python3
"""
YouTube Video and Standalone Subtitle Downloader with Pre-flight Check & Live Progress
- Detects system environment (Python, yt-dlp, installed browsers)
- Interactive/CLI-driven browser selection (Chrome, Safari, Firefox, Edge)
- Auto-fallback if cookie database is locked
- Prints clear visual pipeline roadmap and step-by-step progress
"""

import sys
import os
import shutil
import subprocess
import argparse

def print_pipeline_roadmap(current_step=1):
    steps = [
        ("1/5", "🛠️ 环境预检与配置确认 (Pre-flight Check & Configuration)"),
        ("2/5", "⬇️ 视频与独立原声字幕下载 (Media & Standalone Subtitle Download)"),
        ("3/5", "🧹 滚动去重与语义长句重构 (Deduplication & Sentence Restructure)"),
        ("4/5", "🌐 上下文感知滑动窗口翻译 (Context-Aware Translation)"),
        ("5/5", "⚡ 4维反共识提炼与交互网页生成 (Contrarian Insights & HTML Dashboard)"),
    ]
    
    print("\n" + "=" * 68)
    print("🎬 YouTube Interview Processor 全流程流水线状态看板")
    print("=" * 68)
    for num, title in steps:
        step_idx = int(num.split("/")[0])
        if step_idx < current_step:
            status = "✅ 已完成"
            color_mark = "  "
        elif step_idx == current_step:
            status = "▶️ 进行中"
            color_mark = "👉"
        else:
            status = "⏳ 待执行"
            color_mark = "  "
        print(f"{color_mark} [{num}] {title.ljust(48)} [{status}]")
    print("=" * 68 + "\n")

def detect_available_browsers():
    """检测当前操作系统安装的主流浏览器"""
    browsers = []
    # macOS 应用程序检测
    mac_apps = {
        'chrome': '/Applications/Google Chrome.app',
        'safari': '/Applications/Safari.app',
        'firefox': '/Applications/Firefox.app',
        'edge': '/Applications/Microsoft Edge.app',
        'arc': '/Applications/Arc.app',
        'brave': '/Applications/Brave Browser.app'
    }
    for b_name, path in mac_apps.items():
        if os.path.exists(path):
            browsers.append(b_name)
            
    # 通用 PATH 二进制检测
    for b in ['google-chrome', 'chromium', 'firefox', 'microsoft-edge']:
        if shutil.which(b) and b not in browsers:
            browsers.append(b)
    return browsers

def ensure_dependencies():
    """检测 yt-dlp，缺失时尝试自动安装"""
    if shutil.which("yt-dlp"):
        return True, "已就绪"

    print("⚠️ [依赖预检] 系统中未检测到 'yt-dlp'。正在尝试为您自动安装...")
    # 1. 尝试 pip 安装
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if shutil.which("yt-dlp"):
            return True, "已通过 pip 自动安装成功"
    except Exception:
        pass

    # 2. 尝试 brew 安装 (macOS)
    if shutil.which("brew"):
        try:
            subprocess.run(["brew", "install", "yt-dlp"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if shutil.which("yt-dlp"):
                return True, "已通过 Homebrew 自动安装成功"
        except Exception:
            pass

    return False, "未安装，请执行 brew install yt-dlp 或 pip install yt-dlp"

def run_preflight_check(output_dir=".", preferred_browser=None):
    """阶段 1：环境预检与系统配置检查"""
    print_pipeline_roadmap(current_step=1)
    print("🔍 [阶段 1/5] 正在执行系统环境与前置依赖预检...")
    
    # 1. Python 环境
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  • Python 运行环境: v{py_ver} ({sys.executable}) [✅ 通过]")

    # 2. yt-dlp 检测
    ytdlp_ok, ytdlp_msg = ensure_dependencies()
    if ytdlp_ok:
        ytdlp_ver = subprocess.getoutput("yt-dlp --version").strip()
        print(f"  • yt-dlp 下载工具: v{ytdlp_ver} ({ytdlp_msg}) [✅ 通过]")
    else:
        print(f"  • yt-dlp 下载工具: [❌ 失败: {ytdlp_msg}]")
        return False, None

    # 3. 浏览器检测
    detected_browsers = detect_available_browsers()
    browsers_str = ", ".join(b.capitalize() for b in detected_browsers) if detected_browsers else "未检测到主流浏览器"
    print(f"  • 检测到本地浏览器: {browsers_str} [✅ 共 {len(detected_browsers)} 个可用]")

    # 确定使用的 Cookie 源
    chosen_browser = None
    if preferred_browser and preferred_browser.lower() != "none":
        chosen_browser = preferred_browser.lower()
    elif detected_browsers:
        # 默认优先 Chrome，其次 Safari
        chosen_browser = 'chrome' if 'chrome' in detected_browsers else detected_browsers[0]

    if chosen_browser:
        print(f"  • 认证 Cookie 策略: 选用 {chosen_browser.capitalize()} 浏览器 (可通过 --browser 切换) [✅ 就绪]")
    else:
        print(f"  • 认证 Cookie 策略: 无 Cookie 模式 (仅公开高清视频) [ℹ️ 提示]")

    # 4. 存储路径检查
    abs_out = os.path.abspath(output_dir)
    os.makedirs(abs_out, exist_ok=True)
    if os.access(abs_out, os.W_OK):
        print(f"  • 输出目标目录: {abs_out} [✅ 可写入]")
    else:
        print(f"  • 输出目标目录: {abs_out} [❌ 无写入权限]")
        return False, None

    print("\n✅ 环境预检全部通过！系统已做好处理准备。\n")
    return True, chosen_browser

def run_download(url, output_dir=".", browser="auto", sub_only=False, flat=False):
    # 步骤 1：预检
    ok, chosen_browser = run_preflight_check(output_dir, preferred_browser=None if browser == "auto" else browser)
    if not ok:
        sys.exit(1)

    # 步骤 2：下载媒体与独立字幕
    print_pipeline_roadmap(current_step=2)
    print(f"📥 [阶段 2/5] 正在执行视频与独立字幕抓取...")
    print(f"  • 目标视频 URL: {url}")
    print(f"  • 优先字幕轨道: en-orig (原声语音自动转录)")
    print(f"  • 存储隔离规范: 独立 .srt 外挂文件，严禁封装入视频容器")
    print(f"  • 项目目录策略: {'平铺当前目录 (--flat)' if flat else '自动为每个视频创建独立专属子目录 [默认]'}")

    # 检测本地是否有导出的 cookies.txt 备用
    cookie_file = None
    for cand in ["youtube_cookies.txt", os.path.join(output_dir, "youtube_cookies.txt")]:
        if os.path.isfile(cand):
            cookie_file = os.path.abspath(cand)
            break

    # 输出命名模板：默认建立独立子目录
    out_tmpl = "%(title).100B [%(id)s].%(ext)s" if flat else "%(title).100B [%(id)s]/%(title).100B [%(id)s].%(ext)s"

    # 构建字幕下载指令
    sub_cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en-orig,en",
        "--convert-subs", "srt",
        "-P", output_dir,
        "-o", out_tmpl,
        url
    ]
    if chosen_browser:
        sub_cmd.extend(["--cookies-from-browser", chosen_browser])

    print("\n[2.1/2] 正在拉取独立字幕轨道...")
    sub_ok = False
    try:
        subprocess.run(sub_cmd, check=True)
        print("✅ 原始字幕 (.srt) 下载就绪！")
        sub_ok = True
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️ 使用 {chosen_browser} 浏览器 Cookie 拉取字幕受阻: {e}")
        # 如果有 cookies.txt，优先尝试 cookies.txt
        if cookie_file:
            print(f"尝试使用本地 Cookie 文件重试: {cookie_file}...")
            sub_cmd_cookiefile = [c for c in sub_cmd if c != chosen_browser and c != "--cookies-from-browser"]
            sub_cmd_cookiefile.extend(["--cookies", cookie_file])
            try:
                subprocess.run(sub_cmd_cookiefile, check=True)
                print("✅ 使用本地 cookies.txt 拉取字幕成功！")
                sub_ok = True
            except Exception as e_cook:
                print(f"⚠️ 本地 cookies.txt 尝试失败: {e_cook}")

        if not sub_ok:
            print("尝试无 Cookie 模式降级拉取...")
            sub_cmd_nocookie = [c for c in sub_cmd if c != chosen_browser and c != "--cookies-from-browser"]
            try:
                subprocess.run(sub_cmd_nocookie, check=True)
                print("✅ 降级无 Cookie 拉取字幕成功！")
                sub_ok = True
            except Exception as e2:
                print(f"❌ 字幕下载失败: {e2}")

    if not sub_only:
        # 构建视频下载指令 (不封装字幕)
        video_cmd = [
            "yt-dlp",
            "-P", output_dir,
            "-o", out_tmpl,
            url
        ]
        if chosen_browser:
            video_cmd.extend(["--cookies-from-browser", chosen_browser])

        print("\n[2.2/2] 正在下载视频文件...")
        video_ok = False
        try:
            subprocess.run(video_cmd, check=True)
            print("✅ 视频源文件下载完成！")
            video_ok = True
        except subprocess.CalledProcessError as e:
            print(f"\n⚠️ 视频下载遇到异常: {e}")
            if cookie_file:
                print(f"尝试使用本地 Cookie 文件下载视频: {cookie_file}...")
                video_cmd_cookiefile = [c for c in video_cmd if c != chosen_browser and c != "--cookies-from-browser"]
                video_cmd_cookiefile.extend(["--cookies", cookie_file])
                try:
                    subprocess.run(video_cmd_cookiefile, check=True)
                    print("✅ 使用本地 cookies.txt 下载视频成功！")
                    video_ok = True
                except Exception as e_cook:
                    print(f"⚠️ 本地 cookies.txt 下载视频失败: {e_cook}")

            if not video_ok:
                print("尝试无 Cookie 模式降级重试...")
                video_cmd_nocookie = [c for c in video_cmd if c != chosen_browser and c != "--cookies-from-browser"]
                try:
                    subprocess.run(video_cmd_nocookie, check=True)
                    print("✅ 视频源文件降级下载成功！")
                except Exception as e2:
                    print(f"❌ 视频下载失败: {e2}")
                    sys.exit(1)
    else:
        print("\nℹ️ 已开启 --sub-only 仅字幕模式，跳过视频文件下载。")

    # 扫描与汇报生成的项目目录
    target_abs = os.path.abspath(output_dir)
    found_folder = target_abs
    found_srt = None
    found_video = None

    if not flat:
        # 寻找最近更新的子目录
        subdirs = [os.path.join(target_abs, d) for d in os.listdir(target_abs)
                   if os.path.isdir(os.path.join(target_abs, d)) and not d.startswith('.') and d != '__pycache__']
        if subdirs:
            subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            found_folder = subdirs[0]

    for root, dirs, files in os.walk(found_folder):
        for f in files:
            if f.endswith('.srt') and not found_srt:
                found_srt = os.path.join(root, f)
            elif any(f.endswith(ext) for ext in ['.mp4', '.webm', '.mkv']) and not found_video:
                found_video = os.path.join(root, f)

    print("\n" + "=" * 68)
    print(f"📂 专属项目目录: {found_folder}")
    if found_srt:
        print(f"📄 原始字幕文件: {found_srt}")
    if found_video:
        print(f"🎥 视频源文件:   {found_video}")
    print("=" * 68)
    print("\n🎉 [阶段 2/5] 媒体与字幕抓取全部完成！已准备好进入 [阶段 3: 滚动去重与语义长句重构]。\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube 访谈视频与独立原声字幕全自动下载器")
    parser.add_argument("url", nargs="?", help="YouTube 视频链接 (如 https://www.youtube.com/watch?v=...)")
    parser.add_argument("output_dir", nargs="?", default=".", help="文件保存目录 (默认为当前目录)")
    parser.add_argument("--browser", default="auto", help="Cookie 来源浏览器: chrome, safari, firefox, edge, 或 none (默认自动检测)")
    parser.add_argument("--sub-only", action="store_true", help="仅下载字幕，不下载视频大文件")
    parser.add_argument("--flat", action="store_true", help="不创建独立子目录，直接平铺在 output_dir")
    parser.add_argument("--check-only", action="store_true", help="仅运行阶段 1 环境预检，不下载任何内容")

    args = parser.parse_args()

    if args.check_only:
        run_preflight_check(args.output_dir, preferred_browser=args.browser)
        sys.exit(0)

    if not args.url:
        print("使用帮助: python3 download_video_and_sub.py <YouTube_URL> [output_dir] [--browser chrome/safari/none] [--sub-only] [--flat] [--check-only]")
        sys.exit(1)

    run_download(args.url, args.output_dir, browser=args.browser, sub_only=args.sub_only, flat=args.flat)
