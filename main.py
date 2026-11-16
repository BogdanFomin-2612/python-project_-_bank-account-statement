# Punkt wejścia programu. Na razie: wczytanie wyciągu, kategoryzacja i wypisanie transakcji.

from datetime import datetime

from monobank.czytniki import wczytaj_plik
from monobank.kategorie import wczytaj_reguly, kategoryzuj
from monobank.analiza import (sumy_wedlug_kategorii, suma_cashbacku, suma_prowizji,
                              wydatki_dzienne, statystyki, srednia_kroczaca,
                              wydatki_miesieczne, prognoza_na_nastepny_miesiac)
from monobank.raport import (wypisz_sumy_kategorii, wypisz_cashback_i_prowizje,
                             wypisz_statystyki_dzienne, wypisz_miesiace, zapisz_raport)
from monobank.wykresy import zapisz_wykres_kategorii
from monobank.bledy import BladWczytywania, NieobslugiwanyFormat

PLIK_REGUL = "kategorie.json"
KATALOG_RAPORTOW = "raporty"


def main():
    # strip('"') - Windows dodaje cudzysłowy przy "Kopiuj jako ścieżkę"
    sciezka = input("Podaj ścieżkę do pliku z wyciągiem (np. dane/example_report.csv): ").strip().strip('"')

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

    linie_transakcji = [f"{numer:3}. {transakcja}" for numer, transakcja in enumerate(transakcje, start=1)]
    print("\n".join(linie_transakcji))

    sumy = sumy_wedlug_kategorii(transakcje)
    raport = list(linie_transakcji)
    raport += wypisz_sumy_kategorii(sumy)
    raport += wypisz_cashback_i_prowizje(suma_cashbacku(transakcje), suma_prowizji(transakcje))

    dzienne = wydatki_dzienne(transakcje)
    if len(dzienne) > 0:
        raport += wypisz_statystyki_dzienne(statystyki(dzienne), srednia_kroczaca(dzienne))

    miesiace, kwoty = wydatki_miesieczne(transakcje)
    raport += wypisz_miesiace(miesiace, kwoty, prognoza_na_nastepny_miesiac(kwoty))

    podsumowanie = f"Wczytano transakcji: {len(wszystkie)}, pominięto: {len(wszystkie) - len(transakcje)}"
    print(f"\n{podsumowanie}")
    raport += ["", podsumowanie]

    znacznik_czasu = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    nazwa_raportu = f"{KATALOG_RAPORTOW}/raport_{znacznik_czasu}.txt"
    zapisz_raport(raport, nazwa_raportu)
    print(f"\nZapisano raport do pliku: {nazwa_raportu}")

    if sumy:
        nazwa_wykresu = f"{KATALOG_RAPORTOW}/wykres_kategorii_{znacznik_czasu}.png"
        zapisz_wykres_kategorii(sumy, nazwa_wykresu)
        print(f"Zapisano wykres do pliku: {nazwa_wykresu}")


if __name__ == "__main__":
    main()
