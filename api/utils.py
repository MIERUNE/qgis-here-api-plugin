import json

# QGIS-API
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import QNetworkReply
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface


def handle_reply(reply: QNetworkReply, as_string=False):
    """
    handling QNetworkReply as JSON-dict

    Args:
        reply (QNetworkReply): [description]
        as_string(bool): when true, return json as string

    Returns:
        dict or str
    """
    if reply.error() == QNetworkReply.NoError:
        text_stream = QTextStream(reply)
        text_stream.setCodec("UTF-8")
        text = text_stream.readAll()
        if as_string:
            return text
        return json.loads(text)
    else:
        iface.messageBar().pushWarning("Here", "API Connection error")
        print(reply.error())
        print(reply.errorString())
        if reply.error() in (
            QNetworkReply.ContentAccessDenied,
            QNetworkReply.AuthenticationRequiredError,
        ):
            raise Exception("AuthenticationError")
        elif (
            reply.error() == QNetworkReply.HostNotFoundError
            or reply.error() == QNetworkReply.UnknownNetworkError
        ):
            raise Exception("NetworkError")
        else:
            raise Exception(reply.errorString())

