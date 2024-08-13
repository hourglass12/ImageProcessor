import tkinter as tk
from tkinter import filedialog, Canvas, Frame, Button, Scale, HORIZONTAL
from PIL import Image, ImageTk
import cv2
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(ROOT, "images")

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image and Video Processing Tool")
        self.create_widget()
        self.video_capture = None
        self.current_frame = 0
        self.playing = False

    def create_widget(self):
        # 左側の編集フレームを作成
        self.edit_frame = Frame(self.root, width=200, height=600, bg='lightgray')
        self.edit_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 右側の表示フレームを作成
        self.display_frame = Frame(self.root, width=600, height=600)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 画像・映像表示用のキャンバスを作成
        self.canvas = Canvas(self.display_frame, width=600, height=600, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 入力ボタンを編集フレームに追加
        input_button = Button(self.edit_frame, text="入力", command=self.load_image_video)
        input_button.pack(pady=10)

        # 再生・停止ボタンの追加
        self.play_button = Button(self.edit_frame, text="再生▶", command=self.play_video)
        self.play_button.pack(pady=10)
        self.stop_button = Button(self.edit_frame, text="停止■", command=self.stop_video)
        self.stop_button.pack(pady=10)

        # フレーム選択用のスライダーを追加
        self.frame_slider = Scale(self.display_frame, from_=0, to=100, orient=HORIZONTAL, command=self.update_frame)
        self.frame_slider.pack(fill=tk.X, pady=10)

        # src/items/ディレクトリのスクリプトからボタンを動的に追加
        self.add_processing_buttons()

    def load_image_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image and Video Files", "*.jpg *.jpeg *.png *.mp4 *.avi")],
                                               initialdir=IMAGE_DIR)
        if not file_path:
            return

        if file_path.lower().endswith(('.mp4', '.avi')):
            self.load_video(file_path)
        else:
            self.load_image(file_path)

    def load_image(self, file_path):
        self.image = Image.open(file_path)
        self.display_image(self.image)

    def load_video(self, file_path):
        # 動画をロードして最初のフレームを表示
        self.video_capture = cv2.VideoCapture(file_path)
        self.frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_slider.config(to=self.frame_count-1)
        self.current_frame = 0
        self.show_frame()

    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def show_frame(self):
        if self.video_capture is not None:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.image = Image.fromarray(frame)
                self.display_image(self.image)

    def update_frame(self, event=None):
        if not self.playing:
            self.current_frame = self.frame_slider.get()
            self.show_frame()

    def play_video(self):
        if not self.playing:
            self.playing = True
            self.update_video()

    def stop_video(self):
        self.playing = False

    def update_video(self):
        if self.playing and self.video_capture is not None:
            self.show_frame()
            self.current_frame += 1
            if self.current_frame >= self.frame_count:
                self.current_frame = 0
            self.frame_slider.set(self.current_frame)
            self.root.after(33, self.update_video)  # 約30fpsで再生

    def add_processing_buttons(self):
        items_dir = os.path.join(os.path.dirname(__file__), "items")
        if not os.path.exists(items_dir):
            return

        for module_name in os.listdir(items_dir):
            if module_name.endswith(".py") and module_name != "__init__.py":
                button_name = module_name.replace(".py", "")
                button = Button(self.edit_frame, text=button_name.capitalize(), command=lambda m=button_name: self.load_processing_module(m))
                button.pack(pady=5)

    def load_processing_module(self, module_name):
        module = __import__(f"items.{module_name}", fromlist=[module_name.capitalize()])
        module_class = getattr(module, module_name.capitalize() + "Window")
        module_class(self.image, self)  # 処理モジュールのクラスを初期化

    def update_image(self, updated_image):
        self.display_image(updated_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
