# Własne wyjątki projektu.


# Plik istnieje, ale nie da się z niego odczytać transakcji.
class BladWczytywania(Exception):
    pass


# Plik ma rozszerzenie, którego program nie obsługuje.
class NieobslugiwanyFormat(Exception):
    pass
