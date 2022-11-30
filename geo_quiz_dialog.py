import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "geo_quiz_dialog_base.ui"))


class GeoQuizDialog(QDialog, FORM_CLASS):
    def __init__(self, layer, parent=None):
        super(GeoQuizDialog, self).__init__(parent)
        self.setupUi(self)

        self.layer = layer
        self.features_number.setMaximum(self.layer.featureCount())
        self.features_number.setMinimum(1)

    def get_features_number(self):
        return self.features_number.value()
