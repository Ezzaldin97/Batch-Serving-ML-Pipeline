from prefect import task, flow
from prefect.tasks import task_input_hash
from typing import Dict, Any
from evidently.report import Report
from evidently.metrics import *
import duckdb
import pandas as pd
import datetime


@task(
    name="GetLast30DaysData",
    description="get last 30 days of real/forecasting data",
    tags=["Get", "Data", "Real/Forecasting"],
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(minutes=10),
    retry_delay_seconds=30,
    retries=3,
    log_prints=True,
    timeout_seconds=60,
)
def get_monitoring_data(conn, running_date: str) -> pd.DataFrame:
    """get forcasting and true data of temperature
    that is needed to monitor model performance.

    Parameters
    ----------
    conn : MotherDuck Database Connection
    running_date : str
       string format of pipeline running date

    Returns
    -------
    pd.DataFrame
        pandas dataframe of true and forecasted temperature
    """
    conn.sql("USE ml_apps")
    df = conn.sql(f"""
                  SELECT t1.location_id,
                  t1.reading_date,
                  t1.forecasted_temperature,
                  t2.temperature
                  FROM (
                  SELECT location_id, 
                  reading_date, 
                  forecasted_temperature
                  FROM ml_apps.weather_forecasting.daily_forecasted_weather
                  ) AS t1
                  INNER JOIN (
                  SELECT location_id, 
                  reading_date, 
                  temperature
                  FROM ml_apps.weather_forecasting.daily_weather_data
                  ) AS t2 ON t2.reading_date=t1.reading_date AND 
                       t2.location_id = t1.location_id
                  WHERE t1.reading_date BETWEEN 
                  CAST('{running_date}' AS DATE) - INTERVAL '32 days' 
                  AND CAST('{running_date}' AS DATE) - INTERVAL '2 days';
                  """).df()
    return df


@task(
    name="PerformanceReport",
    description="calculate performance measures of the last 30 days",
    tags=["Performance", "Last30", "Real/Forecasting"],
    retry_delay_seconds=30,
    retries=3,
    log_prints=True,
    timeout_seconds=120,
)
def perf_report(
    df: pd.DataFrame, location_id: str, monitoring_dt: str
) -> Dict[str, Any]:
    pass


@flow(
    name="PerformanceMonitoringFlow",
    description="flow of model performance monitoring",
    validate_parameters=True,
    log_prints=True,
)
def data_prep_flow(db_token: str, date: str) -> None:
    """sub-flow of preparing data of performance monitoring

    Parameters
    ----------
    db_token: MotherDuck Database Credentials
    date: str
        running date of the process,
    """
    print("Connecting To MotherDuck to Load Data")
    with duckdb.connect(f"md:?motherduck_token={db_token}") as conn:
        print("Connection Successfully intiated")
        df = get_monitoring_data(conn, date)
        perf_df = df[["reading_date", "temperature", "forecasted_temperature"]]
        perf_df.rename(
            columns={"temperature": "target", "forecasted_temperature": "prediction"},
            inplace=True,
        )
        perf_df.set_index("reading_date", inplace=True)
