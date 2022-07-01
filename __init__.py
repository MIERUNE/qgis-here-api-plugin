def classFactory(iface):
    from .here_api_plugin import HereApiPlugin
    return HereApiPlugin(iface)
