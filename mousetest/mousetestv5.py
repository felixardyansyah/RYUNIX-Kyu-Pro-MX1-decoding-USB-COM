import hid
import threading
import sys

VENDOR_ID = 0x04F3
PRODUCT_ID_O_WIRELESS = 0x026F

def interface_listener(iface, path):
    """Generic high-speed listener for any HID interface path."""
    write = sys.stdout.buffer.write
    prefix = f"[Interface {iface}] ".encode('ascii')
    
    try:
        h = hid.device()
        h.open_path(path)
        h.set_nonblocking(False)  # Blocking mode for instant hardware interrupt response
        
        while True:
            data = h.read(64)
            if data:
                hex_str = bytes(data).hex(' ', 1).encode('ascii')
                write(prefix + hex_str + b'\n')
    except Exception as e:
        write(f"[Interface {iface} ERROR] {e}\n".encode('ascii'))

def main():
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID_O_WIRELESS)
    if not devices:
        print("No HID devices found. Check your Vendor/Product IDs.")
        return

    print("Scanning and opening all available Ryunix interfaces...")
    
    threads = []
    seen_paths = set()
    
    for info in devices:
        path = info['path']
        if path in seen_paths:
            continue
        seen_paths.add(path)
        
        iface = info.get('interface_number', 0)
        
        # Spawn a dedicated high-speed thread for every unique interface path found
        t = threading.Thread(target=interface_listener, args=(iface, path), daemon=True)
        threads.append(t)
        t.start()
        print(f" -> Started listener for Interface {iface} at path snippet: {path[-20:]}")

    print("\n⚡ ALL INTERFACES STREAMING. Move your mouse or click now!\n")
    
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()