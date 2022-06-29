from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm

from .aoi_view import AoiControl


class MapTile(sw.Tile):
    def __init__(self):

        # set a map in the center
        self.map = sm.SepalMap()
        self.map.add_control(sm.FullScreenControl(self.map, position="topright"))

        # add the options controls
        self.map.add_control(AoiControl(self.map))

        super().__init__(id_="map_tile", title="", inputs=[self.map])
