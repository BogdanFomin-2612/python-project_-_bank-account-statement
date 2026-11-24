# Analizator wyciągów Monobank
# **Autor:** Bohdan Fomin, nr albumu 83044, grupa INLS5
Projekt zaliczeniowy z przedmiotu **Programowanie w Pythonie** (WSB Merito Gdańsk).

Program konsolowy, który wczytuje wyciąg z karty Monobank (CSV, XLSX lub PDF),
przypisuje każdej transakcji kategorię (np. Spożywcze, Taxi, Paliwo), pokazuje, ile pieniędzy
poszło na każdą kategorię, i liczy statystyki wydatków.

Karta jest w hrywnach (UAH), ale mieszkam w Polsce i płacę głównie w złotówkach,
dlatego program pokazuje kwoty w obu walutach.

## Uruchomienie

Potrzebny jest Python 3.10 lub nowszy oraz biblioteki **numpy**, **matplotlib**,
**openpyxl** (pliki XLSX) i **pdfplumber** (pliki PDF).
Wszystkie potrzebne biblioteki są w pliku `requirements.txt`:

```
pip install -r requirements.txt
python main.py
```

### Jeśli `.venv` się zepsuje

Na Windows `python.exe` instalowany przez `py`/winget trzyma wersje w
`C:\Users\<użytkownik>\AppData\Local\Python\pythoncore-X.Y-64\`. Po aktualizacji
Pythona stara wersja bywa usuwana, a stworzone wcześniej `.venv` nadal na nią
wskazuje - stąd błąd `did not find executable at '...\pythoncore-X.Y-64\python.exe'`.

Naprawa: uruchom `setup_venv.ps1` (PowerShell) - wykrywa uszkodzone `.venv`,
tworzy je od nowa i instaluje zależności:

```
.\setup_venv.ps1
```

Program zapyta o ścieżkę do pliku z wyciągiem. Do sprawdzenia programu jest
przykładowy plik `dane/example_report.csv` – ma taki sam format jak prawdziwy
wyciąg z Monobanku i obejmuje 7 miesięcy, ale dane są wymyślone. Własny wyciąg
można pobrać w aplikacji Monobank w jednym z trzech formatów: CSV, XLSX lub PDF.

## Struktura projektu

```
├── main.py              # punkt wejścia: pyta o plik i wypisuje wyniki
├── kategorie.json       # reguły przypisywania kategorii
├── requirements.txt     # potrzebne biblioteki (numpy, matplotlib, openpyxl, pdfplumber)
├── setup_venv.ps1       # tworzy/naprawia .venv i instaluje zależności (Windows)
├── dane/
│   └── example_report.csv  # przykładowy wyciąg (prawdziwe nie trafiają do repozytorium)
├── raporty/             # tu trafiają zapisane raporty .txt i wykresy .png (nie w repozytorium)
└── monobank/            # pakiet z całą logiką
    ├── transakcja.py    # klasa Transakcja
    ├── czytniki.py      # wczytywanie wyciągu z pliku CSV, XLSX i PDF
    ├── kategorie.py     # przypisywanie kategorii i rozpoznawanie zwrotów
    ├── analiza.py       # sumy według kategorii i statystyki (numpy)
    ├── raport.py        # wypisywanie podsumowania i zapis raportu do pliku .txt
    ├── wykresy.py       # wykres kołowy wydatków według kategorii (matplotlib)
    └── bledy.py         # własne wyjątki
```

## Jak to działa

### 1. Wczytanie pliku

Funkcja `wczytaj_plik()` sprawdza rozszerzenie pliku i wywołuje odpowiednią
funkcję: `wczytaj_csv()`, `wczytaj_xlsx()` albo `wczytaj_pdf()`. Nieznane
rozszerzenie kończy się wyjątkiem `NieobslugiwanyFormat`.

We wszystkich trzech formatach tabela ma te same 10 kolumn w tej samej kolejności,
dlatego każdy czytnik tylko wyciąga wiersze, a sam obiekt `Transakcja` powstaje
w jednym wspólnym miejscu – w funkcji `zbuduj_transakcje()`. Dzięki temu ten sam
kod nie jest napisany trzy razy.

Kolumny biorę po numerze (`wiersz[0]`, `wiersz[3]` itd.), a nie po nazwie, bo tak
jest prościej. Z wyciągu biorę tylko to, co jest potrzebne: datę, opis, kod MCC,
kwotę w UAH, kwotę w walucie operacji, walutę, prowizję i cashback.

Jeśli plik jest pusty albo jakiś wiersz ma złą liczbę kolumn czy niepoprawną datę,
program rzuca własny wyjątek `BladWczytywania` i wypisuje, w którym wierszu jest błąd.

#### CSV

Plik jest czytany przez generator `czytaj_linie()`, który oddaje go linia po linii
(`yield`), zamiast wczytywać całość do pamięci. Te linie trafiają do `csv.reader`.

#### XLSX

Monobank nazywa ten plik `.xls`, ale w środku jest zwykły xlsx. `openpyxl` patrzy
na samo rozszerzenie i odmawia otwarcia pliku (`InvalidFileException`), dlatego
podaję mu **otwarty plik zamiast ścieżki** – wtedy sprawdza już samą zawartość.

Nad tabelą bank wypisuje kilkanaście wierszy z danymi klienta (imię, adres, IBAN),
więc transakcje zaczynam czytać dopiero od wiersza z nagłówkami, czyli od komórki
`Date and time`.

#### PDF

Wyciąg PDF jest podpisany elektronicznie, więc plik `.pdf` to tak naprawdę koperta
z podpisem (PKCS#7) – `pdfplumber` nie potrafi jej otworzyć. Prawdziwy dokument
siedzi w środku, dlatego funkcja `wytnij_pdf()` czyta plik binarnie i wycina kawałek
od napisu `%PDF` do ostatniego `%%EOF`. Wynik trafia do `pdfplumber` przez
`io.BytesIO`, czyli tak, jakby to był osobny plik na dysku.

Same transakcje wyciągam metodą `extract_tables()`, bo bank rysuje je w tabeli –
to pewniejsze niż szukanie wzorców w zwykłym tekście. Nagłówek tabeli powtarza się
na każdej stronie, więc wiersze zaczynające się od `Date and time` pomijam.

W PDF trzeba uważać na dwie rzeczy. Po pierwsze, długie napisy są łamane na dwie
linie (`Products and\nsupermarkets`), dlatego funkcja `na_tekst()` zamienia znak
nowej linii na spację. Po drugie, tysiące są rozdzielone spacją (`-1 170.65`),
więc `float()` sam by sobie z tym nie poradził.

#### Zamiana tekstu na liczbę

Funkcja `na_liczbe()` zostawia z tekstu tylko cyfry, kropkę, przecinek i minus –
wyrażeniem regularnym `[^\d.,-]`. Usuwa to od razu dwie przeszkody: spację
rozdzielającą tysiące w PDF oraz pauzę `—`, którą Monobank wpisuje w pustej
kolumnie (`float("—")` wywaliłby program). W XLSX kwoty przychodzą już jako liczby,
więc wtedy funkcja po prostu je zwraca.

#### Sprawdzenie

Ten sam wyciąg za wrzesień pobrany w trzech formatach daje identyczny wynik:
98 transakcji, 14 921,07 UAH wydatków i te same sumy w każdej kategorii.

### 2. Pomijanie niepotrzebnych transakcji

Niektóre operacje nie są prawdziwymi wydatkami, więc je pomijam:

- **Skarbonka** (po ukraińsku „Копилка”) – Monobank zaokrągla płatności i odkłada
  resztę do skarbonki. To przekładanie moich własnych pieniędzy, a nie wydatek.

**Zwroty** nie są pomijane. Np. Dott (hulajnogi) najpierw blokuje 7 zł, a po przejeździe
oddaje całość albo część. Taki zwrot ma kwotę dodatnią, ale to nie jest wpływ na konto,
więc odejmuję go od kategorii zakupu (tu: Transport). Dzięki temu widać, ile przejazd
naprawdę kosztował.

Zwrot rozpoznaję na dwa sposoby, bo każdy format wyciągu opisuje go inaczej:

1. W CSV i XLSX bank pisze wprost `Cancellation. Dott` – wyłapuje to wyrażenie
   regularne `^Cancellation\.`.
2. W PDF opisy są zamienione na ogólne nazwy kategorii banku (`Auto`, `Travel`,
   `Products and supermarkets`) i ten ślad znika. Zostaje sam kod MCC: dodatnia
   kwota z kodem sklepu to nie wpływ, tylko oddane pieniądze. Prawdziwe wpływy
   mają inne kody – przelew albo doładowanie karty.

### 3. Przypisanie kategorii

Każda transakcja dostaje kategorię w tej kolejności:

1. kwota dodatnia (wpływ na konto) → `Wpływy` – chyba że to zwrot (patrz wyżej),
2. w opisie jest słowo kluczowe z `kategorie.json` (np. `youtube`) → kategoria tego słowa,
3. kod MCC transakcji jest w `kategorie.json` → kategoria z tego kodu,
4. nic nie pasuje → `Inne`.

**MCC** (Merchant Category Code) to kod rodzaju sklepu, który bank dostaje przy
każdej płatności kartą. Np. 5411 to supermarkety, a 4121 to taksówki. Dzięki temu
nie muszę wpisywać każdego sklepu osobno – Biedronka, Lidl i Spar mają ten sam kod.

Słowa kluczowe są sprawdzane przed MCC, bo są dokładniejsze. Wyszukiwanie odbywa się
przez wyrażenia regularne (`re.search`) bez względu na wielkość liter.

### 4. Podsumowanie

Funkcja `sumy_wedlug_kategorii()` przechodzi po wszystkich wydatkach i sumuje kwoty
w słowniku `kategoria -> [suma w UAH, suma w PLN]`. Potem zamienia go na listę krotek
i sortuje od największego wydatku. Wpływy nie są tu liczone, a zwroty zmniejszają
sumę swojej kategorii.

Program liczy też łączny **cashback** i **prowizje** banku z kolumn
`Cashback amount` i `Commission`. Pusta wartość jest w nich oznaczona znakiem `—`,
dlatego funkcja `na_liczbe()` zamienia go na 0.

### 5. Statystyki (numpy)

- `wydatki_dzienne()` – tablica `np.array` z sumą wydatków za każdy dzień okresu.
  Dni bez wydatków też się liczą (jako 0), inaczej średnia byłaby zawyżona.
  Liczę po dniach, a nie po pojedynczych transakcjach, bo blokada Dott i jej zwrot
  w tym samym dniu się znoszą i nie psują mediany.
- `statystyki()` – słownik z wynikami `np.mean`, `np.median`, `np.std`,
  `np.max` i `np.min`.
- `srednia_kroczaca()` – średnia z 7 kolejnych dni liczona przez `np.convolve`.
- `wydatki_miesieczne()` – suma wydatków w każdym miesiącu.
- `prognoza_na_nastepny_miesiac()` – regresja liniowa `np.polyfit`: przez sumy
  miesięczne prowadzę prostą `y = a*x + b`, a prognoza to jej wartość dla
  następnego miesiąca. Liczę ją dopiero od 3 miesięcy – przy mniejszej liczbie
  program pisze, że danych jest za mało.

### 6. Zapis raportu i wykres (matplotlib)

Funkcje `wypisz_*()` z `raport.py` oprócz wypisywania na ekran zwracają też swoje
wiersze jako listę tekstu. `main.py` zbiera te listy w jeden raport i zapisuje go
funkcją `zapisz_raport()` do pliku `raporty/raport_<data>_<godzina>.txt`.

Funkcja `zapisz_wykres_kategorii()` z `wykresy.py` rysuje wykres kołowy wydatków
według kategorii (na podstawie `sumy_wedlug_kategorii()`) i zapisuje go jako
`raporty/wykres_kategorii_<data>_<godzina>.png`. Łączna suma wydatków jest w
tytule wykresu, a w legendzie w lewym dolnym rogu – nazwa każdej kategorii razem
z kwotą w UAH (paleta `tab20`, żeby kolory się nie powtarzały przy >10 kategoriach).
Wykres nie jest wyświetlany na ekranie (`matplotlib.use("Agg")`) – program
konsolowy nie powinien czekać na zamknięcie okna.

Katalog `raporty/` jest tworzony automatycznie przy pierwszym zapisie i nie
trafia do repozytorium (jest w `.gitignore`), podobnie jak prawdziwe wyciągi.

## Plik kategorie.json

Wszystkie reguły są w pliku JSON, więc żeby dodać nowy sklep albo kategorię,
nie trzeba zmieniać kodu.

```json
{
    "pomijane": ["копилка", "^jar$", "^partial withdrawal$"],
    "slowa_kluczowe": {
        "Subskrypcje": ["youtube", "spotify", "netflix"]
    },
    "mcc": {
        "5411": "Spożywcze",
        "4121": "Taxi"
    }
}
```

- `pomijane` – transakcje, których opis pasuje do któregoś wzorca, są pomijane
  (skarbonka to „Копилка” w CSV i XLSX, ale `Jar` oraz `Partial withdrawal` w PDF),
- `slowa_kluczowe` – kategoria i lista słów, które mają być w opisie,
- `mcc` – kod MCC i kategoria (kody są w cudzysłowie, bo w JSON klucze muszą być tekstem).

## Przykładowy wynik

Dla pliku `dane/example_report.csv` (lista transakcji skrócona):

```
Podaj ścieżkę do pliku z wyciągiem (np. dane/example_report.csv): dane/example_report.csv
  1. 29.10.2026 22:29    -317.04 UAH /  -26.53 PLN  Taxi          Bolt
  2. 29.10.2026 13:05    -617.71 UAH /  -51.69 PLN  Inne          Rossmann
  3. 28.10.2026 17:58    -454.29 UAH /  -38.00 PLN  Rozrywka      Cinema City
...
==================================================
Spożywcze:     28877.32 UAH /  2417.80 PLN
Paliwo:        12289.96 UAH /  1027.71 PLN
Odzież:         9333.06 UAH /   779.93 PLN
Gastronomia:    8819.63 UAH /   739.17 PLN
Inne:           6309.03 UAH /   403.40 PLN
...
Apteka:          821.60 UAH /    68.86 PLN

Cashback: 366.77 UAH
Prowizje banku: 23.79 UAH

Wydatki dzienne (UAH):
  średnio:       422.30
  mediana:       143.96
  odchylenie:    637.64
  najwięcej:    3201.86
  najmniej:        0.00
  średnio w ostatnim tygodniu: 612.50

Wydatki miesięczne (UAH):
  2026-04:   12754.21
  2026-05:   11734.67
  ...
  2026-10:   18015.06
  Prognoza na następny miesiąc: 13942.47

Wczytano transakcji: 269, pominięto: 85

Zapisano raport do pliku: raporty/raport_2026-11-16_16-09-49.txt
Zapisano wykres do pliku: raporty/wykres_kategorii_2026-11-16_16-09-49.png
```

Jeśli płatność była w hrywnach, pokazywana jest tylko kwota w UAH.

## Co jeszcze do zrobienia

- ✅ statystyki na numpy (średnia, mediana, odchylenie standardowe, trend) – **Done**
- ✅ zapis raportu do pliku tekstowego i wykresy (matplotlib) – **Done**
- ✅ wczytywanie wyciągów w formacie XLSX i PDF – **Done**
- menu w konsoli,
- generator przykładowych danych do pokazania programu
