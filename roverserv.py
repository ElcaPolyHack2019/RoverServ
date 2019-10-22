from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from
from roverserv import Rover
import yaml

import time

##############################
# Globals (cough)
##############################

def initializeRoverList():
    roverList = []
    with open("rovers.yml", 'r') as stream:
        try:
            dataMap = yaml.safe_load(stream)
            for roverData in dataMap:
                roverList.append(Rover(roverData['name'], roverData['ip'], roverData['port']))
        except yaml.YAMLError as exc:
            print(exc)
    return roverList

app = Flask(__name__)
swagger = Swagger(app)
ros = None
rovers = initializeRoverList()

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

    topics = rover.get_topics()

    return jsonify(topics['topics'])


@app.route("/api/<rover_id>/forward")
def forward(rover_id: str):
    duration = float(is_none(request.args.get("t"), 1.0))
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.drive_forward(duration)

    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/backward")
def backward(rover_id: str):
    duration = float(is_none(request.args.get("t"), 1.0))
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.drive_backward(duration)

    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/rotate")
def rotate(rover_id: str):
    duration = float(is_none(request.args.get("t"), 1.0))
    direction = str(is_none(request.args.get("d"), "left"))
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    if (direction == 'left' or direction == 'l' or direction == 'ccw'):
        rover.rotate_ccw(duration)
    else:
        rover.rotate_cw(duration)

    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/stop")
def stop(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    rover.stop()
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/led")
def led(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    rover.led()
    return jsonify({'success': 'ok'})

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
