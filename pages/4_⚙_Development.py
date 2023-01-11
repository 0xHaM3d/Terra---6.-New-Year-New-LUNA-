# Libraries
import streamlit as st
from shroomdk import ShroomDK
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
sdk = ShroomDK("653fb086-1a65-45b0-aa0c-28333f2d4f31")

# Global Variables
theme_plotly = None  # None or streamlit

# Layout
st.set_page_config(page_title='Development', page_icon=':bar_chart:', layout='wide')
st.title('⚙ Development')

st.write("")
st.write("")
st.write(
    """
    **Overview** 
    Growth and success in the blockchain industry are often measured by how quickly the ecosystem grows and how many 
    new features are added. Here you can see a snapshot of all the contracts that have been deployed and are actively 
    being used on the Terra blockchain. The provided charts show how the total number of current contracts and the 
    total number of newly deployed contracts have evolved over time.

    Adoption by users, or the number of people who start using a blockchain project, is also crucial to its development
    and expansion. The dashboard also tracks the number of new users and identifies the contracts/protocols through 
    which they are recruited by showing which contracts are most frequently used by new users.

    This dashboard also displays daily data on the most popular contracts according to the number of users and the
    number of transactions, further segmented by new and returning users.
    """
)
st.write("")
st.write("")
st.write("")
st.write("")

st.subheader('Active Contracts, Daily & Total New Deployed Contracts Over Time')


df_query1 = """ 
with first_date_contract as (
select 
  tx:body:messages[0]:contract as contract,
  min(block_timestamp) as min_date
  from terra.core.fact_transactions 
  group by 1
)
  , new_contract as (
  SELECT
date_Trunc('day',min_date) as date,
count(distinct contract) as new_contract_cnt,
sum(new_contract_cnt) over (order by date) as cum_new_contract_cnt
from first_date_contract 
where min_date::date <= CURRENT_DATE - 1
group by 1
order by 1 asc
  
  )
, active as (
  SELECT
date_Trunc('day',block_timestamp)::date as date,
case when block_timestamp>='2023-01-01' then '2023' else '2022' end as period,
count(distinct tx:body:messages[0]:contract) as activ_contract_cnt
from terra.core.fact_transactions  
where block_timestamp::date <= CURRENT_DATE - 1
group by 1, 2
)
SELECT
  	date,
  	period,
  	activ_contract_cnt,
  	new_contract_cnt,
  	cum_new_contract_cnt
FROM new_contract JOIN active USING(date)
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query1)
df = pd.DataFrame(results.records)
df.info()

fig = px.bar(df, x='date', y='activ_contract_cnt', color='period')
fig.update_layout(title_text='Daily # of Active Contracts')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='new_contract_cnt', color='period')
fig.update_layout(title_text='Daily # of New Deployed Contracts')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.area(df, x='date', y='cum_new_contract_cnt')
fig.update_layout(title_text='Total # of New Deployed Contracts Over Time')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.area(df, x='date', y=['activ_contract_cnt', 'new_contract_cnt'])
fig.update_layout(title_text='Daily # of Active vs. New Deployed Contracts')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)



st.write("")
st.write("")
st.write("")

st.write(
    """
    **Top 10 Active Contract by the Most Traffic** 
    The following visuals show the top 10 active contracts based on the most traffic (transactions count and users count)
    in 2022 and 2023.
    """
)

st.subheader('Top 10 Deployed Contract by the Most Trafic in **:blue[2022]**')

df_query2 = """ 
with first_date_contract as (
select 
  	tx:body:messages[0]:contract as new_dep_contracts,
  	min(block_timestamp) as min_date,
  	count(distinct tx_id) as transactions,
  	count(distinct tx_sender) as users
from terra.core.dim_address_labels join terra.core.fact_transactions on address=tx:body:messages[0]:contract
group by 1
  )
select 
  project_name,
  count(distinct tx_id) as tx_cnt,
  count(distinct tx_sender) as usr_cnt
from terra.core.dim_address_labels join terra.core.fact_transactions on address = tx:body:messages[0]:contract
WHERE tx:body:messages[0]:contract in (SELECT new_dep_contracts from first_date_contract)
AND block_timestamp::date <= '2022-12-31'
group by 1
order by 2 DESC
limit 10
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query2)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='project_name', y=['tx_cnt', 'usr_cnt'])
    fig.update_layout(title_text='Daily # of Txs & Usres by Contracts')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.pie(df, values='tx_cnt', names='project_name', title='Total # & % of Txs by Contracts')
    fig.update_layout(legend_title='Contracts', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")

st.subheader('Top 10 Deployed Contract by the Most Trafic in **:blue[2023]**')

df_query3 = """ 
with first_date_contract as (
select 
  	tx:body:messages[0]:contract as new_dep_contracts,
  	min(block_timestamp) as min_date,
  	count(distinct tx_id) as transactions,
  	count(distinct tx_sender) as users
from terra.core.dim_address_labels join terra.core.fact_transactions on address=tx:body:messages[0]:contract
group by 1
  )
select 
  project_name,
  count(distinct tx_id) as tx_cnt,
  count(distinct tx_sender) as usr_cnt
from terra.core.dim_address_labels join terra.core.fact_transactions on address = tx:body:messages[0]:contract
WHERE tx:body:messages[0]:contract in (SELECT new_dep_contracts from first_date_contract)
AND block_timestamp::date >= '2023-01-01'
AND block_timestamp::date <= CURRENT_DATE - 1
group by 1
order by 2 DESC
limit 10
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query3)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='project_name', y=['tx_cnt', 'usr_cnt'])
    fig.update_layout(title_text='Daily # of Txs & Usres by Contracts')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.pie(df, values='tx_cnt', names='project_name', title='Total # & % of Txs by Contracts')
    fig.update_layout(legend_title='Contracts', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")

st.subheader('Distribution of Deployed Contracts Type by User & Txs Count in **:blue[2022]**')

st.write("")
st.write("")
df_query4 = """ 
with first_date_contract as (
select 
  	tx:body:messages[0]:contract as new_dep_contracts,
  	min(block_timestamp) as min_date,
  	count(distinct tx_id) as transactions,
  	count(distinct tx_sender) as users
from terra.core.dim_address_labels join terra.core.fact_transactions on address=tx:body:messages[0]:contract
group by 1
  )
select 
  label_type,
  count(distinct tx_id) as tx_cnt,
  count(distinct tx_sender) as usr_cnt
from terra.core.dim_address_labels join terra.core.fact_transactions on address = tx:body:messages[0]:contract
WHERE tx:body:messages[0]:contract in (SELECT new_dep_contracts from first_date_contract)
AND block_timestamp::date <= '2022-12-31'
group by 1
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query4)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='tx_cnt', names='label_type', title='Distribution of Deployed Contracts Type by Txs Count')
    fig.update_layout(legend_title='Contracts Type', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.pie(df, values='usr_cnt', names='label_type', title='Distribution of Deployed Contracts Type by User Count')
    fig.update_layout(legend_title='Contracts Type', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='label_type', y=['tx_cnt'])
    fig.update_layout(title_text='Total # of Txs by Contracts Type')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.bar(df, x='label_type', y=['usr_cnt'])
    fig.update_layout(title_text='Total # of Users by Contracts Type')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")

st.subheader('Distribution of Deployed Contracts Type by User & Txs Count in **:blue[2023]**')

st.write("")
st.write("")
df_query5 = """ 
with first_date_contract as (
select 
  	tx:body:messages[0]:contract as new_dep_contracts,
  	min(block_timestamp) as min_date,
  	count(distinct tx_id) as transactions,
  	count(distinct tx_sender) as users
from terra.core.dim_address_labels join terra.core.fact_transactions on address=tx:body:messages[0]:contract
group by 1
  )
select 
  label_type,
  count(distinct tx_id) as tx_cnt,
  count(distinct tx_sender) as usr_cnt
from terra.core.dim_address_labels join terra.core.fact_transactions on address = tx:body:messages[0]:contract
WHERE tx:body:messages[0]:contract in (SELECT new_dep_contracts from first_date_contract)
AND block_timestamp::date >= '2023-01-01'
AND block_timestamp::date <= CURRENT_DATE - 1
group by 1
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query5)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='tx_cnt', names='label_type', title='Distribution of Deployed Contracts Type by Txs Count')
    fig.update_layout(legend_title='Contracts Type', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.pie(df, values='usr_cnt', names='label_type', title='Distribution of Deployed Contracts Type by User Count')
    fig.update_layout(legend_title='Contracts Type', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='label_type', y=['tx_cnt'])
    fig.update_layout(title_text='Total # of Txs by Contracts Type')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.bar(df, x='label_type', y=['usr_cnt'])
    fig.update_layout(title_text='Total # of Users by Contracts Type')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

