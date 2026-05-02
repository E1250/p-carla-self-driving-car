import numpy as np
import yaml
import matplotlib.pyplot as plt

from config.settings import Settings
import math

class RunValidator:
    def __init__(self):
        pass
    
    def validate(self):
        pass


def validate_run(df, output_dir:str, cfg:Settings):
    """
    Validating the run and create summaries about the data extracted from our run to check if we are going to use this run or just adjust and create another one. 
    We are also checking if we extracted the expected data.
    """  

    # Threshold
    MIN_SPEED = 1.0  # m/s, lower values arctan(vy/vx) is numerically unstable
    MAX_SLIP = 0.5   # rad - estimated range, Peak at ~0.1-0.2 rad
    
    df["speed"] = np.sqrt(df['v_x'] ** 2 + df["v_y"] ** 2)  # Pythagorean theorem  a^2 + b^2 = c^2, as both a, b are vectors. 
    
    v_long = df["v_x"] * np.cos(df["yaw"]) + df["v_y"] * np.sin(df["yaw"])
    v_lat = -df["v_x"] * np.sin(df["yaw"]) + df["v_y"] * np.cos(df["yaw"])
    df["slip_angle"] = np.arctan2(v_lat, v_long)   # getting the angle between valocity vector and forward direction.

    print(df.describe())
    print(df.info())

    clean_df = df[
        (df["speed"] > MIN_SPEED)
        & (df['slip_angle'] > -MAX_SLIP)
        & (df['slip_angle'] < MAX_SLIP)
    ]

    checks = {
        "total_raw_sample": len(df),
        "clean_samples": len(clean_df),
        "ticks": cfg.vehicle.ticks,
        "warmup_ticks": cfg.vehicle.warmup_ticks,
        "autopilot": cfg.vehicle.autopilot,
        "nan_count_post_merge": df.isna().sum().sum()  # High value means timing and merge issue. 
        # "raw_df_description": df.describe().to_dict(),
        # "clean_df_description": clean_df.describe().to_dict(),
    }

    with open(str(output_dir / "summary.yaml"), "w") as f:
        yaml.dump(checks, f, default_flow_style=False)


    _, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Slip angle direction
    axes[0].hist(clean_df["slip_angle"], bins=50, color="blue", edgecolor="black")
    axes[0].set_title("Slip Angle Distribution")
    axes[0].set_xlabel("Slip Angle (rad)")
    axes[0].set_ylabel("Count")
    axes[0].axvline(0.1, color="red", linestyle="--", label="Peak region start")
    axes[0].axvline(0.2, color="red", linestyle="--", label="Peak region end")
    axes[0].legend()

    # Speed distribution 
    axes[1].hist(clean_df["speed"], bins=50, color="green", edgecolor="black")
    axes[1].set_title("Speed Distribution")
    axes[1].set_xlabel("Speed (m/s)")
    axes[1].set_ylabel("Count")

    # Timeline - slip angle across ticks
    axes[2].plot(clean_df["slip_angle"].values, alpha=0.6, color="orange")
    axes[2].set_title("Slip Angle Over Time")
    axes[2].set_xlabel("Tick")
    axes[2].set_ylabel("Slip Angle (rad)")

    plt.tight_layout()
    plt.savefig(str(output_dir/"validation_report.png"), dpi=150)
    plt.close()