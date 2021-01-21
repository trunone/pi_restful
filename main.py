from flask import Flask, request
from flask_restful import Resource, Api

import os
import threading

import board
import busio
import adafruit_ccs811
import adafruit_si7021
import adafruit_bmp280

app = Flask(__name__)
api = Api(app)

i2c = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c)
si7021 = adafruit_si7021.SI7021(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

bmp280.sea_level_pressure = 1017

sensors = {}

sensors['si7021'] = {'temperature': [], 'humidity': []}

sensors['ccs811'] = {'co2': [], 'voc': []}

sensors['bmp280'] = {'temperature': [], 'pressure': [], 'altitude': []}

AVERAGE_PERIOD = 10

def update_si7021():
    try:
        sensors['si7021']['temperature'].append(si7021.temperature)
        sensors['si7021']['humidity'].append(si7021.relative_humidity)
    except Exception as e:
        print(e)

    for key in sensors['si7021'].keys():
        if len(sensors['si7021'][key]) > AVERAGE_PERIOD*2:
            sensors['si7021'][key] = sensors['si7021'][key][-9:]

    threading.Timer(6, update_si7021).start()

def update_ccs811():
    try:
        sensors['ccs811']['co2'].append(ccs811.eco2)
        sensors['ccs811']['voc'].append(ccs811.tvoc)
    except Exception as e:
        print(e)

    for key in sensors['ccs811'].keys():
        if len(sensors['ccs811'][key]) > AVERAGE_PERIOD*2:
            sensors['ccs811'][key] = sensors['ccs811'][key][-9:]

    threading.Timer(6, update_ccs811).start()

def update_bmp280():
    try:
        sensors['bmp280']['temperature'].append(bmp280.temperature)
        sensors['bmp280']['pressure'].append(bmp280.pressure)
        sensors['bmp280']['altitude'].append(bmp280.altitude)
    except Exception as e:
        print(e)

    for key in sensors['bmp280'].keys():
        if len(sensors['bmp280'][key]) > AVERAGE_PERIOD*2:
            sensors['bmp280'][key] = sensors['bmp280'][key][-9:]

    threading.Timer(6, update_bmp280).start()

class GetMiStatus(Resource):
    def get(self):
        return MiVar

class GetSensorStatus(Resource):
    def get(self, sensor):
        try:
            result = {}
            for key in sensors[sensor].keys():
                if len(sensors[sensor][key]) < AVERAGE_PERIOD:
                    return {}
                result[key] = round(sum(sensors[sensor][key][-9:]) / AVERAGE_PERIOD, 2)
            return result
        except Exception as e:
            print(e)
            return {}

api.add_resource(GetSensorStatus, '/sensor/<string:sensor>')

if __name__ == '__main__':
    while not ccs811.data_ready:
        pass
    update_si7021()
    update_ccs811()
    update_bmp280()
    app.run(host='0.0.0.0', port='5000')
