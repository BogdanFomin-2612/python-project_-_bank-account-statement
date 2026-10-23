# Obliczenia na liście transakcji.


def sumy_wedlug_kategorii(transakcje):
    # Słownik: kategoria -> [suma w UAH, suma w PLN]. Liczymy wydatki (kwota < 0)
    # i zwroty. Zwrot ma kwotę dodatnią, więc "+= -kwota" odejmuje go od sumy kategorii.
    sumy = {}
    for transakcja in transakcje:
        if transakcja.kwota >= 0 and not transakcja.zwrot:
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


def suma_cashbacku(transakcje):
    # Przy zwrocie bank cofa cashback (wartość ujemna), więc suma od razu to uwzględnia.
    return sum(transakcja.cashback for transakcja in transakcje)


def suma_prowizji(transakcje):
    return sum(transakcja.prowizja for transakcja in transakcje)
