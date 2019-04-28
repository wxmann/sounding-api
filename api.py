from flask import Flask, request, jsonify
from flask_cors import cross_origin

import handlers

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})


@app.route('/sounding', methods=['GET'])
@cross_origin()
def sounding_route():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    hour = request.args.get('hour')
    station = request.args.get('station')

    response_body = handlers.sounding_handler(year, month, day, hour, station)
    response = jsonify(response_body)
    response.status_code = 200
    return response


@app.route('/params', methods=['POST'])
@cross_origin()
def params_route():
    soundingdata = request.get_json()

    response_body = handlers.parameter_handler(soundingdata)
    response = jsonify(response_body)
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run()