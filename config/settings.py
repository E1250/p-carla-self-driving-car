from pydantic import BaseMode

class CarlaModel(BaseModel):
    no_rendering_mode:bool
    synchronous_mode:bool
    carla_connection_timeout:int
    fixed_delta_seconds=float
    carla_client_port:int

class VehicleModel(BaseModel):
    vehicle_blueprint_id:str
    spectator_mode:bool
    warmup_ticks:int
    output_dir:str


class Settings():
    carla_client:CarlaModel
    vehicle:VehicleModel
