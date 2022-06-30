from ipyleaflet import WidgetControl
from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm

from component.message import cm


class ParameterControl(WidgetControl):
    def __init__(self, m):

        # save the map as a member of the control
        self.m = m

        # create a clickable btn
        btn = sm.MapBtn(logo="fas fa-cogs", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}

        # create the paramter widgets
        w_bins = sw.Select(items=[], label="Toto", v_model=None)
        self.tile = sw.Tile(
            "nested_tile",
            cm.parameter.title,
            inputs=[w_bins],
            btn=sw.Btn(),
            alert=sw.Alert(),
        )

        # customize the tile to fit the map requirements
        self.tile.max_height = "40vh"
        self.tile.min_height = "40vh"
        self.tile.min_width = "400px"
        self.tile.max_width = "400px"
        self.tile.style_ = "overflow: auto"
        self.tile.class_list.add("pa-2")

        # assemble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            value=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[self.tile],
            v_slots=[slot],
            offset_x=True,
            top=True,
            left=True,
        )

        super().__init__(widget=self.menu, position="bottomright")
