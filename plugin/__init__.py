import requests, urllib.request
from PyQt5.QtWidgets import QAction, QMessageBox, QInputDialog, QLineEdit
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject

def classFactory(iface):
    return FlurstueckssucheNRW(iface)

class FlurstueckssucheNRW:
    def __init__(self, iface):
        self.iface = iface
    def initGui(self):
        self.action = QAction('Flurstueck suchen', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToWebMenu("Flurstueckssuche NRW", self.action)
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action
    def run(self):
        text, okPressed = QInputDialog.getText(None, "Wulf Geoinformatik - Flurstueckssuche NRW","Flurstueck: 5189-34-1550", QLineEdit.Normal, "")
        if okPressed and text != '':
            gemarkungsnummer = text.split('-')[0]
            flurnummer = text.split('-')[1]
            flurstuecksnummer = text.split('-')[2]
            flst = Flurstueck(gemarkungsnummer, flurnummer, flurstuecksnummer, self.iface)
            flst.flurstuecksKenzeichenErzeugen()
            flst.abfrage()
            flst.zeigen()

class Flurstueck:
    def __init__(self, gemarkungsnummer, flurnummer, flurstuecksnummer, iface):
        self.gemarkungsnummer = gemarkungsnummer
        self.flurnummer = flurnummer
        self.flurstuecksnummer = flurstuecksnummer
        self.flurstueckskenzeichen = ''
        self.x = None
        self.y = None
    def abfrage(self):
        myproxies = urllib.request.getproxies()
        uri = 'https://www.wfs.nrw.de/geobasis/wfs_nw_inspire-flurstuecke_alkis?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&STOREDQUERY_ID=urn:ogc:def:query:OGC-WFS::GetFeatureById&ID=CadastralParcel_' + self.flurstueckskenzeichen
        r = requests.get(uri, proxies = myproxies)
        referencePoint = r.text.split('referencePoint')[1]
        gmlPos = referencePoint.split('gml:pos')[1]
        self.x = gmlPos.split(' ')[0].replace('>', '')
        self.y = gmlPos.split(' ')[1].replace('</', '')
    def flurstuecksKenzeichenErzeugen(self):
        self.flurnummer = str(self.flurnummer)
        if len(self.flurnummer) == 1:
            self.flurnummer = '00' + self.flurnummer
        elif len(self.flurnummer) == 2:
            self.flurnummer = '0' + self.flurnummer
        elif len(self.flurnummer) == 3:
            pass
        else:
            pass
        self.flurstuecksnummer = str(self.flurstuecksnummer)
        if len(self.flurstuecksnummer) == 1:
            self.flurstuecksnummer = '0000' + self.flurstuecksnummer
        elif len(self.flurstuecksnummer) == 2:
            self.flurstuecksnummer = '000' + self.flurstuecksnummer
        elif len(self.flurstuecksnummer) == 3:
            self.flurstuecksnummer = '00' + self.flurstuecksnummer
        elif len(self.flurstuecksnummer) == 4:
            self.flurstuecksnummer = '0' + self.flurstuecksnummer
        elif len(self.flurstuecksnummer) == 5:
            pass
        else:
            pass
        self.flurstueckskenzeichen = '05'+ str(self.gemarkungsnummer) + self.flurnummer + self.flurstuecksnummer + '______'
    def zeigen(self):
        layername = self.flurstueckskenzeichen.replace('_','')
        layer =  QgsVectorLayer('Point?crs=epsg:25832', layername , "memory")
        provider = layer.dataProvider()
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY((QgsPointXY(float(self.x), float(self.y)))))
        provider.addFeatures([feature])
        QgsProject.instance().addMapLayers([layer])
