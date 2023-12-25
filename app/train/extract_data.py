import duckdb
from dotenv import dotenv_values
import datetime
import argparse
import yaml

ENV = dotenv_values(".env")


def extract_data(output_path: str) -> None:
    datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    query_date = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=699), "%Y-%m-%d"
    )
    con = duckdb.connect(f"md:?motherduck_token={ENV['MOTHERDUCK_TOKEN']}")
    con.sql("USE ml_apps")
    df_daily = con.sql(f"""
        SELECT strftime(reading_timestamp, '%Y-%m-%d') AS reading_date,
               AVG(temperature) AS temperature,
               MAX(temperature) AS maximum_temperature,
               MIN(temperature) AS minimum_temperature,
        FROM ml_apps.weather_forecasting.hourly_weather_data
        WHERE strftime(reading_timestamp, '%Y-%m-%d') >= '{query_date}'
        GROUP BY reading_date
        ORDER BY reading_date ASC
    """).df()
    con.close()
    df_daily.to_csv(output_path, index=False)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="arguments of data extraction")
    args_parser.add_argument("--conf", required=True)
    args = args_parser.parse_args()
    with open(args.conf, mode="r") as file:
        conf = yaml.safe_load(file)
    extract_data(output_path=conf["extract_data"]["output_path"])
