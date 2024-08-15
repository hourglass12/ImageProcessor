from threading import Thread
import tkinter as tk
from tkinter import ttk, filedialog, Canvas, Frame, Button, Scale, HORIZONTAL, OptionMenu, StringVar
from PIL import Image, ImageTk
import cv2
import os
import time
import numpy as np

ROOT = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(ROOT, "images")

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image and Video Processing Tool")
        self.processor = None
        self.original_image = None
        self.create_widget()
        self.video_capture = None
        self.current_frame = 0
        self.playing = False
        self.zoom_level = 1.0

        self.progress_window = None
        self.progress_var = None
        self.progress_bar = None

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

        # 再生・停止ボタン（デフォルトでは非表示）
        self.play_button = Button(self.edit_frame, text="再生▶", command=self.play_video)
        self.stop_button = Button(self.edit_frame, text="停止■", command=self.stop_video)
        
        # フレームレート選択ボタン（デフォルトでは非表示）
        self.fps_var = StringVar(value="30")
        self.fps_menu = OptionMenu(self.edit_frame, self.fps_var, "15", "30", "60")

        # フレーム選択用のスライダーを追加（デフォルトでは非表示）
        self.frame_slider = Scale(self.display_frame, from_=0, to=100, orient=HORIZONTAL, command=self.update_frame)

        # src/items/ディレクトリのスクリプトからボタンを動的に追加
        self.add_processing_buttons()

        self.save_as_button = Button(self.edit_frame, text="save as", command=self.save_as)
        self.save_as_button.pack()

        # マウスホイールでズーム機能
        self.canvas.bind("<MouseWheel>", self.zoom)

    def load_image_video(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image and Video Files", "*.jpg *.jpeg *.png *.mp4 *.avi")],
                                               initialdir=IMAGE_DIR)
        if not self.file_path:
            return

        if self.file_path.lower().endswith(('.mp4', '.avi')):
            self.load_video(self.file_path)
            # 動画時にのみ再生・停止ボタン、フレームレート選択、スライダーを表示
            self.play_button.pack(pady=10)
            self.stop_button.pack(pady=10)
            self.fps_menu.pack(pady=10)
            self.frame_slider.pack(fill=tk.X, pady=10)
        else:
            self.load_image(self.file_path)
            # 画像の場合は再生・停止ボタン、スライダーを非表示
            self.play_button.pack_forget()
            self.stop_button.pack_forget()
            self.fps_menu.pack_forget()
            self.frame_slider.pack_forget()

    def load_image(self, file_path):
        self.original_image = Image.open(file_path)
        if self.processor is not None:
            self.processor.set_image(self.original_image)
            self.processor.preprocess()
        self.display_image(self.original_image)

    def load_video(self, file_path):
        self.video_capture = cv2.VideoCapture(file_path)
        self.frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_slider.config(to=self.frame_count-1)
        self.current_frame = 0
        self.show_frame()

    def display_image(self, image):
        # キャンバスに収まるように画像をリサイズ（アスペクト比を維持）
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = image.size

        # アスペクト比を維持してサイズを調整
        scale = min(canvas_width / image_width, canvas_height / image_height)
        new_width = int(image_width * scale * self.zoom_level)
        new_height = int(image_height * scale * self.zoom_level)

        # 中心に配置するためのオフセット計算
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        # キャンバスをクリアし、背景を黒に設定
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='black')

        # 画像をキャンバスの中心に配置
        self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.tk_image)

    def show_frame(self):
        if self.video_capture is not None:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.original_image = Image.fromarray(frame)
                if self.processor is not None:
                    self.processor.set_image(self.original_image)
                    self.processor.preprocess()
                    self.image = self.processor.apply_process()
                else:
                    self.image = self.original_image.copy()
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
            fps = int(self.fps_var.get())
            delay = int(1000 / fps)
            self.root.after(delay, self.update_video)

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= 0.9
        if self.image:
            self.display_image(self.image)

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
        self.processor = module_class(self)  # 処理モジュールのクラスを初期化
        if self.original_image is not None:
            self.processor.set_image(self.original_image)
            self.processor.preprocess()

    def update_image(self, updated_image):
        self.display_image(updated_image)

    def save_as(self):
        if self.processor:
            if self.file_path.lower().endswith(('.mp4', '.avi')):
                self.save_video_as()
            else:
                self.save_image_as()

    def save_video_as(self):
        output_video_path = filedialog.asksaveasfilename(initialdir=IMAGE_DIR,
                                                            initialfile=f"{os.path.splitext(os.path.basename(self.file_path))[0]}_processed",
                                                            defaultextension=".mp4",  # デフォルトの拡張子
                                                            filetypes=[
                                                                ("MP4 files", "*.mp4"),
                                                                ("AVI files", "*.avi"),
                                                                ("MOV files", "*.mov"),
                                                                ("All files", "*.*"),
                                                            ]
            )
        if output_video_path:
            # プログレスバーのウィンドウを作成
            self.progress_window = ProgressWindow(self.root)

            # 別スレッドで動画処理を実行
            processing_thread = Thread(target=self._process_on_frames, args=(output_video_path, ))
            processing_thread.start()
        

    def _process_on_frames(self, output_video_path):
        # 動画のプロパティを取得
        width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 出力フォーマットを指定

        # 動画の書き込み準備
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height), isColor=True)
        
        self.progress_window.start_timer()
        
        for i in range(total_frames):
            ret, frame = self.video_capture.read()
            if not ret:
                break

            # フレームに画像処理を施す
            self.processor.set_image(Image.fromarray(frame))
            processed_frame = np.array(self.processor.apply_process())
            # 処理後のフレームを出力動画に書き込み
            out.write(processed_frame)

            # プログレスバーの更新
            self.progress_window.update_progress(i + 1, total_frames)

        # リソースを解放
        #self.video_capture.release()
        out.release()
        self.progress_window.show_complete()

    def save_image_as(self):
        output_image_path = filedialog.asksaveasfilename(initialdir=IMAGE_DIR,
                                                            initialfile=f"{os.path.splitext(os.path.basename(self.file_path))[0]}_processed{os.path.splitext(os.path.basename(self.file_path))[1]}",
            )
        processed_image = np.array(self.processor.apply_process())
        cv2.imwrite(output_image_path, processed_image)

class ProgressWindow:
    def __init__(self, root, title="Processing Progress"):
        self.root = root
        self.start_time = None

        # 新しいウィンドウを作成
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title(title)

        # プログレスバーを作成
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_window, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(padx=20, pady=10, fill=tk.X)

        # 経過時間と予想残り時間を表示するラベル
        self.elapsed_time_label = tk.Label(self.progress_window, text="Elapsed Time: 0s")
        self.elapsed_time_label.pack(pady=5)

        self.estimated_time_label = tk.Label(self.progress_window, text="Estimated Remaining Time: 0s")
        self.estimated_time_label.pack(pady=5)

        # 現在のフレーム番号とトータルフレーム数を表示するラベル
        self.current_frame_label = tk.Label(self.progress_window, text="Frame: 0/0")
        self.current_frame_label.pack(pady=5)

        # 1フレーム当たりの平均処理時間を表示するラベル
        self.avg_time_per_frame_label = tk.Label(self.progress_window, text="Avg. Time per Frame: 0s")
        self.avg_time_per_frame_label.pack(pady=5)

        # 終了を示すラベル
        self.complete_label = tk.Label(self.progress_window, text="")
        self.complete_label.pack(pady=5)

    def start_timer(self):
        self.start_time = time.time()

    def update_progress(self, current_frame, total_frames):
        elapsed_time = time.time() - self.start_time
        avg_time_per_frame = elapsed_time / current_frame
        remaining_time = avg_time_per_frame * (total_frames - current_frame)

        # プログレスバーとラベルを更新
        self.progress_var.set((current_frame / total_frames) * 100)
        self.elapsed_time_label.config(text=f"Elapsed Time: {int(elapsed_time)}s")
        self.estimated_time_label.config(text=f"Estimated Remaining Time: {int(remaining_time)}s")
        self.current_frame_label.config(text=f"Frame: {current_frame}/{total_frames}")
        self.avg_time_per_frame_label.config(text=f"Avg. Time per Frame: {avg_time_per_frame:.2f}s")

        self.root.update_idletasks()

    def close(self):
        self.progress_window.destroy()

    def show_complete(self):
        self.complete_label.config(text=f"Process complete")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
