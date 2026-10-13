from fastapi import FastAPI

app = FastAPI(title="SpeakSpark API")


@app.on_event("startup")
def startup_event() -> None:
    from app.database import init_db

    init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
