import json


""" Settings for coordinated work ClientCarCenter и Server """
_max_buffer = 4096      # Receive buffer for socket
_input_limits = {'uint64': (0, 2 ** 64 - 1),    # Arbitrary types limit
                 'uint16': (0, 2 ** 16 - 1),
                 'uint8': (0, 2 ** 8 - 1)}
_input_types = {'uint64': int, 'uint16': int, 'uint8': int,     # Python-types for casting
                'float': float, 'string': str, 'char': str}     # arbitrary types

host = '127.0.0.1'      # Server parameters
port = 9099


def encode(d: dict) -> bytes:   # Necessary for equal encode/decode
    j = json.dumps(d, ensure_ascii=False)
    return j.encode('utf-8')


def decode(b: bytes) -> dict:
    return json.loads(b, encoding='utf-8')


default_form = {        # Approximate parameters for enter information about sold car
    "ownerName": "string",
    "serialNumber": 'uint64',
    "modelYear": 'uint64',
    "code": 'string',
    "vehicleCode": 'string',
    "engine": {
        "capacity": 'uint16',
        "numCylinders": 'uint8',
        "maxRpm": 'uint16',
        "manufacturerCode": "char"},
    "fuelFigures": {
        "speed": 'uint16',
        "mpg": 'float',
        "usageDescription": 'string'},
    "performanceFigures": {
        "octaneRating": 'uint16',
        "acceleration": {
            "mph": 'uint16',
            "seconds": 'float'}, },
    "manufacturer": 'string',
    "model": 'string',
    "activationCode": 'string'
}


"""
example = {
    "ownerName": "Bill Gates",
    "serialNumber": 56897546678,
    "modelYear": 2018,
    "code": "GL-600",
    "vehicleCode": "WF0EXXGBBE9J34589",
    "engine": {
        "capacity": 4800,
        "numCylinders": 8,
        "maxRpm": 4000,
        "manufacturerCode": "A"},
    "fuelFigures": {
        "speed": 100,
        "mpg": 4.3,
        "usageDescription": "OLALA"},
    "performanceFigures": {
        "octaneRating": 95,
        "acceleration": {
            "mph": 100,
            "seconds": 3.5}, },
    "manufacturer": "VOLKSWAGEN",
    "model": "POLO",
    "activationCode": "RUN023"
}
"""
