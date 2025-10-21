import flet as ft

def main(page: ft.Page):
    def pick_result(e: ft.FilePickerResultEvent):
        if e.path:
            page.add(ft.Text(f"選択されたパス: {e.path}"))
        else:
            page.add(ft.Text("キャンセルされました"))

    file_picker = ft.FilePicker(on_result=pick_result)
    page.overlay.append(file_picker)

    btn = ft.ElevatedButton("フォルダ選択", on_click=lambda e: file_picker.get_directory_path())
    page.add(btn)

ft.app(target=main, view=None)