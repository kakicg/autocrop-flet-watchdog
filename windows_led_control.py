"""
Windows 側 - Pico の LED をシリアルで操作

【事前準備】
  1. Pico に pico_serial_led.py を main.py として保存
  2. Thonny を終了し、Pico を RESET（または USB 抜き差し）
  3. pip install pyserial

【使い方】
  対話モード:     python windows_led_control.py
  デモ実行:       python windows_led_control.py --demo
  ポート指定:     python windows_led_control.py --port COM5
  複数Pico 全台:  python windows_led_control.py --all
"""
import sys
import time
import argparse

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("pyserial がこの環境にありません。")
    print("  仮想環境 (.venv) を使っている場合は:")
    print("    python -m pip install pyserial")
    print("  または:")
    print("    pip install pyserial")
    sys.exit(1)

BAUD = 115200
PICO_VID = "2E8A"


def find_pico_port():
    """接続されている最初の Pico の COM ポートを検出"""
    ports = find_pico_ports()
    return ports[0] if ports else None


def find_pico_ports():
    """接続されている全ての Pico の COM ポートのリストを検出"""
    return [
        p.device
        for p in serial.tools.list_ports.comports()
        if PICO_VID in (p.hwid or "").upper()
    ]


def send(ser, cmd: str):
    """1文字送信（Pico は1文字ずつ処理）"""
    ser.write(cmd.encode("ascii"))
    ser.flush()


def main():
    parser = argparse.ArgumentParser(description="Pico LED を Windows から操作")
    parser.add_argument("--port", "-p", help="COM ポート (例: COM3)。未指定なら1台目を使用")
    parser.add_argument("--all", "-a", action="store_true", help="接続中の全 Pico に送信")
    parser.add_argument("--demo", "-d", action="store_true", help="点灯→消灯→点滅のデモを実行")
    args = parser.parse_args()

    if args.all:
        ports = find_pico_ports()
    else:
        port = args.port or find_pico_port()
        ports = [port] if port else []

    if not ports:
        print("Pico の COM ポートが見つかりません。")
        print("  --port COM3 で指定するか、複数台接続時は --all を試してください。")
        sys.exit(1)

    if len(ports) > 1:
        print(f"接続: {len(ports)} 台の Pico → {', '.join(ports)} ({BAUD} bps)")
    else:
        print(f"接続中: {ports[0]} ({BAUD} bps)")

    # 複数台の場合は全ポートを開く
    connections = []
    for port in ports:
        try:
            connections.append(serial.Serial(port, BAUD, timeout=0.5))
        except serial.SerialException as e:
            print(f"警告: {port} を開けません: {e}")
    if not connections:
        print("いずれのポートも開けません。Thonny を終了していますか？")
        sys.exit(1)

    def send_all(cmd: str):
        for ser in connections:
            try:
                send(ser, cmd)
            except Exception:
                pass

    if args.demo:
        print("デモ: 点灯 → 消灯 → 3回点滅")
        send_all("1")
        time.sleep(1)
        send_all("0")
        time.sleep(0.5)
        send_all("b")
        time.sleep(2)
        for ser in connections:
            ser.close()
        print("完了")
        return

    print("--- コマンド ---")
    print("  1 または on   … 点灯")
    print("  0 または off  … 消灯")
    print("  b または blink … 3回点滅")
    print("  t または trigger … トリガーピン(GP16)をパルス出力")
    print("  q … 終了")
    print()

    try:
        while True:
            try:
                key = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if not key:
                continue
            if key in ("q", "quit", "exit"):
                break
            if key in ("1", "on", "h"):
                send_all("1")
                print("  → 点灯")
            elif key in ("0", "off", "l"):
                send_all("0")
                print("  → 消灯")
            elif key in ("b", "blink"):
                send_all("b")
                print("  → 点滅")
            elif key in ("t", "trigger"):
                send_all("T")
                print("  → トリガー出力")
            else:
                print("  1 / 0 / b / t / q のいずれかを入力してください")
    finally:
        for ser in connections:
            ser.close()
        print("終了")


if __name__ == "__main__":
    main()
