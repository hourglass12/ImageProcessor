import tkinter as tk
from tkinter import Toplevel, IntVar, HORIZONTAL
from tkinter.ttk import Scale, Radiobutton, Label
from PIL import ImageFilter, ImageEnhance

class SharpeningWindow:
    def __init__(self, main_app):
        self.window = Toplevel()
        self.window.title("Sharpening Filter")
        self.original_image = None
        self.image = None
        self.main_app = main_app

        # 先鋭化のオン/オフを管理する変数
        self.sharpen_var = IntVar(value=0)  # 0: Off, 1: On

        # 先鋭化オン/オフのラジオボタン
        self.radio_off = Radiobutton(self.window, text="Off", variable=self.sharpen_var, value=0, command=self.toggle_sharpen)
        self.radio_off.pack(anchor=tk.W)

        self.radio_on = Radiobutton(self.window, text="On", variable=self.sharpen_var, value=1, command=self.toggle_sharpen)
        self.radio_on.pack(anchor=tk.W)

        # 先鋭化の強度（k値）を調整するスライダー
        self.k_value = tk.DoubleVar()
        self.scale = Scale(self.window, from_=0, to=5, orient=HORIZONTAL, variable=self.k_value, command=self.func_k_scale)
        self.scale.pack(fill=tk.X)

        self.k_value_label = Label(self.window, text=self.scale.get())
        self.k_value_label.pack(fill=tk.X)

        # UIの初期化
        #self.toggle_sharpen()

    def func_k_scale(self, k):
        self.adjust_sharpen(k)
        self.show_k_value()

    def show_k_value(self):
        self.k_value_label["text"] = self.scale.get()

    def adjust_sharpen(self, k):
        if self.sharpen_var.get() == 1:
            k = float(k)
            self.image = self.apply_sharpen(k)
            self.main_app.update_image(self.image)

    def toggle_sharpen(self):
        if self.sharpen_var.get() == 1:
            self.adjust_sharpen(self.scale.get())
        else:
            self.image = self.original_image.copy()
            self.main_app.update_image(self.image)

    def apply_sharpen(self, k):
        enhancer = ImageEnhance.Sharpness(self.original_image)
        sharpened_image = enhancer.enhance(k)
        return sharpened_image

    def set_image(self, image_pil):
        self.original_image = image_pil.copy()
        self.image = image_pil.copy()

    def preprocess(self):
        pass

    def apply_process(self):
        if self.sharpen_var.get() == 1:
            k = float(self.scale.get())
            self.image = self.apply_sharpen(k)
        else:
            self.image = self.original_image.copy()
        return self.image


