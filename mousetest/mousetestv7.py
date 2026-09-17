import time
import hid

VENDOR_ID = 0x04F3
PRODUCT_ID = 0x026E

VENDOR_ID_WIRELESS = 0x04F3
PRODUCT_ID_WIRELESS = 0x026F

target_path = None
for vid, pid in [(VENDOR_ID_WIRELESS, PRODUCT_ID_WIRELESS), (VENDOR_ID, PRODUCT_ID)]:
    for info in hid.enumerate(vid, pid):
        path_str = info['path'].decode('utf-8', errors='ignore') if isinstance(info['path'], bytes) else info['path']
        if "Col05" in path_str:
            target_path = info['path']
            break
    if target_path:
        break

if not target_path:
    print("Error: Could not find Col05 control path for wired or wireless device.")
    exit()

try:
    device = hid.device()
    device.open_path(target_path)
    device.set_nonblocking(False)
    
    print("Successfully connected to mouse control collection (Col05)!")
    print("\nPolling Rate Test Controls:")
    print("  [1] Set Polling Rate to 125 Hz  (Code: 0x08)")
    print("  [2] Set Polling Rate to 250 Hz  (Code: 0x04)")
    print("  [3] Set Polling Rate to 500 Hz  (Code: 0x02)")
    print("  [4] Set Polling Rate to 1000 Hz (Code: 0x01)")
    print("  [q] Quit")
    print("-" * 40)

    counter = 0x10

    def send_and_get_response(payload):
        res = device.send_feature_report(payload)
        print(f"Sent payload | Bytes written: {res}")
        
        try:
            response = device.get_feature_report(0x06, 32)
            if response:
                hex_response = "".join(f"{b:02x}" for b in response)
                print(f" <- Mouse Response: {hex_response}")
            else:
                print(" <- Mouse Response: None / Empty")
        except Exception as read_err:
            print(f" <- Response Read Error: {read_err}")

    while True:
        choice = input("Enter choice (1-4, q): ").strip().lower()
        counter = (counter + 1) & 0xFF
        
        # Map choice to polling rate hex code
        rate_mapping = {
            '1': 0x08,  # 125 Hz
            '2': 0x04,  # 250 Hz
            '3': 0x02,  # 500 Hz
            '4': 0x01   # 1000 Hz
        }

        if choice in rate_mapping:
            code = rate_mapping[choice]
            # Constructing a 32-byte feature report payload for polling rate
            # Adjusting byte indexes to match your control block format
            payload = [
                0x06, 0x04, counter, 0x00, 0x00, 
                code, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00
            ]
            print(f"Sending Polling Rate code {code:#04x} with counter {counter:#04x}...")
            send_and_get_response(payload)
            
        elif choice == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Use 1, 2, 3, 4, or q.")

    device.close()

except Exception as e:
    print(f"Error: {e}")