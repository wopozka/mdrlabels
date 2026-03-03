# Szybki Start

## 1. Instalacja

Otwórz terminal w katalogu projektu i wykonaj:

```bash
pip install -r requirements.txt
```

## 2. Przygotowanie

### Utwórz jeden folder na dane:
```
C:\path\to\labels_data\        (folder z JSON-ami i PDF-ami)
├── example_label.json
├── label_device_a.json
├── label_device_b.json
└── (tutaj umieszczysz też PDF-y szablonów)
```

W **jednym folderze** przechowywane są:
- Pliki JSON z definicjami etykiet
- Pliki PDF szablonów

### Skopiuj pliki JSON-ów do folderu:
Projekt zawiera przykładowe pliki:
- `example_label.json`
- `label_device_a.json`
- `label_device_b.json`

## 3. Konfiguracja aplikacji

1. Uruchom program:
```bash
python mdrlabel.py
```

2. Przejdź do **Settings → Configuration**

3. Wskaż ścieżkę:
   - **Labels folder**: Wskaż folder z plikami JSON-ów i PDF-ów

4. Kliknij **OK**

## 4. Użytkowanie

1. **Wybierz etykietę** z dropdown-u "select product" - pojawią się odpowiednie pola formularza
2. **Wypełnij pola** danych (Use by date, Batch, Manufacturing date, etc.)
3. **(Opcjonalnie) Otwórz PDF** aby zobaczyć szablon:
   - File → Open PDF
   - Wskaż plik PDF-a z folderu Labels
4. Hover nad PDF-em aby zobaczyć współrzędne w statusbarze

## 5. Struktura JSON-a

Każdy plik JSON powinien zawierać:

```json
{
  "label_name": "Nazwa etykiety (wyświetlana w dropdown-ie)",
  "template_pdf": "nazwa_szablonu.pdf",
  "udi_di": "58063361",
  "fields": [
    {
      "name": "Nazwa wyświetlana w formularzu",
      "key": "klucz_pola",
      "type": "text",
      "format": "DD/MM/YYYY",
      "pdf_position": {"x": 50, "y": 100, "width": 80, "height": 15},
      "font_size": 10
    }
  ],
  "barcode": {
    "type": "gs1-128 lub datamatrix",
    "format": "{udi_di}{serial_number}",
    "pdf_position": {"x": 200, "y": 100, "width": 150, "height": 40},
    "required_fields": ["serial_number"]
  }
}
```

## 6. Współrzędne PDF-a

Współrzędne w pliku JSON odnoszą się do **punktów PDF** (1/72 cala).
Aby znaleźć współrzędne:

1. Otwórz PDF w aplikacji (File → Open PDF)
2. Hover nad elementem na PDF-ie
3. Pasek statusu pokaże: `PDF X: XXX   PDF Y: YYY   Zoom: 100%`
4. Skopiuj wartości X i Y do JSON-a

## Przykład workflow-u

1. Mam szablon PDF-a dla urządzenia medycznego
2. Tworzę plik JSON z definicją pól i ich współrzędnymi na PDF-ie
3. Kopię plik JSON do folderu Labels
4. Uruchamiam aplikację
5. Aplikacja wczytuje JSON-y i wyświetla je w dropdown-ie
6. Wybieram etykietę → generują się pola formularza
7. Wypełniam dane
8. (Opcjonalnie) Otwieram PDF, żeby zobaczyć gdzie będą umieszczane dane

## Troubleshooting

**"Please configure the labels folder first"**
- Przejdź do Settings → Configuration i wskaż folder

**Pola nie pojawiają się po wyborze etykiety**
- Sprawdź czy JSON zawiera pole "fields" z tablicą pól
- Sprawdzaj console (terminal) pod kątem błędów

**PDF nie otwiera się**
- Upewnij się że PyMuPDF (fitz) jest zainstalowany: `pip install PyMuPDF`
- Sprawdź czy plik jest poprawnym PDF-em

**Błędy przy importach**
- Uruchom `pip install -r requirements.txt` ponownie
- Sprawdź czy Python 3.7+ jest zainstalowany: `python --version`


