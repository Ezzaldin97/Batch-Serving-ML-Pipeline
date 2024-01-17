import streamlit as st
import pandas as pd
from typing import List
import plotly.graph_objects as go


class MonitoringServer:
    def get_location_ids(self, conn) -> List[int]:
        conn.sql("USE ml_apps")
        ids = conn.sql("""
                 SELECT DISTINCT location_id AS location_id
                 FROM ml_apps.weather_forecasting.performance_monitoring;
                 """).df()
        return ids["location_id"]

    def get_perf_report_data(self, conn, id: int, monitor_date: str) -> pd.DataFrame:
        conn.sql("USE ml_apps")
        data = conn.sql(f"""
                        SELECT *
                        FROM ml_apps.weather_forecasting.performance_monitoring
                        WHERE location_id = {id} AND
                        monitoring_date = CAST('{monitor_date}' AS DATE);
                        """).df()
        return data

    def plot_error_normality(self, x: List[float], y: List[float]) -> None:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name="residuals",
            )
        )
        st.plotly_chart(fig)
