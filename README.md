# Project Clearance

Deliberately insecure FastAPI app for scanner/QA testing. Not for deployment.

The portal it presents is themed as "FareDesk", an Amadeus-style flight booking
agent console. Every flaw in it is intentional.

    uv venv --python 3.13 .venv
    uv pip install --python .venv/bin/python -r requirements.txt
    .venv/bin/uvicorn app.main:app --port 8000

Run from the project root — static files are mounted at a relative path.

Routes: `/`, `POST /login`, `/search`, `/api/flight-offers`, `/booking/{pnr}`, `/admin/stats`.
PNRs: ABC101–ABC105.
