from PyQt4.QtCore import *
from sidewalk import sidewalkList
from osmStreet import osmStreetList

def main():
    #layer = iface.activeLayer()
    swList = sidewalkList()
    ostrList = osmStreetList(swList.getbounds())
   # import os
    #os.path.dirname(os.path.abspath(__file__))



main()