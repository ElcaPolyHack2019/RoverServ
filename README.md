# RoverServ
Server application for the PolyHack 2019

# Instructions
1. Create a python virtual environment
```bash
python3 -m venv roverserv-env
```
2. Activate it
```bash
source roverserv-env/bin/activate
```
or
```bash
.\roverserv-env\Scripts\activate
```
3. Install the requirements
```bash
pip3 install -r requirements.txt
```
4. Run the server
```bash
python3 roverserv.py
```

Note: The needed autobahn-python package is not yet python 3.8 compatible.
To run the server with python 3.8, just apply the fix from this pr:
https://github.com/crossbario/autobahn-python/pull/1259/files
(Replace `time.clock` with `time.perf_counter` in `roverserv-env\Lib\site-packages\autobahn\util.py` line 466)

# API
View the api by connecting to http://ip:5000/apidocs/

# Docker
```
docker build -t elcalan/roverserv:latest .
docker run -it --rm -p 5000:5000 elcalan/roverserv:latest
```

