import ee
from sepal_ui.scripts import utils as su


@su.need_ee
def gen_grid(aoi, size):

    bb = aoi.geometry().bounds().transform(ee.Projection("EPSG:3857"), maxError=1)

    # get min max coordiantes
    coords = ee.List(bb.coordinates().get(0))
    xmin = ee.List(coords.get(0)).get(0)
    ymin = ee.List(coords.get(0)).get(1)
    xmax = ee.List(coords.get(2)).get(0)
    ymax = ee.List(coords.get(2)).get(1)

    # given in kilometer but GEE works in meters
    size = size * 1000
    xx = ee.List.sequence(xmin, ee.Number(xmax), size)
    yy = ee.List.sequence(ymin, ee.Number(ymax), size)

    def map_over_x(x):
        def map_over_y(y):
            xmin_loc = ee.Number(x)
            ymin_loc = ee.Number(y)
            xmax_loc = xmin_loc.add(ee.Number(size))
            ymax_loc = ymin_loc.add(ee.Number(size))

            coords = ee.List([xmin_loc, ymin_loc, xmax_loc, ymax_loc])
            rect = ee.Geometry.Rectangle(coords, "EPSG:3857", False)

            return ee.Feature(rect)

        return yy.map(map_over_y)

    cells = xx.map(map_over_x).flatten()

    return ee.FeatureCollection(cells).filterBounds(aoi)


@su.need_ee
def gen_admin_grid(aoi, level):

    admin_dataset = ee.FeatureCollection(f"FAO/GAUL/2015/level{level}")

    # use a negative buffer to avoid to include the neighbors
    aoi_buffer = aoi.geometry().buffer(distance=-1)

    return admin_dataset.filterBounds(aoi_buffer)
