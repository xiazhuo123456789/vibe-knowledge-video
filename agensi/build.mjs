// Build the Agensi distribution package from the repo.
// Usage: node agensi/build.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const STAGE = path.join(ROOT, 'dist', 'agensi-stage');

const read = (p) => fs.readFileSync(p, 'utf8').replace(/\r\n/g, '\n');
const must = (s, old, count = 1) => {
  const n = s.split(old).length - 1;
  if (n !== count) throw new Error(`expected ${count} occurrence(s), found ${n}: ${JSON.stringify(old.slice(0, 60))}`);
  return s;
};
const mustMatch = (s, re, file) => {
  if (!re.test(s)) throw new Error(`pattern not found in ${file}: ${re}`);
  return s;
};

// ---- 1. stage tree --------------------------------------------------------
fs.rmSync(STAGE, { recursive: true, force: true });
fs.mkdirSync(STAGE, { recursive: true });
const copyDir = (rel, filter) => {
  const src = path.join(ROOT, rel);
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (filter && !filter(e.name)) continue;
    fs.cpSync(path.join(src, e.name), path.join(STAGE, rel, e.name), { recursive: true });
  }
};
copyDir('references');
copyDir('scripts');
copyDir('assets');
copyDir('docs', (n) => !['original-analysis', 'use-with-other-ai.md', 'CHANGELOG-v2.md'].includes(n));
fs.copyFileSync(path.join(HERE, 'README.md'), path.join(STAGE, 'README.md'));
fs.copyFileSync(path.join(HERE, 'LICENSE'), path.join(STAGE, 'LICENSE'));

// ---- 2. SKILL.md ----------------------------------------------------------
let skill = read(path.join(ROOT, 'SKILL.md'));

const DESC = 'description: "Turn one fact, theorem or paper into a 2-minute cinematic knowledge short using pure code: HTML Canvas animation plus synthesized instrumental music, 1920x1080 30fps, bilingual on-screen subtitles (Chinese main line plus English italic), no voiceover. Requires local ffmpeg, Python with playwright/pillow/numpy, and an LLM API key supplied by the user. Distilled from studying eight publicly released short videos; this package ships no third-party footage, audio or transcripts. Works with any SKILL.md agent."';
skill = must(skill, 'name: vibe-knowledge-video');
skill = skill.replace('name: vibe-knowledge-video', 'name: cinematic-knowledge-shorts');
skill = mustMatch(skill, /^description: .*$/m, 'SKILL.md').replace(/^description: .*$/m, DESC);
skill = must(skill, 'author: "CodeBuddy AI"').replace('author: "CodeBuddy AI"', 'author: "Xiazhuo"');
skill = skill.replace('created: "2026-10-09"', 'license: "MIT"');
skill = skill.replace('updated: "2026-10-25"', 'updated: "2026-10-31"');

const swaps = [
  ['# Vibe 知识大赏 · AI 知识视频制作', '# Cinematic Knowledge Shorts · AI Knowledge Video Production'],
  ['制作"Vibe知识大赏"风格的电影感知识短视频', '制作电影感知识短视频（cinematic knowledge short）'],
  ['- "做一个 Vibe知识大赏 风格的视频"', '- "做一个电影感知识短视频（cinematic knowledge short）"'],
  ['- "做一条抖音知识号风格的片子"', '- "做一条知识科普短视频"'],
  ['是抖音横屏知识大片', '是横屏知识短片'],
  ['逆向工程自 8 条原片（详见 `references/style-guide.md`）：', 'Distilled from studying eight publicly released short videos (see `references/style-guide.md`):'],
  ['VIBE知识大赏 大写标签 + 金色衬线片名 + 副标题双语（Juno 系列标配）', '大写系列标签 + 金色衬线片名 + 副标题双语（该格式标配）'],
  ['（Juno 系列双语标配，如', '（该格式双语标配，如'],
  ['8 条原片的叙事弧逐段拆解 + 通用剧本模板', '八条参考片的叙事弧结构归纳 + 通用剧本模板'],
  ['- `docs/CHANGELOG-v2.md` — v2.x 升级的完整说明（改了什么、为什么、怎么用）\n', ''],
];
for (const [a, b] of swaps) { must(skill, a); skill = skill.split(a).join(b); }

const DOUYIN = '## 二、抖音发布文案模板\n\n```\nVibe知识大赏 | 《标题》一句话钩子？\n[2-3 句核心内容概括，含一个具体年份+人名+反直觉结论]\n#vibe知识大赏 #AI把知识拍成大片了 #claude5.5 [主题词 3-5 个]\n```\n\n';
must(skill, DOUYIN);
skill = skill.replace(DOUYIN, '');
must(skill, '## 三、铁律（Gotchas）');
skill = skill.replace('## 三、铁律（Gotchas）', '## 二、铁律（Gotchas）');
skill = must(skill, '## 四、参考文件').replace('## 四、参考文件', '## 三、参考文件');
skill = skill.replace('+ 抖音发布文案（模板见下）+', '+ 可选发布文案 +');

// ---- 3. per-file line patches --------------------------------------------
const linePatches = [
  ['references/style-guide.md', /^# Vibe知识大赏 风格 DNA 完整规范$/m, '# Cinematic Knowledge Shorts — Style DNA'],
  ['references/style-guide.md', /^> 逆向工程自 8 条原片：.*$/m, '> Distilled from studying eight publicly released short videos, all generated with code. No original footage, audio or transcript is redistributed in this package.'],
  ['references/style-guide.md', /^- \*\*水印\*\*：.*$/m, '- **水印**：`@你的署名`——小号、半透明、左上角，全片不动。'],
  ['references/style-guide.md', /^([ \t]*)- Iwanau（理科模拟风）：.*$/m, '$1- 理科模拟风：暖橙 `#E8A87C`'],
  ['references/style-guide.md', /^([ \t]*)- \*\*Juno（卡片纸艺风）：.*$/m, '$1- **卡片纸艺风**：金 + 米白纸张——金色衬线标题 `#C9A96A`、米白卡片 `#EDE4D3`、红色印章 `#B53A2F`、金色线框图标（标题卡、晾衣绳卡片、规则卡、文献复原件都是纸质感）'],
  ['references/style-guide.md', /^([ \t]*)- 叁号暗房（哲学风）：.*$/m, '$1- 哲学冷白风：冷白 + 主题色'],
  ['references/style-guide.md', /^- \*\*出品卡\*\*：.*$/m, '- **出品卡**：`@你的署名 出品` + 互动问题。'],
  ['references/style-guide.md', /^## 8\. 发布文案规范.*$/m, '## 8. 发布文案规范（短视频平台）'],
  ['references/style-guide.md', /^- 标题：`.*$/m, '- 标题：`《片名》 | 一句钩子？`'],
  ['references/style-guide.md', /^- 标签：`.*$/m, '- 标签：`#知识视频 #科普 #AI视频` + 3–5 个主题词（#博弈论 #概率论 #哲学）'],
  ['docs/publish-guide.md', /^([ \t]*)- \[ \] 发布标题格式：.*$/m, '$1- [ ] 发布标题格式：`《片名》 | 一句钩子？`'],
  ['docs/publish-guide.md', /^([ \t]*)- \[ \] 话题标签：.*$/m, '$1- [ ] 话题标签：3–5 个主题标签（#知识视频 #科普 #AI视频 等）'],
];
for (const [rel, re, rep] of linePatches) {
  const p = path.join(STAGE, rel);
  let body = read(p);
  mustMatch(body, re, rel);
  body = body.replace(re, rep);
  fs.writeFileSync(p, body, 'utf8');
}

// prompt-brief.md: drop the trailing Douyin publishing card section
{
  const p = path.join(STAGE, 'references/prompt-brief.md');
  const body = read(p);
  const cut = body.indexOf('\n## 抖音发布卡');
  if (cut > 0) fs.writeFileSync(p, body.slice(0, cut) + '\n', 'utf8');
}

// ---- 4. global scrub -----------------------------------------------------
let skillWritten = skill;
fs.writeFileSync(path.join(STAGE, 'SKILL.md'), skillWritten, 'utf8');

const scrub = [
  ['Vibe知识大赏 风格的知识短片', '电影感知识短片（cinematic knowledge short）'],
  ['Vibe知识大赏 风格', '电影感'],
  ['Vibe知识大赏', 'Cinematic Knowledge Shorts'],
  ['VIBE知识大赏', 'KNOWLEDGE SHORTS'],
  ['vibe知识大赏', 'cinematic knowledge shorts'],
  ['Juno 系列双语标配', '该格式双语标配'],
  ['Juno 系列标配', '该格式标配'],
  ['Juno（卡片纸艺风）', '卡片纸艺风'],
  ['Juno 纸艺风', '纸艺风'],
  ['Juno 风', '纸艺风'],
  ['Juno', '参考系列'],
  ['Iwanau（理科模拟风）', '理科模拟风'],
  ['Iwanau', '参考创作者'],
  ['叁号暗房（哲学风）', '哲学冷白风'],
  ['叁号暗房', '参考创作者'],
  ['本片由 Claude Opus 5.5 代码生成，无实拍素材', '本片由 AI 代码生成，无实拍素材'],
  ['《Opus5.5做视频从原理到实操》', '一份视频制作方法论文档'],
  ['Claude Opus 5.5', 'AI'],
  ['8 条原片', '8 条参考短片'],
  ['原片', '参考短片'],
  ['抖音', '短视频平台'],
];
const textFiles = [];
const walk = (d) => {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p); else if (/\.(md|txt|html|py|sh)$/.test(e.name)) textFiles.push(p);
  }
};
walk(STAGE);
for (const f of textFiles) {
  let body = read(f);
  const before = body;
  for (const [a, b] of scrub) body = body.split(a).join(b);
  if (body !== before) fs.writeFileSync(f, body, 'utf8');
}

// ---- 5. verify -----------------------------------------------------------
const banned = ['Vibe知识大赏', 'vibe知识大赏', 'VIBE知识大赏', 'Iwanau', 'Juno', '叁号暗房', 'CodeBuddy', 'original-analysis', '抖音'];
const hits = [];
for (const f of textFiles) {
  const body = read(f);
  for (const b of banned) if (body.includes(b)) hits.push(`${path.relative(STAGE, f)} :: ${b}`);
}
let bytes = 0, count = 0;
const sizeWalk = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) sizeWalk(p); else { bytes += fs.statSync(p).size; count++; } } };
sizeWalk(STAGE);

console.log(JSON.stringify({ stage: STAGE, files: count, bytes, bannedHits: hits, head: read(path.join(STAGE, 'SKILL.md')).split('\n').slice(0, 12) }, null, 2));
if (hits.length) process.exitCode = 2;
