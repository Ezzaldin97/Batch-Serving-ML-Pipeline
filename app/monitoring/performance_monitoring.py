from prefect import task, flow
from prefect.tasks import task_input_hash
from typing import Dict, Any
from evidently.report import Report
from evidently.metrics import (
    RegressionQualityMetric,
    RegressionPredictedVsActualPlot,
    RegressionAbsPercentageErrorPlot,
    RegressionErrorNormality,
    RegressionTopErrorMetric,
)
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
    print("Getting Actual/Forecasting Temperacture Data")
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
def perf_reporter(ref_df: pd.DataFrame, curr_df: pd.DataFrame) -> Dict[str, Any]:
    """generate model performance report

    Parameters
    ----------
    ref_df : pd.DataFrame
        reference dataframe that is used to compare
        model performance on
    curr_df : pd.DataFrame
       new dataframe that will test model performance on

    Returns
    -------
    Dict[str, Any]
        dictionary of performance report
    """
    performance_report = Report(
        metrics=[
            RegressionQualityMetric(),
            RegressionPredictedVsActualPlot(),
            RegressionAbsPercentageErrorPlot(),
            RegressionErrorNormality(),
            RegressionTopErrorMetric(),
        ]
    )
    print("calculating model performance metrics")
    performance_report.run(
        reference_data=ref_df,
        current_data=curr_df,
    )
    measures = performance_report.as_dict()["metrics"][0]["result"]["current"]
    normality = performance_report.as_dict()["metrics"][0]["result"]["error_normality"]
    return {**measures, **normality}


@task(
    name="InsertPerformanceReportInDB",
    description="insert performance measures to motherduck",
    tags=["Performance", "Last30", "Real/Forecasting", "MotherDuck"],
    retry_delay_seconds=60,
    retries=3,
    log_prints=True,
    timeout_seconds=60,
)
def perf_to_db(
    conn, perf_report: Dict[str, Any], monitoring_date: str, location_id: str
) -> None:
    """insert model performance results into
    motherduck database

    Parameters
    ----------
    conn : MotherDuck Database Connection
    perf_report: Dict[str, Any]
       performance report measured as dictionary
    monitoring_date : str
       string format of pipeline running date
    location_id: str
       id of the location
    """
    conn.sql("USE ml_apps")
    print(
        f"Deleting performance data records of {monitoring_date} and {location_id} if"
        " they exists"
    )
    conn.sql(f"""
             DELETE FROM ml_apps.weather_forecasting.performance_monitoring
             WHERE monitoring_date = CAST('{monitoring_date}' AS DATE) AND
             location_id = {location_id};
             """)
    print("Inserting New Records")
    conn.sql(f"""
             INSERT INTO ml_apps.weather_forecasting.performance_monitoring
             VALUES(
             {location_id},
             CAST('{monitoring_date}' AS DATE),
             {perf_report['rmse']},
             {perf_report['mean_error']},
             {perf_report['error_std']},
             {perf_report['mean_abs_error']},
             {perf_report['abs_error_std']},
             {perf_report['mean_abs_perc_error']},
             {perf_report['abs_perc_error_std']},
             {perf_report['order_statistic_medians_x']},
             {perf_report['order_statistic_medians_y']},
             {perf_report['slope']},
             {perf_report['intercept']},
             {perf_report['r']}
             );
             """)


@task(
    name="DeleteOutofRangePerformanceData",
    description="delete out of range data",
    tags=["Delete", "PerformanceData", "MotherDuck"],
    retry_delay_seconds=60,
    retries=3,
    log_prints=True,
    timeout_seconds=60,
)
def delete_out_of_range_data(conn, thresh_date: str) -> None:
    print("Deleting Out of Range Data")
    conn.sql(f"""
            DELETE FROM ml_apps.weather_forecasting.performance_monitoring
            WHERE monitoring_date <= CAST('{thresh_date}' AS DATE)-1000
        """)
    print("Data Deleted Successfully")


@flow(
    name="PerformanceMonitoringFlow",
    description="flow of model performance monitoring",
    validate_parameters=True,
    log_prints=True,
)
def perf_monitor_flow(db_token: str, date: str) -> None:
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
        location_ids = df["location_id"].unique()
        for location_id in location_ids:
            print(f"Calculating performance and storing results of {location_id}")
            perf_df = df[["reading_date", "temperature", "forecasted_temperature"]]
            perf_df.rename(
                columns={
                    "temperature": "target",
                    "forecasted_temperature": "prediction",
                },
                inplace=True,
            )
            perf_df.set_index("reading_date", inplace=True)
            perf_report = perf_reporter(ref_df=perf_df, curr_df=perf_df)
            perf_to_db(
                conn=conn,
                perf_report=perf_report,
                monitoring_date=date,
                location_id=location_id,
            )
        delete_out_of_range_data(conn=conn, thresh_date=date)
