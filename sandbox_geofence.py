
import geopandas as gpd
from shapely.geometry import Point
import time


def find_polygon_id(latitude, longitude, shapefile):
    point = gpd.GeoSeries([Point(longitude, latitude)])
    point_in_polygons = shapefile.contains(point.geometry[0])

    if any(point_in_polygons):
        polygon_ids = shapefile.loc[point_in_polygons, 'id']
        if len(polygon_ids) > 1:
            return "-2"  # in multiple polygons, should never happen
        else:
            return str(polygon_ids.iloc[0])
    else:
        return "-99"  # not in any of the polygons


if __name__ == '__main__':

    # Path to the shapefile
    shapefile_path = 'shapefile_500/grid.shp'

    # Read the shapefile
    dataframe = gpd.read_file(shapefile_path)

    # test coordinates somewhere in Jakarta, Indonesia
    latitude = -6.2088
    longitude = 106.8456

    # let's see how long this takes with 6769 polygons
    start_time = time.time()
    for i in range(1000):
        polygon_id = find_polygon_id(latitude, longitude, dataframe)
    end_time = time.time()

    print("The coordinates are inside Polygon ID:", polygon_id)

    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds") # ok this is 0.9 seconds, not bad
