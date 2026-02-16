# Raspberry Pi Pico - LED 点灯テスト 配線

## 1. オンボードLEDで試す（配線なし）

Pico には **GP25** に接続された内蔵LEDが付いています。

- **配線**: 不要。USB で PC につなぎ、プログラムを実行するだけ。
- **プログラム**: `pico_led_blink.py` の `LED_PIN = 25` のまま使う。

---

## 2. 外部LEDで試す（配線あり）

### 用意するもの

- LED 1個（色は何でも可）
- 抵抗 1本（**330Ω** または 220Ω〜470Ω）
- ジャンパー線（オス-メス または オス-オス）2本

### 配線図（回路）

```
Pico                          LED
┌─────────────┐
│  GP15 ──────┼────[330Ω]─────┤陽極(+・足が長い)├──── 陰極(-) ────┐
│             │                    LED                              │
│  GND ───────┼────────────────────────────────────────────────────┘
│  (3.3V)     │
└─────────────┘
```

- **GP15**（または GP0, GP2 など）→ **抵抗 330Ω** → **LED の陽極（長い足）** → **LED の陰極（短い足）** → **GND**

### ピン位置（Pico 上面・USB が手前）

```
       USB
    ┌─────────┐
    │  ○   ○  │  ← 向こう側
  ──┤ GP0  ○  ├──
  ──┤ GP1  ○  ├──
  ──┤ GND  3V3├──
  ──┤ GP2  ○  ├──
  ──┤ GP3  ○  ├──
  ──┤ GP4  ○  ├──
  ──┤ GP5  ○  ├──
  ──┤ GND  ○  ├──
  ──┤ GP6  ○  ├──
  ──┤ GP7  ○  ├──
  ──┤ GP8  ○  ├──
  ──┤ GP9  ○  ├──
  ──┤ GND  ○  ├──
  ──┤ GP10 ○  ├──
  ──┤ GP11 ○  ├──
  ──┤ GP12 ○  ├──
  ──┤ GP13 ○  ├──
  ──┤ GND  ○  ├──
  ──┤ GP14 ○  ├──
  ──┤ GP15 ○  ├──  ← ここにLED（抵抗経由）をつなぐ例
  ──┤ GP16 ○  ├──
    └─────────┘
```

- 使うGPIOは **GP15** と **GND** のどれか1つ。GND は「GND」と書いてあるピンならどこでも可。

---

## 2.5 トリガー出力ピン（起動完了通知など）

アプリ起動完了時に外部機器（カメラ、リレーなど）へトリガーをかけたい場合に使います。

- **デフォルトピン**: **GP16**（`pico_serial_led.py` の `TRIGGER_PIN` で変更可）
- **出力**: コマンド「T」受信で **約100ms の HIGH パルス**（`TRIGGER_PULSE_MS` で変更可）
- **配線例**: GP16 → 相手機器のトリガー入力。GND は共通。3.3V レベルなので、5V 系の機器の場合はレベル変換やリレーを挟んでください。

アプリ（main.py）のスタンバイ完了時に自動でこのトリガーが1回出力されます。手動テストは `python windows_led_control.py` で `t` を入力してください。

### プログラム側（ピン変更）

`pico_serial_led.py` の先頭付近:

```python
TRIGGER_PIN = 16   # 例: 17 に変更するなら 17
TRIGGER_PULSE_MS = 100   # パルス幅（ミリ秒）
```

### プログラム側

`pico_led_blink.py` で外部LEDを使う場合:

```python
# LED_PIN = 25   # オンボード
LED_PIN = 15     # 外部LED (GP15)
```

---

## 3. プログラムの書き込み・実行

1. Pico を USB で PC に接続。
2. **Thonny** を開く（https://thonny.org/）。
3. 右下で「Raspberry Pi Pico」と COM ポートを選択。
4. `pico_led_blink.py` を開く。
5. 「ファイル」→「名前を付けて保存」→「Raspberry Pi Pico」を選び、`main.py` で保存（起動時に自動実行）するか、そのまま保存して「実行」(F5)。

オンボードLEDまたは外部LEDが 0.5 秒間隔で点滅すればOKです。

---

## 4. Windows の Python から操作する

Thonny ではなく、Windows 側の Python で LED を操作する場合です。

1. **Pico 側**: `pico_serial_led.py` を Thonny で開き、**main.py として Pico に保存**する。
2. **Thonny を終了**する（シリアルを離す）。
3. Pico の **RESET** ボタンを押すか、USB を抜き差しする。→ Pico が main.py を実行し、シリアルでコマンド待ちになる。
4. **Windows 側**で次を実行する。
   ```bash
   pip install pyserial
   python windows_led_control.py
   ```
5. 対話で `1`（点灯）、`0`（消灯）、`b`（点滅）、`t`（トリガー）、`q`（終了）を入力する。
6. デモだけ実行する場合: `python windows_led_control.py --demo`
7. ポートを指定する場合: `python windows_led_control.py --port COM3`

---

## 5. 複数台の Pico を接続する

複数の Pico を USB で接続すると、それぞれ別の COM ポート（例: COM3, COM5, COM7）で認識されます。

- **アプリ（main.py）**: スタンバイ時の LED 点滅・トリガーは **接続されている全 Pico** に送信されます。追加の設定は不要です。
- **手動操作**: `python windows_led_control.py --all` で全台に同じコマンドを送信。`--port COM5` で 1 台だけ指定することもできます。
- **注意**: 各 Pico には同じ `pico_serial_led.py`（main.py）を書き込んでおいてください。台数が増えてもコマンドは同じです。
