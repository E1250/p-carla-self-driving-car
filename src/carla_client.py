import carla

from config.settings import Settings

class CarlaClient():
    def __set_world_settings(self) -> None:
        self.world_settings.no_rendering_mode = self.config.carla_client.no_rendering_mode
        self.world_settings.synchronous_mode = self.config.carla_client.synchronous_mode
        self.world_settings.fixed_delta_seconds = self.config.carla_client.fixed_delta_seconds
        
    def __init__(self, cfg:Settings):
        self.config = cfg
        
        # Connect to Carla sim
        self.client = carla.Client("localhost", self.config.carla_client.carla_client_port)
        self.client.set_timeout(self.config.carla_client.carla_connection_timeout)

         # Traffic settings
        self.traffic_manager = self.client.get_trafficmanager()

        self.world = self.client.get_world()
        self.world_name = self.world.get_map().name

        # World settings
        self.world_settings = self.world.get_settings()
        self.__set_world_settings()
        self.world.apply_settings(self.world_settings)

       

    def info(self) -> None:
        """Printing the world name, and the list of supported sensors in this world
           Blueprint is like modules or designs for sensors and vehicles
        """
        print(self.world_name)
        self.get_filtered_blueprint(bp_filter="sensor.*")
    
    def get_filtered_blueprint(self, bp_filter:str="*") -> None:
        """Filter and print world blueprints to find vehicles, sensors and cameras"""
        for item in self.world.get_blueprint_library().filter(bp_filter):
            print(item.id)

    def clear_world(self) -> None:
        """Remove existing vehicles in the world, could be reset for the world
        You must declare a filter or it will remove everything from the world
        """
        actors = self.world.get_actors().filter("vehicle.*")
        for actor in actors: actor.destroy()