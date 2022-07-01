from ipyleaflet import WidgetControl
from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
from sepal_ui.scripts import utils as su
from sepal_ui import color as sc
from traitlets import Int
import ee

from component.message import cm
from component import parameter as cp
from component import model as cmo
from component import scripts as cs

__all__ = ["ParameterControl"]


class ParameterTile(sw.Tile):

    updated = Int(0).tag(sync=True)
    "updated integer to notify the rest of the application that the parameters are ready"

    def __init__(self, m, aoi_model):

        # save the useful members
        self.m = m
        self.aoi_model = aoi_model
        self.model = cmo.Geo4lupModel()

        # create the parameter widget
        bin_items = [
            {"text": getattr(cm.parameter.bin.items, i), "value": i}
            for i in cp.bin_items
        ]
        w_bins = sw.Select(items=bin_items, label=cm.parameter.bin.label, v_model=None)

        # wire the model to the widgets
        self.model.bind(w_bins, "bin_type")

        super().__init__("", "", [w_bins], sw.Btn(cm.parameter.btn), sw.Alert())

        # nest tthe tile
        self.nest()
        self.class_list.replace("ma-5", "ma-0")
        self.children[0].class_list.remove("pa-5")
        self.children[0].raised = False
        self.children[0].elevation = 0

        # add some js behaviour
        self.btn.on_event("click", self.select_bining)

    @su.loading_button(debug=False)
    def select_bining(self, widget, event, data):

        # exit if the variables are missing
        if not all(
            [
                self.alert.check_input(self.aoi_model.name),
                self.alert.check_input(self.model.bin_type),
            ]
        ):
            return

        bin_type = self.model.bin_type

        if "TILE" in bin_type:
            size = int(bin_type.replace("TILE", ""))
            bins = cs.gen_grid(self.aoi_model.feature_collection, size)
        elif "ADMIN" in bin_type:
            level = bin_type.replace("ADMIN", "")
            bins = cs.gen_admin_grid(self.aoi_model.feature_collection, level)
        else:
            raise Exception("not yet ready")

        # add the layer on the map
        empty = ee.Image().byte()
        outline = empty.paint(featureCollection=bins, color=1, width=2)
        self.m.addLayer(outline, {"palette": sc.secondary}, "bins")

        self.updated += 1

        return


class ParameterControl(WidgetControl):
    def __init__(self, m, aoi_model):

        # create the internal tile component
        self.tile = ParameterTile(m, aoi_model)

        # create a clickable btn
        btn = sm.MapBtn(logo="fas fa-cog", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}

        # create the card
        title = sw.Html(tag="h4", children=[cm.parameter.title.capitalize()])
        card_title = sw.CardTitle(children=[title])
        card_text = sw.CardText(children=[self.tile])
        card = sw.Card(
            tile=True,
            max_height="40vh",
            min_height="40vh",
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
            top=True,
            left=True,
        )

        super().__init__(widget=self.menu, position="bottomright")

        # add js behaviour
        self.tile.observe(lambda _: setattr(self.menu, "v_model", False), "updated")
