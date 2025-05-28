import os

# QGIS-API
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from ..settings_manager import SettingsManager

# uiファイルの定義と同じクラスを継承する
class DialogConfig(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dialog_config.ui"), self
        )

        self.ui.pushButton_run.clicked.connect(self._accepted)
        self.ui.pushButton_cancel.clicked.connect(self._rejected)

        smanager = SettingsManager()
        apikey = smanager.get_setting("apikey")
        self.ui.apikey_txt.setText(apikey)

    def _accepted(self):
        smanager = SettingsManager()

        apikey = self.ui.apikey_txt.text()
        smanager.store_setting("apikey", apikey)

        self.close()

    def _rejected(self):
        self.close()
