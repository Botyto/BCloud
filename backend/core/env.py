from dataclasses import dataclass
import json
import os
import sys
from typing import Any, Dict, List


ValueType = str|bool|int|List[Any]|Dict[str, Any]


@dataclass
class EnvironmentSource:
    sort_key: int
    name: str|None
    data: Dict[str, ValueType]


class EnvironmentData:
    case_sensitive: bool
    sources: List[EnvironmentSource]

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive
        self.sources = []

    def add_dict(self, sort_key: int, data: Dict[str, ValueType], name: str|None = None):
        if not self.case_sensitive:
            data = {k.lower(): v for k, v in data.items()}
        self.sources.append(EnvironmentSource(sort_key, name, data))
        self.sources.sort(key=lambda x: x.sort_key)

    def add_cmdline(self, sort_key: int):
        args = sys.argv[1:]
        config = {}
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                try:
                    value = int(value)
                except ValueError:
                    pass
            else:
                key, value = arg, True
            assert key not in config, "Duplicate key in command line arguments"
            config[key] = value
        self.add_dict(sort_key, config, "cmdline")

    def add_dotenv(self, sort_key: int, filepath: str, optional: bool = False):
        if not os.path.isfile(filepath):
            if not optional:
                raise FileNotFoundError(f"Env source file `{filepath}` not found")
            config = {}
        else:
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
        self.add_dict(sort_key, config, "dotenv")

    def add_json(self, sort_key: int, filepath: str, optional: bool = False):
        if not os.path.isfile(filepath):
            if not optional:
                raise FileNotFoundError(f"Env source file `{filepath}` not found")
            config = {}
        else:
            with open(filepath) as f:
                config = json.load(f)
        self.add_dict(sort_key, config, "json")

    def add_os_env(self, sort_key: int):
        self.add_dict(sort_key, dict(os.environ), "os_env")

    def get(self, key: str, default: ValueType|None = None) -> ValueType|None:
        if not self.case_sensitive:
            key = key.lower()
        for source in self.sources:
            result = source.data.get(key, None)
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
