import pandas as pd

from dataclasses import fields
from acp4.io.io import Data


def print_data_length(
    discharge: pd.DataFrame,
    camel: pd.DataFrame,
    herxheimweyher: pd.DataFrame,
    steinweiler: pd.DataFrame,
    ) -> None:
    
    data = {
        "discharge": discharge,
        "camel": camel,
        "herxheimweyher": herxheimweyher,
        "steinweiler": steinweiler
    }
    
    print(f"Before alignment")
    for name, df in data.items():
        print(f"Name: {name}")
        print(f"Num rows of available data: {len(df.index)}")
        print(f"Length of available data: {df.index.max() - df.index.min()}")
        print(f"Period: {df.index.min()} - {df.index.max()}")
        print("------------------------\n")
        
    
def print_data_length_aligned(data: Data) -> None:
    
    for field in fields(data):
        df = getattr(data, field.name)
        
        print("After alignment")
        print(f"Num rows of available data: {len(df.index)}")
        print(f"Length of available data: {df.index.max() - df.index.min()}")
        print(f"Period: {df.index.min()} - {df.index.max()}")
        print("------------------------")
        
        break


def check_missing_values(data: Data) -> None:
    
    for field in fields(data):
        df = getattr(data, field.name)

        na_count = df.isna().sum()
        na_count = na_count[na_count > 0]

        print(f"Name: {field.name}")

        if na_count.empty:
            print("No missing values.")
        else:
            print(f"Number of NAs:\n{na_count}")
            print(f"Percentage of NAs:\n{(na_count / len(df) * 100).round(2)}%")

        print("------------------------")
        

def check_duplicated_dates(data: Data) -> None:
    for field in fields(data):
        df = getattr(data, field.name)

        print(f"Name: {field.name}")
        print(f"Duplicated dates: {df.index.duplicated().any()}")
        print("------------------------")


def check_non_negative_cols(data: Data) -> None:
    
    non_negative_cols = {
        "precipitation_mean",
        "radiation_global_mean",
    }

    for field in fields(data):
        df = getattr(data, field.name)

        if field.name == "discharge":
            print(field.name)
            for col in df.columns.to_list():
                print(f"Negative values in {col}: {(df[col] < 0).any()}")
            print("---------------------------------")
        
        else:
            print(field.name)
            for col in df.columns.to_list():
                if col in non_negative_cols:
                    print(f"Negative values in {col}: {(df[col] < 0).any()}")
            print("---------------------------------")
    
    
def check_if_float(data: Data) -> None:
    for field in fields(data):
        df = getattr(data, field.name)
        print(f"Dataset: {field.name}")

        for col in df.columns:
            print(f"{col}: {pd.api.types.is_float_dtype(df[col])}")

        print("-------------------------")
    