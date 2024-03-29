# ML Batch Job

![](imgs/ml-batch-job.svg)

## Objective:

The primary objective of this Machine Learning Batch Job project is to develop a robust and efficient machine learning pipeline for automating the training and deployment of models. The pipeline aims to streamline the end-to-end process of model development, training, evaluation, and deployment, ensuring scalability, reproducibility, and maintainability.

### Reproducibility:

A well-designed machine learning pipeline enables the recreation of experiments, ensuring that results can be reproduced consistently. This is crucial for debugging, validating models, and comparing different versions.

### Scalability:

Scalability is essential for handling large datasets and accommodating the growing complexity of machine learning models. An efficient pipeline can easily scale to handle increased volumes of data and computational demands.

### Automation:

Automation reduces manual intervention, minimizing the chances of errors and improving overall efficiency. A good pipeline automates tasks such as data preprocessing, model training, and deployment, allowing for seamless integration into production environments.

### Model Versioning:

Version control for models is vital for tracking changes, understanding model evolution, and rolling back to previous versions if needed. A well-designed pipeline facilitates proper versioning of models, making it easier to manage and maintain model lifecycle.

### Monitoring and Logging:

A good pipeline incorporates monitoring and logging functionalities, enabling tracking of model performance and system behavior. This is essential for identifying issues promptly, ensuring model health, and making informed decisions for model improvements.

## Project Description:

create a robust, simple, effecient, and modern end to end ML Batch Serving Pipeline Using set of modern open-source/free Platforms/Tools including
- [Free Weather API](https://open-meteo.com/)
- [MotherDuck](https://app.motherduck.com/)
- [Ploomber](https://ploomber.io/)
- [Prefect](https://www.prefect.io/)
- [EvidentlyAI](https://www.evidentlyai.com/)
- [DVC](https://dvc.org/)
- [Streamlit](https://streamlit.io/)
- Github Actions
- Python

the project will focus on the best technical implementation to solve the issues in production environment, and how to use the mensioned platforms and tools to build an end to end pipeline.

## Prerequisities:

- Intermediate Python
- Machine Learning/Time Series Forecasting Concepts
- SQL
- Bash Scripting
- Git Fundamentals
- Basic Understanding of Github Actions(Preferrable)

## Project Setup:

- create an account on the following platforms:
  - [MotherDuck](https://app.motherduck.com/)
  - [Ploomber](https://ploomber.io/)
- create motherduck token, and ploomber api key
- use this url: [Weather-API](https://archive-api.open-meteo.com/v1/archive) to get the data, and for more information please visit the documentation.
- install/use python>=3.10,<3.12
- install [Poetry](https://python-poetry.org/) dependancy management, or create a virtual environment, and use `requirements.txt` to install needed packages.
- use `pyproject.toml` & `poetry.lock` files to install the project dependencies by
```bash
poetry install
```
- install Git & Make Command.
- add all your secret keys to github repository secrets, I added the following:
  - MOTHERDUCK_TOKEN
  - PLOOMBER_API_KEY
  - METERO_URL
feel free to add more based on your needs.

- create the following schema in MotherDuck:
```SQL
-- create database 'ml_apps' & schema for this project 'weather_forecasting'

-- hourly temperature data
CREATE OR REPLACE TABLE ml_apps.weather_forecasting.hourly_weather_data(
  location_id INTEGER,
  reading_timestamp TIMESTAMP_NS,
  temperature FLOAT NOT NULL,
  tz VARCHAR(50)
);

-- daily weather data table
CREATE OR REPLACE TABLE ml_apps.weather_forecasting.daily_weather_data(
  location_id INTEGER,
  reading_date TIMESTAMP_NS,
  temperature FLOAT NOT NULL
);

-- inference TABLE...
CREATE OR REPLACE TABLE ml_apps.weather_forecasting.daily_forecasted_weather(
  location_id INTEGER,
  reading_date TIMESTAMP_NS,
  forecasted_temperature FLOAT NOT NULL,
  inference_date TIMESTAMP_NS
);

-- performance monitoring last 30 days..
CREATE OR REPLACE TABLE ml_apps.weather_forecasting.performance_monitoring(
  location_id INTEGER,
  monitoring_date TIMESTAMP_NS,
  RMSE FLOAT NOT NULL,
  mean_error FLOAT NOT NULL,
  error_std FLOAT NOT NULL,
  mean_abs_error FLOAT NOT NULL,
  abs_error_std FLOAT NOT NULL,
  mean_abs_perc_error FLOAT NOT NULL,
  abs_perc_error_std FLOAT NOT NULL,
  order_statistic_medians_x FLOAT[] NOT NULL,
  order_statistic_medians_y FLOAT[] NOT NULL,
  slope FLOAT NOT NULL,
  intercept FLOAT NOT NULL,
  r FLOAT NOT NULL
);
```

## Project Development:

### From API Data To MotherDuck:

this is a very important, and critical part in every ML lifecycle, of course as all of us know ML models can't work without a continous feed of data in production, this data must be similar to the data used in production, and updated to fire the model.

so, this part get the updated hourly API data everyday from source, and load it to MotherDuck Serverless Database.

this job schedualed using Github Actions to run everyday at specific time to get the data, and load it into the table in motherduck.

for more information about the implementation use the following:

- [From API Data To MotherDuck readme](app/api_data/README.md)

### Model Development:

ML Projects aren't a singular well-defined task, it is iterative process that can take months, or years to optimize model performance, meet business metrics, time complexity, and many other issues.

through model development journey many things can happen, that make development chaotic:

- many versions of experiments.
- no versioning for model artifacts, models, and data
- no unified platform to share results, data, and trails between multiple project developers.
- randomness, and updating code in experiments can produce many issues.

all of this reasons, must be considered when developing the model, and that's why using tools like **DVC, MLFlow, and many more** becomes very important, and skill that must be acquired by Data Scientists, and ML Engineers.

this project uses:

- **DVC**: 
  - for Data, model, and artifacts version control
  - automating training pipeline.
- **DVC-VSCode Extension**: for experiment tracking(DVC Studio can be used for Team.)

for more information about the implementation use the following:

- [Training Using DVC](app/train/README.md)

## Inference/Prodcutionizing the Model:

in machine learning **inference** refers to making predictions using the trained model.

after a successfull training process, the trained model can be deployed to make predictions on unseen data, and here **MLOps Engineer/Data Scientist/Developer** must make sure about the requirements of production environment to produce accurate results, also must make sure that the requirements of the application is considered like low latency in real-time applications.

here we developed a batch-serving forecasting application, and consider everything we need to produce a successfull up-to-date application that forecast the temperature in Cairo/Egypt, for more information about the implementation:

- [Inference](app/inference/README.md)

## Monitoring (Data Quality/Model Performance):

track & analyze model performance in production is one of the important concepts in MLOps, especially for Risky Models that support decisions, just imagine here that business team use a ML Model, and Performance of this Model in Production dropped for some reason 😮😮.

a reliable ML Pipelines have a monitoring service, to help teams track model performance, data quality, and features/target drift.

monitoring ML models help specialized teams to detect issues, understand root-cause, analyze, decision whether to retrain or not, and document the problems and issues that happened to avoid repeating it in the future.

monitoring service can be divided into:

- Business(Product) KPIs
- Model Quality
- Data Quality/Drift
- Software Health

in this project, I tried to create a performance monitoring service using evidentlyAI, and Streamlit, find more about the implementation here: [Monitoring](app/monitoring/README.md)

## Machine Learning application UI Deployment 🎉🎉:

Finally, Last Thing is to show your results, and make it accessible to anyone 🤗.

Using **streamlit**, and **Ploomber Cloud**, you can create an amazing multi page application, and host for free on ploomber cloud 😎.

for more about implementation: [Application UI](forecasting_dashboard_app/README.md)

you can access it from here: [temperature-forecasting-app](https://tiny-salad-1121.ploomberapp.io/)

## Resources:

- [API-Documentation](https://open-meteo.com/en/docs/)
- [Prefect-Documentation](https://docs.prefect.io/latest/)
- [Duckdb](https://duckdb.org/)
- [Duckdb-Book](https://motherduck.com/duckdb-book/)
- [MotherDuck](https://motherduck.com/docs/getting-started)
- [DVC-Course](https://learn.iterative.ai/courses)
- [EvidentlyAI-Course](https://evidentlyai.thinkific.com/courses/ml-observability-course)
- [Monitor-in-Production](https://neptune.ai/blog/how-to-monitor-your-models-in-production-guide)
- [Trigger-Using-Github-Actions](https://ploomber.io/blog/end-to-end/)