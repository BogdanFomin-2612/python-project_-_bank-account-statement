# Wypisywanie wyników na ekran.


def wypisz_sumy_kategorii(sumy):
    print("=" * 50)
    for kategoria, uah, pln in sumy:
        tekst = f"{kategoria + ':':<13} {uah:>9.2f} UAH"
        # kategorie opłacane tylko w hrywnach nie mają kwoty w PLN
        if pln > 0:
            tekst += f" / {pln:>8.2f} PLN"
        print(tekst)
