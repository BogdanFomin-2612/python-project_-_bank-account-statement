# Przypisywanie kategorii do transakcji na podstawie reguł z pliku JSON.

import json
import re

from monobank.bledy import BladWczytywania

KATEGORIA_INNE = "Inne"
KATEGORIA_WPLYWY = "Wpływy"

# Zwrot pieniędzy (anulowana płatność) ma w wyciągu opis "Cancellation. <sklep>",
# np. "Cancellation. Dott". ^ = początek tekstu, \. = zwykła kropka.
WZORZEC_ZWROTU = r"^Cancellation\."


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


def czy_zwrot(transakcja, reguly):
    # Zwrot poznajemy na dwa sposoby, bo każdy format wyciągu opisuje go inaczej.
    # W CSV i XLSX bank pisze wprost "Cancellation. Dott".
    if re.match(WZORZEC_ZWROTU, transakcja.opis):
        return True
    # W PDF opisy są zamienione na ogólne nazwy ("Auto") i ten ślad znika.
    # Zostaje sam MCC: dodatnia kwota z kodem sklepu to nie wpływ, tylko
    # oddane pieniądze - prawdziwe wpływy mają inne kody (przelew, doładowanie).
    return transakcja.kwota > 0 and str(transakcja.mcc) in reguly["mcc"]


def znajdz_kategorie(transakcja, reguly):
    # Zwrot ma kwotę dodatnią, ale to nie jest wpływ. Przechodzi dalej i dostaje
    # kategorię anulowanego zakupu - ma ten sam MCC i nazwę sklepu w opisie.
    if transakcja.kwota > 0 and not transakcja.zwrot:
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
        transakcja.zwrot = czy_zwrot(transakcja, reguly)
        transakcja.kategoria = znajdz_kategorie(transakcja, reguly)
        wynik.append(transakcja)
    return wynik
