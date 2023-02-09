from typing import Dict, Tuple
from uuid import uuid4
from requests import post
from .profile_handler import ProfileHandler

class Configuration:
    def __init__(self, profile: str, overrides: Dict):
        self.token = None
        self.profile = profile
        self.overrides = overrides

    @property
    def AsPayload(self) -> Dict:
        values = ProfileHandler.GetProfileData(self.profile).copy()
        values.update(self.overrides)

        return {
            'token': self.token,
            'values': values
        }

class ConfigurationHandler:
    configurations: Dict[str, Configuration] = {}
    backend = None

    @classmethod
    def SetBackEnd(cls, backend: str) -> None:
        cls.backend = backend

    @classmethod
    def Post(cls, endpoint: str, payload: Dict) -> Tuple[bool, str]:
        response = post(url=f"{cls.backend}/{endpoint}", json=payload, headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            try:
                return False, response.json()["detail"]
            except Exception as e:
                return False, f"Invalid reply from TSN backend: Status '{response.status_code}', Exception: '{e}'"

        return True, ""

    @classmethod
    def Add(cls, identifier: str, profile: str, overrides: Dict) -> Tuple[bool, str]:
        """Tokens are generated as int. Sent as str on the front-end, but as int in the back-end"""

        if identifier not in cls.configurations.keys():
            config = Configuration(profile, overrides)
            token = uuid4().int
            while token in [c.token for c in cls.configurations.values()]:  # Ensure that the token is unique
                token = uuid4().int
            config.token = token

            if cls.backend is not None:
                success, detail = cls.Post('/apply', {'identifier': identifier, **config.AsPayload})
                if not success:
                    return False, detail

            else:  # Limited functionality: Accept only best_effort without customization
                if profile != 'best_effort' or len(overrides) > 0:
                    return False, "Requested profile or overrides are not supported"

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
                if cls.backend is not None:
                    success, detail = cls.Post('/clear', {'identifier': identifier, **config.AsPayload})
                    if not success:
                        return False, detail

                _ = cls.configurations.pop(identifier)
                return True, f"Configuration '{identifier}' successfully removed"