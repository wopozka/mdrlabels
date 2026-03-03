# JSON Schema - Definicja Etykiet Medycznych

## Struktura główna

```json
{
  "label_name": "string",
  "template_pdf": "string",
  "udi_di": "string",
  "fields": [array],
  "barcode": {object}
}
```

## Pola główne

### label_name
**Typ:** string  
**Wymagane:** tak  
**Opis:** Nazwa etykiety wyświetlana w dropdown-ie "select product"  
**Przykład:** `"Medical Device Label - Device A"`

### template_pdf
**Typ:** string  
**Wymagane:** tak  
**Opis:** Nazwa pliku PDF-a szablonu (bez ścieżki, znajduje się w folderze Templates)  
**Przykład:** `"device_a_template.pdf"`

### udi_di
**Typ:** string  
**Wymagane:** tak  
**Opis:** Unikalny identyfikator urządzenia medycznego (UDI-DI)  
**Przykład:** `"58063361"`

### fields
**Typ:** array  
**Wymagane:** tak  
**Opis:** Tablica pól formularza do wypełnienia  
**Liczba elementów:** 1 lub więcej

## Struktura pola (fields[])

**Ważne:** Każde pole identyfikowane jest poprzez **App_ID** (Application Identifier) - unikalny identyfikator zgodnie ze standardami zarządzania identyfikatorami aplikacji. App_ID jest używany wewnętrznie przez aplikację do mapowania wartości z formularza na pozycje w dokumencie PDF.

```json
{
  "name": "string",
  "key": "string",
  "type": "string",
  "format": "string",
  "pdf_position": {object},
  "font_size": "number"
}
```

### name
**Typ:** string  
**Wymagane:** tak  
**Opis:** Etykieta pola wyświetlana w formularzu  
**Przykład:** `"Use by date"`

### App_ID
**Typ:** string  
**Wymagane:** tak  
**Opis:** Application Identifier - unikalny identyfikator pola (używany wewnętrznie), zgodnie ze standardami zarządzania identyfikatorami aplikacji  
**Przykład:** `"use_by_date"`
**Uwaga:** Powinno być unique w obrębie pola "fields". Używa konwencji snake_case (małe litery z podkreśleniami)

### type
**Typ:** string  
**Wymagane:** tak  
**Dozwolone wartości:** `"text"`, `"date"`, `"number"`, `"alphanumeric"`  
**Opis:** Typ danych pola  
**Przykład:** `"text"`

### format
**Typ:** string  
**Wymagane:** nie (opcjonalne)  
**Opis:** Format danych (dla walidacji i podpowiedzi)  
**Przykłady:**
- `"DD/MM/YYYY"` - data w formacie europejskim
- `"YYYY-MM-DD"` - data w formacie ISO
- `"alphanumeric"` - znaki alfanumeryczne
- `"numeric"` - tylko cyfry

### pdf_position
**Typ:** object  
**Wymagane:** tak  
**Opis:** Pozycja pola na PDF-ie w punktach (1/72 cala)

```json
{
  "x": "number",
  "y": "number",
  "width": "number",
  "height": "number"
}
```

- **x:** Pozycja od lewej krawędzi (w punktach PDF)
- **y:** Pozycja od górnej krawędzi (w punktach PDF)
- **width:** Szerokość pola
- **height:** Wysokość pola

**Przykład:**
```json
"pdf_position": {"x": 50, "y": 100, "width": 80, "height": 15}
```

### font_size
**Typ:** number  
**Wymagane:** nie (opcjonalne, domyślnie 10)  
**Opis:** Rozmiar czcionki tekstu na PDF-ie  
**Przykład:** `10`, `12`, `14`

## Struktura barcode

```json
{
  "type": "string",
  "format": "string",
  "pdf_position": {object},
  "required_fields": [array]
}
```

### type
**Typ:** string  
**Wymagane:** tak  
**Dozwolone wartości:** `"gs1-128"`, `"datamatrix"`, `"code128"`, `"ean13"`  
**Opis:** Typ kodu kreskowego  
**Przykład:** `"gs1-128"`

### format
**Typ:** string  
**Wymagane:** tak  
**Opis:** Szablon formatu kodu kreskowego (może zawierać zmienne {key})  
**Przykłady:**
- `"{udi_di}{serial_number}"` - UDI-DI + numer seryjny
- `"{udi_di}{lot_number}{patient_id}"` - UDI-DI + lot + pacjent
- `"{udi_di}"` - samo UDI-DI

### pdf_position
**Typ:** object (ten sam format co dla pola)  
**Wymagane:** tak  
**Opis:** Pozycja kodu kreskowego na PDF-ie  
**Przykład:**
```json
"pdf_position": {"x": 200, "y": 100, "width": 150, "height": 40}
```

### required_fields
**Typ:** array  
**Wymagane:** tak  
**Opis:** Lista kluczy pól wymaganych do wygenerowania kodu kreskowego  
**Przykład:** `["serial_number"]`  
**Uwaga:** Wartości muszą odpowiadać kluczom pól zdefiniowanych w "fields"

## Pełny przykład

```json
{
  "label_name": "Medical Device - Sterile Gauze",
  "template_pdf": "gauze_template.pdf",
  "udi_di": "58063361",
  "fields": [
    {
      "name": "Use by date",
      "App_ID": "use_by_date",
      "type": "date",
      "format": "DD/MM/YYYY",
      "pdf_position": {"x": 50, "y": 100, "width": 80, "height": 15},
      "font_size": 10
    },
    {
      "name": "Batch Number",
      "App_ID": "batch",
      "type": "alphanumeric",
      "format": "alphanumeric",
      "pdf_position": {"x": 50, "y": 130, "width": 80, "height": 15},
      "font_size": 10
    },
    {
      "name": "Manufacturing Date",
      "App_ID": "manufacturing_date",
      "type": "date",
      "format": "DD/MM/YYYY",
      "pdf_position": {"x": 50, "y": 160, "width": 80, "height": 15},
      "font_size": 10
    },
    {
      "name": "Serial Number",
      "App_ID": "serial_number",
      "type": "alphanumeric",
      "pdf_position": {"x": 200, "y": 100, "width": 100, "height": 15},
      "font_size": 10
    }
  ],
  "barcode": {
    "type": "gs1-128",
    "format": "{udi_di}{serial_number}",
    "pdf_position": {"x": 200, "y": 130, "width": 150, "height": 40},
    "required_fields": ["serial_number"]
  }
}
```

## Walidacja

Przy wczytywaniu JSON-a aplikacja sprawdza:
- ✓ Czy wszystkie pola wymagane są obecne
- ✓ Czy wartości pól są prawidłowego typu
- ✓ Czy klucze pól w "barcode.required_fields" istnieją w "fields"
- ✓ Czy pliki JSON są poprawnym JSON-em

## Tips & Tricks

### Szukanie współrzędnych

1. Otwórz PDF w aplikacji
2. Hover nad elementem
3. Pasek statusu pokaże współrzędne: `PDF X: 50   PDF Y: 100`
4. Skopiuj wartości do JSON-a

### Rozmiar pola

- **width** i **height** to przybliżone wymiary na PDF-ie
- Mogą być zmieniane bez wpływu na funkcjonalność
- Przydatne dla wyrównania z szablonią

### Kody kreskowe

- GS1-128: Używaj dla standardowych kodów międzynarodowych
- DataMatrix: Kompaktowy, przydatny gdy miejsca jest mało
- Format može zawierać dowolne kombinacje UDI-DI i pól

### Format daty

Sugerowane formaty:
- `"DD/MM/YYYY"` - Europejski
- `"MM/DD/YYYY"` - Amerykański
- `"YYYY-MM-DD"` - ISO (międzynarodowy standard)

## Błędy i rozwiązania

**"Error loading JSON: ..."**
- Sprawdź czy JSON jest poprawny (bez błędów w składni)
- Użyj online JSON validator

**Pola nie pojawiają się**
- Sprawdź czy "fields" nie jest pusta
- Sprawdź czy pola zawierają "name" i "key"

**Kod kreskowy się nie generuje**
- Upewnij się że wszystkie pola z "required_fields" są wypełnione
- Sprawdź czy "format" zawiera prawidłowe {klucze}

