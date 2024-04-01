import os
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QPushButton, QProgressBar, QMessageBox, QVBoxLayout, QWidget, QTextEdit, QComboBox, QHBoxLayout
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtCore import Qt, QThread, Signal
from qt_material import apply_stylesheet
from opencc import OpenCC

class Worker(QThread):
    progress_updated = Signal(int)
    finished = Signal()
    progress_message_updated = Signal(str)
    progress_percentage_updated = Signal(int)
    text_converted = Signal(str)

    def __init__(self, directory, file_extensions):
        super().__init__()
        self.directory = directory
        self.file_extensions = file_extensions
        self.cc = OpenCC('s2twp')

    def run(self):
        total_files = sum(len(files) for _, _, files in os.walk(self.directory))
        files_to_convert = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(tuple(self.file_extensions)):
                    files_to_convert.append(os.path.join(root, file))

        pending_total_files = len(files_to_convert)
        processed_files = 0
        for file_path in files_to_convert:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            converted_content = self.cc.convert(content)
            converted_content = re.sub(r'lang="zh-CN"', 'lang="zh-TW"', converted_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)

            processed_files += 1
            self.progress_updated.emit(processed_files * 100 // pending_total_files)
            self.progress_percentage_updated.emit(processed_files * 100 // pending_total_files)
            self.progress_message_updated.emit(f"路徑檔案總數: {total_files} 待處理檔案進度: ({str(processed_files).zfill(len(str(pending_total_files)))} / {pending_total_files}) {os.path.relpath(file_path, self.directory)}")
            if processed_files == pending_total_files:
                self.progress_message_updated.emit("所有檔案轉換完成！")

    def run_text_mode(self, text):
        converted_text = self.cc.convert(text)
        self.text_converted.emit(converted_text)

class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("簡繁轉換工具")
        self.setGeometry(0, 0, 500, 200)

        self.directory_path = ""
        self.file_extensions = []
        self.directory_selected = False  # 新增一個變數來追蹤是否已選擇資料夾


        layout = QVBoxLayout()

        self.label = QLabel("選擇資料夾:", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.directory_layout = QHBoxLayout()
        self.directory_label = QLabel(self)
        self.directory_label.setAlignment(Qt.AlignCenter)
        self.directory_layout.addWidget(self.directory_label)

        self.browse_button = QPushButton("📁" + " 請選擇路徑", self)
        self.browse_button.setStyleSheet("border: 2px solid #E5446D; background: rgba(229,68,109, 0.2); color: #E5446D;")
        self.directory_layout.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.select_directory)

        layout.addLayout(self.directory_layout)

        self.extension_input = QTextEdit(self)
        self.extension_input.setPlaceholderText("輸入檔案副檔名，請以空格、換行或逗號區分\n\n(例如：html, js, css, yaml, text） 副檔名前可選擇不加.")
        self.extension_input.setStyleSheet("border: 2px solid #E5446D;  color: #FFFFFF;")
        layout.addWidget(self.extension_input)

        self.button_layout = QHBoxLayout()
        self.mode_switch_button = QPushButton("切換模式", self)
        self.mode_switch_button.setStyleSheet("border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;")
        self.mode_switch_button.clicked.connect(self.switch_mode)
        self.button_layout.addWidget(self.mode_switch_button)

        self.convert_button = QPushButton("❌請先選擇路徑❌", self)
        self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
        self.button_layout.addWidget(self.convert_button)
        self.convert_button.clicked.connect(self.start_conversion)

        layout.addLayout(self.button_layout)

        self.convert_format_combo_box = QComboBox(self)
        self.convert_format_combo_box.addItem("台灣化 (s2twp)")
        self.convert_format_combo_box.addItem("中國化 (tw2sp)")
        self.convert_format_combo_box.addItem("繁體化 (s2tw)")
        self.convert_format_combo_box.addItem("簡體化 (tw2s)")
        self.convert_format_combo_box.setStyleSheet("border: 2px solid #43C59E; color: #43C59E; border-radius: 4px")
        layout.addWidget(self.convert_format_combo_box)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        self.progress_bar.setStyleSheet("border-radius: 4px")

        self.processing_text_edit = QTextEdit(self)
        layout.addWidget(self.processing_text_edit)
        self.processing_text_edit.setReadOnly(True)
        self.processing_text_edit.setPlaceholderText("輸出運行結果的地方. . .")
        self.processing_text_edit.setStyleSheet("border: 2px solid #4f5b62; color: #43C59E; border-radius: 4px")

        self.font_label = QLabel(self)
        self.font_label.setAlignment(Qt.AlignCenter)
        self.font_label.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
        layout.addWidget(self.font_label)

        self.layout = layout

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.statusBar().showMessage('Ready')

        self.worker = Worker("", [])
        self.worker.progress_updated.connect(self.update_progress_bar)
        self.worker.progress_message_updated.connect(self.update_processing_text_edit)
        self.worker.progress_percentage_updated.connect(self.update_status_bar)
        self.worker.text_converted.connect(self.update_text_edit)
        self.worker.finished.connect(self.show_message_box)

        self.center()

        self.extension_input.textChanged.connect(self.update_button_status_style)

        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansTC-Regular.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.font_label.setText(f"目前使用的字體：{font_family}")
        else:
            print("Failed to load font")

        self.mode = "path"

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, screen.height() * 0.40 - size.height() // 2)

    def switch_mode(self):
        if self.mode == "path":
            self.mode = "text"
            self.label.setText("輸入文本:")
            self.directory_label.setText("")
            # self.browse_button.setText("❌取消選擇路徑❌")
            self.browse_button.setText("📋" + " 一鍵複製結果內容")
            self.extension_input.setPlaceholderText("請在此輸入文本內容")
            self.convert_button.setText("✔️ 開始轉換 ✔️")
            self.processing_text_edit.setReadOnly(False)  # 取消唯讀
            self.browse_button.clicked.disconnect(self.select_directory)  # 取消選擇路徑的功能
            self.browse_button.clicked.connect(self.copy_to_clipboard)  # 連接一鍵複製結果內容的功能
            
            # 在切換模式時不顯示提示
            self.statusBar().showMessage('Ready')
        else:
            self.mode = "path"
            self.label.setText("選擇資料夾:")
            self.directory_label.setText("")
            self.browse_button.setText("📁" + " 請選擇路徑")
            self.extension_input.setPlaceholderText("輸入檔案副檔名，請以空格、換行或逗號區分\n\n(例如：html, js, css, yaml, text） 副檔名前可選擇不加.")
            self.convert_button.setText("❌請先選擇路徑❌")
            self.processing_text_edit.setReadOnly(True)  # 設為唯讀
            self.browse_button.clicked.disconnect(self.copy_to_clipboard)  # 取消一鍵複製結果內容的功能
            self.browse_button.clicked.connect(self.select_directory)  # 連接選擇路徑的功能
        self.update_button_status_style()

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { border-radius: 4px; border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;}")

    def show_message_box(self):
        QMessageBox.information(self, "轉換完成", "所有檔案轉換完成！")
        self.progress_bar.setValue(0)

    def extensions_input_changed(self):
        extensions = self.extension_input.toPlainText().replace(".", "").replace(",", " ").split()
        extensions = [f".{ext}" for ext in extensions]
        return extensions
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "選擇資料夾")

        if directory:
            self.directory_selected = True  # 設定為已選擇資料夾
            self.directory_path = directory
            self.directory_label.setText(directory)
            self.worker.directory = directory
            self.extensions_input_changed()
            self.browse_button.setText("📁" + " 可變更路徑")
            self.browse_button.setStyleSheet("border: 2px solid #43C59E; background: rgba(67, 197, 158, 0.2); color: #43C59E;")
            self.update_button_status_style()

    def update_button_status_style(self):
        extensions = self.extensions_input_changed()
        if self.mode == "path":
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
        else:
            if self.extension_input.toPlainText():
                self.convert_button.setText("✔️ 開始轉換 ✔️")
                self.convert_button.setStyleSheet("border: 2px solid #43C59E; background: #43C59E; color: #FFFFFF;")
                self.extension_input.setStyleSheet("border: 2px solid #43C59E; color: #FFFFFF;")
            else:
                self.convert_button.setText("❌請輸入文本❌")
                self.convert_button.setStyleSheet("border: 2px solid #5448C8; background: #5448C8; color: #FFFFFF;")
                self.extension_input.setStyleSheet("border: 2px solid #E5446D;  color: #FFFFFF;")

    def start_conversion(self):
        if self.mode == "path" and not self.directory_selected:  # 在路徑模式下檢查是否選擇了資料夾
            QMessageBox.warning(self, "警告", "請選擇資料夾！")
            return
        
        if not self.extensions_input_changed() and self.mode == "path":
            QMessageBox.warning(self, "警告", "請輸入檔案副檔名！")
            return

        if not self.extension_input.toPlainText() and self.mode == "text":
            QMessageBox.warning(self, "警告", "請輸入文本！")
            return

        selected_format = self.convert_format_combo_box.currentText()
        if selected_format == "台灣化 (s2twp)":
            convert_format = 's2twp'
        elif selected_format == "中國化 (tw2sp)":
            convert_format = 'tw2sp'
        elif selected_format == "繁體化 (s2tw)":
            convert_format = 's2tw'
        elif selected_format == "簡體化 (tw2s)":
            convert_format = 'tw2s'

        self.worker.cc = OpenCC(convert_format)
        if self.mode == "path":
            self.worker.file_extensions = self.extensions_input_changed()
            self.worker.start()
            # 在文本模式下將內容複製到剪貼板
            if self.mode == "text":
                self.copy_to_clipboard()
        else:
            self.worker.run_text_mode(self.extension_input.toPlainText())
            
    def copy_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.processing_text_edit.toPlainText())
        self.browse_button.setText("✔️ 已複製到剪貼板 ✔️")
        
    def update_processing_text_edit(self, progress_message):
        self.processing_text_edit.clear()
        self.processing_text_edit.append(progress_message)
    
    def update_status_bar(self, progress_percentage):
        self.statusBar().showMessage(f"轉換進度: {progress_percentage}%")

    def update_text_edit(self, converted_text):
        self.processing_text_edit.clear()
        self.processing_text_edit.append(converted_text)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    custom_theme_path = os.path.join(os.path.dirname(__file__), 'themes/dark.xml')

    if os.path.exists(custom_theme_path):
        apply_stylesheet(app, theme=custom_theme_path)
    else:
        print("Custom theme file not found!")

    converter_app = ConverterApp()
    converter_app.show()

    sys.exit(app.exec())
