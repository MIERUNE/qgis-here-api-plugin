from PyQt5.QtCore import QSettings


class SettingsManager:
    SETTING_GROUP = "/here"

    def __init__(self):
        self._settings = {"apikey": ""}
        self.load_settings()

    def load_setting(self, key):
        qsettings = QSettings()
        qsettings.beginGroup(self.SETTING_GROUP)
        value = qsettings.value(key)
        qsettings.endGroup()
        if value:
            self._settings[key] = value

    def load_settings(self):
        for key in self._settings:
            self.load_setting(key)

    def store_setting(self, key, value):
        qsettings = QSettings()
        qsettings.beginGroup(self.SETTING_GROUP)
        qsettings.setValue(key, value)
        qsettings.endGroup()

        self.load_settings()

    def get_setting(self, key):
        return self._settings[key]

    def get_settings(self):
        return self._settings
