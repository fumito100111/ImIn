from __future__ import annotations
import os
import customtkinter as ctk
from src.app import App

def main() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    ctk.set_appearance_mode('Dark')
    ctk.set_default_color_theme(f'{root_dir}/color.json')
    app: App = App(root_dir=root_dir)
    app.run()

if __name__ == '__main__':
    main()