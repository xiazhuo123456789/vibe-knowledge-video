#!/usr/bin/env python3
"""
render_frames.py — Vibe知识大赏 逐帧渲染器
用法:
  python3 render_frames.py index.html out_frames/ --fps 30 --duration 140 [--scale 1]
原理:
  Playwright 无头浏览器打开 index.html，对每帧调用 window.render(t) 后截图。
  要求页面暴露 window.render(seconds) —— 画面只由 t 决定（纯时间函数）。
可选:
  页面暴露 window.setup(done) 时先等待异步初始化（字体/数据）完成。
"""
import argparse, asyncio, os, sys, time

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="index.html 路径")
    ap.add_argument("outdir", help="帧输出目录")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--duration", type=float, required=True, help="总时长（秒）")
    ap.add_argument("--scale", type=float, default=1.0, help="deviceScaleFactor（2=超采样抗锯齿）")
    ap.add_argument("--preview", type=int, default=0, metavar="N", help="只渲染 N 张均匀分布的静帧（预览模式）")
    args = ap.parse_args()

    from playwright.async_api import async_playwright

    os.makedirs(args.outdir, exist_ok=True)
    html_path = os.path.abspath(args.html)

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
        page = await browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=args.scale)
        page.on("pageerror", lambda e: print(f"[页面JS错误] {e}", file=sys.stderr))
        await page.goto(f"file://{html_path}")
        # 等字体
        try:
            await page.evaluate("document.fonts.ready.then(()=>true)")
        except Exception:
            pass
        # 异步初始化钩子
        has_setup = await page.evaluate("typeof window.setup === 'function'")
        if has_setup:
            await page.evaluate("window.setup(window.__done!==undefined ? undefined : undefined)") if False else None
            await page.evaluate("new Promise(res => { window.__setupDone = res; window.setup(res); })")
        # 校验 render(t)
        has_render = await page.evaluate("typeof window.render === 'function'")
        if not has_render:
            print("[致命] 页面未暴露 window.render(t) —— 请检查 index.html", file=sys.stderr)
            sys.exit(2)
        # 接管渲染模式：停掉页面自带的预览 rAF 循环（若模板遵守约定）
        await page.evaluate("window.__RENDER_MODE__ = true")

        total = int(args.duration * args.fps)
        if args.preview > 0:
            idxs = [int(i * (total - 1) / (args.preview - 1)) for i in range(args.preview)] if args.preview > 1 else [0]
        else:
            idxs = range(total)

        t0 = time.time()
        n_done = 0
        for fi in idxs:
            t = fi / args.fps
            await page.evaluate(f"window.render({t})")
            await page.screenshot(path=os.path.join(args.outdir, f"f{fi:06d}.png"))
            n_done += 1
            if n_done % 150 == 0 or n_done == len(list(idxs) if not isinstance(idxs, range) else idxs):
                el = time.time() - t0
                print(f"  已渲染 {n_done}/{len(idxs) if not isinstance(idxs, range) else total} 帧  ({el:.0f}s)", flush=True)
        await browser.close()
        print(f"完成：{n_done} 帧 → {args.outdir}")

if __name__ == "__main__":
    asyncio.run(main())
