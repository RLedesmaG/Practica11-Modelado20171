import sys
from PyQt4 import QtCore, QtGui, uic
import xmlrpc
import time 

class ImageDialog(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.proxy= 0
		self.serpiente = None
		self.estado = None
		self.direccion = 1
		self.columna = 0
		self.fila = 0
		self.viboras= []
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(lambda: self.updateTable())
		self.ui = uic.loadUi("cliente.ui")
		self.ui.tableWidget.setRowCount(5)
		self.ui.tableWidget.setColumnCount(5)
		self.ui.ping.clicked.connect(lambda: self.ping())
		self.ui.participar.clicked.connect(lambda: self.participar())
		self.ui.show()

	def ping(self):
		url = self.ui.url.text()
		puerto = self.ui.puerto.value()
		direccion = 'http://'+str(url)+':'+str(puerto)+'/' 
		self.proxy = xmlrpclib.ServerProxy(direccion)
		self.ui.ping.setText('Pinging...')
		try:
			self.ui.ping.setText(self.proxy.ping())
		except:
			self.ui.ping.setText('No pong :(')

	def participar_juego(self):
		url = self.ui.url.text()
		puerto = self.ui.puerto.value()
		direccion = 'http://'+str(url)+':'+str(puerto)+'/' 
		self.proxy = xmlrpclib.ServerProxy(direccion)
		color = '{250,250,250}'
		idn = '0'
		try:
			self.serpiente = self.proxy.yo_juego()
			self.estado = self.proxy.estado_del_juego()
		except:
			print ('no hay conexion')
		self.columna = self.estado['tamX']
		self.fila = self.estado['tamY']
		self.ui.tableWidget.setRowCount(self.rila)
		self.ui.tableWidget.setColumnCount(self.columna)
		self.ui.id.setText(str(self.serpiente['id']))
		self.ui.color.setText(str(self.serpiente['color']))
		self.ui.participar.setVisible(False)
		self.timer.start(self.estado['espera'])
		self.viboras = self.estado['viboras']

	def keyPressEventTable(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Left:
			if (self.direccion != 1):
				self.direccion = 3
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('<')
		elif key == QtCore.Qt.Key_Up:
			if (self.direccion != 2):
				self.direccion = 0
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('^')
		elif key == QtCore.Qt.Key_Right:
			if (self.direccion != 3):
				self.direccion = 1
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('>')
		elif key == QtCore.Qt.Key_Down:
			if (self.direccion != 0):
				self.direccion = 2
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('v')


	def updateTable(self):
		self.ui.tableWidget.clear()
		self.estado = self.proxy.estado_del_juego()
		if (self.estado['tamY']!= self.fila or self.estado['tamX']!= self.columna):
			self.fila = self.estado['tamY']
			self.columna = self.estado['tamX']
			self.ui.tableWidget.setRowCount(self.fila)
			self.ui.tableWidget.setColumnCount(self.columna)
			self.viboras = self.estado['viboras']
		for s in self.viboras:
			cuerpo = s['camino']
			color = s['color']
			for c in cuerpo:
				self.ui.tableWidget.setItem(c[0],c[1], QtGui.QTableWidgetItem("", 0))
				self.ui.tableWidget.item(c[0],c[1]).setBackground(QtGui.QColor(color['r'],color['g'],color['b']))




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = ImageDialog()
    sys.exit(app.exec_())