class Rover:
    def __init__(self, rover_id: str, bridge_host: str, bridge_port: int):
        self.rover_id = rover_id
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port

    def to_json(self):
        return {
            'rover_id': self.rover_id,
            'bridge_host': self.bridge_host,
            'bridge_port': self.bridge_port,
        }
