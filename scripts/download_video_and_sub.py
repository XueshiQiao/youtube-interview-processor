#!/usr/bin/env python3
"""
YouTube Video and Standalone Subtitle Downloader
- Downloads standalone video and separate .srt subtitle (no container embedding)
- Prioritizes 'en-orig' auto-captions
- Includes robust error diagnosis and user-friendly troubleshooting advice
"""

import sys
import os
import shutil
import subprocess

def ensure_dependencies():
    if shutil.which("yt-dlp"):
        return

    print("\n⚠️ [依赖检测] 系统中未检测到 'yt-dlp' 命令行工具。")
    print("🚀 正在为您自动安装 'yt-dlp' 依赖...")

    # 1. 优先尝试使用当前 Python 环境的 pip 安装
    try:
        print("-> 正在执行: pip install -U yt-dlp ...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], check=True)
        if shutil.which("yt-dlp"):
            print("✅ 'yt-dlp' 已通过 pip 自动安装成功！\n")
            return
    except Exception as e:
        print(f"   pip 自动安装受阻: {e}")

    # 2. 如果是 macOS 且已安装 Homebrew，尝试使用 brew 安装
    if shutil.which("brew"):
        try:
            print("-> 正在尝试通过 Homebrew 安装: brew install yt-dlp ...")
            subprocess.run(["brew", "install", "yt-dlp"], check=True)
            if shutil.which("yt-dlp"):
                print("✅ 'yt-dlp' 已通过 Homebrew 自动安装成功！\n")
                return
        except Exception as e:
            print(f"   Homebrew 自动安装受阻: {e}")

    # 3. 若自动安装均失败，输出清晰的手动安装指引
    print("\n❌ 自动安装尝试失败，请根据您的操作系统手动执行安装命令：")
    print("   - macOS 推荐: brew install yt-dlp")
    print("   - Python 通用: pip install -U yt-dlp")
    print("   - Linux: sudo apt install yt-dlp 或从 GitHub 下载二进制发布包")
    sys.exit(1)

def run_download(url, output_dir=".", browser_cookies="chrome"):
    ensure_dependencies()
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n[1/2] 正在拉取视频与独立字幕信息: {url}")
    print(f"  - 目标保存目录: {os.path.abspath(output_dir)}")
    print(f"  - 优先拉取字幕语言: en-orig (原声语音转录)")
    print(f"  - 独立字幕模式: 保持 .srt 外部文件，不封装入视频容器")
    
    # 步骤 1: 下载独立字幕 (en-orig, 降级至 en)
    sub_cmd = [
        "yt-dlp",
        "--cookies-from-browser", browser_cookies,
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en-orig,en",
        "--convert-subs", "srt",
        "-P", output_dir,
        url
    ]
    
    print("\n执行字幕下载命令...")
    try:
        subprocess.run(sub_cmd, check=True)
        print("✅ 原始字幕下载完成！")
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️ 字幕下载遇到异常 (返回码 {e.returncode})：")
        print("【故障排查指引】：")
        print("1. 如果报错与 Chrome Cookie 锁死相关：请尝试完全退出 Chrome 浏览器后重试，或去掉 '--cookies-from-browser'。")
        print("2. 如果该视频未提供 'en-orig'：可通过 'yt-dlp --list-subs <URL>' 查看该视频支持的字幕语言。")
        print("3. 如果网络超时：请检查网络连接或代理配置。")
        # 不强制退出，继续尝试下载视频
    
    # 步骤 2: 下载视频文件 (不合并字幕)
    video_cmd = [
        "yt-dlp",
        "--cookies-from-browser", browser_cookies,
        "-P", output_dir,
        url
    ]
    
    print("\n执行视频下载命令...")
    try:
        subprocess.run(video_cmd, check=True)
        print("✅ 视频下载完成！")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 视频下载失败 (返回码 {e.returncode})：")
        print("【故障排查指引】：")
        print("1. 请确认该 YouTube 视频是否为私密/会员专享视频。")
        print("2. 检查存储空间是否充足。")
        sys.exit(e.returncode)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 download_video_and_sub.py <YouTube_URL> [output_dir]")
        sys.exit(1)
    url_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else "."
    run_download(url_arg, out_arg)
