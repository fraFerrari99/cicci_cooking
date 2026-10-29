# Cucina con Cicci

Piattaforma web di ricette senza pubblicità, con assistente di cottura hands-free
e pannello autore. Monorepo: `backend/` (FastAPI) e, a breve, `frontend/` (Next.js).

## Prerequisiti

- [uv](https://docs.astral.sh/uv/) (gestisce Python 3.12 e le dipendenze)
- Docker Desktop (per Postgres e per provare l'immagine di produzione)

## Avvio rapido (backend)

```bash
cd backend
cp .env.example .env
uv sync                 # crea .venv e installa tutto
make dev                # http://localhost:8000/api/docs
```

Con Docker (API + Postgres):

```bash
cd backend
cp .env.example .env
make up                 # build + avvio, ricarica il codice al salvataggio
```

Endpoint di prova: `GET http://localhost:8000/api/v1/health`

## Comandi utili

```bash
cd backend
make help               # elenco target
make test               # pytest
make lint               # ruff + mypy
make fmt                # formatta
make check              # lint + test (quello che girerà in CI)
make pre-commit-install # git hook: lint automatico a ogni commit
```

## Struttura

```
backend/
├── api/index.py        # entrypoint Vercel (serverless), importa app.main:app
├── app/
│   ├── main.py         # create_app(): middleware, handler errori, router
│   ├── core/           # config (env), logging (structlog), exceptions
│   ├── middleware/     # request id + access log
│   ├── routers/        # endpoint, montati sotto /api/v1
│   └── schemas/        # modelli Pydantic condivisi
└── tests/
```

## Convenzioni

- Commit: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`…)
- Codice: ruff (lint + format, 100 colonne), mypy strict su `app/`
- Ogni risposta di errore ha la forma `{"error": {"code", "message", "details?", "request_id"}}`
- Ogni risposta porta l'header `X-Request-ID`: citarlo nei bug report

## Deploy

Vercel: `vercel.json` instrada `/api/*` verso la function Python. Configurazione
e variabili d'ambiente nel task Kanban "Deploy Vercel + Supabase + R2".
