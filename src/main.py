import json
import pickle
import time
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model and features once at startup
    with open("model/model.pkl", "rb") as model_file:
        app.state.model = pickle.load(model_file)

    with open("model/model_features.json") as features_file:
        app.state.features = json.load(features_file)

    # Load demographic data and convert to O(1) dictionary
    demographics = pd.read_csv("data/zipcode_demographics.csv", dtype={"zipcode": str})
    demographics.set_index("zipcode", inplace=True)
    app.state.demographics = demographics.to_dict(orient="index")

    yield
    # Clean up state on shutdown
    app.state.model = None
    app.state.features = None
    app.state.demographics = None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
