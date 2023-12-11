from prefect import flow
from app.api_data.weather_data_flows import data_flow
from dotenv import dotenv_values
import argparse
import datetime


@flow(
    name="MLBatchFlow",
    description="ML Batch Job Flow",
    validate_parameters=True,
    log_prints=True,
)
def ml_job(data_url, params, db_token, running_date: str) -> None:
    """Parent Flow of Predictive ML Batch Job

    Parameters
    ----------
    data_url : str
        API url
    params : Dict[str, Any]
        Parameters Needed to access API and get data
    db_token : str
        MotherDuck Database Credentials
    running_date : str
        date string format of batch job running date
    """
    data_flow(
        api_data_url=data_url,
        url_params=params,
        db_token=db_token,
        deleting_thresh_dt=running_date,
    )


if __name__ == "__main__":
    API_URL = "https://archive-api.open-meteo.com/v1/archive"
    ENV = dotenv_values(".env")
    default_date = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=2), "%Y-%m-%d"
    )
    parser = argparse.ArgumentParser(description="ML Job Parameters")
    parser.add_argument("--running_date", default=default_date, type=str)
    args = parser.parse_args()
    url_params = {
        "latitude": 30.052723,
        "longitude": 31.190199,
        "start_date": args.running_date,
        "end_date": args.running_date,
        "hourly": "temperature_2m",
        "timezone": "Africa/Cairo",
    }
    ml_job(
        data_url=API_URL,
        params=url_params,
        db_token=ENV["MOTHERDUCK_TOKEN"],
        running_date=args.running_date,
    )
