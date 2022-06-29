from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm

from .aoi_view import AoiControl


class MapTile(sw.Tile):
    def __init__(self):

        # set a map in the center
        self.map = sm.SepalMap()

        # create the different control to add to the map
        fullscreen_control = sm.FullScreenControl(self.map, position="topright")
        self.aoi_control = AoiControl(self.map)

        self.map.add_control(fullscreen_control)
        self.map.add_control(self.aoi_control)

        super().__init__(id_="map_tile", title="", inputs=[self.map])
