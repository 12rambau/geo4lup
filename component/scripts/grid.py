import inspect
from pathlib import Path

import pandas as pd
import ee
from sepal_ui.scripts import utils as su

from component import parameter as cp


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
def gen_admin_grid(aoi_model, level):

    admin_dataset = ee.FeatureCollection(f"FAO/GAUL/2015/level{level}")

    # different behaviour with respect to the aoi selection
    # filterbounds cannot be used as it includes all the neighboring area
    # and using a negative buffer on aoi is to long to compute
    if aoi_model.name == "cafi_LSIB":
        bins = admin_dataset.filter(ee.Filter.inList("ADM0_CODE", cp.gaul_codes))
    elif aoi_model.admin is not None:
        # extract the first admin line from sepal_ui database
        gaul_dataset = Path(inspect.getfile(su)).parent / "gaul_database.csv"
        df = pd.read_csv(gaul_dataset)
        is_in = df.filter([f"ADM{i}_CODE" for i in range(3)]).isin([aoi_model.admin])
        aoi_level = int(is_in[~((~is_in).all(axis=1))].idxmax(1).iloc[0][3])
        line = df[~((~is_in).all(axis=1))]
        requested_level_code = int(line[f"ADM{level}_CODE"].values[0])

        # use the computerd bin level only when requested level is bigger than aoi
        bin_level = level if aoi_level > level else aoi_level
        bin_code = requested_level_code if aoi_level > level else aoi_model.admin

        bins = admin_dataset.filter(ee.Filter.eq(f"ADM{bin_level}_CODE", bin_code))

    return bins
