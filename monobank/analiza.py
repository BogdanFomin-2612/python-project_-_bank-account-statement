# Obliczenia na liście transakcji.

from datetime import timedelta

import numpy as np

OKNO_SREDNIEJ = 7         # średnia krocząca z 7 dni (tydzień)
MIN_MIESIECY_PROGNOZA = 3  # z 1-2 punktów prosta "przewidywałaby" cokolwiek


def czy_wydatek(transakcja):
    # Wydatek ma kwotę ujemną. Zwrot jest dodatni, ale też go liczymy,
    # bo "+= -kwota" odejmuje go od wydatków (np. anulowany przejazd Dott).
    return transakcja.kwota < 0 or transakcja.zwrot


def sumy_wedlug_kategorii(transakcje):
    # Słownik: kategoria -> [suma w UAH, suma w PLN].
    sumy = {}
    for transakcja in transakcje:
        if not czy_wydatek(transakcja):
            continue
        if transakcja.kategoria not in sumy:
            sumy[transakcja.kategoria] = [0.0, 0.0]
        sumy[transakcja.kategoria][0] += -transakcja.kwota
        # PLN znamy tylko wtedy, gdy płatność była w złotówkach
        if transakcja.waluta == "PLN":
            sumy[transakcja.kategoria][1] += -transakcja.kwota_w_walucie

    # zamiana na listę krotek (kategoria, uah, pln), od największego wydatku
    wynik = []
    for kategoria, kwoty in sumy.items():
        wynik.append((kategoria, kwoty[0], kwoty[1]))
    return sorted(wynik, key=lambda krotka: krotka[1], reverse=True)


def wydatki_dzienne(transakcje):
    # Tablica numpy: ile wydano każdego dnia, od pierwszego do ostatniego dnia wyciągu.
    sumy = {}
    for transakcja in transakcje:
        if not czy_wydatek(transakcja):
            continue
        dzien = transakcja.data.date()
        sumy[dzien] = sumy.get(dzien, 0.0) + -transakcja.kwota

    if not sumy:
        return np.array([])

    # Dni bez wydatków też się liczą (jako 0), inaczej średnia byłaby zawyżona.
    kwoty = []
    dzien = min(sumy)
    while dzien <= max(sumy):
        kwoty.append(sumy.get(dzien, 0.0))
        dzien += timedelta(days=1)
    return np.array(kwoty)


def statystyki(kwoty):
    # Podstawowe statystyki z numpy, zwracane jako słownik.
    return {
        "suma": np.sum(kwoty),
        "srednia": np.mean(kwoty),
        "mediana": np.median(kwoty),
        "odchylenie": np.std(kwoty),
        "max": np.max(kwoty),
        "min": np.min(kwoty),
    }


def srednia_kroczaca(kwoty, okno=OKNO_SREDNIEJ):
    # Splot z [1/7, 1/7, ...] = średnia z każdych kolejnych 7 dni.
    # mode="valid" - liczymy tylko tam, gdzie mamy pełne 7 dni.
    if len(kwoty) < okno:
        return np.array([])
    return np.convolve(kwoty, np.ones(okno) / okno, mode="valid")


def wydatki_miesieczne(transakcje):
    # Zwraca krotkę: (lista miesięcy np. "2026-07", tablica numpy z sumami).
    sumy = {}
    for transakcja in transakcje:
        if not czy_wydatek(transakcja):
            continue
        miesiac = transakcja.data.strftime("%Y-%m")
        sumy[miesiac] = sumy.get(miesiac, 0.0) + -transakcja.kwota

    miesiace = sorted(sumy)  # tekst "RRRR-MM" sortuje się dobrze jak daty
    kwoty = np.array([sumy[miesiac] for miesiac in miesiace])
    return miesiace, kwoty


def prognoza_na_nastepny_miesiac(kwoty_miesieczne):
    # Regresja liniowa: dopasowujemy prostą y = a*x + b, gdzie x to numer miesiąca
    # (0, 1, 2, ...), i odczytujemy jej wartość dla kolejnego numeru.
    if len(kwoty_miesieczne) < MIN_MIESIECY_PROGNOZA:
        return None
    x = np.arange(len(kwoty_miesieczne))
    a, b = np.polyfit(x, kwoty_miesieczne, 1)
    prognoza = a * len(kwoty_miesieczne) + b
    return max(prognoza, 0.0)  # prosta może zejść poniżej zera, a wydatki nie


def suma_cashbacku(transakcje):
    # Przy zwrocie bank cofa cashback (wartość ujemna), więc suma od razu to uwzględnia.
    return sum(transakcja.cashback for transakcja in transakcje)


def suma_prowizji(transakcje):
    return sum(transakcja.prowizja for transakcja in transakcje)
