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
    print("Error: Could not find Col05 control path.")
    exit()

try:
    device = hid.device()
    device.open_path(target_path)
    device.set_nonblocking(False)
    print("Successfully connected to mouse (Col05) - Hybrid Brightness Controller!")
    print("\nBrightness Controls:")
    print("  --- Dynamic Rolling Counter Mode ---")
    print("  [1] 100% Brightness (Rolling)")
    print("  [2] 75% Brightness (Rolling)")
    print("  [3] 25% Brightness (Rolling)")
    print("  --- Static Raw Payload Mode ---")
    print("  [6] Send 100% Raw Static Payload")
    print("  [7] Send 75% Raw Static Payload")
    print("  [8] Send 25% Raw Static Payload")
    print("  [9] Send rr% Raw Static Payload")
    print("  [q] Quit")
    print("-" * 40)

    counter = 0x30

    # Exact static raw payloads captured from logs
    payload_100_static = [
        [0x06, 0x06, 0x31, 0x18, 0x20, 0x00, 0x03, 0x41, 0x00] + [0x00]*23,
    ]

    payload_75_static = [
        [0x06, 0x06, 0x43, 0x01, 0x64, 0x00, 0x03, 0x32, 0x00] + [0x00]*23,
    ]

    payload_25_static = [
        [0x06, 0x06, 0x42, 0x01, 0x83, 0x00, 0x03, 0x11, 0x00] + [0x00]*23,
    ]

    payload_rr_static = [
        [0x06, 0x06, 0x10, 0x00, 0x00, 0x00, 0x07, 0x33, 0x00] + [0x00]*23,
    ]

    while True:
        choice = input("Select option (1-3, 6-9, or q): ").strip().lower()
        
        if choice == 'q':
            print("Exiting...")
            break
            
        if choice in ['1', '2', '3']:
            counter = (counter + 1) & 0xFF
            
            if choice == '1':
                byte4 = (counter + 0x51) & 0xFF
                byte5 = 0x20
                body_tail = [0x00, 0x34, 0x10]
                label = "100% (Rolling)"
                
            elif choice == '2':
                byte4 = (counter + 0x41) & 0xFF
                byte5 = ((counter & 0x0F) + 1) << 4
                body_tail = [0x00, 0x33, 0x10]
                label = "75% (Rolling)"
                
            elif choice == '3':
                byte4 = (counter + 0x21) & 0xFF
                byte5 = ((counter & 0x0F) + 1) << 4
                body_tail = [0x00, 0x31, 0x10]
                label = "25% (Rolling)"
                
            payload = [
                0x06, 0x06, counter, 0x01, byte4,
                byte5, *body_tail,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ]
            
            res = device.send_feature_report(payload)
            hex_str = "".join(f"{b:02x}" for b in payload)
            print(f"Sent [{label}] | Counter: 0x{counter:02X} | Written: {res}")
            print(f"Packet: {hex_str}")
            
            # Automatically read back response
            try:
                report_id = payload[0]
                response = device.get_feature_report(report_id, 33)
                resp_hex = "".join(f"{b:02x}" for b in response)
                print(f"Received: {resp_hex}\n")
            except Exception as read_err:
                print(f"Read error: {read_err}\n")
            
        elif choice in ['6', '7', '8', '9']:
            if choice == '6':
                active_static = payload_100_static
                label = "100% Static Raw"
            elif choice == '7':
                active_static = payload_75_static
                label = "75% Static Raw"
            elif choice == '8':
                active_static = payload_25_static
                label = "25% Static Raw"
            elif choice == '9':
                active_static = payload_rr_static
                label = "idk% Static Raw"

            for single_payload in active_static:
                res = device.send_feature_report(single_payload)
                hex_str = "".join(f"{b:02x}" for b in single_payload)
                print(f"Sent [{label} block] | Written: {res}")
                print(f"Packet: {hex_str}")
                
                # Automatically read back response for each frame
                try:
                    report_id = single_payload[0]
                    response = device.get_feature_report(report_id, 33)
                    resp_hex = "".join(f"{b:02x}" for b in response)
                    print(f"Received: {resp_hex}")
                except Exception as read_err:
                    print(f"Read error: {read_err}")

                time.sleep(0.01) # brief pause between burst frames
            print()
            
        else:
            print("Invalid choice. Please pick 1-3, 6-9, or q.")

    device.close()

except Exception as e:
    print(f"Error: {e}")