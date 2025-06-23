import os

# QGIS-API
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton

from .ui.routematching.dialog_routematching import DiadlogRouteMatching
from .ui.dialog_config import DialogConfig

PLUGIN_NAME = "HERE Route API Plugin"


class HereApiPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.icon_path = os.path.join(self.plugin_dir, "imgs", "icon.png")
        self.actions = []
        self.menu = PLUGIN_NAME

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_plugin_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        if add_to_plugin_toolbar:
            self.iface.addToolBarIcon(action)
        self.actions.append(action)
        return action

    def initGui(self):
        # Add a button Menu on the Plugin toolbar
        tool_button = QToolButton()
        icon = QIcon(self.icon_path)
        default_action = QAction(icon, "Route Maching", self.iface.mainWindow())
        default_action.triggered.connect(self.show_dialog_main)
        tool_button.setDefaultAction(default_action)

        menu = QMenu()
        tool_button.setMenu(menu)
        tool_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        menu.addAction(default_action)

        action_config = QAction(icon, "Config", self.iface.mainWindow())
        action_config.triggered.connect(self.show_dialog_config)
        menu.addAction(action_config)

        self.toolButtonAction = self.iface.addToolBarWidget(tool_button)

        # Add actions to the plugin menu
        self.add_action(
            icon_path=None,
            text="Route Matching",
            add_to_plugin_toolbar=False,
            callback=self.show_dialog_main,
            parent=self.win,
        )

        self.add_action(
            icon_path=None,
            text="Config",
            add_to_plugin_toolbar=False,
            callback=self.show_dialog_config,
            parent=self.win,
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        self.iface.removeToolBarIcon(self.toolButtonAction)

    def show_dialog_main(self):
        self.dialog_main = DiadlogRouteMatching()
        self.dialog_main.exec()

    def show_dialog_config(self):
        self.dialog_config = DialogConfig()
        self.dialog_config.exec()
