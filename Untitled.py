from PyQt4.QtCore import *
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry,QgsFeature  
import overpy

class sidewalkList:
    def __init__(self):
        if not self._existLayer("sidewalks"):
            self.importSidewalk()
            self.importSidewalk_v()
        assert hasattr(self, 'layer')
    
    def importSidewalk(self):
        sidewalks = QgsVectorLayer(self._setUri("shifted").uri(), "sidewalks","postgres")
        self.layer = sidewalks
        QgsMapLayerRegistry.instance().addMapLayer(sidewalks)

    def importSidewalk_v(self):
        self.vertices = QgsVectorLayer(self._setUri("shifted_vertices_pgr","","the_geom").uri(), "sidewalks_v","postgres")
        QgsMapLayerRegistry.instance().addMapLayer(self.vertices)
    
    
    def _existLayer(self,table_name):
        canvas = qgis.utils.iface.mapCanvas()
        allLayers = canvas.layers()
        for l in allLayers:
            if l.name() == table_name:
                self.layer = l
                return True
        return False

    def getbounds(self):
        if hasattr(self, 'bounds'):
            return self.bound
        self.bound = []
        # TODO: find bbox methods(estimated of extents) of QGSFeature
        #n, e, s, w
        bbox = [90, 0,  0, -180]
        for line in self.layer.getFeatures():
            temp = line.geometry().boundingBox()
            bbox[0] = min(bbox[0],temp.yMinimum())
            bbox[2] = max(bbox[2],temp.yMaximum())
            bbox[1] = min(bbox[1],temp.xMinimum())
            bbox[3] = max(bbox[3],temp.xMaximum())
        return bbox

    def _setUri(self, table_name,query_subset = "",geom = "geom"):
        uri = QgsDataSourceURI()
        uri.setConnection("52.11.192.158", "5432", "test", "postgres","")
        uri.setDataSource("public", table_name, geom,query_subset)
        return uri

    def importCurbRamps(self):
        bbox = self.getbounds()
        if self._existLayer('curbRamps'):
            return
        query_statement = "ST_Transform(curbramps.geom,4326) && ST_MakeEnvelope(%.14f,%.14f,%.14f,%.14f,4326)" % (bbox[3],bbox[0],bbox[1],bbox[2])
        self.curbRamps = QgsVectorLayer(self._setUri("curbramps",query_statement).uri(), "curbRamps","postgres")
        QgsMapLayerRegistry.instance().addMapLayer(self.curbRamps)

    def importCrossWalk(self):
        bbox = self.getbounds()
        if self._existLayer('markedCrosswalks'):
            return
        query_statement = "ST_Transform(mrkdcrosswalks.geom,4326) && ST_MakeEnvelope(%.14f,%.14f,%.14f,%.14f,4326)" % (bbox[3],bbox[0],bbox[1],bbox[2])
        self.crosswalks = QgsVectorLayer(self._setUri("mrkdcrosswalks",query_statement).uri(), "markedCrosswalks","postgres")
        QgsMapLayerRegistry.instance().addMapLayer(self.crosswalks)

    def importIntersect(self):
        bbox = self.getbounds()
        #if self._existLayer('markedCrosswalks'):
        #    return
        query_statement = "ST_Transform(sdot_intersection.geom,4326) && ST_MakeEnvelope(%.14f,%.14f,%.14f,%.14f,4326)" % (bbox[3],bbox[0],bbox[1],bbox[2])
        self.intersection = QgsVectorLayer(self._setUri("sdot_intersection",query_statement).uri(), "sdot_intersection","postgres")
        QgsMapLayerRegistry.instance().addMapLayer(self.intersection)


    def _setDB(self):
        db = QSqlDatabase.addDatabase("QPSQL"); # Don't know what does this mean
        db.setHostName("52.11.192.158")
        db.setDatabaseName("test")
        db.setPort(5432)
        db.setUserName("postgres")
        return db


    def assign_intersections(self):
        db = self._setDB()
        





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
        layerData.addAttributes( [ QgsField("id", QVariant.Int)])
        n = 0
        for node in result.nodes:
            fet = QgsFeature()
            n = n + 1
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(node.lon, node.lat)))
            fet.setAttributes([n])
            layerData.addFeatures([fet])
        street_inter_Layer.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(street_inter_Layer)




def main():
    swList = sidewalkList()
    ostrList = osmStreetList(swList.getbounds())
    swList.importCurbRamps()
    swList.importCrossWalk()
    swList.importIntersect()


main()



