"""FareDesk - Amadeus-style flight booking agent portal."""

import logging
import traceback
from datetime import datetime

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config
from app.fares import calculate_total_fare

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("faredesk")

app = FastAPI(title=config.APP_NAME)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


FLIGHTS = [
    {
        "id": "FL-1001",
        "carrier": "AF",
        "flight_number": "AF1780",
        "origin": "CDG",
        "destination": "MAD",
        "depart": "2026-10-02T07:35",
        "arrive": "2026-10-02T09:50",
        "cabin": "ECONOMY",
        "seats_left": 9,
        "base_fare": 148.00,
        "currency": "EUR",
    },
    {
        "id": "FL-1002",
        "carrier": "IB",
        "flight_number": "IB3435",
        "origin": "CDG",
        "destination": "MAD",
        "depart": "2026-10-02T11:10",
        "arrive": "2026-10-02T13:20",
        "cabin": "ECONOMY",
        "seats_left": 4,
        "base_fare": 132.50,
        "currency": "EUR",
    },
    {
        "id": "FL-1003",
        "carrier": "LH",
        "flight_number": "LH1042",
        "origin": "FRA",
        "destination": "LHR",
        "depart": "2026-10-02T08:05",
        "arrive": "2026-10-02T08:45",
        "cabin": "BUSINESS",
        "seats_left": 2,
        "base_fare": 410.00,
        "currency": "EUR",
    },
    {
        "id": "FL-1004",
        "carrier": "BA",
        "flight_number": "BA0906",
        "origin": "FRA",
        "destination": "LHR",
        "depart": "2026-10-02T15:40",
        "arrive": "2026-10-02T16:25",
        "cabin": "ECONOMY",
        "seats_left": 17,
        "base_fare": 196.75,
        "currency": "EUR",
    },
    {
        "id": "FL-1005",
        "carrier": "EK",
        "flight_number": "EK0074",
        "origin": "DXB",
        "destination": "BOM",
        "depart": "2026-10-03T03:15",
        "arrive": "2026-10-03T07:55",
        "cabin": "ECONOMY",
        "seats_left": 23,
        "base_fare": 289.00,
        "currency": "EUR",
    },
    {
        "id": "FL-1006",
        "carrier": "AI",
        "flight_number": "AI0996",
        "origin": "DXB",
        "destination": "BOM",
        "depart": "2026-10-03T09:40",
        "arrive": "2026-10-03T14:05",
        "cabin": "ECONOMY",
        "seats_left": 6,
        "base_fare": 254.30,
        "currency": "EUR",
    },
]


BOOKINGS = {
    "ABC101": {
        "pnr": "ABC101",
        "passenger_name": "Marianne Delacroix",
        "dob": "1984-03-17",
        "passport": "17FR44821",
        "nationality": "FR",
        "email": "m.delacroix@example.fr",
        "phone": "+33 6 41 92 03 77",
        "flight_id": "FL-1001",
        "itinerary": "CDG 07:35 -> MAD 09:50 / AF1780 / 02OCT26",
        "seat": "14C",
        "baggage_kg": 23,
        "pax": 1,
        "status": "CONFIRMED",
        "total_paid": 191.31,
    },
    "ABC102": {
        "pnr": "ABC102",
        "passenger_name": "Tomas Berglund",
        "dob": "1971-11-02",
        "passport": "SE9930114",
        "nationality": "SE",
        "email": "t.berglund@example.se",
        "phone": "+46 70 118 55 20",
        "flight_id": "FL-1003",
        "itinerary": "FRA 08:05 -> LHR 08:45 / LH1042 / 02OCT26",
        "seat": "2A",
        "baggage_kg": 18,
        "pax": 1,
        "status": "CONFIRMED",
        "total_paid": 459.20,
    },
    "ABC103": {
        "pnr": "ABC103",
        "passenger_name": "Priya Raghunathan",
        "dob": "1993-06-28",
        "passport": "Z4471902",
        "nationality": "IN",
        "email": "p.raghunathan@example.in",
        "phone": "+91 98204 33176",
        "flight_id": "FL-1005",
        "itinerary": "DXB 03:15 -> BOM 07:55 / EK0074 / 03OCT26",
        "seat": "31F",
        "baggage_kg": 30,
        "pax": 2,
        "status": "TICKETED",
        "total_paid": 817.36,
    },
    "ABC104": {
        "pnr": "ABC104",
        "passenger_name": "Ahmed El-Masry",
        "dob": "1966-01-09",
        "passport": "A08812345",
        "nationality": "EG",
        "email": "a.elmasry@example.eg",
        "phone": "+20 100 774 2210",
        "flight_id": "FL-1004",
        "itinerary": "FRA 15:40 -> LHR 16:25 / BA0906 / 02OCT26",
        "seat": "9D",
        "baggage_kg": 20,
        "pax": 1,
        "status": "CONFIRMED",
        "total_paid": 220.36,
    },
    "ABC105": {
        "pnr": "ABC105",
        "passenger_name": "Lucia Ferrante",
        "dob": "1999-09-14",
        "passport": "YB1177403",
        "nationality": "IT",
        "email": "l.ferrante@example.it",
        "phone": "+39 340 662 1188",
        "flight_id": "FL-1002",
        "itinerary": "CDG 11:10 -> MAD 13:20 / IB3435 / 02OCT26",
        "seat": "22B",
        "baggage_kg": 12,
        "pax": 3,
        "status": "CONFIRMED",
        "total_paid": 445.20,
    },
}


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    if config.DEBUG:
        body = (
            "FareDesk internal error\n"
            "path: %s\n"
            "query: %s\n\n%s"
            % (request.url.path, request.url.query, traceback.format_exc())
        )
        return PlainTextResponse(body, status_code=500)
    return PlainTextResponse("Internal Server Error", status_code=500)


@app.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(email: str = Form(""), password: str = Form("")):
    log.info("agent login attempt email=%s password=%s", email, password)
    return RedirectResponse(url="/search?origin=CDG&destination=MAD&date=2026-10-02", status_code=303)


@app.get("/search", response_class=HTMLResponse)
def search(request: Request, origin: str = "", destination: str = "", date: str = ""):
    if date:
        parsed = datetime.strptime(date, "%Y-%m-%d")
        date_label = parsed.strftime("%d %b %Y").upper()
    else:
        date_label = "ANY DATE"

    results = []
    for f in FLIGHTS:
        if origin and f["origin"].upper() != origin.upper():
            continue
        if destination and f["destination"].upper() != destination.upper():
            continue
        row = dict(f)
        row["total"] = calculate_total_fare(f["base_fare"], config.DEFAULT_TAX_RATE, 0, 1)
        results.append(row)

    if not results:
        results = [dict(f, total=calculate_total_fare(f["base_fare"], config.DEFAULT_TAX_RATE, 0, 1)) for f in FLIGHTS]

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "origin": origin,
            "destination": destination,
            "date": date,
            "date_label": date_label,
            "results": results,
        },
    )


@app.get("/api/flight-offers")
def flight_offers(origin: str = "", destination: str = ""):
    offers = []
    for f in FLIGHTS:
        if origin and f["origin"].upper() != origin.upper():
            continue
        if destination and f["destination"].upper() != destination.upper():
            continue
        offers.append(
            {
                "offerId": f["id"],
                "carrierCode": f["carrier"],
                "flightNumber": f["flight_number"],
                "itinerary": {
                    "origin": f["origin"],
                    "destination": f["destination"],
                    "departureAt": f["depart"],
                    "arrivalAt": f["arrive"],
                },
                "cabin": f["cabin"],
                "seatsRemaining": f["seats_left"],
                "price": {
                    "base": f["base_fare"],
                    "total": calculate_total_fare(f["base_fare"], config.DEFAULT_TAX_RATE, 0, 1),
                    "currency": f["currency"],
                },
            }
        )
    return {"meta": {"count": len(offers), "source": config.AMADEUS_BASE_URL}, "data": offers}


@app.get("/booking/{pnr}", response_class=HTMLResponse)
def booking_detail(request: Request, pnr: str):
    record = BOOKINGS.get(pnr.upper())
    if record is None:
        return HTMLResponse("<pre>PNR %s not found</pre>" % pnr, status_code=404)

    log.info(
        "booking retrieved pnr=%s name=%s dob=%s passport=%s nationality=%s email=%s phone=%s seat=%s",
        record["pnr"],
        record["passenger_name"],
        record["dob"],
        record["passport"],
        record["nationality"],
        record["email"],
        record["phone"],
        record["seat"],
    )

    return templates.TemplateResponse(
        "booking.html",
        {"request": request, "b": record},
    )


@app.get("/admin/stats")
def admin_stats():
    revenue = sum(b["total_paid"] for b in BOOKINGS.values())
    by_status = {}
    for b in BOOKINGS.values():
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1
    return JSONResponse(
        {
            "bookings_total": len(BOOKINGS),
            "bookings_by_status": by_status,
            "pax_total": sum(b["pax"] for b in BOOKINGS.values()),
            "revenue_total": round(revenue, 2),
            "currency": "EUR",
            "env": config.ENV,
            "debug": config.DEBUG,
            "amadeus_key": config.AMADEUS_API_KEY,
        }
    )
