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


def find_polygon_id(latitude, longitude, nbhd_gdf):
    point = gpd.GeoSeries([Point(longitude, latitude)])
    point_in_polygons = nbhd_gdf.contains(point.geometry[0])

    if any(point_in_polygons):
        polygon_names = nbhd_gdf.loc[point_in_polygons, 'Name']

        return polygon_names.iloc[0]

    else:
        return "-99"


class GeoFence(Resource):
    def get(self):
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        # logging
        print("###xxx###:GEOFENCE. time=TIME,devid={},loginid={},lat={},lon={}".format(deviceid, loginid, latitude,
                                                                                       longitude))

        if isNumeric(latitude) and isNumeric(longitude) and isInt(loginid):
            latitude = float(latitude)
            longitude = float(longitude)
            loginid = int(loginid)

            if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
                return {"success": False, "message": "latitude and longitude should be in valid range {} {}".format(latitude, longitude)}, 400
                # Path to the shapefile

            # Read the shapefile
            shapefile_path = 'shapefile_nairobi_L1/nairobi_L1.shp'
            nbhds_gdf = gpd.read_file(shapefile_path)

            polygon_name = find_polygon_id(latitude, longitude, nbhds_gdf)

            if polygon_name == "-99":
                return {
                           "success": False,
                           "message": "Cannot find neighborhood. Please move to a new location and try again."
                       }, 400

            elif polygon_name == "-2":
                return {"success": False, "message": "found in multiple polygons"}, 200

            return {"success": True, "message": "You are in neighborhood " + str(polygon_name)}, 200
        
        else:
            return {"success": False, "message": "Bad request, latitude and longitude should be numeric parameter"}, 400


class Login(Resource):
    def get(self):
        deviceid = request.args.get('deviceid')
        loginid = request.args.get('loginid')

        # logging
        print("###xxx###:LOGIN. time=TIME,devid={},loginid={}".format(deviceid, loginid))

        if isInt(loginid):
            loginid_str = str(loginid)
            loginid = int(loginid)
            print("###xxx###:LOGIN. loginid={}".format(loginid))

            if len(loginid_str) == 6:
                return {"success": True, "message": "Login OK for login ID={}".format(loginid)}, 200
            else:
                return {"success": False, "message": "Unique ID should have 6 digits, but got {}".format(loginid)}, 400
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

            return {"success": True, "message": "Login OK for login ID={}".format(loginid)}, 200
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

        if isInt(loginid) and isNumeric(latitude) and isNumeric(longitude):
            loginid = int(loginid)
            latitude = float(latitude)
            longitude = float(longitude)

            # Read the shapefile
            shapefile_path = 'shapefile_nairobi_L1/nairobi_L1.shp'
            nbhds_gdf = gpd.read_file(shapefile_path)
            polygon_name = find_polygon_id(latitude, longitude, nbhds_gdf)

            ## FOR DEBUGGING: ALWAYS APPROVE
            return {"success": True, "message": "Start Task OK in neighborhood " + str(polygon_name)}, 200

        else:
            return {"success": False, "message": "Error."}, 400


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

            # Read the shapefile
            shapefile_path = 'shapefile_nairobi_L1/nairobi_L1.shp'
            nbhds_gdf = gpd.read_file(shapefile_path)
            polygon_name = find_polygon_id(latitude, longitude, nbhds_gdf)

            return {"success": True, "message": "Stop Task OK in neighborhood " + str(polygon_name)}, 200
        else:
            return {"success": False,
                    "message": "Login or deviceid not integer or lat or long not float, or arguments not provided"}, 400


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(GeoFence, '/geofence')
api.add_resource(StartTask, '/start')
api.add_resource(StopTask, '/stop')
