from prefect import flow
from app.api_data.weather_data_flows import data_flow
from app.inference.prepare_daily_data import data_prep_flow
from dotenv import dotenv_values
import argparse
import datetime


@flow(
    name="DataProcessingFlow",
    description="Data Processing & Preparation Main Flow",
    validate_parameters=True,
    log_prints=True,
)
def data_processing_job(data_url, params, db_token, running_date: str) -> None:
    """Parent Flow of Data Processing

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
    inference_flag = data_prep_flow(db_token=db_token, date=running_date)
    if inference_flag:
        print("Inference Can be Started Safely")
    else:
        raise RuntimeError("Daily Data Preparation Flow Failed")


if __name__ == "__main__":
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
    data_processing_job(
        data_url=ENV["METEO_URL"],
        params=url_params,
        db_token=ENV["MOTHERDUCK_TOKEN"],
        running_date=args.running_date,
    )
