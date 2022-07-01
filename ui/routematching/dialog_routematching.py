import json
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import *
# QGIS-API
from qgis.PyQt import uic
from qgis.core import *
from qgis.gui import *

from ...settings_manager import SettingsManager
from ...api.routematching import get_request

from itertools import repeat

PNUM_PART = 400
PNUM_MAX = 10000


# uiファイルの定義と同じクラスを継承する
class DiadlogRouteMatching(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(os.path.join(os.path.dirname(
            __file__), 'dialog_routematching.ui'), self)

        self.ui.pushButton_run.clicked.connect(self.process_res)
        self.ui.pushButton_cancel.clicked.connect(self.close)

        # UIの設定
        self.ui.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.ui.mMapLayerComboBox.layerChanged.connect(self.set_fields)
        self.ui.mFieldComboBox.setLayer(self.ui.mMapLayerComboBox.currentLayer())
        self.ui.mMapLayerComboBox.setLayer(None)

        # 処理可能のポイント数上限を10000とする
        self.ui.mMapLayerComboBox.layerChanged.connect(self.check_max_point)

        # コンボボックスに空の選択肢を設定
        self.ui.mMapLayerComboBox.setAllowEmptyLayer(True)
        self.ui.mFieldComboBox.setAllowEmptyFieldName(True)

    def check_max_point(self) -> bool:
        cur_lyr = self.ui.mMapLayerComboBox.currentLayer()
        if cur_lyr is not None:
            pcount = cur_lyr.featureCount()
            if pcount > PNUM_MAX:
                self.ui.mMapLayerComboBox.setLayer(None)
                QMessageBox.information(None, "Error", f"The processing limit is {PNUM_MAX} points.")

    def process_res(self):
        # インプットフィチャーを取得する
        lyr = self.get_selected_layer()

        # インプットフィチャーが存在する場合、処理を行う
        if lyr:
            fid = self.get_sort_field()
            input_features = self.get_input_features(input_lyr=lyr, sort_field=fid)

            # UIからmodeパラメタを取得する
            mode = self.get_mode()

            # waypoint以外のパラメタ辞書
            api_para = self.generate_para_dict(mode=mode)
            # waypointリスト
            waypoints = self.generate_waypoint_list(input_features=input_features)

            # Timeoutを防ぐためにpoint数の上限を決めて、入力waypointをいくつかの部分に分割する
            part = -(-len(waypoints) // PNUM_PART)

            # 入力レイヤを分割して複数のURLを作成する
            waypoint_list_per_part = list(map(self.generate_perpart_waypoints, range(1, part + 1), repeat(waypoints)))
            waypoint_paras = list(map(self.generate_waypoint_para, waypoint_list_per_part))

            # APIリクエストする
            res_list = list(map(get_request, repeat(api_para), waypoint_paras))

            # APIレスポンスを処理してfeatureを作成する
            features_for_geojson = []
            features_list = list(map(self.generate_link_features, res_list))
            for feature in features_list:
                features_for_geojson.extend(feature)

            # 各部分の起点終点をつなげる
            start_points = list(map(lambda x: x[0]["geometry"]["coordinates"][0], features_list))
            end_points = list(map(lambda x: x[-1]["geometry"]["coordinates"][1], features_list))
            links = self.generate_links_from_points(start=start_points, end=end_points, part=part)
            features_for_geojson.extend(links)

            # geojsonを作成し、QGIS上で表示する
            geojson = self.generate_link_geojson(features_for_geojson)
            self.show_layers(geojson)

            # 処理完了のダイアログを表示
            QMessageBox.information(None, "Info", "Process is complete.", QMessageBox.Yes)
            self.close()

    def set_fields(self, layer):
        self.ui.mFieldComboBox.setLayer(layer)

    def get_selected_layer(self):
        input_lyr = self.ui.mMapLayerComboBox.currentLayer()
        # レイヤが選択されている確認
        if input_lyr is None:
            QMessageBox.information(None, "Info", "Layer is not selected.", QMessageBox.Yes)
            return
        else:
            return input_lyr

    def get_sort_field(self):
        sort_field = self.ui.mFieldComboBox.currentField()
        return False if sort_field == "" else sort_field

    def get_input_features(self, input_lyr, sort_field):
        if sort_field == False:
            result = list(input_lyr.getFeatures())
        else:
            result = sorted(
                list(input_lyr.getFeatures()), key=lambda f: f[sort_field]
            )
        return result

    def get_mode(self):
        return self.ui.comboBox.currentText()

    def generate_para_dict(self, mode):
        result = {
            "apiKey": self.get_api_key(),
            "mode": f"fastest;{mode};traffic:disabled",
            "language": "ja-jp",
            "depature": "",
        }
        return result

    def generate_waypoint_list(self, input_features):
        result = list(map(lambda feature:
                          f"{feature.geometry().asPoint().y()},{feature.geometry().asPoint().x()}",
                          input_features))
        return result

    def generate_waypoint_para(self, waypoints: dict) -> str:
        """waypoint辞書からURLの形に合った文字列を作成する

        Args:
            waypoints (dict): waypoint辞書

        Returns:
            str: リクエストパラメタ
        """
        waypoint_para = "&".join(list(map(lambda x: f"{x}={waypoints[x]}", waypoints.keys())))
        return waypoint_para

    def generate_perpart_waypoints(self, i: int, waypoints: list) -> list:
        """Point数が上限を超えた場合入力レイヤを分割する

        Args:
            i (int): パーツインディクス

        Returns:
            list:分割後pointのリスト
        """
        waypoint_idx = list(map(lambda x: f"waypoint{x}", list(range(0, PNUM_PART, 1))))
        from_no = (i - 1) * PNUM_PART
        to_no = from_no + PNUM_PART

        return {k: v for k, v in zip(waypoint_idx, waypoints[from_no:to_no])}

    def generate_link_features(self, res: dict) -> list:
        """APIレスポンスからlinkを取得し、geojsonに適したfeatureを作成する

        Args:
            res (dict): APIレスポンス

        Returns:
            list: geojsonフィーチャー
        """

        # Although route/leg are list、api response always include only one item.
        # So, implicitly consider only first one.
        links = res["response"]["route"][0]["leg"][0]["link"]

        features = []
        for link in links:
            # shape to geojson-coordinates
            coordinates = []
            shape = link.get("shape", [])
            for i in range(len(shape) // 2):
                coordinates.append(
                    (shape[2 * i + 1], shape[2 * i])
                )
            # make geojson-feature
            feature = {"type": "Feature",
                       "properties": {
                           "linkId": link["linkId"],
                           "length": link["length"]
                       },
                       "geometry": {
                           "coordinates": coordinates,
                           "type": "LineString"
                       }
                       }
            features.append(feature)

        return features

    def generate_links_from_points(self, start: list, end: list, part: int) -> list:
        """指定した座標によってリンクを作成する

        Args:
            start (list): リンクの起点
            end (list): リンクの終点

        Returns:
            list: geojsonフィーチャー
        """
        start_points = start[1:part]
        end_points = end[0:part - 1]

        features = list(map(lambda x: {"type": "Feature",
                                       "properties": {
                                           "linkId": "",
                                           "length": ""
                                       },
                                       "geometry": {
                                           "coordinates": [
                                               start_points[x],
                                               end_points[x]
                                           ],
                                           "type": "LineString"
                                       }
                                       },
                            list(range(0, part - 1))))

        return features

    def generate_link_geojson(self, features: list) -> str:
        """リンクフィーチャでgeojsonを作成する

        Args:
            features (list): リンクフィーチャー

        Returns:
            str: リンクフィーチャーで作成したgeojson
        """
        geojson_dict = {
            "type": "FeatureCollection",
            "features": features,
        }
        return json.dumps(geojson_dict)

    def show_layers(self, geojson: str):
        """geojsonをQGIS canvasで表示する

        Args:
            geojson (str): 表示するgeojson
        """
        layer = QgsVectorLayer(geojson, "route", "ogr")
        layer.renderer().symbol().setWidth(0.8)
        layer.renderer().symbol().setColor(QColor.fromRgb(255, 0, 0))
        layer.triggerRepaint()
        QgsProject.instance().addMapLayer(layer)

    def get_api_key(self) -> str:
        """SettingsManagerからapiKeyを取得する

        Returns:
            str: ユーザが入力したAPIキー
        """
        smanager = SettingsManager()
        apikey = smanager.get_setting('apikey')
        return apikey
