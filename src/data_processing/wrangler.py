from dataclasses import dataclass, field
from glob import glob

import logging
import os

from hydra import compose, initialize
import numpy as np
import pandas as pd

CONF_DIR = "../../config"

initialize(version_base = None, config_path=CONF_DIR, job_name="data-wrangler")
main_conf = compose(config_name="main")
data_conf = compose(config_name="data")

@dataclass
class DataWrangler:
    """
    This class is responsible for wrangling the data from the source.
    """
    raw_data_path: list[str] = field(default_factory = lambda: glob(main_conf.data.raw.path))
    processed_data_path: str = field(default = main_conf.data.processed.path)
    
    def __post_init__(self):
        if os.path.exists(self.processed_data_path):
            self.df = pd.read_csv(self.processed_data_path, index=False)
        else:
            self.df = None
    
    def load_data(self, use_exist:bool = True) -> pd.DataFrame:
        """ 
        Loads the cleaned data (or wrangle data).
        Arguments:
            use_exist (bool): If True, loads the processed data if it exists; 
                otherwise, raise error.
        Returns:
            df (pandas.DataFrame): Cleaned data.
        """
        if use_exist:
            if self.df is not None:
                logging.info("Loading processed data")
                return self.df
            else:
                logging.error("No processed data found. Wrangling data")
                return self.wrangle_data()
        else:
            return self.wrangle_data()
    
    def wrangle_data(self) -> pd.DataFrame:
        """Wrapper function to ingest and clean the data.
        Returns:
            self.df: Cleaned dataframe.
        """
        df = self.ingest_data()
        self.df = self.clean_data(df)
        
        self.save_data()
        return self.df
    
    def ingest_data(self) -> pd.DataFrame:
        """Concatenate multiple files into a single dataframe
        
        Arguments:
            filepaths: list of filepaths
        Returns:
            df: concatenated dataframe
        """
        frames = [pd.read_csv(file_path, compression = 'zip', low_memory = False, index_col = "id") 
                  for file_path in self.raw_data_path]
        
        df = pd.concat(frames)   
        df.drop_duplicates(inplace=True) 
        
        return df
    
    def clean_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the data and selects the features to be used in the model.
        Arguments:
            df (pandas.DataFrame): Raw data.
        Returns:
            df (pandas.DataFrame): Cleaned data.
        """
        # Keep relevant columns
        df = df[data_conf.keep_columns]
        
        # Drop irrelevant rows
        df = self._drop_rows(df)
        
        # Standardize price
        df = self._convert_price_to_usd(df)
        
        self.df = df
        return self.df
    
    def save_data(self, 
                  df: pd.DataFrame = None) -> None:
        """Save the processed dataframe to the specified data path
        
        Arguments:
            df: dataframe to be saved
        """
        df = self.df if df is None else df
        
        os.makedirs(os.path.dirname(self.processed_data_path), exist_ok=True)
            
        df.to_csv(self.processed_data_path, index=False)

    def _drop_rows(self, df:pd.DataFrame) -> pd.DataFrame:
        """Drops irrelevant rows.
        Arguments:
            df (pandas.DataFrame): Raw data.
        Returns:
            df (pandas.DataFrame): Data without irrelevant rows.
        """
        # Delete under-representative countries
        df = df[~df["l1"].isin(data_conf.drop_rows.countries)]
        
        # Delete rows with NaN values 
        df = df.dropna(subset=data_conf.drop_rows.nan, how = 'any', ignore_index=True)
        
        # Drop duplicates based on lat and lon
        df = df.drop_duplicates(subset=data_conf.drop_rows.duplicates, keep='first', ignore_index=True)
        
        return df

    def _convert_price_to_usd(self, df:pd.DataFrame) -> pd.DataFrame:
        """Standardizes price.
        Arguments:
            df (pandas.DataFrame): Raw data.
        Returns:
            df (pandas.DataFrame): Data with standardized price.
        """
        # Standardize currency to USD 
        df["price_usd"] = df.apply(lambda x: self._convert_to_usd(x["price"], x["currency"]), axis=1, result_type="expand")
        
        # Drop "price" and "currency" columns
        df = df.drop(columns = ["price", "currency"])
        
        # Drop extreme outlier prices
        mask_price_low = df["price_usd"] >= np.percentile(df["price_usd"], data_conf.outliers_percentile.price.lower)
        mask_price_high = df["price_usd"] <= np.percentile(df["price_usd"], data_conf.outliers_percentile.price.upper)
        df = df[mask_price_low & mask_price_high]
    
        return df

    def _convert_to_usd(self, amount:float, currency_code:str) -> float:
        """Converts the amount to USD using 
        average exchange rate to USD for 2020

        Args:
            amount (float): amount in local currency
            currency_code (str): 3-character currency code

        Returns:
            float: _description_
        """
        currency_dict = {
            "USD": 1,
            "PEN": 0.2863,
            "ARS": 0.0143,
            "UYU": 0.0239,
            "COP": 0.00027,
        }
        if currency_code in currency_dict:
            return amount * currency_dict[currency_code]

if __name__ == "__main__":
    data_wrangler = DataWrangler()
    data_wrangler.load_data(use_exist=False)
    data_wrangler.df.info()