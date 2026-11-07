# FiftyFit checker

Checkt elke 15 minuten (ca. 6:00–22:00) of er plekken vrijkomen bij
[FiftyFit in het Leeghwaterbad](https://spurd.booqi.me/product/293152/fiftyfit)
en stuurt een pushmelding via [ntfy.sh](https://ntfy.sh) zodra een volle les
van 0 naar 1 of meer vrije plekken gaat.

## Hoe het werkt

- GitHub Actions draait `check_fiftyfit.py` volgens het schema in
  `.github/workflows/check.yml`.
- Het script haalt de beschikbaarheid op via de open API van Spurd en
  vergelijkt die met de vorige run (`state.json`, wordt automatisch gecommit).
- Gaat een les die aan je filters voldoet van 0 naar >0 vrij, dan krijg je een
  melding met een link naar de boekingspagina.
- De eerste run slaat alleen de stand op en stuurt geen meldingen.

## Instellen

- **Secret** `NTFY_TOPIC`: je eigen geheime ntfy-topic. Abonneer je in de
  ntfy-app op dezelfde topicnaam.

## Filters aanpassen

De filters zijn repo-variables (Settings → Secrets and variables → Actions →
Variables), of via de `gh` CLI:

```bash
gh variable set WEEKDAYS --body "0,2"        # 0=ma, 1=di ... 6=zo
gh variable set TIMES --body "11:45,13:00"   # starttijden, komma-gescheiden
```

Laat een variable leeg (of verwijder hem met `gh variable delete`) om op alle
dagen of alle tijden te checken.

## Handmatig draaien

```bash
gh workflow run check.yml
```
