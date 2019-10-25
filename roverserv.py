from flask import Flask, Response, request, jsonify, abort, make_response
from flask_cors import CORS
from flasgger import Swagger, swag_from
from roverserv import Rover
from roverserv import Gps
import yaml
import os

import time

##############################
# Globals (cough)
##############################

app = Flask(__name__)
CORS(app)
# TODO: How to extract this into .yml?
template = {
    "info": {
        "title": "Polyhack 2019 Elca rover server API",
        "description": "Overview of endpoints for controlling the rover."
    }
}
swagger = Swagger(app, template=template)
rovers = []
gps: Gps = None

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

    gps_position = gps.get_position(rover.tag)
    if (gps_position):
        rover.update_gps(gps_position)
    return jsonify(rover.to_json())


@app.route("/api/<rover_id>/topics")
@swag_from("static/swagger-doc/topics.yml")
def topics(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    topics = rover.get_topics()
    return jsonify(topics['topics'])


@app.route("/api/<rover_id>/forward")
@swag_from("static/swagger-doc/forward.yml")
def forward(rover_id: str):
    duration = get_param_float(request, ["duration", "dur", "d"], 1.0)
    power = get_param_float(request, ["power", "p"], 1.0)
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.drive_forward(duration, power)
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/backward")
@swag_from("static/swagger-doc/backward.yml")
def backward(rover_id: str):
    duration = get_param_float(request, ["duration", "dur", "d"], 1.0)
    power = get_param_float(request, ["power", "p"], 1.0)
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.drive_backward(duration, power)
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/rotate")
@swag_from("static/swagger-doc/rotate.yml")
def rotate(rover_id: str):
    duration = get_param_float(request, ["duration", "dur", "d"], 1.0)
    power = get_param_float(request, ["power", "p"], 1.0)
    direction = get_param_str(request, ["direction", "dir"], "left")
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    if (direction == 'left' or direction == 'l' or direction == 'ccw'):
        rover.rotate_ccw(duration, power)
    else:
        rover.rotate_cw(duration, power)
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/stop")
@swag_from("static/swagger-doc/stop.yml")
def stop(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.stop()
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/image")
@swag_from("static/swagger-doc/image.yml")
def image(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    image_data = rover.get_image()
    if (not image_data):
        abort(Response('No image yet'))

    response = make_response(image_data)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route("/api/<rover_id>/led")
@swag_from("static/swagger-doc/led.yml")
def led(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")

    rover.led()
    return jsonify({'success': 'ok'})


@app.route("/api/<rover_id>/lidar")
@swag_from("static/swagger-doc/lidar.yml")
def lidar(rover_id: str):
    rover = get_rover_by_id(rover_id)
    if rover is None:
        abort(404, description=f"Rover with id {rover_id} not found.")
    data = rover.lidar()
    return jsonify(data)

##############################
# Misc
##############################


def get_rover_by_id(rover_id: str):
    return next((rover for rover in rovers if rover.rover_id == rover_id), None)


def get_param(request, names: [], default):
    for name in names:
        if (name in request.args):
            return request.args.get(name)
    return default


def get_param_float(request, names: [], default):
    return float(get_param(request, names, default))


def get_param_str(request, names: [], default):
    return str(get_param(request, names, default))


def parse_settings():
    global rovers
    global gps
    settingsFile = os.getenv("ROVERSERVER_SETTINGS", "settings.yml")
    with open(settingsFile, 'r') as stream:
        try:
            dataMap = yaml.safe_load(stream)
            # Initialize the Gps
            gps = Gps(dataMap['gps']['ip'], dataMap['gps']['port'])
            # Initialize the rovers
            for roverData in dataMap['rovers']:
                rovers.append(Rover(roverData['name'], roverData['ip'], roverData['port'], roverData['tag']))
        except yaml.YAMLError as exc:
            print(exc)
    return dataMap

##############################
# Main
##############################


if __name__ == '__main__':
    # Initialize settings
    parse_settings()
    # Start the web server
    port = int(os.getenv("ROVERSERV_PORT", 5000))
    host = "0.0.0.0"
    app.run(host=host, debug=True, port=port)
