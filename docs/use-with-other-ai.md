# 在豆包 / Codex 等其他 AI 上使用本技能

> 一句话结论：**把整个仓库给它，而不是单个 SKILL.md 文件**。知识部分任何 AI 通用；渲染合成需要能执行命令的环境（Playwright + ffmpeg）。

## 先理解这个技能的两半

| 组成 | 内容 | 对 AI 的要求 |
|---|---|---|
| **知识半**（纯文档） | `SKILL.md` + `references/`（风格DNA、叙事模板、简报模板） | 只要能读文件/读长文本就行，**豆包网页版也可以** |
| **执行半**（流水线） | `scripts/` 四件套 + `assets/template.html` | 需要能跑 shell、装依赖的环境（Playwright、ffmpeg、numpy） |

所以"能不能用"取决于你用的 AI 有没有**代码执行环境**：

| AI 工具 | 能读知识 | 能跑流水线 | 推荐用法 |
|---|---|---|---|
| **CodeBuddy / Claude Code** | ✅ | ✅ | 装进 `~/.codebuddy/skills/` 自动触发（本技能原生形态） |
| **OpenAI Codex CLI** | ✅ | ✅（沙箱装依赖） | clone 本仓库，`AGENTS.md` 自动生效，一句话开工 |
| **Cursor / Trae（豆包系 IDE）** | ✅ | ✅（本地终端） | clone 本仓库，让 AI 先读 `SKILL.md` 与 `AGENTS.md` |
| **豆包网页版 / App** | ✅（上传文档） | ❌（无法执行命令） | 当"编剧+码农"用：出剧本、分镜、`index.html` 代码；渲染在你本地跑（见下） |

## 用法一：Codex CLI（开箱即用）

```bash
git clone https://gitee.com/x2576080434/vibe-knowledge-video.git
cd vibe-knowledge-video
codex "用这个仓库的技能，做一条《辛普森悖论》的知识视频"
```

Codex 会自动读取仓库根的 `AGENTS.md`：先装依赖，再按 `SKILL.md` 的七步流程走，需要你确认剧本分镜后开始渲染。GitHub 源同理：

```bash
git clone https://github.com/xiazhuo123456789/vibe-knowledge-video.git
```

> 首次使用建议先跑一次环境准备（见 `AGENTS.md` 里的安装命令），避免沙箱联网装依赖超时。

## 用法二：Cursor / Trae 等 AI IDE

1. clone 仓库并用 IDE 打开该目录；
2. （可选）把 `AGENTS.md` 的内容复制进你的项目规则文件（Cursor 是 `.cursor/rules`，Trae 是项目 Rules）；
3. 对 AI 说："**先读 SKILL.md 和 AGENTS.md，然后按七步流程做《××》视频**"。

关键就一句：**让它先读文档再动手**，不要直接说"给我做个视频"（那样它会用默认审美，丢掉全部风格 DNA）。

## 用法三：豆包网页版（只能做一半，但那一半很值）

豆包没有命令执行环境，把它当**编剧 + 前端码农**：

1. 下载本仓库 zip，在豆包对话里上传这些文件（或分次粘贴内容）：
   - `SKILL.md`（必传）
   - `references/style-guide.md` + `references/narrative-templates.md`（风格与叙事核心）
   - `assets/template.html`（改起来省一半功夫）
2. 对豆包说：
   > 严格按 SKILL.md 的七步流程做《××》视频：先给我剧本和分镜表（第1-3步），我确认后再写完整 index.html（第5步）。index.html 必须暴露 window.render(t)，画面只由 t 决定。
3. 豆包产出 `script.md`、`storyboard.md`、`index.html` 后，**在你自己电脑上**执行第 6–7 步：

```bash
# 一次性环境准备（本机要有 Python 3.10+）
pip install playwright pillow numpy
playwright install chromium
# 再装 ffmpeg：https://ffmpeg.org/download.html（或 brew/winget/apt install ffmpeg）

# 渲染合成（在仓库目录下）
python3 scripts/render_frames.py index.html out_frames/ --fps 30 --duration 130
python3 scripts/synth_bgm.py bgm.wav --bpm 77 --duration 130 \
  --sections "0,8,pad;8,30,piano;30,90,full;90,105,arp;105,120,piano;120,130,outro"
bash scripts/build_video.sh out_frames/ bgm.wav final.mp4
python3 scripts/qa_check.py final.mp4
```

出来的 `final.mp4` 就是成片；QA 不过就把报告贴回给豆包让它改代码。

## 常见坑

- **只发一个 SKILL.md 文件** → AI 缺风格坐标/母题库/模板，做出来味道不对。`SKILL.md` 里到处引用 `references/` 和 `assets/`，它们是一套的。
- **SKILL.md 开头的 frontmatter 别的 AI 不认识** → 没关系，那几行是 CodeBuddy 的技能注册信息，内容主体是普通 Markdown，直接能读。
- **对话型 AI 说"我帮你渲染好了"** → 网页版没有执行环境，它最多给你代码；真渲染必须本地/沙箱跑。
- **忘装 Chromium** → `playwright install chromium` 是必须的一步，`pip install playwright` 不带浏览器。
- **ffmpeg 无 H.264 编码器** → `build_video.sh` 会自动回退到 libopenh264；两者都没有时需换完整版 ffmpeg。

## 为什么仓库里有个 AGENTS.md

`AGENTS.md` 是 Codex 发起、Gemini CLI / Jules / Cursor 等广泛支持的 **AI 助手通用约定**：这些工具进入仓库后会自动读取它。所以这份文件就是本技能的"跨平台适配层"——你不用在每个平台手动配置，clone 下来即用。
