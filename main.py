from src.data_collector import DataCollector
from src.vehicle import Vehicle
from src.carla_client import CarlaClient
from config.settings import get_settings
import os
import shutil
import cv2 as cv

config = get_settings()

# Clear previous run frames
os.makedirs(r"G:\MyComputer\Robotics Wrolds\CARLA_0.9.13\Carla_Sim_Project\data\frames", exist_ok=True)
shutil.rmtree(r"G:\MyComputer\Robotics Wrolds\CARLA_0.9.13\Carla_Sim_Project\data\frames")
os.makedirs(r"G:\MyComputer\Robotics Wrolds\CARLA_0.9.13\Carla_Sim_Project\data\frames")

carla_client = CarlaClient(cfg=config)
carla_client.clear_world()
carla_client.info()

world = carla_client.world

# Now we need to select a car from the list above
tesla_vehicle = Vehicle(world=world, cfg=config)
imu_sensor = tesla_vehicle.create_and_attach("sensor.other.imu")
rgb_sensor = tesla_vehicle.create_and_attach("sensor.camera.rgb")

data_collector = DataCollector(world, tesla_vehicle, cfg=config)
imu_sensor.listen(data_collector.collect_imu)  # Wait and printing the data
rgb_sensor.listen(data_collector.collect_rgb)  # Wait and printing the data

try: 
    data_collector.run(run_name="run1")
finally: 
    tesla_vehicle.destroy()
    cv.destroyAllWindows()