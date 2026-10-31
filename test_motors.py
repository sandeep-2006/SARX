from pymavlink import mavutil
import time

def test_motor(master, motor_number, throttle_percent, duration_sec):
    print(f"Testing Motor {motor_number} at {throttle_percent}% for {duration_sec} seconds...")
    
    # MAV_CMD_DO_MOTOR_TEST structure
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0, # Confirmation
        motor_number, # Param 1: Motor instance (1, 2, 3, 4...)
        2,            # Param 2: Throttle type (2 = Percentage)
        throttle_percent, # Param 3: Throttle value (e.g., 5 for 5%)
        duration_sec, # Param 4: Timeout in seconds
        1,            # Param 5: Motor count (test 1 motor at a time)
        0,            # Param 6: Test order (0 = default)
        0             # Param 7: Empty
    )

# Connect to Pixhawk
master = mavutil.mavlink_connection('/dev/serial0', baud=921600)
master.wait_heartbeat()
print("Connected to Flight Controller.")

# Test Motors 1 through 4 sequentially
# Warning: Ensure props are removed!
for motor in range(1, 5):
    test_motor(master, motor, throttle_percent=5, duration_sec=3)
    time.sleep(4) # Wait for the motor to stop before testing the next one

print("Motor testing complete.")