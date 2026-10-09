#!/usr/bin/env python3
"""
synth_bgm.py — Vibe知识大赏 配乐合成器（纯 numpy，无采样无虚拟乐器）
用法:
  python3 synth_bgm.py bgm.wav --bpm 77 --duration 140 [--key Am] [--sections "0,8,pad;8,30,piano;30,90,full;90,105,arp;105,120,piano;120,140,outro"]
风格（逆向自原片）:
  76-78 BPM 小调，低音 pad 长音 + 钢琴柱式和弦 + 轻打击，段落起伏对齐分镜章节。
  织体级别: pad(只有铺底) < piano(进钢琴) < full(进打击+arp弱) < arp(琶音突出) < outro(回落)
输出: 44.1kHz 16bit 立体声 WAV，峰值 -1dB。
"""
import argparse, numpy as np, struct, wave

SR = 44100

def note_freq(name):
    """'A3' -> 频率"""
    names = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
    n = name[:-1]; octv = int(name[-1])
    midi = 12*(octv+1) + names[n]
    return 440.0 * 2**((midi-69)/12)

def env_ad(n, a, d, curve=3.0):
    """attack-decay 包络"""
    e = np.ones(n)
    na = max(1, int(a*SR)); nd = max(1, int(d*SR))
    na = min(na, n); 
    e[:na] = np.linspace(0, 1, na)**0.5
    tail = min(nd, n-na)
    if tail > 0:
        e[na:na+tail] *= np.linspace(1, 0.35, tail)
    return e

def pad_tone(freq, dur, amp=0.10):
    n = int(dur*SR); t = np.arange(n)/SR
    w = (np.sin(2*np.pi*freq*t)*1.0 + np.sin(2*np.pi*freq*2*t)*0.25
         + np.sin(2*np.pi*freq*0.5*t)*0.4 + np.sin(2*np.pi*freq*1.005*t)*0.5)  # 微失谐=合唱感
    # 缓起缓落
    fade = min(int(1.2*SR), n//2)
    envl = np.ones(n); envl[:fade] = np.linspace(0,1,fade); envl[-fade:] = np.linspace(1,0,fade)
    return amp * w * envl / 2.2

def piano_tone(freq, dur, amp=0.16):
    n = int(dur*SR); t = np.arange(n)/SR
    # 简易钢琴: 基频+泛音，指数衰减
    w = np.sin(2*np.pi*freq*t) + 0.5*np.sin(2*np.pi*freq*2*t) + 0.25*np.sin(2*np.pi*freq*3*t) + 0.12*np.sin(2*np.pi*freq*4.02*t)
    envl = np.exp(-t*2.2) * env_ad(n, 0.004, 0.1)
    return amp * w * envl / 2.0

def kick(dur=0.22, amp=0.30):
    n = int(dur*SR); t = np.arange(n)/SR
    f = 110*np.exp(-t*24) + 42
    return amp * np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*13)

def shaker(dur=0.06, amp=0.05):
    n = int(dur*SR)
    noise = np.random.default_rng(7).uniform(-1,1,n)
    b = np.exp(-np.arange(n)/ (n*0.25))
    return amp * noise * b

def arp_tone(freq, dur, amp=0.08):
    return piano_tone(freq, dur, amp*0.6)

# 和弦进行（小调，纪录片感）: i - VI - III - VII （如 Am F C G）
PROGRESSIONS = {
    'Am': [['A2','E3','A3','C4','E4'], ['F2','C3','F3','A3','C4'], ['C3','G3','C4','E4','G4'], ['G2','D3','G3','B3','D4']],
    'Dm': [['D2','A2','D3','F3','A3'], ['Bb2','F3','Bb3','D4','F4'], ['F2','C3','F3','A3','C4'], ['C3','G3','C4','E4','G4']],
    'Em': [['E2','B2','E3','G3','B3'], ['C3','G3','C4','E4','G4'], ['G2','D3','G3','B3','D4'], ['D2','A2','D3','F#3','A3']],
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="输出 WAV 路径")
    ap.add_argument("--bpm", type=float, default=77)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--key", default="Am", choices=list(PROGRESSIONS.keys()))
    ap.add_argument("--sections", default="",
                    help='分镜段落，格式 "起秒,止秒,织体" 分号分隔。织体: pad/piano/full/arp/outro')
    args = ap.parse_args()

    rng = np.random.default_rng(42)
    total_n = int(args.duration * SR)
    mix = np.zeros(total_n)
    beat = 60.0/args.bpm
    bar = beat*4

    # 解析段落
    sections = []
    if args.sections:
        for s in args.sections.split(';'):
            s = s.strip()
            if not s: continue
            a, b, tex = s.split(',')
            sections.append((float(a), float(b), tex.strip()))

    def texture_at(t):
        if not sections: return 'full'
        for a, b, tex in sections:
            if a <= t < b: return tex
        return sections[-1][2] if sections else 'full'

    # 1) pad: 每小节换和弦，铺满全曲
    tpos = 0.0; ci = 0
    while tpos < args.duration:
        chord = PROGRESSIONS[args.key][ci % 4]
        dur = min(bar, args.duration - tpos)
        if dur < 0.4: break
        seg = np.zeros(total_n)
        n = int(dur*SR)
        for i, note in enumerate(chord):
            amp = 0.09 if i == 0 else 0.055
            tone = pad_tone(note_freq(note), dur, amp)
            seg[:len(tone)] += tone
        mix += seg
        tpos += dur; ci += 1

    # 2) 钢琴柱式和弦：每小节第一拍
    tpos = 0.0; ci = 0
    while tpos < args.duration - 0.5:
        tex = texture_at(tpos)
        if tex in ('piano','full','arp','outro'):
            chord = PROGRESSIONS[args.key][ci % 4]
            # 高声部三音
            for note in chord[2:]:
                tone = piano_tone(note_freq(note), beat*3.6, 0.13 if tex != 'outro' else 0.09)
                i0 = int(tpos*SR)
                mix[i0:i0+len(tone)] += tone[:max(0, total_n-i0)]
        tpos += bar; ci += 1

    # 3) 打击: full 段 kick 每 2 拍 + shaker 8 分音符
    tpos = 0.0; bi = 0
    while tpos < args.duration - 0.3:
        tex = texture_at(tpos)
        if tex == 'full':
            if bi % 2 == 0:
                k = kick()
                i0 = int(tpos*SR); mix[i0:i0+len(k)] += k[:max(0,total_n-i0)]
            for off in (0, beat/2):
                sh = shaker(amp=0.035)
                i0 = int((tpos+off)*SR); mix[i0:i0+len(sh)] += sh[:max(0,total_n-i0)]
        tpos += beat; bi += 1

    # 4) 琶音: arp 段
    tpos = 0.0; ci = 0
    while tpos < args.duration - 0.3:
        tex = texture_at(tpos)
        if tex == 'arp':
            chord = PROGRESSIONS[args.key][ci % 4]
            for k_i, note in enumerate(chord[1:]):
                tone = arp_tone(note_freq(note), beat*0.9)
                i0 = int((tpos + k_i*beat/2)*SR)
                if i0+len(tone) < total_n:
                    mix[i0:i0+len(tone)] += tone
        tpos += bar; ci += 1

    # 5) 高频空气感: 极轻的粉噪 + 缓慢音量呼吸
    air = rng.uniform(-1, 1, total_n)
    # 简易一阶低通做粉噪
    air = np.convolve(air, np.ones(8)/8, 'same') * 0.012
    breath = 0.85 + 0.15*np.sin(np.arange(total_n)/SR * 2*np.pi/16)  # 16s 呼吸周期
    mix += air*breath

    # 6) 总线: 软限幅 + 峰值 -1dB
    mix = np.tanh(mix*1.1)/np.tanh(1.1)
    peak = np.abs(mix).max() + 1e-9
    mix = mix/peak*0.891  # -1dB

    # 立体声: 微延迟展宽
    delay = int(0.012*SR)
    L = mix
    R = np.concatenate([np.zeros(delay), mix[:-delay]])*0.96 + mix*0.04

    stereo = np.stack([L, R], axis=1)
    pcm = (stereo*32767).astype('<i2')
    with wave.open(args.out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"BGM 完成: {args.out}  {args.bpm}BPM  {args.duration}s  {args.key}小调")

if __name__ == "__main__":
    main()
