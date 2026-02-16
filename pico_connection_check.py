"""
Raspberry Pi Pico USB 接続確認スクリプト
Windows で Pico が COM ポートとして認識されているか確認します。
"""
import sys

try:
    import serial.tools.list_ports
    import serial
except ImportError:
    print("pyserial がインストールされていません。以下を実行してください:")
    print("  pip install pyserial")
    sys.exit(1)


def main():
    print("=== 利用可能な COM ポート一覧 ===\n")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("COM ポートが検出されませんでした。")
        print("  - Pico の USB ケーブルが接続されているか確認してください")
        print("  - Pico に MicroPython/CircuitPython 等が書き込まれていると USB シリアルで認識されます")
        return

    pico_candidates = []
    for p in ports:
        desc = p.description or ""
        hwid = (p.hwid or "").upper()
        # Raspberry Pi Pico は VID 2E8A (Raspberry Pi Foundation)
        is_pico = "2E8A" in hwid or "Pico" in desc or "Raspberry" in desc
        if is_pico:
            pico_candidates.append(p)
        print(f"  {p.device}: {desc}")
        print(f"    HWID: {p.hwid}\n")

    if pico_candidates:
        print("--- Pico と思われるポート ---")
        for p in pico_candidates:
            print(f"  → {p.device}")
        port = pico_candidates[0].device
    else:
        port = ports[0].device
        print(f"--- 最初のポートで開くテスト: {port} ---\n")

    print(f"\nポート {port} を開いて接続テストします...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"  OK: {port} を開けました。")
        ser.close()
        print("  接続確認できました。")
    except serial.SerialException as e:
        print(f"  エラー: {e}")
        print("  - 他のソフトがポートを使っていないか確認してください")
        print("  - デバイスマネージャーで COM 番号を確認してください")


if __name__ == "__main__":
    main()
