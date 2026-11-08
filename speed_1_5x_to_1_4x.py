#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1/5倍速の動画を1/4倍速に変換する(5フレームに1枚=5枚目を破棄)。

画質優先の構成:
  - 間引きと再エンコードは ffmpeg の select フィルタで実施(YUVのまま処理)
  - 既定はロスレス (libx264 -qp 0 / vp9 lossless)、pix_fmt は入力と同じ
  - OpenCV は変換前後の総フレーム数カウント(検証)に使用
  - GUIでファイル選択、同じフォルダ・同じ拡張子で保存、ログも同じフォルダへ
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
DROP_EVERY = 5        # この枚数ごとに
DROP_INDEX = 4        # この位置(0始まり)を破棄 → 5枚目を破棄
SUFFIX = "_1-4x"
OUTPUT_FPS = 30.0     # 出力フレームレートを固定。None にすると入力と同じ
LOSSLESS = False      # True にすると完全無劣化(ただしファイルは数倍〜十数倍)
CRF = 14              # LOSSLESS=False のときの画質 (小さいほど高画質)
X264_PRESET = "slow"  # 遅いほど圧縮効率が上がる(画質は同じ)
# -------------------------------------------------------------------------


def select_file() -> str:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="1/5倍速の動画を選択",
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
             "-show_entries", "stream=pix_fmt,codec_name,width,height,r_frame_rate,nb_frames",
             "-of", "json", path],
            capture_output=True, text=True, check=True,
        ).stdout
        return json.loads(out).get("streams", [{}])[0]
    except Exception:
        return {}


def count_frames(path: str) -> int:
    """OpenCV で実際に復号して総フレーム数を数える(メタデータより確実)。"""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return -1
    n = 0
    while cap.grab():
        n += 1
    cap.release()
    return n


def video_codec_args(ext: str) -> list:
    ext = ext.lower()
    if ext == ".webm":
        return ["-c:v", "libvpx-vp9", "-lossless", "1"] if LOSSLESS \
            else ["-c:v", "libvpx-vp9", "-crf", str(CRF), "-b:v", "0"]
    # mp4 / mov / mkv / avi など
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
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if not fps or fps != fps or fps <= 0:
        fps = 30.0
        print("警告: fps を取得できないため 30 とみなします。")

    out_fps = float(OUTPUT_FPS) if OUTPUT_FPS else fps
    if abs(fps - out_fps) > 0.01:
        print(f"注意: 入力 {fps:.3f} fps → 出力 {out_fps:.3f} fps で書き出します。"
              f"フレームの複製・追加破棄はしませんが、再生速度は入力比 "
              f"{fps / out_fps / (1 - 1 / DROP_EVERY):.3f} 倍になります。")

    print("変換前のフレーム数を集計中...")
    n_in = count_frames(in_path)

    # 5n+5 枚目を捨て、残りを out_fps で等間隔に並べ直す
    vf = (f"select='not(eq(mod(n\\,{DROP_EVERY})\\,{DROP_INDEX}))',"
          f"setpts=N/{out_fps}/TB")
    cmd = ["ffmpeg", "-y", "-i", in_path, "-an", "-sn", "-dn",
           "-vf", vf, "-r", f"{out_fps}"] + video_codec_args(ext)
    if pix_fmt:
        cmd += ["-pix_fmt", pix_fmt]          # 入力と同じ色形式を維持
    cmd += ["-map_metadata", "0", out_path]

    print("変換中...")
    if subprocess.run(cmd).returncode != 0:
        messagebox.showerror("エラー", "ffmpeg の変換に失敗しました。")
        sys.exit(1)

    print("変換後のフレーム数を集計中...")
    n_out = count_frames(out_path)
    expected = n_in - (n_in + DROP_EVERY - 1 - DROP_INDEX) // DROP_EVERY

    log = f"""1/5倍速 → 1/4倍速 変換ログ
日時              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
入力ファイル      : {in_path}
出力ファイル      : {out_path}
解像度            : {width} x {height}
フレームレート    : 入力 {fps:.6f} fps → 出力 {out_fps:.6f} fps
入力コーデック    : {src_codec} / pix_fmt {pix_fmt or '不明'}
出力設定          : {'ロスレス' if LOSSLESS else f'CRF {CRF}'} ({' '.join(video_codec_args(ext))})
間引き規則        : {DROP_EVERY} フレームごとに {DROP_INDEX + 1} 枚目を破棄

変換前 総フレーム数 : {n_in}
変換後 総フレーム数 : {n_out}  (期待値 {expected})
破棄フレーム数      : {n_in - n_out}
フレーム数比        : {n_out / n_in:.6f} (期待値 {expected / n_in:.6f})
変換前 再生時間     : {n_in / fps:.3f} s
変換後 再生時間     : {n_out / out_fps:.3f} s
音声                : なし (-an)
"""
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log)

    print(log)
    if n_out != expected:
        print("注意: 変換後フレーム数が期待値と一致しません。ログを確認してください。")
    messagebox.showinfo("完了",
                        f"出力: {out_path}\nログ: {log_path}\n\n{n_in} → {n_out} フレーム")


if __name__ == "__main__":
    main()
