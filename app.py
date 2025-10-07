import sys, os, certifi
import pandas as pd

ca = certifi.where()

from dotenv import load_dotenv

load_dotenv()
mongo_db_url = os.getenv("MONFODB_URL_KEY")
print(mongo_db_url)

import pymongo
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging
from network_security.pipeline.training_pipeline import TrainingPipeline
from network_security.utils.main_utils.utils import load_object
from network_security.utils.ml_utils.model.estimator import NetworkModel
from network_security.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
    FINAL_MODEL_DIR,
    PREPROCESSING_OBJECT_FILE_NAME,
    MODEL_FILE_NAME,
    PREDICTION_OUTPUT_DIR,
    OUTPUT_FILE_NAME,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="./templates")

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train")
async def train_route():
    try:
        train_pipline = TrainingPipeline()
        train_pipline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocessor = load_object(
            os.path.join(FINAL_MODEL_DIR, PREPROCESSING_OBJECT_FILE_NAME)
        )
        final_model = load_object(os.path.join(FINAL_MODEL_DIR, MODEL_FILE_NAME))
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        y_pred = network_model.predict(df)

        df["predicted_column"] = y_pred
        df.to_csv(os.path.join(PREDICTION_OUTPUT_DIR, OUTPUT_FILE_NAME))
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse(
            "table.html", {"request": request, "table": table_html}
        )
    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    app_run(app, host="localhost", port=8000)
