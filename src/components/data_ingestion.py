import os
import sys
import pandas as pd
from dataclasses import dataclass
from sklearn.model_selection import train_test_split

from src.utils import get_mongo_client
from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name: str = "accountability_db"
    collection_name: str = "tasks"
    raw_data_path: str = os.path.join("artifacts", "data.csv")
    train_data_path: str = os.path.join("artifacts", "train.csv")
    validation_data_path: str = os.path.join("artifacts", "validation.csv")
    test_data_path: str = os.path.join("artifacts", "test.csv")


class DataIngestion:
    def __init__(self):
        self.config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion from MongoDB")
        try:
            client = get_mongo_client(self.config.mongo_uri)
            db = client[self.config.db_name]
            collection = db[self.config.collection_name]

            records = list(collection.find({"completed": {"$exists": True}}))
            if not records:
                raise ValueError("No completed/labelled tasks found in MongoDB collection")

            df = pd.DataFrame(records)
            logging.info(f"Loaded {len(df)} records from MongoDB")

            df["planned_datetime"] = pd.to_datetime(df["planned_datetime"])
            df["hour_of_day"] = df["planned_datetime"].dt.hour
            df["day_of_week"] = df["planned_datetime"].dt.dayofweek

            drop_cols = ["_id", "task_id", "title", "planned_datetime", "completed_at", "created_at"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            df["completed"] = df["completed"].astype(int)

            os.makedirs(os.path.dirname(self.config.raw_data_path), exist_ok=True)
            df.to_csv(self.config.raw_data_path, index=False)
            logging.info(f"Raw data saved to {self.config.raw_data_path}")

            # first split: 70% train, 30% temp
            train_df, temp_df = train_test_split(
                df, test_size=0.30, random_state=42, stratify=df["completed"]
            )
            # second split: temp → 50/50 → 15% val, 15% test
            val_df, test_df = train_test_split(
                temp_df, test_size=0.50, random_state=42, stratify=temp_df["completed"]
            )

            train_df.to_csv(self.config.train_data_path, index=False)
            val_df.to_csv(self.config.validation_data_path, index=False)
            test_df.to_csv(self.config.test_data_path, index=False)

            logging.info(
                f"Split complete — train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}"
            )

            return (
                self.config.train_data_path,
                self.config.validation_data_path,
                self.config.test_data_path,
            )

        except Exception as e:
            raise CustomException(e, sys)
