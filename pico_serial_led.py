"""
Raspberry Pi Pico - シリアルでLEDを操作 (MicroPython)

Windows 側の Python から USB シリアルでコマンドを受け取り、LED を点灯/消灯します。

【使い方】
  1. このファイルを Pico に main.py として保存する
  2. Thonny を終了する（シリアルを離す）
  3. Pico の RESET ボタンを押すか、USB を抜き差しする
  4. Windows 側で windows_led_control.py を実行する

【コマンド】
  1文字: 1 / H → 点灯,  0 / L → 消灯,  b / B → 3回点滅,  T → トリガーパルス
  文字列: "READY\\n" → 起動完了で点滅,  "GOOD\\n" → 40桁で3秒間早い点滅,  "NOGOOD\\n" → 40桁以外で1回長点滅
"""

from machine import Pin
import sys
import time

LED_PIN = 25   # オンボードLED。外部LEDなら 15 などに変更
TRIGGER_PIN = 16   # トリガー出力用GPIO（カメラ・リレーなど）。変更可: 14, 15, 16, 17 など
TRIGGER_PULSE_MS = 100   # パルス幅（ミリ秒）

led = Pin(LED_PIN, Pin.OUT)
trigger = Pin(TRIGGER_PIN, Pin.OUT)
trigger.value(0)

def blink(n=3, on_ms=200, off_ms=200):
    for _ in range(n):
        led.value(1)
        time.sleep_ms(on_ms)
        led.value(0)
        time.sleep_ms(off_ms)


# READY 受信時の点滅回数・速度（好みで変更可）
READY_BLINK_COUNT = 5
READY_BLINK_ON_MS = 150
READY_BLINK_OFF_MS = 150

# GOOD 受信時: 3秒間早い点滅
GOOD_BLINK_DURATION_MS = 3000
GOOD_BLINK_ON_MS = 80
GOOD_BLINK_OFF_MS = 80

def blink_for_ms(duration_ms, on_ms, off_ms):
    """指定ミリ秒の間、早い点滅を繰り返す"""
    end = time.ticks_add(time.ticks_ms(), duration_ms)
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        led.value(1)
        time.sleep_ms(on_ms)
        led.value(0)
        time.sleep_ms(off_ms)
    led.value(0)

def pulse_trigger():
    trigger.value(1)
    time.sleep_ms(TRIGGER_PULSE_MS)
    trigger.value(0)

print("LED/トリガー シリアル待ち受け (1=ON, 0=OFF, b=blink, T=trigger, READY=点滅)")
print("Windows 側のプログラムを起動してください。")

# "READY\n" 用の行バッファ（1文字コマンド以外を貯める）
line_buf = ""

while True:
    try:
        c = sys.stdin.read(1)
    except Exception:
        break
    if not c:
        continue
    # 1文字コマンド: 即実行
    if c in ("1", "0", "H", "L", "B", "b", "T"):
        line_buf = ""
        c = c.upper()
        if c in ("1", "H"):
            led.value(1)
        elif c in ("0", "L"):
            led.value(0)
        elif c == "B":
            blink(3)
        elif c == "T":
            pulse_trigger()
        continue
    # 改行まで貯めて "READY" / "GOOD" / "NOGOOD" なら点滅
    if c == "\n" or c == "\r":
        line_upper = line_buf.strip().upper()
        if line_upper == "READY":
            blink(READY_BLINK_COUNT, READY_BLINK_ON_MS, READY_BLINK_OFF_MS)
        elif line_upper == "GOOD":
            blink_for_ms(GOOD_BLINK_DURATION_MS, GOOD_BLINK_ON_MS, GOOD_BLINK_OFF_MS)  # 3秒間早い点滅
        elif line_upper == "NOGOOD":
            blink(1, 500, 500)  # 40桁以外: 1回長く点滅（0.5秒点灯・0.5秒消灯）
        line_buf = ""
        continue
    line_buf += c
