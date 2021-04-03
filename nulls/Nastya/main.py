#!/usr/bin/python3


#Импорт всякого очень интересного и не очень
import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget,
        QPushButton, QLineEdit, QInputDialog, QDialog, QDialogButtonBox, QComboBox, QCalendarWidget,
        QFormLayout, QLabel, QSpinBox, QTreeView, QVBoxLayout, QHBoxLayout)

from PyQt5 import QtCore
from PyQt5.QtGui import QImage


#Импортим файл myDatabase.py который написали сами потому что мы могем
import myDatabase


class Msg:
    def __init__(self, img=None, text=None, f=None):
        if img != None:
            self.set_img(img, f)
        elif text != None:
            self.set_text(text, f)
    def set_img(self, img, f = None):
        self.f = f
        self.img = img
        self.date = QtCore.QDateTime.currentDateTime()
    def set_text(self, text, f = None):
        self.f = f
        self.text = text
        self.date = QtCore.QDateTime.currentDateTime()
    def is_text(self):
        return self.text != None
    def is_img(self):
        return self.img != None

class Message(QWidget):
    def __init__(self, msg, parent=None):
        super().__init__(parent=parent)
        self.msg = msg
        #лайоут это кароч такая штука которая рамещает на себе виджеты так чтоб их размер не зависил он конкретных размеров окна
        #лайоут все шо надо растянет или сожмет что все по красоте было
        layout = QFormLayout()
        #Поставим лайоут по методу родителя
        super().setLayout(layout)
        if msg.is_text():
            #Лайоут был особый, пацанский поэтому заполняем его вот так вот
            layout.addRow(QLabel(msg.text), QLabel(msg.date.toString()))
        elif msg.is_img():
            layout.addRow(msg.img, QLabel(msg.date.toString()))



class Dialog(QWidget):
    def __init__(self, msg, author, func, parent=None):
        super().__init__(parent=parent)
        self.func = func
        self.msg = msg
        self.author = author
        layout = QHBoxLayout()
        super().setLayout(layout)
        author_label = QLabel(author)
        layout.addWidget(author_label)
        layout.addWidget(self.msg)

    doubleClicked = QtCore.pyqtSignal()
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()

        



#Чтоб запрашивать данные от пользователя разом напишем диалог
#Диалог он потому что нужно меньше всего переопределять и он работает из коробки
#А главное он просит у пользователя accept или reject и кароч это круто
class myDialog(QWidget):
    #Тупа конструктор
    #l - лист типа [(надпись, виджет с которого будем получать ввод), ...] title - заголовок окошка
    def __init__(self, msgs, title = "question", d_id = None, parent = None):
        self.d_id = d_id
        #Конструктор родителя а именно КуТэДиалога. super() - это типа батя
        super().__init__(parent, QtCore.Qt.Window)
        #Метод установки заголовка он у родителя поэтому от родителя его и дернем
        self.setWindowTitle(title)
        #лайоут это кароч такая штука которая рамещает на себе виджеты так чтоб их размер не зависил он конкретных размеров окна
        #лайоут все шо надо растянет или сожмет что все по красоте было
        layout = QVBoxLayout()
        #Поставим лайоут по методу родителя
        super().setLayout(layout)
        self.msg_layout = QVBoxLayout()
        tmp_layout = QHBoxLayout()

        layout.addLayout(self.msg_layout)
        layout.addLayout(tmp_layout)
        self.send = QPushButton("Send")
        self.send.clicked.connect(self.send_msg)
        self.text = QLineEdit()
        self.attach = QPushButton("Send Pic")
        self.send.clicked.connect(self.attach_msg)
        tmp_layout.addWidget(self.text)
        tmp_layout.addWidget(self.attach)
        tmp_layout.addWidget(self.send)
        
        self.img = None

        self.update(msgs)

    def update(self, msgs):
        for i in reversed(range(self.msg_layout.count())): 
            self.msg_layout.itemAt(i).widget().deleteLater()
        for msg in msgs:
            self.msg_layout.addWidget(msg)

    def attach_msg(self):
        pass

    send_sig = QtCore.pyqtSignal(str)
    def send_msg(self):
        m = Msg(text=self.text.text())
        msg = Message(m)
        self.msg_layout.addWidget(msg)
        self.send_sig.emit(self.text.text())
        self.text.clear()



class MainWindow(QMainWindow):
    #Тупа конструктор который получает имя бд
    def __init__(self, dataBaseName):
        #Тоже что и выше
        super().__init__()
        #Откроем бд и запомним ее в _myDatabase
        self._myDatabase = myDatabase.MyDataBase(dataBaseName)

        #Размеры окошка ширина, высота, позиция от левого края экрана, от правого
        self.setGeometry(300,300,200,200)
        #Тупа заголовок
        self.setWindowTitle('Messanger')
        #Ниже надо раскоментить чтоб поставить иконку
        #self.setWindowIcon(QIcon('Файл с иконкой'))

        #это на будущее
        w = QWidget()

        #Вертикальный лайоут так хочу так и будет
        mainLayout = QVBoxLayout()
        w.setLayout(mainLayout)

        #Вот оно будущее. Специфика QMainWindow
        self.setCentralWidget(w)
        
        #dialogs = self._myDatabase.get_dialogs()
        
        def create_d(text, author):
            m = Msg()
            m.set_text(text)
            msg = Message(m)
            return Dialog(msg, author, lambda x : print(x) )
        dialogs = [create_d("aaa", "bb"), create_d("ccc", "ff")]

        #Пичкуем наши лайоуты всем чем надо
        for d in dialogs:
            d.doubleClicked.connect(self.create_my_dialog)
            mainLayout.addWidget(d)

    def create_my_dialog(self):
        d = self.sender()

        #msgs = self._myDatabase.get_msg_from_author(d.author)

        msgs = []

        m = Msg()
        m.set_text("aaa")
        msgs.append(Message(m))
        m.set_text("bbb")
        msgs.append(Message(m))

        self.md = myDialog(msgs, title=d.author, parent=self)
        self.md.send_sig.connect(self.msg_sended)
        self.md.show()

    def msg_sended(self, msg):
        md = self.sender()
        print('from me to', md.d_id, ':', msg)
        #self._myDatabase.add_msg()


#Это то как все делают чтоб при импорте данного файла куда-то ничего не работало а работало тока тута
if __name__ == "__main__":
    #тут все как положено трогать ничего нельзя потому что так принято
    app = QApplication(sys.argv)

    w = MainWindow("test.bd")
    w.show()

    sys.exit(app.exec_())


