# AGENTS.md — vibe-knowledge-video 通用 Agent 指令

> 本文件是给 AI 编程助手（OpenAI Codex / Gemini CLI / Jules / Cursor / Trae 等）看的入口指令。
> 这些工具会自动读取仓库根目录的 `AGENTS.md` 并遵守其中约定。

## 你现在拿到了什么

这是一个**视频制作技能仓库**：把数学/概率/哲学等硬知识拍成「Vibe知识大赏」风格的电影感知识短视频（1920×1080、2:00–2:45、无配音、双语字幕、纯代码生成）。

## 收到视频制作请求时，你必须这样做

1. **先完整阅读 `SKILL.md`**——它是七步工作流的总纲（选题核实→剧本→分镜→用户确认→代码实现→渲染合成→自检交付），逐步执行，不可跳步。
2. 需要风格细节时读 `references/`：
   - `references/style-guide.md` — 布局坐标、配色、动效规格、视觉母题库
   - `references/narrative-templates.md` — 六段式叙事弧模板 + 8 条原片逐段拆解
   - `references/prompt-brief.md` — 创作简报（Brief）填空模板
3. 写代码前**必须让用户确认剧本和分镜**（第 4 步），不要自作主张直接开做。
4. 页面模板从 `assets/template.html` 起改，不要从零造轮子。

## 环境准备（渲染合成前执行一次）

```bash
# Python 依赖
pip install playwright pillow numpy

# 无头浏览器
playwright install chromium

# ffmpeg（视频合成必需，需含 H.264 编码器）
# Ubuntu/Debian: apt install -y ffmpeg
# macOS: brew install ffmpeg
# Windows: winget install ffmpeg

# 可选：QA 字幕 OCR 校验
# apt install -y tesseract-ocr tesseract-ocr-chi-sim
ffmpeg -version  # 验证可用
```

## 不可违反的技术契约

- `index.html` 必须暴露 **`window.render(t)`**：给定秒数 t 画出该帧；画面只由 t 决定（固定随机种子、无计时器、无帧间状态）。这是逐帧渲染器 `scripts/render_frames.py` 的调用契约。
- 渲染器会设置 `window.__RENDER_MODE__ = true` 接管渲染循环——页面自己的 requestAnimationFrame 预览循环检测到该标志后必须停止，否则预览循环会用墙上时钟覆盖 render(t) 的画面状态。
- 字体加载完成再截图（`document.fonts.ready`）。
- Canvas 文字手动换行，禁止依赖浏览器自动换行。

## 渲染合成命令（第 6 步）

```bash
python3 scripts/render_frames.py index.html out_frames/ --fps 30 --duration 130
python3 scripts/synth_bgm.py bgm.wav --bpm 77 --duration 130 \
  --sections "0,8,pad;8,30,piano;30,90,full;90,105,arp;105,120,piano;120,130,outro"
bash scripts/build_video.sh out_frames/ bgm.wav final.mp4
python3 scripts/qa_check.py final.mp4   # 六维自检，任何一项 < 8 分须修复重渲
```

## 能力边界（对用户诚实）

- 若当前环境**无法安装依赖或执行 shell**（如纯对话型网页 AI）：只完成第 1–5 步（剧本/分镜/index.html 代码），并把上面两条命令块原样交给用户，请其在本地终端执行第 6–7 步。
- 所有事实（年份/人名/论文名/数字）须联网核实，没把握的不写。

## 语言

与用户交流用中文；代码注释用中文；成片字幕为中文主句 + 英文斜体对照（风格 DNA 要求，见 `references/style-guide.md`）。
