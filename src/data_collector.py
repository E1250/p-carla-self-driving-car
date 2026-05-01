import queue
import threading
import pandas as pd
from pathlib import Path
import carla

from config.settings import Settings
from src.vehicle import Vehicle
from typing import Optional

import glob 
import os
import cv2 as cv
from tqdm import tqdm
import numpy as np

from utils.utils import frames_to_video_generator, merge_and_export_df

class DataCollector():
    def __init__(self, world, vehicle:Vehicle, cfg:Settings):
        self.config=cfg
        self.world = world
        self.vehicle = vehicle
        self.imu_collected_data = []
        self.rgb_collected_data = []
        self.spectator = self.world.get_spectator()
        self.output_path = Path(__file__).parent.parent / self.config.vehicle.output_dir

        self._frames_queue = queue.Queue() # Like the list, but more than one worker can adjust
        self._writer_thread = threading.Thread( # assign this func to a worker to start in parallel
            target=self.__frame_writer_worker, # Function name
            daemon=True  # Close when app close.
        )
        self._writer_thread.start()  # Starting the thread.

    def collect_imu(self, imu_data:carla.libcarla.ServerSideSensor):
        """Exact data being collected"""
        velocity = self.vehicle.vehicle.get_velocity()
        self.imu_collected_data.append({
            'timestamp': imu_data.timestamp,
            'acc_x': imu_data.accelerometer.x,
            'acc_y': imu_data.accelerometer.y,
            'acc_z': imu_data.accelerometer.z,
            'gyro_x': imu_data.gyroscope.x,
            'gyro_y': imu_data.gyroscope.y,
            'gyro_z': imu_data.gyroscope.z,
            'v_x': velocity.x,
            'v_y': velocity.y
        })

    def collect_rgb(self, rgb_data:carla.libcarla.ServerSideSensor):
        """Collecting data and stack them in queue, and let a worker save frames sequestionally avoiding any frame being dropped"""
        # rgb_data.save_to_disk(frame_path) # this one consume and block thread, and drop frames
        img_array = np.frombuffer(rgb_data.raw_data, dtype=np.uint8)
        img_array = img_array.reshape((rgb_data.height, rgb_data.width, 4))
        img_array = img_array[:, :, :3] # Drop alpha

        img_metadata = (img_array, rgb_data.timestamp, rgb_data.frame) # (img, timestamp, frame)
        self._frames_queue.put(img_metadata)  # Append into queue

        # Render frames
        if self.config.carla_client.cv_render_debug: 
            cv.imshow("CARLA Camera", img_array)
            cv.waitKey(1)

    def __frame_writer_worker(self):
        """Worker thread to save images in the queue"""
        while True:
            img_metadata = self._frames_queue.get()
            if img_metadata is None: break   # As you push None at the end to flush - Poison Pill pattern.
            img_array, timestamp, frame = img_metadata

            frame_path = str(self.output_path / "frames" / f"img_{frame}.png")
            cv.imwrite(frame_path, img_array)

            self.rgb_collected_data.append({
                "timestamp": timestamp,
                "frame": frame,
                "filename": f"img_{frame}.png"
            })
   
    def __warmup_ticks(self, ticks:Optional[int]=None):
        """Warmup ticks to avoid garbage sensor readings of spawns"""
        warmup_ticks = ticks or self.config.vehicle.warmup_ticks
        print(f"Warming env up with {warmup_ticks} ticks")
        for _ in tqdm(range(warmup_ticks), "Warmup..."): self.world.tick()
    
    def __clear_outdir(self, run_name:str):
        """Clean after warmups, and empty frames dir from the previous run"""
        #TODO, i am not sure if this really remove only the warmup ticks, due to the thread. 
        self.imu_collected_data.clear()
        self.rgb_collected_data.clear()

        # Create experiment folder.
        os.makedirs(str(self.output_path / run_name), exist_ok=True)

    def __update_spectator(self, spectator_mode:Optional[bool]=None):
        # Attach spectator camera. 
        if spectator_mode or self.config.vehicle.spectator_mode:
            vehicle_transform = self.vehicle.vehicle.get_transform()
            self.spectator.set_transform(
                carla.Transform(vehicle_transform.location + carla.Location(x=-8, z=4), carla.Rotation(pitch=-15))
            )

    def custom_control(self, i):
        #TODO thinking of moving to vehicle class. 
        control = self.vehicle.vehicle_control
        if i < 100:
            control.throttle, control.steer = 0.5, 0
        elif i < 300:
            control.throttle, control.steer = 0.3, -0.3
        elif i < 400:
            control.throttle, control.steer = 0.3, 0.3
        else:
            control.throttle = 0
            control.brake = 0.5
        return control

    def run(self, run_name:str, num_ticks:int=1000, spectator_mode:Optional[bool]=None, autopilot:Optional[bool]=None):
        self.__warmup_ticks()
        self.__clear_outdir(run_name=run_name)

        if autopilot or self.config.vehicle.autopilot:
            print("Autopilot is enabled..")
            with self.vehicle.autopilot():
                for _ in tqdm(range(num_ticks), "Collecting"):
                    self.__update_spectator(spectator_mode)
                    self.world.tick()
        else: 
            print("It is better to override the default custom_control function")
            for i in tqdm(range(num_ticks), "Collecting"):
                control = self.custom_control(i)
                self.vehicle.vehicle.apply_control(control)
                self.__update_spectator(spectator_mode)
                self.world.tick()

        # Wait until queue on thread is empty
        self._frames_queue.put(None)  # Poison pill pattern, Stoping the queue
        self._writer_thread.join()  # block main thread and Let writer thread finish first

        run_path = self.output_path / run_name
        merge_and_export_df(
            df1=self.imu_collected_data,
            df2=self.rgb_collected_data, 
            export_path=run_path,
            export_name=f"{run_name}.parquet")
        frames_to_video_generator(
            frames_dir=self.output_path / "frames",
            export_path=run_path)