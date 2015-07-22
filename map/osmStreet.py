from qgis.core import *
import qgis.utils
from PyQt4.QtCore import *
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry,QgsFeature  
import qgis
import overpy 

class osmStreetList:
    def __init__(self,bbox):
        if not self.existLayer():
            self.importOsmStreet(bbox)
            assert hasattr(self, 'result')
            self.createStreetLayer(self.result)
            self.createIntersectLayer(self.result)

    def existLayer(self):
        canvas = qgis.utils.iface.mapCanvas()
        allLayers = canvas.layers()
        for l in allLayers:
            if l.name() == 'streets':
                self.layer = l
                return True
        return False

    def importOsmStreet(self,bbox):
        api = overpy.Overpass()
        location_statement = "(%.14f,%.14f,%.14f,%.14f)" % (bbox[0],bbox[1],bbox[2],bbox[3])
        query_statement = """
        (
          node
          ["highway"]
          %s ;
          way
          ["highway"]
          %s ;
        );
        (._;>;);
        out;
        """ % (location_statement, location_statement)
        self.result = api.query(query_statement)

    
    def createStreetLayer(self,result):
        lineLayer = QgsVectorLayer("LineString?crs=EPSG:4326", "streets", "memory")
        lineLayer.startEditing()  
        layerData = lineLayer.dataProvider() 
        layerData.addAttributes( [ QgsField("name", QVariant.String),
                        QgsField("highway",  QVariant.String)])
        for way in result.ways:
            fet = QgsFeature()
            path = []
            for node in way.nodes:
                path.append(QgsPoint(node.lon,node.lat))
            fet.setGeometry(QgsGeometry.fromPolyline(path))
            fet.setAttributes([way.tags.get("name", "n/a"),way.tags.get("highway", "n/a")]);
            layerData.addFeatures([fet])
        lineLayer.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(lineLayer)

    def createIntersectLayer(self,result):
        street_inter_Layer = QgsVectorLayer("Point?crs=EPSG:4326", "street_intersection", "memory")
        street_inter_Layer.startEditing()  
        layerData = street_inter_Layer.dataProvider()
        for node in result.nodes:
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(node.lon, node.lat)))
            layerData.addFeatures([fet])
        street_inter_Layer.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(street_inter_Layer)