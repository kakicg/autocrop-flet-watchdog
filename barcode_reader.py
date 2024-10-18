import evdev

def read_barcode():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    barcode_device = None

    for device in devices:
        if "Barcode" in device.name:  # 名前でバーコードリーダーを識別
            barcode_device = device
            break

    if not barcode_device:
        print("バーコードリーダーが見つかりません。")
        return None

    print(f"バーコードリーダー検出: {barcode_device.name}")
    barcode = ""

    # バーコード読み取り
    for event in barcode_device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event = evdev.events.KeyEvent(event)
            if key_event.keystate == key_event.key_down:
                if key_event.keycode == "KEY_ENTER":
                    print(f"バーコード: {barcode[:6]}")
                    return barcode[:6]  # 製品番号の最初の6桁を返す
                else:
                    barcode += key_event.keycode.lstrip("KEY_")