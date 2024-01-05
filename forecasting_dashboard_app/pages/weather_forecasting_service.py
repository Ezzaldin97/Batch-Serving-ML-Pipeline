import streamlit as st
import pandas as pd
import duckdb

# add this below in development forecasting_dashboard_app.
from serve.weather_forecasting import (
    ForecastingDashboadServer,
)
import datetime
from dotenv import dotenv_values
from typing import Union

ENV = dotenv_values(".env")
current_datetime = datetime.datetime.now()
current_day = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

st.set_page_config(
    page_title="weather forecasting service",
    page_icon="🔮",
)

st.markdown("# Waether Forecasting Service")
st.sidebar.header("Weather Forecasting Service")

st.markdown("## Actual & Forecasted Temperature in Cairo 🌡")

wf_server = ForecastingDashboadServer(running_date=current_day)


@st.cache_data
def get_dashboard_data() -> Union[pd.DataFrame, pd.DataFrame]:
    db_token = ENV["MOTHERDUCK_TOKEN"]
    with duckdb.connect(f"md:?motherduck_token={db_token}") as conn:
        hist = wf_server.get_historical_data(conn)
        preds = wf_server.get_forecasting_data(conn)
    return hist, preds


hist_df, preds_df = get_dashboard_data()
wf_server.plot_it(hist_df, preds_df)
