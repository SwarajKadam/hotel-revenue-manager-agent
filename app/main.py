from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.etl import verify_load, run_etl
from app.agent import ask_agent
from app.metrics import (
    get_revenue_by_month,
    get_channel_mix,
    get_ota_dependency,
    get_cancellations_by_month,
    get_room_type_adr,
    get_group_business_summary,
    get_pickup_last_7_days,
    get_market_mix,
)


app = FastAPI(title="Hotel Revenue Manager Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "Hotel Revenue Manager Agent API",
        "description": "Backend API for ETL verification, hotel revenue metrics, and AI revenue manager chat.",
        "available_routes": [
            "/health",
            "/verify",
            "/etl/run",
            "/chat",
            "/metrics/revenue-by-month",
            "/metrics/channel-mix",
            "/metrics/ota-dependency",
            "/metrics/cancellations",
            "/metrics/room-type-adr",
            "/metrics/group-business",
            "/metrics/pickup-last-7-days",
            "/metrics/market-mix",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Backend is running.",
    }


@app.get("/verify")
def verify():
    return verify_load()


@app.post("/etl/run")
def run_etl_endpoint():
    checks = run_etl()
    return {
        "message": "ETL completed successfully.",
        "checks": checks,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask_agent(request.message)

    return {
        "question": request.message,
        "answer": answer,
    }


@app.get("/metrics/revenue-by-month")
def revenue_by_month():
    return get_revenue_by_month()


@app.get("/metrics/channel-mix")
def channel_mix():
    return get_channel_mix()


@app.get("/metrics/ota-dependency")
def ota_dependency():
    return get_ota_dependency()


@app.get("/metrics/cancellations")
def cancellations():
    return get_cancellations_by_month()


@app.get("/metrics/room-type-adr")
def room_type_adr():
    return get_room_type_adr()


@app.get("/metrics/group-business")
def group_business():
    return get_group_business_summary()


@app.get("/metrics/pickup-last-7-days")
def pickup_last_7_days():
    return get_pickup_last_7_days()


@app.get("/metrics/market-mix")
def market_mix():
    return get_market_mix()