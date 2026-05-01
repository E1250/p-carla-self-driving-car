from pathlib import Path
import pandas as pd
import glob
import os
import cv2 as cv

def merge_and_export_df(df1:pd.DataFrame, df2:pd.DataFrame, export_path:Path, export_name:str, tolerance=0.05) -> pd.DataFrame:
    """Merging two dataframes on timestamp and save locally as parquet"""
    df1 = pd.DataFrame(df1).sort_values("timestamp")
    df2 = pd.DataFrame(df2).sort_values("timestamp")

    merged_df = pd.merge_asof(df1, df2, on="timestamp", tolerance=tolerance, direction="nearest")
    print(merged_df.describe())
    print(merged_df.info())
    merged_df.to_parquet(str(export_path / export_name), index=False)
    return merged_df

def frames_to_video_generator(frames_dir:Path, export_path:Path):
    """Collect and Generate a video from folder of frames"""
    frames = sorted(glob.glob(os.path.join(str(frames_dir), "*.png")))

    h, w, _ = cv.imread(frames[0]).shape
    video_writer = cv.VideoWriter(str(export_path / "run_video.mp4"), cv.VideoWriter_fourcc(*"mp4v"), 20, (w, h))
    for f in frames: video_writer.write(cv.imread(f, cv.IMREAD_COLOR))
    video_writer.release()

    print(f"Saved {len(frames)} frames to {export_path}")