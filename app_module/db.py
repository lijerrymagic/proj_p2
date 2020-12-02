import pymysql
from app_module.models import User, Vehicle, Address, Customer

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
    conn.commit()

    cur.close()
    conn.close()


def insert_address(address_obj):
    run_query('''insert into zlrz_address (state, city, street, zipcode) values (%s, %s, %s, %s)'''
              , (address_obj.state, address_obj.city, address_obj.street, int(address_obj.zipcode)))
    rs = run_query('''select * from zlrz_address where state = %s and city = %s and street=%s and zipcode=%s'''
                   , (address_obj.state, address_obj.city, address_obj.street, int(address_obj.zipcode)))
    return rs[0][0]


def insert_customer(customer_obj):
    run_query('''insert into zlrz_customer (cust_type, firstname, lastname, cust_email, cust_phonenum, addr_id, 
    username, password) values (%s, %s, %s, %s, %s, %s, %s, %s) '''
              , (customer_obj.cust_type, customer_obj.first_name, customer_obj.last_name, customer_obj.cust_email,
                 customer_obj.cust_phonenum, customer_obj.address_id, customer_obj.username, customer_obj.password))
    rs = run_query('''select * from zlrz_customer where firstname = %s and lastname = %s order by cust_id desc'''
                   , (customer_obj.first_name, customer_obj.last_name))
    return rs[0][0]


def get_password(username):
    rs = run_query('''select password from zlrz_customer where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_user_type(username):
    rs = run_query('''select cust_type from zlrz_customer where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_vehicles():
    rs = run_query('''select * from zlrz_vehicle''')
    return rs


def get_vehicle_by_id(vehicle_id):
    rs = run_query('''select * from zlrz_vehicle where vehicle_id=%s''', (vehicle_id,))
    return rs if rs is not None else rs
