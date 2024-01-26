# Streamlit Forecasting Dashboard App:

we need here to create multi-page application that holds performance monitoring service of the model, and forecasting service that shows the forecasting, and actual temperature daily.

using [streamlit](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app), and [ploomber-cloud](https://ploomber.io/), we created multi page streamlit application, and deploy it easly.

to create multi page application, create all secondary pages in sub directory called `pages/`, and the main page must be named `app.py` to follow ploomber cloud instructions, like the following
```shell
# application file structure
.
|-- README.md
|-- app.py
|-- pages
|   |-- monitoring_service.py
|   `-- weather_forecasting_service.py
|-- ploomber-cloud.json
|-- requirements.txt
`-- serve
    |-- monitoring.py
    `-- weather_forecasting.py
```

to deploy the application:

- create ploomber cloud account, and create API key.
- first set API key using
```shell
ploomber-cloud key <API-key>
```
- intialize it
```shell
ploomber-cloud init
```
- you will be asked to choose project type
- to deploy your application 
```shell
ploomber-cloud deploy
```

to trigger, and refresh the application use Github actions [refresh-dashboard](../.github/workflows/refresh_dashboard.yml)