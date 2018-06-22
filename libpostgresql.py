import psycopg2


class DB():
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def get_connected_db(cls, path=None):
        conn = None
        conn = psycopg2.connect(database='test', user='postgres', password='', host='127.0.0.1', port='5432')

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

def select_test():
    select_sql = 'select name, ip_address from device;'
    db = DB.get_connected_db()
    result = db.fetchall(select_sql)
    key = ['name', 'ip_address']
    db.close()
    data = [dict(zip(key, item)) for item in result]
    print(data)
    
def insert_test():
    insert_sql = "insert into device values('%s', '%s');" % ('10.8.11.20', '10.8.11.20')
    db = DB.get_connected_db()
    db.execute_sql(insert_sql)
    db.close()

def delete_test():
    delete_sql = "delete from device where name='%s';" % '10.8.11.20'
    db = DB.get_connected_db()
    db.execute_sql(delete_sql)
    db.close()

if __name__ == '__main__':
    insert_test()
    select_test()
    delete_test()
    select_test()


