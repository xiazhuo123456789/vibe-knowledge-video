# Vibe 知识大赏 · AI 知识视频制作 Skill

<p align="center">
  <b>把数学、概率、哲学等硬知识，拍成电影感的抖音知识大片</b><br>
  纯代码生成 · 无配音 · 双语字幕 · 历史文献再现 · 动画模拟推演
</p>

<p align="center">
  <img src="https://img.shields.io/badge/style-Vibe%E7%9F%A5%E8%AF%86%E5%A4%A7%E8%B5%8F-0A0A1E" alt="style">
  <img src="https://img.shields.io/badge/render-Canvas%202B%20%2B%20render(t)-C9A96A" alt="render">
  <img src="https://img.shields.io/badge/audio-numpy%20synth%20BGM-76BPM" alt="audio">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
</p>

---

> **这是什么**：一套完整的 Claude / AI Agent 技能（Skill），逆向工程自抖音「Vibe知识大赏」系列爆款知识视频（由 @Iwanau / @Juno / 叁号暗房 用 Claude Opus 5.5 代码生成）。装上它，对 AI 说一句话，就能从选题走到成片 MP4 + 抖音发布文案。
>
> **What is this**: A complete AI-agent skill that reproduces the "Vibe Knowledge Awards" style of viral Douyin explainer videos — 100% code-generated (HTML Canvas + synthesized music), no voiceover, bilingual subtitles, cinematic history-document recreations. Say one sentence, get a finished MP4.

## 🎬 这种视频长什么样

成片规格（逆向自 8 条原片的实测数据）：

| 维度 | 规范 |
|---|---|
| 画幅 | 1920×1080 横屏，30fps |
| 时长 | 2:00–2:45 |
| 声音 | **无旁白配音**，纯器乐 BGM 76–78 BPM（沉静纪录片节奏，numpy 从零合成） |
| 画面 | 深蓝黑底 `#0A0A1E`，五区布局（水印/顶标签/中央动画/注释带/双语字幕带） |
| 密度 | 逐秒运动均值 3.97，静止秒 < 25% —— 画面必须一直在动 |
| 严谨 | 结尾必有学术引用 + 免责声明，历史图示必标"示意图" |

六段叙事弧：**冷开场钩子 → 历史锚点（真实文献再现）→ 机制动画模拟 → 反直觉转折 → 现实落点 → 声明+引用收尾**

## 🚀 快速开始

### 安装到 CodeBuddy / Claude Code

```bash
# 方式一：克隆到技能目录
git clone https://github.com/<你的用户名>/vibe-knowledge-video.git
cp -r vibe-knowledge-video ~/.codebuddy/skills/

# 方式二：项目级安装
cp -r vibe-knowledge-video /path/to/your/project/.codebuddy/skills/
```

### 依赖

| 工具 | 用途 | 说明 |
|---|---|---|
| Python 3.10+ | 渲染/配乐/自检脚本 | `pip install playwright pillow numpy` |
| Playwright + Chromium | 逐帧截图 | `playwright install chromium` |
| ffmpeg | 视频合成 | 需 H.264 编码器（libx264 或 libopenh264，脚本自动检测） |
| tesseract + chi_sim（可选） | QA 时 OCR 校验字幕 | `apt install tesseract-ocr tesseract-ocr-chi-sim` |

### 使用

对装好技能的 AI 说：

```
用 vibe-knowledge-video 做一条《××》的知识视频
```

它会带你走完七步流水线：

```
选题核实 → 剧本 → 分镜表 → 你确认 → 代码实现 → 渲染合成 → 自检交付
```

或者手动调用脚本三件套：

```bash
# 1. 逐帧渲染（页面需暴露 window.render(t) 纯时间函数）
python3 scripts/render_frames.py index.html out_frames/ --fps 30 --duration 130

# 2. 合成 77BPM 小调 BGM（织体分段对齐分镜章节）
python3 scripts/synth_bgm.py bgm.wav --bpm 77 --duration 130 \
  --sections "0,8,pad;8,30,piano;30,90,full;90,105,arp;105,120,piano;120,130,outro"

# 3. 帧序列 + BGM → MP4（-14 LUFS 响度，抖音标准）
bash scripts/build_video.sh out_frames/ bgm.wav final.mp4

# 4. 六维自检（不过不出门）
python3 scripts/qa_check.py final.mp4
```

从 `assets/template.html` 开始——它已内置五区布局、双语字幕系统、标题卡、晾衣绳卡片/纸艺母题库、固定种子随机数、缓动函数库。

## 📁 仓库结构

```
vibe-knowledge-video/
├── SKILL.md                    # 技能主文件：触发条件 + 七步工作流 + 铁律
├── references/
│   ├── style-guide.md          # 风格 DNA 完整规范（布局坐标/配色/动效/母题库）
│   ├── narrative-templates.md  # 8 条原片逐段拆解 + 六段式剧本模板 + 选题公式
│   └── prompt-brief.md         # 可直接填空的 XML 创作简报模板
├── scripts/
│   ├── render_frames.py        # Playwright 逐帧渲染器（render(t) 确定性架构）
│   ├── synth_bgm.py            # numpy 合成配乐（pad/钢琴/kick/shaker/琶音，段落织体）
│   ├── build_video.sh          # ffmpeg 合成（编码器自动回退 + 响度归一）
│   └── qa_check.py             # 自动 QA（规格/深色占比/字幕带/节奏/削波）
├── assets/
│   └── template.html           # 标准模板：开箱即改的分镜配置区
├── docs/
│   └── original-analysis/      # 8 条原片逐秒 OCR 记录（风格逆向的一手数据）
├── examples/                   # 示例项目（欢迎 PR 你的作品）
├── README.md
└── LICENSE
```

## 🔍 风格是怎么逆向出来的

对 8 条原片（共 17.5 分钟）做了程序化逐帧分析：

- **下载原片**（1920×1080），每秒抽帧，共 **1091 帧**
- **逐帧 OCR**（中文+英文），还原每条片逐秒的完整文案流（见 `docs/original-analysis/`）
- **音频转录验证**：确认全系列无旁白——旁白全部做成画面字幕
- **BGM 节奏测量**：全部 76–78 BPM
- **色彩/布局测量**：深蓝黑底、字幕带 85–91% 高度、注释带 70%
- **运动密度测量**：相邻帧差异均值 3.97，峰值 34

所有规范数字（字幕字号、留停时长、密度阈值）都来自实测，不是拍脑袋。

## 🙏 致谢与说明

- 本 Skill 的风格规范逆向自抖音「Vibe知识大赏」系列，向原作者 **@Iwanau**、**@Juno**、**叁号暗房 Logos** 致敬——他们的作品证明了"知识可以被拍成大片"。
- 原片由 Claude Opus 5.5 代码生成；制作方法论的公开资料可参考 xilo 的《零基础入门 Opus 5.5 做视频》。
- `docs/original-analysis/` 中的逐秒文字记录仅作风格研究与教学用途，版权归原作者所有；请勿用于二次发布。
- 本仓库不含任何原视频文件。

## 📄 License

[MIT](LICENSE) — 脚本、模板、文档可自由使用；请保留致谢部分。

---

<p align="center">如果这个项目帮到了你，欢迎 Star ⭐ / PR 你的作品到 examples/</p>
