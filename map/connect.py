from qgis.core import *
import qgis.utils

from sidewalk import sidewalkList
from osmStreet import osmStreetList

from PyQt4.QtCore import *

def main():
    #layer = iface.activeLayer()
    swList = sidewalkList()
    ostrList = osmStreetList(swList.getbounds())
main()