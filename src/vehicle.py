from contextlib import contextmanager
import random
import carla

from config.settings import Settings
from typing import Optional

class Vehicle():
    def __init__(self, world, cfg:Settings, blueprint_id:Optional[str]=None):  # Note that | is not supported in python 3.7
        self.config = cfg
        self.blueprint_id = blueprint_id or self.config.vehicle.vehicle_blueprint_id
        self.world = world
        self.blueprint_library = world.get_blueprint_library()
        self.vehicle = self.__respawn_vehicle(self.blueprint_id)
        self.vehicle_control = carla.VehicleControl()
        self.attached_objects = []

    @contextmanager
    def autopilot(self):
        self.vehicle.set_autopilot(True)
        yield
        self.vehicle.set_autopilot(False)

    def __respawn_vehicle(self, blueprint_id:str):
        # Now we need to select a car from the blueprint
        vehicle_blueprint = self.blueprint_library.find(blueprint_id)
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        return self.world.spawn_actor(vehicle_blueprint, spawn_point)

    def create_and_attach(self, blueprint_id_to_attach:str):
        """Create the blueprint object and attach it to this vehicle"""
        object_bp = self.blueprint_library.find(blueprint_id_to_attach)
        # Placing the imu sensor, on the car - It could be placed anywhere on the car, it doesn't have to be at a specific location
        object_transform = carla.Transform(carla.Location(2, 0, 1.2)) # (0,0,0) Center of the vechile
        attached_object = self.world.spawn_actor(object_bp, object_transform, attach_to=self.vehicle)

        self.attached_objects.append(attached_object)

        return attached_object

    def destroy(self):
        """Destroying the vahicle and its attachements"""
        for item in self.attached_objects:
            item.stop()
            item.destroy()

        self.vehicle.destroy()