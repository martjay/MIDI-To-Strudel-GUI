"""
MIDI to Strudel GUI Converter
拖放 MIDI 文件直接转换为 Strudel 代码，支持参数调节与一键复制。
"""

import sys
import os
import math
import mido
import webbrowser
from pathlib import Path
from types import SimpleNamespace
from collections import defaultdict
import importlib.util

from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QPlainTextEdit, QFileDialog, QFrame,
    QCheckBox, QSpinBox, QComboBox, QGroupBox, QSplitter, QStatusBar
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QDragEnterEvent, QDropEvent, QIcon, QAction
)

# 动态载入同目录下的 Midi-to-Strudel.py (支持源码运行、Windows EXE 与 macOS .app 打包运行)
def load_converter_module():
    search_dirs = []
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            search_dirs.append(Path(sys._MEIPASS))
        exe_dir = Path(sys.executable).resolve().parent
        search_dirs.append(exe_dir)
        # 兼容 macOS .app 独立包 (Contents/MacOS/.. -> Contents/Resources)
        if sys.platform == 'darwin':
            res_dir = exe_dir.parent / "Resources"
            if res_dir.exists():
                search_dirs.append(res_dir)
    else:
        search_dirs = [Path(__file__).resolve().parent, Path.cwd()]

    converter_path = None
    for d in search_dirs:
        candidate = d / "Midi-to-Strudel.py"
        if candidate.exists():
            converter_path = candidate
            break

    if not converter_path:
        raise FileNotFoundError("找不到转换核心脚本: Midi-to-Strudel.py")

    spec = importlib.util.spec_from_file_location("midi_to_strudel_core", converter_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

converter = load_converter_module()


class DropZoneWidget(QFrame):
    """支持鼠标拖放与点击选择文件的视觉交互卡片"""
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("dropZone")
        self.is_hovered = False
        self.current_filename = ""

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 24, 20, 24)

        self.icon_label = QLabel("📥")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 38px; background: transparent;")

        self.title_label = QLabel("将 MIDI 文件拖放到此处")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f5; background: transparent;")

        self.hint_label = QLabel("支持 .mid / .midi 格式，或点击此处选择文件")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 13px; color: #8e8e9f; background: transparent;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)

        self.update_style(normal=True)

    def update_style(self, normal=True, active=False):
        if active:
            # 拖拽悬浮状态：青色高亮边框与深蓝底色
            self.setStyleSheet("""
                QFrame#dropZone {
                    border: 2px dashed #00e5ff;
                    border-radius: 12px;
                    background-color: #1a2a3a;
                }
            """)
        elif self.current_filename:
            # 已加载文件状态：亮绿微光边框
            self.setStyleSheet("""
                QFrame#dropZone {
                    border: 2px solid #00e676;
                    border-radius: 12px;
                    background-color: #18261e;
                }
            """)
        else:
            # 普通状态
            self.setStyleSheet("""
                QFrame#dropZone {
                    border: 2px dashed #3e3e4e;
                    border-radius: 12px;
                    background-color: #1e1e24;
                }
                QFrame#dropZone:hover {
                    border-color: #7c4dff;
                    background-color: #24222f;
                }
            """)

    def set_file_info(self, file_path: str, info_text: str = ""):
        self.current_filename = os.path.basename(file_path)
        self.icon_label.setText("🎵")
        self.title_label.setText(f"当前文件: {self.current_filename}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00e676; background: transparent;")
        if info_text:
            self.hint_label.setText(info_text)
        self.update_style(normal=False)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.mid', '.midi')):
                    event.acceptProposedAction()
                    self.update_style(active=True)
                    self.title_label.setText("松开鼠标立即转换！")
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.update_style(normal=True)
        if self.current_filename:
            self.title_label.setText(f"当前文件: {self.current_filename}")
        else:
            self.title_label.setText("将 MIDI 文件拖放到此处")

    def dropEvent(self, event: QDropEvent):
        self.update_style(normal=True)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(('.mid', '.midi')):
                self.file_dropped.emit(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 MIDI 文件", "", "MIDI Files (*.mid *.midi);;All Files (*.*)"
            )
            if file_path:
                self.file_dropped.emit(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI to Strudel Converter 🌀")
        self.resize(980, 760)
        self.setMinimumSize(840, 600)
        
        self.current_midi_path = None
        self.current_code = ""

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # 1. 顶部 Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        title_lbl = QLabel("🌀 MIDI to Strudel 代码转换器")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #f5f5f7;")
        sub_lbl = QLabel("一键将标准 MIDI 文件转换为 Strudel Live-Coding 算法代码")
        sub_lbl.setStyleSheet("font-size: 13px; color: #8e8e9e;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        open_web_btn = QPushButton("🌐 打开 Strudel REPL")
        open_web_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_web_btn.setToolTip("在默认浏览器中打开 Strudel 在线编程编辑器")
        open_web_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b36;
                color: #00e5ff;
                border: 1px solid #3d3d4e;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #353545;
                border-color: #00e5ff;
            }
        """)
        open_web_btn.clicked.connect(lambda: webbrowser.open("https://strudel.cc/"))
        header_layout.addWidget(open_web_btn)
        main_layout.addLayout(header_layout)

        # 2. 拖拽识别区 (Drop Zone)
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.file_dropped.connect(self.handle_file_loaded)
        main_layout.addWidget(self.drop_zone)

        # 3. 参数配置控制条 (Settings Panel)
        # 3. 参数配置控制面板 (Settings Panel - 垂直3行分组布局)
        settings_group = QGroupBox("⚙️ 转换参数微调 (修改后自动重新转换)")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(18, 14, 18, 14)
        settings_layout.setSpacing(12)

        # 第 1 行: 数值与音准核心参数
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(24)

        # 3.1 分辨率 (Notes per bar)
        res_box = QHBoxLayout()
        res_lbl = QLabel("细分精度:")
        res_lbl.setStyleSheet("color: #cfcfe0; font-size: 13px;")
        self.res_combo = QComboBox()
        self.res_combo.addItems(["16 拍", "32 拍", "64 拍 (推荐)", "128 拍 (极高)"])
        self.res_combo.setCurrentIndex(2) # 64
        self.res_combo.currentIndexChanged.connect(self.trigger_reconvert)
        res_box.addWidget(res_lbl)
        res_box.addWidget(self.res_combo)
        row1_layout.addLayout(res_box)

        # 3.2 小节限制 (Bar limit)
        bar_box = QHBoxLayout()
        bar_lbl = QLabel("最大小节:")
        bar_lbl.setStyleSheet("color: #cfcfe0; font-size: 13px;")
        self.bar_spin = QSpinBox()
        self.bar_spin.setRange(0, 9999)
        self.bar_spin.setValue(0)
        self.bar_spin.setSpecialValueText("无限制")
        self.bar_spin.valueChanged.connect(self.trigger_reconvert)
        bar_box.addWidget(bar_lbl)
        bar_box.addWidget(self.bar_spin)
        row1_layout.addLayout(bar_box)

        # 3.3 八度移调 (Octave shift)
        oct_box = QHBoxLayout()
        oct_lbl = QLabel("八度移调:")
        oct_lbl.setStyleSheet("color: #cfcfe0; font-size: 13px;")
        self.octave_combo = QComboBox()
        self.octave_combo.addItems(["-2 八度", "-1 八度", "原调 0 (默认)", "+1 八度", "+2 八度"])
        self.octave_combo.setCurrentIndex(2)  # 原调 0
        self.octave_combo.setToolTip("升降八度。如果旋律在DAW中因中央C定义差异偏低，可设为 +1 八度")
        self.octave_combo.currentIndexChanged.connect(self.trigger_reconvert)
        oct_box.addWidget(oct_lbl)
        oct_box.addWidget(self.octave_combo)
        row1_layout.addLayout(oct_box)

        row1_layout.addStretch()
        settings_layout.addLayout(row1_layout)

        # 第 2 行: 智能音频与声学增强选项
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(22)

        self.chk_auto_drums = QCheckBox("🥁 通道10转鼓组")
        self.chk_auto_drums.setToolTip("自动将 MIDI 标准第10通道(打击乐)转换为 Roland TR-909 鼓组音色")
        self.chk_auto_drums.setChecked(True)
        self.chk_auto_drums.toggled.connect(self.trigger_reconvert)
        row2_layout.addWidget(self.chk_auto_drums)

        self.chk_guess_inst = QCheckBox("智能匹配乐器")
        self.chk_guess_inst.setToolTip("读取 MIDI 中的乐器换音编号，匹配 Strudel 类似乐器音色")
        self.chk_guess_inst.setChecked(True)
        self.chk_guess_inst.toggled.connect(self.trigger_reconvert)
        row2_layout.addWidget(self.chk_guess_inst)

        self.chk_enhance_sound = QCheckBox("✨ 智能声学塑形 (防断音)")
        self.chk_enhance_sound.setToolTip("为非钢琴乐器注入定制连奏 (legato)、延音释放 (release/decay)、滤波与混响，彻底消除突兀断音")
        self.chk_enhance_sound.setChecked(True)
        self.chk_enhance_sound.toggled.connect(self.trigger_reconvert)
        row2_layout.addWidget(self.chk_enhance_sound)

        self.chk_auto_gain = QCheckBox("🎚️ 智能分轨音量平衡")
        self.chk_auto_gain.setToolTip("提取各音轨的力度 (Velocity) 与主音量 (CC 7) 自动平衡响度，防止爆音与声部混乱")
        self.chk_auto_gain.setChecked(True)
        self.chk_auto_gain.toggled.connect(self.trigger_reconvert)
        row2_layout.addWidget(self.chk_auto_gain)

        row2_layout.addStretch()
        settings_layout.addLayout(row2_layout)

        # 第 3 行: 输出代码格式选项
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(22)

        self.chk_small_print = QCheckBox("紧凑单行格式")
        self.chk_small_print.setToolTip("将全部 note 连成单行，减少代码行数")
        self.chk_small_print.setChecked(False)
        self.chk_small_print.toggled.connect(self.trigger_reconvert)
        row3_layout.addWidget(self.chk_small_print)

        self.chk_flat_seq = QCheckBox("扁平序列")
        self.chk_flat_seq.setToolTip("不生成复合节拍与多复音切片，只保留扁平音序")
        self.chk_flat_seq.setChecked(False)
        self.chk_flat_seq.toggled.connect(self.trigger_reconvert)
        row3_layout.addWidget(self.chk_flat_seq)

        row3_layout.addStretch()
        settings_layout.addLayout(row3_layout)

        main_layout.addWidget(settings_group)

        # 4. 代码预览区域
        preview_header = QHBoxLayout()
        preview_title = QLabel("💻 Strudel 代码预览")
        preview_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cfcfe0;")
        self.stats_lbl = QLabel("等待载入 MIDI 文件...")
        self.stats_lbl.setStyleSheet("font-size: 12px; color: #8e8e9e;")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()
        preview_header.addWidget(self.stats_lbl)
        main_layout.addLayout(preview_header)

        self.code_editor = QPlainTextEdit()
        font_family = "Menlo" if sys.platform == "darwin" else "Consolas"
        font = QFont(font_family, 12 if sys.platform == "darwin" else 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.code_editor.setFont(font)
        self.code_editor.setPlaceholderText("// 转换后的 Strudel 代码将实时显示在此处...\n// 转换完成后点击下方的【一键复制】按钮即可直接在 strudel.cc 中播放！")
        main_layout.addWidget(self.code_editor, stretch=1)

        # 5. 底部操作栏 (一键复制等)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        self.copy_btn = QPushButton("📋 一键复制 Strudel 代码")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #7c4dff);
                color: #0b0b12;
                border: none;
                border-radius: 9px;
                padding: 12px 24px;
                font-weight: 800;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #33ecff, stop:1 #996eff);
            }
            QPushButton:pressed {
                background-color: #00b0cc;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        bottom_layout.addWidget(self.copy_btn, stretch=2)

        self.save_btn = QPushButton("💾 保存为 .txt")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b36;
                color: #f0f0f5;
                border: 1px solid #3d3d4e;
                border-radius: 9px;
                padding: 12px 18px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #353545;
                border-color: #7c4dff;
            }
        """)
        self.save_btn.clicked.connect(self.save_to_file)
        bottom_layout.addWidget(self.save_btn, stretch=1)

        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8e8e9e;
                border: 1px solid #3d3d4e;
                border-radius: 9px;
                padding: 12px 14px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #ff5252;
                border-color: #ff5252;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        bottom_layout.addWidget(self.clear_btn)

        main_layout.addLayout(bottom_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪。请拖放 .mid 文件到上方区域")

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #131317;
            }
            QWidget {
                color: #f0f0f5;
            }
            QGroupBox {
                border: 1px solid #2e2e3a;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #9e9eb0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }
            QComboBox, QSpinBox {
                background-color: #22222b;
                color: #f0f0f5;
                border: 1px solid #3d3d4e;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QComboBox:hover, QSpinBox:hover {
                border-color: #00e5ff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QCheckBox {
                color: #cfcfe0;
                font-size: 13px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #4a4a5c;
                border-radius: 4px;
                background-color: #22222b;
            }
            QCheckBox::indicator:checked {
                background-color: #00e5ff;
                border-color: #00e5ff;
            }
            QPlainTextEdit {
                background-color: #17171d;
                color: #a6e22e;
                border: 1px solid #2e2e3c;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #3e3e5e;
            }
            QStatusBar {
                background-color: #131317;
                color: #7a7a8e;
                border-top: 1px solid #1e1e26;
            }
        """)

    def handle_file_loaded(self, file_path: str):
        if not os.path.exists(file_path):
            self.status_bar.showMessage(f"文件不存在: {file_path}", 4000)
            return
        
        self.current_midi_path = file_path
        self.convert_midi(file_path)

    def get_selected_notes_per_bar(self) -> int:
        idx = self.res_combo.currentIndex()
        mapping = {0: 16, 1: 32, 2: 64, 3: 128}
        return mapping.get(idx, 64)

    def trigger_reconvert(self):
        if self.current_midi_path:
            self.convert_midi(self.current_midi_path)

    def convert_midi(self, file_path: str):
        try:
            self.status_bar.showMessage("正在解析 MIDI 并生成 Strudel 代码...")
            QApplication.processEvents()

            mid = mido.MidiFile(file_path)
            tempo, bpm, cycle_len = converter.get_timing_values(mid)
            octave_shift = self.octave_combo.currentIndex() - 2
            auto_drums = self.chk_auto_drums.isChecked()

            events, instruments, drum_keys, mix_info = converter.collect_note_events(
                mid, tempo, auto_drums=auto_drums, octave_shift=octave_shift
            )

            args = SimpleNamespace(
                bar_limit=self.bar_spin.value(),
                notes_per_bar=self.get_selected_notes_per_bar(),
                tab_size=2,
                guess_instrument=self.chk_guess_inst.isChecked(),
                enhance_sound=self.chk_enhance_sound.isChecked(),
                auto_gain=self.chk_auto_gain.isChecked(),
                flat_sequences=self.chk_flat_seq.isChecked(),
                small_print=self.chk_small_print.isChecked()
            )

            tracks = converter.build_tracks(events, cycle_len, args)
            output_code = converter.build_output(
                tracks, bpm, instruments, args, drum_keys=drum_keys, mix_info=mix_info
            )

            self.current_code = output_code
            self.code_editor.setPlainText(output_code)

            # 更新文件卡片
            track_count = len(tracks)
            total_bars = max([len(bars) for _, bars in tracks]) if tracks else 0
            file_size_kb = os.path.getsize(file_path) / 1024
            info_str = f"BPM: {int(bpm)} | 轨道数: {track_count} | 长度: {total_bars} 小节 | 大小: {file_size_kb:.1f} KB"
            self.drop_zone.set_file_info(file_path, info_str)

            # 更新统计信息
            lines = len(output_code.splitlines())
            chars = len(output_code)
            self.stats_lbl.setText(f"{lines} 行 | {chars} 字符")

            self.status_bar.showMessage(f"✅ 转换成功: {os.path.basename(file_path)}", 5000)

        except Exception as e:
            self.status_bar.showMessage(f"❌ 转换失败: {str(e)}", 8000)
            self.code_editor.setPlainText(f"// 转换发生错误:\n// {str(e)}")

    def copy_to_clipboard(self):
        text = self.code_editor.toPlainText().strip()
        if not text:
            self.status_bar.showMessage("剪贴板为空，请先载入并转换 MIDI 文件！", 3000)
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # 视觉动效反馈
        orig_text = "📋 一键复制 Strudel 代码"
        self.copy_btn.setText("✅ 已成功复制到剪贴板！")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: #003314;
                border: none;
                border-radius: 9px;
                padding: 12px 24px;
                font-weight: 800;
                font-size: 15px;
            }
        """)

        def reset_btn():
            self.copy_btn.setText(orig_text)
            self.copy_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #7c4dff);
                    color: #0b0b12;
                    border: none;
                    border-radius: 9px;
                    padding: 12px 24px;
                    font-weight: 800;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #33ecff, stop:1 #996eff);
                }
            """)

        QTimer.singleShot(1800, reset_btn)
        self.status_bar.showMessage("✅ 已成功复制全部代码，可直接前往 strudel.cc 粘贴播放！", 4000)

    def save_to_file(self):
        text = self.code_editor.toPlainText().strip()
        if not text:
            self.status_bar.showMessage("内容为空，无需保存", 3000)
            return

        default_name = "strudel_output.txt"
        if self.current_midi_path:
            base = os.path.splitext(os.path.basename(self.current_midi_path))[0]
            default_name = f"{base}_strudel.txt"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存代码为文件", default_name, "Text Files (*.txt);;JavaScript Files (*.js);;All Files (*.*)"
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            self.status_bar.showMessage(f"已保存到: {save_path}", 4000)

    def clear_all(self):
        self.current_midi_path = None
        self.current_code = ""
        self.code_editor.clear()
        self.drop_zone.current_filename = ""
        self.drop_zone.icon_label.setText("📥")
        self.drop_zone.title_label.setText("将 MIDI 文件拖放到此处")
        self.drop_zone.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f5; background: transparent;")
        self.drop_zone.hint_label.setText("支持 .mid / .midi 格式，或点击此处选择文件")
        self.drop_zone.update_style(normal=True)
        self.stats_lbl.setText("等待载入 MIDI 文件...")
        self.status_bar.showMessage("已清空", 2000)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    
    # 如果启动时命令行传入了文件路径（如拖放到 .bat 启动）
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        window.handle_file_loaded(sys.argv[1])
        
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
