import pymysql
from app_module.models import User, Vehicle, Address, Customer, Location, Coupon, VehicleClass

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


def insert_vehicle(vehicle_obj):
    run_query('''insert into zlrz_vehicle (veh_make, veh_model, veh_year, veh_vin, veh_license, vc_num, ol_id) values (%s, %s, %s, %s, %s, %s, %s)'''
              , (vehicle_obj.make, vehicle_obj.model, int(vehicle_obj.year), vehicle_obj.vin_num, vehicle_obj.license_num, vehicle_obj.class_num, vehicle_obj.location_id))
    rs = run_query('''select * from zlrz_vehicle where veh_make = %s and veh_model = %s and veh_year = %s and veh_vin = %s and veh_license = %s and vc_num = %s and ol_id = %s'''
                   , (vehicle_obj.make, vehicle_obj.model, int(vehicle_obj.year), vehicle_obj.vin_num, vehicle_obj.license_num, vehicle_obj.class_num, vehicle_obj.location_id))
    return rs[0][0]


def insert_vehicle_class(class_obj):
    run_query('''insert into zlrz_vehicle_class (vc_name, vc_rateperday, vc_feeovermile) values (%s, %s, %s)'''
              , (class_obj.vc_name, int(class_obj.vc_rateperday), int(class_obj.vc_feeovermile)))
    rs = run_query('''select * from zlrz_vehicle_class where vc_name = %s and vc_rateperday = %s and vc_feeovermile = %s'''
                   , (class_obj.vc_name, int(class_obj.vc_rateperday), int(class_obj.vc_feeovermile)))
    return rs[0][0]


def insert_office_location(location_obj):
    run_query('''insert into zlrz_office_location (ol_phonenum, ol_state, ol_city, ol_street, ol_zipcode) values (%s, %s, %s, %s, %s)'''
              , (location_obj.phone, location_obj.state, location_obj.city, location_obj.street, int(location_obj.zipcode)))
    rs = run_query('''select * from zlrz_office_location where ol_phonenum = %s and ol_state = %s and ol_city = %s and ol_street=%s and ol_zipcode=%s'''
                   , (location_obj.phone, location_obj.state, location_obj.city, location_obj.street, int(location_obj.zipcode)))
    return rs[0][0]


def get_password(username):
    rs = run_query('''select password from zlrz_customer where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_user_type(username):
    rs = run_query('''select cust_type from zlrz_customer where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_user_id(username):
    rs = run_query('''select cust_id from zlrz_customer where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_coupon(cust_id):
    rs = run_query('''select zlrz_coupons.* from zlrz_cust_coupon join zlrz_coupons 
    on zlrz_cust_coupon.cou_id = zlrz_coupons.cou_id where zlrz_cust_coupon.cust_id = %s'''
                   , (cust_id,))
    return list(map(lambda t: Coupon(t[1], t[2], t[3], t[0]), rs))[0] if rs is not None else rs


def get_vehicles():
    """
    Get full location
    :return:
    """
    rs = run_query('''select * from zlrz_vehicle''')
    return [] if rs is None else rs


def get_all_locations():
    """
    Get all location objects
    :return:
    """
    rs = run_query('''select * from zlrz_office_location''')
    return [] if rs is None else list(map(lambda t: Location(t[1], t[2], t[3], t[4], t[5], t[0]), rs))

def get_all_vehclasses():
    """
    Get all vehicleclass objects
    :return:
    """
    rs = run_query('''select * from zlrz_vehicle_class''')
    return [] if rs is None else list(map(lambda t: VehicleClass(t[1], t[2], t[3], t[0]), rs))


def get_vehicle_by_id(vehicle_id):
    rs = run_query('''select * from zlrz_vehicle where veh_id=%s''', (int(vehicle_id),))
    return list(map(lambda t: Vehicle(t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[0]), rs))[0] \
        if rs is not None else None


def get_vehicle_class(vehicle_id):
    rs = run_query('''select zlrz_vehicle_class.* from zlrz_vehicle join zlrz_vehicle_class 
    on zlrz_vehicle.vc_num = zlrz_vehicle_class.vc_num where zlrz_vehicle.veh_id=%s''', (int(vehicle_id),))
    return list(map(lambda t: VehicleClass(t[1], t[2], t[3], t[0]), rs))[0] if rs is not None else None
