from pymavlink import mavutil
import time

# 1. Connect to the Pixhawk
print("Connecting to Pixhawk...")
master = mavutil.mavlink_connection('/dev/serial0', baud=921600)
master.wait_heartbeat()
print("Heartbeat detected!")

# 2. Wait for 3D GPS Lock (Crucial for GUIDED mode)
print("Waiting for GPS lock...")
while True:
    msg = master.recv_match(type='GPS_RAW_INT', blocking=True)
    if msg.fix_type >= 3: # 3 = 3D fix, 4 = DGPS, 5 = RTK Float, 6 = RTK Fixed
        print(f"GPS Lock acquired! Satellites visible: {msg.satellites_visible}")
        break
    time.sleep(0.5)

# 3. Change Flight Mode to GUIDED
print("Switching to GUIDED mode...")
mode_id = master.mode_mapping()['GUIDED']
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id
)

# Wait for mode switch confirmation
while True:
    msg = master.recv_match(type='HEARTBEAT', blocking=True)
    if msg.custom_mode == mode_id:
        print("Mode successfully changed to GUIDED.")
        break

# 4. Arm the Drone
print("Arming motors...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    1, 0, 0, 0, 0, 0, 0 # Param 1: 1 means arm, 0 means disarm
)
master.motors_armed_wait()
print("Motors armed!")

# 5. Send Takeoff Command
target_altitude = 10 # meters
print(f"Sending takeoff command to {target_altitude} meters...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
    0, 0, 0, 0, 0, 0, target_altitude
)

# 6. Monitor Altitude until target is reached
print("Climbing...")
while True:
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        # relative_alt is in millimeters, convert to meters
        current_alt = msg.relative_alt / 1000.0
        print(f"Current Altitude: {current_alt:.1f}m")
        if current_alt >= (target_altitude - 0.5): # within 0.5m of target
            print("Target altitude reached!")
            break
    time.sleep(0.2)

# 7. Hover for 10 seconds
print("Hovering for 10 seconds...")
time.sleep(10)

# 8. Command Landing
print("Commanding landing...")
land_mode_id = master.mode_mapping()['LAND']
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    land_mode_id
)

print("Landing in progress. The Pixhawk will automatically disarm once it detects the ground.")
