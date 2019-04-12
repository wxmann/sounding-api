from flask import Flask, request, jsonify
from flask_cors import cross_origin

from datetime import datetime

from sounding import getsounding
from transform import dictify_df, dictify_ser

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})


@app.route('/sounding', methods=['GET'])
@cross_origin()
def route():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    hour = request.args.get('hour')
    ts = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))

    station = request.args.get('station')

    info, data = getsounding(ts, station)
    response_dict = {
        'info': dictify_ser(info),
        'data': dictify_df(data)
    }

    response = jsonify(response_dict)
    response.status_code = 200
    return response


app.run()