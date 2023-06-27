from flask import Flask, request
from flask_restful import Api, Resource
import geopandas as gpd
from shapely.geometry import Point


app = Flask(__name__)
api = Api(app)



def isNumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
class GeoFence(Resource):
    def get(self):
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        if isNumeric(latitude) and isNumeric(longitude):
            latitude = float(latitude)
            longitude = float(longitude)

            if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
                return { "success": False ,"message": "latitude and longitude should be in valid range {} {}".format(latitude, longitude)}, 400    
                # Path to the shapefile
            shapefile_path = 'shapefile_500/grid.shp'

            # Read the shapefile
            dataframe = gpd.read_file(shapefile_path)

            polygon_id = self.find_polygon_id(latitude, longitude, dataframe)
            if polygon_id == -99:
                return {    "success": False ,"message": "couldn't find in any grid" }, 200 
            elif polygon_id == -2:
                return {    "success": False ,"message": "found in multiple polygons" }, 200             
            return {    "success": True ,"message": "in grid {}".format(polygon_id)}, 200
        
        else:
            return {    "success": False, "message": "Bad request, latitude and longitude should be numeric parameter"}, 400
        
    def find_polygon_id(self, latitude, longitude, shapefile):
        point = gpd.GeoSeries([Point(longitude, latitude)])
        point_in_polygons = shapefile.contains(point.geometry[0])

        if any(point_in_polygons):
            polygon_ids = shapefile.loc[point_in_polygons, 'id']
            if len(polygon_ids) > 1:
                return -2  # in multiple polygons, should never happen
            else:
                return polygon_ids.iloc[0]
        else:
            return -99  # not in any of the polygons
        
api.add_resource(GeoFence, '/geofence')