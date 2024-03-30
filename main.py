from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QPushButton, QProgressBar, QMessageBox, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QThread, Signal
from qt_material import apply_stylesheet
import os
import re
from opencc import OpenCC

# 定義 Worker 類
class Worker(QThread):
    progress_updated = Signal(int)
    finished = Signal()

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

# 在ConverterApp類中新增一個方法以設置UI佈局
class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("簡繁轉換工具")
        self.setGeometry(100, 100, 400, 150)

        self.directory_path = ""

        # 創建一個垂直佈局
        layout = QVBoxLayout()

        # 將選擇資料夾標籤添加到佈局中，並設置對齊方式為中心
        self.label = QLabel("選擇資料夾:", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 將路徑標籤添加到佈局中，並設置對齊方式為中心
        self.directory_label = QLabel(self)
        self.directory_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.directory_label)

        # 將瀏覽按鈕添加到佈局中
        self.browse_button = QPushButton("瀏覽", self)
        layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.select_directory)

        # 將開始轉換按鈕添加到佈局中
        self.convert_button = QPushButton("開始轉換", self)
        layout.addWidget(self.convert_button)
        self.convert_button.clicked.connect(self.start_conversion)

        # 將進度條添加到佈局中
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # 創建一個widget並將佈局設置為其主佈局
        widget = QWidget()
        widget.setLayout(layout)

        # 將widget設置為中心窗口的主widget
        self.setCentralWidget(widget)

        self.worker = Worker("")
        self.worker.progress_updated.connect(self.update_progress_bar)
        self.worker.finished.connect(self.show_message_box)

        self.center()

    def center(self):
        # 取得第一個螢幕
        screen = QApplication.primaryScreen().geometry()
        # 取得視窗尺寸
        size = self.geometry()
        # 計算中心位置
        self.move((screen.width() - size.width()) // 2, screen.height() * 0.40 - size.height() // 2)

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

    def start_conversion(self):
        if self.directory_path:
            self.worker.start()
        else:
            QMessageBox.warning(self, "警告", "請先選擇資料夾！")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # 設置 Qt Material 主題樣式
    apply_stylesheet(app, theme='dark_pink.xml')

    converter_app = ConverterApp()
    converter_app.show()

    sys.exit(app.exec())
