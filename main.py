import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QPushButton, QProgressBar, QMessageBox, QVBoxLayout, QWidget, QTextEdit, QLineEdit
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt, QThread, Signal
from qt_material import apply_stylesheet
import re
from opencc import OpenCC

# 定義 Worker 類
class Worker(QThread):
    progress_updated = Signal(int)
    finished = Signal()
    progress_message_updated = Signal(str)  # 新增進度訊息更新的信號

    def __init__(self, directory, file_extensions):
        super().__init__()
        self.directory = directory
        self.file_extensions = file_extensions

    def run(self):
        cc = OpenCC('s2twp')
        total_files = sum(len(files) for _, _, files in os.walk(self.directory))
        files_to_convert = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(tuple(self.file_extensions)):  # 使用者輸入的副檔名
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
            # print(f"路徑檔案總數: {total_files} 待處理檔案進度: ({str(processed_files).zfill(len(str(pending_total_files)))} / {pending_total_files}) {os.path.relpath(file_path, self.directory)}")
            self.progress_message_updated.emit(f"路徑檔案總數: {total_files} 待處理檔案進度: ({str(processed_files).zfill(len(str(pending_total_files)))} / {pending_total_files}) {os.path.relpath(file_path, self.directory)}")  # 發射進度訊息更新的信號
            

        # self.finished.emit()  # 發送轉換完成的信號

# 在ConverterApp類中新增一個方法以設置UI佈局
class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("簡繁轉換工具")
        self.setGeometry(100, 100, 400, 200)

        self.directory_path = ""
        self.file_extensions = []

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
        self.browse_button = QPushButton("📁" + " 請選擇路徑", self)
        layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.select_directory)

        # 添加多行文本框以接收使用者輸入的檔案副檔名
        self.extension_input = QTextEdit(self)
        self.extension_input.setPlaceholderText("輸入檔案副檔名，每行一個（例如：.html）")
        layout.addWidget(self.extension_input)

        # 將開始轉換按鈕添加到佈局中，並設置樣式為綠色
        self.convert_button = QPushButton("❌請先選擇路徑❌", self)
        layout.addWidget(self.convert_button)
        self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
        self.convert_button.clicked.connect(self.start_conversion)

        # 將進度條添加到佈局中
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        
        # 設置進度條的樣式，包括圓角
        self.progress_bar.setStyleSheet("QProgressBar { border-radius: 4px; }")

        # 創建 QTextEdit 來顯示處理中的內容
        self.processing_text_edit = QTextEdit(self)
        layout.addWidget(self.processing_text_edit)

        # 創建字體標籤
        self.font_label = QLabel(self)
        self.font_label.setAlignment(Qt.AlignCenter)
        self.font_label.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
        layout.addWidget(self.font_label)

        # 將 layout 設置為成員變數
        self.layout = layout

        # 創建一個widget並將佈局設置為其主佈局
        widget = QWidget()
        widget.setLayout(layout)

        # 將widget設置為中心窗口的主widget
        self.setCentralWidget(widget)

        # 創建 Worker 實例時將 processing_text_edit 作為參數傳遞給它
        self.worker = Worker("", [])
        self.worker.progress_updated.connect(self.update_progress_bar)
        self.worker.progress_message_updated.connect(self.update_processing_text_edit)  # 連接進度訊息更新的信號
        self.worker.finished.connect(self.show_message_box)

        self.center()

        # 設置字體標籤的文字
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansTC-Regular.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.font_label.setText(f"目前使用的字體：{font_family}")
        else:
            print("Failed to load font")

    def center(self):
        # 取得第一個螢幕
        screen = QApplication.primaryScreen().geometry()
        # 取得視窗尺寸
        size = self.geometry()
        # 計算中心位置
        self.move((screen.width() - size.width()) // 2, screen.height() * 0.40 - size.height() // 2)

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { border-radius: 4px; border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;}")

    def show_message_box(self):
        QMessageBox.information(self, "轉換完成", "所有檔案轉換完成！")
        self.progress_bar.setValue(0)  # 轉換完成後將進度條歸0

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if directory:
            self.directory_path = directory
            self.directory_label.setText(directory)
            self.worker.directory = directory
            self.file_extensions = self.extension_input.toPlainText().split()  # 將多行文本分割成副檔名列表
            self.convert_button.setText("✔️" + " 開始轉換 " + "✔️")
            self.convert_button.setStyleSheet("border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;")
            
            # 更新 browse_button 樣式，包括透明度
            self.browse_button.setText("📁" + " 可變更路徑")
            self.browse_button.setStyleSheet("border: 2px solid #43C59E; background: rgba(67, 197, 158, 0.2); color: rgba(255, 255, 255, 0.5);")

    def start_conversion(self):
        if self.directory_path and self.file_extensions:  # 確保資料夾路徑和副檔名都已獲取
            self.worker.file_extensions = self.file_extensions  # 將副檔名列表傳遞給 Worker
            self.worker.start()
        else:
            QMessageBox.warning(self, "警告", "請先選擇資料夾並輸入檔案副檔名！")

    # 定義更新編輯區域內容的槽函式
    def update_processing_text_edit(self, progress_message):
        self.processing_text_edit.clear()
        self.processing_text_edit.append(progress_message)


if __name__ == "__main__":
    import sys

    # 啟動您的應用程式窗口
    app = QApplication(sys.argv)

    # 設置 Qt Material 自訂義 XML 文件路徑
    custom_theme_path = os.path.join(os.path.dirname(__file__), 'themes/dark.xml')

    # 檢查自訂主題文件是否存在
    if os.path.exists(custom_theme_path):
        # 應用自訂主題
        apply_stylesheet(app, theme=custom_theme_path)
    else:
        print("Custom theme file not found!")

    # 啟動您的應用程式窗口
    converter_app = ConverterApp()
    converter_app.show()

    # 運行應用程式
    sys.exit(app.exec())
