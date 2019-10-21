from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from
import roslibpy
from roverserv import Rover

##############################
# Globals (cough)
##############################

app = Flask(__name__)
swagger = Swagger(app)
ros = None
rovers = [
    Rover('1', 'localhost', 9090)
]

##############################
# Web API
##############################


@app.route("/")
@swag_from("static/swagger-doc/main.yml")
def main():
    return "Welcome to RoverServ!"


@app.route("/api/<rover_id>")
@swag_from("static/swagger-doc/rover.yml")
def rover(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    rover.update_gps()
    return jsonify(rover.to_json())


@app.route("/api/<rover_id>/topics")
def topics(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    client = get_socket(rover)
    topics = get_topics(client)
    close_client(client)
    return jsonify(topics['topics'])


@app.route("/api/<rover_id>/forward")
def forward(rover_id: str):
    duration = float(is_none(request.args.get("t"), 1.0))
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    rover.drive_forward(duration)
    return jsonify({'success': 'ok'})

##############################
# Web Sockets
##############################


def get_socket(rover: Rover):
    client = roslibpy.Ros(host=rover.bridge_host, port=rover.bridge_port)
    client.run()
    return client


def get_topics(client):
    service = roslibpy.Service(client, '/rosapi/topics', 'rosapi/Topics')
    request = roslibpy.ServiceRequest()
    result = service.call(request)
    return result


def close_client(client):
    client.close()

##############################
# Misc
##############################


def get_rover_by_id(rover_id: str):
    return next((rover for rover in rovers if rover.rover_id == rover_id), None)


def is_none(value, alternative):
    if value is None:
        return alternative
    else:
        return value

##############################
# Main
##############################


if __name__ == '__main__':
    port = 5000
    host = "0.0.0.0"
    # Start the web server
    app.run(host=host, debug=True, port=port)
