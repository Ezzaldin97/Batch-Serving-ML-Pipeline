# Inference Pipeline:

After Training, and Saving the Model Object, we can move on to the deployment phase, and how to create an Inference Pipeline That can use the New(Unseen) Data, and Model to Predict/Forecast the Target Variable.

## Inference Requirements:

- Model Runs every Month (first Day of Month).
- Raw Data must run first to get the hourly temperature, then Data aggregated to get the daily temperature(Covered in first step).
- Training Considerations:
  - forecasting horizon: **30 days**, model will forecast the next 30 days.
  - window length: **365 days**, model fitted on 365 days.
  - in production model will take the last 400 days temperature data, and forecast the next 30 days.
- Most of Forecasting Models do online training, so when new data provided, it is used to update the model parameters and cutoff value, but here we setted the arguments to update the data only, and keeping the same fitted parameters
```python
# using prophet in sktime package..
preds = model.update_predict_single(
            fh=range(1, 31), y=scoring_df, update_params=False
        )
```

- Forecasting Flow Triggered by This [Gihub Action](../../.github/workflows/trigger_pred_flow.yml)