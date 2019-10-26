import math
import roslibpy
from .gpsposition import GpsPosition


class Gps:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.client = roslibpy.Ros(host=self.ip, port=self.port)
        self.client.run()

        self.listener = roslibpy.Topic(self.client, '/tag_detections', 'apriltag_ros/AprilTagDetectionArray', throttle_rate=1000, queue_length=10)
        self.listener.subscribe(self.data_received)

        self.last_positions = {}

    def __del__(self):
        if (self.client):
            self.listener.unsubscribe()
            self.client.terminate()

    def get_position(self, id: int):
        if (id in self.last_positions):
            return self.last_positions[id]
        return None

    def data_received(self, message):
        for detection in message['detections']:
            id = detection['id'][0]

            position = self.invertY(detection['pose']['pose']['pose']['position'])
            orientation = self.invertY(detection['pose']['pose']['pose']['orientation'])
            reference = {'w': 0.0, 'x': 1.0, 'y': 0.0, 'z': 0.0}
            rotated = self.mult(self.mult(orientation, reference), self.conjugate(orientation))
            angle = math.atan2(rotated['y'], rotated['x']) * 180.0 / math.pi

            # Adjust for "stretching" of the camera image
            position['x'] = position['x'] / 1.5

            self.last_positions[id] = GpsPosition(id, position['x'], position['y'], angle)

    @staticmethod
    def mult(p, q):
        return {
            'w': p['w']*q['w'] - p['x']*q['x'] - p['y']*q['y'] - p['z']*q['z'],
            'x': p['w']*q['x'] + p['x']*q['w'] + p['y']*q['z'] - p['z']*q['y'],
            'y': p['w']*q['y'] + p['y']*q['w'] + p['z']*q['x'] - p['x']*q['z'],
            'z': p['w']*q['z'] + p['z']*q['w'] + p['x']*q['y'] - p['y']*q['x']
        }

    @staticmethod
    def conjugate(q):
        return {
            'w': q['w'],
            'x': -q['x'],
            'y': -q['y'],
            'z': -q['z'],
        }

    @staticmethod
    def invertY(v):
        res = v.copy()
        res['y'] = -res['y']
        return res
