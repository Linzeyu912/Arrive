"""Double-click launcher: owns only the child processes it starts."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
from urllib.request import build_opener, ProxyHandler
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend' / 'src'))
from arrive.config import Settings, data_path, prepare_data_directory
from filelock import FileLock, Timeout

URL = 'http://127.0.0.1:5173'


class Services:
    def __init__(self):
        self.root = prepare_data_directory(Settings().data_dir)
        self.lock = FileLock(str(data_path(self.root, 'cache/desktop-launcher.lock')), thread_local=False)
        self.processes = []
        self.logs = []
        self.stopping = threading.Event()
        self.log_dir = data_path(self.root, 'logs/launcher')
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        self.lock.acquire(timeout=0)
        try:
            python = ROOT / 'backend/.venv/Scripts/python.exe'
            vite = ROOT / 'frontend/node_modules/vite/bin/vite.js'
            node = shutil.which('node.exe') or shutil.which('node')
            if not python.is_file() or not vite.is_file() or not node:
                raise RuntimeError('缺少运行依赖，请先按 README 安装 Python 后端和前端依赖。')
            for port in (8000, 5173):
                with socket.socket() as probe:
                    if probe.connect_ex(('127.0.0.1', port)) == 0:
                        raise RuntimeError(f'端口 {port} 已被占用。请先关闭之前启动的服务，再重试。')
            env = os.environ.copy()
            env['ARRIVE_DATA_DIR'] = str(self.root)
            env['PYTHONIOENCODING'] = 'utf-8'
            commands = [
                ('backend', [str(python), '-m', 'uvicorn', 'arrive.main:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log'], ROOT),
                ('frontend', [node, str(vite), '--host', '127.0.0.1', '--port', '5173', '--strictPort'], ROOT / 'frontend'),
            ]
            for name, command, cwd in commands:
                log = data_path(self.root, f'logs/launcher/{name}.log').open('ab')
                self.logs.append(log)
                self.processes.append(subprocess.Popen(command, cwd=cwd, env=env,
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)))
            opener = build_opener(ProxyHandler({}))
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                if self.stopping.is_set():
                    raise RuntimeError('启动已取消。')
                if any(p.poll() is not None for p in self.processes):
                    raise RuntimeError('服务提前退出，请查看启动日志。')
                try:
                    with opener.open('http://127.0.0.1:8000/health', timeout=1) as response:
                        health = json.load(response)
                    with opener.open(URL, timeout=1) as response:
                        html = response.read(10000).decode('utf-8')
                    if health.get('service') == 'arrive-backend' and '/src/main.tsx' in html:
                        return
                except (OSError, ValueError):
                    pass
                self.stopping.wait(.3)
            raise RuntimeError('启动等待超时，请查看启动日志。')
        except BaseException:
            self.close()
            raise

    def close(self):
        self.stopping.set()
        # No PID files or port-wide kills: stop only this launcher's live children.
        for process in reversed(self.processes):
            if process.poll() is None:
                if os.name == 'nt':
                    # Windows venv redirectors can have a child interpreter.
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        for log in self.logs:
            log.close()
        self.lock.release()


def main():
    app = tk.Tk()
    app.title('抵达 · Arrive')
    app.geometry('440x245')
    app.resizable(False, False)
    app.configure(bg='#faf7f2')
    tk.Label(app, text='抵达 / Arrive', font=('Microsoft YaHei UI', 20), bg='#faf7f2').pack(pady=(22, 10))
    label = tk.Label(app, text='正在启动，请稍候…', font=('Microsoft YaHei UI', 11), bg='#faf7f2', wraplength=400)
    label.pack(pady=8)
    try:
        services = Services()
    except Exception as exc:
        messagebox.showerror('无法启动', str(exc), parent=app)
        app.destroy()
        return
    state = {'done': False, 'error': None, 'closing': False}
    open_button = tk.Button(app, text='打开 Arrive', command=lambda: webbrowser.open(URL), state='disabled', width=24)
    open_button.pack(pady=6)

    def close():
        if state['closing']:
            return
        state['closing'] = True
        label.config(text='正在停止服务…')
        open_button.config(state='disabled')
        services.stopping.set()
        def stop():
            thread.join()
            services.close()
            state['closed'] = True
        threading.Thread(target=stop, daemon=True).start()
        def wait():
            if state.get('closed'):
                app.destroy()
            else:
                app.after(100, wait)
        wait()

    tk.Button(app, text='停止并退出', command=close, width=24).pack(pady=4)
    app.protocol('WM_DELETE_WINDOW', close)

    def start():
        try:
            services.start()
        except Timeout:
            state['error'] = '已有一个 Arrive 启动器正在运行，请使用原来的窗口。'
        except Exception as exc:
            state['error'] = str(exc)
        finally:
            state['done'] = True
    thread = threading.Thread(target=start, daemon=True)
    thread.start()

    def refresh():
        if state['closing']:
            return
        if not state['done']:
            app.after(200, refresh)
        elif state['error']:
            label.config(text=state['error'])
            tk.Button(app, text='查看日志', command=lambda: os.startfile(services.log_dir)).pack()
        else:
            label.config(text='已启动，关闭此窗口会停止项目。')
            open_button.config(state='normal')
            webbrowser.open(URL)
    refresh()
    app.mainloop()


if __name__ == '__main__':
    main()
