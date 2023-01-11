# Libraries
import streamlit as st
from shroomdk import ShroomDK
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np
sdk = ShroomDK("653fb086-1a65-45b0-aa0c-28333f2d4f31")

# Global Variables
theme_plotly = None  # None or streamlit
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Layout
st.set_page_config(page_title='Activiy', page_icon=':bar_chart:', layout='wide')
st.title('🔥 Activity')

st.markdown("""
            One of the most crucial aspects of the crypto industry is the **activity** of a blockchain network.
            Because it serves as an indicator of a project's potential for success and because it provides a number 
            of helpful metrics regarding the development of the network and its utilization.
            """)


st.markdown('In the current app, I tried to track the basic metrics registered on **Terra Ecosystem** so far such as:')
st.write('')
st.write('**_Transactions_**')
st.write('- Total & average Transaction per day & week')
st.write('- Total & average Transaction Fee per day & week')
st.write('- Average Transaction per active & new users')
st.write('- Total new user per day & week')
st.write('- Succeed & Failed transactions rate by week')
st.write('')
st.write('**_Wallets_**')
st.write('- Total number of new wallets per week')
st.write('- Total number of active wallets per week')
st.write('- Cumulative number of new wallets over time by week')
st.write('- Whales activities per day & week')

st.write("")
st.write("")


df_query1 = """ 
with LUNA2_price as (
  select 
  	block_timestamp,
	median(to_amount/from_amount) as USD_Price
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tb1 as (
  SELECT
  	t.block_timestamp,
  	tx_id,
  	TX_SENDER,
  	fee,
  	(fee * USD_Price) AS fee_usd	
FROM terra.core.fact_transactions t
JOIN LUNA2_price p ON t.block_timestamp = p.block_timestamp
WHERE t.block_timestamp::date >= '2022-05-28' 
AND t.block_timestamp::date <= '2022-12-31'
  )
  , lstTb as (
  SELECT
	COUNT(DISTINCT date_trunc('day', block_timestamp)::date) AS day_cnt,
	COUNT(DISTINCT tx_id) AS tx_cnt,
  	COUNT(DISTINCT TX_SENDER) AS user_cnt,
  	SUM(fee) AS fee_luna, 
  	SUM(fee_usd) AS fee_usd
FROM tb1
  )
SELECT 
	avg(tx_cnt/day_cnt) as avg_tx_per_day,
	avg(user_cnt/day_cnt) as avg_usr_per_day,
	avg(fee_usd/day_cnt) as avg_fee_usd_per_day,
	avg(fee_luna/day_cnt) as avg_fee_luna_per_day,
	avg(fee_usd/tx_cnt) as avg_fee_usd_per_tx,
	avg(fee_usd/user_cnt) as avg_fee_usd_per_usr
FROM lstTb
"""

st.write("")
st.write("")
st.subheader('Daily Average Transactions Metrics in **:red[2022]**')

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query1)
df = pd.DataFrame(results.records)
df.info()

st.markdown(""" <style> div.css-12w0qpk.e1tzin5v2{
 background-color: 	#7fffd4;
 border: 2px solid;
 padding: 10px 5px 5px 5px;
 border-radius: 10px;
 color: #00008b;
 box-shadow: 10px;
}
div.css-1r6slb0.e1tzin5v2{
 background-color: 	#7fffd4;
 border: 2px solid; /* #900c3f */
 border-radius: 10px;
 padding: 10px 5px 5px 5px;
 color: darkblue;
}
div.css-50ug3q.e16fv1kl3{
 font-weight: 900;
} 
</style> """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Txs per Day**', value=str(df['avg_tx_per_day'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average User per Day**', value=str(df['avg_usr_per_day'].map('{:,.0f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per Day**',
              value=str(df['avg_fee_usd_per_day'].map('{:,.0f}'.format).values[0]))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Spent Fees(LUNA2.0) per Day**', value=str(df['avg_fee_luna_per_day'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average Spent Fees($) per Tx**', value=str(df['avg_fee_usd_per_tx'].map('{:,.2f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per User**', value=str(df['avg_fee_usd_per_usr'].map('{:,.2f}'.format).values[0]))

df_query2 = """ 
with LUNA2_price as (
  select 
  	block_timestamp,
	median(to_amount/from_amount) as USD_Price
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tb1 as (
  SELECT
  	t.block_timestamp,
  	tx_id,
  	TX_SENDER,
  	fee,
  	(fee * USD_Price) AS fee_usd	
FROM terra.core.fact_transactions t
JOIN LUNA2_price p ON t.block_timestamp = p.block_timestamp
WHERE t.block_timestamp::date >= '2023-01-01' 
AND t.block_timestamp::date <= CURRENT_DATE - 1
  )
  , lstTb as (
  SELECT
	COUNT(DISTINCT date_trunc('day', block_timestamp)::date) AS day_cnt,
	COUNT(DISTINCT tx_id) AS tx_cnt,
  	COUNT(DISTINCT TX_SENDER) AS user_cnt,
  	SUM(fee) AS fee_luna, 
  	SUM(fee_usd) AS fee_usd
FROM tb1
  )
SELECT 
	avg(tx_cnt/day_cnt) as avg_tx_per_day,
	avg(user_cnt/day_cnt) as avg_usr_per_day,
	avg(fee_usd/day_cnt) as avg_fee_usd_per_day,
	avg(fee_luna/day_cnt) as avg_fee_luna_per_day,
	avg(fee_usd/tx_cnt) as avg_fee_usd_per_tx,
	avg(fee_usd/user_cnt) as avg_fee_usd_per_usr
FROM lstTb
"""

st.write("")
st.write("")
st.subheader('Daily Average Transactions Metrics in **:red[2023]**')

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
    st.metric(label='**Average Txs per Day**', value=str(df['avg_tx_per_day'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average User per Day**', value=str(df['avg_usr_per_day'].map('{:,.0f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per Day**',
              value=str(df['avg_fee_usd_per_day'].map('{:,.0f}'.format).values[0]))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Spent Fees(LUNA2.0) per Day**', value=str(df['avg_fee_luna_per_day'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average Spent Fees($) per Tx**', value=str(df['avg_fee_usd_per_tx'].map('{:,.2f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per User**', value=str(df['avg_fee_usd_per_usr'].map('{:,.2f}'.format).values[0]))

st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Transaction Metrics Over Time by Day')

df_query3 = """ 
with LUNA2_price as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as USDPrice
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
SELECT 
    block_timestamp::date as date,
  	case when block_timestamp>='2023-01-01' then '2023' else '2022' end as period,
	count(distinct tx_id) as tx_cnt,
    sum(tx_cnt) over (order by date) as cum_tx_cnt,
    avg(tx_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_day_tx,
    avg(tx_cnt) over (order by date, date rows between 14 preceding and current row) as ma15_day_tx,
    avg(tx_cnt) over (order by date, date rows between 29 preceding and current row) as ma30_day_tx,
	count(distinct TX_SENDER) as usr_cnt,
    avg(usr_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_day_usr,
    avg(usr_cnt) over (order by date, date rows between 14 preceding and current row) as ma15_day_usr,
    avg(usr_cnt) over (order by date, date rows between 29 preceding and current row) as ma30_day_usr,
	sum(FEE) as tx_fee_luna,
    sum(tx_fee_luna) over (order by date) as cum_tx_fee_luna,
  	avg(tx_fee_luna) over (order by date, date rows between 6 preceding and current row) as ma7_day_fee_luna,
    avg(tx_fee_luna) over (order by date, date rows between 14 preceding and current row) as ma15_day_fee_luna,
    avg(tx_fee_luna) over (order by date, date rows between 29 preceding and current row) as ma30_day_fee_luna,
	sum(FEE*USDPrice) as tx_fee_usd,
    sum(tx_fee_usd) over (order by date) as cum_tx_fee_usd,
  	avg(tx_fee_usd) over (order by date, date rows between 6 preceding and current row) as ma7_day_fee_usd,
    avg(tx_fee_usd) over (order by date, date rows between 14 preceding and current row) as ma15_day_fee_usd,
    avg(tx_fee_usd) over (order by date, date rows between 29 preceding and current row) as ma30_day_fee_usd,
  	avg(CASE WHEN tx_succeeded = true THEN 1 ELSE 0 END) as avg_succeed_tx_cnt,
	avg(CASE WHEN tx_succeeded != true THEN 1 ELSE 0 END) as avg_failed_tx_cnt,
	100*avg_succeed_tx_cnt/(tx_cnt) as avg_success_rate,
	100*avg_failed_tx_cnt/(tx_cnt) as avg_failed_rate
FROM terra.core.fact_transactions t JOIN LUNA2_price p on t.block_timestamp::date = p.p_date
WHERE block_timestamp > '2022-05-28' -- LUNA 2.0 LAUNCH
AND block_timestamp <= CURRENT_DATE - 1
group by 1,2
order by 1
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query3)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='tx_cnt', color='period')
fig.update_layout(title_text='Transaction Traffic per day')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='usr_cnt', color='period')
fig.update_layout(title_text='User Traffic per day')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('tx_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='tx_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('ma7_day_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='ma7_day_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='MA7-D Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Average Success & Failed Txs Conut')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Average Success & Failed Txs Rate')),
                use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.subheader('Network Performance Overall View')


df_query4 = """ 
with LUNA2_price as (
  select 
  	block_timestamp,
	median(to_amount/from_amount) as USD_Price
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tb1 as (
  SELECT
  	t.block_timestamp,
  	tx_id,
  	TX_SENDER,
  	fee,
  	(fee * USD_Price) AS fee_usd	
FROM terra.core.fact_transactions t
JOIN LUNA2_price p ON t.block_timestamp = p.block_timestamp
WHERE t.block_timestamp::date >= '2022-05-28' 
AND t.block_timestamp::date <= '2022-12-31'
  )
  , lstTb as (
  SELECT
	COUNT(DISTINCT date_trunc('week', block_timestamp)::date) AS week_cnt,
	COUNT(DISTINCT tx_id) AS tx_cnt,
  	COUNT(DISTINCT TX_SENDER) AS user_cnt,
  	SUM(fee) AS fee_luna, 
  	SUM(fee_usd) AS fee_usd
FROM tb1
  )
SELECT 
	avg(tx_cnt/week_cnt) as avg_tx_per_week,
	avg(user_cnt/week_cnt) as avg_usr_per_week,
	avg(fee_usd/week_cnt) as avg_fee_usd_per_week,
	avg(fee_luna/week_cnt) as avg_fee_luna_per_week,
	avg(fee_usd/tx_cnt) as avg_fee_usd_per_tx,
	avg(fee_usd/user_cnt) as avg_fee_usd_per_usr
FROM lstTb
"""

st.write("")
st.write("")
st.subheader('Weekly Average Transactions Metrics in **:red[2022]**')

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query4)
df = pd.DataFrame(results.records)
df.info()

st.markdown(""" <style> div.css-12w0qpk.e1tzin5v2{
 background-color: #ff8c00;
 border: 2px solid;
 padding: 10px 5px 5px 5px;
 border-radius: 10px;
 color: #8b0000;
 box-shadow: 10px;
}
div.css-1r6slb0.e1tzin5v2{
 background-color: #ff8c00;
 border: 2px solid; /* #900c3f */
 border-radius: 10px;
 padding: 10px 5px 5px 5px;
 color: darkred;
}
div.css-50ug3q.e16fv1kl3{
 font-weight: 900;
} 
</style> """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Txs per Week**', value=str(df['avg_tx_per_week'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average User per Week**', value=str(df['avg_usr_per_week'].map('{:,.0f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per Week**',
              value=str(df['avg_fee_usd_per_week'].map('{:,.0f}'.format).values[0]))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Spent Fees(LUNA2.0) per Week**', value=str(df['avg_fee_luna_per_week'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average Spent Fees($) per Tx**', value=str(df['avg_fee_usd_per_tx'].map('{:,.2f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per User**', value=str(df['avg_fee_usd_per_usr'].map('{:,.2f}'.format).values[0]))

df_query5 = """ 
with LUNA2_price as (
  select 
  	block_timestamp,
	median(to_amount/from_amount) as USD_Price
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tb1 as (
  SELECT
  	t.block_timestamp,
  	tx_id,
  	TX_SENDER,
  	fee,
  	(fee * USD_Price) AS fee_usd	
FROM terra.core.fact_transactions t
JOIN LUNA2_price p ON t.block_timestamp = p.block_timestamp
WHERE t.block_timestamp::date >= '2022-12-31' 
AND t.block_timestamp::date <= current_date - 1
  )
  , lstTb as (
  SELECT
	COUNT(DISTINCT date_trunc('week', block_timestamp)::date) AS week_cnt,
	COUNT(DISTINCT tx_id) AS tx_cnt,
  	COUNT(DISTINCT TX_SENDER) AS user_cnt,
  	SUM(fee) AS fee_luna, 
  	SUM(fee_usd) AS fee_usd
FROM tb1
  )
SELECT 
	avg(tx_cnt/week_cnt) as avg_tx_per_week,
	avg(user_cnt/week_cnt) as avg_usr_per_week,
	avg(fee_usd/week_cnt) as avg_fee_usd_per_week,
	avg(fee_luna/week_cnt) as avg_fee_luna_per_week,
	avg(fee_usd/tx_cnt) as avg_fee_usd_per_tx,
	avg(fee_usd/user_cnt) as avg_fee_usd_per_usr
FROM lstTb
"""

st.write("")
st.write("")
st.subheader('Weekly Average Transactions Metrics in **:red[2023]**')

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query5)
df = pd.DataFrame(results.records)
df.info()

st.markdown(""" <style> div.css-12w0qpk.e1tzin5v2{
 background-color: #ff8c00;
 border: 2px solid;
 padding: 10px 5px 5px 5px;
 border-radius: 10px;
 color: #8b0000;
 box-shadow: 10px;
}
div.css-1r6slb0.e1tzin5v2{
 background-color: #ff8c00;
 border: 2px solid; /* #900c3f */
 border-radius: 10px;
 padding: 10px 5px 5px 5px;
 color: darkred;
}
div.css-50ug3q.e16fv1kl3{
 font-weight: 900;
} 
</style> """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Txs per Week**', value=str(df['avg_tx_per_week'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average User per Week**', value=str(df['avg_usr_per_week'].map('{:,.0f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per Week**',
              value=str(df['avg_fee_usd_per_week'].map('{:,.0f}'.format).values[0]))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Average Spent Fees(LUNA2.0) per Week**', value=str(df['avg_fee_luna_per_week'].map('{:,.0f}'.format).values[0]))

with c2:
    st.metric(label='**Average Spent Fees($) per Tx**', value=str(df['avg_fee_usd_per_tx'].map('{:,.2f}'.format).values[0]))

with c3:
    st.metric(label='**Average Spent Fees($) per User**', value=str(df['avg_fee_usd_per_usr'].map('{:,.2f}'.format).values[0]))

st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Transaction Metrics Over Time by **:red[Day]**')

df_query6 = """ 
with LUNA2_price as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as USDPrice
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
SELECT 
    block_timestamp::date as date,
  	case when block_timestamp>='2023-01-01' then '2023' else '2022' end as period,
	count(distinct tx_id) as tx_cnt,
    sum(tx_cnt) over (order by date) as cum_tx_cnt,
    avg(tx_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_day_tx,
    avg(tx_cnt) over (order by date, date rows between 14 preceding and current row) as ma15_day_tx,
    avg(tx_cnt) over (order by date, date rows between 29 preceding and current row) as ma30_day_tx,
	count(distinct TX_SENDER) as usr_cnt,
    avg(usr_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_day_usr,
    avg(usr_cnt) over (order by date, date rows between 14 preceding and current row) as ma15_day_usr,
    avg(usr_cnt) over (order by date, date rows between 29 preceding and current row) as ma30_day_usr,
	sum(FEE) as tx_fee_luna,
    sum(tx_fee_luna) over (order by date) as cum_tx_fee_luna,
  	avg(tx_fee_luna) over (order by date, date rows between 6 preceding and current row) as ma7_day_fee_luna,
    avg(tx_fee_luna) over (order by date, date rows between 14 preceding and current row) as ma15_day_fee_luna,
    avg(tx_fee_luna) over (order by date, date rows between 29 preceding and current row) as ma30_day_fee_luna,
	sum(FEE*USDPrice) as tx_fee_usd,
    sum(tx_fee_usd) over (order by date) as cum_tx_fee_usd,
  	avg(tx_fee_usd) over (order by date, date rows between 6 preceding and current row) as ma7_day_fee_usd,
    avg(tx_fee_usd) over (order by date, date rows between 14 preceding and current row) as ma15_day_fee_usd,
    avg(tx_fee_usd) over (order by date, date rows between 29 preceding and current row) as ma30_day_fee_usd,
  	avg(CASE WHEN tx_succeeded = true THEN 1 ELSE 0 END) as avg_succeed_tx_cnt,
	avg(CASE WHEN tx_succeeded != true THEN 1 ELSE 0 END) as avg_failed_tx_cnt,
	100*avg_succeed_tx_cnt/(tx_cnt) as avg_success_rate,
	100*avg_failed_tx_cnt/(tx_cnt) as avg_failed_rate
FROM terra.core.fact_transactions t JOIN LUNA2_price p on t.block_timestamp::date = p.p_date
WHERE block_timestamp > '2022-05-28' -- LUNA 2.0 LAUNCH
AND block_timestamp <= CURRENT_DATE - 1
group by 1,2
order by 1
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query6)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='tx_cnt', color='period')
fig.update_layout(title_text='Transaction Traffic per day')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='usr_cnt', color='period')
fig.update_layout(title_text='User Traffic per day')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('tx_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='tx_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('ma7_day_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='ma7_day_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='MA7-D Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Average Success & Failed Txs Conut')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily Average Success & Failed Txs Rate')),
                use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Transaction Metrics Over Time by **:red[Week]**')

df_query7 = """ 
with LUNA2_price as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as USDPrice
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
SELECT 
    date_trunc('week', block_timestamp)::date as date,
  	case when block_timestamp>='2023-01-01' then '2023' else '2022' end as period,
	count(distinct tx_id) as tx_cnt,
    sum(tx_cnt) over (order by date) as cum_tx_cnt,
    avg(tx_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_week_tx,
	count(distinct TX_SENDER) as usr_cnt,
    avg(usr_cnt) over (order by date, date rows between 6 preceding and current row) as ma7_week_usr,
	sum(FEE) as tx_fee_luna,
    sum(tx_fee_luna) over (order by date) as cum_tx_fee_luna,
  	avg(tx_fee_luna) over (order by date, date rows between 6 preceding and current row) as ma7_week_fee_luna,
	sum(FEE*USDPrice) as tx_fee_usd,
    sum(tx_fee_usd) over (order by date) as cum_tx_fee_usd,
  	avg(tx_fee_usd) over (order by date, date rows between 6 preceding and current row) as ma7_week_fee_usd,
  	avg(CASE WHEN tx_succeeded = true THEN 1 ELSE 0 END) as avg_succeed_tx_cnt,
	avg(CASE WHEN tx_succeeded != true THEN 1 ELSE 0 END) as avg_failed_tx_cnt,
	100*avg_succeed_tx_cnt/(tx_cnt) as avg_success_rate,
	100*avg_failed_tx_cnt/(tx_cnt) as avg_failed_rate
FROM terra.core.fact_transactions t JOIN LUNA2_price p on t.block_timestamp::date = p.p_date
WHERE block_timestamp > '2022-05-28' -- LUNA 2.0 LAUNCH
AND block_timestamp <= CURRENT_DATE - 1
group by 1,2
order by 1
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query7)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='tx_cnt', color='period')
fig.update_layout(title_text='Transaction Traffic per Week')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='usr_cnt', color='period')
fig.update_layout(title_text='User Traffic per Week')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('tx_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='tx_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Weekly Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('ma7_week_fee_usd', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='ma7_week_fee_luna')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='MA7-W Amount Fees Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Weely Average Success & Failed Txs Conut')),
                use_container_width=True, theme=theme_plotly)
with c2:
    base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
    line = base.mark_line(color='orange').encode(y=alt.Y('avg_success_rate', axis=alt.Axis(grid=True)))
    bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_failed_rate')
    st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Weekly Average Success & Failed Txs Rate')),
                use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")

df_query8 = """ 
--SQL Credit: https://app.flipsidecrypto.com/velocity/queries/50d4b68a-e7b1-4efb-be98-b951b4a5eeca
with 
  whales_movements as (
  SELECT
  block_timestamp,
  TX:body:messages[0]:from_address as seller,
  TX:body:messages[0]:to_address as buyer,
  TX:body:messages[0]:amount[0]:amount/pow(10,6) as amount,
  tx_id
from terra.core.fact_transactions
where tx:body:messages[0]:amount[0]:denom = 'uluna' 
  and block_timestamp > '2022-05-28' 
  and block_timestamp <= CURRENT_DATE - 1
  and tx_succeeded = true
  and amount >=1e4
)
SELECT 
  trunc(block_timestamp,'week')::date as date,
  case 
  		when block_timestamp>='2023-01-01' then '2023' 
  else '2022' end as period,
  count(distinct tx_id) as tx_cnt,
  count(distinct seller)*(-1) as whales_selling_cnt,
  count(distinct buyer) as whales_buying_cnt,
  whales_selling_cnt - whales_buying_cnt as net_whales_behavior,
  sum(amount) as moved_volume
FROM whales_movements
group by 1 ,2
order by 1 
"""
st.subheader('Specific **:red[Whales]** Behaviour analysis')

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query8)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='tx_cnt', color='period')
fig.update_layout(title_text='Transaction Traffic per day')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, = st.columns(2)
with c1:
    fig = px.bar(df, x='date', y='whales_selling_cnt', color='period')
    fig.update_layout(title_text='Whales Count as Seller by Week')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with c2:
    fig = px.bar(df, x='date', y='whales_buying_cnt', color='period')
    fig.update_layout(title_text='Whales Count as Buyer by Week')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
line = base.mark_line(color='orange').encode(y=alt.Y('net_whales_behavior', axis=alt.Axis(grid=True)))
bar = base.mark_line(color='purple',opacity=0.5).encode(y='moved_volume')
st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Whales Type vs. Moved Volume')),
                use_container_width=True, theme=theme_plotly)


df_query9 = """ 
--SQL Credit: https://app.flipsidecrypto.com/velocity/queries/ea6781ea-31b1-4bac-bfc4-f7dcb62ef423
SELECT 
    trunc(block_timestamp,'week')::date as date,
    label,
	count(distinct tx_id) as tx_cnt,
    sum( tx_cnt) over (partition by label order by date) as cum_tx_cnt,
	sum(TX:body:messages[0]:amount[0]:amount)/pow(10,6) as volume,
    sum(volume) over (partition by label order by date) as cum_volume,
    count(distinct TX:body:messages[0]:from_address) as usr_cnt
FROM terra.core.fact_transactions x
  join terra.classic.dim_labels y on x.TX:body:messages[0]:to_address = y.address
WHERE tx:body:messages[0]:amount[0]:denom = 'uluna' -- LUNA 2.0 ACTIONS
AND block_timestamp > '2022-05-28' -- LUNA 2.0 LAUNCH
AND block_timestamp <= CURRENT_DATE - 1
AND tx_succeeded = true
group by 1,2
order by 1 
"""
st.subheader('Activity per **:red[Platform]** by Week')

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query9)
df = pd.DataFrame(results.records)
df.info()

fig = px.bar(df, x='date', y='tx_cnt', color='label', log_y=True)
fig.update_layout(title_text='Tx Count per Platform by Week(Log Scale)')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='usr_cnt', color='label', log_y=True)
fig.update_layout(title_text='User Count per Platform by Week(Log Scale)')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='volume', color='label', log_y=True)
fig.update_layout(title_text='VOLUME(LUNA2.0) per Platform by Week(Log Scale)')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


st.subheader('**:red[New Users]** Over Time by Week')


df_query10 = """ 
with new_users as (
  SELECT 
  distinct TX:body:messages[0]:from_address as wallet,
  min(block_timestamp) as debut
  from terra.core.fact_transactions 
  where block_timestamp > '2022-05-28' 
  AND tx_succeeded = true
  group by 1 
),
  tx_user as (
  SELECT
  trunc(block_timestamp,'day') as date,
  TX:body:messages[0]:from_address as wallet,
  count(distinct tx_id) as txs
  from terra.core.fact_transactions 
  where block_timestamp > '2022-05-28' 
  AND tx_succeeded = true
  group by 1,2
  ),
  final as (
SELECT 
  date_trunc('week', block_timestamp)::date as date,
  case 
  		when block_timestamp>='2023-01-01' then '2023' 
  else '2022' end as period,
  count(distinct TX:body:messages[0]:from_address) as active_users,
  count(distinct wallet) as new_users,
  sum(new_users) over (order by date) as cum_new_users
FROM terra.core.fact_transactions x
  join new_users y on x.block_timestamp=y.debut
WHERE tx:body:messages[0]:amount[0]:denom = 'uluna' -- LUNA 2.0 ACTIONS
AND block_timestamp > '2022-05-28' -- LUNA 2.0 LAUNCH
AND tx_succeeded = true
group by 1,2
order by 1
  )
SELECT
	x.date,
  	period,
	active_users,
  	new_users,
  	cum_new_users,
  	avg(txs) as avg_tx_per_user
from final x
join tx_user y on x.date=y.date
group by 1,2,3,4,5
order by 1 asc  
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query10)
df = pd.DataFrame(results.records)
df.info()

fig = px.bar(df, x='date', y='new_users', color='period')
fig.update_layout(title_text='New User per Week')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
line = base.mark_line(color='orange').encode(y=alt.Y('cum_new_users', axis=alt.Axis(grid=True)))
bar = base.mark_line(color='purple',opacity=0.5).encode(y='avg_tx_per_user')
st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Weekly Average Txs per Users vs. Total New Users')),
                use_container_width=True, theme=theme_plotly)

st.write(
         """
**:red[NOTE]**
:The dot graphs below by color assigned has been used for each individual dot over the past two months.
The values of the related measurements are shown in the dot graphs, with the hours of the day and days of the
week indicated by their positions along the **x-** and **y-axes**, respectively.
In the dot plots, when the  dot’s color become darker the rate went up and vice versa.
"""
         )


df_query11 = """ 
WITH tx as (
  SELECT
  dayname(BLOCK_TIMESTAMP::date) as day_of_week,
  HOUR(block_timestamp) as hour_of_day,
  count(*) as tx_cnt,
  tx_succeeded,
  count(CASE WHEN tx_succeeded != true THEN 1 END) as fail_tx_cnt
  FROM terra.core.fact_transactions
  WHERE BLOCK_TIMESTAMP::date >= CURRENT_DATE-60
  and BLOCK_TIMESTAMP::date < CURRENT_DATE
  GROUP BY 1, 2,4
)
SELECT
   day_of_week,
   hour_of_day,
   (tx_cnt-fail_tx_cnt)/60 as stpm,
   (fail_tx_cnt/tx_cnt) as tfr
FROM tx
ORDER by 1, 2  
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query11)
df = pd.DataFrame(results.records)
df.info()

c1, c2 = st.columns(2)
with c1:
    fig = px.scatter(df, x='hour_of_day', y='day_of_week', color='stpm',
                                 title='Success transactions per minute on hour of day (UTC)')
    fig.update_layout(legend_title=None, xaxis_title='Hour', yaxis_title='Days of Week',
                          coloraxis_colorbar=dict(title='STPM'))
    fig.update_xaxes(categoryorder='category ascending')
    fig.update_yaxes(categoryorder='array', categoryarray=week_days)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.scatter(df, x='hour_of_day', y='day_of_week', color='tfr',
                                 title='Transactions fail rate on hours of day(UTC)')
    fig.update_layout(legend_title=None, xaxis_title='Hour', yaxis_title=None, coloraxis_colorbar=dict(title='TFR'))
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)



df_query12 = """ 
WITH tx as ( 
  SELECT
  dayname(BLOCK_TIMESTAMP::date) as day_of_week,
  HOUR(block_timestamp) as hour_of_day,
  count(*) as tx_cnt,
  tx_succeeded,
  count(CASE WHEN tx_succeeded != true THEN 1 END) as fail_tx_cnt
  FROM terra.core.fact_transactions
  WHERE BLOCK_TIMESTAMP::date >= CURRENT_DATE-60
  and BLOCK_TIMESTAMP::date < CURRENT_DATE
  GROUP BY 1, 2,4
)
SELECT
   sum(tx_cnt-fail_tx_cnt)/(60*1440) as succeed_tx_per_minute, 
   sum(fail_tx_cnt)/sum(tx_cnt)*100  as failed_rate
FROM tx  
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query12)
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

c1, c2 = st.columns(2)
with c1:
    st.metric(label='**Success Tx/Minute**', value=str(df['succeed_tx_per_minute'].map('{:,.2f}'.format).values[0]))

with c2:
    st.metric(label='**Failed Transaction Rate(%)**', value=str(df['failed_rate'].map('{:,.2f}'.format).values[0]))


