import carla
import time
import pandas as pd
# 
client = carla.Client("localhost", 2000)
client.set_timeout(10)

world = client.get_world()

settings = world.get_settings()
# settings.no_rendering_mode = True  # Stop rendering, env work but no UI.
settings.synchronous_mode = True
settings.fixed_delta_seconds = 0.05
world.apply_settings(settings)


# Printing the world name
print(world.get_map().name)

# Without fileting, it will just remove everything in the world
actors = world.get_actors().filter("vehicle.*")
for actor in actors:
    actor.destroy()

# It is something like modules or designs, could be also for sensors, and vehicles
blueprint_library = world.get_blueprint_library()
# for pb in blueprint_library:
#     print(pb.id)

# find all vehicles 
# vehicles = blueprint_library.filter("vehicle.*")
# for v in vehicles:
#     print(v.id)

# Now we need to select a car from the list above
vehicles_blueprint = blueprint_library.find("vehicle.tesla.model3")
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicles_blueprint, spawn_point)

# Viewport Camera (Spectator)
spectator = world.get_spectator()
vehicle_transform = vehicle.get_transform()
spectator.set_transform(
    carla.Transform(vehicle_transform.location + carla.Location(x=-8, z=4),
    carla.Rotation(pitch=-15))
)

# sensors_bp = blueprint_library.filter("sensor.*")
camera_bp = blueprint_library.filter("*")
for sensor in camera_bp:
    print(sensor)

imu_bp = blueprint_library.find("sensor.other.imu")
# Placing the imu sensor, on the car - It could be placed anywhere on the car, it doesn't have to be at a specific location
imu_tarnsform = carla.Transform(carla.Location(0, 0, 0)) # Center of the vehicle
imu = world.spawn_actor(imu_bp, imu_tarnsform, attach_to=vehicle)


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


imu.listen(process_imu)  # Wait and printing the data

# Warmup ticks to avoid garbage reads.
for i in range(20):
    world.tick()

imu_list.clear()

# In synchronous mode, carla doesn't work until you tick
# for i in range(200):
#     world.tick()


control = carla.VehicleControl()
for i in range(50_000):
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
    
    vehicle.apply_control(control)
    world.tick()

imu_df = pd.DataFrame(imu_list)
imu_df.to_parquet("Carla_Sim_Project\data\imu_run1.parquet", index=False)

imu.stop()
imu.destroy()
vehicle.destroy()