import os
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QPushButton, QProgressBar, QMessageBox, QVBoxLayout, QWidget, QTextEdit, QComboBox, QHBoxLayout
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt, QThread, Signal
from qt_material import apply_stylesheet
from opencc import OpenCC

# 定義 Worker 類
class Worker(QThread):
    progress_updated = Signal(int)
    finished = Signal()
    progress_message_updated = Signal(str)  # 新增進度訊息更新的信號
    progress_percentage_updated = Signal(int)  # 新增進度百分比更新的信號

    def __init__(self, directory, file_extensions):
        super().__init__()
        self.directory = directory
        self.file_extensions = file_extensions
        self.cc = OpenCC('s2twp')  # 初始設置為台灣化

    def run(self):
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

            # 將檔案內容進行轉換
            converted_content = self.cc.convert(content)

            # 替換 lang 屬性的值
            converted_content = re.sub(r'lang="zh-CN"', 'lang="zh-TW"', converted_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)

            processed_files += 1
            self.progress_updated.emit(processed_files * 100 // pending_total_files)
            self.progress_percentage_updated.emit(processed_files * 100 // pending_total_files)  # 發送進度百分比更新的信號
            self.progress_message_updated.emit(f"路徑檔案總數: {total_files} 待處理檔案進度: ({str(processed_files).zfill(len(str(pending_total_files)))} / {pending_total_files}) {os.path.relpath(file_path, self.directory)}")  # 發射進度訊息更新的信號
            if processed_files == pending_total_files:
                self.progress_message_updated.emit("所有檔案轉換完成！")

# 在ConverterApp類中新增一個方法以設置UI佈局
class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("簡繁轉換工具")
        self.setGeometry(0, 0, 500, 200)

        self.directory_path = ""
        self.file_extensions = []

        # 創建一個垂直佈局
        layout = QVBoxLayout()

        # 將選擇資料夾標籤和路徑標籤放在一起
        self.label = QLabel("選擇資料夾:", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 將路徑標籤放在選擇資料夾標籤的旁邊
        self.directory_layout = QHBoxLayout()
        self.directory_label = QLabel(self)
        self.directory_label.setAlignment(Qt.AlignCenter)
        self.directory_layout.addWidget(self.directory_label)

        # 將瀏覽按鈕移到路徑標籤的旁邊
        self.browse_button = QPushButton("📁" + " 請選擇路徑", self)
        self.browse_button.setStyleSheet("border: 2px solid #E5446D; background: rgba(229,68,109, 0.2); color: #E5446D;")
        self.directory_layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.select_directory)

        layout.addLayout(self.directory_layout)

        # 添加多行文本框以接收使用者輸入的檔案副檔名
        self.extension_input = QTextEdit(self)
        self.extension_input.setPlaceholderText("輸入檔案副檔名，請以【空格】【換行】或【,】區分\n\n(例如：html, js, css, yaml, text） 副檔名前可選擇不加【.】")
        self.extension_input.setStyleSheet("border: 2px solid #E5446D;  color: #FFFFFF;")
        layout.addWidget(self.extension_input)

        # 將開始轉換按鈕放在副檔名輸入框旁邊
        self.button_layout = QHBoxLayout()
        self.convert_button = QPushButton("❌請先選擇路徑❌", self)
        self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
        self.button_layout.addWidget(self.convert_button)
        self.convert_button.clicked.connect(self.start_conversion)

        # 添加下拉選單和字體標籤
        self.convert_format_combo_box = QComboBox(self)
        self.convert_format_combo_box.addItem("台灣化 (s2twp)")
        self.convert_format_combo_box.addItem("中國化 (tw2sp)")
        self.convert_format_combo_box.addItem("繁體化 (s2tw)")
        self.convert_format_combo_box.addItem("簡體化 (tw2s)")
        self.convert_format_combo_box.setStyleSheet("border: 2px solid #43C59E; color: #43C59E; border-radius: 4px")
        self.button_layout.addWidget(self.convert_format_combo_box)

        layout.addLayout(self.button_layout)

        # 將進度條和處理中的內容放在一起
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        self.progress_bar.setStyleSheet("border-radius: 4px")

        # 創建 QTextEdit 來顯示處理中的內容
        self.processing_text_edit = QTextEdit(self)
        layout.addWidget(self.processing_text_edit)
        self.processing_text_edit.setReadOnly(True)  # 將文本編輯框設置為只讀模式
        self.processing_text_edit.setPlaceholderText("輸出運行結果的地方. . .")
        self.processing_text_edit.setStyleSheet("border: 2px solid #4f5b62; color: #43C59E; border-radius: 4px")

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

        # 創建一個狀態列
        self.statusBar().showMessage('Ready')

        # 創建 Worker 實例時將 processing_text_edit 作為參數傳遞給它
        self.worker = Worker("", [])
        self.worker.progress_updated.connect(self.update_progress_bar)
        self.worker.progress_message_updated.connect(self.update_processing_text_edit)  # 連接進度訊息更新的信號
        self.worker.progress_percentage_updated.connect(self.update_status_bar)  # 連接進度百分比更新的信號
        self.worker.finished.connect(self.show_message_box)

        self.center()

        # 監聽附檔名輸入框的變化
        self.extension_input.textChanged.connect(self.update_button_ststus_style)

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

    def extensions_input_changed(self):
        # 修改副檔名處理
        extensions = self.extension_input.toPlainText().replace(".", "").replace(",", " ").split()  # 去除"."後再分割
        extensions = [f".{ext}" for ext in extensions]  # 在每個副檔名前面加上"."
        return extensions
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "選擇資料夾")

        if directory:
            self.directory_path = directory
            self.directory_label.setText(directory)
            self.worker.directory = directory
            self.extensions_input_changed()  # 檢查副檔名輸入框是否有值

            # 更新 browse_button 樣式，包括透明度
            self.browse_button.setText("📁" + " 可變更路徑")
            self.browse_button.setStyleSheet("border: 2px solid #43C59E; background: rgba(67, 197, 158, 0.2); color: #43C59E;")
            self.update_button_ststus_style()  # 檢查路徑是否有值並更新按鈕狀態

    def update_button_ststus_style(self):
        # 監聽副檔名輸入框的變化
        # extensions = self.extension_input.toPlainText().replace(".", "").replace(",", " ").split()  # 去除"."後再分割
        # extensions = [f".{ext}" for ext in extensions]  # 在每個副檔名前面加上"."
        extensions = self.extensions_input_changed()
        # DEBUG: 顯示副檔名輸入框內容
        print("附檔名輸入框內容:", extensions)
        if self.directory_path and extensions:
            self.convert_button.setText("✔️ 開始轉換 ✔️")
            self.convert_button.setStyleSheet("border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;")
            self.extension_input.setStyleSheet("border: 2px solid #43C59E; color: #FFFFFF;")
        elif extensions != []:
            self.convert_button.setText("❌請先選擇路徑❌")
            self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
            self.extension_input.setStyleSheet("border: 2px solid #43C59E; color: #FFFFFF;")
        elif self.directory_path:
            self.convert_button.setText("❌請輸入副檔名❌")
            self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
            self.extension_input.setStyleSheet("border: 2px solid #E5446D;  color: #FFFFFF;")
        else:
            self.convert_button.setText("❌請選擇路徑❌")
            self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
            self.extension_input.setStyleSheet("border: 2px solid #E5446D;  color: #FFFFFF;")

    def start_conversion(self):
        if not self.directory_path:  # 檢查是否選擇了資料夾
            QMessageBox.warning(self, "警告", "請選擇資料夾！")
            return
        
        if not self.extensions_input_changed():  # 檢查是否輸入了副檔名
            QMessageBox.warning(self, "警告", "請輸入檔案副檔名！")
            return

        # 如果路徑和副檔名都已獲取，則開始轉換
        selected_format = self.convert_format_combo_box.currentText()
        if selected_format == "繁體化 (s2tw)":
            convert_format = 's2tw'
        elif selected_format == "簡體化 (tw2s)":
            convert_format = 'tw2s'
        elif selected_format == "台灣化 (s2twp)":
            convert_format = 's2twp'
        elif selected_format == "中國化 (tw2sp)":
            convert_format = 'tw2sp'

        self.worker.cc = OpenCC(convert_format)
        self.worker.file_extensions = self.extensions_input_changed()  # 將副檔名列表傳遞給 Worker
        self.worker.start()

    # 定義更新編輯區域內容的槽函式
    def update_processing_text_edit(self, progress_message):
        self.processing_text_edit.clear()
        self.processing_text_edit.append(progress_message)
    
    # 定義更新狀態列內容的槽函式
    def update_status_bar(self, progress_percentage):
        self.statusBar().showMessage(f"轉換進度: {progress_percentage}%")

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
