import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import os
import re
from opencc import OpenCC
import threading

def convert_file(file_path):
    cc = OpenCC('s2twp')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 將檔案內容從簡體字轉換為繁體字
    converted_content = cc.convert(content)
    
    # 替換 lang 屬性的值
    converted_content = re.sub(r'lang="zh-CN"', 'lang="zh-TW"', converted_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(converted_content)

def convert_files_in_directory(directory):
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    processed_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.html', '.css', '.js', '.yaml')):
                file_path = os.path.join(root, file)
                convert_file(file_path)
                processed_files += 1
                update_progress_bar(processed_files, total_files)
    messagebox.showinfo("完成", "資料夾內所有檔案轉換完成！")

def update_progress_bar(processed_files, total_files):
    progress = int((processed_files / total_files) * 100)
    progress_bar['value'] = progress

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_path.set(directory)
        # 創建新的執行緒來執行耗時任務
        threading.Thread(target=convert_files_in_directory, args=(directory,)).start()

# 創建主視窗
root = tk.Tk()
root.title("簡繁體轉換")

# 資料夾路徑變數
directory_path = tk.StringVar()

# 資料夾路徑標籤
label = tk.Label(root, text="選擇資料夾路徑：")
label.pack()

# 顯示資料夾路徑
path_entry = tk.Entry(root, textvariable=directory_path, width=50)
path_entry.pack()

# 選擇資料夾按鈕
browse_button = tk.Button(root, text="瀏覽", command=choose_directory)
browse_button.pack()

# 進度條
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.pack()

# 啟動事件迴圈
root.mainloop()
