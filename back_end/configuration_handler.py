from typing import Dict, Tuple
from uuid import uuid4

class Configuration:
    def __init__(self, profile: str, overrides: Dict):
        self.token = None
        self.profile = profile
        self.overrides = overrides

class ConfigurationHandler:
    configurations: Dict[str, Configuration] = {}
    backend = None

    @classmethod
    def SetBackEnd(cls, backend: str):
        cls.backend = backend

    @classmethod
    def Add(cls, identifier: str, profile: str, overrides: Dict) -> Tuple[bool, str]:
        """Tokens are generated as int. Sent as str on the front-end, but as int in the back-end"""

        if identifier not in cls.configurations.keys():
            if cls.backend is not None:
                pass  # TODO: Apply configuration
            else:  # Limited functionality: Accept only best_effort without customization
                if profile != 'best_effort' or len(overrides) > 0:
                    return False, "Requested profile or overrides are not supported"

            config = Configuration(profile, overrides)
            token = uuid4().int
            while token in [c.token for c in cls.configurations.values()]:  # Ensure that the token is unique
                token = uuid4().int
            config.token = token

            cls.configurations[identifier] = config
            return True, str(config.token)
        else:
            return False, f"Identifier '{identifier}' already exists"

    @classmethod
    def Remove(cls, identifier: str, token: str) -> Tuple[bool, str]:
        if identifier not in cls.configurations.keys():
            return False, f"Identifier '{identifier}' does not exist"
        else:
            config = cls.configurations[identifier]
            if token != str(config.token):  # Front-end handles tokens as str
                return False, f"Unauthorized"
            else:
                # TODO: Clear configuration
                _ = cls.configurations.pop(identifier)
                return True, f"Configuration '{identifier}' successfully removed"