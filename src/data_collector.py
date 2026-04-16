import pandas as pd
from pathlib import Path
import carla

from Carla_Sim_Project.config.settings import get_settings
config = get_settings()

class DataCollector():
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.imu_collected_data = []
        self.rgb_collected_data = []
        self.spectator = self.world.get_spectator()

    def collect_imu(self, imu_data:carla.libcarla.ServerSideSensor):
        """Exact data being collected"""
        self.imu_collected_data.append({
            'timestamp': imu_data.timestamp,
            'acc_x': imu_data.accelerometer.x,
            'acc_y': imu_data.accelerometer.y,
            'acc_z': imu_data.accelerometer.z,
            'gyro_x': imu_data.gyroscope.x,
            'gyro_y': imu_data.gyroscope.y,
            'gyro_z': imu_data.gyroscope.z,
        })

    def collect_rgb(self, rgb_data:carla.libcarla.ServerSideSensor):
        frame_path = fr"Carla_Sim_Project\data\frames\img_{rgb_data.frame}.png"
        rgb_data.save_to_disk(frame_path)

        self.rgb_collected_data.append({
            "timestamp": rgb_data.timestamp,
            "frame": rgb_data.frame,
            "filename": f"img_{rgb_data.frame}.png"
        })
   
    def __warmup_ticks(self, ticks:int=config.vehicle.warmup_ticks):
        """Warmup ticks to avoid garbage sensor readings of spawns"""
        for _ in range(ticks): self.world.tick()
        self.imu_collected_data.clear()
        self.rgb_collected_data.clear()


    def run(self, spectator_mode:bool=config.vehicle.spectator_mode):
        self.__warmup_ticks()

        control = carla.VehicleControl()

        for i in range(1000):
            if i < 50:
                control.throttle = 0.5
                control.steer = 0
            elif i < 100:
                control.throttle = 0.3
                control.steer = -0.3
            elif i < 150:
                control.throttle = 0.3
                control.steer = 0.3
            # else:
            #     control.throttle = 0
            #     control.brake = 0.5

            
            self.vehicle.apply_control(control)
            if spectator_mode:
                vehicle_transform = self.vehicle.get_transform()
                self.spectator.set_transform(
                    carla.Transform(vehicle_transform.location + carla.Location(x=-8, z=4), carla.Rotation(pitch=-15))
                )
            self.world.tick()


    def export_imu_parquet(self, export_path:str):
        """Export collected imu data parquet"""
        df = pd.DataFrame(self.imu_collected_data)
        df.to_parquet(export_path, index=False)
    
    def export_rgb_parquet(self, export_path:str):
        """Export collected rgb data parquet"""
        df = pd.DataFrame(self.rgb_collected_data)
        df.to_parquet(export_path, index=False)

    def fuse_sensor(self, tolerance=0.05):
        imu_df = pd.DataFrame(self.imu_collected_data).sort_values("timestamp")
        camera_df = pd.DataFrame(self.rgb_collected_data).sort_values("timestamp")

        return pd.merge_asof(imu_df, camera_df, on="timestamp", tolerance=tolerance, direction="nearest")
