#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画をクロップして 960x540 に解像度変更する。

  - GUIでファイル選択(tkinter)
  - 1フレーム目を表示し、マウスドラッグでクロップ範囲を指定(OpenCV)
    → 右上のラベル等、写したくない部分を外して選ぶ
  - 選択範囲を16:9に収めてから 960x540 へ縮小(歪みなし)
  - 再エンコードは ffmpeg、fps・総フレーム数は変更しない
  - 出力は入力と同じフォルダ・同じ拡張子 (*_960x540.ext)、ログも同じフォルダ
音声は扱いません (-an)。
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

import cv2
import tkinter as tk
from tkinter import filedialog, messagebox

# ---- 設定 ----------------------------------------------------------------
OUT_W, OUT_H = 960, 540   # 出力解像度
SUFFIX = "_960x540"
CROP = (474, 160, 1312, 738)   # 固定クロップ (x, y, w, h) / 1920x1080 用・16:9
                          # None にすると毎回マウスで選択
KEEP_ASPECT = True        # True: 選択範囲を16:9に切り詰めてから縮小(歪まない)
                          # False: 選択範囲をそのまま960x540に引き伸ばす
LOSSLESS = False          # True で完全無劣化(ファイルは数倍〜十数倍)
CRF = 14                  # LOSSLESS=False のときの画質 (小さいほど高画質)
X264_PRESET = "slow"
PREVIEW_MAX_W = 1280      # 選択ウィンドウの最大幅(画面に収めるため)
# -------------------------------------------------------------------------


def select_file() -> str:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="解像度を変更する動画を選択",
        filetypes=[
            ("動画ファイル", "*.mp4 *.mov *.avi *.mkv *.mpg *.mpeg *.wmv *.webm *.m4v"),
            ("すべてのファイル", "*.*"),
        ],
    )
    root.destroy()
    return path


def probe(path: str) -> dict:
    """ffprobe で映像ストリーム情報を取得(無ければ空dict)。"""
    if shutil.which("ffprobe") is None:
        return {}
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=pix_fmt,codec_name,width,height,r_frame_rate",
             "-of", "json", path],
            capture_output=True, text=True, check=True,
        ).stdout
        return json.loads(out).get("streams", [{}])[0]
    except Exception:
        return {}


def count_frames(path: str) -> int:
    """実際に復号して総フレーム数を数える(メタデータより確実)。"""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return -1
    n = 0
    while cap.grab():
        n += 1
    cap.release()
    return n


def fit_aspect(x, y, w, h, ar):
    """選択範囲を ar に合わせて『切り詰める』(外側は絶対に足さない)。"""
    if w / h > ar:          # 横に広すぎ → 幅を詰める
        new_w, new_h = h * ar, h
    else:                   # 縦に長すぎ → 高さを詰める
        new_w, new_h = w, w / ar
    x += (w - new_w) / 2
    y += (h - new_h) / 2
    return x, y, new_w, new_h


def even(v: float) -> int:
    """偶数に丸める(yuv420p は幅・高さが偶数である必要がある)。"""
    return int(round(v)) // 2 * 2


def pick_crop(first_frame):
    """1フレーム目を表示してマウスでクロップ範囲を選ばせる。"""
    fh, fw = first_frame.shape[:2]
    scale = min(1.0, PREVIEW_MAX_W / fw)
    disp = cv2.resize(first_frame, (int(fw * scale), int(fh * scale))) if scale < 1 else first_frame

    title = "crop: drag the area to KEEP -> Enter/Space to confirm, c to cancel"
    print("ウィンドウ上でドラッグして残す範囲を選び、Enter または Space で確定(c で中止)")
    roi = cv2.selectROI(title, disp, showCrosshair=False, fromCenter=False)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    x, y, w, h = [v / scale for v in roi]
    if w < 10 or h < 10:
        return None
    return x, y, w, h


def video_codec_args() -> list:
    if LOSSLESS:
        return ["-c:v", "libx264", "-qp", "0", "-preset", X264_PRESET]
    return ["-c:v", "libx264", "-crf", str(CRF), "-preset", X264_PRESET]


def main():
    if shutil.which("ffmpeg") is None:
        messagebox.showerror("エラー", "ffmpeg が見つかりません。PATH を確認してください。")
        sys.exit(1)

    in_path = select_file()
    if not in_path:
        print("キャンセルされました。")
        return
    in_path = os.path.abspath(in_path)

    folder = os.path.dirname(in_path)
    base, ext = os.path.splitext(os.path.basename(in_path))
    out_path = os.path.join(folder, f"{base}{SUFFIX}{ext}")
    log_path = os.path.join(folder, f"{base}{SUFFIX}.log")

    info = probe(in_path)
    pix_fmt = info.get("pix_fmt")
    src_codec = info.get("codec_name", "unknown")

    cap = cv2.VideoCapture(in_path)
    if not cap.isOpened():
        messagebox.showerror("エラー", f"動画を開けません:\n{in_path}")
        sys.exit(1)
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ok, first = cap.read()
    cap.release()
    if not ok:
        messagebox.showerror("エラー", "1フレーム目を読めません。")
        sys.exit(1)

    # --- クロップ範囲の決定 ---
    if CROP is not None:
        crop = tuple(float(v) for v in CROP)
        mode = "固定値"
        if CROP[0] + CROP[2] > src_w or CROP[1] + CROP[3] > src_h:
            print(f"警告: 固定クロップ {CROP} が入力 {src_w}x{src_h} の範囲外です。"
                  f"枠内に収まるよう自動で寄せます。設定値を確認してください。")
    else:
        crop = pick_crop(first)
        mode = "手動選択"
        if crop is None:
            print("クロップ範囲が選択されませんでした。中止します。")
            return

    x, y, w, h = crop
    if KEEP_ASPECT:
        x, y, w, h = fit_aspect(x, y, w, h, OUT_W / OUT_H)
    # 偶数化・画面内に収める
    cw, ch = even(w), even(h)
    cx = max(0, min(even(x), src_w - cw))
    cy = max(0, min(even(y), src_h - ch))
    print(f"クロップ: x={cx} y={cy} w={cw} h={ch}  →  {OUT_W}x{OUT_H}")

    # 確認用にクロップ1枚目を画像保存
    preview_path = os.path.join(folder, f"{base}{SUFFIX}_frame1.png")
    cv2.imwrite(preview_path,
                cv2.resize(first[cy:cy + ch, cx:cx + cw], (OUT_W, OUT_H),
                           interpolation=cv2.INTER_AREA))

    print("変換前のフレーム数を集計中...")
    n_in = count_frames(in_path)

    vf = f"crop={cw}:{ch}:{cx}:{cy},scale={OUT_W}:{OUT_H}:flags=lanczos"
    cmd = ["ffmpeg", "-y", "-i", in_path, "-an", "-sn", "-dn",
           "-vf", vf] + video_codec_args()
    if pix_fmt:
        cmd += ["-pix_fmt", pix_fmt]
    cmd += ["-map_metadata", "0", out_path]

    print("変換中...")
    if subprocess.run(cmd).returncode != 0:
        messagebox.showerror("エラー", "ffmpeg の変換に失敗しました。")
        sys.exit(1)

    print("変換後のフレーム数を集計中...")
    n_out = count_frames(out_path)

    log = f"""解像度変更 (クロップ + リサイズ) ログ
日時              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
入力ファイル      : {in_path}
出力ファイル      : {out_path}
確認用1フレーム目  : {preview_path}
入力解像度        : {src_w} x {src_h}
クロップ範囲      : x={cx} y={cy} w={cw} h={ch}  ({mode}{', 16:9に調整' if KEEP_ASPECT else ', アスペクト無視'})
出力解像度        : {OUT_W} x {OUT_H}
スケーリング      : lanczos
フレームレート    : {fps:.6f} fps (変更なし)
入力コーデック    : {src_codec} / pix_fmt {pix_fmt or '不明'}
出力設定          : {'ロスレス' if LOSSLESS else f'CRF {CRF}'} ({' '.join(video_codec_args())})

変換前 総フレーム数 : {n_in}
変換後 総フレーム数 : {n_out}  (期待値 {n_in})
音声                : なし (-an)
"""
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log)

    print(log)
    if n_out != n_in:
        print("注意: フレーム数が入力と一致しません。ログを確認してください。")
    messagebox.showinfo(
        "完了",
        f"出力: {out_path}\nログ: {log_path}\n確認用画像: {preview_path}\n\n"
        f"{src_w}x{src_h} → crop {cw}x{ch} → {OUT_W}x{OUT_H} / {n_out} フレーム",
    )


if __name__ == "__main__":
    main()
