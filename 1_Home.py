from pymongo import MongoClient
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
from footer import footer

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["finance"]
collection = db["tickers_meta_ref"]

#Setting basic page configuration
st.set_page_config(
    page_title="STONKS RABBI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

#Title and sidebar configuration
st.title("STONKS RABBI - A Market Analyser & Forecaster")
st.sidebar.success("Select a page above.")

#Function to get dropdown options
@st.cache_data
def get_options():
    # Find all names and symbols in the collection
    name_options = []
    symbol_options = []
    for doc in collection.find({}, {'Name': 1, 'Symbol': 1}):
        name_options.append(doc['Name'])
        symbol_options.append(doc['Symbol'])

    return name_options, symbol_options


# Importing data from yfinance and returning the pandas datafrane
@st.cache_data
def load_data(symbol):
    # Query the ticker data using yfinance
    ticker_data = yf.download(symbol, period='max', progress=False)

    # Filter for the required columns
    ticker_data = ticker_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

    return ticker_data

# Get options for dropdown menu
name_options, symbol_options = get_options()


# Option Selectbox (1) --> Company Listed Name
name_option_sb = st.selectbox('**COMPANY LISTING NAME**', name_options, key='selected_name_1',)

# Option Selectbox (2) (Auto-Filled) --> Company Listed Symbol
data_symbol = [data['Symbol'] for data in collection.find({'Name': name_option_sb}, {'Symbol': 1})]
symbol_option_sb = st.selectbox('**COMPANY LISTING SYMBOL**', data_symbol, key='selected_name_2', disabled=True)

# On clicking Analyse Button
if st.button('Analyse'):
    #Saving name and symbol into the session
    st.session_state['name_option_sb'] = name_option_sb
    st.session_state['data_symbol'] = data_symbol
    
    #Wait fileter (spiiner) till API returns data 
    with st.spinner("Fetching Stonkkkss..."):
        image = Image.open('/Users/shreyansh/Documents/Stonks Rabbi - Market Analyser and Predictor/stonks_cover.jpg')
        st.image(image,width=450)
        hist = load_data(data_symbol)
        st.session_state['data'] = hist # loading data into session state so that it can be used ahead.
    
    #Confirmation and re-route suggestion message
    st.write("**Chose Options From the Sidebar!**")
    

footer()
