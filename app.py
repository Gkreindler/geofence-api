from flask import Flask, request
from flask_restful import Api, Resource
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random


app = Flask(__name__)
api = Api(app)


def isNumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class GeoFence(Resource):
    def get(self):
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        # logging
        print("###xxx###:GEOFENCE. time=TIME,devid={},loginid={},lat={},lon={}".format(deviceid, loginid, latitude,
                                                                                       longitude))

        if isNumeric(latitude) and isNumeric(longitude):
            latitude = float(latitude)
            longitude = float(longitude)

            if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
                return {"success": False, "message": "latitude and longitude should be in valid range {} {}".format(latitude, longitude)}, 400
                # Path to the shapefile

            shapefile_path = 'shapefile_nairobi_L1/nairobi_L1.shp'

            # Read the shapefile
            dataframe = gpd.read_file(shapefile_path)

            polygon_name = self.find_polygon_id(latitude, longitude, dataframe)

            if polygon_name == "-99":
                return {"success": False, "message": "couldn't find in any grid"}, 200
            elif polygon_name == "-2":
                return {"success": False, "message": "found in multiple polygons"}, 200
            return {"success": True, "message": "in neighborhood " + polygon_name}, 200
        
        else:
            return {"success": False, "message": "Bad request, latitude and longitude should be numeric parameter"}, 400

    def find_polygon_id(self, latitude, longitude, shapefile):
        point = gpd.GeoSeries([Point(longitude, latitude)])
        point_in_polygons = shapefile.contains(point.geometry[0])

        if any(point_in_polygons):
            polygon_names = shapefile.loc[point_in_polygons, 'name']
            if len(polygon_names) > 1:
                return "-2"  # in multiple polygons, should never happen
            else:
                return polygon_names.iloc[0]
        else:
            return "-99"  # not in any of the polygons


class Login(Resource):
    def get(self):
        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        # logging
        print("###xxx###:LOGIN. time=TIME,devid={},loginid={}".format(deviceid, loginid))

        # read login IDs
        allids_path = 'tables/pilot8_allids.csv'
        allids_df = pd.read_csv(allids_path)

        if isInt(loginid):
            loginid = int(loginid)
            allids = list(allids_df["uniqueid"])
            print("###xxx###:LOGIN. allids={}".format(allids))

            if loginid in allids:
                return {"success": True, "message": "Login OK for {}, {}".format(deviceid, loginid)}, 200
            else:
                return {"success": False, "message": "Unique ID not in the list {}, {}".format(deviceid, loginid)}, 400
        else:
            return {"success": False, "message": "Login or deviceid not integer or not provided"}, 400


class Logout(Resource):
    def get(self):
        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        # logging
        print("###xxx###:LOGOUT. time=TIME,devid={},loginid={}".format(deviceid, loginid))

        if isInt(loginid):
            loginid = int(loginid)

            return {"success": True, "message": "Login OK for {}, {}".format(deviceid, loginid)}, 200
        else:
            return {"success": False, "message": "Login or deviceid not integer or not provided"}, 400


class StartTask(Resource):
    def get(self):
        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        # logging
        print("###xxx###:START_TASK. time=TIME,devid={},loginid={},lat={},lon={}".format(deviceid, loginid, latitude,
                                                                                          longitude))
        ru = random.random()
        if isInt(loginid) and isNumeric(latitude) and isNumeric(longitude) and ru < 0.5:
            loginid = int(loginid)

            latitude = float(latitude)
            longitude = float(longitude)

            return {"success": True, "message": "Start Task OK"}, 200
        else:
            return {"success": False, "message": "Login or deviceid not integer or lat or long not float, or arguments not provided"}, 400


class StopTask(Resource):
    def get(self):
        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        # logging
        print("###xxx###:STOP_TASK. time=TIME,devid={},loginid={},lat={},lon={}".format(deviceid, loginid, latitude,
                                                                                       longitude))

        if isInt(loginid) and isNumeric(latitude) and isNumeric(longitude):
            loginid = int(loginid)

            latitude = float(latitude)
            longitude = float(longitude)

            return {"success": True, "message": "Start Task OK"}, 200
        else:
            return {"success": False,
                    "message": "Login or deviceid not integer or lat or long not float, or arguments not provided"}, 400


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(GeoFence, '/geofence')
api.add_resource(StartTask, '/start')
api.add_resource(StopTask, '/stop')
