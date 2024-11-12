import hashlib
from functools import wraps
from flask import Flask, request, jsonify
import mqtt, db, jwt, scripts
from secret import JWT_SECRET
app = Flask(__name__)
@app.route("/")
def index():
    return "HELLO"
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "OK"}), 200
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # print(data)
            current_user = db.get_user_by_id(data['user_id'])
        except Exception as e:
            print(f"Ошибка token reguired: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
@app.route("/api/users/check_token", methods=["GET"])
@token_required
def check_token(current_user):
    return jsonify({"message": "Token is valid"}), 200
# users
@app.route("/api/users/register", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("username")
    email = data.get("email")
    password = data.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    result = db.register_user(name, email, hashed_password)
    if result == True:
        return jsonify({"message": "User created"}), 201
    else:
        return jsonify({"message": result}), 500
@app.route("/api/users/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    result = db.login_user(email, hashed_password)
    if result != False:
        token = db.generate_token(result)
        return jsonify({'token': token})
    elif result == False:
        return jsonify({"message": "Неверный логин или пароль"}), 400
    else:
        return jsonify({"message": result}), 500
@app.route("/api/users/change_pass", methods=["POST"])
@token_required
def change_password(current_user):
    user_id = current_user['user_id']
    data = request.get_json()
    old_password = data.get("old_password")
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    new_password = data.get("new_password")
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    result = db.change_password(user_id, hashed_old_password, hashed_new_password)
    if result == True:
        return jsonify({"message": "Password changed"}), 200
    elif result == False:
        return jsonify({"message": "Invalid credentials"}), 400
    else:
        return jsonify({"message": result}), 500
@app.route("/api/users/get_user", methods=["GET"])
@token_required
def get_user(current_user):
    # print(current_user)
    return jsonify(current_user), 200
# homes
@app.route("/api/homes/create", methods=["POST"])
@token_required
def create_home(current_user):
    user_id = current_user['user_id']
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    # print(user_id,name, address)
    result = db.create_home(name, user_id, address)
    if result == True:
        return jsonify({"message": "Home created"}), 201
    else:
        return jsonify({"message": result}), 500
@app.route("/api/homes/get_homes", methods=["GET"])
@token_required
def get_homes(current_user):
    user_id = current_user['user_id']
    result = db.get_homes(user_id)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No homes found"}), 404
    else:
        return jsonify({"message": "No homes found"}), 500
@app.route("/api/homes/get_homes_with_rooms", methods=["GET"])
@token_required
def get_homes_with_rooms(current_user):
    user_id = current_user['user_id']
    result = db.get_homes_with_rooms(user_id)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No homes found"}), 404
    else:
        return jsonify({"message": "No homes found"}), 500
@app.route("/api/homes/get_home", methods=["GET"])
@token_required
def get_home(current_user):
    home_id = request.args.get("home_id")
    result = db.get_home(home_id)
    # print(type(result))
    if type(result) == dict and result != []:
        return jsonify({"home": result}), 200
    elif result == []:
        return jsonify({"message": "No home found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/homes/change_home", methods=["POST"])
@token_required
def change_home(current_user):
    data = request.get_json()
    home_id = data.get("home_id")
    name = data.get("name")
    address = data.get("address")
    result = db.change_home(home_id, name, address)
    if result == True:
        return jsonify({"message": "Home changed"}), 200
    elif result == False:
        return jsonify({"message": "Home not found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/homes/delete", methods=["DELETE"])
@token_required
def delete_home(current_user):
    home_id = request.args.get("home_id")
    result = db.delete_home(home_id)
    if result == True:
        return jsonify({"message": "Home deleted"}), 200
    else:
        return jsonify({"message": result}), 500
@app.route("/api/rooms/create", methods=["POST"])
@token_required
def create_room(current_user):
    data = request.get_json()
    name = data.get("name")
    home_id = data.get("home_id")
    result = db.create_room(name, home_id)
    if result == True:
        return jsonify({"message": "Room created"}), 201
    else:
        return jsonify({"message": result}), 500
@app.route("/api/rooms/get_rooms", methods=["GET"])
@token_required
def get_rooms(current_user):
    home_id = request.args.get("home_id")
    result = db.get_rooms_in_home(home_id)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No rooms found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/rooms/change_name", methods=["POST"])
@token_required
def change_room_name(current_user):
    data = request.get_json()
    room_id = data.get("room_id")
    name = data.get("name")
    result = db.change_room_name(room_id, name)
    if result == True:
        return jsonify({"message": "Room name changed"}), 200
    elif result == False:
        return jsonify({"message": "Room not found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/rooms/delete", methods=["DELETE"])
@token_required
def delete_room(current_user):
    room_id = request.args.get("room_id")
    result = db.delete_room(room_id)
    if result == True:
        return jsonify({"message": "Room deleted"}), 200
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/create", methods=["POST"])
@token_required
def create_device(current_user):
    data = request.get_json()
    name = data.get("name")
    room_id = data.get("room_id")
    type = data.get("type")
    status = data.get("status")
    mac = data.get("mac")
    result1 = db.delete_waiting_device(mac)
    result2 = db.create_device(name, room_id, type, status, mac)
    if result1 == True and result2 == True:
        mqtt.publish(f"devices/device_{mac}/first_connection_result", "added")
        db.create_device_log(db.get_device_by_mac(mac)[0]['device_id'], "Device created")
        return jsonify({"message": "Device created"}), 201
    else:
        return jsonify({"message": f"{result1},{result2}"}), 500
@app.route("/api/devices/get_devices", methods=["GET"])
@token_required
def get_devices(current_user):
    result = db.get_devices(current_user['user_id'])
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No devices found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/change_device_room", methods=["GET"])
@token_required
def add_device_in_room(current_user):
    device_id = request.args.get("device_id")
    room_id = request.args.get("room_id")

    old_room_id = db.get_device(device_id)['room_id']
    old_room = db.get_room(old_room_id)['name']
    new_room = db.get_room(room_id)['name']

    result = db.change_device_room(device_id, room_id)
    if result == True:
        db.create_device_log(device_id, f"Device moved from {old_room} to {new_room}")
        return jsonify({"message": "Device added in room"}), 200
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/get_device_by_mac", methods=["GET"])
@token_required
def get_devices_by_mac(current_user):
    mac = request.args.get("mac")
    result = db.get_device_by_mac(mac)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No devices found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/change_name", methods=["POST"])
@token_required
def change_device_name(current_user):
    data = request.get_json()
    device_id = data.get("device_id")
    name = data.get("name")
    result = db.change_device_name(device_id, name)
    if result == True:
        return jsonify({"message": "Device name changed"}), 200
    elif result == False:
        return jsonify({"message": "Device not found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/change_status", methods=["POST"])
@token_required
def change_device_status(current_user):
    data = request.get_json()
    device_id = data.get("device_id")
    status = data.get("status")
    result = db.change_device_status(device_id, status)
    if result == True:
        mqtt.publish(f"devices/device_{db.get_device(device_id)['mac']}/status", status)
        db.create_device_log(device_id, f"Device status changed to {status}")
        return jsonify({"message": "Device status changed"}), 200
    elif result == False:
        return jsonify({"message": "Device not found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/delete", methods=["DELETE"])
@token_required
def delete_device(current_user):
    device_id = request.args.get("device_id")
    mac = db.get_device(device_id)['mac']
    result1 = db.delete_device(device_id)
    result2 = db.delete_device_data(device_id)
    result3 = db.delete_scripts_by_device(device_id)
    if type(result3) == list and result3 != []:
        for script in result3:
            scripts.stop_script(script[0])
    if (result1 == True and result2 == True and result3 == []):
        mqtt.publish(f"devices/device_{mac}/hard_reset", "true")
        return jsonify({"message": "Device deleted"}), 200
    else:
        return jsonify({"message": f"{result1, result2}"}), 500
@app.route("/api/devices/get_device_by_user", methods=["GET"])
@token_required
def get_device_by_user(current_user):
    user_id = current_user['user_id']
    result = db.get_devices_by_user(user_id)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No devices found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/get_detailed_device", methods=["GET"])
@token_required
def get_detailed_device(current_user):
    device_id = request.args.get("device_id")
    result = db.get_device(device_id)
    if type(result) == dict and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No devices found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/change_data", methods=["POST"])
@token_required
def change_device_data(current_user):
    data = request.get_json()
    device_id = data.get("device_id")
    data_type_id = data.get("data_type_id")
    data_value = data.get("data_value")
    result = db.add_or_change_device_data(device_id, data_type_id, data_value)
    mac = db.get_device(device_id)['mac']
    data_name_in_code = db.get_data_type(data_type_id)['name_in_code']
    if result == True:
        mqtt.publish(f"devices/device_{mac}/{data_name_in_code}", data_value)
        return jsonify({"message": "Device data changed"}), 200
    elif result == False:
        return jsonify({"message": "Device not found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/devices/get_data", methods=["GET"])
@token_required
def get_device_data(current_user):
    device_id = request.args.get("device_id")
    result = db.get_device_data(device_id)
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No data found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/waiting_devices/check", methods=["GET"])
@token_required
def check_waiting_devices(current_user):
    mac = request.args.get("mac")
    result = db.search_waiting_device(mac)

    if type(result) == dict and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No waiting devices found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/scripts/create", methods=["POST"])
@token_required
def create_script(current_user):
    data = request.get_json()
    name = data.get("name")
    time = data.get("time")
    days = data.get("days")
    device_id = data.get("device_id")
    data_type_id = data.get("data_type_id")
    value = data.get("value")
    script_id = db.create_script(name, time, days, device_id, data_type_id, value)
    if script_id != None:
        scripts.start_script(time, days, device_id, data_type_id, value, script_id)
        return jsonify({"message": "Script created"}), 201
    else:
        return jsonify({"message": "Error"}), 500
@app.route("/api/scripts/get_scripts", methods=["GET"])
@token_required
def get_scripts(current_user):
    result = db.get_all_scripts_by_user(current_user['user_id'])
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No scripts found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/scripts/get_scripts_with_devices", methods=["GET"])
@token_required
def get_scripts_with_devices(current_user):
    result = db.get_all_scripts_by_user_with_devices(current_user['user_id'])
    if type(result) == list and result != []:
        return jsonify(result), 200
    elif result == []:
        return jsonify({"message": "No scripts found"}), 404
    else:
        return jsonify({"message": result}), 500
@app.route("/api/scripts/delete", methods=["DELETE"])
@token_required
def delete_script(current_user):
    script_id = request.args.get("script_id")
    result = db.delete_script(script_id)
    if result == True:
        scripts.stop_script(script_id)
        return jsonify({"message": "Script deleted"}), 200
    else:
        return jsonify({"message": result}), 500