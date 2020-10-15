import sqlite3 as sql

class TransactionObject():
    database    = "STOCKS.db"
    conn        = None
    cur         = None
    connected   = False

    def connect(self):
        TransactionObject.conn      = sql.connect(TransactionObject.database)
        TransactionObject.cur       = TransactionObject.conn.cursor()
        TransactionObject.connected = True

    def disconnect(self):
        TransactionObject.conn.close()
        TransactionObject.connected = False

    def execute(self, sql, parms = None):
        if TransactionObject.connected:
            if parms == None:
                TransactionObject.cur.execute(sql)
            else:
                TransactionObject.cur.execute(sql, parms)
            return True
        else:
            return False

    def fetchall(self):
        return TransactionObject.cur.fetchall()

    def persist(self):
        if TransactionObject.connected:
            TransactionObject.conn.commit()
            return True
        else:
            return False



def initDB():
    trans = TransactionObject()
    trans.connect()
    trans.execute("CREATE TABLE IF NOT EXISTS STOCKS (id INTEGER PRIMARY KEY , mercado TEXT, papel TEXT, status TEXT, data DATE, mes INTEGER, ano INTEGER, valor DOUBLE, pm DOUBLE, quantidade INTEGER, qconsolidado INTEGER, custos DOUBLE, consolidado TEXT, valorAtual DOUBLE, dataFechamento DATE, dayTrade INTEGER)")
    trans.persist()
    trans.disconnect()

def insert(mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado, valorAtual, dataFechamento, dayTrade):
    trans = TransactionObject()
    trans.connect()
    trans.execute("INSERT INTO STOCKS VALUES(NULL, ?,?,?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado, valorAtual, dataFechamento, dayTrade))
    trans.persist()
    trans.disconnect()


# def view():
#     trans = TransactionObject()
#     trans.connect()
#     trans.execute("SELECT mercado, papel, status, data, valor, quantidade, pm, qconsolidado, custos FROM STOCKS")
#     rows = trans.fetchall()
#     trans.disconnect()
#     return rows


def viewAll():
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS")
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def search(mercado="", papel="", status="", data="", mes="", ano="", valor="", pm="", quantidade="", qconsolidado="", custos="", consolidado=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? or papel=? or status=? or data=? or mes=? or ano=? or valor=? or pm=? or quantidade=? or qconsolidado=? or custos=? or consolidado=?", (mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

# def searchReturnAll(mercado="", papel="", status="", data="", mes="", ano="", valor="", pm="", quantidade="", qconsolidado="", custos="", consolidado=""):
#     trans = TransactionObject()
#     trans.connect()
#     trans.execute("SELECT * FROM STOCKS WHERE mercado=? or papel=? or status=? or data=? or mes=? or ano=? or valor=? or pm=? or quantidade=? or qconsolidado=? or custos=? or consolidado=?", (mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado))
#     rows = trans.fetchall()
#     trans.disconnect()
#     return rows

def searchMonthandYear(mercado="", papel="", status="", data="", mes="", ano="", valor="", pm="", quantidade="", qconsolidado="", custos="", consolidado=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? or papel=? or status=? or data=? or mes=? and ano=? or valor=? or pm=? or quantidade=? or qconsolidado=? or custos=? or consolidado=?", (mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def searchMercadoPapel(mercado="", papel=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? and papel=?", (mercado, papel))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def searchPapel(papel=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE papel=?", (papel))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def searchPapeisDistintos():
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT DISTINCT papel FROM STOCKS ", ())
    rows = trans.fetchall()
    trans.disconnect()
    return rows


def searchPapelConsolidado(mercado="", papel="", consolidado=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? and papel=? and consolidado=?", (mercado, papel, consolidado))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def searchPosicaoConsolidada(consolidado="", qconsolidado=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE consolidado=? and qconsolidado>?", (consolidado, qconsolidado))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

#utilizada paenas na logica do pm/consolidado
def search2Insert(id="", mercado="", papel=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT status, pm, qconsolidado FROM STOCKS WHERE id <=? and mercado=? and papel=?", (id, mercado, papel))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

#apenas para calculo IRPF
def searchVendas(mercado="", status="", mes="", ano="", dayTrade=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? and status=? and mes=? and ano=? and dayTrade=?", (mercado, status, mes, ano, dayTrade))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

#apenas para calculo IRPF
def searchOperacoesMes(mercado="", mes="", ano="", dayTrade=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE mercado=? and mes=? and ano=? and dayTrade=?", (mercado, mes, ano, dayTrade))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

#apenas para calculo IRPF
def searchPapelDataStatus(status="", papel="", data=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE status=? and papel=? and data=? ", (status, papel, data))
    rows = trans.fetchall()
    trans.disconnect()
    return rows


def searchPapelOrderedDateStatus(papel=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE papel=? ORDER BY data DESC, Status DESC", (papel))
    rows = trans.fetchall()
    trans.disconnect()
    return rows

def searchPapeisDistintosDataDescendente(papel=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE papel=? ORDER BY data DESC", (papel))
    rows = trans.fetchall()
    trans.disconnect()
    return rows


# def searchPapeisDiferentes(listPapeistoAvoid=""):
#     trans = TransactionObject()
#     trans.connect()
#     trans.execute("SELECT * FROM STOCKS WHERE papel<>?", (listPapeistoAvoid))
#     rows = trans.fetchall()
#     trans.disconnect()
#     return rows


def selectNextLine(idAnterior):
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT * FROM STOCKS WHERE idAnterior=? > id LIMIT 1", (idAnterior))
    trans.persist()
    trans.disconnect()

def delete(id):
    trans = TransactionObject()
    trans.connect()
    trans.execute("DELETE FROM STOCKS WHERE id = ?", (id,))
    trans.persist()
    trans.disconnect()

def update(id, mercado="", papel="", status="", data="", mes="", ano="", valor="", pm="", quantidade="", qconsolidado="", custos="", consolidado="", valorAtual="", dataFechamento="", dayTrade=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("UPDATE STOCKS SET mercado =?, papel=?, status=?, data=?, mes=?, ano=?, valor=?, pm=?, quantidade=?, qconsolidado=?, custos=?, consolidado=?, valorAtual=?, dataFechamento=? , dayTrade=? WHERE id = ?",(mercado, papel, status, data, mes, ano, valor, pm, quantidade, qconsolidado, custos, consolidado, valorAtual, dataFechamento, dayTrade, id))
    trans.persist()
    trans.disconnect()

def updateConsolidado(id, consolidado=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("UPDATE STOCKS SET consolidado=? WHERE id = ?", (consolidado, id))
    trans.persist()
    trans.disconnect()

def updateDayTrade(id, dayTrade=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("UPDATE STOCKS SET dayTrade=? WHERE id = ?", (dayTrade, id))
    trans.persist()
    trans.disconnect()

def updateValorAtual(id, valorAtual="", dataFechamento=""):
    trans = TransactionObject()
    trans.connect()
    trans.execute("UPDATE STOCKS SET valorAtual=?, dataFechamento=? WHERE id = ?", (valorAtual, dataFechamento, id))
    trans.persist()
    trans.disconnect()

def searchLowestDate():
    trans = TransactionObject()
    trans.connect()
    trans.execute("SELECT min(data) FROM STOCKS ")
    rows = trans.fetchall()
    trans.disconnect()
    return rows

initDB()
