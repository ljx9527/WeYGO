from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from .config import load_config
from .runner import request_stop, run_task
from .window_picker import apply_region_to_config, get_active_window_region


class WeYgoApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("WeYGO")
        self.geometry("560x420")
        self.minsize(520, 360)

        self.config_data = load_config()
        self.worker: threading.Thread | None = None
        self.events: queue.Queue[str] = queue.Queue()

        self.status_text = tk.StringVar(value="未选择游戏窗口")
        self.region_text = tk.StringVar(value="游戏窗口：未选择")
        self.task_text = tk.StringVar(value="NPC 自动决斗")
        self.execute_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.after(200, self._poll_events)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(root, text="WeYGO 自动任务", font=("Microsoft YaHei UI", 16, "bold"))
        header.pack(anchor=tk.W)

        ttk.Label(root, textvariable=self.status_text).pack(anchor=tk.W, pady=(6, 14))

        region_frame = ttk.LabelFrame(root, text="游戏窗口")
        region_frame.pack(fill=tk.X)

        ttk.Label(region_frame, textvariable=self.region_text).pack(anchor=tk.W, padx=10, pady=(10, 6))
        ttk.Button(region_frame, text="手动选中游戏窗口", command=self.pick_window).pack(
            anchor=tk.W, padx=10, pady=(0, 10)
        )

        task_frame = ttk.LabelFrame(root, text="任务")
        task_frame.pack(fill=tk.X, pady=12)

        ttk.Label(task_frame, textvariable=self.task_text).grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Checkbutton(task_frame, text="实际点击执行", variable=self.execute_var).grid(
            row=0, column=1, sticky=tk.W, padx=10, pady=10
        )
        task_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, pady=(4, 12))

        self.start_button = ttk.Button(button_frame, text="开始", command=self.start_task)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_task, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=8)

        ttk.Button(button_frame, text="退出", command=self.destroy).pack(side=tk.RIGHT)

        log_frame = ttk.LabelFrame(root, text="运行日志")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def pick_window(self) -> None:
        self._append_log("请在 3 秒内点击游戏窗口...")
        self.status_text.set("等待你点击游戏窗口")
        self.after(100, self._pick_window_after_delay)

    def _pick_window_after_delay(self) -> None:
        def worker() -> None:
            time.sleep(3)
            try:
                region = get_active_window_region()
                apply_region_to_config(self.config_data, region)
                self.events.put(
                    "REGION|"
                    f"{region.x},{region.y},{region.width},{region.height}|"
                    f"{region.source}"
                )
            except Exception as exc:
                self.events.put(f"ERROR|选择窗口失败：{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def start_task(self) -> None:
        if self.worker and self.worker.is_alive():
            return

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_text.set("任务运行中")
        self._append_log("开始 NPC 自动决斗任务")

        task_config = self.config_data
        execute = bool(self.execute_var.get())

        def worker() -> None:
            code = run_task(task_config, "npc-auto-duel", execute)
            self.events.put(f"DONE|{code}")

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()

    def stop_task(self) -> None:
        path = request_stop(self.config_data)
        self.status_text.set("已请求停止")
        self._append_log(f"已请求停止：{path}")

    def _poll_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break

            kind, _, payload = event.partition("|")
            if kind == "REGION":
                dims, _, source = payload.partition("|")
                self.region_text.set(f"游戏窗口：{dims}")
                self.status_text.set("游戏窗口已选择")
                self._append_log(f"已选中：{source} ({dims})")
            elif kind == "ERROR":
                self.status_text.set("发生错误")
                self._append_log(payload)
                messagebox.showerror("WeYGO", payload)
            elif kind == "DONE":
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.status_text.set("任务完成" if payload == "0" else f"任务结束：{payload}")
                self._append_log(f"任务结束，退出码：{payload}")

        self.after(200, self._poll_events)

    def _append_log(self, text: str) -> None:
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)


def main() -> None:
    app = WeYgoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
