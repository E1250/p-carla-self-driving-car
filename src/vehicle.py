import random
import carla

class Vehicle():
    def __init__(self, blueprint_id:str, world):
        self.blueprint_id = blueprint_id
        self.world = world
        self.blueprint_library = world.get_blueprint_library()
        self.vehicle = self.__respawn_vehicle(blueprint_id)
        self.attached_objects = []

    def __respawn_vehicle(self, blueprint_id:str):
        # Now we need to select a car from the blueprint
        vehicle_blueprint = self.blueprint_library.find(blueprint_id)
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(vehicle_blueprint, spawn_point)
        return self.vehicle

    def create_and_attach(self, blueprint_id_to_attach:str):
        """Create the blueprint object and attach it to this vehicle"""
        object_bp = self.blueprint_library.find(blueprint_id_to_attach)
        # Placing the imu sensor, on the car - It could be placed anywhere on the car, it doesn't have to be at a specific location
        object_transform = carla.Transform(carla.Location(0, 0, 0)) # Center of the vechile
        attached_object = self.world.spawn_actor(object_bp, object_transform, attach_to=self.vehicle)

        self.attached_objects.append(attached_object)

        return attached_object

    def destroy(self):
        """Destroying the vahicle and its attachements"""
        for item in self.attached_objects:
            item.stop()
            item.destroy()

        self.vehicle.destroy()
