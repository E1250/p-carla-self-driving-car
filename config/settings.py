from pydantic import BaseModel
from pathlib import Path
import yaml

from models import CarlaModel, VehicleModel
from functools import lru_cache

class Settings(BaseModel):
    carla_client:CarlaModel
    vehicle:VehicleModel

    # We don't need .env here, No need for SettingsConfigDict and settings_customise_source
    @classmethod
    def from_yaml(cls, yaml_path=Path(__file__).parent / "settings.yaml"):
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@lru_cache(maxsize=1)
def get_settings():
    """Dependency Injection alternative, cache the output of this return, and return each time."""
    return Settings.from_yaml()


if __name__ == "__main__":
    configs = get_settings()
    print(type(configs))
    print(configs)