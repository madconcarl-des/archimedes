"""
Archimedes POC1: Data Ingestion Service

This module handles fetching economic data from public APIs:
- IMF (International Monetary Fund)
- World Bank
- OECD (Organisation for Economic Co-operation and Development)
- FRED (Federal Reserve Economic Data)
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting economic data from public APIs"""

    def __init__(self, database_url: str, fred_api_key: Optional[str] = None):
        """
        Initialize the data ingestion service

        Args:
            database_url: PostgreSQL connection string
            fred_api_key: API key for FRED (optional for other sources)
        """
        self.database_url = database_url
        self.fred_api_key = fred_api_key
        self.engine = create_engine(database_url)

    def fetch_imf_data(self, country_code: str, indicator: str, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Fetch data from IMF International Financial Statistics

        Args:
            country_code: ISO 2-letter country code (e.g., 'US')
            indicator: IMF indicator code (e.g., 'NGDP_R_K_SA_XDC' for real GDP)
            start_year: Start year for data
            end_year: End year for data

        Returns:
            pandas DataFrame with columns: date, value, country_code, indicator
        """
        try:
            base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
            # Example: CompactData/IFS/Q.US.NGDP_R_K_SA_XDC
            endpoint = f"{base_url}CompactData/IFS/Q.{country_code}.{indicator}"

            logger.info(f"Fetching IMF data: {country_code} - {indicator}")
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse SDMX-JSON structure
            observations = []
            try:
                series = data['CompactData']['DataSet']['Series']
                if isinstance(series, dict):
                    series = [series]

                for s in series:
                    obs = s.get('Obs', [])
                    if isinstance(obs, dict):
                        obs = [obs]

                    for o in obs:
                        observations.append({
                            'date': pd.to_datetime(o['@TIME_PERIOD']),
                            'value': float(o['@OBS_VALUE']),
                            'country_code': country_code,
                            'indicator': indicator,
                            'source': 'IMF'
                        })
            except (KeyError, TypeError) as e:
                logger.warning(f"Error parsing IMF data: {e}")

            df = pd.DataFrame(observations)
            logger.info(f"Fetched {len(df)} observations from IMF")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching IMF data: {e}")
            return pd.DataFrame()

    def fetch_worldbank_data(self, country_code: str, indicator: str, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Fetch data from World Bank API

        Args:
            country_code: ISO 3-letter country code (e.g., 'USA')
            indicator: World Bank indicator code (e.g., 'NY.GDP.MKTP.KD.ZG' for GDP growth)
            start_year: Start year for data
            end_year: End year for data

        Returns:
            pandas DataFrame with columns: date, value, country_code, indicator
        """
        try:
            base_url = "https://api.worldbank.org/v2/"
            endpoint = f"{base_url}country/{country_code}/indicator/{indicator}"
            params = {
                'format': 'json',
                'date': f"{start_year}:{end_year}",
                'per_page': 1000
            }

            logger.info(f"Fetching World Bank data: {country_code} - {indicator}")
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # World Bank returns [metadata, data]
            if len(data) < 2 or data[1] is None:
                logger.warning(f"No data returned from World Bank for {country_code} - {indicator}")
                return pd.DataFrame()

            observations = []
            for item in data[1]:
                if item['value'] is not None:
                    observations.append({
                        'date': pd.to_datetime(f"{item['date']}-01-01"),
                        'value': float(item['value']),
                        'country_code': item['countryiso3code'],
                        'indicator': indicator,
                        'source': 'World Bank'
                    })

            df = pd.DataFrame(observations)
            logger.info(f"Fetched {len(df)} observations from World Bank")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching World Bank data: {e}")
            return pd.DataFrame()

    def fetch_oecd_data(self, country_code: str, indicator: str, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Fetch data from OECD API

        Args:
            country_code: ISO 3-letter country code (e.g., 'USA')
            indicator: OECD indicator code
            start_year: Start year for data
            end_year: End year for data

        Returns:
            pandas DataFrame with columns: date, value, country_code, indicator
        """
        try:
            # OECD uses SDMX-JSON format
            # Example: GDP from Quarterly National Accounts
            base_url = "https://stats.oecd.org/SDMX-JSON/data/"
            dataset = "QNA"  # Quarterly National Accounts
            # Structure: LOCATION.MEASURE.TRANSFORMATION.FREQUENCY
            endpoint = f"{base_url}{dataset}/{country_code}.{indicator}.Q"
            params = {
                'startTime': f"{start_year}-Q1",
                'endTime': f"{end_year}-Q4"
            }

            logger.info(f"Fetching OECD data: {country_code} - {indicator}")
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            observations = []
            try:
                dataSets = data['dataSets'][0]['series']
                for key, series in dataSets.items():
                    obs = series['observations']
                    for time_idx, value_list in obs.items():
                        # Parse quarter (e.g., "0:0:0:0" = index 0 in each dimension)
                        observations.append({
                            'date': pd.to_datetime(f"{start_year + int(time_idx)//4}-{(int(time_idx)%4)*3+1}-01"),
                            'value': float(value_list[0]),
                            'country_code': country_code,
                            'indicator': indicator,
                            'source': 'OECD'
                        })
            except (KeyError, IndexError) as e:
                logger.warning(f"Error parsing OECD data: {e}")

            df = pd.DataFrame(observations)
            logger.info(f"Fetched {len(df)} observations from OECD")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching OECD data: {e}")
            return pd.DataFrame()

    def fetch_fred_data(self, series_id: str, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Fetch data from FRED (Federal Reserve Economic Data)

        Args:
            series_id: FRED series ID (e.g., 'GDP' for US Gross Domestic Product)
            start_year: Start year for data
            end_year: End year for data

        Returns:
            pandas DataFrame with columns: date, value, indicator
        """
        if not self.fred_api_key:
            logger.warning("FRED API key not provided, skipping FRED data fetch")
            return pd.DataFrame()

        try:
            base_url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'observation_start': f"{start_year}-01-01",
                'observation_end': f"{end_year}-12-31"
            }

            logger.info(f"Fetching FRED data: {series_id}")
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            observations = []
            for item in data.get('observations', []):
                if item['value'] != '.':  # FRED uses '.' for missing values
                    observations.append({
                        'date': pd.to_datetime(item['date']),
                        'value': float(item['value']),
                        'country_code': 'USA',  # FRED is US-only
                        'indicator': series_id,
                        'source': 'FRED'
                    })

            df = pd.DataFrame(observations)
            logger.info(f"Fetched {len(df)} observations from FRED")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching FRED data: {e}")
            return pd.DataFrame()

    def save_to_database(self, df: pd.DataFrame, table_name: str = 'observations'):
        """
        Save DataFrame to PostgreSQL database

        Args:
            df: pandas DataFrame to save
            table_name: Name of the table to save to
        """
        if df.empty:
            logger.warning("Empty DataFrame, nothing to save")
            return

        try:
            # Append to existing table, replace duplicates
            df.to_sql(
                table_name,
                self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            logger.info(f"Saved {len(df)} rows to {table_name}")

        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    def run_daily_ingestion(self, countries: List[str], indicators: Dict[str, List[str]], start_year: int, end_year: int):
        """
        Run daily data ingestion for all sources

        Args:
            countries: List of country codes
            indicators: Dict of {source: [indicator_codes]}
            start_year: Start year for historical data
            end_year: End year (usually current year)
        """
        logger.info("Starting daily data ingestion")

        all_data = []

        # Fetch from each source
        for country in countries:
            # IMF data
            for indicator in indicators.get('imf', []):
                df = self.fetch_imf_data(country, indicator, start_year, end_year)
                if not df.empty:
                    all_data.append(df)

            # World Bank data
            for indicator in indicators.get('worldbank', []):
                df = self.fetch_worldbank_data(country, indicator, start_year, end_year)
                if not df.empty:
                    all_data.append(df)

            # OECD data
            for indicator in indicators.get('oecd', []):
                df = self.fetch_oecd_data(country, indicator, start_year, end_year)
                if not df.empty:
                    all_data.append(df)

        # FRED data (US only)
        for indicator in indicators.get('fred', []):
            df = self.fetch_fred_data(indicator, start_year, end_year)
            if not df.empty:
                all_data.append(df)

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Total observations fetched: {len(combined_df)}")

            # Save to database
            self.save_to_database(combined_df)
        else:
            logger.warning("No data fetched from any source")

        logger.info("Daily ingestion completed")


# Example usage
if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://archimedes:password@localhost:5432/archimedes_poc1"
    FRED_API_KEY = "your_fred_api_key_here"  # Get from https://fred.stlouisfed.org/docs/api/api_key.html

    # G20 countries (subset for POC)
    G20_COUNTRIES = ['USA', 'CHN', 'JPN', 'DEU', 'GBR', 'FRA', 'IND', 'BRA', 'CAN', 'AUS']

    # Indicators to fetch
    INDICATORS = {
        'worldbank': [
            'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
            'FP.CPI.TOTL.ZG',     # Inflation, consumer prices (annual %)
            'SL.UEM.TOTL.ZS',     # Unemployment, total (% of labor force)
        ],
        'fred': [
            'GDP',      # Gross Domestic Product
            'CPIAUCSL', # Consumer Price Index
            'UNRATE',   # Unemployment Rate
        ]
    }

    # Initialize service
    service = DataIngestionService(DATABASE_URL, FRED_API_KEY)

    # Run ingestion for 2000-2024
    service.run_daily_ingestion(
        countries=G20_COUNTRIES,
        indicators=INDICATORS,
        start_year=2000,
        end_year=2024
    )

    print("Data ingestion completed successfully!")
