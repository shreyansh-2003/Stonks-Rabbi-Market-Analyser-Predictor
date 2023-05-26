import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
from pymongo import MongoClient
import yfinance as yf
# Import SessionState
from streamlit.runtime.state import SessionState
from footer import footer

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["finance"]
tickers_meta = db["tickers_meta_ref"]

st.set_page_config(
    page_title="STONKS RABBI (Company Overview)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Loading data from pymongo database finance to local environment
@st.cache_data(experimental_allow_widgets=True)
def get_data(symbol):
    #PyMongo Code
    # Find document with given symbol
    #doc_i = tickers_meta.find({"Symbol": symbol}, {})
    #for doc in doc_i:
    
    #Streamlit Easy Deployment Replacement
    doc = tickers_meta_json[tickers_meta_json["Symbol"]==symbol].to_dict()
    
    if doc:
        # Display basic fields
        st.write(f"## {doc['Name']} ({doc['Symbol']})")
        st.write(f"**Sector:** {doc['Sector']}")
        st.write(f"**Industry:** {doc['Industry']}")
        st.write(f"**Country:** {doc['Country']}")
        st.write(f"**Market Cap:** {doc['Market Cap']}")
        st.write(f"**IPO Year:** {doc['IPO Year']}")
        st.write(f"**Max Years:** {doc['Max Years']}")
        st.write(f"**% Change:** {doc['% Change']}")
        st.write(f"**Net Change:** {doc['Net Change']}")
        st.write(f"**Volume:** {doc['Volume']}")

        # Display dropdown menu for Data attributes
        data = doc["Data"]
        data_keys = list(data.keys())
        data_keys.sort()
        selected_data = st.selectbox(f"**Select One '{doc['Symbol']}' Attribute**", data_keys)

        st.write(f"**{selected_data}:** {data[selected_data]}")

    else:
        st.write("Company Data not found from meta source.")




# Visualising Price Movement of Stocks (Candlestick Chart)
def candlestick_plot(df):
    # Extract unique years from the index
    year_range = df.index.year.unique()
    year_range = [int(year) for year in year_range]
    # Set the default selected year to the most recent year in the data
    selected_year = year_range[-1]
    # Create a slider to select the year
    selected_year = st.slider('**Select Year**', min_value=year_range[0], max_value=year_range[-1], value=selected_year)
    # Filter the data based on the selected year
    filtered_df = df[df.index.year == selected_year]
    filtered_df = filtered_df.sort_index()
    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=filtered_df.index,
        open=filtered_df['Open'],
        high=filtered_df['High'],
        low=filtered_df['Low'],
        close=filtered_df['Close'],
        increasing_line_color='cyan',
        decreasing_line_color='gray'
    )])

    # Set the chart title and axis labels
    fig.update_layout(title=f'High vs Low Price ({selected_year})', xaxis_title='Date', yaxis_title='Price')

    return fig


# Opening vs Closing Price
def plot_open_close(hist, all_years=True):
    if all_years:
        max_year, min_year = hist.index.year.unique()[-1], hist.index.year.unique()[0]
        fig = px.bar(hist, x=hist.index, y=['Open', 'Close'], barmode='group')
        fig.update_layout(title=f'Opening vs Closing Price {min_year}-{max_year}', xaxis_title='Date',
                          yaxis_title='Price')
        return fig

    else:
        # Extract unique years and months from the index
        year_range = hist.index.year.unique()
        year_range = [int(year) for year in year_range]
        month_range = range(0, 13)
        # Set the default selected year and month to the most recent year and None
        selected_year = year_range[-1]
        selected_month = 0
        # Create a dropdown to select the year
        selected_year = st.selectbox('**Select Year**', year_range)
        # Create a slider to select the month
        selected_month = st.slider('**Select Month**', min_value=0, max_value=12, value=selected_month, step=1)
        # Filter the data based on the selected year and month (if any)
        filtered_df = hist[hist.index.year == selected_year]

        if selected_month != 0:
            filtered_df = filtered_df[filtered_df.index.month == selected_month]

        fig = px.bar(filtered_df, x=filtered_df.index, y=['Open', 'Close'], barmode='group')

        if selected_month == 0:
            fig.update_layout(title=f'Opening vs Closing Price ({selected_year})', xaxis_title='Date',
                              yaxis_title='Price')
        else:
            fig.update_layout(title=f'Opening vs Closing Price ({selected_month}/{selected_year})', xaxis_title='Date',
                              yaxis_title='Price')

    return fig


# Comparing High vs Low Price
def plot_high_low(hist, all_years=True):
    if all_years:
        max_year, min_year = hist.index.year.unique()[-1], hist.index.year.unique()[0]
        fig = px.bar(hist, x=hist.index, y=['High', 'Low'], barmode='group',
                     color_discrete_map={'High': 'green', 'Low': 'yellow'})
        fig.update_layout(title=f'High vs Low {min_year}-{max_year}', xaxis_title='Date',
                          yaxis_title='Price',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        return fig

    else:
        # Extract unique years and months from the index
        year_range = hist.index.year.unique()
        year_range = [int(year) for year in year_range]
        month_range = range(0, 13)
        # Set the default selected year and month to the most recent year and None
        selected_year = year_range[-1]
        selected_month = 0
        # Create a dropdown to select the year
        selected_year = st.selectbox('**Select Year**', year_range)
        # Create a slider to select the month
        selected_month = st.slider('**Select Month**', min_value=0, max_value=12, value=selected_month, step=1)
        # Filter the data based on the selected year and month (if any)
        filtered_df = hist[hist.index.year == selected_year]

        if selected_month != 0:
            filtered_df = filtered_df[filtered_df.index.month == selected_month]

        fig = px.bar(filtered_df, x=filtered_df.index, y=['High', 'Low'], barmode='group',
                     color_discrete_map={'High': 'green', 'Low': 'yellow'})

        if selected_month == 0:
            fig.update_layout(title=f'High vs Low Price ({selected_year})', xaxis_title='Date', yaxis_title='Price')
        else:
            fig.update_layout(title=f'High vs Low Price ({selected_month}/{selected_year})', xaxis_title='Date',
                              yaxis_title='Price',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)')

    return fig


def plot_closing_price_over_time(hist, all_years=True):
    if all_years:
        hist = hist.sort_index()
        fig = px.line(hist, x=hist.index, y='Close', color_discrete_map={'Close': 'purple'})
        fig.update_layout(title='Closing Price over Time',
                          xaxis_title='Date', yaxis_title='Price',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)'
                          )

    else:
        # Extract unique years and months from the index
        year_range = hist.index.year.unique()
        year_range = [int(year) for year in year_range]
        month_range = range(0, 13)
        # Set the default selected year and month to the most recent year and None
        selected_year = year_range[-1]
        selected_month = 0
        # Create a dropdown to select the year
        selected_year = st.selectbox('**Select Year**', year_range)
        # Create a slider to select the month
        selected_month = st.slider('**Select Month**', min_value=0, max_value=12, value=selected_month, step=1)
        # Filter the data based on the selected year and month (if any)
        filtered_df = hist[hist.index.year == selected_year]
        prev_year_df = hist[hist.index.year == selected_year-1]

        if selected_month != 0:
            filtered_df = filtered_df[filtered_df.index.month == selected_month]

        filtered_df = filtered_df.sort_index()
        fig = px.line(filtered_df, x=filtered_df.index, y='Close', color_discrete_map={'Close': 'purple'})
        st.write(filtered_df['Close'].mean())

        if filtered_df['Close'].mean() < prev_year_df['Close'].mean():
            st.markdown("**Stock Performance**")
            st.markdown("<h6 style = 'color: red;' >Falling Year</h6 >", unsafe_allow_html=True)

        if filtered_df['Close'].mean() > prev_year_df['Close'].mean():
            st.markdown("**Stock Performance**")
            st.markdown("<h6 style = 'color: green;' >Rising Year</h6 >", unsafe_allow_html=True)

        if selected_month == 0:
            fig.update_layout(title=f'Closing Price over ({selected_year})', xaxis_title='Date', yaxis_title='Price',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)'
                              )
        else:
            fig.update_layout(title=f'Closing Price over ({selected_month}/{selected_year})', xaxis_title='Date',
                              yaxis_title='Price',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)'
                              )

    return fig


def plot_volume_over_time(hist, all_years=True):
    if all_years:
        fig = px.line(hist, x=hist.index, y='Volume', color_discrete_map={'Volume': 'Block'})
        fig.update_layout(title='Volume of Stocks Traded over Time', xaxis_title='Date',
                          yaxis_title='Volume',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)'
                          )

    else:
        # Extract unique years and months from the index
        year_range = hist.index.year.unique()
        year_range = [int(year) for year in year_range]
        month_range = range(0, 13)
        # Set the default selected year and month to the most recent year and None
        selected_year = year_range[-1]
        selected_month = 0
        # Create a dropdown to select the year
        selected_year = st.selectbox('**Select Year**', year_range)
        # Create a slider to select the month
        selected_month = st.slider('**Select Month**', min_value=0, max_value=12, value=selected_month, step=1)
        # Filter the data based on the selected year and month (if any)
        filtered_df = hist[hist.index.year == selected_year]

        if selected_month != 0:
            filtered_df = filtered_df[filtered_df.index.month == selected_month]

        filtered_df = filtered_df.sort_index()
        fig = px.line(filtered_df, x=filtered_df.index, y='Volume', color_discrete_map={'Volume': 'Black'})

        if selected_month == 0:
            fig.update_layout(title=f'Volume of Stocks Traded over ({selected_year})',
                              xaxis_title='Date', yaxis_title='Volume',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)')
        else:
            fig.update_layout(title=f'Volume of Stocks Traded over ({selected_month}/{selected_year})',
                              xaxis_title='Date',
                              yaxis_title='Volume')

    return fig


def plot_daily_pct_change(hist, all_years=True):
    hist['daily_pct_change'] = hist['Close'].pct_change()
    if all_years:
        fig = px.line(hist, x=hist.index, y='daily_pct_change', color_discrete_map={'daily_pct_change': 'purple'})
        fig.update_layout(title='Daily Percentage Change in Closing Price',
                          xaxis_title='Date', yaxis_title='Percentage Change',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
    else:
        # Extract unique years and months from the index
        year_range = hist.index.year.unique()
        year_range = [int(year) for year in year_range]
        month_range = range(0, 13)
        # Set the default selected year and month to the most recent year and None
        selected_year = year_range[-1]
        selected_month = 0
        # Create a dropdown to select the year
        selected_year = st.selectbox('**Select Year**', year_range)
        # Create a slider to select the month
        selected_month = st.slider('**Select Month**', min_value=0, max_value=12, value=selected_month, step=1)
        # Filter the data based on the selected year and month (if any)
        filtered_df = hist[hist.index.year == selected_year]

        if selected_month != 0:
            filtered_df = filtered_df[filtered_df.index.month == selected_month]

        filtered_df = filtered_df.sort_index()
        fig = px.line(filtered_df, x=filtered_df.index, y='daily_pct_change',
                      color_discrete_map={'daily_pct_change': 'purple'})

        if selected_month == 0:
            fig.update_layout(title=f'Daily Percentage Change in Closing Price over ({selected_year})',
                              xaxis_title='Date', yaxis_title='Daily % Change',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)')
        else:
            fig.update_layout(title=f'Daily Percentage Change in Closing Price over ({selected_month}/{selected_year})',
                              xaxis_title='Date',
                              yaxis_title='Daily % Change',
                              plot_bgcolor='rgba(0, 0, 0, 0)',
                              paper_bgcolor='rgba(0, 0, 0, 0)')

    return fig


@st.cache_data
def plot_rolling_average(hist, window=30, all_years=True):
    hist['rolling_avg'] = hist['Close'].rolling(window=window).mean()
    fig = px.line(hist, x=hist.index, y='rolling_avg')

    fig.update_layout(title=f'Rolling Average of Closing Price over {window} Days', xaxis_title='Date',
                      yaxis_title='Price')
    return fig


@st.cache_data
def plot_closing_price_vs_volume(hist, all_years=True):
    fig = px.scatter(hist, x='Close', y='Volume', trendline='ols')

    fig.update_layout(title='Closing Price vs Volume Traded', xaxis_title='Closing Price', yaxis_title='Volume')
    return fig


@st.cache_data
def plot_dist_close(hist, all_years=True):
    fig = px.histogram(hist, x='Close', nbins=20, opacity=0.7)

    fig.update_layout(title='Distribution of Closing Price', xaxis_title='Closing Price', yaxis_title='Count')
    return fig


@st.cache_data
def plot_dist_volume(hist, all_years=True):
    fig = px.histogram(hist, x='Volume', nbins=20, opacity=0.7)

    fig.update_layout(title='Distribution of Volume Traded', xaxis_title='Volume', yaxis_title='Count')
    return fig

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')



if isinstance(st.session_state.json_tickers_meta, pd.DataFrame):
    tickers_meta_json = st.session_state.json_tickers_meta
# Fetching Session Data
if isinstance(st.session_state.data, pd.DataFrame):
    hist = st.session_state.data
    csv = convert_df(hist)
if st.session_state.name_option_sb:
    comp_title = st.session_state.name_option_sb
if st.session_state.data_symbol:
    comp_symbol = st.session_state.data_symbol[0]
else:
    pass

#Title
st.markdown("<h1 style='text-align: center; color: red;'>COMPANY OVERVIEW</h1>", unsafe_allow_html=True)

#Metadata
get_data(comp_symbol)

#Dataset
st.markdown("<h3 style='color: #00008b;'>Company Stock Historical Data</h3>", unsafe_allow_html=True)
# st.markdown("## Company Stock Historical Data")
st.download_button(
    label="Download Data As CSV",
    data=csv,
    file_name='stocks_data.csv',
    mime='text/csv',
)
st.dataframe(hist)


#Plots
st.markdown("<h3 style='color: #00008b;'>Visual Analysis</h3>", unsafe_allow_html=True)

# create a container for the selectbox and the plot
plot_container = st.container()
# List of all dropdown options
options_dd = ['Price Movement of Stocks (Candlestick Chart)',
              'Opening vs Closing Price',
              'High vs Low Price',
              'Closing Price over Time',
              'Volume of Stocks Traded over Time',
              'Percentage Change in Closing Price',
              'Rolling Average of Closing Price over Time',
              'Closing Price vs Volume Traded',
              'Distribution of Closing Price',
              'Distribution of Volume Traded']

# display the selectbox in the container
plot_type = plot_container.selectbox("**Pick a Analysis / Visualization Technique**", options=options_dd)
# plot the selected option in the same container
with plot_container:
    if plot_type == "Price Movement of Stocks (Candlestick Chart)":
        st.markdown("#### Visualising Price Movement of Stocks (Candlestick Chart)")
        st.markdown("A **candlestick chart** is a type of financial "
                    "chart used to represent the *price movement* "
                    "of stocks. The chart displays the ```opening```, "
                    "```closing```, ```high```, and ```low``` prices of the stock in "
                    "a visually appealing way. The body of the candlestick "
                    "represents the opening and closing prices, while "
                    "the wick or shadow represents the high and low prices."
                    " It is an important tool for technical analysis and helps "
                    "investors to identify trends and patterns in the stock market. "
                    "By analyzing candlestick charts, investors can make informed decisions about"
                    " buying or selling stocks.")
        fig = candlestick_plot(hist)
        st.plotly_chart(fig)

    if plot_type == 'Opening vs Closing Price':
        st.markdown("#### Opening vs Closing Price")
        st.markdown("The opening and closing prices of a stock are "
                    "two of the most important pieces of information for investors. "
                    "The ```opening price``` is the price at which a stock opens for trading, "
                    "while the ```closing price``` is the price at which it closes. "
                    "The difference between these two prices can indicate the level of **investor sentiment** "
                    "towards a particular stock. "
                    "A large difference between the opening and closing prices may "
                    "suggest significant market volatility, "
                    "while a small difference may suggest a relatively stable market. "
                    "By monitoring the opening and closing prices, investors can better understand the market "
                    "and make more informed decisions about buying or selling stocks.")

        st.markdown("<h5 style = 'color: #964B00;'>COMBINED</h5>", unsafe_allow_html=True)
        fig_all = plot_open_close(hist, all_years=True)
        st.plotly_chart(fig_all)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_open_close(hist, all_years=False)
        st.plotly_chart(fig)

    elif plot_type == 'High vs Low Price':
        st.markdown("#### Comparing High vs Low Price")
        st.markdown("The high and low prices of a stock are important indicators of the stock's volatility. "
                    "The high price represents the highest price at which the stock was traded during a"
                    " particular period, while the low price represents the lowest price at which it was traded."
                    " By comparing the high and low prices, investors can gain insights into the level of volatility"
                    " of the stock market. A high range between the high and low prices may suggest a more "
                    "volatile market, while a low range may suggest a more stable market. "
                    "Understanding the high and low prices can help investors to make better decisions"
                    " about when to buy or sell stocks.")
        st.markdown("<h5 style = 'color: #964B00;'>COMBINED</h5>", unsafe_allow_html=True)
        fig_all = plot_high_low(hist)
        st.plotly_chart(fig_all)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_high_low(hist, all_years=False)
        st.plotly_chart(fig)


    elif plot_type == 'Closing Price over Time':
        st.markdown("#### Visualising Closing Price over Time")
        st.markdown("The closing price of a stock is the last price at which it was "
                    "traded on a particular day. By analyzing the closing price of a stock "
                    "over time, investors can gain insights into the stock's overall performance. "
                    "The closing price over time can help investors to identify trends and patterns"
                    " in the stock market, which can inform investment decisions. By analyzing "
                    "the closing price over time, investors can determine the best time to"
                    " buy or sell stocks.")
        st.markdown("<h5 style = 'color: #964B00;'>COMBINED</h5>", unsafe_allow_html=True)
        fig_all = plot_closing_price_over_time(hist)
        st.plotly_chart(fig_all, theme=None)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_closing_price_over_time(hist, all_years=False)
        st.plotly_chart(fig, theme=None)

    elif plot_type == 'Volume of Stocks Traded over Time':
        # Reset the color sequence to default

        st.markdown("#### Visualising Volume of Stocks Traded over Time")
        st.markdown("The volume of stocks traded over time is a critical indicator of market sentiment. "
                    "High trading volume may suggest a bullish market, while low trading volume "
                    "may suggest a bearish market. By analyzing the volume of stocks traded over time,"
                    " investors can gain insights into the level of investor interest in a "
                    "particular stock. This information can help investors to make more informed"
                    " decisions about buying or selling stocks.")
        st.markdown("<h5 style = 'color: #964B00;'>COMBINED</h5>", unsafe_allow_html=True)
        fig_all = plot_volume_over_time(hist)
        st.plotly_chart(fig_all, theme=None)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_volume_over_time(hist, all_years=False)
        st.plotly_chart(fig, theme=None)


    elif plot_type == 'Percentage Change in Closing Price':
        st.markdown("#### Visualising Daily % Change in Closing Price")
        st.markdown("The percentage change in the closing price of a stock is an "
                    "important indicator of market performance. It represents the "
                    "percentage increase or decrease in the closing price of a stock "
                    "compared to its previous closing price. By monitoring the percentage"
                    " change in the closing price, investors can gain insights into the "
                    "overall performance of the stock market. This information can help "
                    "investors to make informed decisions about buying or selling stocks.")
        st.markdown("<h5 style = 'color: #964B00;'>COMBINED</h5>", unsafe_allow_html=True)

        fig_all = plot_daily_pct_change(hist)
        st.plotly_chart(fig_all)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_daily_pct_change(hist, all_years=False)
        st.plotly_chart(fig)

    elif plot_type == 'Rolling Average of Closing Price over Time':
        st.markdown("#### Visualising the Rolling Average of Closing Price over Time")
        st.markdown("The rolling average of the closing price over time is a popular technical "
                    "analysis tool used by investors to identify trends in the stock market. "
                    "It is calculated by taking the average closing price of a stock over a "
                    "specific time period, such as 50 or 200 days. By analyzing the rolling "
                    "average of the closing price, investors can gain insights into the overall "
                    "performance of the stock market. This information can help investors to make "
                    "more informed decisions about buying or selling stocks.")
        fig_all = plot_rolling_average(hist)
        st.plotly_chart(fig_all)
        st.markdown("<h5 style = 'color: #964B00;'>YEAR-WISE</h5>", unsafe_allow_html=True)
        fig = plot_rolling_average(hist, all_years=False)
        st.plotly_chart(fig)


    elif plot_type == 'Closing Price vs Volume Traded':
        st.markdown("#### Comparing Closing Price and Volume Traded")
        st.markdown("The relationship between the closing price and the volume traded "
                    "is an important indicator of market sentiment. High trading volume "
                    "with a rising closing price may suggest a bullish market, while low "
                    "trading volume with a falling closing price may suggest a bearish market. "
                    "By analyzing the relationship between the closing price and the volume traded,"
                    " investors can gain insights into the level of investor interest "
                    "in a particular stock. This information can help investors to make more "
                    "informed decisions about buying or selling stocks. ")
        fig = plot_closing_price_vs_volume(hist)
        st.plotly_chart(fig)

    elif plot_type == 'Distribution of Closing Price':
        st.markdown("#### Distribution of Closing Price")
        st.markdown("The distribution of closing price is a graphical "
                    "representation of the frequency of closing prices of a stock. "
                    "By analyzing the distribution of closing price, investors can gain "
                    "insights into the range of closing prices and how often they occur. "
                    "This information can help investors to understand the level of volatility "
                    "of a particular stock. It can also provide insights into the level of investor"
                    " interest in the stock, as well as the overall performance of the stock market.")
        fig = plot_dist_close(hist)
        st.plotly_chart(fig)

    if plot_type == 'Distribution of Volume Traded':
        st.markdown("#### Distribution of Volume traded")
        st.markdown("The distribution of volume traded is a graphical"
                    " representation of the frequency of volume traded for a "
                    "particular stock. By analyzing the distribution of volume traded,"
                    " investors can gain insights into the level of investor interest in "
                    "the stock. This information can help investors to understand the level"
                    " of liquidity of the stock, as well as the overall performance of the "
                    "stock market. It can also provide insights into potential trends and "
                    "patterns in the market, which can inform investment decisions.")
        fig = plot_dist_volume(hist)
        st.plotly_chart(fig)

