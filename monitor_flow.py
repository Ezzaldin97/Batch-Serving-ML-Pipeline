from prefect import flow
from app.monitoring.performance_monitoring import perf_monitor_flow
from dotenv import dotenv_values
import argparse
import datetime


@flow(
    name="MonitorFlow",
    description="Inference/Monitoring Main Flow",
    validate_parameters=True,
    log_prints=True,
)
def monitor_flow(db_token, running_date: str) -> None:
    """main flow of monitoring

    Parameters
    ----------
    db_token : str
        MotherDuck Database Credentials
    running_date : str
        running date of the process
    """
    perf_monitor_flow(db_token=db_token, date=running_date)


if __name__ == "__main__":
    ENV = dotenv_values(".env")
    default_date = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=2), "%Y-%m-%d"
    )
    parser = argparse.ArgumentParser(description="ML Job Parameters")
    parser.add_argument("--running_date", default=default_date, type=str)
    args = parser.parse_args()
    monitor_flow(
        db_token=ENV["MOTHERDUCK_TOKEN"],
        running_date=args.running_date,
    )
