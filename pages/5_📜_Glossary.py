# Libraries
import streamlit as st

# [theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

# Layout
st.set_page_config(page_title='Definitions & Data Transparency', page_icon=':bar_chart:', layout='wide')
st.write("### 📜 Definitions & Data Transparency")

st.write("")
st.write("")
st.write("")
st.write("")

st.write(
    """
    The main data source is [**Flipside Crypto**](https://flipsidecrypto.xyz/). They offer free access to blockchain 
    data across a variety of different blockchains. 
    The SQL queries to extract the data to display are written by me and are automatically updated every
    24 hours by SDK. They all are open-sourced and feel free to reach out if you need access to anything in
    particular. 
    """
)
st.write(
    """
    #### How are daily transactions counted?    
    To calculate daily transactions on Terra LUNA2.0 (as well as other chains transactions), 
    all transactions that interact with on protocols are included. 

    The users that have had as the first transactions called as **New Users**.
    All addresses that execute a transaction interacting on Terra LUNA2.0s' ecosystem
    for the first time have been counted as **New Users** number.

    #### Popularity assessed by:
    The volume of active users on Terra Luna2.0 per day 
    The adoption by new users per day

    #### How is the users growth(Cumulative) calculated?    
    On a given day, all addresses that execute a transaction interacting for the first time have been counted 
    towards the daily New Users number. 
    The cumulative curve is simply a progressive sum of the new daily users.  

    #### Performance assessed by:
    The success rate of transactions in the Optimism
    The average STPM(Succeed Transactions per Minute) per week
    The average FTR(Failed Transactions Rate) per week
    The average transactions fee($)

    #### Circulating Supply
    The amount of coins that are circulating in the market and are tradeable by the public. 
    It is comparable to looking at shares readily available in the market (not held & locked by insiders, governments).

    #### Total Supply
    The amount of coins that have already been created, minus any coins that have been burned (removed from circulation).
    It is comparable to outstanding shares in the stock market.
    Total Supply = Onchain supply - burned tokens [1](https://www.coingecko.com/en/coins/terra)
    """

)

st.write("")
st.write("")
st.write("")
st.write("")

st.write("")
st.write("")
st.write("")
st.write("")

fig = st.write(
    """
                     ### Made with :red[❤] & Honor
    """
)