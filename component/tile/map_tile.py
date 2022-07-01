from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
from sepal_ui.scripts import utils as su
from ipyleaflet import WidgetControl

from component.message import cm
from component import widget as cw
from component import scripts as cs
from component import parameter as cp


class MapTile(sw.Tile):
    def __init__(self):

        # set a map in the center
        self.map = sm.SepalMap()

        # create the different control to add to the map
        fullscreen_control = sm.FullScreenControl(self.map, position="topright")
        self.aoi_control = cw.AoiControl(self.map)
        self.parameter_control = cw.ParameterControl(
            self.map, self.aoi_control.aoi_view.model
        )

        self.map.add_control(fullscreen_control)
        self.map.add_control(self.parameter_control)
        self.map.add_control(self.aoi_control)

        # add a statebar to the map
        self.state_bar = sw.StateBar().add_msg(cm.computation.state.landing)
        self.map.add_control(WidgetControl(widget=self.state_bar, position="topleft"))

        super().__init__(id_="map_tile", title="", inputs=[self.map])

        # add js behaviour
        self.aoi_control.aoi_view.observe(self.parameter_control.tile.reset, "updated")
        self.parameter_control.tile.observe(self.compute_driver_index, "updated")

    # @su.switch("loading", on_widgets=["state_bar"])
    def compute_driver_index(self, change):

        self.state_bar.add_msg(cm.computation.state.computing, True)

        aoi_model = self.aoi_control.aoi_view.model
        model = self.parameter_control.tile.model

        if not all([aoi_model.name is not None, model.bin_type is not None]):
            self.state_bar.add_msg(cm.computation.state.missing)

        # load the index
        index = cs.compute_driver_index(aoi_model, model)
        self.map.addLayer(index, cp.viz, "driver index")

        self.state_bar.add_msg(cm.computation.state.complete, False)

        return
