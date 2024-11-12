import schedule
import mqtt, db
schedule_jobs = []
def device_action(device_id, data_type_id, value):
    mac = db.get_device(device_id)['mac']
    if data_type_id == "status":
        mqtt.publish(f"devices/device_{mac}/status", value)
        result=db.change_device_status(device_id, value)
        print(f"Device {mac} status changed to {value}")
        if result != True:
            print(f"Error device_action status: {result}")
    else:
        result = db.add_or_change_device_data(device_id, data_type_id, value)
        data_name_in_code = db.get_data_type(data_type_id)['name_in_code']
        mqtt.publish(f"devices/device_{mac}/{data_name_in_code}", value)
        print(f"Device {mac} {data_name_in_code} changed to {value}")
        if result != True:
            print(f"Error device_action data: {result}")
def start_script(time, days, device_id, data_type_id, value, script_id):
    time = str(time)
    for day in days.split(';'):
        job = None
        if day == "mon":
            job = schedule.every().monday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "tue":
            job = schedule.every().tuesday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "wed":
            job = schedule.every().wednesday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "thu":
            job = schedule.every().thursday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "fri":
            job = schedule.every().friday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "sat":
            job = schedule.every().saturday.at(time).do(device_action, device_id, data_type_id, value)
        elif day == "sun":
            job = schedule.every().sunday.at(time).do(device_action, device_id, data_type_id, value)
        if job != None:
            print(f"Starting script {script_id, job}")
            job.script_id = script_id
            schedule_jobs.append(job)
def start_db_scripts():
    for script in db.get_all_scripts():
        start_script(script['time'], script['days'], script['device_id'], script['data_type_id'], script['value'], script['script_id'])
def stop_script(script_id):
    print(schedule_jobs)
    jobs_to_remove = [job for job in schedule_jobs if int(job.script_id) == int(script_id)]
    for job in jobs_to_remove:
        print(f"Stopping script {script_id, job}")
        schedule.cancel_job(job)
        schedule_jobs.remove(job)