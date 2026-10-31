from pymavlink import mavutil
import time

# Connect to the Pixhawk via the Pi's UART pins (GPIO 14/15)
# Note: Ensure the Pixhawk's SERIAL port baud rate matches this (usually 921600 for companion computers)
print("Connecting to Pixhawk...")
master = mavutil.mavlink_connection('/dev/serial0', baud=921600)

# Wait for the heartbeat to confirm connection
master.wait_heartbeat()
print(f"Heartbeat received from system (System ID: {master.target_system} Component ID: {master.target_component})")

# Request continuous data streams
master.mav.request_data_stream_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_EXTRA1, 5, 1 # 5 Hz
)

print("Reading Attitude Data (Press Ctrl+C to stop)...")
try:
    while True:
        # Filter the incoming MAVLink stream for ATTITUDE messages
        msg = master.recv_match(type='ATTITUDE', blocking=True)
        if msg:
            print(f"Roll: {msg.roll:.2f} | Pitch: {msg.pitch:.2f} | Yaw: {msg.yaw:.2f}")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Telemetry check stopped.")