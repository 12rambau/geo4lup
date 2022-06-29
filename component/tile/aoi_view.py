from ipyleaflet import WidgetControl
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from sepal_ui import aoi
from sepal_ui.scripts import utils as su
from sepal_ui import color as sc
import ee

from component.message import cm


class AoiView(aoi.AoiView):
    """
    extend the aoi_view component from sepal_ui mapping to add
    the extra coloring parameters used in this application. We are forced to copy/paste
    the _update_aoi function
    """

    def __init__(self, **kwargs):

        # limit the interaction to 3 types:
        # custom asset
        # country
        # administrative level 1
        kwargs["methods"] = ["ADMIN0", "ADMIN1", "ASSET"]

        super().__init__(**kwargs)

        # change the name of the custom asset to "subregional"
        tmp_item = self.w_method.items.copy()
        for i in tmp_item:
            if "value" in i:
                if i["value"] == "ASSET":
                    i["text"] = cm.aoi.subregion.capitalize()
                    break

        # forced to empty the item list to trigger the event
        self.w_method.items = []
        self.w_method.items = tmp_item

        # make the asset selector readonly
        self.w_asset.readonly = True

        # only use the countries that are in the CAFI project
        countries = [
            68,  # Democratic republic of the Congo
            59,  # congo
            89,  # gabon
            45,  # cameroon
            76,  # equatorial guinea
            49,  # Central African Republic
        ]
        tmp_item = self.w_admin_0.items.copy()
        tmp_item = [i for i in tmp_item if i["value"] in countries]
        self.w_admin_0.items = []
        self.w_admin_0.items = tmp_item

        # add js behaviour
        self.w_method.observe(self.select_subregional, "v_model")

        # select subregional by default
        self.w_method.v_model = "ASSET"

    @su.loading_button(debug=False)
    def _update_aoi(self, widget, event, data):
        """
        extention of the original method that display information on the map.
        In the ee display we changed the display parameters
        """

        # update the model
        self.model.set_object()

        # update the map
        if self.map_:
            [self.map_.remove_layer(lr) for lr in self.map_.layers if lr.name == "aoi"]
            self.map_.zoom_bounds(self.model.total_bounds())

            if self.ee:

                empty = ee.Image().byte()
                outline = empty.paint(
                    featureCollection=self.model.feature_collection, color=1, width=2
                )

                self.map_.addLayer(outline, {"palette": sc.primary}, "aoi")
            else:
                self.map_.add_layer(self.model.get_ipygeojson())

            self.map_.hide_dc()

        # tell the rest of the apps that the aoi have been updated
        self.updated += 1

    def select_subregional(self, change):
        """select the subregional asset and hide the asset selector"""

        if self.w_method.v_model == None:
            return

        if self.w_method.v_model == "ASSET":
            self.w_asset.hide()
            self.w_asset.w_file.v_model = "projects/ee-geo4lup/assets/cafi_LSIB"

        return


class AoiControl(WidgetControl):
    def __init__(self, m):

        # create a clickable btn
        btn = sm.MapBtn(logo="fas fa-map-marker-alt", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}
        content = AoiView(map_=m)
        content.max_height = "40vh"
        content.min_height = "40vh"
        content.min_width = "400px"
        content.max_width = "400px"
        content.style_ = "overflow: auto"
        content.class_list.add("pa-2")

        # assemble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            value=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[content],
            v_slots=[slot],
            offset_x=True,
            top=True,
            left=True,
        )

        super().__init__(widget=self.menu, position="bottomright")
