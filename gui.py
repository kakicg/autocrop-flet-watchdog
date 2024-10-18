import flet as ft

def start_gui(page: ft.Page):
    page.title = "商品撮影システム"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50

    def set_item(event):
        event.control.value = ""
        page.session.set("barcode_loop", False)
        # page.update()

    def next_item(event):
        page.session.set("gridview_loop", False)
        # page
        
    barcode_textfield = ft.TextField(on_submit=set_item, border_color=ft.colors.BLACK)
    barcode_controls = [
        ft.Text("バーコードをスキャンしてください", size=12, color=ft.colors.WHITE),
        barcode_textfield
    ]
    top1_row = ft.Row(barcode_controls)
    page.add(top1_row)

    item_infos = [
        ft.Text("商品情報", size=12, color=ft.colors.WHITE, weight=ft.FontWeight.W_600),
        ft.CupertinoFilledButton(text="次へ", on_click=next_item, opacity_on_click=0.3,),
    ]
    top2_row = ft.Row(item_infos)
    page.add(top2_row)

    gridview = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=200,
        child_aspect_ratio=0.5625,
        spacing=30,
        run_spacing=10,
    )
    page.add(gridview)

def add_image_and_update(page: ft.Page, image_path: str, item_num: str, height: float):
    """FletのGUIを更新して画像と高さ情報を表示する"""
    # 画像コンポーネントの作成
    gridview = page.controls[-1]

    gridview.controls.insert(0,
        ft.Column(
            [
                ft.Text(
                    f"[ {item_num} ]",
                    size=12,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Text(
                    f"推定高さ:{height}",
                    size=12,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.W_100,
                ),
                ft.Image(
                    src=image_path,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                ),
            ]
        )            
    )
    page.update()
