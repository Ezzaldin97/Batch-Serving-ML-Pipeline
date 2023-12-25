from sktime.split import temporal_train_test_split
import pandas as pd
import argparse
import yaml


def split_data(
    test_size: int, data_path: str, train_output_path: str, test_output_path: str
) -> None:
    df = pd.read_csv(data_path)
    df["reading_date"] = pd.to_datetime(df["reading_date"])
    df.set_index("reading_date", inplace=True)
    train_daily, test_daily = temporal_train_test_split(
        y=df["temperature"], test_size=test_size
    )
    train_daily.to_csv(train_output_path)
    test_daily.to_csv(test_output_path)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="arguments of data splitter")
    args_parser.add_argument("--conf", required=True)
    args = args_parser.parse_args()
    with open(args.conf, mode="r") as file:
        conf = yaml.safe_load(file)
    split_data(
        test_size=conf["split_data"]["test_size"],
        data_path=conf["extract_data"]["output_path"],
        train_output_path=conf["split_data"]["train_output_path"],
        test_output_path=conf["split_data"]["test_output_path"],
    )
