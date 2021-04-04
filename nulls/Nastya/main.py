#!/usr/bin/python3


#Импорт всякого очень интересного и не очень
import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget,
        QPushButton, QLineEdit, QInputDialog, QDialog, QDialogButtonBox,
        QFormLayout, QLabel, QSpinBox, QTreeView, QVBoxLayout, QHBoxLayout, QFileDialog)

from PyQt5 import QtCore
from PyQt5.QtGui import (QImage, QPalette, QPixmap, QIcon)


#Импортим файл myDatabase.py который написали сами потому что мы могем
import myDatabase
from myDatabase import Msg

base_img = '/home/shurik/Documents/dino_solo.png'

class Message(QWidget):
    def __init__(self, msg, small=False, parent=None):
        super().__init__(parent=parent)
        self.small = small
        self.msg = msg
        #лайоут это кароч такая штука которая рамещает на себе виджеты так чтоб их размер не зависил он конкретных размеров окна
        #лайоут все шо надо растянет или сожмет что все по красоте было
        layout = QFormLayout()
        #Поставим лайоут по методу родителя
        super().setLayout(layout)
        
        self.pixmap = QPixmap(self.msg.avatar)
        if self.msg.is_f():
            self.pixmap = QPixmap(base_img)
            
        self.pixmap = self.pixmap.scaled(QtCore.QSize(20,20),QtCore. Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation);

        def add_author_date(msg):
            l = QHBoxLayout()
            label = QLabel()
            title = QLabel(msg.date.toString())
            label.setPixmap(self.pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)
            title.setMinimumHeight(self.pixmap.height())
            title.setAlignment(QtCore.Qt.AlignCenter)
            l.addWidget(label)
            l.addWidget(title)
            l.setSpacing(0)
            l.addStretch()
            return l

        print(msg)
        if msg.is_text():
            label = QLabel(msg.text)
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse);
            #Лайоут был особый, пацанский поэтому заполняем его вот так вот
            layout.addRow(label, add_author_date(msg))
        elif msg.is_img():
            img = QLabel()
            pixmap = QPixmap(msg.img)
            if self.small:
                pixmap = pixmap.scaled(QtCore.QSize(50,50),QtCore. Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation);
            img.setPixmap(pixmap)
            layout.addRow(img, add_author_date(msg))
        self.setAutoFillBackground(True)

        self.change_bg(False)
        if msg.replay != None:
            m = Message(msg.replay)
            layout.addRow('', m)


    doubleClicked = QtCore.pyqtSignal()
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


    def change_bg(self, clicked):
        p = QPalette()
        if clicked:
            p.setColor(QPalette.Background, QtCore.Qt.gray)
        else:
            p.setColor(QPalette.Background, QtCore.Qt.white)
        self.setPalette(p);


class Dialog(QWidget):
    def __init__(self, msg, author, d_id=None, parent=None):
        super().__init__(parent=parent)
        self.msg = Message(msg = msg.msg, small = True)
        self.d_id = d_id
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
    def __init__(self, msgs, title = "question", d_id = None, author = None, parent = None):
        self.d_id = d_id
        #Конструктор родителя а именно КуТэДиалога. super() - это типа батя
        super().__init__(parent, QtCore.Qt.Window)
        #Метод установки заголовка он у родителя поэтому от родителя его и дернем
        self.setWindowIcon(QIcon(base_img))
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
        self.attach.clicked.connect(self.attach_msg)
        tmp_layout.addWidget(self.text)
        tmp_layout.addWidget(self.attach)
        tmp_layout.addWidget(self.send)
        
        self.img = None
        self.replay_to = None

        self.update(msgs)

    def update(self, msgs):
        self.msgs = {}

        for i in reversed(range(self.msg_layout.count())): 
            self.msg_layout.itemAt(i).widget().deleteLater()

        for msg in msgs:
            print(msg.date)
            m = Message(msg)
            m.doubleClicked.connect(self.replay)
            self.msgs[msg] = m
            self.msg_layout.addWidget(m)

    def attach_msg(self):
        self.img = QFileDialog.getOpenFileName(self, "Attach Img", ".", "Image Files (*.png *.jpg *.jpeg *.bmp * .tif)")[0]
        self.send_msg()
        self.img = None

    send_sig = QtCore.pyqtSignal(Msg)
    def send_msg(self):
        m = None
        if self.img == None:
            if self.text.text() == '':
                return
            m = Msg(m_id = len(self.msgs.keys()), text=self.text.text(), f=True)
        else:
            m = Msg(m_id = len(self.msgs.keys()), img=self.img, f=True)
        if self.replay_to != None:
            m.replay = self.replay_to
            self.replay_to = None
            self.unselect()
        #msg = Message(m)
        #self.msg_layout.addWidget(msg)
        #self.send_sig.emit(self.text.text())
        self.send_sig.emit(m)
        self.text.clear()

        m = Msg(text="aaaa", f=False)
        self.send_sig.emit(m)

    def unselect(self, l_id = []):
        for k in self.msgs.keys():
            self.msgs[k].change_bg(k in l_id)

    def replay(self):
        msg = self.sender()
        self.replay_to = msg.msg
        print(msg.msg.m_id)
        self.unselect([self.replay_to])


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
        
        dialogs = []
        for d, m in self._myDatabase.dialogs().items():
            msg = Message(m)
            dialogs.append(Dialog(msg, d.account.name, d.id))

        #Пичкуем наши лайоуты всем чем надо
        for d in dialogs:
            d.doubleClicked.connect(self.create_my_dialog)
            mainLayout.addWidget(d)

        self.add = QPushButton("New Dialog")
        self.add.clicked.connect(self.new_dialog)
        mainLayout.addWidget(self.add)

    def new_dialog(self):
        pass

    def create_my_dialog(self):
        d = self.sender()

        msgs = self._myDatabase.messages(d.d_id)
        #d.d_id

        #msgs = []

        #m = Msg(m_id = 0, text = "aaa")
        #msgs.append(m)
        #m = Msg(m_id = 1, text = "bbb")
        #msgs.append(m)

        self.md = myDialog(msgs, title=d.author, parent=self, d_id=d.d_id)
        self.md.send_sig.connect(self.msg_sended)
        self.md.show()

    def msg_sended(self, msg):
        md = self.sender()
        #m = msg
        #m = Msg(m_id = len(md.msgs), text = msg)
        #tmp = list(md.msgs.keys())
        #tmp.append(m)
        #print('from me to', md.d_id, ':', msg)
        self._myDatabase.add_msg(md.d_id, msg)
        md.update(self._myDatabase.messages(md.d_id))
        #md.update(self._myDatabase.get_msg_from_author(md.d_id))


#Это то как все делают чтоб при импорте данного файла куда-то ничего не работало а работало тока тута
if __name__ == "__main__":
    #тут все как положено трогать ничего нельзя потому что так принято
    app = QApplication(sys.argv)

    w = MainWindow("test.db")
    w.show()

    sys.exit(app.exec_())


