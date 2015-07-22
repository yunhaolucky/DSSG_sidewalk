from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry  
lineLayer = QgsVectorLayer("LineString", "hello", "memory")
lineLayer.startEditing()  
layerData = lineLayer.dataProvider() 
layerData.addAttributes([ QgsField("ID", QVariant.String), QgsField("latStart", QVariant.String), QgsField("lonStart", QVariant.String), QgsField("latEnd", QVariant.String), QgsField("lonEnd", QVariant.String) ])#
lineLayer.commitChanges()
QgsMapLayerRegistry.instance().addMapLayer(lineLayer)  
 