import carla

class CarlaClient():
    def __set_world_settings(self):
        self.world_settings.no_rendering_mode = False
        self.world_settings.synchronous_mode = True
        self.fixed_delta_seconds = 0.05

    def __init__(self):
        # Connect to Carla sim
        self.client = carla.Client("localhost", 2000)
        self.client.set_timeout(10)

        self.world = self.client.get_world()
        self.world_name = self.world.get_map().name

        # World settings
        self.world_settings = self.world.get_settings()
        self.__set_world_settings()
        self.world.apply_settings(self.world_settings)

        # Contains world objects
        self.blueprint_library = self.world.get_blueprint_library()

    def info(self):
        print(self.world_name)

    