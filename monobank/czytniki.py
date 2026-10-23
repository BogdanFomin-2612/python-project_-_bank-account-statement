# Funkcje czytające wyciągi Monobank z plików.

import csv
import os
from datetime import datetime

from monobank.transakcja import Transakcja
from monobank.bledy import BladWczytywania, NieobslugiwanyFormat

FORMAT_DATY = "%d.%m.%Y %H:%M:%S"   # np. 23.09.2026 21:17:24

# Kolumny w CSV z Monobanku (w tej kolejności):
# 0 data i godzina, 1 opis, 2 MCC, 3 kwota w UAH, 4 kwota w walucie operacji,
# 5 waluta operacji, 6 kurs, 7 prowizja, 8 cashback, 9 saldo
LICZBA_KOLUMN = 10
BRAK_WARTOSCI = "—"   # Monobank wpisuje ten znak (pauzę), gdy kolumna jest pusta


def czytaj_linie(sciezka):
    # Generator: oddaje plik linia po linii, zamiast wczytywać go całego do pamięci.
    with open(sciezka, encoding="utf-8", newline="") as plik:
        for linia in plik:
            yield linia


def na_liczbe(tekst):
    # Pusta kolumna to "—", a nie pusty tekst - float("—") by się wywalił, więc zwracamy 0.
    if tekst == BRAK_WARTOSCI:
        return 0.0
    return float(tekst)


def wczytaj_csv(sciezka):
    transakcje = []
    czytnik = csv.reader(czytaj_linie(sciezka))

    naglowek = next(czytnik, None)  # pierwszy wiersz to nazwy kolumn - pomijamy
    if naglowek is None:
        raise BladWczytywania("Plik jest pusty")

    for numer, wiersz in enumerate(czytnik, start=2):
        if not wiersz:  # pusta linia
            continue
        if len(wiersz) != LICZBA_KOLUMN:
            raise BladWczytywania(f"Wiersz {numer}: oczekiwano {LICZBA_KOLUMN} kolumn, jest {len(wiersz)}")

        try:
            transakcja = Transakcja(
                data=datetime.strptime(wiersz[0], FORMAT_DATY),
                opis=wiersz[1],
                mcc=int(wiersz[2]),
                kwota=float(wiersz[3]),
                kwota_w_walucie=float(wiersz[4]),
                waluta=wiersz[5],
                prowizja=na_liczbe(wiersz[7]),
                cashback=na_liczbe(wiersz[8]),
            )
        except ValueError:
            raise BladWczytywania(f"Wiersz {numer}: niepoprawna data, MCC lub kwota")

        transakcje.append(transakcja)

    return transakcje


def wczytaj_plik(sciezka):
    # Wybiera funkcję czytającą na podstawie rozszerzenia pliku.
    rozszerzenie = os.path.splitext(sciezka)[1].lower()
    if rozszerzenie == ".csv":
        return wczytaj_csv(sciezka)
    raise NieobslugiwanyFormat(f"Nieobsługiwany format pliku: {rozszerzenie}")
