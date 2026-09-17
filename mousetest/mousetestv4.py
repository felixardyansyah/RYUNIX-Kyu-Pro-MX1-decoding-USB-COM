import hid
import time

VENDOR_ID = 0x04F3
PRODUCT_ID_O_WIRELESS = 0x026E  # Update if testing wired (0x026E) testing wireless (0x026F)

def list_and_listen_interfaces():
    print("Scanning for Ryunix HID interfaces...")
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID_O_WIRELESS)
    
    if not devices:
        print("No devices found. Check your Vendor/Product IDs.")
        return

    handles = []
    for info in devices:
        path = info['path']
        interface_number = info.get('interface_number', 'Unknown')
        print(f"\nFound interface -> Path: {path} | Interface: {interface_number}")
        
        try:
            h = hid.device()
            h.open_path(path)
            h.set_nonblocking(True)
            handles.append((interface_number, h))
            print(f"Successfully opened interface {interface_number}!")
        except Exception as e:
            print(f"Skipping path (likely blocked by Windows OS driver): {e}")

    print("\nListening for live reports... Try toggling switches or plugging in the cable.\n")
    
    try:
        while True:
            for iface, h in handles:
                try:
                    data = h.read(64)
                    if data:
                        hex_data = " ".join([f"{b:02x}" for b in data])
                        print(f"[Interface {iface}] Received {len(data)} bytes -> [ {hex_data} ]")
                except Exception:
                    pass
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        for _, h in handles:
            try:
                h.close()
            except:
                pass

if __name__ == "__main__":
    list_and_listen_interfaces()