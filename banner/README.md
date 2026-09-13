# banner

`hero-robots.gif` z profilowego README jest generowany, nie rysowany ręcznie.
Wszystkie liczby w panelu pochodzą z API GitHuba — nic nie jest wpisane na
sztywno, przy każdym renderze lecą zapytania po aktualne dane.

```
render.sh          # przelicza statystyki i składa gif
fetch_stats.py     # profil, repozytoria, gwiazdki, kontrybucje, bajty na język
make_banner.py     # podpis i panel jako warstwa nakładana na każdą klatkę
source.mp4         # przycięty i wyciszony materiał źródłowy (10 s, 1010x358)
hero-robots.gif    # wynik
```

Odświeżenie ręczne:

```bash
./banner/render.sh
```

Poza tym `.github/workflows/banner.yml` robi to samo w każdy poniedziałek i
commituje gif, jeśli liczby się zmieniły.

## Skąd biorą się liczby

| pozycja | źródło |
| --- | --- |
| imię i nazwisko | `name` z `/users/{login}` |
| repozytoria | `/users/{login}/repos`, bez forków |
| języki | bajty rozpoznane przez linguist, zsumowane po repozytoriach |
| gwiazdki | suma `stargazers_count` z tych samych repozytoriów |
| kontrybucje | `contributionsCollection` z GraphQL — ostatnie 12 miesięcy |

Login bierze się z `GITHUB_REPOSITORY_OWNER`, a lokalnie z `origin` w gicie,
więc skrypty nie mają w sobie żadnej nazwy użytkownika.

## Uwagi o składaniu

Panel jest domalowany do płótna gifa, a nie wstawiony jako drugi obrazek pod
banerem — GitHub wstawia między dwa obrazki odstęp i szew byłby widoczny.

`source.mp4` jest tylko materiałem wejściowym dla `render.sh`; w README trafia
wyłącznie `hero-robots.gif`, bo wideo GitHub w README nie odtworzy.

Materiał leci przez `hue`/`eq`/`colorbalance` (stała `grade` w `render.sh`),
żeby fioletowe tło i roboty wpadły w paletę Kanagawa Dragon — tę samą, którą
ma render kalendarza kontrybucji.

Font: JetBrains Mono, z fallbackiem na DejaVu Sans Mono. `make_banner.py`
szuka pliku po nazwie w katalogach z fontami, więc działa tak samo lokalnie
i na runnerze.
