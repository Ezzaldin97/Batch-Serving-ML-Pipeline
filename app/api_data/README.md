# Weather API Data to Duckdb:

## Implementation Steps:

1- after creating MotherDuck account, and save token to `.env` file, create a database for ML projects, schema for this project, and table to save hourly API data to motherduck:
```SQL
-- create database
CREATE DATABASE IF NOT EXISTS ml_apps;
-- use ml_apps
USE ml_apps;
-- create schema
CREATE SCHEMA IF NOT EXISTS weather_forecasting;
-- create hourly weather api data
CREATE OR REPLACE TABLE ml_apps.weather_forecasting.hourly_weather_data(
  location_id INTEGER,
  reading_timestamp TIMESTAMP_NS,
  temperature FLOAT NOT NULL,
  tz VARCHAR(50)
);
```
for more information about duckdb visit the documentation: [duckdb](https://duckdb.org/docs/archive/0.9.2/)

2- use API url to get the hourly data, and pass parameters to specify the locations, and date, parameters used:
```JSON
{
    "latitude": 30.052723,
    "longitude": 31.190199,
    "start_date": start dat,
    "end_date": end date,
    "hourly": "temperature_2m",
    "timezone": "Africa/Cairo",
}
```
this parameters used to get the hourly temperature in cairo every day. 
to validate the paramaters, before send the request, use pydantic base model to validate the object data:
```python
class URLParams(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    hourly: Union[str, List[str]]
    timezone: str
``` 
3- create a sub-flow to get the data from API, transform it if needed, remove the data if it is found to avoid duplication issues, insert it into database, and remove the old records to maintain storage.
take a look at: [sub-flow](weather_data_flows.py)

4- add the sub-flow to main [main-flow](../../pred_flow.py)

5- test it using 
```bash
make run-pred-flow
```
6- finally, we need to create a schedualed job to run everyday using github actions: [schedualed-job](../../.github/workflows/trigger_pred_flow.yml)