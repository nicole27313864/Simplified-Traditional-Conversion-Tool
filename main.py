import os
import re
from opencc import OpenCC
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QPushButton, QProgressBar, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class Worker(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        cc = OpenCC('s2twp')
        total_files = sum(len(files) for _, _, files in os.walk(self.directory))
        files_to_convert = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(('.html', '.css', '.js', '.yaml')):
                    files_to_convert.append(os.path.join(root, file))

        pending_total_files = len(files_to_convert)
        processed_files = 0
        for file_path in files_to_convert:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 將檔案內容從簡體字轉換為繁體字
            converted_content = cc.convert(content)

            # 替換 lang 屬性的值
            converted_content = re.sub(r'lang="zh-CN"', 'lang="zh-TW"', converted_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)

            processed_files += 1
            self.progress_updated.emit(processed_files * 100 // pending_total_files)
            print(f"路徑檔案總數: {total_files} 待處裡檔案進度: ({str(processed_files).zfill(len(str(pending_total_files)))} / {pending_total_files}) {os.path.relpath(file_path, self.directory)}")


        print("轉換完成！")
        self.finished.emit()

class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("簡繁轉換工具")
        self.setGeometry(100, 100, 400, 150)

        self.directory_path = ""

        self.label = QLabel("選擇資料夾:", self)
        self.label.move(20, 20)

        self.directory_label = QLabel(self)
        self.directory_label.setGeometry(120, 20, 250, 25)

        self.browse_button = QPushButton("瀏覽", self)
        self.browse_button.setGeometry(300, 20, 80, 25)
        self.browse_button.clicked.connect(self.select_directory)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(20, 60, 360, 25)

        self.worker = Worker("")
        self.worker.progress_updated.connect(self.update_progress_bar)
        self.worker.finished.connect(self.show_message_box)

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)

    def show_message_box(self):
        QMessageBox.information(self, "轉換完成", "所有檔案轉換完成！")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if directory:
            self.directory_path = directory
            self.directory_label.setText(directory)
            self.worker.directory = directory
            self.worker.start()

if __name__ == "__main__":
    app = QApplication([])
    converter_app = ConverterApp()
    converter_app.show()
    app.exec()
