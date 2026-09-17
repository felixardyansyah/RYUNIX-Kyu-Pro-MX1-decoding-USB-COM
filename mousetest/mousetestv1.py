import time
import hid

VENDOR_ID = 0x04F3
PRODUCT_ID = 0x026E

VENDOR_ID_WIRELESS = 0x04F3
PRODUCT_ID_WIRELESS = 0x026F


# Captured White Preset payload
white_payload = [
    0x06, 0x03, 0x11, 0x01, 0x0a, 0xff, 0xff, 0xff, 
    0xff, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0xff, 
    0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0x00, 0xff, 
    0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00
]

# Captured Purple Custom payload
purple_payload = [
    0x06, 0x03, 0x14, 0x01, 0xd0, 0x40, 0x00, 0x80, 
    0xff, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0xff, 
    0xff, 0xff, 0x00, 0xff, 0xff, 0xff, 0x00, 0xff, 
    0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00
]

target_path = None
for info in hid.enumerate(VENDOR_ID_WIRELESS, PRODUCT_ID_WIRELESS):
    path_str = info['path'].decode('utf-8', errors='ignore') if isinstance(info['path'], bytes) else info['path']
    if "Col05" in path_str:
        target_path = info['path']
        break

if not target_path:
    print("Error: Could not find Col05 control path.")
    exit()

try:
    device = hid.device()
    device.open_path(target_path)
    print("Successfully connected to mouse lighting collection (Col05)!")
    print("\nControls:")
    print("  [1] Send White Payload")
    print("  [2] Send Purple Payload")
    print("  [q] Quit")
    print("-" * 30)

    while True:
        choice = input("Press a key (1, 2, or q): ").strip().lower()
        
        if choice == '1':
            res = device.send_feature_report(white_payload)
            print(f"Sent White! Bytes accepted: {res}")
        elif choice == '2':
            res = device.send_feature_report(purple_payload)
            print(f"Sent Purple! Bytes accepted: {res}")
        elif choice == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice, press 1, 2, or q.")

    device.close()

except Exception as e:
    print(f"Error: {e}")