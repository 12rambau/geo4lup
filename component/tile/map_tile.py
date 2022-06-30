from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm

from component import widget as cw


class MapTile(sw.Tile):
    def __init__(self):

        # set a map in the center
        self.map = sm.SepalMap()

        # create the different control to add to the map
        fullscreen_control = sm.FullScreenControl(self.map, position="topright")
        aoi_control = cw.AoiControl(self.map)
        parameter_control = cw.ParameterControl(self.map)

        self.map.add_control(fullscreen_control)
        self.map.add_control(aoi_control)
        self.map.add_control(parameter_control)

        super().__init__(id_="map_tile", title="", inputs=[self.map])