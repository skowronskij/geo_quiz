from qgis.PyQt.QtCore import Qt

from qgis.gui import QgsMapToolIdentifyFeature, QgsMapTool
from qgis.core import Qgis
from qgis.utils import iface


class GeoQuizMapTool(QgsMapToolIdentifyFeature):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.layer = None
        self.features_id_list = []
        self.score = 0
        self.total = None
        self.current_feature = None
        self.message_bar = iface.messageBar()

    def show_message(self, message, type, time=2):
        self.message_bar.pushMessage("Geo Quiz", message, type, time)

    def activate(self):
        self.score = 0
        self.select_feature_from_list()
        return super().activate()

    def set_layer(self, layer):
        self.layer = layer

    def set_features_id_list(self, id_list):
        self.features_id_list = id_list
        self.total = len(self.features_id_list)

    def canvasReleaseEvent(self, mouse_click_event):
        if mouse_click_event.button() != Qt.LeftButton:
            return

        identified = self.identify(mouse_click_event.x(), mouse_click_event.y(), [self.layer])
        if identified:
            selected_feature = identified[0].mFeature
            if selected_feature.id() == self.current_feature.id():
                self.select_feature_from_list()
                self.show_message("Dobrze! Zdobywasz punkt!", Qgis.Success, 2)
                self.score += 1
            else:
                self.select_feature_from_list()
                self.select_feature_from_list()
                self.show_message(f"Zła odpowiedź! Wybrałeś {selected_feature['nazwa']}", Qgis.Critical, 3)

    def select_feature_from_list(self):
        if self.features_id_list:
            feature_id = self.features_id_list.pop(0)
            self.current_feature = self.layer.getFeature(feature_id)
            self.show_message(f"Zaznacz: {self.current_feature['nazwa']}", Qgis.Info, 8)
        else:
            self.message_bar.clearWidgets()
            self.show_message(f"Koniec gry. Twój wynik: {self.score}/{self.total}.", Qgis.Warning, 4)
            self.score = 0
            self.canvas.unsetMapTool(self)
