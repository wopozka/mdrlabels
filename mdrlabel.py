# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QToolBar,
                             QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QStyleFactory, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import sys
import importlib

# Try to import Qt PDF modules at runtime. Use importlib to avoid static import resolution
try:
    _qtpdf = importlib.import_module('PyQt6.QtPdf')
    _qtpdfw = importlib.import_module('PyQt6.QtPdfWidgets')
    QPdfDocument = getattr(_qtpdf, 'QPdfDocument', None)
    QPdfView = getattr(_qtpdfw, 'QPdfView', None)
    PDF_SUPPORT = QPdfDocument is not None and QPdfView is not None
except Exception:
    QPdfDocument = None
    QPdfView = None
    PDF_SUPPORT = False

class MdrLabel(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('MDR Label')
        self.setGeometry(100, 100, 800, 600)
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu('&File')
        open_act = QAction('&Open PDF', self)
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

        # Central area: PDF viewer (if available) or placeholder
        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        if PDF_SUPPORT:
            self.pdf_doc = QPdfDocument(self)
            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_doc)
            central_layout.addWidget(self.pdf_view)
        else:
            placeholder = QLabel('PDF preview not available (QtPdfWidgets missing)')
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            central_layout.addWidget(placeholder)

    def close_app(self):
        print('zamykam')
        self.close()

    def open_pdf(self):
        """Show file dialog and load selected PDF into the viewer."""
        path, _ = QFileDialog.getOpenFileName(self, 'Open PDF', '', 'PDF Files (*.pdf)')
        if path:
            self.load_pdf(path)

    def load_pdf(self, path: str):
        """Load a PDF file into the PDF viewer if supported. Returns True on success."""
        if not PDF_SUPPORT:
            return False
        # QPdfDocument.load returns an enum/status in some versions; just call and rely on view update
        try:
            self.pdf_doc.load(path)
            return True
        except Exception:
            return False

if __name__ == "__main__":
    print('otwieram')
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    w = MdrLabel(None)
    w.show()
    app.exec()
