import streamlit as st
import pandas as pd
import plotly.graph_objects as go


class ForecastingDashboadServer:
    def __init__(self, running_date: str) -> None:
        self.running_date = running_date

    def get_historical_data(self, conn) -> pd.DataFrame:
        conn.sql("USE ml_apps")
        df = conn.sql(f"""
                      SELECT reading_date, temperature
                      FROM ml_apps.weather_forecasting.daily_weather_data
                      WHERE reading_date BETWEEN 
                      CAST('{self.running_date}' AS DATE) - INTERVAL '120 days' AND 
                      CAST('{self.running_date}' AS DATE);
                 """).df()
        df.dropna(inplace=True)
        return df

    def get_forecasting_data(self, conn) -> pd.DataFrame:
        conn.sql("USE ml_apps")
        df = conn.sql(f"""
                      SELECT reading_date, forecasted_temperature
                      FROM ml_apps.weather_forecasting.daily_forecasted_weather
                      WHERE reading_date BETWEEN 
                      CAST('{self.running_date}' AS DATE) - INTERVAL '30 days' AND 
                      CAST('{self.running_date}' AS DATE) + INTERVAL '30 days';
                 """).df()
        df.dropna(inplace=True)
        return df

    def plot_it(self, hist_df: pd.DataFrame, preds_df: pd.DataFrame) -> None:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist_df["reading_date"],
                y=hist_df["temperature"],
                mode="lines",
                name="actual temperature",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=preds_df["reading_date"],
                y=preds_df["forecasted_temperature"],
                mode="lines+markers",
                name="forecasted_temperature",
            )
        )
        st.plotly_chart(fig)
