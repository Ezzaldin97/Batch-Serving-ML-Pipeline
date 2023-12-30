from prefect import task, flow
from prefect.tasks import task_input_hash
from sktime.exceptions import NotFittedError
import pandas as pd
import datetime
import duckdb
import pickle


@task(
    name="GetInferenceData",
    description="get daily weather data that are needed to forecast weather",
    tags=["Get", "InferenceData"],
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(minutes=10),
    retry_delay_seconds=30,
    retries=3,
    log_prints=True,
    timeout_seconds=60,
)
def get_inference_data(conn, running_date: str) -> pd.DataFrame:
    """connect to motherduck,
    and get data needed to forecast next 30 days

    Parameters
    ----------
    conn : MotherDuck Database Connection
    running_dt: str
         string format of pipeline running date

    Returns
    -------
    pd.DataFrame
        dataframe of daily historical weather data.
    """
    df = conn.sql(
        "SELECT * FROM ml_apps.weather_forecasting.daily_weather_data WHERE"
        f" reading_date >= CAST('{running_date}' AS DATE) - INTERVAL '400 days'"
    ).df()
    return df


@task(
    name="ForecastWeather",
    description="Forecast the next 30",
    tags=["Forecast", "Inference"],
    retry_delay_seconds=30,
    retries=3,
    log_prints=True,
    timeout_seconds=30,
)
def forecast_weather(hist_df: pd.DataFrame, model_path: str) -> pd.DataFrame:
    """forecast the temperature next 30 days

    Parameters
    ----------
    hist_df : pd.DataFrame
        historical temperature dataframe
    model_path : str
        path of pickle file

    Returns
    -------
    pd.DataFrame
       dataframe of forecasted temperature

    Raises
    ------
    NotFittedError
        Exception class to raise if estimator is used before fitting
    """
    id = pd.Series([75354428 for _ in range(30)], name="location_id")
    scoring_df = hist_df[["reading_date", "temperature"]]
    scoring_df.set_index("reading_date", inplace=True)
    with open(model_path, "rb") as pkl:
        model = pickle.load(pkl)
    try:
        model.check_is_fitted()
        preds = model.update_predict_single(
            fh=range(1, 31), y=scoring_df, update_params=False
        )
        preds.reset_index(inplace=True)
        preds.columns = ["reading_date", "forecasted_temperature"]
        preds = pd.concat([id, preds], axis=1)
        return preds
    except NotFittedError:
        raise NotFittedError("Loaded Model isn't fitted on Training Data")


@task(
    name="LoadForecastsIntoMotherDuck",
    description="Load Weather Forecasts into database",
    tags=["Load", "ForecastedData", "Database"],
    retry_delay_seconds=30,
    retries=3,
    log_prints=True,
    timeout_seconds=60,
)
def load_forecasts_into_db(conn, preds_df: pd.DataFrame) -> None:
    """load forecasted temperature to motherduck

    Parameters
    ----------
    conn : MotherDuck Database Connection
    preds_df : pd.DataFrame
        dataframe of forecasted temperature
    """
    conn.sql(
        "INSERT INTO ml_apps.weather_forecasting.daily_forecasted_weather SELECT * FROM"
        " preds_df"
    )


@flow(
    name="WeatherForecastingFlow",
    description="Forecast Weather, and insert results into DB",
    validate_parameters=True,
    log_prints=True,
)
def forecast_flow(db_token: str, date: str, model_path: str) -> None:
    """flow of inference

    Parameters
    ----------
    db_token : str
        MotherDuck Database Credentials
    date : str
        running date of the process
    model_path : str
        path of pickle file
    """
    print("Connecting To MotherDuck to Get/Load Data")
    with duckdb.connect(f"md:?motherduck_token={db_token}") as conn:
        print("Getting Scoring Data From MotherDuck")
        df = get_inference_data(conn=conn, running_date=date)
        if len(df) > 0:
            preds = forecast_weather(hist_df=df, model_path=model_path)
            print(f"Model Forecasted Next {len(preds)} days")
            load_forecasts_into_db(conn=conn, preds_df=preds)
            print("Data Loaded into MotherDuck")
        else:
            print("No Records in Scoring data..")
    print("Connection with MotherDuck Closed")
