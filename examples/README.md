# 示例作品

用 `assets/template.html` + 脚本三件套即可跑通最小示例：

```bash
cp ../assets/template.html .
python3 ../scripts/render_frames.py template.html frames/ --fps 30 --duration 10
python3 ../scripts/synth_bgm.py bgm.wav --bpm 77 --duration 10
bash ../scripts/build_video.sh frames/ bgm.wav demo.mp4
python3 ../scripts/qa_check.py demo.mp4
```

欢迎 PR 你的成片（附 index.html 与视频链接）到本目录。
