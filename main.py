import time
import uuid
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

EMAIL = "24f3003188@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-q8xq0y.example.com"

api = FastAPI()

@api.get("/stats")
def stats(values: str = Query(...)):
    numbers = [int(x.strip()) for x in values.split(",")]

    if not numbers:
        return {"error": "values cannot be empty"}

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }

cors_app = CORSMiddleware(
    app=api,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)

class HeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                duration = max(0.0, time.perf_counter() - start)
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-request-id", request_id.encode()),
                    (b"x-process-time", f"{duration:.6f}".encode()),
                ])
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)

app = HeadersMiddleware(cors_app)
