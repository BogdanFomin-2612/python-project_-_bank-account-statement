# Funkcje czytające wyciągi Monobank z plików CSV, XLSX i PDF.

import csv
import io
import os
import re
from datetime import datetime

import openpyxl
import pdfplumber

from monobank.transakcja import Transakcja
from monobank.bledy import BladWczytywania, NieobslugiwanyFormat

FORMAT_DATY = "%d.%m.%Y %H:%M:%S"   # np. 23.09.2026 21:17:24

# Kolumny wyciągu (w każdym z trzech formatów są te same i w tej samej kolejności):
# 0 data i godzina, 1 opis, 2 MCC, 3 kwota w UAH, 4 kwota w walucie operacji,
# 5 waluta operacji, 6 kurs, 7 prowizja, 8 cashback, 9 saldo
LICZBA_KOLUMN = 10

# Pierwsza komórka wiersza z nagłówkami tabeli - po niej poznajemy, gdzie
# zaczynają się transakcje w XLSX i który wiersz pominąć w PDF.
NAGLOWEK_TABELI = "Date and time"

# Z tekstu kwoty zostawiamy tylko cyfry, kropkę, przecinek i minus. Wyrzuca to
# spację rozdzielającą tysiące w PDF ("-1 170.65") oraz pauzę "—", którą
# Monobank wpisuje w pustej kolumnie.
WZORZEC_LICZBY = re.compile(r"[^\d.,-]")


def czytaj_linie(sciezka):
    # Generator: oddaje plik linia po linii, zamiast wczytywać go całego do pamięci.
    with open(sciezka, encoding="utf-8", newline="") as plik:
        for linia in plik:
            yield linia


def na_liczbe(wartosc):
    # W CSV i PDF kwoty są tekstem, w XLSX przychodzą już jako liczby.
    if wartosc is None:
        return 0.0
    if not isinstance(wartosc, str):
        return float(wartosc)

    tekst = WZORZEC_LICZBY.sub("", wartosc).replace(",", ".")
    if tekst in ("", "-"):   # pusta kolumna
        return 0.0
    return float(tekst)


def na_tekst(wartosc):
    # W PDF długie napisy są łamane na dwie linie ("Products and\nsupermarkets").
    return str(wartosc).replace("\n", " ").strip()


def zbuduj_transakcje(wiersz, numer):
    # Wszystkie trzy formaty dają ten sam układ kolumn, więc transakcję
    # składamy w jednym miejscu.
    if len(wiersz) != LICZBA_KOLUMN:
        raise BladWczytywania(f"Wiersz {numer}: oczekiwano {LICZBA_KOLUMN} kolumn, jest {len(wiersz)}")

    try:
        return Transakcja(
            data=datetime.strptime(na_tekst(wiersz[0]), FORMAT_DATY),
            opis=na_tekst(wiersz[1]),
            mcc=int(wiersz[2]),
            kwota=na_liczbe(wiersz[3]),
            kwota_w_walucie=na_liczbe(wiersz[4]),
            waluta=na_tekst(wiersz[5]),
            prowizja=na_liczbe(wiersz[7]),
            cashback=na_liczbe(wiersz[8]),
        )
    except ValueError:
        raise BladWczytywania(f"Wiersz {numer}: niepoprawna data, MCC lub kwota")


def wczytaj_csv(sciezka):
    transakcje = []
    czytnik = csv.reader(czytaj_linie(sciezka))

    naglowek = next(czytnik, None)  # pierwszy wiersz to nazwy kolumn - pomijamy
    if naglowek is None:
        raise BladWczytywania("Plik jest pusty")

    for numer, wiersz in enumerate(czytnik, start=2):
        if not wiersz:  # pusta linia
            continue
        transakcje.append(zbuduj_transakcje(wiersz, numer))

    return transakcje


def wczytaj_xlsx(sciezka):
    # Monobank nazywa plik ".xls", ale w środku to zwykły xlsx. openpyxl patrzy
    # na rozszerzenie i odmawia go otworzyć, dlatego podajemy mu otwarty plik
    # zamiast ścieżki - wtedy sprawdza samą zawartość.
    with open(sciezka, "rb") as plik:
        arkusz = openpyxl.load_workbook(plik, data_only=True).active

    transakcje = []
    tabela = False   # czy doszliśmy już do wiersza z nagłówkami

    for numer, wiersz in enumerate(arkusz.iter_rows(values_only=True), start=1):
        if not tabela:
            # na górze pliku bank wypisuje dane klienta, a dopiero niżej tabelę
            tabela = wiersz[0] == NAGLOWEK_TABELI
            continue
        if wiersz[0] is None:   # pusty wiersz
            continue
        transakcje.append(zbuduj_transakcje(wiersz, numer))

    if not tabela:
        raise BladWczytywania("Nie znaleziono tabeli z transakcjami")
    return transakcje


def wytnij_pdf(sciezka):
    # Monobank podpisuje wyciąg elektronicznie, więc plik ".pdf" to tak naprawdę
    # koperta z podpisem. Prawdziwy dokument siedzi w środku - wycinamy go
    # od napisu "%PDF" do ostatniego "%%EOF".
    with open(sciezka, "rb") as plik:
        dane = plik.read()

    poczatek = dane.find(b"%PDF")
    koniec = dane.rfind(b"%%EOF")
    if poczatek == -1 or koniec == -1:
        raise BladWczytywania("W pliku nie ma dokumentu PDF")

    return dane[poczatek:koniec + len(b"%%EOF")]


def wczytaj_pdf(sciezka):
    transakcje = []
    numer = 0

    # BytesIO sprawia, że pdfplumber czyta wycięte bajty tak, jakby to był plik na dysku
    with pdfplumber.open(io.BytesIO(wytnij_pdf(sciezka))) as pdf:
        for strona in pdf.pages:
            for tabela in strona.extract_tables():
                for wiersz in tabela:
                    numer += 1
                    if wiersz[0] == NAGLOWEK_TABELI:   # nagłówek powtarza się na każdej stronie
                        continue
                    transakcje.append(zbuduj_transakcje(wiersz, numer))

    if not transakcje:
        raise BladWczytywania("Nie znaleziono tabeli z transakcjami")
    return transakcje


def wczytaj_plik(sciezka):
    # Wybiera funkcję czytającą na podstawie rozszerzenia pliku.
    rozszerzenie = os.path.splitext(sciezka)[1].lower()
    if rozszerzenie == ".csv":
        return wczytaj_csv(sciezka)
    if rozszerzenie in (".xlsx", ".xls"):
        return wczytaj_xlsx(sciezka)
    if rozszerzenie == ".pdf":
        return wczytaj_pdf(sciezka)
    raise NieobslugiwanyFormat(f"Nieobsługiwany format pliku: {rozszerzenie}")
