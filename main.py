# Punkt wejścia programu. Na razie: wczytanie wyciągu, kategoryzacja i wypisanie transakcji.

from monobank.czytniki import wczytaj_plik
from monobank.kategorie import wczytaj_reguly, kategoryzuj
from monobank.analiza import sumy_wedlug_kategorii, suma_cashbacku, suma_prowizji
from monobank.raport import wypisz_sumy_kategorii, wypisz_cashback_i_prowizje
from monobank.bledy import BladWczytywania, NieobslugiwanyFormat

PLIK_REGUL = "kategorie.json"


def main():
    # strip('"') - Windows dodaje cudzysłowy przy "Kopiuj jako ścieżkę"
    sciezka = input("Podaj ścieżkę do pliku z wyciągiem: ").strip().strip('"')

    try:
        wszystkie = wczytaj_plik(sciezka)
        reguly = wczytaj_reguly(PLIK_REGUL)
    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {sciezka}")
        return
    except (BladWczytywania, NieobslugiwanyFormat) as blad:
        print(f"Błąd: {blad}")
        return

    transakcje = kategoryzuj(wszystkie, reguly)

    for numer, transakcja in enumerate(transakcje, start=1):
        print(f"{numer:3}. {transakcja}")

    wypisz_sumy_kategorii(sumy_wedlug_kategorii(transakcje))
    wypisz_cashback_i_prowizje(suma_cashbacku(transakcje), suma_prowizji(transakcje))

    print(f"\nWczytano transakcji: {len(wszystkie)}, pominięto: {len(wszystkie) - len(transakcje)}")


if __name__ == "__main__":
    main()
