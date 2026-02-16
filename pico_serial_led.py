"""
Raspberry Pi Pico - シリアルでLEDを操作 (MicroPython)

Windows 側の Python から USB シリアルでコマンドを受け取り、LED を点灯/消灯します。

【使い方】
  1. このファイルを Pico に main.py として保存する
  2. Thonny を終了する（シリアルを離す）
  3. Pico の RESET ボタンを押すか、USB を抜き差しする
  4. Windows 側で windows_led_control.py を実行する

【コマンド】1文字で送信
  1 または H  → LED 点灯
  0 または L  → LED 消灯
  b または B  → 3回点滅
  T           → トリガーピンをパルス出力（起動完了通知など）
  q           → 終了（Pico は待ち受け続けます）
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

def pulse_trigger():
    trigger.value(1)
    time.sleep_ms(TRIGGER_PULSE_MS)
    trigger.value(0)

print("LED/トリガー シリアル待ち受け (1=ON, 0=OFF, b=blink, T=trigger)")
print("Windows 側のプログラムを起動してください。")

while True:
    try:
        c = sys.stdin.read(1)
    except Exception:
        break
    if not c:
        continue
    c = c.upper()
    if c in ("1", "H"):
        led.value(1)
    elif c in ("0", "L"):
        led.value(0)
    elif c == "B":
        blink(3)
    elif c == "T":
        pulse_trigger()
