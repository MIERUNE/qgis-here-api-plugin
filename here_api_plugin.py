import os

# QGIS-API
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from .ui.routematching.dialog_routematching import DiadlogRouteMatching
from .ui.dialog_config import DialogConfig

PLUGIN_NAME = 'HERE Route API Plugin'


class HereApiPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = PLUGIN_NAME
        self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
        self.toolbar.setObjectName(PLUGIN_NAME)

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
            parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    def initGui(self):
        # メニュー設定
        self.add_action(
            icon_path=None,
            text="Route Matching",
            callback=self.show_dialog_main,
            parent=self.win)
        self.add_action(
            icon_path=None,
            text="Config",
            callback=self.show_dialog_config,
            parent=self.win)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def show_dialog_main(self):
        self.dialog_main = DiadlogRouteMatching()
        self.dialog_main.exec()

    def show_dialog_config(self):
        self.dialog_config = DialogConfig()
        self.dialog_config.exec()
