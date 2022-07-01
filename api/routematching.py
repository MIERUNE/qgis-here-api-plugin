from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import *
# QGIS-API
from qgis.PyQt import uic
from qgis.core import *
from qgis.gui import *

from .utils import handle_reply


def get_request(api_para: dict, waypoint_para: str):
    """urlでAPIにリクエストする

    Args:
        api_para (dict): waypoint以外のリクエストパワメタ
        waypoint_para (str): waypointパラメタで作成した文字列

    Returns:
        str: APIレスポンス
    """
    apiKey = api_para["apiKey"]
    mode = api_para["mode"]
    language = api_para["language"]
    departure = "now"
    region = "JPN"
    routeMatch = 1
    url = f"https://routematching.hereapi.com/v8/match/routelinks?apikey={apiKey}&mode={mode}&routeMatch={routeMatch}&language={language}&region={region}&departure={departure}&{waypoint_para}"

    nwa_manager = QgsNetworkAccessManager.instance()
    req = QNetworkRequest(QUrl(url))

    eventLoop = QEventLoop()
    reply = nwa_manager.get(req)
    reply.finished.connect(eventLoop.quit)
    eventLoop.exec_()

    result = handle_reply(reply)

    return result
