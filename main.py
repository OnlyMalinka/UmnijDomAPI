import db, mqtt, scripts
from API import app
import threading, time

def ping():
    while True:
        for mac in db.get_all_macs():
            mqtt.publish(f"devices/device_{mac}/ping", "ping")
            db.change_device_connection(mac, "offline")
        #print("Ping")
        time.sleep(5)

def schedule_scripts():
    scripts.start_db_scripts()
    while True:
        scripts.schedule.run_pending()
        time.sleep(1)



# Create a thread that will run the ping function
ping_thread = threading.Thread(target=ping)
scripts_thread = threading.Thread(target=schedule_scripts)




# Start the thread
ping_thread.start()
scripts_thread.start()
mqtt.start_mqtt()
app.run(debug=False, port=5000, host='0.0.0.0')

