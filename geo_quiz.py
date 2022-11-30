import random
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsVectorLayer, QgsProject

from .resources import *
from .geo_quiz_dialog import GeoQuizDialog
from .geo_quiz_map_tool import GeoQuizMapTool


class GeoQuiz:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "GeoQuiz_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr("&Geo Quiz")

        self.europe_layer = None
        self.europe_layer_id = None
        self.start_quiz_action = None
        self.geo_quiz_map_tool = None
        self.__connect_signals()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("GeoQuiz", message)

    def __connect_signals(self):
        QgsProject.instance().layersRemoved.connect(self._on_layers_remove)

    def __disconnect_signals(self):
        QgsProject.instance().layersRemoved.disconnect(self._on_layers_remove)

    def _on_layers_remove(self, deleted_layers_ids):
        if self.europe_layer_id in deleted_layers_ids:
            self.europe_layer = None
            self.europe_layer_id = None
            self.start_quiz_action.setChecked(False)
            self.canvas.unsetMapTool(self.geo_quiz_map_tool)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ":/plugins/geo_quiz/icon.png"
        self.start_quiz_action = self.add_action(
            icon_path, text=self.tr("Start Geo Quiz!"), callback=self.run, parent=self.iface.mainWindow()
        )
        self.start_quiz_action.setCheckable(True)

        # setting up map tool
        self.geo_quiz_map_tool = GeoQuizMapTool(self.canvas)
        self.geo_quiz_map_tool.setAction(self.start_quiz_action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Geo Quiz"), action)
            self.iface.removeToolBarIcon(action)
        self.__disconnect_signals()

    def _add_europe_layer(self):
        """Add Europe layer to current QGIS project"""

        if not self.europe_layer:
            layer_path = os.path.join(self.plugin_dir, "data", "panstwa_europy.geojson")
            self.europe_layer = QgsVectorLayer(layer_path, "Geo Quiz - państwa europy", "ogr")
            self.europe_layer_id = self.europe_layer.id()
            QgsProject.instance().addMapLayer(self.europe_layer)
            self.geo_quiz_map_tool.set_layer(self.europe_layer)

    def _select_random_feautres(self, n):
        features_ids = [feature.id() for feature in self.europe_layer.getFeatures()]
        return random.sample(features_ids, n)

    def run(self, check):
        if not check:
            self.canvas.unsetMapTool(self.geo_quiz_map_tool)
            return

        self._add_europe_layer()

        dialog = GeoQuizDialog(self.europe_layer)
        result = dialog.exec_()

        if result:
            features_number = dialog.get_features_number()
            random_features = self._select_random_feautres(features_number)
            self.geo_quiz_map_tool.set_features_id_list(random_features)
            self.canvas.setMapTool(self.geo_quiz_map_tool)
        else:
            self.start_quiz_action.setChecked(False)
