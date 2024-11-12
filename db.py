import psycopg2, jwt
from datetime import datetime, timedelta
import secret

def get_connection():
    return psycopg2.connect(
        database=secret.database,
        host=secret.host,
        user=secret.user,
        password=secret.passwordDB,
        port="5434"
    )


def generate_token(user_id):
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=secret.ExpireTime)
        }
        token = jwt.encode(payload, secret.JWT_SECRET, algorithm='HS256')
        return token
    except Exception as e:
        return str(e)





# user
def register_user(username, email, password):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cur.fetchone() is not None:
                    return "Пользователь с такой почтой уже существует"
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cur.fetchone() is not None:
                    return "Пользователь с таким именем пользователя уже существует"

        cur.execute("INSERT INTO users (username, email, password, created_at) VALUES (%s, %s, %s, %s)", (username, email, password, datetime.now()))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        return "Пользователь с такой почтой/именем пользователя уже существует"
    except Exception as e:
        return str(e)


def login_user(email, password):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE email = %s AND password = %s", (email, password))
                user_id = cur.fetchone()
                if user_id:
                    return user_id[0]
                else: return False
    except Exception as e:
        print(f"Error login_user: {e}")

def get_user_by_id(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                user = {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "created_at": row[4]
                }
                return user
    except Exception as e:
        print(f"Error get_user_by_id: {e}")

def change_password(user_id, old_password, new_password):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (user_id, old_password))
                if cur.fetchone():
                    cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, user_id))
                    conn.commit()
                    return True
                else: return False
    except Exception as e:
        return str(e)

# home

def create_home(name, user_id, address):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO homes (name, user_id, address, created_at) VALUES (%s, %s, %s, %s)", (name, user_id, address, datetime.now()))
                conn.commit()
                return True
    except psycopg2.errors.UniqueViolation:
        return "Пользователь с такой почтой/именем пользователя уже существует"
    except Exception as e:
        return str(e)


def get_homes(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM homes WHERE user_id = %s", (user_id,))
                rows = cur.fetchall()
                homes = []
                for row in rows:
                    home = {
                        "home_id": row[0],
                        "user_id": row[1],
                        "address": row[2],
                        "created_at": row[3],
                        "name": row[4]
                    }
                    homes.append(home)
                return homes
    except Exception as e:
        print(f"Error get_homes: {e}")

def get_homes_with_rooms(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM homes WHERE user_id = %s", (user_id,))
                rows = cur.fetchall()
                homes = []
                for row in rows:
                    cur.execute("SELECT * FROM rooms WHERE home_id = %s", (row[0],))
                    rooms = []
                    for room in cur.fetchall():
                        rooms.append({
                            "room_id": room[0],
                            "home_id": room[1],
                            "name": room[2],
                            "created_at": room[3]
                        })
                    home = {
                        "home_id": row[0],
                        "user_id": row[1],
                        "address": row[2],
                        "created_at": row[3],
                        "name": row[4],
                        "rooms": rooms
                    }
                    homes.append(home)
                return homes
    except Exception as e:
        print(f"Error get_homes_with_rooms: {e}")

def get_home(home_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM rooms WHERE home_id = %s", (home_id,))
                rows = cur.fetchall()
                rooms = []
                for row in rows:
                    cur.execute("SELECT * FROM devices WHERE room_id = %s", (row[0],))
                    devices = []
                    for device in cur.fetchall():
                        devices.append({
                            "device_id": device[0],
                            "room_id": device[1],
                            "name": device[2],
                            "type": device[3],
                            "status": device[4],
                            "mac": device[5],
                            "created_at": device[6],
                            "connection": device[7]
                        })
                    rooms.append({
                        "room_id": row[0],
                        "home_id": row[1],
                        "name": row[2],
                        "created_at": row[3],
                        "devices": devices
                    })
                cur.execute("SELECT * FROM homes WHERE home_id = %s", (home_id,))
                row = cur.fetchone()
                home = {
                    "home_id": row[0],
                    "user_id": row[1],
                    "address": row[2],
                    "created_at": row[3],
                    "name": row[4],
                    "rooms": rooms
                }
                return home
    except Exception as e:
        print(f"Error get_home: {e}")

def change_home_name(home_id, new_name):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE homes SET name = %s WHERE home_id = %s", (new_name, home_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def change_home_address(home_id, new_address):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE homes SET address = %s WHERE home_id = %s", (new_address, home_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def change_home(home_id, new_name, new_address):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE homes SET name = %s, address = %s WHERE home_id = %s", (new_name, new_address, home_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)
def delete_home(home_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM rooms WHERE home_id = %s", (home_id,))
                rows = cur.fetchall()
                if rows == []:
                    cur.execute("DELETE FROM homes WHERE home_id = %s", (home_id,))
                    conn.commit()
                    return True
                else: return "В доме есть комнаты"
    except Exception as e:
        return str(e)

# room
def create_room(name, home_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO rooms (name, home_id, created_at) VALUES (%s, %s, %s)", (name, home_id, datetime.now()))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def get_rooms_in_home(home_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM rooms WHERE home_id = %s", (home_id,))
                rows = cur.fetchall()
                rooms = []
                for row in rows:
                    room = {
                        "room_id": row[0],
                        "home_id": row[1],
                        "name": row[2],
                        "created_at": row[3]
                    }
                    rooms.append(room)
                return rooms
    except Exception as e:
        print(f"Error get_rooms_in_home: {e}")

def get_room(room_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
                row = cur.fetchone()
                room = {
                    "room_id": row[0],
                    "home_id": row[1],
                    "name": row[2],
                    "created_at": row[3]
                }
                return room
    except Exception as e:
        print(f"Error get_room: {e}")

def change_room_name(room_id, new_name):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE rooms SET name = %s WHERE room_id = %s", (new_name, room_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def delete_room(room_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE room_id = %s", (room_id,))
                rows = cur.fetchall()
                if rows == []:
                    cur.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
                    conn.commit()
                    return True
                else: return "В комнате есть устройства"
    except Exception as e:
        return str(e)
# device
def create_device(name, room_id, type, status, mac):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE mac = %s", (mac,))
                if cur.fetchone():
                    return False
                cur.execute("INSERT INTO devices (name,room_id, type, status, mac, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (name, room_id, type, status, mac, datetime.now()))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def change_device_room(device_id, room_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE devices SET room_id = %s WHERE device_id = %s", (room_id, device_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)


def get_device(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE device_id = %s", (device_id,))
                row = cur.fetchone()
                cur.execute("SELECT * FROM device_data WHERE device_id = %s", (device_id,))
                data = []
                for device_data in cur.fetchall():
                    cur.execute("SELECT * FROM data_types WHERE type_id = %s", (device_data[2],))
                    data_type = cur.fetchone()
                    data.append({
                        "type_id": device_data[2],
                        "data_value": device_data[1],
                        "data_name": data_type[1],
                        "data_unit": data_type[2],
                        "data_min": data_type[3],
                        "data_max": data_type[4],
                        "data_drawer": data_type[5],
                        "name_in_code": data_type[6]
                    })
                device = {
                    "device_id": row[0],
                    "room_id": row[1],
                    "name": row[2],
                    "type": row[3],
                    "status": row[4],
                    "mac": row[5],
                    "created_at": row[6],
                    "connection": row[7],
                    "data": data
                }
                return device
    except Exception as e:
        print(f"Error get_device: {e}")

def get_devices(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices JOIN rooms ON devices.room_id = rooms.room_id JOIN homes ON rooms.home_id = homes.home_id WHERE homes.user_id = %s", (user_id,))
                rows = cur.fetchall()
                devices = []
                for row in rows:
                    cur.execute("SELECT * FROM device_data JOIN data_types ON device_data.data_type_id = data_types.type_id WHERE device_data.device_id = %s", (row[0],))
                    data = []
                    for device_data in cur.fetchall():
                        data.append({
                            "type_id": device_data[2],
                            "data_value": device_data[1],
                            "data_name": device_data[4],
                            "data_unit": device_data[5],
                            "data_min": device_data[6],
                            "data_max": device_data[7],
                            "data_drawer": device_data[8],
                            "name_in_code": device_data[9]
                        })
                    device = {
                        "device_id": row[0],
                        "room_id": row[1],
                        "name": row[2],
                        "type": row[3],
                        "status": row[4],
                        "mac": row[5],
                        "created_at": row[6],
                        "connection": row[7],
                        "data": data
                    }
                    devices.append(device)
                return devices
    except Exception as e:
        print(f"Error get_devices: {e}")

def get_devices_by_room(room_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE room_id = %s", (room_id,))
                rows = cur.fetchall()
                devices = []
                for row in rows:
                    device = {
                        "device_id": row[0],
                        "room_id": row[1],
                        "name": row[2],
                        "type": row[3],
                        "status": row[4],
                        "mac": row[5],
                        "created_at": row[6],
                        "connection": row[7]
                    }
                    devices.append(device)
                return devices
    except Exception as e:
        print(f"Error get_devices_by_room: {e}")

def get_device_by_mac(mac):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE mac = %s", (mac,))
                rows = cur.fetchall()
                devices = []
                for row in rows:
                    device = {
                        "device_id": row[0],
                        "room_id": row[1],
                        "name": row[2],
                        "type": row[3],
                        "status": row[4],
                        "mac": row[5],
                        "created_at": row[6],
                        "connection": row[7]
                    }
                    devices.append(device)
                return devices
    except Exception as e:
        print(f"Error get_device_by_mac: {e}")

def get_devices_by_user(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices JOIN rooms ON devices.room_id = rooms.room_id JOIN homes ON rooms.home_id = homes.home_id WHERE homes.user_id = %s", (user_id,))
                rows = cur.fetchall()
                devices = []
                for row in rows:
                    device = {
                        "device_id": row[0],
                        "room_id": row[1],
                        "name": row[2],
                        "type": row[3],
                        "status": row[4],
                        "mac": row[5],
                        "created_at": row[6],
                        "connection": row[7]
                    }
                    devices.append(device)
                return devices
    except Exception as e:
        print(f"Error get_device_by_user: {e}")

def change_device_name(device_id, new_name):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE devices SET name = %s WHERE device_id = %s", (new_name, device_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)


def change_device_status(device_id, new_status):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE devices SET status = %s WHERE device_id = %s", (new_status, device_id))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def change_device_status_by_mac(mac, new_status):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE devices SET status = %s WHERE mac = %s", (new_status, mac))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def get_all_macs():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT mac FROM devices")
                rows = cur.fetchall()
                macs = []
                for row in rows:
                    macs.append(row[0])
                return macs
    except Exception as e:
        print(f"Error get_all_macs: {e}")

def change_device_connection(mac, connection):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE devices SET connection = %s WHERE mac = %s", (connection, mac))
                if cur.rowcount == 0:
                    return False
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def delete_device(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM device_logs WHERE device_id = %s", (device_id,))
                cur.execute("DELETE FROM device_data WHERE device_id = %s", (device_id,))
                cur.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def delete_device_by_mac(mac):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM devices WHERE mac = %s", (mac,))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

# device log
def create_device_log(device_id, action):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO device_logs (device_id, action, created_at) VALUES (%s, %s, %s)", (device_id, action, datetime.now()))
                conn.commit()
                return True
    except Exception as e:
        print(f"Error create_device_log: {e}")

def get_device_logs(device_id, amount):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM device_logs WHERE device_id = %s LIMIT %s", (device_id, amount))
                rows = cur.fetchall()
                logs = []
                for row in rows:
                    log = {
                        "log_id": row[0],
                        "device_id": row[1],
                        "action": row[2],
                        "created_at": row[3]
                    }
                    logs.append(log)
                return logs
    except Exception as e:
        print(f"Error get_device_logs: {e}")

# device data
def add_or_change_device_data(device_id, data_id, data_value):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM device_data WHERE device_id = %s AND data_type_id = %s", (device_id, data_id))
                if cur.fetchone():
                    cur.execute("UPDATE device_data SET data_value = %s WHERE device_id = %s AND data_type_id = %s", (data_value, device_id, data_id))
                else:
                    cur.execute("INSERT INTO device_data (device_id, data_type_id, data_value) VALUES (%s, %s, %s)", (device_id, data_id, data_value))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def get_device_data(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM device_data WHERE device_id = %s", (device_id,))
                rows = cur.fetchall()
                data = []
                for row in rows:
                    cur.execute("SELECT * FROM data_types WHERE type_id = %s", (row[2],))
                    data_type = cur.fetchone()
                    data1 = {
                        "type_id": row[2],
                        "data_value": row[1],
                        "data_name": data_type[1],
                        "data_unit": data_type[2],
                        "data_min": data_type[3],
                        "data_max": data_type[4],
                        "data_drawer": data_type[5],
                        "name_in_code": data_type[6]
                    }
                    data.append(data1)
                return data
    except Exception as e:
        print(f"Error get_device_data: {e}")

def get_data_type_by_name(name_in_code):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM data_types WHERE name_in_code = %s", (name_in_code,))
                row = cur.fetchone()
                data = {
                    "type_id": row[0],
                    "data_name": row[1],
                    "data_unit": row[2],
                    "data_min": row[3],
                    "data_max": row[4],
                    "data_drawer": row[5],
                    "name_in_code": row[6]
                }
                return data
    except Exception as e:
        print(f"Error get_device_data_by_type: {e}")

def delete_device_data(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM device_data WHERE device_id = %s", (device_id,))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def get_sensor_data(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM device_data JOIN data_types ON device_data.data_type_id = data_types.type_id WHERE device_data.device_id = %s AND data_types.data_drawer =%s", (device_id, "Sensor"))
                rows = cur.fetchall()
                data = []
                for row in rows:
                    data1 = {
                        "type_id": row[2],
                        "data_value": row[1],
                        "data_name": row[4],
                        "data_unit": row[5],
                        "data_min": row[6],
                        "data_max": row[7],
                        "data_drawer": row[8],
                        "name_in_code": row[9]
                    }
                    data.append(data1)
                return data
    except Exception as e:
        print(f"Error get_sensor_data: {e}")

def get_data_type(data_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM data_types WHERE type_id = %s", (data_id,))
                row = cur.fetchone()
                data = {
                    "type_id": row[0],
                    "data_name": row[1],
                    "data_unit": row[2],
                    "data_min": row[3],
                    "data_max": row[4],
                    "data_drawer": row[5],
                    "name_in_code": row[6]
                }
                return data
    except Exception as e:
        print(f"Error get_data_type: {e}")
def add_waiting_device(mac, type):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM devices WHERE mac = %s", (mac,))
                if cur.fetchone():
                    delete_device_by_mac(mac)

                cur.execute("SELECT * FROM waiting_devices WHERE mac = %s", (mac,))
                if cur.fetchone():
                    return "Устройство уже ожидает подключения"

                cur.execute("INSERT INTO waiting_devices (mac, type, created_at) VALUES (%s, %s, %s)", (mac, type, datetime.now()))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def search_waiting_device(mac):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM waiting_devices WHERE mac = %s", (mac,))
                row = cur.fetchone()
                if row:
                    return {
                        "waiting_device_id": row[0],
                        "mac": row[1],
                        "type": row[2],
                        "created_at": row[3]
                    }
                else: return False
    except Exception as e:
        return str(e)

def delete_waiting_device(mac):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM waiting_devices WHERE mac = %s", (mac,))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

#scripts
def get_all_scripts():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM scripts")
                rows = cur.fetchall()
                scripts = []
                for row in rows:
                    script = {
                        "script_id": row[0],
                        "name": row[1],
                        "time": row[2],
                        "days": row[3],
                        "device_id": row[4],
                        "data_type_id": row[5],
                        "value": row[6]
                    }
                    scripts.append(script)
                return scripts
    except Exception as e:
        print(f"Error get_all_scripts: {e}")

def get_all_scripts_by_user(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM scripts JOIN devices ON scripts.device_id = devices.device_id JOIN rooms ON devices.room_id = rooms.room_id JOIN homes ON rooms.home_id = homes.home_id WHERE homes.user_id = %s", (user_id,))
                rows = cur.fetchall()

                scripts = []
                for row in rows:
                    script = {
                        "script_id": row[0],
                        "name": row[1],
                        "time": str(row[2]),
                        "days": row[3],
                        "device_id": row[4],
                        "data_type_id": row[5],
                        "value": row[6]
                    }
                    scripts.append(script)
                print(scripts)
                return scripts
    except Exception as e:
        print(f"Error get_all_scripts_by_user: {e}")

def get_all_scripts_by_user_with_devices(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM scripts JOIN devices ON scripts.device_id = devices.device_id JOIN rooms ON devices.room_id = rooms.room_id JOIN homes ON rooms.home_id = homes.home_id WHERE homes.user_id = %s", (user_id,))
                rows = cur.fetchall()
                scripts = []
                for row in rows:
                    if row[5] != "status":
                        cur.execute("SELECT * FROM data_types WHERE type_id = %s", (row[5],))
                        data_type_name = cur.fetchone()[1]
                    else: data_type_name = "Статус"
                    script = {
                        "script_id": row[0],
                        "name": row[1],
                        "time": str(row[2]),
                        "days": row[3],
                        "data_type_id": row[5],
                        "data_type_name": data_type_name,
                        "value": row[6],
                        "device": {
                            "device_id": row[7],
                            "room_id": row[8],
                            "name": row[9],
                            "type": row[10],
                            "status": row[11],
                            "mac": row[12],
                            "created_at": row[13],
                            "connection": row[14]
                        }
                    }
                    scripts.append(script)
                return scripts
    except Exception as e:
        print(f"Error get_all_scripts_by_user_with_devices: {e}")

def create_script(name, time, days, device_id, data_type_id, value):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO scripts (name, time, days, device_id, data_type_id, value) VALUES (%s, %s, %s, %s, %s, %s) RETURNING script_id", (name, time, days, device_id, data_type_id, value))
                script_id = cur.fetchone()[0]
                conn.commit()
                return script_id
    except Exception as e:
        print(f"Error create_script: {e}")

def delete_script(script_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM scripts WHERE script_id = %s", (script_id,))
                conn.commit()
                return True
    except Exception as e:
        return str(e)

def delete_scripts_by_device(device_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT script_id FROM scripts WHERE device_id = %s", (device_id,))
                scripts = cur.fetchall()
                cur.execute("DELETE FROM scripts WHERE device_id = %s", (device_id,))
                conn.commit()
                return scripts
    except Exception as e:
        return str(e)