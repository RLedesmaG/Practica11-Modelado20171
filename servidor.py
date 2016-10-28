import sys
import uuid
from PyQt4 import QtGui, QtCore, uic
from xmlrpc.server import SimpleXMLRPCServer
from random import randint

class MyWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('servidor.ui', self)
        
        self.tableWidget.horizontalHeader().setResizeMode(1)
        self.tableWidget.verticalHeader().setResizeMode(1)
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection)
        
        
        self.columnas.valueChanged.connect(self.cambiaColumnas)
        self.filas.valueChanged.connect(self.cambiaFilas)
        self.servidor.clicked.connect(self.iniciaServer)
        self.espera.valueChanged.connect(self.actualizaTimer)
        self.timeout.valueChanged.connect(self.actualizaTimeout)
        self.inicio.clicked.connect(self.start)

        self.jugando = False
        self.pausado = False
        self.timer = None
        self.timerServer = None
        self.timerTabla = None
        self.highscore = 0
        self.serpientes = []
        self.setItems()
        
        self.show()
    
    def cambiaColumnas(self):
        self.tableWidget.setColumnCount(self.columnas.value())
        self.setItems();
    
    def cambiaFilas(self):
        self.tableWidget.setRowCount(self.filas.value())
        self.setItems();


    def setItems(self):        
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(255,255,255))      
               

    def listaViboras(self):       
        lista = list()
        for serpiente in self.serpientes:
            lista.append(serpiente.obtener_diccionario())
        return lista

    def iniciaServer(self):       
        puerto = self.puerto.value()
        direccion = self.url.text()

    def actualizaTabla(self):       
        for serpiente in self.serpientes:
            serpiente.camino = []
            for casilla in serpiente.casillas:                
                serpiente.camino.append((casilla[0], casilla[1])) 
        
        self.server = SimpleXMLRPCServer((direccion, puerto))
        puerto = self.server.server_address[1] 
        self.puerto.setValue(puerto)
        self.puerto.setReadOnly(True)
        self.url.setReadOnly(True)
        self.servidor.setEnabled(False)
        
        self.server.register_function(self.ping)
        self.server.register_function(self.yo_juego)
        self.server.register_function(self.cambia_direccion)
        self.server.register_function(self.estado_del_juego)
        self.server.timeout = 0
        self.timerServer = QtCore.QTimer(self)
        self.timerServer.timeout.connect(self.server.handle_request)
        self.timerServer.start(self.server.timeout)

    def ping(self):
        return "Pong!"

    def yo_juego(self):       
        serpiente = self.nuevaSerpiente()
        diccionario = {"id": serpiente.id, "color": serpiente.color}
        return diccionario

    def cambia_direccion(self, identificador, numero):        
        for s in self.serpientes:           
            if s.id == identificador:                
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True

    def estado_del_juego(self):       
        diccionario = dict()
        diccionario = {
            'espera': self.server.timeout, 
            'tamX': self.tableWidget.columnCount(),
            'tamY': self.tableWidget.rowCount(),
            'viboras': self.listaViboras()
        }
        return diccionario

    def nuevaSerpiente(self):       
        serpiente = Serpiente()
        creada = False
        while not creada:           
            creada = True
            uno = randint(1, self.tableWidget.rowCount()/2)
            dos = uno + 1
            tres = dos +1 
            ancho = randint(1, self.tableWidget.columnCount()-1)
            achecar_1, achecar_2, achecar_3 = [uno, ancho], [dos, ancho], [tres, ancho]
            for s in self.serpientes:                
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 in s.casillas:
                    creada = False
                    break
            serpiente.casillas = [achecar_1, achecar_2, achecar_3]
            self.serpientes.append(serpiente)
            return serpiente

    def actualizaTimeout(self):        
        self.servidor.timeout = self.timeout.value()
        self.timerServer.setInterval(self.timeout.value())


    def start(self):       
        if not self.jugando:
            
            self.nuevaSerpiente()
            self.inicio.setText("Pausar Juego")
            self.dibujar()
            self.timer = QtCore.QTimer(self)            
            self.timer.timeout.connect(self.mover)
            self.timer.start(200)
            self.timerTabla = QtCore.QTimer(self)
            self.timerTabla.timeout.connect(self.actualizaTabla)
            self.timerTabla.start(100)
            self.tableWidget.installEventFilter(self)
            self.jugando = True
        elif self.jugando and not self.pausado:
            self.timer.stop()
            self.pausado = True
            self.inicio.setText("Reanudar Juego")
        elif self.pausado:
            self.timer.start()
            self.pausado = False
            self.inicio.setText("Pausar Juego")

    def end(self):      
        self.serpientes = []
        self.timer.stop()
        self.jugando = False
        self.inicio.setText("Inicia Juego")
        self.setItems()

    
    def eventFilter(self, source, event):        
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget):
                key = event.key()               
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    for serpiente in self.serpientes:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    for serpiente in self.serpientes:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    for serpiente in self.serpientes:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    for serpiente in self.serpientes:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event)

    def dibujar(self):      
        for serpiente in self.serpientes:
            for cuerpo in serpiente.casillas:
                self.tableWidget.item(cuerpo[0], cuerpo[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))            

    def choque(self, serpiente):       
        for cuerpo in serpiente.casillas[0:len(serpiente.casillas)-2]:             
            if serpiente.casillas[-1][0] == cuerpo[0] and serpiente.casillas[-1][1] == cuerpo[1]:
                return True
        return False

    def choque2(self, serpiente2):        
        for serpiente in self.serpientes:            
            if serpiente.id != serpiente2.id:
                for cuerpo in serpiente.casillas[:]:                    
                    if serpiente2.casillas[-1][0] == cuerpo[0] and serpiente2.casillas[-1][1] == cuerpo[1]:
                        
                        self.serpientes.remove(serpiente2)
    def mover(self):       
        for serpiente in self.serpientes:
            if self.choque(serpiente) or self.choque2(serpiente):
                self.serpientes.remove(serpiente)
                self.setItems()
                serpiente_1 = self.nuevaSerpiente()
                self.serpientes = [serpiente_1]
            self.tableWidget.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(255,255,255))
            x = 0
            for tupla in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                tupla[0] = serpiente.casillas[x][0]
                tupla[1] = serpiente.casillas[x][1]           
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.tableWidget.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.tableWidget.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.tableWidget.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.tableWidget.columnCount()-1
        self.dibujar()

    def actualizaTimer(self):     
        valor = self.espera.value()
        self.timer.setInterval(valor)


class Serpiente():   
    def __init__(self):
        self.id = str(uuid.uuid4())[:8]
        red, green, blue = randint(0,255), randint(0,255), randint(0,255)
        self.color = {"r": red, "g": green, "b": blue}
        self.camino = []
        self.casillas = []
        self.camino = []
        self.tam = len(self.casillas)
        self.direccion = "Abajo"

    def obtener_diccionario(self):       
        diccionario = dict()
        diccionario = {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }
        return diccionario
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
