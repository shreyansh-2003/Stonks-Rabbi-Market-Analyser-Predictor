import warnings
import pmdarima

warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX

import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde
import streamlit as st

st.set_page_config(
    page_title="STONKS RABBI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Fetching Session Data
if isinstance(st.session_state.data, pd.DataFrame):
    data = st.session_state.data
else:
    pass

def plot_closing_price(stock_data):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines')
    )
    fig.update_layout(
        title='Stock Closing Price',
        xaxis_title='Date',
        yaxis_title='Close Prices',
        template='plotly_white',
        width=800,
        height=500,
    )
    return fig


def plot_distribution(stock_data):
    df_close = stock_data['Close']
    x = np.linspace(df_close.min(), df_close.max(), 1000)
    density = gaussian_kde(df_close)(x)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x, y=density, mode='lines', fill='tozeroy', name='Close')
    )
    fig.update_layout(
        title='Distribution of Stock Closing Prices',
        xaxis_title='Price',
        yaxis_title='Density',
        template='plotly_dark',
    )
    fig.update_traces(line_color='#FFA500', line_width=2, fillcolor='rgba(255, 165, 0, 0.3)')
    return fig


def test_stationarity(stock_data):
    df_close = stock_data['Close']
    # Determing rolling statistics
    rolmean = df_close.rolling(12).mean()
    rolstd = df_close.rolling(12).std()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=stock_data.index, y=df_close, mode='lines', line=dict(color='blue'), name='Original')
    )
    fig.add_trace(
        go.Scatter(x=stock_data.index, y=rolmean, mode='lines', line=dict(color='red'), name='Rolling Mean')
    )
    fig.add_trace(
        go.Scatter(x=stock_data.index, y=rolstd, mode='lines', line=dict(color='black'), name='Rolling Std')
    )

    fig.update_layout(
        title='Rolling Mean and Standard Deviation',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        margin=dict(l=50, r=50, t=50, b=50),
    )
    fig.update_traces(line_width=2)

    adft = adfuller(df_close, autolag='AIC')
    output = pd.Series(adft[0:4],
                       index=['Test Statistics', 'p-value', 'No. of lags used', 'Number of observations used'])
    for key, values in adft[4].items():
        output['critical value (%s)' % key] = values
    st.write(output)

    return fig


def plot_seasonal_decompose(stock_data):
    df_close = stock_data['Close']
    result = seasonal_decompose(df_close, model='multiplicative', period=30)

    trace1 = go.Scatter(x=result.observed.index, y=result.observed, name='Observed')
    fig1 = go.Figure([trace1])
    fig1.update_layout(title='Observed Component', xaxis_title='Date', yaxis_title='Price')

    trace2 = go.Scatter(x=result.trend.index, y=result.trend, name='Trend')
    fig2 = go.Figure([trace2])
    fig2.update_layout(title='Trend Component', xaxis_title='Date', yaxis_title='Price')

    trace3 = go.Scatter(x=result.seasonal.index, y=result.seasonal, name='Seasonality')
    fig3 = go.Figure([trace3])
    fig3.update_layout(title='Seasonality Component', xaxis_title='Date', yaxis_title='Price')

    trace4 = go.Scatter(x=result.resid.index, y=result.resid, name='Residual')
    fig4 = go.Figure([trace4])
    fig4.update_layout(title='Residual Component', xaxis_title='Date', yaxis_title='Price')

    return fig1, fig2, fig3, fig4


def plot_eliminate_trend(stock_data):
    df_close = stock_data['Close']
    df_log = np.log(df_close)
    moving_avg = df_log.rolling(12).mean()
    std_dev = df_log.rolling(12).std()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df_close.index, y=std_dev, mode='lines', name='Standard Deviation', line=dict(color='black')))
    fig.add_trace(go.Scatter(x=df_close.index, y=moving_avg, mode='lines', name='Mean', line=dict(color='red')))

    fig.update_layout(title='Moving Average', legend=dict(x=0.7, y=0.9))

    return fig


def plot_train_test_split(stock_data):
    df_close = stock_data['Close']
    train_data, test_data = df_close[3:int(len(df_close) * 0.9)], df_close[int(len(df_close) * 0.9):]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_close.index, y=df_close, name='Train data', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=test_data.index, y=test_data, name='Test data', line=dict(color='blue')))
    fig.update_layout(xaxis_title='Dates', yaxis_title='Closing Prices', legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'))
    return fig


def plot_autoarima(data):
    train_data, test_data = data[:int(len(data) * 0.7)], data[int(len(data) * 0.7):]
    model_autoARIMA = pmdarima.auto_arima(train_data, start_p=0, start_q=0,
                                          test='adf',  # use adftest to find optimal 'd'
                                          max_p=3, max_q=3,  # maximum p and q
                                          m=7,
                                          max_d =  5,  # frequency of series
                                          d=None,  # let model determine 'd'
                                          seasonal=True,  # No Seasonality
                                          start_P=0,
                                          D=0,
                                          trace=True,
                                          error_action='ignore',
                                          suppress_warnings=True,
                                          stepwise=True)
    st.write(model_autoARIMA.summary())
    model_autoARIMA.plot_diagnostics(figsize=(15, 8))
    st.pyplot(plt)

    pred = model_autoARIMA.predict( n_periods=len(test_data))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index[-len(test_data):], y=test_data, name='Actual Test data'))
    fig.add_trace(go.Scatter(x=data.index[-len(test_data):], y=pred, name='Predictions'))
    fig.update_layout(title='autoARIMA Predictions', xaxis_title='Date', yaxis_title='Closing Price')

    st.plotly_chart(fig)


# Fetching Session Data
if isinstance(st.session_state.data, pd.DataFrame):
    data = st.session_state.data
if st.session_state.name_option_sb:
    comp_title = st.session_state.name_option_sb
if st.session_state.data_symbol:
    comp_symbol = st.session_state.data_symbol[0]
else:
    pass

st.markdown("<h1 style='text-align: center; color: red;'>FORECASTING COMPANY STOCKS</h1>", unsafe_allow_html=True)

st.write(f"## {comp_title} ({comp_symbol})")

st.markdown("Forecasting company stocks is important because it helps investors and traders make informed decisions "
            "about buying and selling stocks, which can result in significant financial gains or losses. The process "
            "of "
            "forecasting involves analyzing historical price data to identify patterns and trends, and using "
            "statistical "
            "models to make predictions about future price movements.")

st.markdown("The various visualizations and plots listed below can be helpful in different stages of the forecasting process."
            " The daily closing price visualization can give a quick overview of how the stock price has changed over time, "
            "while the distribution of stock closing prices can help identify the range of prices and any potential outliers. "
            "The stationarity test plot can help ensure that the data is suitable for modeling, while the seasonal decomposition"
            " plot can help identify any recurring patterns in the data.")

st.markdown("The eliminated trend plot can help identify the underlying trend in the data and remove it to better identify any other patterns or trends."
            " The train test split plot can help divide the data into training and testing sets, which can be used to evaluate the accuracy of the models."
            " The auto ARIMA plot can help identify the best parameters for the ARIMA model, which is a common statistical model used in time series forecasting.")

st.markdown("The ARIMA model summary and forecast plot can help evaluate the performance of the model and generate "
            "predictions about future price movements. Overall, these tools can help investors and traders make more"
            " informed decisions about buying and selling stocks, by providing insights into historical trends and"
            " predictions about future price movements.")


st.markdown("### Chose From an Option Below")
with st.spinner("This won't take long..."):
    with st.expander("**Auto ARIMA Diagnostics**"):
        plot_autoarima(data['Close'])

# create expanders for each plot
with st.expander("**Daily Closing Price Visualisation**"):
    fig1 = plot_closing_price(data)
    st.plotly_chart(fig1)

with st.expander("**Distribution of Stock Closing Prices**"):
    fig2 = plot_distribution(data)
    st.plotly_chart(fig2)

with st.expander("**Stationarity Data Test**"):
    fig3 = test_stationarity(data)
    st.plotly_chart(fig3)

with st.expander("**Seasonal Decomposition Plot**"):
    fig_a, fig_b, fig_c, fig_d = plot_seasonal_decompose(data)
    st.plotly_chart(fig_a)
    st.plotly_chart(fig_b)
    st.plotly_chart(fig_c)
    st.plotly_chart(fig_d)

with st.expander("**Eliminated Trend Plot**"):
    fig5 = plot_eliminate_trend(data)
    st.plotly_chart(fig5)

with st.expander("**Train Test Split Plot**"):
    fig6 = plot_train_test_split(data)
    st.plotly_chart(fig6)







