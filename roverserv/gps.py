import math
import roslibpy


class Gps:
    def __init__(self):
        self.client = roslibpy.Ros(host='192.168.1.10', port=9090)
        self.client.run()

        self.listener = roslibpy.Topic(self.client, '/tag_detections', 'apriltag_ros/AprilTagDetectionArray', throttle_rate=1000, queue_length=10)
        self.listener.subscribe(self.data_received)

    def __del__(self):
        if (self.client):
            self.listener.unsubscribe()
            self.client.terminate()

    def data_received(self, message):
        for detection in message['detections']:
            id = detection['id'][0]

            position = detection['pose']['pose']['pose']['position']
            orientation = detection['pose']['pose']['pose']['orientation']

            x = round(position['x'], 2)
            y = round(position['y'], 2)
            z = round(position['z'], 2)

            rot_x = orientation['x']
            rot_y = orientation['y']
            rot_z = orientation['z']
            rot_w = orientation['w']

            roll = round(math.degrees(math.atan2(2*rot_y*rot_w + 2*rot_x*rot_z, 1 - 2*rot_y*rot_y - 2*rot_z*rot_z)) % 360, 0)
            pitch = round(math.degrees(math.atan2(2*rot_x*rot_w + 2*rot_y*rot_z, 1 - 2*rot_x*rot_x - 2*rot_z*rot_z)) % 360, 0)
            yaw = round(math.degrees(math.asin(2*rot_x*rot_y + 2*rot_z*rot_w)) % 360, 0)

            if (id == 53):
                print(f'{id}: {x}/{y} / {roll}/{pitch}/{yaw}')
