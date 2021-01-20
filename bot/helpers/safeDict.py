from typing import Dict


class SafeDict(Dict[str, str]):
    """ modded dict """

    def __missing__(self, key: str) -> str:
        return '{' + key + '}'
