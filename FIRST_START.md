# 🚀 Pierwszy Start - MDR Label

## Krok 1: Instalacja (5 minut)

```bash
# Przejdź do folderu projektu
cd C:\Users\pwawrzyniak\PycharmProjects\mdrlabels

# Zainstaluj zależności
pip install -r requirements.txt
```

## Krok 2: Przygotowanie Folderu (2 minuty)

Utwórz folder do przechowywania etykiet i szablonów (np. `C:\mdr_labels_data\`):

```
C:\mdr_labels_data\
├── example_label.json          (pliki JSON z definicjami etykiet)
├── label_device_a.json
├── label_device_b.json
└── (tutaj umieszczysz też PDF-y szablonów)
```

W jednym folderze przechowywane są:
- **JSON-y** z definicjami etykiet
- **PDF-y** szablonów

## Krok 3: Dodanie Przykładowych Plików (1 minuta)

Projekt zawiera przykładowe JSON-y:
- `example_label.json`
- `label_device_a.json`
- `label_device_b.json`

Skopiuj je do folderu `C:\mdr_labels_data\`

## Krok 4: Uruchomienie Aplikacji (1 minuta)

```bash
python mdrlabel.py
```

## Krok 5: Konfiguracja (2 minuty)

1. Aplikacja się uruchomi
2. Przejdź do: **Settings → Configuration**
3. Kliknij **Browse...** przy **Labels folder**
   - Wskaż: `C:\mdr_labels_data\`
4. Kliknij **OK**

## Krok 6: Test (2 minuty)

1. W dropdown-ie **"select product / page"** powinna się pojawić lista etykiet:
   - Medical Device Label 001
   - Medical Device Label - Device A
   - Medical Device Label - Device B
2. Kliknij na każdą z nich
3. Powinna się zmienić zawartość pól formularza

## Gotowe! 🎉

Aplikacja jest teraz gotowa do użytku!

### Dalsze Kroki

1. **Chcesz dodać swoją etykietę?**
   - Stwórz nowy plik JSON w `C:\mdr_labels_data\` (patrz JSON_SCHEMA.md)
   - Restart aplikacji

2. **Chcesz zobaczyć szablon PDF?**
   - Umieść PDF w `C:\mdr_labels_data\`
   - File → Open PDF

3. **Szukasz więcej informacji?**
   - Przeczytaj: QUICKSTART.md
   - Przeczytaj: USER_GUIDE.md
   - Przeczytaj: JSON_SCHEMA.md

## Troubleshooting

**"Etykiety się nie pojawiły w dropdown-ie?"**
- Sprawdź czy folder jest poprawnie skonfigurowany
- Sprawdź czy JSON-y są w folderze
- Restart aplikacji

**"ModuleNotFoundError: No module named 'PyQt6'"**
- Uruchom: `pip install PyQt6`

**"ModuleNotFoundError: No module named 'pymupdf'"**
- Uruchom: `pip install PyMuPDF`

**Więcej problemów?**
- Przeczytaj: USER_GUIDE.md → Troubleshooting

---

**Czas do pełnej konfiguracji: ~15 minut** ⏱️

