
import datetime

from peewee import *

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, QVariant

#Пишем свою модель потому что там проще и она будет наследником QAbst...TableModel по той же причине
class MyModel(QAbstractTableModel):
    #Тупа конструктор
    def __init__(self, items, labels):
        super().__init__()
        #Скопируем че нада
        #Итемы тут [[00, 01, ...], [10, 11, ...], ...]
        self.list = items.copy()
        #Это названия колонок
        self.colLabels = labels.copy()

    #Так принято прегружать виртуальные методы 
    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        return len(self.colLabels)
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QVariant(self.colLabels[section])
        return QVariant()

    #Тут тоже так принято
    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return QVariant()
        val = ''
        if role == QtCore.Qt.DisplayRole:
            try:
                #Мы не знаем как на передали список и шо там поэтому так
                tmp = self.list[index.row()]
                #Чтоб было одинковый интерфейс сделаем тупле если внутри список то он станет туплом если там соло итем то он станет туплом
                val = tuple(tmp)[index.column()]
            except IndexError:
                pass
        return val






#Так надо читай доки
mainDatabase = SqliteDatabase(None)

#Чтоб в каждый класс не писать
class BaseModel(Model):
    class Meta:
        #Да глобальная переменная определит классы. Так надо
        database = mainDatabase

#Класс - Таблица в ней поля
class Store(BaseModel):
    #Чар поле с именем "name"
    name = CharField()
    #Это поле пусть уникально
    adress = CharField(unique = True)

class Product(BaseModel):
    name = CharField(unique = True)
    praise = IntegerField()
    #store - Это ключе к таблице Store может быть пустым поросто так
    store = ForeignKeyField(Store, null = True)

class Storage(BaseModel):
    adress = CharField(unique = True)
    #backref - значит что у Product появится ключк storage к Storage
    product = ForeignKeyField(Product, backref="storage")

class Rate(BaseModel):
    author = CharField()
    stars = IntegerField()
    product = ForeignKeyField(Product)

class Supply(BaseModel):
    product = ForeignKeyField(Product)
    count = IntegerField()
    date = DateTimeField()

class Cashier(BaseModel):
    store = ForeignKeyField(Store)
    name = CharField(unique = True)
    salary = IntegerField()


#Заполним первый магазин
def initDatabase1():
    tmp_store = Store.create(name = "6shesterechka", adress = "prospect nezavisimosti 17")
    tmp_product = Product.create(name = "anti-coronovirus", praise = 999999, store = tmp_store)
    tmp_storage = Storage.create(adress = "fantasy", product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 1, date = datetime.datetime(2024, 10, 1, 12, 24))
    tmp_supply = Supply.create(product = tmp_product, count = 111, date = datetime.datetime(2026, 10, 1, 12, 24))
    tmp_product = Product.create(name = "mal'chik", praise = 100000*1000000, store = tmp_store)
    tmp_storage = Storage.create(adress = "u drakoshi", product = tmp_product)
    tmp_rate = Rate.create(author = "na zabore", stars = 3, product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 33, date = datetime.datetime(1999, 10, 1, 12, 24))
    tmp_cash = Cashier.create(store = tmp_store, name = "Petya", salary = 1)

#Второй магазин
def initDatabase2():
    tmp_store = Store.create(name = "RF", adress = "Eurasia")
    tmp_product = Product.create(store = tmp_store, name = "oil", praise = 1970)
    tmp_storage = Storage.create(adress = "Ural", product = tmp_product)
    tmp_rate = Rate.create(author = "Naval'nii", stars = 0, product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 10000000000, date = datetime.datetime(2021, 1, 1, 1, 0))
    tmp_cash = Cashier.create(store = tmp_store, name = "Dima Medvedev", salary = 1000000)

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
        mainDatabase.create_tables([Store, Product, Storage, Rate, Supply, Cashier])
        try:
            #попробуем заполнить бд если бд уже заполнена то уникальные поля бросят ошибку и мы выйдем
            initDatabase()
        except IntegrityError:
            #Чтоб знать что мы не инициализируем ее. Ну так. Лишним не будет
            print("database init canceled")


    #Имена магазинов хз зачем
    def stores(self):
        return [i.name for i in Store.select()]

    #Имена товаров
    def products(self):
        return [i.name for i in Product.select()]

    #Имена товаров у которых есть поставки
    def products_in_supply(self):
        return {i.product.name : None for i in Supply.select()}.keys()

    #макс зп
    def max_salary(self):
        return Cashier.select(fn.MAX(Cashier.salary)).scalar()

    #Добавим че надо
    def add(self, num, author, prod):
        finded = Product.get(Product.name == prod)
        if finded is None:
            return
        Rate.create(author = author, stars = num, product = finded)

    #первый запрос
    def first(self, name):
        tmp = [(str(i.date), i.count) for i in Supply.select().join(Product).where(Product.name == name)]
        tmp.append(("all", Supply.select(fn.SUM(Supply.count)).join(Product).where(Product.name == name).scalar()))
        #Напомню. tmp - Это типа двумерный массив(таблица) ["supplies ...", ...] - Это список имен колонок
        return MyModel(tmp, ["supplies of '"+name+"'", "count"])

    #Второй запрос
    def second(self, substr):
        tmp = [(i.adress, i.product.name, i.product.praise) for i in 
                Storage.select().join(Product).join(Store).where(Store.name.contains(substr)).order_by(Product.praise)]
        return MyModel(tmp, ['adress of storages', 'products', 'praise'])

    #Неожиданно но третий запрос
    def third(self, num, date):
        tmp = [(i.stars, i.product.name, i.product.store.adress) for i in 
                Rate.select().join(Product).join(Supply).switch(Product).join(Store).join(Cashier).where((Supply.date > date) & (Cashier.salary < num))]
        return MyModel(tmp, ['rate', 'product', 'store adress'])



