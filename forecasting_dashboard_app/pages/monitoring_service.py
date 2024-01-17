import streamlit as st
import duckdb
from serve.monitoring import MonitoringServer
from typing import List
from dotenv import dotenv_values
import datetime

st.set_page_config(
    page_title="monitoring service",
    page_icon="📊",
)

st.markdown("# Monitoring Service")
st.sidebar.header("Monitoring Service")

last_date = datetime.datetime.now() - datetime.timedelta(days=2)
first_date = datetime.datetime.now() - datetime.timedelta(days=50)
monitor_server = MonitoringServer()
ENV = dotenv_values(".env")


@st.cache_data
def get_ids_data() -> List[int]:
    db_token = ENV["MOTHERDUCK_TOKEN"]
    with duckdb.connect(f"md:?motherduck_token={db_token}") as conn:
        ids = monitor_server.get_location_ids(conn=conn)
    return ids


@st.cache_data
def get_dashboard_data(id: int, date: str):
    db_token = ENV["MOTHERDUCK_TOKEN"]
    with duckdb.connect(f"md:?motherduck_token={db_token}") as conn:
        data = monitor_server.get_perf_report_data(
            conn=conn,
            id=id,
            monitor_date=date,
        )
    return data


d = st.date_input(
    label="Performance Monitoring Date:",
    value=last_date,
    max_value=last_date,
    min_value=first_date,
    format="YYYY-MM-DD",
)

id = st.selectbox(
    "Location ID",
    get_ids_data(),
)

data = get_dashboard_data(id, d)

st.write("### Model Performance Report")
st.write("#### Model Quality")
col1, col2, col3, col4 = st.columns(4)
try:
    col1.metric("RMSE", f"{round(data.loc[0, 'RMSE'], 2):.2f}", delta_color="off")
    col2.metric(
        "ME",
        f"{round(data.loc[0, 'mean_error'], 2):.2f}",
        f"{round(data.loc[0, 'error_std'], 2):.2f}(+/-)",
        delta_color="off",
    )
    col3.metric(
        "MAE",
        f"{round(data.loc[0, 'mean_abs_error'], 2):.2f}",
        f"{round(data.loc[0, 'abs_error_std'], 2):.2f}(+/-)",
        delta_color="off",
    )
    col4.metric(
        "MAPE",
        f"{round(data.loc[0, 'mean_abs_perc_error'], 2):.2f}",
        f"{round(data.loc[0, 'abs_perc_error_std'], 2):.2f}(+/-)",
        delta_color="off",
    )

    st.write("#### Error Normality")
    monitor_server.plot_error_normality(
        x=data.loc[0, "order_statistic_medians_x"],
        y=data.loc[0, "order_statistic_medians_y"],
    )
except KeyError:
    st.write("#### No Data Provided Now")
