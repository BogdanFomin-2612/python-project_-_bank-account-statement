# Przypisywanie kategorii do transakcji na podstawie reguł z pliku JSON.

import json
import re

from monobank.bledy import BladWczytywania

KATEGORIA_INNE = "Inne"
KATEGORIA_WPLYWY = "Wpływy"


def wczytaj_reguly(sciezka):
    try:
        with open(sciezka, encoding="utf-8") as plik:
            return json.load(plik)
    except FileNotFoundError:
        raise BladWczytywania(f"Brak pliku z regułami: {sciezka}")
    except json.JSONDecodeError:
        raise BladWczytywania(f"Plik {sciezka} nie jest poprawnym JSON-em")


def pasuje(opis, wzorce):
    # Czy opis zawiera któryś z wzorców? Wzorce to wyrażenia regularne,
    # więc w JSON można wpisać zwykłe słowo albo np. "bar .*".
    for wzorzec in wzorce:
        if re.search(wzorzec, opis, re.IGNORECASE):
            return True
    return False


def czy_pominac(transakcja, reguly):
    # Np. przelewy do/ze "Skarbonki" - to przekładanie własnych pieniędzy, a nie wydatek.
    return pasuje(transakcja.opis, reguly["pomijane"])


def znajdz_kategorie(transakcja, reguly):
    if transakcja.kwota > 0:
        return KATEGORIA_WPLYWY

    # 1. słowa kluczowe z opisu - są dokładniejsze niż MCC, więc mają pierwszeństwo
    for kategoria, wzorce in reguly["slowa_kluczowe"].items():
        if pasuje(transakcja.opis, wzorce):
            return kategoria

    # 2. kod MCC (w JSON klucze są tekstem, dlatego str())
    mcc = str(transakcja.mcc)
    if mcc in reguly["mcc"]:
        return reguly["mcc"][mcc]

    return KATEGORIA_INNE


def kategoryzuj(transakcje, reguly):
    # Zwraca nową listę: bez pominiętych transakcji, każda z wpisaną kategorią.
    wynik = []
    for transakcja in transakcje:
        if czy_pominac(transakcja, reguly):
            continue
        transakcja.kategoria = znajdz_kategorie(transakcja, reguly)
        wynik.append(transakcja)
    return wynik
