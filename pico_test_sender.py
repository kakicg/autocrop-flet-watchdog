"""
Pico テスト送信アプリ (Flet GUI)

Raspberry Pi Pico に USB シリアルで
"READY\n", "GOOD\n", "NOGOOD\n", "BAD\n" を送信するテスト用デスクトップアプリ。

使い方:
  python pico_test_sender.py
"""
import flet as ft
import threading
import time
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

BAUD = 115200
PICO_VID = "2E8A"

COMMANDS = [
    ("READY",  "READY\n",  ft.Colors.BLUE),
    ("GOOD",   "GOOD\n",   ft.Colors.GREEN),
    ("NOGOOD", "NOGOOD\n", ft.Colors.ORANGE),
    ("BAD",    "BAD\n",    ft.Colors.RED),
]


def find_pico_ports():
    if serial is None:
        return []
    return [
        p.device
        for p in serial.tools.list_ports.comports()
        if PICO_VID in (p.hwid or "").upper()
    ]


def find_all_ports():
    if serial is None:
        return []
    return [
        (p.device, p.description or p.device)
        for p in serial.tools.list_ports.comports()
    ]


def main(page: ft.Page):
    page.title = "Pico テスト送信"
    page.window.width = 520
    page.window.height = 620
    page.padding = 20

    ser_lock = threading.Lock()
    ser_ref: list[serial.Serial | None] = [None]

    # --- UI parts ---
    port_dropdown = ft.Dropdown(
        label="ポート",
        width=280,
        options=[],
    )

    status_text = ft.Text("未接続", size=14, color=ft.Colors.GREY)

    log_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)

    def log(msg: str, color: str = ft.Colors.WHITE):
        ts = datetime.now().strftime("%H:%M:%S")
        log_list.controls.append(
            ft.Text(f"[{ts}] {msg}", size=13, color=color)
        )
        if len(log_list.controls) > 200:
            log_list.controls.pop(0)
        page.update()

    def refresh_ports(_=None):
        all_ports = find_all_ports()
        pico_ports = find_pico_ports()
        port_dropdown.options = [
            ft.dropdown.Option(
                key=dev,
                text=f"{dev}  ({desc})" + (" ★Pico" if dev in pico_ports else ""),
            )
            for dev, desc in all_ports
        ]
        if pico_ports and not port_dropdown.value:
            port_dropdown.value = pico_ports[0]
        elif all_ports and not port_dropdown.value:
            port_dropdown.value = all_ports[0][0]
        page.update()

    def connect(_=None):
        if serial is None:
            log("pyserial がインストールされていません", ft.Colors.RED)
            return
        port = port_dropdown.value
        if not port:
            log("ポートを選択してください", ft.Colors.ORANGE)
            return
        with ser_lock:
            if ser_ref[0] and ser_ref[0].is_open:
                ser_ref[0].close()
            try:
                ser_ref[0] = serial.Serial(port, BAUD, timeout=0.5)
                status_text.value = f"接続中: {port}"
                status_text.color = ft.Colors.GREEN
                log(f"{port} に接続しました", ft.Colors.GREEN)
            except serial.SerialException as e:
                status_text.value = "接続失敗"
                status_text.color = ft.Colors.RED
                log(f"接続エラー: {e}", ft.Colors.RED)
        page.update()

    def disconnect(_=None):
        with ser_lock:
            if ser_ref[0] and ser_ref[0].is_open:
                port = ser_ref[0].port
                ser_ref[0].close()
                ser_ref[0] = None
                status_text.value = "未接続"
                status_text.color = ft.Colors.GREY
                log(f"{port} を切断しました", ft.Colors.ORANGE)
            else:
                log("接続されていません", ft.Colors.GREY)
        page.update()

    def send_command(cmd_label: str, cmd_bytes: str, color: str):
        def handler(_=None):
            with ser_lock:
                s = ser_ref[0]
                if not s or not s.is_open:
                    log("未接続です。先に接続してください", ft.Colors.RED)
                    return
                try:
                    s.write(cmd_bytes.encode("ascii"))
                    s.flush()
                    log(f"送信: {cmd_label}", color)
                except Exception as e:
                    log(f"送信エラー ({cmd_label}): {e}", ft.Colors.RED)
        return handler

    cmd_buttons = []
    for label, cmd, color in COMMANDS:
        cmd_buttons.append(
            ft.ElevatedButton(
                text=label,
                bgcolor=color,
                color=ft.Colors.WHITE,
                width=110,
                height=60,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                on_click=send_command(label, cmd, color),
            )
        )

    page.add(
        ft.Text("Pico テスト送信", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10),
        ft.Row(
            [
                port_dropdown,
                ft.IconButton(ft.Icons.REFRESH, on_click=refresh_ports, tooltip="ポート再検索"),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        ft.Row(
            [
                ft.ElevatedButton("接続", icon=ft.Icons.USB, on_click=connect),
                ft.ElevatedButton("切断", icon=ft.Icons.USB_OFF, on_click=disconnect),
                status_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        ft.Divider(height=10),
        ft.Text("コマンド送信", size=16, weight=ft.FontWeight.BOLD),
        ft.Row(cmd_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        ft.Divider(height=10),
        ft.Row(
            [
                ft.Text("ログ", size=16, weight=ft.FontWeight.BOLD),
                ft.TextButton("クリア", on_click=lambda _: (log_list.controls.clear(), page.update())),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Container(
            content=log_list,
            expand=True,
            bgcolor=ft.Colors.BLACK12,
            border_radius=8,
            padding=8,
        ),
    )

    refresh_ports()


if __name__ == "__main__":
    ft.app(target=main)
