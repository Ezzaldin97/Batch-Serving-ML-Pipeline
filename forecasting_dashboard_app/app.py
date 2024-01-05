import streamlit as st

st.set_page_config(
    page_title="main",
    page_icon="🤗",
)

st.markdown("# App Main Page")
st.sidebar.header("Main Page")

st.markdown("""
    ## Welcome to Egypt/Cairo Weather Forecasting App! 👋

    Weather Forecasting Service uses:
    - **(Facebook Prophet)[https://facebook.github.io/prophet/]** 
    to forecast next 30 days of temperature in Cairo. 
    - **(Open-Meteo API)[https://open-meteo.com/]** to provide updated data.
    - **(MotherDuck)[https://motherduck.com/]** as project database.
    - **(EvidentlyAI)[https://www.evidentlyai.com/] to calculate monitoring KPIs**
    - **Github-Actions**
    - **(Ploomber Cloud)[https://ploomber.io/] to deploy the application**

    ## Application Pages:

    ### Weather Forecasting Service:

    Plot Temperature Forecasting VS Actual Temperature,
    Forecasting Service runs every month to forecast next 30 days,
    and Actual Values added every day. 

    ### Performance/Data Monitoring Service:

    Monitor data quality, data drift, model performance. 
    """)
