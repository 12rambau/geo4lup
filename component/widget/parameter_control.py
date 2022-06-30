from ipyleaflet import WidgetControl
from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm

from component.message import cm
from component import parameter as cp


class ParameterControl(WidgetControl):
    def __init__(self, m):

        # save the map as a member of the control
        self.m = m

        # create a clickable btn
        btn = sm.MapBtn(logo="fas fa-cog", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}

        # create the paramter widgets
        bin_items = [
            {"text": getattr(cm.parameter.bin.items, i), "value": i}
            for i in cp.bin_items
        ]
        w_bins = sw.Select(
            items=bin_items, label=cm.parameter.bin.label.capitalize(), v_model=None
        )
        title = sw.Html(tag="h4", children=[cm.parameter.title.capitalize()])
        card_title = sw.CardTitle(children=[title])
        self.content = sw.Tile(
            "", "", inputs=[w_bins], btn=sw.Btn(cm.parameter.btn), alert=sw.Alert()
        ).nest()
        self.content.class_list.replace("ma-5", "ma-0")
        self.content.children[0].class_list.remove("pa-5")
        self.content.children[0].raised = False
        self.content.children[0].elevation = 0
        card_text = sw.CardText(children=[self.content])
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
            value=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[card],
            v_slots=[slot],
            offset_x=True,
            top=True,
            left=True,
        )

        super().__init__(widget=self.menu, position="bottomright")
