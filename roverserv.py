from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from

##############################
# Globals (cough)
##############################
app = Flask(__name__)
swagger = Swagger(app)

@app.route("/")
@swag_from("static/swagger-doc/main.yml")
def main():
    return "Welcome to RoverServ!"

##############################
# Main
##############################
if __name__ == '__main__':
    port = 5000
    host = "0.0.0.0"
    # Start the web server
    app.run(host=host, debug=True, port=port)
