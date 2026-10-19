# Analizator wyciągów Monobank
# Bohdan Fomin 83044 INLS5
Projekt zaliczeniowy z przedmiotu **Programowanie w Pythonie** (WSB Merito Gdańsk).

Program konsolowy, który wczytuje wyciąg z karty Monobank, przypisuje każdej
transakcji kategorię (np. Spożywcze, Taxi, Paliwo) i pokazuje, ile pieniędzy
poszło na każdą kategorię.

Karta jest w hrywnach (UAH), ale mieszkam w Polsce i płacę głównie w złotówkach,
dlatego program pokazuje kwoty w obu walutach.

## Uruchomienie

Potrzebny jest Python 3.10 lub nowszy. Obecna wersja korzysta tylko
z biblioteki standardowej, więc nic nie trzeba instalować.

```
python main.py
```

Program zapyta o ścieżkę do pliku z wyciągiem. Do sprawdzenia programu jest
przykładowy plik `dane/example_report.csv` – ma taki sam format jak prawdziwy
wyciąg z Monobanku, ale dane są wymyślone. Własny wyciąg w formacie CSV można
pobrać w aplikacji Monobank.

## Struktura projektu

```
├── main.py              # punkt wejścia: pyta o plik i wypisuje wyniki
├── kategorie.json       # reguły przypisywania kategorii
├── dane/
│   └── example_report.csv  # przykładowy wyciąg (prawdziwe nie trafiają do repozytorium)
└── monobank/            # pakiet z całą logiką
    ├── transakcja.py    # klasa Transakcja
    ├── czytniki.py      # wczytywanie pliku CSV
    ├── kategorie.py     # przypisywanie kategorii
    ├── analiza.py       # liczenie sum według kategorii
    ├── raport.py        # wypisywanie podsumowania
    └── bledy.py         # własne wyjątki
```

## Jak to działa

### 1. Wczytanie pliku

Funkcja `wczytaj_plik()` sprawdza rozszerzenie pliku i wywołuje odpowiednią
funkcję. Na razie obsługiwany jest tylko CSV (`wczytaj_csv()`).

Plik jest czytany przez generator `czytaj_linie()`, który oddaje go linia po linii
(`yield`). Te linie trafiają do `csv.reader`, a z każdego wiersza powstaje obiekt
klasy `Transakcja`.

Kolumny biorę po numerze (`wiersz[0]`, `wiersz[3]` itd.), a nie po nazwie, bo tak
jest prościej. Z wyciągu biorę tylko to, co jest potrzebne: datę, opis, kod MCC,
kwotę w UAH, kwotę w walucie operacji i walutę.

Jeśli plik jest pusty albo jakiś wiersz ma złą liczbę kolumn czy niepoprawną datę,
program rzuca własny wyjątek `BladWczytywania` i wypisuje, w którym wierszu jest błąd.

### 2. Pomijanie niepotrzebnych transakcji

Niektóre operacje nie są prawdziwymi wydatkami, więc je pomijam:

- **Skarbonka** (po ukraińsku „Копилка”) – Monobank zaokrągla płatności i odkłada
  resztę do skarbonki. To przekładanie moich własnych pieniędzy, a nie wydatek.
- **Dott** – przejazdy hulajnogami. W moim wyciągu każdy przejazd był od razu
  anulowany (płatność + zwrot), więc tylko zaśmiecały listę.

### 3. Przypisanie kategorii

Każda transakcja dostaje kategorię w tej kolejności:

1. kwota dodatnia (wpływ na konto) → `Wpływy`,
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
i sortuje od największego wydatku. Wpływy nie są tu liczone.

## Plik kategorie.json

Wszystkie reguły są w pliku JSON, więc żeby dodać nowy sklep albo kategorię,
nie trzeba zmieniać kodu.

```json
{
    "pomijane": ["копилка", "dott"],
    "slowa_kluczowe": {
        "Subskrypcje": ["youtube", "spotify", "netflix"]
    },
    "mcc": {
        "5411": "Spożywcze",
        "4121": "Taxi"
    }
}
```

- `pomijane` – transakcje, których opis pasuje do któregoś wzorca, są pomijane,
- `slowa_kluczowe` – kategoria i lista słów, które mają być w opisie,
- `mcc` – kod MCC i kategoria (kody są w cudzysłowie, bo w JSON klucze muszą być tekstem).

## Przykładowy wynik

```
Podaj ścieżkę do pliku z wyciągiem: dane/wyciag.csv
  1. 23.09.2026 21:17    -186.88 UAH /  -15.70 PLN  Spożywcze     ZABKA
  2. 22.09.2026 19:17    -356.40 UAH /  -29.99 PLN  Subskrypcje   YouTube
  3. 19.09.2026 22:31    -219.22 UAH /  -18.51 PLN  Taxi          Uber
  4. 10.09.2026 18:58    5000.00 UAH                Wpływy        Przelew przychodzący
==================================================
Subskrypcje:     356.40 UAH /    29.99 PLN
Taxi:            219.22 UAH /    18.51 PLN
Spożywcze:       186.88 UAH /    15.70 PLN

Wczytano transakcji: 6, pominięto: 2
```

Jeśli płatność była w hrywnach, pokazywana jest tylko kwota w UAH.

## Co jeszcze do zrobienia

- statystyki na numpy (średnia, mediana, odchylenie standardowe, trend),
- zapis raportu do pliku tekstowego i wykresy (matplotlib),
- menu w konsoli,
- wczytywanie wyciągów w formacie XLSX i PDF.
