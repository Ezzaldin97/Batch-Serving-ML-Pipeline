import pandas as pd
from sktime.forecasting.fbprophet import Prophet
from sktime.split import SlidingWindowSplitter
from sktime.forecasting.model_selection import ForecastingGridSearchCV
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error
from typing import Dict, Any
import yaml
import argparse
import pickle
import json


class Trainer:
    def __init__(
        self, tuning_params: Dict[str, Any], random_state: int, df: pd.DataFrame
    ) -> None:
        self.tuning_params = tuning_params
        self.random_state = random_state
        self.df = df

    @staticmethod
    def get_supported_estimators() -> Dict:
        return {"prophet": Prophet}

    def tuner(self):
        splitter = SlidingWindowSplitter(
            fh=list(range(1, self.tuning_params["cv"]["fh"] + 1)),
            window_length=self.tuning_params["cv"]["window_length"],
            step_length=self.tuning_params["cv"]["step_size"],
        )
        estimators = Trainer.get_supported_estimators()
        if self.tuning_params["estimator_name"] not in estimators.keys():
            raise ValueError(
                f'Unsupported estimator: {self.tuning_params["estimator_name"]}'
            )
        forecaster = estimators[self.tuning_params["estimator_name"]]()
        sscv = ForecastingGridSearchCV(
            forecaster=forecaster,
            cv=splitter,
            param_grid=self.tuning_params[self.tuning_params["estimator_name"]][
                "params"
            ],
            verbose=1,
            scoring=mean_absolute_percentage_error,
        )
        sscv.fit(self.df)
        return sscv, sscv.best_score_, sscv.best_params_

    def train(self) -> None:
        model, score, params = self.tuner()
        results = {"best-score": score, "best-params": params}
        with open(self.tuning_params["training_results"], "w") as file:
            json.dump(results, file, indent=4)
        with open(self.tuning_params["model_path"], mode="wb") as pkl:
            pickle.dump(model, pkl)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="arguments of data splitter")
    args_parser.add_argument("--conf", required=True)
    args = args_parser.parse_args()
    with open(args.conf, mode="r") as file:
        conf = yaml.safe_load(file)
    df = pd.read_csv(conf["split_data"]["train_output_path"])
    df["reading_date"] = pd.to_datetime(df["reading_date"])
    df.set_index("reading_date", inplace=True)
    trainer = Trainer(
        tuning_params=conf["tuner"], random_state=conf["base"]["random_state"], df=df
    )
    trainer.train()
