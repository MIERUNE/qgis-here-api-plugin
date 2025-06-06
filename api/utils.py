import json

# QGIS-API
from qgis.utils import iface
from qgis.PyQt.QtCore import QTextStream
from qgis.PyQt.QtNetwork import QNetworkReply


def handle_reply(reply: QNetworkReply, as_string=False):
    """
    handling QNetworkReply as JSON-dict

    Args:
        reply (QNetworkReply): [description]
        as_string(bool): when true, return json as string

    Returns:
        dict or str
    """
    if reply.error() == QNetworkReply.NetworkError.NoError:
        text_stream = QTextStream(reply)
        text_stream.setCodec("UTF-8")
        text = text_stream.readAll()
        if as_string:
            return text
        return json.loads(text)
    else:
        if reply.error() in (
            QNetworkReply.NetworkError.ContentAccessDenied,
            QNetworkReply.NetworkError.AuthenticationRequiredError,
        ):
            iface.messageBar().pushWarning("HERE Route API Plugin", "AuthenticationError")
        elif (
            reply.error() == QNetworkReply.NetworkError.HostNotFoundError
            or reply.error() == QNetworkReply.NetworkError.UnknownNetworkError
        ):
            iface.messageBar().pushWarning("HERE Route API Plugin", "NetworkError")
        else:
            iface.messageBar().pushWarning("HERE Route API Plugin", reply.errorString())
