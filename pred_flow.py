from prefect import flow
from app.inference.forecast import forecast_flow
from dotenv import dotenv_values
import argparse
import datetime
import yaml

@flow(
    name="InferenceFlow",
    description="Inference/Monitoring Main Flow",
    validate_parameters=True,
    log_prints=True,
)
def pred_flow(db_token, running_date: str, model_path: str) -> None:
    """main flow of weather forecasting & performance monitoring

    Parameters
    ----------
    db_token : str
        MotherDuck Database Credentials
    running_date : str
        running date of the process
    model_path : str
        path of model's pickle file
    """
    forecast_flow(db_token=db_token, 
                  date=running_date, 
                  model_path=model_path)

if __name__ == "__main__":
    ENV = dotenv_values(".env")
    default_date = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=2), "%Y-%m-%d"
    )
    parser = argparse.ArgumentParser(description="ML Job Parameters")
    parser.add_argument("--running_date", default=default_date, type=str)
    args = parser.parse_args()
    with open('conf/params.yaml', 'r') as f:
        conf = yaml.safe_load(f)
    pred_flow(
        db_token=ENV["MOTHERDUCK_TOKEN"],
        running_date=args.running_date,
        model_path=conf['tuner']['model_path']
    )