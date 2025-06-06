# QGIS-API
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest

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
    eventLoop.exec()

    result = handle_reply(reply)

    return result
