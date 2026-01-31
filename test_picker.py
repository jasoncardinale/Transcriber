# import flet as ft


# def main(page: ft.Page):
#     page.title = "Test File Picker"

#     async def pick_files(e):
#         print("pick_files called")
#         file_picker = ft.FilePicker()
#         files_list = await file_picker.pick_files(allow_multiple=True)
#         print("files_list =", files_list)
#         if files_list:
#             result.value = ", ".join([f.name for f in files_list])
#         else:
#             result.value = "Cancelled!"
#         page.update()

#     result = ft.Text("")

#     page.add(
#         ft.Row(
#             controls=[
#                 ft.Button(
#                     "Pick files",
#                     icon=ft.Icons.UPLOAD_FILE,
#                     on_click=pick_files,
#                 ),
#                 result,
#             ]
#         )
#     )


# ft.run(main)

import flet as ft


def main(page: ft.Page):
    page.title = "Test File Picker with Tabs"

    result = ft.Text("")

    async def pick_files(e):
        print("pick_files called")
        file_picker = ft.FilePicker()
        files_list = await file_picker.pick_files(allow_multiple=True)
        print("files_list =", files_list)
        if files_list:
            result.value = ", ".join([f.name for f in files_list])
        else:
            result.value = "Cancelled!"
        page.update()

    tab1 = ft.Column(
        [
            ft.Text("Tab 1 Content"),
            ft.Row(
                controls=[
                    ft.Button(
                        "Pick files",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=pick_files,
                    ),
                    result,
                ]
            ),
        ]
    )

    tab2 = ft.Column([ft.Text("Tab 2 Content")])

    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Upload"),
                        ft.Tab(label="View"),
                    ]
                ),
                ft.TabBarView(expand=True, controls=[tab1, tab2]),
            ],
        ),
        expand=True,
    )

    page.add(tabs)


ft.run(main)
