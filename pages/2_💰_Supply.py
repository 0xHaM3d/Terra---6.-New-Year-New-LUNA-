# Libraries
import streamlit as st
from shroomdk import ShroomDK
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
sdk = ShroomDK("653fb086-1a65-45b0-aa0c-28333f2d4f31")
from pandas.core.reshape.reshape import unstack

# Global Variables
theme_plotly = None  # None or streamlit

# Layout
st.set_page_config(page_title='Supply', page_icon=':bar_chart:', layout='wide')
st.title('💰 Supply')

st.write("")
st.write("")
st.subheader('LUNA 2.0 Price')

df_query = """ 
with btc as (
  SELECT
  HOUR::DATE as DATE,
symbol,
avg(price) btc_price
FROM ethereum.core.fact_hourly_token_prices
  WHERE symbol in ('WBTC')
  and hour >= '2022-05-28' -- LUNA 2.0 LAUNCH
  group by 1,2
)
  , eth as (
  SELECT
  HOUR::DATE as DATE,
symbol,
avg(price) eth_price
FROM ethereum.core.fact_hourly_token_prices
  WHERE symbol in ('WETH')
  and hour >= '2022-05-28' -- LUNA 2.0 LAUNCH
  group by 1,2
)
, luna as (
  select 
  	block_timestamp::date as date,
	median(to_amount/from_amount) as lunna_price
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and block_timestamp >= '2022-05-28' -- LUNA 2.0 LAUNCH
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
SELECT date, btc_price, eth_price, lunna_price
FROM btc join luna USING(date)
join eth USING(date)
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query)
df = pd.DataFrame(results.records)
df.info()

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('btc_price', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='lunna_price')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily $LUNA2.0 vs $BTC price evolution')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('eth_price', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='lunna_price')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily $LUNA2.0 vs $ETH price evolution')),
                use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Supply Metrics')

df_query2 = """ 
with tb1 as (
  select 
  sum(AMOUNT) as sent, SENDER
from terra.core.ez_transfers
WHERE CURRENCY='uluna'
group by 2
  ),  
tb2 as (
  select 
  sum(AMOUNT) as rec, 
  RECEIVER
from terra.core.ez_transfers
WHERE CURRENCY='uluna'
group by 2
  )
  , total_sup as (
  select 
  sum(rec)/1e4 as total_supply 
from tb2 a left join tb1 b on a.RECEIVER=b.SENDER 
where sent is null
  )
 , tb3 as (
  select 
  	date_trunc('day',BLOCK_TIMESTAMP) as date,
	sum(case when FROM_CURRENCY='uluna' then FROM_AMOUNT/1e6 else null end) as from_amountt,
	sum(case when to_CURRENCY='uluna' then FROM_AMOUNT/1e6 else null end) as to_amountt,
   from_amountt-to_amountt as circulating_volume
from terra.core.ez_swaps
group by date
), 
  cirSupply as (
  select 
  		DATE ,
		sum(circulating_volume) over (order by date) as circulating_supply
  from tb3
  )
select 
  circulating_supply, 
  circulating_supply*100/1043378214 as supply_ratio,
  total_supply
from cirSupply JOIN total_sup
where date='2022-12-11'
AND date <= CURRENT_DATE - 1
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query2)
df = pd.DataFrame(results.records)
df.info()

st.markdown(""" <style> div.css-12w0qpk.e1tzin5v2{
 background-color: #00FFFF;
 border: 2px solid;
 padding: 10px 5px 5px 5px;
 border-radius: 10px;
 color: #000080;
 box-shadow: 10px;
}
div.css-1r6slb0.e1tzin5v2{
 background-color: #00FFFF;
 border: 2px solid; /* #900c3f */
 border-radius: 10px;
 padding: 10px 5px 5px 5px;
 color: navy;
}
div.css-50ug3q.e16fv1kl3{
 font-weight: 900;
} 
</style> """, unsafe_allow_html=True)


c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Circulating Supply**', value=str(df['circulating_supply'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Circulating Supply/Total Supply(%)**', value=str(df['supply_ratio'].map('{:,.2f}'.format).values[0]))

with c3:
    st.metric(label='**Total Supply**', value=str(df['total_supply'].map('{:,.0f}'.format).values[0]))

st.write("")
st.write("")
st.write("")
st.write("")

df_query3 = """ 
with tb1 as (
  select 
  	BLOCK_TIMESTAMP::date as date,
	sum(case when FROM_CURRENCY='uluna' then FROM_AMOUNT/1e6 else null end) as from_amt,
	sum(case when to_CURRENCY='uluna' then FROM_AMOUNT/1e6 else null end) as to_amt,
	from_amt-to_amt as circ_volume  	
from terra.core.ez_swaps
group by date
), 
  tb2 as (
  select 
  	DATE,
	sum(circ_volume) over (order by date) as circulating_supply
  from tb1
  )
select 
  date,
  circulating_supply, 
  round((circulating_supply* 100/1043378214), 2) as supply_ratio  
from tb2 
where date >= '2022-08-11'
and date <= CURRENT_DATE - 1
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query3)
df = pd.DataFrame(results.records)
df.info()
fig = px.area(df, x='date', y='circulating_supply')
fig.update_layout(title_text='Circulating Supply Over Time', showlegend=False)
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.scatter(df, x='date', y='supply_ratio')
fig.update_layout(title_text='Percentage of Circulating Supply/Total Supply Ratio Over Time', showlegend=False)
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Stablecoins Turnover')
st.write("")
st.write("")
df_query4 = """ 
with
t1 as (
select 
  block_timestamp,
  case when currency='ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4' then 'axlUSDC' 
  when currency='ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF' then 'axlUSDT'
  end as stablecoin, 
  case when stablecoin in ('axlUSDC','axlUSDT') then 6 end as decimal,
  amount,
  sender,
  receiver,
  transfer_type,
  tx_id
from terra.core.ez_transfers x
where currency in ('ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4',
  					'ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF') 
and message_type in ('/ibc.applications.transfer.v1.MsgTransfer','/cosmos.bank.v1beta1.MsgMultiSend','/cosmos.bank.v1beta1.MsgSend')
  ),
t2 as (
  SELECT
  	date_Trunc('day',block_timestamp) as timespan,
  	stablecoin,
  	count(distinct tx_id) as transfers_in,
  	count(distinct sender) as users_depositing,
  	sum(amount/pow(10,decimal)) as amount_transferred_in,
  	avg(amount/pow(10,decimal)) as avg_amount_transferred_in,
  	sum(transfers_in) over (partition by stablecoin order by timespan) as "Cumulative Inflow Transfers",
  	sum(amount_transferred_in) over (partition by stablecoin order by timespan) as "Cumulative Inflowed Volume"
  from t1 where transfer_type='IBC_Transfer_In'
  group by 1,2
)
  , t3 as (
  SELECT
  	date_Trunc('day',block_timestamp) as timespan,
  	stablecoin,
  	count(distinct tx_id) as transfers_out,
  	count(distinct sender) as users_sending,
  	sum(amount/pow(10,decimal)) as amount_transferred_out,
  	avg(amount/pow(10,decimal)) as avg_amount_transferred_out,
  	sum(transfers_out) over (partition by stablecoin order by timespan) as "Cumulative Outflow Transfers",
  	sum(amount_transferred_out) over (partition by stablecoin order by timespan) as "Cumulative Outflowed Volume"
  from t1 where transfer_type='IBC_Transfer_Off'
  group by 1,2
)
SELECT
	ifnull(t2.timespan,t3.timespan)::date as date,
	ifnull(t2.stablecoin,t3.stablecoin) as stablecoin,
	ifnull(transfers_in,0) as inflow_transfers,
    ifnull(transfers_out,0)*-1 as outflow_transfers, 
  	inflow_transfers+outflow_transfers as net_transfers,
	ifnull(users_depositing,0) as inflowed_users,
  	ifnull(users_sending,0)*-1 as outflowed_users,
  	inflowed_users+outflowed_users as netflow_users,
	ifnull(amount_transferred_in,0) as inflowed_volume,
  	ifnull(amount_transferred_out,0)*-1 as outflowed_volume,
  	inflowed_volume+outflowed_volume as netflowed_volume,
	ifnull(avg_amount_transferred_in,0) as avg_inflowed_volume,
  	ifnull(avg_amount_transferred_out,0)*-1 as avg_outflowed_volume,
  	avg_inflowed_volume+avg_outflowed_volume as avg_netflowed_volume
from t2
full outer join t3 on t2.timespan=t3.timespan and t2.stablecoin=t3.stablecoin
  where date <= CURRENT_DATE - 1
order by 1 asc,2
"""

df_query5 = """ 
with
t1 as (
select 
  block_timestamp,
  case when currency='ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4' then 'axlUSDC' 
  when currency='ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF' then 'axlUSDT'
  end as stablecoin, 
  case when stablecoin in ('axlUSDC','axlUSDT') then 6 end as decimal,
  amount,
  sender,
  receiver,
  transfer_type,
  tx_id
from terra.core.ez_transfers x
where currency in ('ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4',
  					'ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF') 
and message_type in ('/ibc.applications.transfer.v1.MsgTransfer','/cosmos.bank.v1beta1.MsgMultiSend','/cosmos.bank.v1beta1.MsgSend')
  ),
t2 as (
  SELECT
  	date_Trunc('week',block_timestamp) as timespan,
  	stablecoin,
  	count(distinct tx_id) as transfers_in,
  	count(distinct sender) as users_depositing,
  	sum(amount/pow(10,decimal)) as amount_transferred_in,
  	avg(amount/pow(10,decimal)) as avg_amount_transferred_in,
  	sum(transfers_in) over (partition by stablecoin order by timespan) as "Cumulative Inflow Transfers",
  	sum(amount_transferred_in) over (partition by stablecoin order by timespan) as "Cumulative Inflowed Volume"
  from t1 where transfer_type='IBC_Transfer_In'
  group by 1,2
)
  , t3 as (
  SELECT
  	date_Trunc('week',block_timestamp) as timespan,
  	stablecoin,
  	count(distinct tx_id) as transfers_out,
  	count(distinct sender) as users_sending,
  	sum(amount/pow(10,decimal)) as amount_transferred_out,
  	avg(amount/pow(10,decimal)) as avg_amount_transferred_out,
  	sum(transfers_out) over (partition by stablecoin order by timespan) as "Cumulative Outflow Transfers",
  	sum(amount_transferred_out) over (partition by stablecoin order by timespan) as "Cumulative Outflowed Volume"
  from t1 where transfer_type='IBC_Transfer_Off'
  group by 1,2
)
SELECT
	ifnull(t2.timespan,t3.timespan)::date as date,
	ifnull(t2.stablecoin,t3.stablecoin) as stablecoin,
	ifnull(transfers_in,0) as inflow_transfers,
    ifnull(transfers_out,0)*-1 as outflow_transfers, 
  	inflow_transfers+outflow_transfers as net_transfers,
	ifnull(users_depositing,0) as inflowed_users,
  	ifnull(users_sending,0)*-1 as outflowed_users,
  	inflowed_users+outflowed_users as netflow_users,
	ifnull(amount_transferred_in,0) as inflowed_volume,
  	ifnull(amount_transferred_out,0)*-1 as outflowed_volume,
  	inflowed_volume+outflowed_volume as netflowed_volume,
	ifnull(avg_amount_transferred_in,0) as avg_inflowed_volume,
  	ifnull(avg_amount_transferred_out,0)*-1 as avg_outflowed_volume,
  	avg_inflowed_volume+avg_outflowed_volume as avg_netflowed_volume
from t2
full outer join t3 on t2.timespan=t3.timespan and t2.stablecoin=t3.stablecoin
  where date <= CURRENT_DATE - 1
order by 1 asc,2
"""
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Terra Stablecoins Turnover metrics Over Time(daily & weekly')

st.write("""
         In this first part, we can take a look at the main activity metrics on Inflow/Outflow of Stablecoins on Terra,
         where it can be seen how the number of transactions done across the protocol by hour over the past week
         and by day and week since LUNA2.0 Launch
        """
         )
from plotly.subplots import make_subplots

# Daily
st.subheader('Terra Stablecoins Turnover by day')
st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query4)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['inflow_transfers', 'outflow_transfers'])
    fig.update_layout(title_text='Inflow/Outflow Transfer Txs Count')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.bar(df, x='date', y=['inflowed_users', 'outflowed_users'])
    fig.update_layout(title_text='Inflow/Outflow Transferrer Coun')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['inflowed_volume', 'outflowed_volume'])
    fig.update_layout(title_text='Inflow/Outflow Transferred Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.line(df, x='date', y=['net_transfers', 'netflow_users', 'netflowed_volume'], log_y=True)
    fig.update_layout(title_text='Net Inflow/Outflow Txs, Usres & Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['avg_inflowed_volume', 'avg_outflowed_volume'])
    fig.update_layout(title_text='Average Inflow/Outflow Transferred Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.line(df, x='date', y=['avg_netflowed_volume'])
    fig.update_layout(title_text='Average Net flow Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)



# weekly
st.subheader('Terra Stablecoins Turnover by Week')
st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query5)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['inflow_transfers', 'outflow_transfers'])
    fig.update_layout(title_text='Inflow/Outflow Transfer Txs Count')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.bar(df, x='date', y=['inflowed_users', 'outflowed_users'])
    fig.update_layout(title_text='Inflow/Outflow Transferrer Coun')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['inflowed_volume', 'outflowed_volume'])
    fig.update_layout(title_text='Inflow/Outflow Transferred Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.line(df, x='date', y=['net_transfers', 'netflow_users', 'netflowed_volume'], log_y=True)
    fig.update_layout(title_text='Net Inflow/Outflow Txs, Usres & Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y=['avg_inflowed_volume', 'avg_outflowed_volume'])
    fig.update_layout(title_text='Average Inflow/Outflow Transferred Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.line(df, x='date', y=['avg_netflowed_volume'])
    fig.update_layout(title_text='Average Net flow Volume')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)



df_query6 = """ 
with
t1 as (
select 
  block_timestamp,
  case when currency='ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4' then 'axlUSDC' 
  when currency='ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF' then 'axlUSDT'
  end as stablecoin, 
  case when stablecoin in ('axlUSDC','axlUSDT') then 6 end as decimal,
  amount,
  sender,
  receiver,
  transfer_type,
  tx_id
from terra.core.ez_transfers x
where currency in ('ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4',
  					'ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF') 
and message_type in ('/ibc.applications.transfer.v1.MsgTransfer','/cosmos.bank.v1beta1.MsgMultiSend','/cosmos.bank.v1beta1.MsgSend')
  ),
t2 as (
  SELECT
  	stablecoin,
  	count(distinct block_timestamp::date) as day_in_cnt,
  	count(distinct tx_id) as transfers_in,
  	count(distinct sender) as users_depositing,
  	sum(amount/pow(10,decimal)) as amount_transferred_in
  from t1 
  where transfer_type='IBC_Transfer_In'
  and block_timestamp::date <= CURRENT_DATE - 1
  group by 1
)
  , t3 as (
  SELECT
  	stablecoin,  	
  	count(distinct block_timestamp::date) as day_out_cnt,
  	count(distinct tx_id) as transfers_out,
  	count(distinct sender) as users_sending,
  	sum(amount/pow(10,decimal)) as amount_transferred_out
  from t1 
  where transfer_type='IBC_Transfer_Off'
  and block_timestamp::date <= CURRENT_DATE - 1
  group by 1
)
  , t4 as (
  SELECT
  		stablecoin,
  		avg(transfers_in/day_in_cnt) as avg_tx_int_per_day,
  		avg(users_depositing/day_in_cnt) as avg_users_depositing_per_day,
  		avg(amount_transferred_in/day_in_cnt) as avg_volume_in_per_day,
  		avg(amount_transferred_in/transfers_in) as avg_volume_in_per_tx,
  		avg(amount_transferred_in/users_depositing) as avg_volume_in_per_user
  FROM t2
  GROUP by 1
  )
  , t5 as (
  SELECT
  		stablecoin,
  		avg(transfers_out/day_out_cnt) as avg_tx_out_per_day,
  		avg(users_sending/day_out_cnt) as avg_users_sending_out_per_day,
  		avg(amount_transferred_out/day_out_cnt) as avg_volume_out_per_day,
  		avg(amount_transferred_out/transfers_out) as avg_volume_out_per_tx,
  		avg(amount_transferred_out/users_sending) as avg_volume_out_per_user
  FROM t3
  GROUP by 1
  )
SELECT
	ifnull(t4.stablecoin,t5.stablecoin) as stablecoin,
	ifnull(avg_tx_int_per_day,0) as ave_inflow_transfers,
    ifnull(avg_tx_out_per_day,0) as avg_outflow_transfers, 
  	ave_inflow_transfers - avg_outflow_transfers as avg_net_transfers,
	ifnull(avg_users_depositing_per_day,0) as avg_inflowed_users,
  	ifnull(avg_users_sending_out_per_day,0) as avg_outflowed_users,
  	avg_inflowed_users- avg_outflowed_users as avg_netflow_users,
	ifnull(avg_volume_in_per_day,0) as avg_inflowed_volume,
  	ifnull(avg_volume_out_per_day,0) as avg_outflowed_volume,
  	avg_inflowed_volume - avg_outflowed_volume as avg_netflowed_volume,
	ifnull(avg_volume_in_per_tx,0) as avg_inflowed_volume_per_tx,
  	ifnull(avg_volume_out_per_tx,0) as avg_outflowed_volume_per_tx,
  	avg_inflowed_volume_per_tx - avg_outflowed_volume_per_tx as avg_netflowed_volume_per_tx,
	ifnull(avg_volume_in_per_user,0) as avg_inflowed_volume_per_user,
  	ifnull(avg_volume_out_per_user,0) as avg_outflowed_volume_per_user,
  	avg_inflowed_volume_per_user - avg_outflowed_volume_per_user as avg_netflowed_volume_per_user
from t4
full outer join t5 on t4.stablecoin=t5.stablecoin
order by 1 asc,2
"""
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Terra Stablecoins Turnover metrics in Daily Average')
st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query6)
df = pd.DataFrame(results.records)
df.info()
st.dataframe(df, use_container_width=True)


df_query7 = """ 
with
t1 as (
select 
  block_timestamp,
  case when currency='ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4' then 'axlUSDC' 
  when currency='ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF' then 'axlUSDT'
  end as stablecoin, 
  case when stablecoin in ('axlUSDC','axlUSDT') then 6 end as decimal,
  amount,
  sender,
  receiver,
  transfer_type,
  tx_id
from terra.core.ez_transfers x
where currency in ('ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4',
  					'ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF') 
and message_type in ('/ibc.applications.transfer.v1.MsgTransfer','/cosmos.bank.v1beta1.MsgMultiSend','/cosmos.bank.v1beta1.MsgSend')
  ),
t2 as (
  SELECT
  	stablecoin,
  	count(distinct date_trunc('week', block_timestamp)::date) as week_in_cnt,
  	count(distinct tx_id) as transfers_in,
  	count(distinct sender) as users_depositing,
  	sum(amount/pow(10,decimal)) as amount_transferred_in
  from t1 
  where transfer_type='IBC_Transfer_In'
  and block_timestamp::date <= CURRENT_DATE - 1
  group by 1
)
  , t3 as (
  SELECT
  	stablecoin,  	
  	count(distinct date_trunc('week', block_timestamp)::date) as week_out_cnt,
  	count(distinct tx_id) as transfers_out,
  	count(distinct sender) as users_sending,
  	sum(amount/pow(10,decimal)) as amount_transferred_out
  from t1 
  where transfer_type='IBC_Transfer_Off'
  and block_timestamp::date <= CURRENT_DATE - 1
  group by 1
)
  , t4 as (
  SELECT
  		stablecoin,
  		avg(transfers_in/week_in_cnt) as avg_tx_int_per_week,
  		avg(users_depositing/week_in_cnt) as avg_users_depositing_per_week,
  		avg(amount_transferred_in/week_in_cnt) as avg_volume_in_per_week,
  		avg(amount_transferred_in/transfers_in) as avg_volume_in_per_tx,
  		avg(amount_transferred_in/users_depositing) as avg_volume_in_per_user
  FROM t2
  GROUP by 1
  )
  , t5 as (
  SELECT
  		stablecoin,
  		avg(transfers_out/week_out_cnt) as avg_tx_out_per_week,
  		avg(users_sending/week_out_cnt) as avg_users_sending_out_per_week,
  		avg(amount_transferred_out/week_out_cnt) as avg_volume_out_per_week,
  		avg(amount_transferred_out/transfers_out) as avg_volume_out_per_tx,
  		avg(amount_transferred_out/users_sending) as avg_volume_out_per_user
  FROM t3
  GROUP by 1
  )
SELECT
	ifnull(t4.stablecoin,t5.stablecoin) as stablecoin,
	ifnull(avg_tx_int_per_week,0) as ave_inflow_transfers,
    ifnull(avg_tx_out_per_week,0) as avg_outflow_transfers, 
  	ave_inflow_transfers - avg_outflow_transfers as avg_net_transfers,
	ifnull(avg_users_depositing_per_week,0) as avg_inflowed_users,
  	ifnull(avg_users_sending_out_per_week,0) as avg_outflowed_users,
  	avg_inflowed_users- avg_outflowed_users as avg_netflow_users,
	ifnull(avg_volume_in_per_week,0) as avg_inflowed_volume,
  	ifnull(avg_volume_out_per_week,0) as avg_outflowed_volume,
  	avg_inflowed_volume - avg_outflowed_volume as avg_netflowed_volume,
	ifnull(avg_volume_in_per_tx,0) as avg_inflowed_volume_per_tx,
  	ifnull(avg_volume_out_per_tx,0) as avg_outflowed_volume_per_tx,
  	avg_inflowed_volume_per_tx - avg_outflowed_volume_per_tx as avg_netflowed_volume_per_tx,
	ifnull(avg_volume_in_per_user,0) as avg_inflowed_volume_per_user,
  	ifnull(avg_volume_out_per_user,0) as avg_outflowed_volume_per_user,
  	avg_inflowed_volume_per_user - avg_outflowed_volume_per_user as avg_netflowed_volume_per_user
from t4
full outer join t5 on t4.stablecoin=t5.stablecoin
order by 1 asc,2
"""
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Terra Stablecoins Turnover metrics in Weekly Average')
st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query7)
df = pd.DataFrame(results.records)
df.info()
st.dataframe(df, use_container_width=True)


