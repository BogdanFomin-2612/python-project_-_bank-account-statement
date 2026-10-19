# Klasa opisująca jedną transakcję z wyciągu Monobank.


class Transakcja:
    def __init__(self, data, opis, mcc, kwota, kwota_w_walucie, waluta):
        self.data = data                        # obiekt datetime
        self.opis = opis                        # np. "ZABKA", "Bolt"
        self.mcc = mcc                          # kod rodzaju sprzedawcy (Merchant Category Code)
        self.kwota = kwota                      # kwota w UAH: minus = wydatek, plus = wpływ
        self.kwota_w_walucie = kwota_w_walucie  # kwota w walucie operacji (np. w PLN)
        self.waluta = waluta                    # waluta operacji, np. "UAH", "PLN"
        self.kategoria = ""                     # uzupełniana później w kategorie.py

    def __str__(self):
        data_tekst = self.data.strftime("%d.%m.%Y %H:%M")
        kwota_tekst = f"{self.kwota:>9.2f} UAH"
        # przy płatności w obcej walucie dopisujemy oryginalną kwotę, np. "-186.88 UAH / -15.70 PLN"
        if self.waluta != "UAH":
            kwota_tekst += f" / {self.kwota_w_walucie:>7.2f} {self.waluta}"
        return f"{data_tekst}  {kwota_tekst:<27}  {self.kategoria:<12}  {self.opis}"
