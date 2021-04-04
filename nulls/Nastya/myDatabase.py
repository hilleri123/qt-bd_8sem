import datetime
import sqlite3
from peewee import *

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, QVariant

#Так надо читай доки
mainDatabase = SqliteDatabase(None)
print(mainDatabase)


class Msg:
    def __init__(self, msg=None, text=None, img=None, f=None, date=None, m_id=None, replay=None, avatar=None):
        self.text = text
        self.img = img
        self.f = f
        self.avatar = avatar
        self.date = date
        if self.date == None:
            self.date = QtCore.QDateTime.currentDateTime()
        self.m_id = m_id
        self.replay = replay
        if msg != None:
            self.text = msg.text
            self.img = msg.img
            self.f = msg.f
            self.date = QtCore.QDateTime(msg.date)
            self.m_id = msg.id
            self.replay = Msg(replay)
            self.avatar = msg.dialog.account.avatar

    def is_text(self):
        return self.text != None

    def is_img(self):
        return self.img != None

    def is_f(self):
        return self.f != None and self.f
    
    def __str__(self):
        res = ''
        if self.m_id != None:
            res += str(self.m_id) + ' '
        if self.text != None:
            res += self.text + ' '
        if self.replay != None:
            res += '/ ' + str(self.replay) + ' '
        return res


#Чтоб в каждый класс не писать
class BaseModel(Model):
    class Meta:
        #Да глобальная переменная определит классы. Так надо
        database = mainDatabase

#Класс - Таблица в ней поля

class DBAccount(BaseModel):
    name = CharField(unique = True)
    avatar = CharField()

class DBDialog(BaseModel):
    date = DateField()
    account = ForeignKeyField(DBAccount)

class DBMessage(BaseModel):
    #Чар поле с именем "name"
    #Это поле пусть уникально
    text = CharField(null = True)
    img = CharField(null = True)
    f = BooleanField(default=True)
    date = DateField()
    dialog = ForeignKeyField(DBDialog)
    replay = ForeignKeyField('self', null = True)


#Заполним первый магазин
def initDatabase1():
    acc = DBAccount.create(name="Aaa", avatar="/home/shurik/Documents/лунтик.jpg")
    d = DBDialog.create(account=acc, date=datetime.datetime(2020, 2, 1, 12, 0))
    m = DBMessage.create(text="bbb", date=datetime.datetime(2020, 2, 1, 12, 0), f=True, dialog=d)
    m = DBMessage.create(text="ccc", date=datetime.datetime(2020, 2, 1, 12, 2), f=False, dialog=d, replay=m)

#Второй магазин
def initDatabase2():
    acc = DBAccount.create(name="CAaa", avatar="/home/shurik/Documents/Рикардо.jpg")
    d = DBDialog.create(account=acc, date=datetime.datetime(2020, 2, 1, 13, 0))
    m = DBMessage.create(text="bbb", date=datetime.datetime(2020, 2, 1, 13, 0), f=True, dialog=d)
    m = DBMessage.create(text="ccc", date=datetime.datetime(2020, 2, 1, 13, 2), f=False, dialog=d, replay=m)

#Заполним всю бд
def initDatabase():
    initDatabase1()
    initDatabase2()

class MyDataBase:
    def __init__(self, name):
        #Возьмем бд из файла
        mainDatabase.init(name)
        #Названия и так говорящие
        mainDatabase.connect()
        mainDatabase.create_tables(BaseModel.__subclasses__())
        try:
            #попробуем заполнить бд если бд уже заполнена то уникальные поля бросят ошибку и мы выйдем
            initDatabase()
        except IntegrityError:
            #Чтоб знать что мы не инициализируем ее. Ну так. Лишним не будет
            print("database init canceled")


    def dialogs(self):
        return {i.dialog : Msg(msg=i) for i in DBMessage.select().join(DBDialog).order_by(DBMessage.date).distinct()}

    def add_msg(self, d_id, msg):
        replay = None
        if msg.replay:
            replay = msg.replay.m_id
        f = msg.is_f()
            
        print('!'*50, f)
        if msg.is_text():
            DBMessage.create(text=msg.text, f=f, dialog=DBDialog.get_by_id(d_id), date=msg.date.toPyDateTime(), replay=replay)
        if msg.is_img():
            DBMessage.create(img=msg.img, f=f, dialog=DBDialog.get_by_id(d_id), date=msg.date.toPyDateTime(), replay=replay)
        #DBMessage.create()

    def messages(self, d_id):
        tmp = {i : Msg(msg=i) for i in DBMessage.select().join(DBDialog).where(DBDialog.id == d_id)}
        def add_replay(db_m, m):
            #print('!!!', db_m, db_m.replay, '!', Msg(db_m))
            if db_m.replay != None:
                tmp_db_m = DBMessage.get_by_id(db_m.replay)
                print('!!!', m, '!', Msg(msg=tmp_db_m))
                m.replay = add_replay(tmp_db_m, Msg(msg=tmp_db_m))
            return m
        return [add_replay(k, i) for k, i in tmp.items()]

