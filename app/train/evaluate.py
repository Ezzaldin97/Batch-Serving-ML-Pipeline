from sktime.performance_metrics.forecasting import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    mean_squared_percentage_error,
)
from sktime.utils.plotting import plot_series
from typing import Dict, Any, Union
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import yaml
import json
import argparse
import os


class Eval:
    def __init__(
        self,
        eval_params: Dict[str, Any],
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        model_path,
        fh: int,
    ) -> None:
        self.eval_params = eval_params
        self.train_df = train_df[len(train_df) - 365 :]
        self.test_df = test_df
        with open(model_path, "rb") as pkl:
            self.model = pickle.load(pkl)
        self.fh = fh

    @staticmethod
    def calc_metrics(preds, true) -> Dict[str, Union[int, float]]:
        return {
            "mean-absolute-percentage-error": mean_absolute_percentage_error(
                true, preds
            ),
            "mean-squared-percentage-error": mean_squared_percentage_error(true, preds),
            "mean-absolute-error": mean_absolute_error(true, preds),
            "mean-squared-error": mean_squared_error(true, preds),
        }

    @staticmethod
    def plot_pred_vs_true(train, true, preds) -> None:
        fig, ax = plot_series(
            train,
            true,
            preds,
            labels=["train", "test", "preds"],
            title="history VS test VS predictions",
        )
        plt.setp(ax.get_xticklabels(), rotation=90)
        return plt.gcf()

    def eval(self) -> None:
        preds = self.model.update_predict_single(
            fh=range(1, self.fh + 1),
            y=self.train_df,
            update_params=self.eval_params["update_model_params"],
        )
        metrics = Eval.calc_metrics(preds=preds, true=self.test_df)
        with open(self.eval_params["metrics_file"], "w") as js:
            json.dump(metrics, js, indent=4)
        plot = Eval.plot_pred_vs_true(self.train_df, self.test_df, preds)
        plot.savefig(self.eval_params["true_and_prediction"])


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="arguments of evaluate")
    args_parser.add_argument("--conf", required=True)
    args = args_parser.parse_args()
    with open(args.conf, mode="r") as file:
        conf = yaml.safe_load(file)
    fh = conf["tuner"]["cv"]["fh"]
    train_df = pd.read_csv(conf["split_data"]["train_output_path"])
    train_df["reading_date"] = pd.to_datetime(train_df["reading_date"])
    train_df.set_index("reading_date", inplace=True)
    test_df = pd.read_csv(conf["split_data"]["test_output_path"])
    test_df["reading_date"] = pd.to_datetime(test_df["reading_date"])
    test_df.set_index("reading_date", inplace=True)
    evaluator = Eval(
        eval_params=conf["evaluate"],
        train_df=train_df,
        test_df=test_df,
        model_path=conf["tuner"]["model_path"],
        fh=fh,
    )
    evaluator.eval()
