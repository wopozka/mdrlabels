# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QToolBar,
                             QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QStyleFactory, QComboBox, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPixmap
import sys

class MdrLabel(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('MDR Label')
        self.setGeometry(100, 100, 800, 600)
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu('&File')
        open_act = QAction('&Open Image', self)
        open_act.triggered.connect(self.open_pdf)
        file_menu.addAction(open_act)
        exit_act = QAction('&Exit', self)
        exit_act.triggered.connect(self.close_app)
        file_menu.addAction(exit_act)

        # Create a left toolbar with three labelled QLineEdit fields
        toolbar = QToolBar('LeftToolbar')
        toolbar.setMovable(False)
        # Use a container widget with layouts so labels and line edits are aligned
        container = QWidget()
        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(6, 6, 6, 6)
        vlayout.setSpacing(8)

        # Add an (initially empty) dropdown row with label 'select product' — will be populated later
        combo_row = QWidget()
        combo_h = QHBoxLayout()
        combo_h.setContentsMargins(0, 0, 0, 0)
        combo_h.setSpacing(6)
        lbl_combo = QLabel('select product')
        lbl_combo.setFixedWidth(120)
        self.dropdown = QComboBox()
        self.dropdown.setFixedWidth(200)
        combo_h.addWidget(lbl_combo)
        combo_h.addWidget(self.dropdown)
        combo_row.setLayout(combo_h)
        vlayout.addWidget(combo_row)

        # Helper to add a label + lineedit row
        def add_row(label_text):
            row = QWidget()
            hl = QHBoxLayout()
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(120)  # keep labels aligned
            le = QLineEdit()
            hl.addWidget(lbl)
            hl.addWidget(le)
            row.setLayout(hl)
            vlayout.addWidget(row)
            return le

        self.use_by_edit = add_row('Use by date')
        self.batch_edit = add_row('Batch')
        self.mfg_edit = add_row('Manufacturing date')

        # Add stretch to push rows to top
        vlayout.addStretch()
        container.setLayout(vlayout)
        toolbar.addWidget(container)
        # Add toolbar docked to the left (PyQt6 uses the ToolBarArea enum)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)

        # Central area: image viewer (QLabel inside QScrollArea)
        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Image preview components
        self.image_label = QLabel('No image loaded')
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setStyleSheet('background: #f0f0f0; border: 1px solid #aaa;')

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        central_layout.addWidget(self.scroll_area)

        # Keep a reference to the currently loaded pixmap
        self._pixmap = None

    def close_app(self):
        print('zamykam')
        self.close()

    def open_pdf(self):
        """Show file dialog and load selected image into the viewer."""
        path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Images (*.png *.jpg *.jpeg *.bmp *.gif)')
        if path:
            self.load_pdf(path)

    def load_pdf(self, path: str):
        """Load an image file into the image viewer. Returns True on success."""
        try:
            pix = QPixmap(path)
            if pix.isNull():
                # failed to load
                self.image_label.setText('Failed to load image')
                self._pixmap = None
                return False
            self._pixmap = pix
            self.image_label.setPixmap(self._pixmap)
            # Ensure label resizes to pixmap size when not scaled by scroll area
            self.image_label.adjustSize()
            return True
        except Exception as e:
            self.image_label.setText(f'Error loading image: {e}')
            self._pixmap = None
            return False

if __name__ == "__main__":
    print('otwieram')
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    w = MdrLabel(None)
    w.show()
    app.exec()
