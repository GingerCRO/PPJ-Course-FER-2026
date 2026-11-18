import sys

# Čvor generativnog stabla
# Mogućnosti: nezavršni znak, uniformni znak ili epsilon
class Cvor:
    def __init__(self, naziv, redak=None, vrijednost=None):
        self.naziv = naziv
        self.redak = redak
        self.vrijednost = vrijednost
        self.podcvorovi = []

    # Ispis: čvor, podčvorovi, dubina
    def ispisi(self, dubina=0):
        razmaci = " " * dubina

        if self.vrijednost is not None and self.redak is not None:
            print(f"{razmaci}{self.naziv} {self.redak} {self.vrijednost}")
        else:
            print(f"{razmaci}{self.naziv}")

        for cvor in self.podcvorovi:
            cvor.ispisi(dubina + 1)

    # Dodaj podčvor na kraj
    def dodaj_podcvor(self, cvor):
        self.podcvorovi.append(cvor)

globalni_token = []     # Lista svih znakova s ulaza
index = 0               # Pozicija trenutnog znaka u listi

# Funkcija učitava izlaz leksičkog analizatora sa standardnog ulaza
# Vraća listu trojki (tip, redak, vrijednost)
def ucitaj_tokene_iz_datoteke():
    linije = sys.stdin.read().splitlines()
    tokeni = []

    for linija in linije:
        if not linija.strip():      # Preskoči prazne linije
            continue
        dijelovi = linija.split(' ', 2)     # npr. redak "IDN 4 rez" parsiraj u ["IDN", "4", "rez"]
        tip = dijelovi[0]
        redak = int(dijelovi[1])
        vrijednost = dijelovi[2] if len(dijelovi) > 2 else ""
        tokeni.append((tip, redak, vrijednost))     # Dodaj tokene u listu

    return tokeni

# Vrati znak na trenutnoj poziciji
# Vraća trojku (tip, redak, vrijednost) ili None ako je ulaz prazan
def trenutni_token():
    if index < len(globalni_token):
        return globalni_token[index]
    return None

# Funkcija pomiče index na sljedeću poziciju
def sljedeci_token():
    global index        # Mijenja se globalna varijabla, a ne lokalna unutar funkcije
    index += 1

# Funkcija ispisuje sintaksnu pogrešku i prekida izvođenje programa
# Ispisuje znak na kojem je greška nastala
def pogreska(ocekivano_ili_trenutni=None):
    trenutniToken = trenutni_token()
    if trenutniToken is not None:       # Postoji greška
        print(f"err {trenutniToken[0]} {trenutniToken[1]} {trenutniToken[2]}")
    else:                               # Ulaz je prazan
        print("err kraj")
    sys.exit(0)

# Funkcija parsira početni nezavršni znak <program>
# Vraća korijen stabla
def program_parsiraj():
    cvor = Cvor("<program>")

    podcvor = parse_lista_naredbi()
    cvor.dodaj_podcvor(podcvor)

    return cvor

# Funkcija parsira nezavršni znak <lista_naredbi>
def parse_lista_naredbi():
    cvor = Cvor("<lista_naredbi>")
    trenutniToken = trenutni_token()

    if trenutniToken and trenutniToken[0] in ("IDN", "KR_ZA"):      # Početak nove naredbe
        cvor.dodaj_podcvor(parse_naredba())
        cvor.dodaj_podcvor(parse_lista_naredbi())                   # Rekurzivno parsiraj ostatak
    else:                                                           # Nema više naredbi za parsiranje
        cvor.dodaj_podcvor(Cvor("$"))

    return cvor

# Funkcija parsira nezavršni znak <naredba>
def parse_naredba():
    cvor = Cvor("<naredba>")
    trenutniToken = trenutni_token()

    if not trenutniToken:                                       # Ulaz je prazan
        pogreska()

    if trenutniToken[0] == "IDN":                               # Za naredbu pridruživanja
        cvor.dodaj_podcvor(parse_naredba_pridruzivanja())
    elif trenutniToken[0] == "KR_ZA":                           # Početak petlje
        cvor.dodaj_podcvor(parse_za_petlja())
    else:
        pogreska()

    return cvor

# Funkcija parsira nezavršni znak <naredba_pridruživanja>
def parse_naredba_pridruzivanja():
    cvor = Cvor("<naredba_pridruzivanja>")

    trenutniToken = trenutni_token()

    if trenutniToken and trenutniToken[0] == "IDN":         # Identifikator s lijeve strane
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
    else:
        pogreska()

    trenutniToken = trenutni_token()
    if trenutniToken and trenutniToken[0] == "OP_PRIDRUZI":     # Znak '=' nakon identifikatora
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
    else:
        pogreska()

    cvor.dodaj_podcvor(parse_E())           # Izraz desno od znaka '='

    return cvor

# Funkcija parsira nezavršni znak <za_petlja>
def parse_za_petlja():
    cvor = Cvor("<za_petlja>")
    ocekivani = ["KR_ZA", "IDN", "KR_OD"]       # Prva tri završna znaka

    for ocekivano in ocekivani:                 # Provjeri redom sve završne znakove i dodaj ih u listu
        trenutniToken = trenutni_token()
        if trenutniToken and trenutniToken[0] == ocekivano:
            cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
            sljedeci_token()
        else:
            pogreska()

    cvor.dodaj_podcvor(parse_E())           # Početna vrijednost brojača

    trenutniToken = trenutni_token()
    if trenutniToken and trenutniToken[0] == "KR_DO":       # Ključna riječ "do"
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
    else:
        pogreska()

    cvor.dodaj_podcvor(parse_E())                   # Završna vrijednost brojača
    cvor.dodaj_podcvor(parse_lista_naredbi())       # Glavni dio petlje

    trenutniToken = trenutni_token()
    if trenutniToken and trenutniToken[0] == "KR_AZ":           # Ključna riječ "az" --> kraj petlje
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
    else:                                                       # Nešto nedostaje
        pogreska()

    return cvor

# Funkcija parsira nezavršni znak <E>
def parse_E():
    cvor = Cvor("<E>")                      # Čvor <E>
    cvor.dodaj_podcvor(parse_T())           # Prvi član
    cvor.dodaj_podcvor(parse_E_lista())     # Nastavak tog izraza
    return cvor

# Funkcija parsira nezavršni znak <T>
def parse_T():
    cvor = Cvor("<T>")                      # Čvor <T>
    cvor.dodaj_podcvor(parse_P())           # Prvi faktor
    cvor.dodaj_podcvor(parse_T_lista())     # Nastavak tog izraza
    return cvor

# Funkcija parsira nezavršni znak <E_lista>
def parse_E_lista():
    cvor = Cvor("<E_lista>")
    trenutniToken = trenutni_token()

    if trenutniToken and trenutniToken[0] == "OP_PLUS":         # Binarni plus
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_E())
    elif trenutniToken and trenutniToken[0] == "OP_MINUS":      # Binarni minus
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_E())
    else:                                                       # Izraz je završen --> primjena epsilon produkcije
        cvor.dodaj_podcvor(Cvor("$"))

    return cvor

# Funkcija parsira nezavršni znak <T_lista>
def parse_T_lista():
    cvor = Cvor("<T_lista>")
    trenutniToken = trenutni_token()

    if trenutniToken and trenutniToken[0] == "OP_PUTA":         # množenje
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_T())
    elif trenutniToken and trenutniToken[0] == "OP_DIJELI":     # dijeljenje
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_T())
    else:                                                       # Izraz je završen --> primjeni epsilon produkciju
        cvor.dodaj_podcvor(Cvor("$"))

    return cvor

# Funkcija parsira nezavršni znak <P>
def parse_P():
    cvor = Cvor("<P>")
    trenutniToken = trenutni_token()

    if not trenutniToken:           # Ulaz je prazan, a očekuje se nešto
        pogreska()

    if trenutniToken[0] == "OP_PLUS":       # Unarni plus
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_P())
    elif trenutniToken[0] == "OP_MINUS":    # Unarni minus
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_P())
    elif trenutniToken[0] == "L_ZAGRADA":   # Izraz u zagradama
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
        cvor.dodaj_podcvor(parse_E())       # Unutar zagrada imamo novi izraz

        trenutniToken2 = trenutni_token()   # Nakon tog izraza dolazi znak ')'

        if trenutniToken2 and trenutniToken2[0] == "D_ZAGRADA":
            cvor.dodaj_podcvor(Cvor(trenutniToken2[0], trenutniToken2[1], trenutniToken2[2]))
            sljedeci_token()
        else:                               # Nedostaje znak ')'
            pogreska()
    elif trenutniToken[0] in ("IDN", "BROJ"):       # Identifikator ili konstanta
        cvor.dodaj_podcvor(Cvor(trenutniToken[0], trenutniToken[1], trenutniToken[2]))
        sljedeci_token()
    else:                                           # Neispravan izraz
        pogreska()

    return cvor

# main funkcija --> učitava ulaz sa standardnog ulaza, radi generativno stablo i ispisuje ga
def main():
    global globalni_token, index
    globalni_token = ucitaj_tokene_iz_datoteke()

    if not globalni_token:                  # Prazan ulaz je ok, jer <program> --> <lista_naredbi> --> epsilon
        korijen = program_parsiraj()
        korijen.ispisi(0)
        return

    korijen = program_parsiraj()            # Napravi stablo

    if index < len(globalni_token):         # Ostalo je znakova nakon završenog parsiranja
        pogreska()

    korijen.ispisi(0)                       # Ako nije bilo greške, ispiši stablo

if __name__ == "__main__":
    main()