# Przewodnik Użytkownika - MDR Label

## Pierwsze uruchomienie

### 1. Konfiguracja folderów

Przy pierwszym uruchomieniu aplikacja będzie pytać o konfigurację:

1. Wybierz **Settings → Configuration**
2. **Labels folder (JSON)**: Wskaż folder gdzie będą pliki JSON-ów z definicjami etykiet
3. **Templates folder (PDF)**: Wskaż folder gdzie będą pliki PDF-ów szablonów
4. Kliknij **OK**

### 2. Dodanie etykiet

1. Umieść pliki JSON-ów w folderze "Labels folder"
2. Umieść pliki PDF-ów szablonów w folderze "Templates folder"
3. Restart aplikacji - etykiety pojawią się w dropdown-ie "select product"

## Interfejs aplikacji

### Panel lewy (formularz)
- **select product / page**: Dropdown do wyboru etykiety lub strony PDF-a
- Dynamiczne pola do wypełnienia (generowane na podstawie JSON-a)
- Pola "Use by date", "Batch", "Manufacturing date" (domyślne)

### Panel prawy (podgląd PDF)
- Wyświetla wybrane PDF-y
- Zoom: Ctrl + scroll
- Panning: Prawy klik + drag
- Statusbar: Pokazuje współrzędne kursora (PDF X, PDF Y, Zoom %)

### Menu
- **File → Open PDF**: Otwórz plik PDF-a szablonu
- **File → Exit**: Zamknij aplikację
- **Settings → Configuration**: Zmień foldery źródłowe

## Workflow typowego użytkownika

### Scenariusz 1: Dodanie nowej etykiety medycznej

1. **Przygotuj PDF szablon**
   - Stwórz lub weź istniejący plik PDF-a szablonu etykiety

2. **Stwórz plik JSON**
   - Nazwa: `label_my_device.json`
   - Zawartość: Definicja etykiety z polami i współrzędnymi
   - Zapisz w folderze "Labels folder"

3. **Umieść PDF**
   - Skopiuj plik PDF-a do folderu "Templates folder"

4. **Restart aplikacji**
   - Nowa etykieta pojawi się w dropdown-ie

5. **Test**
   - Wybierz etykietę z dropdown-u
   - Sprawdź czy pojawił się się prawidłowy formularz
   - Opcjonalnie otwórz PDF, aby sprawdzić współrzędne

### Scenariusz 2: Szukanie współrzędnych dla nowego pola

1. **Otwórz PDF** (File → Open PDF)

2. **Hover nad elementem** na PDF-ie gdzie chcesz umieścić tekst

3. **Odczytaj współrzędne** z statusbaru (np. "PDF X: 150   PDF Y: 200")

4. **Skopiuj do JSON-a**
   ```json
   "pdf_position": {"x": 150, "y": 200, "width": 80, "height": 15}
   ```

## Pola formularza

### Dynamiczne pola
Aplikacja automatycznie generuje pola na podstawie JSON-a. Każde pole może mieć:
- Własną etykietę (label)
- Własny typ danych (text, date, number, alphanumeric)
- Swoją pozycję na PDF-ie
- Unikalny **App_ID** (Application Identifier) - identyfikator zgodnie ze standardami zarządzania identyfikatorami aplikacji
### Domyślne pola
- **Use by date**: Data ważności (zapamiętana w panelu)
- **Batch**: Numer partii (zapamiętana w panelu)
- **Manufacturing date**: Data produkcji (zapamiętana w panelu)

## Praca z PDF-ami

### Otwieranie PDF-a
1. File → Open PDF
2. Wybierz plik PDF-a

### Nawigacja
- **Scroll**: Przewijanie (Ctrl+scroll to zoom)
- **Prawy klik + drag**: Panning (przesuwanie widoku)
- **Ctrl + scroll**: Zoom in/out
- **Dropdown "select product / page"**: Zmiana strony (gdy PDF jest otwarty)

### Odczyt współrzędnych
- Hover nad elementem na PDF-ie
- Statusbar pokaże: `PDF X: XXX   PDF Y: YYY   Zoom: 100%`

## Kody kreskowe

### Obsługiwane typy
- **gs1-128**: Standard międzynarodowy dla opieki zdrowotnej
- **datamatrix**: Kompaktowy, przydatny gdy miejsca mało
- **code128**: Ogólny standard
- **ean13**: Europejski kod produktu

### Jak to działa
1. JSON definiuje format kodu (np. `{udi_di}{serial_number}`)
2. Aplikacja łączy wartości pól w jedną wartość
3. Generator kodów kreskowych tworzy kod na podstawie tej wartości

## Ustawienia aplikacji

### Zmiana folderów źródłowych
1. Settings → Configuration
2. Zmień ścieżkę dla folderu Labels
3. Kliknij OK - aplikacja przeładuje etykiety

### Reset
Jeśli coś się zepsuło:
1. Zamknij aplikację
2. Usuń plik konfiguracji (zwykle w `%APPDATA%\MDRLabel\`)
3. Uruchom aplikację od nowa

## Troubleshooting

### Etykiety nie pojawiają się w dropdown-ie
- ✗ Nie skonfigurowano ścieżek → Settings → Configuration
- ✗ JSON-y nie są w prawidłowym folderze
- ✗ JSON ma błędy w składni → Sprawdź console
- ✓ Restart aplikacji może pomóc

### Pola formularza się nie generują
- ✗ JSON nie zawiera "fields"
- ✗ "fields" jest puste
- ✓ Sprawdzić console pod kątem błędów

### PDF nie otwiera się
- ✗ Plik nie jest PDF-em
- ✗ PyMuPDF nie jest zainstalowany → `pip install PyMuPDF`
- ✗ Plik PDF jest uszkodzony

### Współrzędne PDF-a są niedokładne
- Mogą być niedokładne przy zoom != 100%
- Zawsze wyszukuj współrzędne przy zoom = 100%
- Statusbar pokazuje dokładne wartości

## Zaawansowane

### Edycja JSON-ów bez restartu
1. Zmodyfikuj plik JSON
2. Settings → Configuration → OK (bez zmieniania ścieżek)
3. Etykiety będą przeładowane

### Backup i restore
- Wszystkie dane są w folderach JSON i PDF
- Proste cofnięcie: skopiuj wcześniejszy plik JSON

### Integracja z systemami
- JSON format pozwala na łatwą integrację
- Można automatycznie generować JSON-y na podstawie bazy danych
- Kod kreskowy może być w dowolnym formacie

## Skróty klawiszowe

| Skrót | Działanie |
|-------|-----------|
| Ctrl + Scroll | Zoom PDF-a |
| Prawy klik + drag | Panning PDF-a |
| Alt + O | Open PDF (File menu) |
| Alt + S | Settings menu |
| Alt + C | Configuration |

## FAQ

**P: Czy mogę edytować pliki JSON w Excelu?**  
O: Nie, JSON to format tekstowy. Użyj edytora tekstu (Notepad++, Visual Studio Code, itp.)

**P: Czy mogę mieć więcej niż 3 domyślne pola?**  
O: Tak, dodaj je do JSON-a jako pola dynamiczne

**P: Czy mogę używać różnych formatów dat?**  
O: Tak, ustaw "format" w JSON-ie (DD/MM/YYYY, YYYY-MM-DD, itd.)

**P: Jakie maksymalne rozmiary plików PDF?**  
O: Brak ograniczeń w teorii, ale bardzo duże PDF-y mogą być wolne

**P: Czy mogę eksportować etykiety?**  
O: Aktualnie nie, ale można dodać tę funkcję w przyszłości

## Wsparcie

Jeśli napotkasz problemy:
1. Sprawdź JSON_SCHEMA.md
2. Sprawdzć console'ę pod kątem błędów
3. Sprawdź czy wszystkie zależności są zainstalowane

