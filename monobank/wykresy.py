# Wykresy matplotlib - zapisywane do plików PNG, bez wyświetlania okna.

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def zapisz_wykres_kategorii(sumy, sciezka):
    # sumy - lista krotek (kategoria, uah, pln) z analiza.sumy_wedlug_kategorii().
    kategorie = [kategoria for kategoria, uah, pln in sumy]
    kwoty = [uah for kategoria, uah, pln in sumy]
    suma_calkowita = sum(kwoty)

    plt.figure(figsize=(9, 8))
    # tab10 ma tylko 10 kolorów i powtarzałby je przy >10 kategoriach
    kolory = plt.get_cmap("tab20").colors
    # bez labels na samych wycinkach - nazwa kategorii i kwota są w legendzie
    wycinki, _, _ = plt.pie(kwoty, autopct="%1.1f%%", colors=kolory)
    plt.title(f"Wydatki według kategorii - łącznie {suma_calkowita:.2f} UAH")

    etykiety_legendy = [f"{kategoria}: {kwota:.2f} UAH" for kategoria, kwota in zip(kategorie, kwoty)]
    # legenda w lewym dolnym rogu, poza samym wykresem
    plt.legend(wycinki, etykiety_legendy, loc="upper left", bbox_to_anchor=(-0.4, 0.15))

    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    plt.savefig(sciezka, bbox_inches="tight")
    plt.close()
