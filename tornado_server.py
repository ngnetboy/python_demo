from tornado.web import Application
from tornado.web import RequestHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import asyncpg
import asyncio
import uvloop
import psycopg2


class DB(object):
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def get_connected_db(cls, path=None):
        conn = None
        conn = psycopg2.connect(database="cm", user="postgres", password="", host="127.0.0.1", port="5432")
        if conn:
            return DB(conn)
        else:
            return None

    def get_cursor(self):
        return self.conn.cursor()

    def execute_sql(self, sql):
        assert sql
        cu = self.get_cursor()
        cu.execute(sql)
        self.conn.commit()
        cu.close()
    
    def execute_sql_ingnore_exception(self, sql):
        try:
            self.execute_sql(sql)
        except Exception as e:
            print(str(e))
            self.conn.rollback()

    def close(self):
        self.conn.close()

    def fetchall(self, sql):
        assert sql
        cu = self.get_cursor()
        cu.execute(sql)
        result = cu.fetchall()
        cu.close()
        return result

    def fetchone(self, sql):
        assert sql
        cu = self.get_cursor()
        cu.execute(sql)
        result = cu.fetchone()
        cu.close()
        return result

class ShowMsg(RequestHandler):
    async def get(self, *args, **kwargs):
        conn = await asyncpg.connect('postgresql://postgres@127.0.0.1/cm')
        rows = await conn.fetchrow('select id, monitor_id, deal_status, target_type, target_name from monitor_msg;')
        await conn.close()
        data = [{key:value} for key, value in rows.items()]
        self.write("ok")

class PoolMsg(RequestHandler):
    async def get(self, *args, **kwargs):
        pool = self.application.pool
        async with pool.acquire() as conn:
            #print(dir(conn))
            async with conn.transaction():
                rows = await conn.fetch("select id, monitor_id, deal_status, target_type, target_name from monitor_msg;")
        self.finish("ok")

class SyncMsg(RequestHandler):
    def get(self, *args, **kwargs):
        db = DB.get_connected_db()
        select_sql = "select id, monitor_id, deal_status, target_type, target_name from monitor_msg;"
        result = db.fetchall(select_sql)
        db.close()
        self.write("ok")

async def init_db_pool():
    return await asyncpg.create_pool(database='cm', host='127.0.0.1', port=5432, password='', user='postgres')

if __name__ == '__main__':

    urlpattern = (
        (r'/showmsg/?', ShowMsg),
        (r'/poolmsg/?', PoolMsg),
        (r'/syncmsg/?', SyncMsg),
    )
    app = Application(
        handlers = urlpattern,
    )

    loop = asyncio.get_event_loop()
    app.pool = loop.run_until_complete(init_db_pool())

    #using uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    app.pool = loop.run_until_complete(init_db_pool())
    
    httpserver = HTTPServer(app, xheaders=True)
    httpserver.listen(8989)
    IOLoop.current().start()
