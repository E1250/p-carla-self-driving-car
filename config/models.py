from pydantic import BaseModel

class CarlaModel(BaseModel):
    no_rendering_mode: bool
    synchronous_mode: bool
    carla_connection_timeout: int
    fixed_delta_seconds: float
    carla_client_port: int
    cv_render_debug: bool

class VehicleModel(BaseModel):
    vehicle_blueprint_id: str
    spectator_mode: bool
    warmup_ticks: int
    output_dir: str
    autopilot: bool