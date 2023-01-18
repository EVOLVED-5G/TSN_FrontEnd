from typing import Dict, Tuple
from uuid import uuid4

class Configuration:
    def __init__(self, profile: str, overrides: Dict):
        self.token = uuid4().hex
        self.profile = profile
        self.overrides = overrides

class ConfigurationHandler:
    configurations: Dict[str, Configuration] = {}

    @classmethod
    def Add(cls, identifier: str, profile: str, overrides: Dict) -> Tuple[bool, str]:
        if identifier not in cls.configurations.keys():
            config = Configuration(profile, overrides)
            cls.configurations[identifier] = config
            # TODO: Apply configuration
            return True, config.token
        else:
            return False, f"Identifier '{identifier}' already exists"

    @classmethod
    def Remove(cls, identifier: str, token: str) -> Tuple[bool, str]:
        if identifier not in cls.configurations.keys():
            return False, f"Identifier '{identifier}' does not exist"
        else:
            config = cls.configurations[identifier]
            if config.token != token:
                return False, f"Unauthorized"
            else:
                # TODO: Clear configuration
                _ = cls.configurations.pop(identifier)
                return True, f"Configuration '{identifier}' successfully removed"