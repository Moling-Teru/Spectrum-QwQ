import tkinter as tk
from tkinter import ttk, messagebox
import os
import soundfile as sf
import librosa
import datetime
import threading
import queue
import stft_unified_time

# 创建一个队列用于线程间通信
log_queue = queue.Queue()

class AudioClipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音频截取与STFT分析")
        self.root.geometry("600x500")

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 音频文件选择
        ttk.Label(main_frame, text="选择音频文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.audio_var = tk.StringVar()
        self.audio_combo = ttk.Combobox(main_frame, textvariable=self.audio_var, state="readonly", width=50)
        self.audio_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.audio_combo.bind('<<ComboboxSelected>>', self.on_audio_selected)

        # 刷新按钮
        ttk.Button(main_frame, text="刷新列表", command=self.refresh_audio_list).grid(row=0, column=2, padx=(10, 0), pady=5)

        # 音频信息显示
        ttk.Label(main_frame, text="音频总时长:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration_label = ttk.Label(main_frame, text="未选择文件", foreground="blue")
        self.duration_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 开始时间输入
        ttk.Label(main_frame, text="开始时间 (秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_time_var = tk.StringVar(value="0")
        start_time_entry = ttk.Entry(main_frame, textvariable=self.start_time_var, width=20)
        start_time_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 结束时间输入
        ttk.Label(main_frame, text="结束时间 (秒):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.end_time_var = tk.StringVar()
        end_time_entry = ttk.Entry(main_frame, textvariable=self.end_time_var, width=20)
        end_time_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 处理按钮
        self.process_button = ttk.Button(main_frame, text="开始处理", command=self.start_processing, state="disabled")
        self.process_button.grid(row=4, column=1, pady=20, sticky=tk.W, padx=(10, 0))

        # 进度条
        ttk.Label(main_frame, text="处理进度:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # 日志显示区域
        ttk.Label(main_frame, text="处理日志:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=(20, 5))

        # 创建日志文本框和滚动条
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0), padx=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 配置主框架的行权重，使日志区域可以扩展
        main_frame.rowconfigure(6, weight=1)

        # 初始化
        self.audio_duration = 0
        self.refresh_audio_list()

        # 开始日志更新线程
        self.update_log()

    def refresh_audio_list(self):
        """刷新音频文件列表"""
        music_dir = "music_stft"
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            self.log_message("创建了music_stft目录")

        wav_files = [f for f in os.listdir(music_dir) if f.lower().endswith('.wav')]
        self.audio_combo['values'] = wav_files

        if wav_files:
            self.log_message(f"找到 {len(wav_files)} 个WAV文件")
        else:
            self.log_message("music_stft目录中没有找到WAV文件")

    def on_audio_selected(self, event=None):
        """当选择音频文件时触发"""
        selected_file = self.audio_var.get()
        if selected_file:
            file_path = os.path.join("music_stft", selected_file)
            try:
                # 获取音频时长
                self.audio_duration = librosa.get_duration(path=file_path)
                self.duration_label.config(text=f"{self.audio_duration:.2f} 秒")

                # 设置默认结束时间为音频总时长
                self.end_time_var.set(str(self.audio_duration))

                # 启用处理按钮
                self.process_button.config(state="normal")

                self.log_message(f"选择文件: {selected_file} (时长: {self.audio_duration:.2f}秒)")

            except Exception as e:
                self.log_message(f"读取音频文件失败: {str(e)}")
                self.duration_label.config(text="读取失败")
                self.process_button.config(state="disabled")

    def validate_time_inputs(self):
        """验证时间输入"""
        try:
            start_time = float(self.start_time_var.get())
            end_time = float(self.end_time_var.get())

            if start_time < 0:
                messagebox.showerror("错误", "开始时间不能为负数")
                return False

            if end_time <= start_time:
                messagebox.showerror("错误", "结束时间必须大于开始时间")
                return False

            if end_time > self.audio_duration:
                messagebox.showerror("错误", f"结束时间不能超过音频总时长 ({self.audio_duration:.2f}秒)")
                return False

            return True, start_time, end_time

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return False

    @staticmethod
    def log_message(message):
        """添加日志消息到队列"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_queue.put(f"[{timestamp}] {message}\n")

    def update_log(self):
        """更新日志显示"""
        try:
            while True:
                message = log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass

        # 继续检查日志更新
        self.root.after(100, self.update_log)

    def start_processing(self):
        """开始处理按钮点击事件"""
        validation_result = self.validate_time_inputs()
        if not validation_result:
            return

        _, start_time, end_time = validation_result

        # 禁用处理按钮，开始进度条
        self.process_button.config(state="disabled")
        self.progress.start()

        # 在新线程中执行处理
        processing_thread = threading.Thread(
            target=self.process_audio,
            args=(start_time, end_time),
            daemon=True
        )
        processing_thread.start()

    def process_audio(self, start_time, end_time):
        """在后台线程中处理音频"""
        try:
            selected_file = self.audio_var.get()
            input_path = os.path.join("music_stft", selected_file)

            # 创建输出目录名称
            base_name = os.path.splitext(selected_file)[0]
            time_range = f"{start_time:.1f}-{end_time:.1f}s"
            output_dir_name = f"{base_name}-{time_range}"
            output_dir = os.path.join("data_stft_time", output_dir_name)

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            self.log_message(f"开始处理: {selected_file}")
            self.log_message(f"时间范围: {start_time:.1f}s - {end_time:.1f}s")
            self.log_message(f"输出目录: {output_dir}")

            # 读取并截取音频
            self.log_message("正在读取音频文件...")
            audio, sr = sf.read(input_path)

            # 转换时间到样本索引
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)

            # 截取音频
            if audio.ndim > 1:
                clipped_audio = audio[start_sample:end_sample, :]
            else:
                clipped_audio = audio[start_sample:end_sample]

            # 保存截取的音频
            clipped_audio_path = os.path.join(output_dir, f"clipped_{base_name}_{time_range}.wav")
            sf.write(clipped_audio_path, clipped_audio, sr)
            self.log_message(f"已保存截取音频: {clipped_audio_path}")

            # 调用STFT处理
            self.log_message("开始STFT分析...")
            stft_unified_time.main(clipped_audio_path, output_dir)

            self.log_message("处理完成!")
            messagebox.showinfo("完成", f"音频处理完成!\n输出目录: {output_dir}")

        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("错误", error_msg)

        finally:
            # 恢复UI状态
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        """重置UI状态"""
        self.progress.stop()
        self.process_button.config(state="normal")

def main():
    root = tk.Tk()
    app = AudioClipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
