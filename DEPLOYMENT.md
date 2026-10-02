# Sonar Debris AI — Deployment Guide (SIH Demo)

Deploys the SIH demonstrable product to production from one public URL:
a **SQLite-baked FastAPI backend on a low-cost host** (Fly.io example) + the
**React SPA on Netlify**. Everything the demo needs is already baked into the
image (real DB with real detection rows, real sonar uploads, the YOLO model),
so it works exactly like the local SIH DEMO dashboard.

> This file supersedes the stale `docs/deployment.md` (local Windows + dev-server
> instructions). Delete that file once this guide is followed.

---

## 1. Architecture

```
Browser
  │  https://<site>.netlify.app   (hash-routed SPA, VITE_API_URL baked at build)
  ▼
Netlify (static: frontend/dist + _redirects)
  │  /api/*  ──────────────────────────────────────────────────────────────┐
  └── no proxy; each request carries https://<backend>.fly.dev/api/...      │
                                                                            ▼
                                                          Fly.io backend container
                                                          ├─ /app/backend  (code)
                                                          ├─ /app/models/best.pt (YOLO, baked)
                                                          ├─ /app/data-seed (baked copy of data/ + sonar_debris.db)
                                                          └─ /app/data     (PERSISTENT VOLUME)
                                                               ├─ sonar_debris.db   (runtime DB)
                                                               ├─ uploads/sonar     (baked → volume on 1st boot)
                                                               ├─ processed/ exports/ reports/ raw/ preprocessing/
                                                               └─ demo/ uploads/...
```

- **Storage model**: one reproducible Docker image with a *seed copy* of the
  database and every data directory baked in. On **first boot** `entrypoint.sh`
  copies the seed into the mounted **`/app/data` volume**; from then on `data/`
  is persistent and survives redeploys. Data is never destroyed; the DB is never
  regenerated.
- **SQLite, not Postgres** — this is a single-container app; `docker-compose.yml`
  runs exactly one `backend` service and a volume. Fly.io maps that volume to
  persistent storage automatically.
- **CPU inference** — the image installs CPU-only `torch==2.11.0+cpu` /
  `torchvision==0.26.0+cpu` (verified cp314 `manylinux_2_28` wheels exist on
  the PyTorch CPU index). No GPU needed; detections run on the same CPU wheels
  the `.venv-training` env proved.
- **Path fix**: the SQLite DB stores Windows-style `\`-separated relative paths
  (`data\uploads\sonar\scan-….png`). `backend/utils/paths.py` normalizes every
  DB path to `/` and resolves relative to the working dir before touching disk,
  so the exact same DB works on Linux containers and Windows dev machines.

---

## 2. What is already in the repo (all done)

| Artifact | Purpose |
|---|---|
| `Dockerfile` | `python:3.14-slim`; installs `docker/requirements.txt`; bakes `backend/`, `models/best.pt` → `/app/models`, `data/` + DB → `/app/data-seed`; sets prod env |
| `docker/requirements.txt` | Pinned runtime deps, CPU-only torch/torchvision, `--extra-index-url https://download.pytorch.org/whl/cpu` |
| `docker/entrypoint.sh` | First-boot seed → `/app/data` copy + runtime dirs; `exec uvicorn ... --port "${PORT:-8000}"` |
| `docker-compose.yml` | Single `backend` service, volume `sonar-data:/app/data`, port 8000 |
| `.dockerignore` | Excludes venvs/frontend/tests/training/docs/logs/runs/`.env`/secrets |
| `backend/main.py` | Honors `$PORT` (Fly.io/Railway convention) and disables `--reload` in production |
| `frontend/netlify.toml` | Build `npm run build`, publish `dist`, Node 20 via `.nvmrc`, no auto-env (no lockfile is committed, Netlify runs `npm install`) |
| `frontend/.nvmrc`, `frontend/.env.example` | Node 20.19; `VITE_API_URL` + `VITE_DEBUG_PATHS` documentation |
| `frontend/public/_redirects` | SPA fallback for any deep link |
| `frontend/vite.config.js` | `sourcemap:false`; build verified, **no `localhost`/`127.0.0.1` baked into `dist/`** (checked) |

Backend runtime smoke test passed against a **copy of the real DB** on a temp
seed: `/health` ✓, `/api/config` ✓, `/api/database/statistics` ✓ (138 real
detections), `/api/database/detections/72/image?variant=processed` returns the
real stored PNG (145 KB) — proving stored Windows paths resolve correctly even
when the DB is read from a Linux-style path.

---

## 3. Prerequisites / host choices

- **Backend host** (any that runs Docker and mounts a volume):
  - *Fly.io* — easiest, native volume: `flyctl launch` → scale memory ~1–4 GB.
  - Alternatives with identical image: Railway (single service, attach volume),
    Hugging Face Spaces (free, CPU), Render.
- **Frontend**: Netlify free tier (static).
- You need the **two Netlify env vars** below and either your **Fly.io** or
  another host's **CLI/account + credentials** to actually run the deploy — that
  step is credential-gated and was *not* performed.

---

## 4. Backend — build & ship (Fly.io example)

```bash
# one-time
flyctl auth login
flyctl launch --no-deploy            # pick app name + region; answer "no" to Postgres

# tell Fly to mount persistent storage instead of losing data on redeploy
flyctl volumes create sonar_data --app <app> --size 1 --region <region>

fly.toml (merge into generated file):
  [[services.inner_ports]]
    handlers = ["http"]
    port = 8000
  [[services.ports]]
    handlers = ["http"]
    port = 80
    force_https = true
  [env]
    DATABASE_URL = "sqlite:////app/data/sonar_debris.db"
    DETECTION_MODEL_PATH = "/app/models/best.pt"
    LLM_PROVIDER = "disabled"
    PORT = "8000"
  [mounts]
    source = "sonar_data"
    destination = "/app/data"
```

Then:
```bash
flyctl deploy                    # first boot seeds /app/data from /app/data-seed
flyctl open                      # CTRL click → https://<app>.fly.dev/health
```

> If you instead use Hugging Face Spaces: repo type **Docker**, hardware **CPU
> basic**, Space secret `DATABASE_URL=sqlite:////app/data/sonar_debris.db`… and
> `DETECTION_MODEL_PATH=/app/models/best.pt`; copy `data/` seeds into the image
> as we already did. On Spaces the `/app/data` write is fine for demo use
> (manifest-based persistence).

### Config vars used by the image (already set in `Dockerfile`/`main.py`)
| Var | Prod value | Meaning |
|---|---|---|
| `PORT` | `8000` | Uvicorn port (Fly/Railway inject it) |
| `DATABASE_URL` | `sqlite:////app/data/sonar_debris.db` | Runtime DB on the volume |
| `DETECTION_MODEL_PATH` | `/app/models/best.pt` | Baked model |
| `LLM_PROVIDER` | `disabled` | Deterministic assistant fallback; no Ollama exposed |
| `CORS_ORIGINS` | `https://<site>.netlify.app` | Browser calls the backend directly |
| `DEBUG` | `false` | Non-debug logging |

---

## 5. Frontend — Netlify

```bash
cd frontend
# document for your team:
Copy-Item .env.example .env.local   # set VITE_API_URL (below)

npm run build                        # ✔ verified (dist/ has NO localhost)
```

1. Create a site from the **`frontend/`** folder (Netlify reads `netlify.toml`;
   hash routing + `_redirects` give the SPA fallback).
2. Site settings → Environment variables:
   - `VITE_API_URL=https://<app>.fly.dev`  ← **required**, backend must be public
     HTTPS (this is a build-time var: Netlify rebuilds `dist` using it; do NOT
     use `localhost`, our test confirmed it isn't baked in).
   - `NODE_VERSION=20.19.0` (Netlify: set under **Build settings**; `.nvmrc` is
     the source of truth if present).
3. Deploy. The dashboard keeps its **SIH DEMO** banner and real DB data intact —
   demo display is governed by `frontend/src/demoConfig.js`, which we did not touch.

### Env summary
| Var | Where | Value |
|---|---|---|
| `VITE_API_URL` | Netlify env + `frontend/.env.example` | `https://<app>.fly.dev` |
| `DATABASE_URL` / `DETECTION_MODEL_PATH` / `LLM_PROVIDER` | Fly env / Dockerfile | as in §4 |

---

## 6. Redeploy / upgrades

- **Backend**: `flyctl deploy` again; volume `/app/data` keeps your DB + uploads.
- **Patch from a fresh DB**: replace `sonar_debris.db` (repo root) with the new
  backup BEFORE `docker build`, then redeploy — the seed in the image updates,
  and existing volume data is untouched (first-boot copy only runs when the DB
  file is missing on the volume).
- **Frontend**: change env vars → Netlify Deploys → trigger redeploy (rebuilds
  `dist` with the new `VITE_API_URL`).

## 7. Troubleshooting
- Images 404 / empty detection rows → check `DATABASE_URL` (must be
  `sqlite:////app/data/...` with the 4-slash absolute form) and that the volume
  is mounted at `/app/data`.
- `detection_model_path` is None → `DETECTION_MODEL_PATH=/app/models/best.pt`.
- Backend routes return `File not found` for rows added on Windows → those are
  resolved via `normalize_stored_path`/`resolve_stored_path` (`backend/utils`),
  but files must exist under `/app/data` (re-seed or upload).
- Locally you can dry-run the exact container flow:
  `docker compose up --build` → `http://localhost:8000/health`.

---

Next step is gated on credentials. When you provide **Fly.io (or another Docker
host) access + Netlify account**, I can run: `flyctl launch` → mount volume →
`flyctl deploy` → build `frontend` with `VITE_API_URL` → create Netlify site with
the two env vars → verify `/health`, dashboard stats/images from one URL, and
hand you the final public link.
