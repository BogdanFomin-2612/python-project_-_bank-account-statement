# Obliczenia na liście transakcji.


def sumy_wedlug_kategorii(transakcje):
    # Słownik: kategoria -> [suma w UAH, suma w PLN]. Liczymy tylko wydatki (kwota < 0).
    sumy = {}
    for transakcja in transakcje:
        if transakcja.kwota >= 0:
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
