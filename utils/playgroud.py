import pandas as pd
import numpy as np

df = pd.read_parquet(r"G:\MyComputer\Robotics Wrolds\CARLA_0.9.13\Carla_Sim_Project\data\run1\run1.parquet")

df["speed"] = np.sqrt(df["v_x"]**2 + df["v_y"]**2)
df["slip_angle"] = np.arctan2(df["v_y"], df["v_x"])

# Filter properly - speed AND reasonable slip angle
clean = df[
    (df['speed'] > 1.0) 
    & (df['slip_angle'] > -0.5) 
    & (df['slip_angle'] < 0.5)
           ]

print(f"Clean samples: {len(clean)} / {len(df)}")
print(f"Slip angle range: {clean['slip_angle'].min():.3f} to {clean['slip_angle'].max():.3f} rad")
print(f"Speed range: {clean['speed'].min():.2f} to {clean['speed'].max():.2f} m/s")