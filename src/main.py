import flet as ft
import httpx
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://pokeapi.co/api/v2/"

# Web環境（Pyodide）かどうかを判定
IS_WEB = "pyodide" in sys.modules or "emscripten" in sys.platform


def main(page: ft.Page):
    page.title = "Pokemon Type Filter"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    api_result = ft.Text(value="Pokemon: N/A")
    pokemon_list = ft.Row([], scroll=ft.ScrollMode.AUTO, wrap=True)
    type_dropdown = ft.Dropdown(label="Select Pokemon Type", width=200, options=[])

    # 詳細表示用のダイアログ
    detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Pokemon Details"),
        content=ft.Container(width=400, height=500),
        actions=[ft.TextButton("Close", on_click=lambda _: close_detail_dialog())],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_detail_dialog():
        """詳細ダイアログを閉じる"""
        detail_dialog.open = False
        page.update()

    def create_pokemon_card(details, pokemon_name):
        """ポケモンカードを作成する共通関数"""
        if details:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(
                                src=details["image"],
                                width=96,
                                height=96,
                                fit=ft.ImageFit.CONTAIN,
                            )
                            if details["image"]
                            else ft.Container(height=96),
                            ft.Text(
                                details["name"].capitalize(),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"#{details['id']:03d}",
                                size=12,
                                color="grey600",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    padding=15,
                    width=150,
                    alignment=ft.alignment.center,
                    ink=True,
                    on_click=lambda e, pokemon_details=details: show_pokemon_detail(
                        pokemon_details
                    ),
                )
            )
        else:
            # 詳細情報が取得できない場合は名前のみ表示
            return ft.Card(
                content=ft.Container(
                    content=ft.Text(pokemon_name.capitalize()),
                    padding=10,
                    width=150,
                    ink=True,
                )
            )

    def show_pokemon_detail(pokemon_details):
        """ポケモンの詳細情報をダイアログで表示"""
        if not pokemon_details:
            return

        # タイプの表示用チップを作成
        type_chips = []
        for pokemon_type in pokemon_details["types"]:
            type_chips.append(
                ft.Chip(
                    label=ft.Text(pokemon_type.capitalize()),
                    bgcolor="#E3F2FD",
                )
            )

        # 能力の表示用チップを作成
        ability_chips = []
        for ability in pokemon_details["abilities"]:
            ability_chips.append(
                ft.Chip(
                    label=ft.Text(ability.replace("-", " ").title()),
                    bgcolor="#E8F5E8",
                )
            )

        # ステータスの表示
        stat_rows = []
        for stat_name, stat_value in pokemon_details["stats"].items():
            stat_display_name = stat_name.replace("-", " ").title()
            stat_rows.append(
                ft.Row(
                    [
                        ft.Text(
                            f"{stat_display_name}:",
                            weight=ft.FontWeight.BOLD,
                            width=120,
                        ),
                        ft.Text(str(stat_value)),
                        ft.ProgressBar(
                            value=stat_value / 255, width=150, color="#2196F3"
                        ),
                    ]
                )
            )

        # ダイアログの内容を設定
        detail_dialog.title = ft.Text(
            f"{pokemon_details['name'].capitalize()} (#{pokemon_details['id']:03d})"
        )
        detail_dialog.content = ft.Container(
            content=ft.Column(
                [
                    # ポケモンの画像
                    ft.Container(
                        content=ft.Image(
                            src=pokemon_details["image"],
                            width=150,
                            height=150,
                            fit=ft.ImageFit.CONTAIN,
                        )
                        if pokemon_details["image"]
                        else ft.Text("No Image Available"),
                        alignment=ft.alignment.center,
                    ),
                    # 基本情報
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Basic Info", size=16, weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(
                                                "Height:",
                                                weight=ft.FontWeight.BOLD,
                                                width=80,
                                            ),
                                            ft.Text(
                                                f"{pokemon_details['height'] / 10:.1f} m"
                                            ),
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(
                                                "Weight:",
                                                weight=ft.FontWeight.BOLD,
                                                width=80,
                                            ),
                                            ft.Text(
                                                f"{pokemon_details['weight'] / 10:.1f} kg"
                                            ),
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(
                                                "Base Exp:",
                                                weight=ft.FontWeight.BOLD,
                                                width=80,
                                            ),
                                            ft.Text(
                                                str(pokemon_details["base_experience"])
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            padding=10,
                        )
                    ),
                    # タイプ
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Types", size=16, weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Row(type_chips, wrap=True),
                                ]
                            ),
                            padding=10,
                        )
                    ),
                    # 能力
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Abilities", size=16, weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Row(ability_chips, wrap=True),
                                ]
                            ),
                            padding=10,
                        )
                    ),
                    # ステータス
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Base Stats", size=16, weight=ft.FontWeight.BOLD
                                    ),
                                    *stat_rows,
                                ]
                            ),
                            padding=10,
                        )
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            width=400,
            height=500,
        )

        detail_dialog.open = True
        page.update()

    def get_pokemon_types():
        """ポケモンのタイプ一覧を取得"""
        try:
            response = httpx.get(f"{BASE_URL}type/")
            if response.status_code == 200:
                data = response.json()
                types = []
                for type_info in data["results"]:
                    # 一部の特殊なタイプは除外
                    if type_info["name"] not in ["unknown", "shadow"]:
                        types.append(
                            ft.dropdown.Option(
                                key=type_info["name"],
                                text=type_info["name"].capitalize(),
                            )
                        )
                return types
            else:
                return []
        except Exception as e:
            print(f"Error fetching types: {e}")
            return []

    def get_pokemon_details(pokemon_name):
        """ポケモンの詳細情報（画像含む）を取得（同期版）"""
        try:
            response = httpx.get(f"{BASE_URL}pokemon/{pokemon_name}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["name"],
                    "id": data["id"],
                    "image": data["sprites"]["front_default"],
                    "height": data["height"],
                    "weight": data["weight"],
                    "types": [type_info["type"]["name"] for type_info in data["types"]],
                    "abilities": [
                        ability["ability"]["name"] for ability in data["abilities"]
                    ],
                    "stats": {
                        stat["stat"]["name"]: stat["base_stat"]
                        for stat in data["stats"]
                    },
                    "base_experience": data.get("base_experience", 0),
                }
            else:
                return None
        except Exception as e:
            print(f"Error fetching Pokemon details for {pokemon_name}: {e}")
            return None

    async def get_pokemon_details_async(pokemon_name):
        """ポケモンの詳細情報（画像含む）を取得（非同期版）"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}pokemon/{pokemon_name}")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "name": data["name"],
                        "id": data["id"],
                        "image": data["sprites"]["front_default"],
                        "height": data["height"],
                        "weight": data["weight"],
                        "types": [
                            type_info["type"]["name"] for type_info in data["types"]
                        ],
                        "abilities": [
                            ability["ability"]["name"] for ability in data["abilities"]
                        ],
                        "stats": {
                            stat["stat"]["name"]: stat["base_stat"]
                            for stat in data["stats"]
                        },
                        "base_experience": data.get("base_experience", 0),
                    }
                else:
                    return None
        except Exception as e:
            print(f"Error fetching Pokemon details for {pokemon_name}: {e}")
            return None

    def get_pokemon_by_type(type_name):
        """指定されたタイプのポケモン一覧を取得"""
        try:
            response = httpx.get(f"{BASE_URL}type/{type_name}")
            if response.status_code == 200:
                data = response.json()
                pokemon_list.controls.clear()

                # ポケモン一覧を表示
                if data["pokemon"]:
                    processing_mode = "非同期処理" if IS_WEB else "スレッド並列処理"
                    api_result.value = f"Found {len(data['pokemon'])} Pokemon of type '{type_name.capitalize()}' ({processing_mode})"

                    # 表示するポケモン数を設定（デスクトップ版では多く、Web版では少なく）
                    max_pokemon = 15 if IS_WEB else 40
                    pokemon_names = [
                        info["pokemon"]["name"]
                        for info in data["pokemon"][:max_pokemon]
                    ]

                    if IS_WEB:
                        # Web環境では非同期処理で並行実行
                        async def load_pokemon_async():
                            # 非同期で全ポケモンの詳細を並行取得
                            tasks = [
                                get_pokemon_details_async(name)
                                for name in pokemon_names
                            ]
                            pokemon_details_list = await asyncio.gather(*tasks)

                            # 取得した詳細情報を使ってカードを作成・表示
                            for details, pokemon_name in zip(
                                pokemon_details_list, pokemon_names
                            ):
                                pokemon_card = create_pokemon_card(
                                    details, pokemon_name
                                )
                                pokemon_list.controls.append(pokemon_card)

                            page.update()

                        # 非同期関数を実行
                        asyncio.create_task(load_pokemon_async())
                    else:
                        # デスクトップ環境では並列処理で高速化
                        with ThreadPoolExecutor(max_workers=8) as executor:
                            pokemon_details_list = list(
                                executor.map(get_pokemon_details, pokemon_names)
                            )

                        # 取得した詳細情報を使ってカードを作成
                        for i, (details, pokemon_name) in enumerate(
                            zip(pokemon_details_list, pokemon_names)
                        ):
                            pokemon_card = create_pokemon_card(details, pokemon_name)
                            pokemon_list.controls.append(pokemon_card)
                else:
                    api_result.value = f"No Pokemon found for type '{type_name}'"

                page.update()
            else:
                api_result.value = "Error fetching Pokemon"
                page.update()
        except Exception as e:
            api_result.value = f"Error: {str(e)}"
            page.update()

    def on_type_change(e):
        """タイプが選択されたときの処理"""
        if type_dropdown.value:
            get_pokemon_by_type(type_dropdown.value)

    # タイプ一覧を取得してドロップダウンに設定
    types = get_pokemon_types()
    type_dropdown.options = types
    type_dropdown.on_change = on_type_change

    # ダイアログをページに追加
    page.overlay.append(detail_dialog)

    page.add(
        ft.Column(
            [
                ft.Row(
                    [type_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [api_result],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=pokemon_list,
                    height=500,
                    padding=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.app(main)
