# Wypisywanie wyników na ekran i zapis raportu do pliku tekstowego.

import os


def wypisz_sumy_kategorii(sumy):
    linie = ["=" * 50]
    for kategoria, uah, pln in sumy:
        tekst = f"{kategoria + ':':<13} {uah:>9.2f} UAH"
        # kategorie opłacane tylko w hrywnach nie mają kwoty w PLN
        if pln > 0:
            tekst += f" / {pln:>8.2f} PLN"
        linie.append(tekst)
    print("\n".join(linie))
    return linie


def wypisz_cashback_i_prowizje(cashback, prowizja):
    linie = ["", f"Cashback: {cashback:.2f} UAH", f"Prowizje banku: {prowizja:.2f} UAH"]
    print("\n".join(linie))
    return linie


def wypisz_statystyki_dzienne(stat, srednie_tygodniowe):
    linie = [
        "",
        "Wydatki dzienne (UAH):",
        f"  średnio:    {stat['srednia']:>9.2f}",
        f"  mediana:    {stat['mediana']:>9.2f}",
        f"  odchylenie: {stat['odchylenie']:>9.2f}",
        f"  najwięcej:  {stat['max']:>9.2f}",
        f"  najmniej:   {stat['min']:>9.2f}",
    ]
    # ostatni element średniej kroczącej = średnia z ostatniego tygodnia wyciągu
    if len(srednie_tygodniowe) > 0:
        linie.append(f"  średnio w ostatnim tygodniu: {srednie_tygodniowe[-1]:.2f}")
    print("\n".join(linie))
    return linie


def wypisz_miesiace(miesiace, kwoty, prognoza):
    linie = ["", "Wydatki miesięczne (UAH):"]
    for miesiac, kwota in zip(miesiace, kwoty):
        linie.append(f"  {miesiac}: {kwota:>10.2f}")
    if prognoza is None:
        linie.append("  Za mało miesięcy na prognozę (potrzeba co najmniej 3).")
    else:
        linie.append(f"  Prognoza na następny miesiąc: {prognoza:.2f}")
    print("\n".join(linie))
    return linie


def zapisz_raport(linie, sciezka):
    # linie - lista wierszy raportu zebrana z funkcji wypisz_* w main.py.
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as plik:
        plik.write("\n".join(linie) + "\n")
