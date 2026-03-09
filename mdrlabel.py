# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.riverbankcomputing.com/static/Docs/PyQt6/index.html
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QToolBar,
                             QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QStyleFactory, QComboBox, QFileDialog, QScrollArea,
                             QDialog, QPushButton, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QSettings, QRegularExpression
from PyQt6.QtGui import QAction, QPixmap, QRegularExpressionValidator
import sys
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from collections import OrderedDict

# Dodane: PyMuPDF do renderowania stron PDF (import przez nazwę 'pymupdf' zamiast 'fitz')
try:
    import pymupdf as fitz
except Exception:
    fitz = None

# Dodane: biblioteki do kodów kreskowych
path = sys.path
sys.path = ["C:\\Users\\pwawrzyniak\\PycharmProjects\\python-barcode"] + path
try:
    import barcode
    from barcode.writer import ImageWriter
except Exception:
    barcode = None

try:
    from datamatrix import DataMatrix
except Exception:
    DataMatrix = None

try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None
    ImageDraw = None

from pylibdmtx.pylibdmtx import encode

# Dodana pomocnicza klasa QLabel z obsługą ruchu myszy
class ImageLabel(QLabel):
    def __init__(self, main_window=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main = main_window
        self.setMouseTracking(True)
        # Panning state (right mouse button drag)
        self._panning = False
        self._pan_last_pos = None

    def mouseMoveEvent(self, event):
        # event.position() zwraca pozycję względem widgetu (QPointF)
        pm = self.pixmap()
        if pm is None:
            if self._main:
                self._main.update_mouse_status(None, None)
            return
        # używamy event.pos() (QPoint) — daje całkowite współrzędne wewnątrz widgetu
        p = event.pos()
        x = int(p.x())
        y = int(p.y())
        pm_w = pm.width()
        pm_h = pm.height()
        lbl_w = self.width()
        lbl_h = self.height()
        # Oblicz przesunięcie jeśli pixmapa jest mniejsza niż etykieta i wyśrodkowana
        offset_x = max((lbl_w - pm_w) // 2, 0)
        offset_y = max((lbl_h - pm_h) // 2, 0)
        img_x = x - offset_x
        img_y = y - offset_y
        # Sprawdź czy kursor znajduje się nad obrazem
        if img_x < 0 or img_y < 0 or img_x >= pm_w or img_y >= pm_h:
            if self._main:
                self._main.update_mouse_status(None, None)
        else:
            if self._main:
                # Przekaż współrzędne względem aktualnie wyświetlanego pixmapa
                # ale skonwertowane na współrzędne PDF (punkty)
                try:
                    pdf_x, pdf_y = self._main.display_to_pdf_coords(img_x, img_y)
                except Exception:
                    pdf_x, pdf_y = img_x, img_y
                self._main.update_mouse_status(pdf_x, pdf_y)

        # Jeśli trwa panning (prawe przycisk wciśnięty) — obsłuż przewijanie
        if self._panning and self._pan_last_pos is not None and self._main and hasattr(self._main, 'scroll_area'):
            cur = event.pos()
            dx = cur.x() - self._pan_last_pos.x()
            dy = cur.y() - self._pan_last_pos.y()
            sa = self._main.scroll_area
            if sa is not None:
                try:
                    hbar = sa.horizontalScrollBar()
                    vbar = sa.verticalScrollBar()
                    # przesuwamy wartości scrollbara przeciwnie do ruchu myszy, żeby obraz podążał za kursorem
                    hbar.setValue(int(hbar.value() - dx))
                    vbar.setValue(int(vbar.value() - dy))
                except Exception:
                    pass
            # zaktualizuj pozycję referencyjną
            self._pan_last_pos = event.pos()

    def leaveEvent(self, event):
        if self._main:
            self._main.update_mouse_status(None, None)
        super().leaveEvent(event)

    def wheelEvent(self, event):
        # Jeśli wciśnięty Ctrl -> zoom; w przeciwnym razie pozwól scroll area obsłużyć przewijanie
        mods = event.modifiers()
        if mods & Qt.KeyboardModifier.ControlModifier:
            # angleDelta().y() zawiera wartość w jednostkach 1/8 stopnia; zwykle 120 na krok
            delta = event.angleDelta().y()
            if self._main:
                self._main.change_zoom(delta)
            event.accept()
        else:
            # Przesuwamy bezpośrednio scrollbary, to działa na dużych obrazach i nie zależy od współrzędnych eventu
            if self._main and hasattr(self._main, 'scroll_area') and self._main.scroll_area is not None:
                sa = self._main.scroll_area
                vbar = sa.verticalScrollBar()
                hbar = sa.horizontalScrollBar()
                delta_x = event.angleDelta().x()
                delta_y = event.angleDelta().y()
                # oblicz liczbę kroków (może być ułamkowe na touchpadach)
                step_y = delta_y / 120.0 if delta_y else 0.0
                step_x = delta_x / 120.0 if delta_x else 0.0
                # wybierz wielkość przesunięcia: użyj singleStep jako jednostki i przemnóż dla sensownej prędkości
                try:
                    v_step = vbar.singleStep() or 20
                except Exception:
                    v_step = 20
                try:
                    h_step = hbar.singleStep() or 20
                except Exception:
                    h_step = 20
                if abs(step_y) > 0:
                    vbar.setValue(int(vbar.value() - step_y * v_step * 3))
                    event.accept()
                    return
                if abs(step_x) > 0:
                    hbar.setValue(int(hbar.value() - step_x * h_step * 3))
                    event.accept()
                    return
            # fallback
            event.ignore()

    def mousePressEvent(self, event):
        # Rozpocznij panning przy prawym przycisku
        if event.button() == Qt.MouseButton.RightButton:
            self._panning = True
            self._pan_last_pos = event.pos()
            try:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            except Exception:
                pass
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Zakończ panning przy zwolnieniu prawego przycisku
        if event.button() == Qt.MouseButton.RightButton:
            self._panning = False
            self._pan_last_pos = None
            try:
                self.unsetCursor()
            except Exception:
                pass
            event.accept()
            return
        super().mouseReleaseEvent(event)

class ConfigDialog(QDialog):
    """Dialog do konfiguracji lokalizacji folderu Labels."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configuration')
        self.setGeometry(100, 100, 500, 100)

        layout = QVBoxLayout()

        # Folder Labels
        h_folder = QHBoxLayout()
        lbl_folder = QLabel('Labels folder:')
        lbl_folder.setFixedWidth(150)
        self.folder_label = QLineEdit()
        self.folder_label.setReadOnly(True)
        btn_folder = QPushButton('Browse...')
        btn_folder.clicked.connect(self._select_folder)
        h_folder.addWidget(lbl_folder)
        h_folder.addWidget(self.folder_label)
        h_folder.addWidget(btn_folder)
        layout.addLayout(h_folder)

        # Przyciski OK/Cancel
        h_buttons = QHBoxLayout()
        btn_ok = QPushButton('OK')
        btn_cancel = QPushButton('Cancel')
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        h_buttons.addStretch()
        h_buttons.addWidget(btn_ok)
        h_buttons.addWidget(btn_cancel)
        layout.addLayout(h_buttons)

        self.setLayout(layout)

        # Załaduj zapisane wartości
        self.load_config()

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Labels Folder')
        if folder:
            self.folder_label.setText(folder)
            # Zapisz od razu po wyborze folderu
            self.save_config()

    def load_config(self):
        config_path = self._get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    folder = config.get('labels_folder', '')
                    self.folder_label.setText(folder)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        config_path = self._get_config_path()
        try:
            config = {
                'labels_folder': self.folder_label.text()
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _get_config_path(self):
        """Zwróć ścieżkę do pliku konfiguracyjnego w katalogu domowym."""
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.mdrlabel')
        return os.path.join(config_dir, 'config.json')

    def get_folder(self):
        return self.folder_label.text()


class LabelManager:
    """Manager do wczytywania i zarządzania etykietami z JSON-ów."""
    def __init__(self, labels_folder: str):
        self.labels_folder = labels_folder
        self.labels = {}
        self.load_labels()

    def load_labels(self):
        """Wczytaj wszystkie JSON-y z folderu."""
        self.labels = {}
        if not os.path.isdir(self.labels_folder):
            return

        for filename in os.listdir(self.labels_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(self.labels_folder, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        label_name = data.get('label_name', filename)
                        if label_name in self.labels:
                            print(f'Error: Duplicate label name "{label_name}" in file {filename}. Skipping.')
                        self.labels[label_name] = data
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def get_label_names(self):
        """Zwróć listę nazw etykiet."""
        return list(self.labels.keys())

    def get_label(self, label_name: str):
        """Zwróć definicję etykiety."""
        return self.labels.get(label_name)

    def get_fields(self, label_name: str):
        """Zwróć listę pól dla danej etykiety."""
        label = self.get_label(label_name)
        if label and 'fields' in label:
            return label['fields']
        return []

    def get_udi_di(self, label_name: str):
        """Zwróć UDI-DI dla danej etykiety."""
        label = self.get_label(label_name)
        if label:
            return label.get('udi_di', '')
        return ''

    def get_barcode_config(self, label_name: str):
        """Zwróć konfigurację kodu kreskowego."""
        label = self.get_label(label_name)
        if label:
            return label.get('barcode', {})
        return {}

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

        # Menu Settings
        settings_menu = self.menu.addMenu('&Settings')
        config_act = QAction('&Configuration', self)
        config_act.triggered.connect(self.show_config_dialog)
        settings_menu.addAction(config_act)

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
        # Domyślnie dropdown wyłączony — aktywujemy go gdy załadujemy PDF
        self.dropdown.setEnabled(False)
        combo_h.addWidget(lbl_combo)
        combo_h.addWidget(self.dropdown)
        combo_row.setLayout(combo_h)
        vlayout.addWidget(combo_row)

        # Podłącz obsługę zmiany wyboru (używana również do wyboru strony PDF)
        self.dropdown.currentIndexChanged.connect(self._on_dropdown_changed)

        # Inicjalizuj LabelManager
        labels_folder = self._load_configuration()
        self.label_manager = LabelManager(labels_folder) if labels_folder else None

        # Zmienna do przechowywania bieżącej etykiety
        self.current_label = None

        # Helper to add a label + lineedit row
        def add_row(label_text, tooltip=None):
            row = QWidget()
            hl = QHBoxLayout()
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(6)
            lbl = QLabel(label_text)
            if tooltip is not None:
                lbl.setToolTip(tooltip)
            lbl.setFixedWidth(120)  # keep labels aligned
            le = QLineEdit()
            hl.addWidget(lbl)
            hl.addWidget(le)
            row.setLayout(hl)
            vlayout.addWidget(row)
            return le

        date_regex = QRegularExpression(r'^\d{4}-\d{2}-\d{2}$')
        date_validator = QRegularExpressionValidator(date_regex)
        self.editable_fields = dict()
        self.editable_fields['PROD_DATE'] = add_row('Manufacturing date', tooltip='Format daty: YYYY-MM-DD')
        self.editable_fields['PROD_DATE'].setToolTip('Format daty: YYYY-MM-DD')
        self.editable_fields['PROD_DATE'].setValidator(date_validator)
        self.editable_fields['BEST_BEFORE'] = add_row('Use by date', tooltip='Format daty: YYYY-MM-DD')
        self.editable_fields['BEST_BEFORE'].setToolTip('Format daty: YYYY-MM-DD')
        self.editable_fields['BEST_BEFORE'].setValidator(date_validator)
        self.editable_fields['BATCH/LOT'] = add_row('Batch')
        self.editable_fields['SERIAL'] = add_row('Serial number')
        self.editable_fields['VAR_COUNT'] = add_row('Count')

        # add buttons to toolbar
        # Fill label
        row = QWidget()
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(6)
        fill_label_button = QPushButton('Fill label')
        fill_label_button.clicked.connect(self.add_dynamic_data_to_pdf_template)
        hl.addWidget(fill_label_button)
        print_button = QPushButton('Print')
        hl.addWidget(print_button)
        row.setLayout(hl)
        vlayout.addWidget(row)

        # Add stretch to push rows to top
        vlayout.addStretch()
        container.setLayout(vlayout)
        toolbar.addWidget(container)
        # Add toolbar docked to the left (PyQt6 uses the ToolBarArea enum)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)

        # Central area: image viewer (ImageLabel inside QScrollArea)
        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Image preview components (używamy ImageLabel, aby śledzić współrzędne myszy)
        self.image_label = ImageLabel(self)
        self.image_label.setText('No image loaded')
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setStyleSheet('background: #f0f0f0; border: 1px solid #aaa;')

        # Pasek statusu do wyświetlania współrzędnych
        self.statusBar().showMessage('')

        self.scroll_area = QScrollArea()
        # Nie zmieniamy rozmiaru widgetu automatycznie — chcemy, żeby QLabel zachował rozmiar obrazka
        # i wtedy QScrollArea pokaże belki przewijania gdy obraz większy niż viewport.
        self.scroll_area.setWidgetResizable(False)
         # Pokaż belki przewijania kiedy potrzebne (gdy obraz większy niż widok)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.image_label)
        central_layout.addWidget(self.scroll_area)

        # Keep a reference to the currently loaded original pixmap
        self._pixmap = None
        # Zoom state
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 5.0

        # PDF-related state
        self._pdf_doc = None
        self._pdf_page_count = 0
        # PDF rendering info: original page size in PDF points and render scale used to produce pixmap
        self._pdf_render_scale = None
        self._pdf_page_width_pts = None
        self._pdf_page_height_pts = None
        self._temp_pdf_files = []
        self._current_pdf_template_path = None

    def update_mouse_status(self, x, y):
        """Aktualizuje pasek statusu współrzędnymi względem obrazka oraz poziomem zoomu."""
        zoom_pct = int(self._zoom * 100)
        if x is None or y is None:
            self.statusBar().showMessage(f'Zoom: {zoom_pct}%')
        else:
            # x,y passed here are PDF coordinates (points) when a PDF is loaded
            try:
                # format as integers for readability
                xi = int(x)
                yi = int(y)
            except Exception:
                xi = x
                yi = y
            self.statusBar().showMessage(f'PDF X: {xi}   PDF Y: {yi}   Zoom: {zoom_pct}%')

    def display_to_pdf_coords(self, img_x, img_y):
        """Konwertuje współrzędne pikselowe z wyświetlanego obrazu (img_x,img_y)
        do współrzędnych w przestrzeni PDF (punkty). Zwraca (pdf_x, pdf_y).

        - img_x/img_y: współrzędne względem lewego-górnego rogu aktualnie wyświetlanego pixmapy (piksele)
        - pdf_x/pdf_y: współrzędne w punktach PDF (origin w lewym-górnym rogu strony, y liczone od góry)
        """
        if self._pdf_doc is None or self._pdf_render_scale is None or self._pdf_page_width_pts is None:
            # brak PDF -> zwróć współrzędne pikselowe
            return img_x, img_y
        try:
            scale = self._pdf_render_scale * self._zoom
            # współrzędne w punktach liczymy jako: img_px / (render_scale * zoom)
            pdf_x = img_x / scale
            # img_y mierzone od góry -> pdf_y liczony od góry (bez odwracania)
            pdf_y = img_y / scale
            return pdf_x, pdf_y
        except Exception:
            return img_x, img_y

    def change_zoom(self, delta):
        """Zmienia poziom zoomu bazując na delta z wheelEvent (angleDelta.y())."""
        if delta == 0:
            return
        # Normalny krok to 120; policz liczbę kroków (może być ułamkowe na touchpadach)
        steps = delta / 120.0
        factor_per_step = 1.25
        new_zoom = self._zoom * (factor_per_step ** steps)
        # Clamp
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        if abs(new_zoom - self._zoom) < 1e-6:
            return
        self._zoom = new_zoom
        self.apply_zoom()

    def apply_zoom(self):
        """Przeskaluj i ustaw pixmapę zgodnie z aktualnym zoomem."""
        if self._pixmap is None:
            # tylko odśwież status
            self.update_mouse_status(None, None)
            return
        orig_w = self._pixmap.width()
        orig_h = self._pixmap.height()
        new_w = max(1, round(orig_w * self._zoom))
        new_h = max(1, round(orig_h * self._zoom))
        scaled = self._pixmap.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        # Ustaw dokładny rozmiar widgetu równy rozmiarowi pixmapy — zapewnia to prawidłowe działanie pasków przewijania
        self.image_label.setFixedSize(scaled.size())
        # Odśwież pasek statusu (bez współrzędnych)
        self.update_mouse_status(None, None)

    def close_app(self):
        print('zamykam')
        # Zapisz konfigurację przed zamknięciem
        self._save_configuration()
        # Close any opened PDF doc
        try:
            if self._pdf_doc is not None:
                try:
                    self._pdf_doc.close()
                except Exception:
                    pass
                self._pdf_doc = None
        except Exception:
            pass
        for filename in self._temp_pdf_files.append:
            os.remove(filename)
        self.close()

    def open_pdf(self):
        """Show file dialog and load selected PDF into the viewer."""
        # Pozwól wybrać tylko PDF
        path, _ = QFileDialog.getOpenFileName(self, 'Open PDF', '', 'PDF Files (*.pdf)')
        if path:
            # upewnij się, że PyMuPDF jest dostępny
            if fitz is None:
                self.image_label.setText('PyMuPDF is not installed')
                return
            self.load_pdf_file(path)

    def load_pdf_file(self, path: str):
        """Otwórz dokument PDF przy pomocy fitz i wczytaj pierwszą stronę jako obraz."""
        try:
            # Zamknij poprzedni dokument jeśli istnieje
            if self._pdf_doc is not None:
                try:
                    self._pdf_doc.close()
                except Exception:
                    pass
                self._pdf_doc = None

            doc = fitz.open(path)
            self._pdf_doc = doc
            self._pdf_page_count = doc.page_count
            return self.load_pdf_page(0)
        except Exception as e:
            self.image_label.setText(f'Error loading PDF: {e}')
            self._pdf_doc = None
            self._pixmap = None
            return False

    def _on_dropdown_changed(self, idx: int):
        self._load_template_pdf(idx)

    def load_pdf_page(self, index: int):
        """Renderuje stronę PDF jako obraz i ustawia ją w viewerze."""
        try:
            page = self._pdf_doc.load_page(index)
            # odczytaj oryginalne rozmiary strony w punktach PDF
            try:
                rect = page.rect
                page_w_pts = float(rect.width)
                page_h_pts = float(rect.height)
            except Exception:
                page_w_pts = None
                page_h_pts = None
            # renderowanie w wyższej rozdzielczości dla lepszej jakości
            # (możesz dostosować mat_scale aby zwiększyć rozdzielczość)
            mat_scale = 2.0
            mat = fitz.Matrix(mat_scale, mat_scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            png_bytes = pix.tobytes('png')
            qpix = QPixmap()
            qpix.loadFromData(png_bytes)
            if qpix.isNull():
                self.image_label.setText('Failed to render PDF page')
                self._pixmap = None
                return False
            self._pixmap = qpix
            # store PDF page size and render scale for coordinate conversion
            if page_w_pts is not None and page_h_pts is not None:
                self._pdf_page_width_pts = page_w_pts
                self._pdf_page_height_pts = page_h_pts
            else:
                self._pdf_page_width_pts = None
                self._pdf_page_height_pts = None
            self._pdf_render_scale = mat_scale
            self._zoom = 1.0
            self.apply_zoom()
            return True
        except Exception as e:
            self.image_label.setText(f'Error rendering page: {e}')
            self._pixmap = None
            return False

    def show_config_dialog(self):
        """Pokaż dialog konfiguracji."""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_config()
            # Przeładuj etykiety po zmianie konfiguracji
            self.reload_labels()

    def reload_labels(self):
        """Przeładuj etykiety z JSON-ów."""
        labels_folder = self._load_configuration()
        if labels_folder:
            self.label_manager = LabelManager(labels_folder)
            self.update_labels_from_json()
        else:
            QMessageBox.warning(self, 'Configuration', 'Please configure the labels folder first.')

    def update_labels_from_json(self):
        """Wczytaj etykiety do dropdown 'select product'."""
        if not self.label_manager:
            return

        label_names = self.label_manager.get_label_names()
        self.dropdown.blockSignals(True)
        self.dropdown.clear()

        for label_name in label_names:
            self.dropdown.addItem(label_name)

        self.dropdown.blockSignals(False)
        self.dropdown.setEnabled(len(label_names) > 0)
        self.dropdown.setCurrentIndex(-1)

        # Nie wybieraj automatycznie - niech użytkownik sam wybierze etykietę
        # Dropdown będzie pusty na początek


    def _load_configuration(self):
        """Wczytaj konfigurację z pliku w katalogu domowym."""
        config_path = self._get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('labels_folder', '')
        except Exception as e:
            print(f"Error loading configuration: {e}")
        return ''

    def _save_configuration(self):
        """Zapisz konfigurację do pliku w katalogu domowym."""
        if not self.label_manager:
            return

        config_path = self._get_config_path()
        try:
            config = {
                'labels_folder': self.label_manager.labels_folder
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def _get_config_path(self):
        """Zwróć ścieżkę do pliku konfiguracyjnego w katalogu domowym."""
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.mdrlabel')
        return os.path.join(config_dir, 'config.json')

    def _load_template_pdf(self, label_idx: int):
        """Wczytaj PDF szablon dla wybranej etykiety i jej pola formularza."""
        if not self.label_manager or label_idx < 0:
            return

        label_names = self.label_manager.get_label_names()
        if label_idx >= len(label_names):
            return

        label_name = label_names[label_idx]
        self.current_label = label_name

        # Pobierz dane etykiety
        label_data = self.label_manager.get_label(label_name)
        if not label_data:
            return

        # Wczytaj pola formularza dla tej etykiety
        fields = self.label_manager.get_fields(label_name)
        # najpierw wyczyść stare pola, potem je wyłącz, a włącz tylko te wymienione w JSONIE
        for field in self.editable_fields:
            self.editable_fields[field].clear()
            self.editable_fields[field].setEnabled(False)

        # wypełnij wartosciami
        for field in fields:
            if field['App_ID'] not in self.editable_fields:
                # obsluzyc sytuacje gdy JSON zawiera pole, którego nie ma w interfejsie
                continue
            self.editable_fields[field['App_ID']].setEnabled(True)
            if 'value' in field and field['value']:
                self.editable_fields[field['App_ID']].setText(field['value'])
            if 'editable' in field and not field['editable']:
                self.editable_fields[field['App_ID']].setEnabled(False)

       # self.populate_dynamic_fields(fields)

        # Wczytaj PDF szablon
        template_pdf = label_data.get('template_pdf', '')
        if template_pdf:
            # Załóż że PDF jest w folderze etykiet
            labels_folder = self.label_manager.labels_folder
            self._current_pdf_template_path = os.path.join(labels_folder, template_pdf)

            if os.path.exists(self._current_pdf_template_path):
                self.load_pdf_file(self._current_pdf_template_path)
            else:
                self.image_label.setText(f'Template PDF not found: {template_pdf}')

    def add_dynamic_data_to_pdf_template(self):
        label_data = self.label_manager.get_label(self.current_label)
        if label_data is None:
            return
        barcode_data = label_data['barcodes']
        UDI = {bcd['name']: OrderedDict({'GTIN':  self.label_manager.get_udi_di(self.current_label)}) for bcd in barcode_data}
        aaa = NamedTemporaryFile(suffix='.pdf', delete=False)
        aaa.close()
        self._temp_pdf_files.append(aaa.name)
        template_pdf = fitz.open(self._current_pdf_template_path)
        page = template_pdf[0]
        colour = (1, 0, 0)
        for bcd in barcode_data:
            print(bcd)
            for app_id in bcd['required_App_IDs']:
                UDI[bcd["name"]][app_id] = ''
        for field_to_fill in label_data['fields']:
            x = field_to_fill['pdf_position']['x']
            y = field_to_fill['pdf_position']['y']
            point = fitz.Point(x, y)
            if field_to_fill['App_ID'] in self.editable_fields:
                text = self.editable_fields[field_to_fill['App_ID']].text()
            else:
                text = f'Błąd: json zawiera niezdefiniowane pole {field_to_fill['App_ID']}'
            page.insert_text(point, text, fontsize=8, color=colour)
            for bcd in barcode_data:
                if field_to_fill['App_ID'] in bcd['required_App_IDs']:
                    if field_to_fill['App_ID'] in ('BEST_BEFORE', 'PROD_DATE'):
                        text_to_udi = text.split('-')
                        UDI[bcd["name"]][field_to_fill['App_ID']] = text_to_udi[0][2:4] + text_to_udi[1] + text_to_udi[2]
                    else:
                        UDI[bcd["name"]][field_to_fill['App_ID']]= text


        # barcode part
        for bcd in barcode_data:
            udi_pi_file = NamedTemporaryFile(dir='c:\\ump', suffix='.png', delete=False)
            udi_pi_file.close()
            # udi_di_pi = barcode.codex.Gs1_128_AI([(key, UDI[key],) for key in UDI], writer=barcode.writer.ImageWriter())
            udi_di_pi = barcode.codex.Gs1_128_AI(UDI[bcd["name"]], writer=barcode.writer.ImageWriter())
            print(udi_di_pi.get_fullcode())
            print(udi_di_pi.get_fullcode(astext=False))
            print(udi_pi_file.name)
            udi_di_pi.save(os.path.splitext(udi_pi_file.name)[0], {'format': 'PNG', })
            x1 = bcd['pdf_position']['x']
            x2 = bcd['pdf_position']['x'] + bcd['pdf_position']['width']
            y1 = bcd['pdf_position']['y']
            y2 = bcd['pdf_position']['y'] + bcd['pdf_position']['height']
            img_rect = fitz.Rect(x1, y1, x2, y2)

        # tworzenie kodu 2d
        # dm = encode ('(01)06009900408439(17)290319(30)01(10)240301'.encode('utf8'))
        # img = Image.frombytes('RGB', (dm.width, dm.height), dm.pixels)
        # img.save('/mnt/c/ump/aaa.png')
            page.insert_image(img_rect, filename=udi_pi_file.name)
        template_pdf.save(self._temp_pdf_files[-1])
        template_pdf.close()
        self.load_pdf_file(self._temp_pdf_files[-1])
        os.remove(udi_pi_file.name)



if __name__ == "__main__":
    print('otwieram')
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    w = MdrLabel(None)
    # Wczytaj etykiety przy starcie
    w.update_labels_from_json()
    w.show()
    app.exec()
