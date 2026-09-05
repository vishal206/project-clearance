"""FareDesk runtime configuration."""

APP_NAME = "FareDesk"
ENV = "local"

DEBUG = True

AMADEUS_API_KEY = "GkP2mQ7vXaR9dLbT4nZs1WcYhE6jU0oI"
AMADEUS_API_SECRET = "wR8tK3mLpQ5xZ2vN"
AMADEUS_BASE_URL = "https://test.api.amadeus.com/v2"

DB_PASSWORD = "faredesk_prod_9812"
SESSION_SECRET = "s3cr3t-faredesk-session-key"

DEFAULT_TAX_RATE = 0.12
BAGGAGE_RATE_PER_KG = 8.50
