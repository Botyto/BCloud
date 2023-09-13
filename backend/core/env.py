import json
import os
from typing import Any, Dict, List, Tuple


ValueType = str|bool|int|List[Any]|Dict[str, Any]


class EnvironmentData:
    case_sensitive: bool
    configs: List[Tuple[int, dict]]

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive
        self.configs = []

    def add_dict(self, sort_key: int, config: Dict[str, ValueType]):
        if not self.case_sensitive:
            config = {k.lower(): v for k, v in config.items()}
        self.configs.append((sort_key, config))
        self.configs.sort()

    def add_dotenv(self, sort_key: int, filepath: str, optional: bool = False):
        if not os.path.isfile(filepath):
            if not optional:
                raise FileNotFoundError(f"Env source file `{filepath}` not found")
            return
        with open(filepath) as f:
            config = {}
            for line in f.readlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                key, value = line.split("=", 1)
                assert key not in config, "Duplicate key in .env file"
                try:
                    value = int(value)
                except ValueError:
                    pass
                config[key] = value
            self.add_dict(sort_key, config)

    def add_json(self, sort_key: int, filepath: str, optional: bool = False):
        if not os.path.isfile(filepath):
            if not optional:
                raise FileNotFoundError(f"Env source file `{filepath}` not found")
            return
        with open(filepath) as f:
            config = json.load(f)
            self.add_dict(sort_key, config)

    def add_os_env(self, sort_key: int):
        self.add_dict(sort_key, dict(os.environ))

    def get(self, key: str, default: ValueType|None = None) -> ValueType|None:
        if not self.case_sensitive:
            key = key.lower()
        for (_, config) in self.configs:
            result = config.get(key, None)
            if result is not None:
                return result
        return default


class Environment(EnvironmentData):
    @property
    def profile(self):
        return self.get("profile", "prod")

    @property
    def debug(self):
        return self.profile == "dev"

    @property
    def production(self):
        return self.profile == "prod"
