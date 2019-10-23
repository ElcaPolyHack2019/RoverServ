import threading
import time
import base64
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
        self.client = None
        self.last_image = None
        self.last_lidar = None

    def __del__(self):
        if (self.client):
            self.release_publishers()
            self.release_listeners()
            self.client.terminate()

    def setup_client(self):
        print(
            f'Setting up rover {self.rover_id} on {self.bridge_host}:{self.bridge_port}')
        try:
            self.client = roslibpy.Ros(
                host=self.bridge_host, port=self.bridge_port)
            self.client.run()
            return True
        except:
            print(f'Failed to connect to {self.rover_id}')
            self.client = None
            return False

    def setup_publishers(self):
        self.joyPublisher = roslibpy.Topic(
            self.client, '/elcaduck/joy', 'sensor_msgs/Joy', queue_size=1, queue_length=1)
        self.joyPublisher.advertise()

    def release_publishers(self):
        self.joyPublisher.unadvertise()

    def setup_listeners(self):
        self.imageListener = roslibpy.Topic(self.client, '/elcaduck/camera_node/image/compressed', 'sensor_msgs/CompressedImage', throttle_rate=1000)
        self.imageListener.subscribe(self.image_received_callback)
        self.lidarListener = roslibpy.Topic(self.client, '/scan', 'sensor_msgs/LaserScan', throttle_rate=1000)
        self.lidarListener.subscribe(self.lidar_received_callback)

    def release_listeners(self):
        self.imageListener.unsubscribe()
        self.lidarListener.unsubscribe()

    def ensure_is_connected(self):
        self.lock.acquire()
        if (not self.client):
            # First initial connection
            result = self.setup_client()
            if (result):
                # The connection succeeded, setup the publishers/listeners
                self.setup_publishers()
                self.setup_listeners()
        elif (not self.client.is_connected):
            # The client is running but not connected anymore, reconnect
            print(f"Reconnecting Rover {self.rover_id}")
            self.release_publishers()
            self.release_listeners()
            self.client.close()
            self.client.connect()
            self.setup_publishers()
            self.setup_listeners()
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
        self.ensure_is_connected()

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
        self.ensure_is_connected()

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
        self.ensure_is_connected()

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
        self.ensure_is_connected()

        self.joyPublisher.publish(roslibpy.Message({
            'buttons': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'axes': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }))

    def get_image(self):
        self.ensure_is_connected()

        if (not self.last_image):
            return None
        decoded_image = base64.decodebytes(str.encode(self.last_image))
        return decoded_image

    def led(self):
        self.ensure_is_connected()

        service = roslibpy.Service(
            self.client, '/elcaduck/led_emitter_node/set_pattern', 'std_msgs/String')
        #request = roslibpy.ServiceRequest("pattern_name: {data: RED}")
        request = roslibpy.ServiceRequest({'data': 'RED'})
        result = service.call(request)
        return result
    
    def lidar(self):
        self.ensure_is_connected()
        return self.last_lidar

    def update_gps(self):
        # TODO
        self.gps_x = 0
        self.gps_y = 0
        self.gps_orientation = 0

    def get_topics(self):
        self.ensure_is_connected()

        service = roslibpy.Service(
            self.client, '/rosapi/topics', 'rosapi/Topics')
        request = roslibpy.ServiceRequest()
        result = service.call(request)
        return result

    def image_received_callback(self, message):
        self.last_image = message['data']
    
    def lidar_received_callback(self, message):
        self.last_lidar = message

    def to_json(self):
        return {
            'rover_id': self.rover_id,
            'bridge_host': self.bridge_host,
            'bridge_port': self.bridge_port,
            'gps_x': self.gps_x,
            'gps_y': self.gps_y,
            'gps_orientation': self.gps_orientation,
        }
