from dataclasses import dataclass

@dataclass(frozen=True)
class ClientInfo:
    key: str  # unike
    label: str = ""

class DataManager:
    def __init__(self):
        pass

    def register_client(self):
        pass

    def get_dashboard_clients(self):
        pass

    def get_client_details(self):
        pass

    def update_client_status(self):
        pass

    def get_system_stats(self):
        pass

    def get_dashboard_data(self):
        pass

    def get_connected_clients_amount(self):
        pass

    def get_cpu_usage(self):
        pass

    def get_ram_usage(self):
        pass

    def get_packets_per_second(self):
        pass
