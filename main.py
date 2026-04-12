from src.vehicle import Vehicle
from src.carla_client import CarlaClient

import carla
import pandas as pd

# 
carla_client = CarlaClient()
carla_client.info()

world = carla_client.world

# #TODO, ignore this line - Without fileting, it will just remove everything in the world
actors = world.get_actors().filter("vehicle.*")
for actor in actors:
    actor.destroy()

# It is something like modules or designs, could be also for sensors, and vehicles
carla_client.get_filtered_blueprint()

# Now we need to select a car from the list above
tesla_vehicle = Vehicle(blueprint_id="vehicle.tesla.model3", world=world)
# vehicle = vehicle.respawn_vehicle()

# # Viewport Camera (Spectator)
# spectator = world.get_spectator()
# vehicle_transform = vehicle.get_transform()
# spectator.set_transform(
#     carla.Transform(vehicle_transform.location + carla.Location(x=-8, z=4),
#     carla.Rotation(pitch=-15))
# )

# sensors_bp = blueprint_library.filter("sensor.*")
# camera_bp = blueprint_library.filter("*")
# for sensor in camera_bp:
#     print(sensor)

imu_sensor = tesla_vehicle.create_and_attach("sensor.other.imu")


imu_list = []
def process_imu(imu_data):
    imu_list.append({
        'timestamp': imu_data.timestamp,
        'acc_x': imu_data.accelerometer.x,
        'acc_y': imu_data.accelerometer.y,
        'acc_z': imu_data.accelerometer.z,
        'gyro_x': imu_data.gyroscope.x,
        'gyro_y': imu_data.gyroscope.y,
        'gyro_z': imu_data.gyroscope.z,
    })


imu_sensor.listen(process_imu)  # Wait and printing the data

# Warmup ticks to avoid garbage reads.
for i in range(20):
    world.tick()

imu_list.clear()

# In synchronous mode, carla doesn't work until you tick
for i in range(200):
    world.tick()


control = carla.VehicleControl()
for i in range(200):
    if i < 50:
        control.throttle = 0.5
        control.steer = 0
    elif i < 100:
        control.throttle = 0.3
        control.steer = -0.3
    elif i < 150:
        control.throttle = 0.3
        control.steer = 0.3
    else:
        control.throttle = 0
        control.brake = 0.5
    
    tesla_vehicle.vehicle.apply_control(control)
    world.tick()

imu_df = pd.DataFrame(imu_list)
imu_df.to_parquet("Carla_Sim_Project\data\imu_run1.parquet", index=False)
print(imu_df.tail(30))


tesla_vehicle.destroy()