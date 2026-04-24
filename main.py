from src.data_collector import DataCollector
from src.vehicle import Vehicle
from src.carla_client import CarlaClient
from config.settings import get_settings

config = get_settings()

carla_client = CarlaClient(cfg=config)
carla_client.clear_world()
carla_client.info()

world = carla_client.world

# Now we need to select a car from the list above
tesla_vehicle = Vehicle(world=world, cfg=config)
imu_sensor = tesla_vehicle.create_and_attach("sensor.other.imu")
rgb_sensor = tesla_vehicle.create_and_attach("sensor.camera.rgb")

data_collector = DataCollector(world, tesla_vehicle.vehicle, cfg=config)
imu_sensor.listen(data_collector.collect_imu)  # Wait and printing the data
rgb_sensor.listen(data_collector.collect_rgb)  # Wait and printing the data

try: 
    data_collector.run()
finally: 
    tesla_vehicle.destroy()

print(data_collector.fuse_sensor())
# data_collector.export_parquet("Carla_Sim_Project\data\imu_run1.parquet")