import time
import random
import hid

VENDOR_ID = 0x04F3
PRODUCT_ID = 0x026E

VENDOR_ID_WIRELESS = 0x04F3
PRODUCT_ID_WIRELESS = 0x026F

# Captured White Preset payload (DPI 1 / 800 -> Byte 4 is 0x0a)
white_payload_dpi1 = [
    0x06, 0x03, 0x11, 0x01, 0x0a, 0xff, 0xff, 0xff, 
    0xff, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0xff, 
    0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0x00, 0xff, 
    0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00
]

# Captured Purple Custom payload (DPI 1 / 800 -> Byte 4 is 0xd0)
purple_payload_dpi1 = [
    0x06, 0x03, 0x14, 0x01, 0xd0, 0x40, 0x00, 0x80, 
    0xff, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0xff, 
    0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0x00, 0xff, 
    0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00
]

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
    # Set non-blocking or blocking mode if needed (default is blocking)
    device.set_nonblocking(False)
    
    print("Successfully connected to mouse lighting collection (Col05)!")
    print("\nControls:")
    print("  --- DPI 1 (800 DPI) ---")
    print("  [1] White (DPI 800)")
    print("  [2] Purple (DPI 800)")
    print("  [3] Random Color (DPI 800)")
    print("  --- DPI 2 (1600 DPI) ---")
    print("  [11] White (DPI 1600)")
    print("  [12] Purple (DPI 1600)")
    print("  [13] Random Color (DPI 1600)")
    print("  [q] Quit")
    print("-" * 30)

    counter = 0x10

    def send_and_get_response(payload):
        # 1. Send the feature report
        res = device.send_feature_report(payload)
        print(f"Sent payload | Bytes written: {res}")
        
        # 2. Read response feature report (Report ID 0x06, expecting 32 bytes)
        try:
            # get_feature_report takes (report_id, length)
            response = device.get_feature_report(0x06, 32)
            if response:
                hex_response = "".join(f"{b:02x}" for b in response)
                print(f" <- Mouse Response: {hex_response}")
            else:
                print(" <- Mouse Response: None / Empty")
        except Exception as read_err:
            print(f" <- Response Read Error (Device may not echo back): {read_err}")

    while True:
        choice = input("Enter choice: ").strip().lower()
        counter = (counter + 1) & 0xFF
        
        if choice == '1':
            payload = list(white_payload_dpi1)
            payload[2] = counter
            send_and_get_response(payload)
            
        elif choice == '2':
            payload = list(purple_payload_dpi1)
            payload[2] = counter
            send_and_get_response(payload)
            
        elif choice == '3':
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            payload = [
                0x06, 0x03, counter, 0x01, 0x0a, 
                r, g, b, 
                0xff, 0x00, 0x00, 0x00, 
                0xff, 0x00, 0x00, 0xff, 
                0xff, 0xff, 0x00, 0xff, 
                0xff, 0xff, 0x00, 0xff, 
                0xff, 0xff, 0xff, 0xff, 
                0xff, 0x00, 0x00, 0x00
            ]
            send_and_get_response(payload)
            
        elif choice == '11':
            payload = list(white_payload_dpi1)
            payload[2] = counter
            payload[4] = 0x13
            send_and_get_response(payload)
            
        elif choice == '12':
            payload = list(purple_payload_dpi1)
            payload[2] = counter
            payload[4] = 0xd9
            send_and_get_response(payload)
            
        elif choice == '13':
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            payload = [
                0x06, 0x03, counter, 0x01, 0x13, 
                r, g, b, 
                0xff, 0x00, 0x00, 0x00, 
                0xff, 0x00, 0x00, 0xff, 
                0xff, 0xff, 0x00, 0xff, 
                0xff, 0xff, 0x00, 0xff, 
                0xff, 0xff, 0xff, 0xff, 
                0xff, 0x00, 0x00, 0x00
            ]
            send_and_get_response(payload)
            
        elif choice == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Use 1, 2, 3, 11, 12, 13, or q.")

    device.close()

except Exception as e:
    print(f"Error: {e}")