import constants
import pymysql
import plugintemplate

class MySQL(plugintemplate.plugin):
    def __init__(self):
        self.Connect()
        
    def Connect(self):
        self.conn = pymysql.connect(host=constants.mysqlhost,port=3306,user="irc_bot",passwd="bl3rp12",db="irc_bot", use_unicode=True, charset='utf8')
        
    def __getattr__(self,attr):
        if attr == "cursor":
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
        except pymysql.err.OperationalError as err:
            if self.timesfailed > 5:
                return
            else:
                self.c.close()
                self.handler.conn.close()
                self.handler.Connect()
                self.c.open()
                self.execute(query, args)
                self.timesfailed += 1
    
    def __getattr__(self,attr):
        return getattr(self.c,attr)