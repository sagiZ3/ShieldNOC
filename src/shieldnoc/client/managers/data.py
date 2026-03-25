from dataclasses import dataclass


@dataclass(frozen=True)
class ClientInfo:
    key: str  # unike
    label: str = ""
    third: str = ""

class DataManager:
    def __init__(self):
        pass
