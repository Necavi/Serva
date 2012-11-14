import constants
import pymysql
import sys

class MySQL:
    def __init__(self):
        self.Connect()
        
    def Connect(self):
        self.conn = pymysql.connect(host=constants.mysqlhost,port=3306,user="irc_bot",passwd="bl3rp12",db="irc_bot", use_unicode=True, charset='utf8')
        
    def __getattr__(self,attr):
        if(attr == "cursor"):
            return Cursor(self)
        else:
            return getattr(self.conn,attr)
            
class Cursor:
    def __init__(self,handler):
        self.c = handler.conn.cursor
        self.handler = handler
        self.timesfailed = 0
        
    def execute(self, query, args=None):
        try:
            x = self.c.execute(query,args)
            self.timesfailed = 0
            return x
        except OperationalError:
            if(self.timesfailed > 5):
                raise OperationalError(sys.exc_info())
			self.c.close()
			self.handler.conn.close()
            self.handler.Connect()
			self.c.open()
            self.execute(query,args)
            timesfailed += 1
    
    def __getattr__(self,attr):
        return getattr(self.c,attr)
    
class main:
    def __init__(self,main):
        self.main = main
        self.main.conn = MySQL()