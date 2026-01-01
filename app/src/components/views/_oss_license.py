from __future__ import annotations
from typing import TYPE_CHECKING
import os
import dataclasses
import customtkinter as ctk
from PIL import Image
if TYPE_CHECKING:
    from . import MainView

# OSSライセンスフィールドのコンポーネント
class OSSLicenseField(ctk.CTkScrollableFrame):
    master: ctk.CTkCanvas     # CTkScrollableFrameのmasterはCTkCanvas型になるため
    _master: OSSLicenseDetail # 親ビューの参照
    root_dir: str
    width: int
    height: int
    license_label: ctk.CTkLabel
    def __init__(self, master: OSSLicenseDetail, width: int, height: int, license_text: str) -> None:
        super(OSSLicenseField, self).__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=int(min(width, height) * 0.02),
            fg_color='transparent',
            bg_color='transparent'
        )
        self._master = master
        self.root_dir = master.root_dir
        self.width = width
        self.height = height
        self.license_text = license_text

        # ライセンス情報の表示
        license_label_width: int = int(self.width * 0.9)
        license_label_height: int = int(self.height * 0.9)
        license_label_font_size: int = int(min(self.width, self.height) * 0.025)
        self.license_label: ctk.CTkLabel = ctk.CTkLabel(
            master=self,
            text=self.license_text,
            width=license_label_width,
            height=license_label_height,
            fg_color='transparent',
            bg_color='transparent',
            justify=ctk.CENTER,
            wraplength=license_label_width,
            font=ctk.CTkFont(size=license_label_font_size)
        )
        self.license_label.pack(padx=int((self.width - license_label_width) / 2), pady=int((self.height - license_label_height) / 2))


# OSSライセンス詳細のコンポーネント
class OSSLicenseDetail(ctk.CTkFrame):
    master: OSSLicenseView
    root_dir: str
    width: int
    height: int
    oss_name: str
    back_button: ctk.CTkButton
    oss_name_label: ctk.CTkLabel
    license_field: OSSLicenseField
    def __init__(self, master: OSSLicenseView, root_dir: str, oss_name: str) -> None:
        super(OSSLicenseDetail, self).__init__(
            master=master,
            width=master.width,
            height=master.height,
            fg_color='transparent',
            bg_color='transparent'
        )
        self.root_dir = root_dir
        self.width = master.width
        self.height = master.height
        self.oss_name = oss_name

        # 戻るボタンの作成
        button_width: int = int(self.width * 0.1)
        button_height: int = int(self.height * 0.05)
        font_size: int = int(min(self.width, self.height) * 0.025)
        self.back_button = ctk.CTkButton(
            master=self,
            width=button_width,
            height=button_height,
            text='戻る',
            image=ctk.CTkImage(
                light_image=Image.open(f'{root_dir}/assets/icons/light/arrow_back_ios.png'),
                dark_image=Image.open(f'{root_dir}/assets/icons/dark/arrow_back_ios.png'),
                size=(font_size, font_size)
            ),
            font=ctk.CTkFont(size=font_size),
            fg_color='transparent',
            bg_color='transparent',
            command=self.back_to_list
        )
        self.back_button.place(relx=0.01, rely=0.01, anchor=ctk.NW)

        # OSSライセンス名ラベルの作成
        oss_name_font_size: int = int(min(self.width, self.height) * 0.035)
        self.oss_name_label = ctk.CTkLabel(
            master=self,
            text=self.oss_name,
            font=ctk.CTkFont(size=oss_name_font_size),
            # fg_color='transparent',
            bg_color='transparent'
        )
        self.oss_name_label.place(relx=0.5, rely=0.05, anchor=ctk.N)

        # OSSライセンスフィールドの作成
        license_field_width: int = int(self.width * 0.8)
        license_field_height: int = int(self.height * 0.8)
        self.license_field = OSSLicenseField(
            master=self,
            width=license_field_width,
            height=license_field_height,
            license_text=master.licenses[oss_name]
        )
        self.license_field.place(relx=0.5, rely=0.95, anchor=ctk.S)

    def back_to_list(self) -> None:
        # OSSライセンス詳細を非表示化
        self.place_forget()

        # OSSライセンスリストビューを作成して表示
        self.master.switch_to_license_list()

        # OSSライセンス詳細を破棄
        self.destroy()

# OSSライセンスリストのコンポーネント
class OSSLicenseList(ctk.CTkScrollableFrame):
    master: ctk.CTkCanvas   # CTkScrollableFrameのmasterはCTkCanvas型になるため
    _master: OSSLicenseView # 親ビューの参照
    root_dir: str
    width: int
    height: int
    buttons: dict[str, ctk.CTkButton] = dict[str, ctk.CTkButton]()
    def __init__(self, master: OSSLicenseView, root_dir: str, width: int, height: int) -> None:
        super(OSSLicenseList, self).__init__(
            master=master,
            width=width,
            height=height,
            label_text='OSSライセンス一覧',
            label_font=ctk.CTkFont(size=int(min(width, height) * 0.05)),
            corner_radius=int(min(width, height) * 0.02),
            bg_color='transparent'
        )
        self._master = master
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # OSSライセンスの一覧を表示するボタンを作成
        button_width: int = int(self.width * 0.9)
        button_height: int = int(self.height * 0.1)
        button_font_size: int = int(min(self.width, self.height) * 0.03)
        for oss_name in sorted(master.licenses.keys(), key=str.lower):
            self.buttons[oss_name] = ctk.CTkButton(
                master=self,
                text=oss_name,
                width=button_width,
                height=button_height,
                font=ctk.CTkFont(size=button_font_size),
                fg_color='transparent',
                bg_color='transparent',
                command=lambda _oss_name=oss_name: self.forward_to_detail(oss_name=_oss_name)
            )
            self.buttons[oss_name].pack(pady=10)

    def forward_to_detail(self, oss_name: str) -> None:
        # OSSライセンスリストを非表示化
        self.place_forget()

        # OSSライセンス詳細ビューを作成して表示
        self._master.switch_to_license_detail(oss_name=oss_name)

        # OSSライセンスリストを破棄
        self.destroy()

# OSSライセンスビューのコンポーネント
class OSSLicenseView(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    licenses: dict[str, str] = dict[str, str]() # OSSの名前とそのライセンス情報の辞書
    view: OSSLicenseList | OSSLicenseDetail
    def __init__(self, master: MainView, root_dir: str, width: int, height: int) -> None:
        super(OSSLicenseView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # ライセンス情報の読み込み
        self._load_licenses(root_dir=root_dir)

        # 初期表示はライセンスリスト
        self.switch_to_license_list()

    # ライセンスリストビューに切り替え
    def switch_to_license_list(self) -> None:
        # OSSライセンスリストビューを作成して表示
        self.view = OSSLicenseList(master=self, root_dir=self.root_dir, width=int(self.width * 0.8), height=int(self.height * 0.8))
        self.view.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # OSSライセンスビューの更新
        self.update_idletasks()

    # ライセンス詳細ビューに切り替え
    def switch_to_license_detail(self, oss_name: str) -> None:
        # OSSライセンス詳細ビューを作成して表示
        self.view = OSSLicenseDetail(master=self, root_dir=self.root_dir, oss_name=oss_name)
        self.view.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # OSSライセンスビューの更新
        self.update_idletasks()

    # ライセンス情報の読み込み
    def _load_licenses(self, root_dir: str) -> None:
        for oss in os.listdir(f'{root_dir}/assets/licenses'):
            # ファイルでなければスキップ
            if not os.path.isfile(f'{root_dir}/assets/licenses/{oss}'):
                continue

            # ライセンス情報の読み込み
            oss_name: str = oss.replace('LICENSE_', '').replace('--', '<escape hyphen>').replace('-', ' ').replace('<escape hyphen>', '-') # 例: 'LICENSE_Google-Material-Symbols-and-Icons' -> 'Google Material Symbols and Icons'
            with open(f'{root_dir}/assets/licenses/{oss}', 'r', encoding='utf-8') as f:
                self.licenses[oss_name] = f.read()