from fetcher import fetch
from generator import generate
from settings import CALENDAR_ID

generate(fetch(CALENDAR_ID))
