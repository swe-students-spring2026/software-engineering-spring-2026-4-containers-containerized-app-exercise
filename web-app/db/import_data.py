"""Script for importing CSV data into MongoDB."""

import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")

TRAIN_CSV = "machine-learning-client/src/data/raw/sign_mnist_train.csv"
TEST_CSV = "machine-learning-client/src/data/raw/sign_mnist_test.csv"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def import_csv(csv_path, collection_name):
    """Import CSV data into MongoDB."""
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient="records")

    db[collection_name].delete_many({})
    if records:
        db[collection_name].insert_many(records)

    print(f"{collection_name}: inserted {len(records)} documents")


def main():
    """Import both train and test CSV files into MongoDB."""
    import_csv(TRAIN_CSV, "sign_mnist_train")
    import_csv(TEST_CSV, "sign_mnist_test")

    print("Databases now visible:", client.list_database_names())
    print("Train count:", db["sign_mnist_train"].count_documents({}))
    print("Test count:", db["sign_mnist_test"].count_documents({}))

    client.close()


if __name__ == "__main__":
    main()
