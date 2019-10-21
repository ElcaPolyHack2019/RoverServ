class Rover:
    def __init__(self, rover_id: str, bridge_host: str, bridge_port: int):
        self.rover_id = rover_id
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.gps_x = 0
        self.gps_y = 0
        self.gps_orientation = 0

    def drive_forward(self, duration: float):
        # TODO
        pass

    def drive_backward(self, duration: float):
        # TODO
        pass

    def rotate(self, angle: float):
        # TODO
        pass

    def update_gps(self):
        # TODO
        self.gps_x = 0
        self.gps_y = 0
        self.gps_orientation = 0

    def to_json(self):
        return {
            'rover_id': self.rover_id,
            'bridge_host': self.bridge_host,
            'bridge_port': self.bridge_port,
            'gps_x': self.gps_x,
            'gps_y': self.gps_y,
            'gps_orientation': self.gps_orientation,
        }
