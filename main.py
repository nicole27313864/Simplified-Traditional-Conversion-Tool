import os
import re
from opencc import OpenCC
from tkinter import Tk, filedialog, StringVar
from tkinter import ttk
import threading
from tkinter import messagebox

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
                print("正在處理檔案:", file_path)
    print("轉換完成！")
    update_progress_bar(total_files, total_files)  # 將進度條設置為100%
    messagebox.showinfo("完成", "檔案處理完成！")

def update_progress_bar(processed_files, total_files):
    progress = round((processed_files / total_files) * 100)
    progress_bar['value'] = progress
    root.update()  # 強制刷新 UI 界面

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_path.set(directory)
        threading.Thread(target=convert_files_in_directory, args=(directory,)).start()

root = Tk()
root.title("簡繁轉換工具")

directory_path = StringVar()

label = ttk.Label(root, text="選擇資料夾:")
label.grid(row=0, column=0, padx=5, pady=5)

directory_entry = ttk.Entry(root, textvariable=directory_path, width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = ttk.Button(root, text="瀏覽", command=select_directory)
browse_button.grid(row=0, column=2, padx=5, pady=5)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
