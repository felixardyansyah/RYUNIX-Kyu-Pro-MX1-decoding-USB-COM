import hid

VENDOR_ID = 0x04F3  
PRODUCT_ID = 0x026E 

VENDOR_ID_WIRELESS = 0x04F3
PRODUCT_ID_WIRELESS = 0x026F

def find_mouse_interface():
    for vid, pid in [(VENDOR_ID_WIRELESS, PRODUCT_ID_WIRELESS), (VENDOR_ID, PRODUCT_ID)]:
        for info in hid.enumerate(vid, pid):
            if info['usage_page'] == 0x0A and info['usage'] == 0xC7:
                return info['path']
                
    for vid, pid in [(VENDOR_ID_WIRELESS, PRODUCT_ID_WIRELESS), (VENDOR_ID, PRODUCT_ID)]:
        devices = hid.enumerate(vid, pid)
        if devices:
            return devices[0]['path']
            
    return None

def print_hex_block(data):
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        print(f"  {i:04x}    {hex_part}")

def main():
    path = find_mouse_interface()
    if not path:
        print("No matching mouse found. Check your Vendor ID and Product ID.")
        return

    device = hid.device()
    try:
        device.open_path(path)
        print(f"Connected to device path: {path}")
        print("\nCommands:")
        print("  [5] Get Feature Report 0x05")
        print("  [6] Get Feature Report 0x06")
        print("  [q] Quit\n")

        while True:
            choice = input("Select command (5, 6, or q): ").strip().lower()
            
            if choice == 'q':
                break
            
            if choice == '5':
                report_id = 0x05
            elif choice == '6':
                report_id = 0x06
            else:
                print("Invalid choice. Press 5, 6, or q.")
                continue

            try:
                # Pure GET_REPORT — no writing required
                response = device.get_feature_report(report_id, 64)
                
                print(f"<- GET_REPORT Response for 0x{choice}:")
                if response:
                    print_hex_block(response)
                else:
                    print("   [Empty Response]")
                print()
                
            except IOError as e:
                print(f"Communication error: {e}\n")

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        device.close()

if __name__ == "__main__":
    main()