from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from PIL import Image, ImageDraw
if TYPE_CHECKING:
    from ..views import MainView

# アプリ説明文
APP_DESCRIPTION = '在室状況をSlack上で共有するためのデスクトップアプリケーションです.\n' \
                    'NFCタグを利用して在室状況を簡単に更新できます.'

# アプリ情報ビューのコンポーネント
class AppInfoView(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    icon_label: ctk.CTkLabel        # アプリアイコンラベル
    name_label: ctk.CTkLabel        # アプリ名ラベル
    description_label: ctk.CTkLabel # アプリ説明ラベル
    version_label: ctk.CTkLabel     # バージョンラベル
    website_button: ctk.CTkButton   # ウェブサイトボタン
    copyright_label: ctk.CTkLabel   # コピーライトラベル
    def __init__(self, master: MainView, root_dir: str, width: int, height: int) -> None:
        super(AppInfoView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # アプリ名 & バージョンを取得
        app_name: str = self.master.master.pyproject['project']['name']
        app_version: str = self.master.master.pyproject['project']['version']

        # コピーライトを取得
        with open(f'{self.root_dir}/LICENSE', 'r', encoding='utf-8') as f:
            copyright: str = ''
            for line in f.readlines():
                if line.startswith('Copyright (c)'):
                    copyright = line.strip().replace('Copyright (c)', '©')
                    break

        # アイコンラベルの作成 & 配置
        icon_label_width: int = int(self.height * 0.4)
        icon_label_height: int = icon_label_width
        icon_corner_radius: int = int(min(icon_label_width, icon_label_height) * 0.6)
        self.icon_label = ctk.CTkLabel(
            master=self,
            width=icon_label_width,
            height=icon_label_height,
            text='',
            image=ctk.CTkImage(
                light_image=self._round_icon_image(f'{self.root_dir}/assets/icons/app/icon.png', icon_corner_radius),
                dark_image=self._round_icon_image(f'{self.root_dir}/assets/icons/app/icon.png', icon_corner_radius),
                size=(icon_label_width, icon_label_height)
            ),
            fg_color='transparent',
            bg_color='transparent'
        )
        self.icon_label.place(relx=0.5, rely=0.1, anchor=ctk.N)

        # アプリ名ラベルの作成 & 配置
        name_label_width: int = int(self.width * 0.8)
        name_label_height: int = int(self.height * 0.05)
        name_label_font_size: int = int(min(name_label_width, name_label_height))
        self.name_label = ctk.CTkLabel(
            master=self,
            text=f'{app_name}',
            width=name_label_width,
            height=name_label_height,
            font=ctk.CTkFont(size=name_label_font_size, weight='bold'),
            fg_color='transparent',
            bg_color='transparent'
        )
        self.name_label.place(relx=0.5, rely=0.525, anchor=ctk.N)

        # アプリ説明ラベルの作成 & 配置
        description_label_width: int = int(self.width * 0.8)
        description_label_height: int = int(self.height * 0.03)
        description_label_font_size: int = int(min(description_label_width, description_label_height))
        self.description_label = ctk.CTkLabel(
            master=self,
            text=APP_DESCRIPTION,
            width=description_label_width,
            height=description_label_height,
            font=ctk.CTkFont(size=description_label_font_size),
            fg_color='transparent',
            bg_color='transparent'
        )
        self.description_label.place(relx=0.5, rely=0.625, anchor=ctk.N)

        # バージョンラベルの作成 & 配置
        version_label_width: int = int(self.width * 0.8)
        version_label_height: int = int(self.height * 0.025)
        version_label_font_size: int = int(min(version_label_width, version_label_height))
        self.version_label = ctk.CTkLabel(
            master=self,
            text=f'Version  {app_version}',
            width=version_label_width,
            height=version_label_height,
            font=ctk.CTkFont(size=version_label_font_size),
            fg_color='transparent',
            bg_color='transparent'
        )
        self.version_label.place(relx=0.5, rely=0.75, anchor=ctk.N)

        # ウェブサイトボタンの作成 & 配置
        # TODO: コマンドを設定 & アイコンのダウンロード (Google Fontsの「Open In New」アイコンを使用予定)
        # website_button_width: int = int(self.width * 0.15)
        # website_button_height: int = int(self.height * 0.04)
        # website_button_font_size: int = int(min(website_button_width, website_button_height) * 0.5)
        # self.website_button = ctk.CTkButton(
        #     master=self,
        #     text='公式Webサイト',
        #     width=website_button_width,
        #     height=website_button_height,
        #     font=ctk.CTkFont(size=website_button_font_size),
        #     image=ctk.CTkImage(
        #         light_image=Image.open(f'{self.root_dir}/assets/icons/light/open_in_new.png'),
        #         dark_image=Image.open(f'{self.root_dir}/assets/icons/dark/open_in_new.png'),
        #         size=(website_button_font_size, website_button_font_size)
        #     ),
        #     compound=ctk.RIGHT,
        #     command=None
        # )
        # self.website_button.place(relx=0.5, rely=0.825, anchor=ctk.N)

        # コピーライトラベルの作成 & 配置
        copyright_label_width: int = int(self.width * 0.45) # 左寄せした時の余白(0.05)を考慮
        copyright_label_height: int = int(self.height * 0.025)
        copyright_label_font_size: int = int(min(copyright_label_width, copyright_label_height))
        self.copyright_label = ctk.CTkLabel(
            master=self,
            text=copyright,
            width=copyright_label_width,
            height=copyright_label_height,
            font=ctk.CTkFont(size=copyright_label_font_size),
            anchor=ctk.SW,
            fg_color='transparent',
            bg_color='transparent'
        )
        self.copyright_label.place(relx=0.5, rely=0.95, anchor=ctk.SE)

    # アプリアイコン画像の角を丸くする
    def _round_icon_image(self, icon_path: str, corner_radius: int) -> Image.Image:
        # 元の画像を読み込む
        raw_image: Image.Image = Image.open(icon_path).convert('RGBA')
        width, height = raw_image.size

        # 角を丸くするためのマスクを作成
        rounded_mask = Image.new('L', (width, height), 0)
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(rounded_mask)
        draw.rounded_rectangle((0, 0, width, height), corner_radius, fill=255)

        # 元の画像にマスクを適用して角を丸くする
        rounded_image: Image.Image = Image.new('RGBA', (width, height))
        rounded_image.paste(raw_image, (0, 0), mask=rounded_mask)

        return rounded_image