import pymysql

HOSTNAME = 'localhost'
USERNAME = 'root'
PASSWORD = '123456'
DATABASE = 'proj_p2'


def get_connection():
    my_sql_connection = pymysql.connect(host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE)
    return my_sql_connection


def run_query(query, args=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, args)

    rs = cur.fetchall()
    if (len(rs) != 0):
        return rs

    cur.close()
    conn.close()
