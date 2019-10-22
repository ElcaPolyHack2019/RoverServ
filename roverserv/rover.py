import threading
import time
import roslibpy


class Rover:
    def __init__(self, rover_id: str, bridge_host: str, bridge_port: int):
        self.lock = threading.Lock()

        self.rover_id = rover_id
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.gps_x = 0
        self.gps_y = 0
        self.gps_orientation = 0

        self.client = self.get_client()
        self.setup_publishers()

    def __del__(self):
        self.client.terminate()

    def get_client(self):
        client = roslibpy.Ros(host=self.bridge_host, port=self.bridge_port)
        client.run()
        return client

    def setup_publishers(self):
        self.joyPublisher = roslibpy.Topic(self.client, '/elcaduck/joy', 'sensor_msgs/Joy', queue_size=1, queue_length=1)
        self.joyPublisher.advertise()

    def release_publishers(self):
        self.joyPublisher.unadvertise()

    def ensure_is_connected(self):
        self.lock.acquire()
        if (not self.client.is_connected):
            print(f"Reconnecting Rover {self.rover_id}")
            self.release_publishers()
            self.client.close()
            self.client.connect()
            self.setup_publishers()
        self.lock.release()

    def drive_forward(self, duration: float):
        self.ensure_is_connected()
        
        self.joyPublisher.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }))
        time.sleep(duration)
        self.stop()

    def drive_backward(self, duration: float):
        talker = roslibpy.Topic(
            self.client, '/elcaduck/joy', 'sensor_msgs/Joy')
        talker.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }))
        time.sleep(duration)
        self.stop()
        talker.unadvertise()

    def rotate_cw(self, duration: float):
        talker = roslibpy.Topic(
            self.client, '/elcaduck/joy', 'sensor_msgs/Joy')
        talker.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]
        }))
        time.sleep(duration)
        self.stop()
        talker.unadvertise()

    def rotate_ccw(self, duration: float):
        talker = roslibpy.Topic(
            self.client, '/elcaduck/joy', 'sensor_msgs/Joy')
        talker.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        }))
        time.sleep(duration)
        self.stop()
        talker.unadvertise()

    def stop(self):
        self.joyPublisher.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }))

    def led(self):
        talker = roslibpy.Topic(
            self.client, '/elcaduck/led_emitter_node/current_led_state', 'std_msgs/String')
        talker.publish(roslibpy.Message({'data': 'OFF'}))
        talker.unadvertise()

    def update_gps(self):
        # TODO
        self.gps_x = 0
        self.gps_y = 0
        self.gps_orientation = 0

    def get_topics(self):
        service = roslibpy.Service(
            self.client, '/rosapi/topics', 'rosapi/Topics')
        request = roslibpy.ServiceRequest()
        result = service.call(request)
        return result

    def to_json(self):
        return {
            'rover_id': self.rover_id,
            'bridge_host': self.bridge_host,
            'bridge_port': self.bridge_port,
            'gps_x': self.gps_x,
            'gps_y': self.gps_y,
            'gps_orientation': self.gps_orientation,
        }
