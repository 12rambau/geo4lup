from datetime import datetime as dt
from pathlib import Path

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su
from sepal_ui import mapping as sm
from ipyleaflet import WidgetControl
import ee
from matplotlib.colors import to_rgba
import rasterio as rio
from osgeo import gdal

from component.message import cm
from component import parameter as cp
from component import scripts as cs

_all_ = ["ExportCOntrol"]


class ExportTile(sw.Tile):

    geometry = None

    dataset = None

    name = None

    aoi_name = None

    def __init__(self, aoi_model):

        # init internal variables
        self.aoi_model = aoi_model

        # create the widgets
        self.w_scale = sw.Slider(
            label=cm.export.slider,
            v_model=30,
            min=10,
            max=300,
            thumb_label="always",
            step=10,
            class_="mt-5",
        )
        self.w_btn_sepal = sw.Btn(cm.export.to_sepal, disabled=True)
        self.w_btn_gee = sw.Btn(cm.export.to_gee, disabled=True)
        w_btns = sw.Row(
            children=[self.w_btn_gee, sw.Spacer(), self.w_btn_sepal], class_="ml-5 mr-5"
        )

        # decorate the function
        alert = sw.Alert()
        self.to_asset = su.loading_button(
            alert=alert, button=self.w_btn_gee, debug=True
        )(self.to_asset)
        self.to_sepal = su.loading_button(
            alert=alert, button=self.w_btn_sepal, debug=True
        )(self.to_sepal)

        # create the tile
        super().__init__("", "", [self.w_scale, w_btns], alert=alert)

        # nest the tile
        self.nest()
        self.class_list.replace("ma-5", "ma-0")
        self.children[0].class_list.remove("pa-5")
        self.children[0].raised = False
        self.children[0].elevation = 0

        # add js behaviour
        self.w_btn_sepal.on_event("click", self.to_sepal)
        self.w_btn_gee.on_event("click", self.to_asset)

    def set_data(self, dataset, geometry, name, aoi_name):

        self.geometry = geometry
        self.dataset = dataset
        self.name = name
        self.aoi_name = aoi_name

        # add visualization properties to the image
        palette = ",".join(cp.viz["palette"])
        self.dataset = ee.Image(
            dataset.set(
                {
                    "visualization_0_bands": "b1",
                    "visualization_0_max": 6,
                    "visualization_0_min": 1,
                    "visualization_0_name": "driver index",
                    "visualization_0_palette": palette,
                    "visualization_0_type": "continuous",
                }
            )
        )

        self.w_btn_gee.disabled = False
        self.w_btn_sepal.disabled = False

        return self

    def to_asset(self, widget, event, data):

        folder = Path(ee.data.getAssetRoots()[0]["id"])

        # check if a dataset is existing
        if any([self.dataset == None, self.geometry == None]):
            raise Exception("missing data")

        name = self.name or dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        export_params = {
            "assetId": str(folder / name),
            "image": self.dataset,
            "description": name,
            "scale": self.w_scale.v_model,
            "region": self.geometry,
            "maxPixels": 1e13,
        }

        task = ee.batch.Export.image.toAsset(**export_params)
        task.start()
        self.alert.add_msg(cm.export.alert.to_gee, "success")

        return

    def to_sepal(self, widget, event, data):

        # check if a dataset is existing
        if any([self.dataset == None, self.geometry == None]):
            raise Exception("missing data")

        # set the parameters
        name = self.name or dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        export_params = {
            "image": self.dataset,
            "description": name,
            "scale": self.w_scale.v_model,
            "region": self.geometry,
            "maxPixels": 1e13,
            "crs": "EPSG:3857",
        }

        gdrive = cs.gdrive()
        files = gdrive.get_files(name)
        if files == []:
            task = ee.batch.Export.image.toDrive(**export_params)
            task.start()
            gee.wait_for_completion(name, self.alert)
            files = gdrive.get_files(name)

        # save everything in the same folder as the json file
        result_dir = cp.result_dir / self.aoi_name
        result_dir.mkdir(exist_ok=True)

        tile_list = gdrive.download_files(files, result_dir)
        gdrive.delete_files(files)

        # add the colormap to each tile
        colormap = {}
        for code, color in enumerate(cp.viz["palette"]):
            colormap[code + 1] = tuple(int(c * 255) for c in to_rgba(color))

        # write the colormap to the file
        for tile in tile_list:
            with rio.open(tile) as f:
                profile = f.profile
            with rio.open(tile, "r+", **profile) as f:
                f.write_colormap(1, colormap)

        # create a vrt from the files
        vrt_path = str(result_dir / f"{name}.vrt")
        files = [str(f) for f in tile_list]
        ds = gdal.BuildVRT(vrt_path, files)
        ds.FlushCache()

        self.alert.add_msg(cm.export.alert.to_sepal, "success")

        return


class ExportControl(WidgetControl):
    def __init__(self, aoi_model):

        # create the internal tile component
        self.tile = ExportTile(aoi_model)

        # create a clickable btn
        btn = sm.MapBtn(logo="fas fa-cloud-download-alt", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}

        # create the card
        title = sw.Html(tag="h4", children=[cm.export.title])
        card_title = sw.CardTitle(children=[title])
        card_text = sw.CardText(children=[self.tile])
        card = sw.Card(
            tile=True,
            max_height="35vh",
            min_height="35vh",
            max_width="400px",
            min_width="400px",
            children=[card_title, card_text],
            style_="overflow: auto",
        )

        # assemble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[card],
            v_slots=[slot],
            offset_x=True,
            bottom=True,
            right=True,
        )

        super().__init__(widget=self.menu, position="topleft")
