"""
Pico LED 制御（他モジュールから利用）
アプリ起動時のスタンバイ通知などに使用。
複数台の Pico 接続時は、全台に同じコマンドを送信します。
"""
import threading
import time

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

BAUD = 115200
PICO_VID = "2E8A"


def _find_pico_port():
    """接続されている最初の Pico の COM ポートを返す（後方互換）。"""
    ports = _find_pico_ports()
    return ports[0] if ports else None


def _find_pico_ports():
    """接続されている全ての Pico の COM ポートのリストを返す。"""
    if serial is None:
        return []
    return [
        p.device
        for p in serial.tools.list_ports.comports()
        if PICO_VID in (p.hwid or "").upper()
    ]


def blink_led_for_seconds(seconds: float = 10, interval: float = 0.5):
    """
    接続中の全 Pico の LED を指定秒数だけ点滅させる。
    バックグラウンドスレッドから呼ぶ想定。接続失敗時は何もしない。
    """
    if serial is None:
        return
    ports = _find_pico_ports()
    if not ports:
        return
    connections = []
    for port in ports:
        try:
            connections.append(serial.Serial(port, BAUD, timeout=0.5))
        except Exception:
            pass
    if not connections:
        return
    try:
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            for ser in connections:
                try:
                    ser.write(b"1")
                    ser.flush()
                except Exception:
                    pass
            time.sleep(interval)
            for ser in connections:
                try:
                    ser.write(b"0")
                    ser.flush()
                except Exception:
                    pass
            time.sleep(interval)
        for ser in connections:
            try:
                ser.write(b"0")
                ser.flush()
            except Exception:
                pass
    except Exception:
        pass
    finally:
        for ser in connections:
            try:
                ser.close()
            except Exception:
                pass


def start_blink_in_background(seconds: float = 10, interval: float = 0.5):
    """LED を指定秒数だけ点滅させるスレッドを開始する（非ブロック）。"""
    def _run():
        blink_led_for_seconds(seconds=seconds, interval=interval)
    t = threading.Thread(target=_run, daemon=True)
    t.start()


def fire_trigger():
    """
    接続中の全 Pico のトリガーピン（デフォルト GP16）をパルス出力する。
    起動完了通知などに使用。接続失敗時は何もしない。
    """
    if serial is None:
        return
    for port in _find_pico_ports():
        try:
            ser = serial.Serial(port, BAUD, timeout=0.5)
            ser.write(b"T")
            ser.flush()
            ser.close()
        except Exception:
            pass


def start_trigger_in_background():
    """全 Pico のトリガーをバックグラウンドで1回出す（非ブロック）。"""
    t = threading.Thread(target=fire_trigger, daemon=True)
    t.start()


def get_pico_port_count():
    """接続中の Pico の台数を返す（デバッグ・表示用）。"""
    return len(_find_pico_ports())


# Pico が "READY\n" を受信して処理開始する場合に送る文字列
READY_MESSAGE = b"READY\n"
# Pico に 40桁バーコード受信完了を通知する文字列
GOOD_MESSAGE = b"GOOD\n"
# Pico に 40桁以外のバーコードを通知する文字列
NOGOOD_MESSAGE = b"NOGOOD\n"


def send_ready():
    """
    接続中の全 Pico に "READY\\n" を送信する。
    Pico 側で "READY\\n" を受けたら処理を開始する実装になっている場合に使用。
    接続失敗時は何もしない。
    """
    if serial is None:
        return
    for port in _find_pico_ports():
        try:
            ser = serial.Serial(port, BAUD, timeout=0.5)
            ser.write(READY_MESSAGE)
            ser.flush()
            ser.close()
        except Exception:
            pass


def start_send_ready_in_background():
    """全 Pico に READY をバックグラウンドで送信する（非ブロック）。"""
    t = threading.Thread(target=send_ready, daemon=True)
    t.start()


def send_good():
    """
    接続中の全 Pico に "GOOD\\n" を送信する。
    40桁バーコードを重複なく受信したときなどに使用。接続失敗時は何もしない。
    """
    if serial is None:
        return
    for port in _find_pico_ports():
        try:
            ser = serial.Serial(port, BAUD, timeout=0.5)
            ser.write(GOOD_MESSAGE)
            ser.flush()
            ser.close()
        except Exception:
            pass


def start_send_good_in_background():
    """全 Pico に GOOD をバックグラウンドで送信する（非ブロック）。"""
    t = threading.Thread(target=send_good, daemon=True)
    t.start()


def send_nogood():
    """
    接続中の全 Pico に "NOGOOD\\n" を送信する。
    40桁以外のバーコードを受信したときに使用。接続失敗時は何もしない。
    """
    if serial is None:
        return
    for port in _find_pico_ports():
        try:
            ser = serial.Serial(port, BAUD, timeout=0.5)
            ser.write(NOGOOD_MESSAGE)
            ser.flush()
            ser.close()
        except Exception:
            pass


def start_send_nogood_in_background():
    """全 Pico に NOGOOD をバックグラウンドで送信する（非ブロック）。"""
    t = threading.Thread(target=send_nogood, daemon=True)
    t.start()
