import sys

# Funkcija određuje i vraća prvi dio teksta za ispis trenutno učitane riječi iz naredbe
def provjeriTip(trenutniSubstring):

    # Riječnik ključnih riječi i njihove oznake u prvom dijelu ispisa
    oznaka = {"za": "KR_ZA",
              "od": "KR_OD",
              "do": "KR_DO",
              "az": "KR_AZ",
              "=": "OP_PRIDRUZI",
              "+": "OP_PLUS",
              "-": "OP_MINUS",
              "*": "OP_PUTA",
              "/": "OP_DIJELI",
              "(": "L_ZAGRADA",
              ")": "D_ZAGRADA"}

    # Ako se radi o nekoj ključnoj riječi, operatoru ili zagradi, vrati njegov ispis
    if trenutniSubstring in oznaka:
        return oznaka[trenutniSubstring]

    # Ako se radi o broju
    elif trenutniSubstring.isdigit():
        return "BROJ"

    # Inače, radi se o identifikatoru
    else:
        return "IDN"

brojTrenutnogRetka = 0

for line in sys.stdin:

    # Svaki put povećaj broj retka
    brojTrenutnogRetka += 1

    # Splitaj po komentaru, odnosno po '//' -> dobijemo dio prije komentara i komentar kojeg zanemarujemo
    # U varijablu naredba spremi naredbu, odnosno dio prije komentara
    # Na kraju, pomoću funkcije strip, maknemo praznine s početka i kraja naredbe
    naredba = line.split('//')[0].strip()

    # Ako se radi o praznom retku -> preskoči ga
    if naredba == '':
        continue

    # Iteriramo po svakoj riječi iz naredbe i odlučujemo o kojem tipu podatka se radi
    i = 0
    while i < len(naredba):
        znak = naredba[i]

        # Je li znak slovo -> ako je, radi se o riječi, a ne o broju
        if znak.isalpha():
            trenutniSubstring = ""
            while i < len(naredba) and naredba[i].isalnum():
                trenutniSubstring += naredba[i]
                i += 1      # Pomakni se na sljedeći znak

            # Dohvati tip pročitane riječi + napravi traženi ispis
            oznaka = provjeriTip(trenutniSubstring)
            print(f"{oznaka} {brojTrenutnogRetka} {trenutniSubstring}")
            continue

        # Je li pročitani znak zapravo cijeli broj
        elif znak.isdigit():
            trenutniSubstring = ""
            while i < len(naredba) and naredba[i].isdigit():
                trenutniSubstring += naredba[i]
                i += 1

            oznaka = provjeriTip(trenutniSubstring)
            print(f"{oznaka} {brojTrenutnogRetka} {trenutniSubstring}")
            continue

        # Je li pročitani znak operator ili zagrada
        elif znak in "+-*/()=":
            oznaka = provjeriTip(znak)
            print(f"{oznaka} {brojTrenutnogRetka} {znak}")
            i += 1
            continue

        # U slučaju nečeg neočekivanog, idemo dalje
        i += 1