# Data Quality/Model Performance Monitoring:

![](../../imgs/pipeline.PNG)

in previous steps we covered [inference](../inference/) and how to get and prepare the data pipeline to be aggregated on a daily level in [data-pipeline](../api_data/), now we have all things we need to monitor performance.
now, data is extracted, prepared daily, and a model works monthly to forecast the next 30 days.

according to [evidentlyAI](https://www.evidentlyai.com/), to monitor performance, we need **reference dataset, and current dataset**, both used to create different, and wide-range of performance/statistical tests to compare the performance of model on current/new(production) data, and reference data(train).

daily temperature data, and forecasted data are stored in MotherDuck Database, first we need to get them using the following:
```SQL
SELECT t1.location_id,
       t1.reading_date,
       t1.forecasted_temperature,
       t2.temperature
FROM (
  SELECT location_id, 
         reading_date, 
         forecasted_temperature
  FROM ml_apps.weather_forecasting.daily_forecasted_weather
) AS t1
INNER JOIN (
  SELECT location_id, 
         reading_date, 
         temperature
  FROM ml_apps.weather_forecasting.daily_weather_data
) AS t2 ON t2.reading_date=t1.reading_date AND 
     t2.location_id = t1.location_id
WHERE t1.reading_date BETWEEN 
      CAST('{running_date}' AS DATE) - INTERVAL '32 days' 
      AND CAST('{running_date}' AS DATE) - INTERVAL '2 days';
```

this will get all needed data(past 30 days) per data per location.

using evidentlyAI performance metrics, we can calculate different performance metrics, and store them in MotherDuck to be used, and analyzed.

as a Developer, you need to specify what's needed to monitor the performance, and create the table that will hold all the measures in MotherDuck
```SQL
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

this table will store the needed information from the output of regression performance report of evidentlyAI,
this is an example of the output:
```JSON
{'metrics': [{'metric': 'RegressionQualityMetric',
   'result': {'columns': {'utility_columns': {'date': None,
      'id': None,
      'target': 'target',
      'prediction': 'prediction'},
     'num_feature_names': [],
     'cat_feature_names': [],
     'text_feature_names': [],
     'datetime_feature_names': [],
     'target_names': None},
    'current': {'r2_score': -1.3432220340204881,
     'rmse': 1.5383304357528687,
     'mean_error': 1.3843027353286743,
     'mean_abs_error': 1.3843027353286743,
     'mean_abs_perc_error': 8.623530715703964,
     'abs_error_max': 2.5520782470703125,
     'underperformance': {'majority': {'mean_error': 1.405837893486023,
       'std_error': 0.4854111671447754},
      'underestimation': {'mean_error': 0.0011749267578125, 'std_error': nan},
      'overestimation': {'mean_error': 2.5520782470703125, 'std_error': nan}},
     'error_std': 0.7007785439491272,
     'abs_error_std': 0.7007785439491272,
     'abs_perc_error_std': 0.04213497042655945},
    'reference': {'r2_score': -1.3432220340204881,
     'rmse': 1.5383304357528687,
     'mean_error': 1.3843027353286743,
     'mean_abs_error': 1.3843027353286743,
     'mean_abs_perc_error': 8.623530715703964,
     'abs_error_max': 2.5520782470703125,
     'underperformance': {'majority': {'mean_error': 1.405837893486023,
       'std_error': 0.4854111671447754},
      'underestimation': {'mean_error': 0.0011749267578125, 'std_error': nan},
      'overestimation': {'mean_error': 2.5520782470703125, 'std_error': nan}},
     'error_std': 0.7007785439491272,
     'abs_error_std': 0.7007785439491272,
     'abs_perc_error_std': 0.04213497042655945},
    'rmse_default': 1.0049463510513306,
    'me_default_sigma': 0.7007785439491272,
    'mean_abs_error_default': 0.7524304389953613,
    'mean_abs_perc_error_default': 4.9902841448783875,
    'abs_error_max_default': 2.4562501907348633,
    'error_normality': {'order_statistic_medians_x': [-1.5881546429662674,
      -1.0981497546858916,
      -0.7825592680591444,
      -0.5306911286167685,
      -0.30892352547711976,
      -0.10153400250628433,
      0.1015340025062842,
      0.30892352547711976,
      0.5306911286167681,
      0.7825592680591442,
      1.0981497546858916,
      1.5881546429662674],
     'order_statistic_medians_y': [0.0011749267578125,
      0.7285175323486328,
      0.8016166687011719,
      0.9956569671630859,
      1.114882469177246,
      1.272003173828125,
      1.5582199096679688,
      1.7376518249511719,
      1.9147911071777344,
      1.9312744140625,
      2.003765106201172,
      2.5520782470703125],
     'slope': 0.7450270677849745,
     'intercept': 1.3843027353286743,
     'r': 0.9857029270119115},
    'error_bias': {}}},
  {'metric': 'RegressionPredictedVsActualPlot', 'result': {}},
  {'metric': 'RegressionAbsPercentageErrorPlot', 'result': {}},
  {'metric': 'RegressionErrorNormality', 'result': {}},
  {'metric': 'RegressionTopErrorMetric', 'result': {}}]}
```

last phase to create the dashboard, or UI to interact with database, and show results.