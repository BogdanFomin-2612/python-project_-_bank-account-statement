# Wypisywanie wyników na ekran.


def wypisz_sumy_kategorii(sumy):
    print("=" * 50)
    for kategoria, uah, pln in sumy:
        tekst = f"{kategoria + ':':<13} {uah:>9.2f} UAH"
        # kategorie opłacane tylko w hrywnach nie mają kwoty w PLN
        if pln > 0:
            tekst += f" / {pln:>8.2f} PLN"
        print(tekst)


def wypisz_cashback_i_prowizje(cashback, prowizja):
    print(f"\nCashback: {cashback:.2f} UAH")
    print(f"Prowizje banku: {prowizja:.2f} UAH")


def wypisz_statystyki_dzienne(stat, srednie_tygodniowe):
    print("\nWydatki dzienne (UAH):")
    print(f"  średnio:    {stat['srednia']:>9.2f}")
    print(f"  mediana:    {stat['mediana']:>9.2f}")
    print(f"  odchylenie: {stat['odchylenie']:>9.2f}")
    print(f"  najwięcej:  {stat['max']:>9.2f}")
    print(f"  najmniej:   {stat['min']:>9.2f}")
    # ostatni element średniej kroczącej = średnia z ostatniego tygodnia wyciągu
    if len(srednie_tygodniowe) > 0:
        print(f"  średnio w ostatnim tygodniu: {srednie_tygodniowe[-1]:.2f}")


def wypisz_miesiace(miesiace, kwoty, prognoza):
    print("\nWydatki miesięczne (UAH):")
    for miesiac, kwota in zip(miesiace, kwoty):
        print(f"  {miesiac}: {kwota:>10.2f}")
    if prognoza is None:
        print("  Za mało miesięcy na prognozę (potrzeba co najmniej 3).")
    else:
        print(f"  Prognoza na następny miesiąc: {prognoza:.2f}")
