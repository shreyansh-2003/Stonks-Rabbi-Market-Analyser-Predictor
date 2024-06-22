# Stonks-Rabbi-Market-Analyser-Predictor

**Website Link:** https://stonks-rabbi.streamlit.app/

Stonks Rabbi is a streamlit-based application that uses the Yahoo Finance API to visualize and analyze stock trends, patterns, and performance over its listed time period. The metadata is handled through pymongo, the frontend is on streamlit, and autoARIMA, pandas, and matplotlib are used for data analytics and visualization. 

## Home Page

The home page, as demonstrated in the video below, features a dropdown menu of Nasdaq stock exchange stocks and portfolios available for selection.

https://github.com/shreyansh-2003/Stonks-Rabbi-Stock-Trends-Analyzer/assets/105413094/9139c6cf-aacd-4c10-869c-e1f72bd419e0

## Company Overview Page

#### Metaadata

The first section of the **Company Overview** page contains essential metadata about the company. It includes a dropdown menu to select various parameters such as address, phone number, 52-week change, audit risk, current ratio, and more. Additionally, this section presents a dataset queried from the Yahoo Finance API, which comprises the Open, High, Low, Close, and Volume data for all recorded days since the stock's inception. This dataset can be directly downloaded by clicking the ```Download Data As CSV``` button.

![CO-1](https://github.com/shreyansh-2003/Stonks-Rabbi-Stock-Trends-Analyzer/assets/105413094/92b957e9-d28a-4e05-b3a1-0b27ac2aca20)



