# PriceNavigator

PriceNavigator ist ein lokal lauffähiges MVP für Produkterfassung, Produktquellen, Angebote, Shops, Einkaufslisten und eine deterministische Shop-Penalty-Optimierung.

## Überblick

Das Projekt ist als Full-Stack-Repository mit zwei klar getrennten Anwendungen aufgebaut:

- `frontend/`: Next.js 16 mit App Router, TypeScript, Vitest und Playwright
- `backend/`: FastAPI, SQLAlchemy 2.x, Alembic, SQLite, pytest und Ruff

Der Fokus liegt auf einem wartbaren Grundsystem statt Wegwerf-Prototyping:

- Produktaufnahme über URL, Hersteller+MPN oder EAN/GTIN
- gekapselte Resolver- und Offer-Provider-Schnittstellen
- echte Persistenz in SQLite
- CRUD-Ansichten für alle Kernentitäten
- CSV-Export
- deterministiche Optimierung mit Shop-Penalty
- Docker-Setup für Self-Hosting-orientierte lokale Starts

## Architektur

### Frontend

- Next.js App Router
- Client-seitige API-Anbindung an das FastAPI-Backend
- einfache, wartbare Komponenten statt schwerer UI-Bibliothek
- responsive Karten-, Tabellen- und Formularstruktur

Wichtige Bausteine:

- `frontend/app/`: Seiten für Dashboard, Produkte, Quellen, Angebote, Shops, Einkaufslisten und Optimierungsläufe
- `frontend/components/product-capture-form.tsx`: Produkt-Resolve und Produkt-Erfassung
- `frontend/components/data-table.tsx`: zentrale Tabellenkomponente mit Suche
- `frontend/components/optimization-result-view.tsx`: Shop-gruppierte Ergebnisansicht
- `frontend/lib/api.ts`: API-Client gegen das Backend

### Backend

- FastAPI mit OpenAPI
- SQLAlchemy 2.x ORM
- Alembic Initialmigration
- SQLite als lokale Standarddatenbank

Wichtige Bausteine:

- `backend/app/api/routes/`: REST-Endpunkte
- `backend/app/services/product_resolver.py`: Resolver-Architektur mit Mock-Resolvern
- `backend/app/services/offer_search.py`: Offer-Provider-Schnittstelle mit Mock-Provider
- `backend/app/services/product_matching.py`: deterministische Matching-Regeln
- `backend/app/services/optimization.py`: Shop-Penalty-Heuristik
- `backend/app/services/seeding.py`: lokale Seed-Daten

### Matching-Regeln

Die Produktzuordnung läuft deterministisch in dieser Priorität:

1. EAN / GTIN
2. Hersteller + MPN
3. Hersteller + Titel + Kernattribute
4. sonst manueller Review

### Optimierung

Die Optimierung nutzt aktive Offers aus `offers` und bewertet Kombinationen mit:

`score = item_sum + shipping_sum + (shop_count - 1) * shop_penalty`

Das MVP nutzt dafür eine kleine, deterministische Kombinationensuche über die besten Offer-Kandidaten je Shop.

## Projektstruktur

```text
.
├── backend
│   ├── app
│   │   ├── api/routes
│   │   ├── core
│   │   ├── models
│   │   ├── repositories
│   │   ├── schemas
│   │   └── services
│   ├── migrations
│   ├── scripts
│   └── tests
├── frontend
│   ├── app
│   ├── components
│   ├── e2e
│   ├── lib
│   ├── scripts
│   └── test
├── docker-compose.yml
├── Makefile
└── README.md
```

## Datenmodell

Implementierte Tabellen:

- `products`
- `product_sources`
- `shops`
- `offers`
- `shopping_lists`
- `shopping_list_items`
- `optimization_runs`
- `optimization_run_items`

Die Initialmigration liegt in:

- `backend/migrations/versions/20260327_0001_initial.py`

## API-Überblick

### Products

- `POST /api/products/resolve`
- `POST /api/products`
- `GET /api/products`
- `GET /api/products/{id}`
- `PUT /api/products/{id}`
- `DELETE /api/products/{id}`

### Product Sources

- `GET /api/product-sources`
- `GET /api/product-sources/{id}`
- `PUT /api/product-sources/{id}`
- `DELETE /api/product-sources/{id}`

### Shops

- `GET /api/shops`
- `POST /api/shops`
- `PUT /api/shops/{id}`
- `DELETE /api/shops/{id}`

### Offers

- `POST /api/offers/search`
- `GET /api/offers`
- `GET /api/offers/{id}`
- `PUT /api/offers/{id}`
- `DELETE /api/offers/{id}`

### Shopping Lists

- `GET /api/shopping-lists`
- `POST /api/shopping-lists`
- `GET /api/shopping-lists/{id}`
- `PUT /api/shopping-lists/{id}`
- `DELETE /api/shopping-lists/{id}`
- `POST /api/shopping-lists/{id}/items`
- `PUT /api/shopping-list-items/{id}`
- `DELETE /api/shopping-list-items/{id}`

### Optimization

- `POST /api/shopping-lists/{id}/optimize`
- `GET /api/optimization-runs`
- `GET /api/optimization-runs/{id}`
- `DELETE /api/optimization-runs/{id}`

### Export

- `GET /api/export/products.csv`
- `GET /api/export/offers.csv`
- `GET /api/export/shopping-list/{id}.csv`

OpenAPI ist lokal verfügbar unter:

- `http://localhost:8000/docs`

## Seed-Daten

Seeded werden:

- 6 Produkte
- 3 Shops
- 15 Angebote
- 1 Einkaufsliste mit 3 Positionen

Die Seed-Daten decken Produkt-Resolve, Angebots-Suche und Optimierung ab.

## Lokal starten ohne Docker

### Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
NPM_CONFIG_CACHE=../.npm-cache npm install
NPM_CONFIG_CACHE=../.npm-cache npm run dev
```

Standard-URLs:

- Frontend: `http://localhost:3100`
- Backend: `http://localhost:8000`

## Start mit Docker

```bash
docker compose up --build
```

Compose startet:

- `backend` auf Port `8000`
- `frontend` auf Port `3100`

Wichtige Details:

- SQLite-Daten liegen über das Bind-Mount `./backend/data:/app/data`
- Backend führt beim Start `alembic upgrade head` aus
- `.env` und `.env.example` liegen separat in `backend/` und `frontend/`

## Häufige Befehle

Per `Makefile`:

```bash
make backend-install
make frontend-install
make db-upgrade
make seed
make test
make lint
make docker-up
```

## Testbefehle

### Backend

```bash
cd backend
. .venv/bin/activate
ruff check .
pytest
```

### Frontend

```bash
cd frontend
NPM_CONFIG_CACHE=../.npm-cache npm run lint
NPM_CONFIG_CACHE=../.npm-cache npm run test
NPM_CONFIG_CACHE=../.npm-cache npm run build
```

### End-to-End

Für Playwright wurde ein lokaler Browserpfad verwendet:

```bash
cd frontend
PLAYWRIGHT_BROWSERS_PATH=../.playwright-browsers npx playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=../.playwright-browsers NPM_CONFIG_CACHE=../.npm-cache npm run e2e
```

Der E2E-Test deckt ab:

1. Produkt anlegen
2. Angebote suchen
3. Einkaufsliste anlegen
4. Position hinzufügen
5. Optimierung starten
6. Ergebnis prüfen

## Bewusst als Mock/Stub umgesetzt

Diese Teile sind im MVP absichtlich gekapselte Mock-Implementierungen:

- `MockUrlResolver`
- `MockManufacturerMpnResolver`
- `MockEanResolver`
- `MockOfferProvider`

Die API und das Datenmodell sind bereits so gebaut, dass echte Provider später ohne API-Bruch ergänzt werden können.

## Echte Resolver/Provider später ergänzen

### Produkte

Neue Resolver implementieren:

- `supports(payload) -> bool`
- `resolve(payload) -> dict | None`

Einbinden in:

- `backend/app/services/product_resolver.py`

### Angebote

Neue Offer-Provider implementieren:

- `search(product) -> ProviderSearchResult`

Einbinden in:

- `backend/app/services/offer_search.py`

Wichtig:

- Provider sollen Offer-Drafts inklusive `shop_payload` liefern
- Persistenz, Matching und API-Verhalten bleiben in den bestehenden Services

## Annahmen und bekannte Einschränkungen

- Keine Authentifizierung im MVP
- Keine echten Scraper oder Preisfeeds, sondern Mock-Datenquellen
- Keine komplexe globale Optimierung über große Suchräume; das MVP nutzt eine deterministische Heuristik mit kleiner Kandidatenmenge
- Frontend lädt Daten überwiegend client-seitig, um die Backend-Anbindung lokal und in Docker einfach zu halten
- `products` werden per Soft-Delete archiviert, `offers` per `is_active=false` deaktiviert
- Versandkosten werden pro Shop vereinfacht über Offer- oder Shop-Defaults bewertet

## Verifikation im aktuellen Stand

Lokal erfolgreich ausgeführt:

- Backend: `ruff check .`
- Backend: `pytest`
- Frontend: `npm run lint`
- Frontend: `npm run test`
- Frontend: `npm run build`
- Frontend: `npm run e2e`

Die Docker-Images bauen erfolgreich. Wenn Docker in der lokalen Umgebung läuft, ist `docker compose up --build` der vorgesehene Startpfad.
