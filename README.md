# Monster Energy-nettside

Dette er en nettside om Monster-drikker. Du kan lage bruker, logge inn og lese om ulike smaker.

## Hva kan du gjøre på nettsiden?

- **Forside** — startside med lenker
- **Registrer** — lage ny bruker med brukernavn og passord
- **Logg inn** — komme inn med brukernavn og passord du har laget
- **Velkommen** — se liste over Monster-smaker (må være innlogget)
- **Klikk på en smak** — lese mer om den ene drikken

Designet er enkelt: svart tekst på hvit bakgrunn, så det er lett å lese.

## Hvordan starter du nettsiden?

1. Sørg for at databasen (MySQL) kjører på PC-en din
2. Åpne terminalen i mappen til prosjektet
3. Skriv: `python app.py`
4. Åpne nettleseren og gå til: `http://127.0.0.1:5000`

Da skal nettsiden vises.

## Passord og sikkerhet

Passord lagres **ikke** som vanlig tekst i databasen. De gjøres om til en lang, kryptert streng (kalt *hash*). Da kan ikke andre se passordet ditt selv om de får tak i databasen.

Det finnes også en **admin**-bruker som lages automatisk når du starter appen


## Hva er nettsiden laget med?

- **Flask** — programmet som kjører nettsiden
- **MySQL** — der brukere og monster-info lagres
- **HTML-maler** — filene som viser sidene i nettleseren


## Mål videre

Målet videre er å fullføre admin brukeren sånn at den kan legge til nye og fjerne gamle monster smaker.