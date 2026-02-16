"""
Raspberry Pi Pico - LED 点滅テスト (MicroPython)

【Pico にこのファイルをコピーして実行してください】
  - Thonny で開き「マイクロコントローラーに保存」→ ファイル名を main.py にすると起動時に自動実行
  - または pico_led_blink.py のまま保存して実行
"""

from machine import Pin
import time

# ========== ここでピンを変更 ==========
# オンボードLEDを使う場合（配線不要）
LED_PIN = 25   # Pico 内蔵LED (GP25)

# 外部LEDを使う場合はコメントを入れ替え
# LED_PIN = 15  # 例: GP15 にLEDを接続する場合
# =====================================

led = Pin(LED_PIN, Pin.OUT)

print("LED 点滅開始 (Ctrl+C で停止)")
print(f"使用ピン: GP{LED_PIN}")

try:
    while True:
        led.value(1)   # 点灯
        print(".", end="")
        time.sleep(0.5)
        led.value(0)   # 消灯
        time.sleep(0.5)
except KeyboardInterrupt:
    led.value(0)
    print("\n終了")
