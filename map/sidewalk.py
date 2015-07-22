from qgis.core import *
import qgis.utils
from PyQt4.QtCore import *
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry,QgsFeature  
import qgis

class sidewalkList:
    def __init__(self):
        if self.existLayer():
            self.readfromQgsVectorLayer()
        else:
            self.importSidewalk()
        assert hasattr(self, 'layer')

    def readfromQgsVectorLayer(self):
        return
    
    def importSidewalk(self):
        uri = QgsDataSourceURI()
        uri.setConnection("52.11.192.158", "5432", "test", "postgres","")
        uri.setDataSource("public", "shifted", "geom")
        shifted = QgsVectorLayer(uri.uri(), "sidewalks","postgres")
        self.layer = shifted
        QgsMapLayerRegistry.instance().addMapLayer(shifted)
    
    
    def existLayer(self):
        canvas = iface.mapCanvas()
        allLayers = canvas.layers()
        for l in allLayers:
            if l.name() == 'sidewalks':
                self.layer = l
                return True
        return False

    def getbounds(self):
        if hasattr(self, 'bounds'):
            return self.bound
        self.bound = []
        # TODO: find bbox methods of QGSFeature
        #n, e, s, w
        bbox = [90, 0,  0, -180]
        for line in self.layer.getFeatures():
            temp = line.geometry().boundingBox()
            bbox[0] = min(bbox[0],temp.yMinimum())
            bbox[2] = max(bbox[2],temp.yMaximum())
            bbox[1] = min(bbox[1],temp.xMinimum())
            bbox[3] = max(bbox[3],temp.xMaximum())
        return bbox