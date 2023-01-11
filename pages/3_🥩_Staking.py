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

# Layout
st.set_page_config(page_title='Staking', page_icon=':bar_chart:', layout='wide')
st.title('🥩 Staking')

st.write(
    """
    By assigning their LUNA to a validator, LUNA owners can participate in the network and collect incentives.
    The return from **:blue[staking]** Luna is figured using the incentives and bonuses earned by validators for their work 
    in mining blocks. As soon as a block is mined, all validators get a proportional share of the reward 
    (based on the number of LUNA staked in their pool, which represents their voting power). 
    After the validator's fee is subtracted from the reward, the remaining funds will be divided among the delegators 
    in proportion to their stake (including the validator).

    What follows is a discussion of the staking behaviors of Terra players. Delegation, redelegation, and undelegation 
    are the three possible user interactions in staking.

    The following visual details the total daily volume, average daily number, and total daily number of 
    wallets participating in all staking actions.
    """
)
st.write("")
st.subheader('Staking Overall View')


st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Staking Metrics in **:blue[Total]**')

df_query1 = """ 
WITH lunaPrice as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as "LUNA2.0 Price($)"
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
  ACTION,
  count(DISTINCT tx_id) as delegation_tx_cnt,
  count(DISTINCT delegator_address) as delegators,
  count(DISTINCT validator_address) as validators,
  sum(amount) as volume_luna,
  sum(CASE WHEN action IN ('Delegate','Redelegate') then amount
  ELSE -1*amount  END) as net_staked_volume_LUNA,
  sum(amount*"LUNA2.0 Price($)") as volume_usd,
  sum(CASE WHEN action IN ('Delegate','Redelegate') then amount*"LUNA2.0 Price($)"
  ELSE -1*amount*"LUNA2.0 Price($)"  END) as net_staked_volume_usd
FROM terra.core.ez_staking a join lunaPrice p on a.block_timestamp::date = p.p_date
WHERE tx_succeeded = 'TRUE'
AND block_timestamp <= CURRENT_DATE - 1
GROUP BY 1 
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query1)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='delegation_tx_cnt', names='action', title='Total Value & Share of Staking Txs')
    fig.update_layout(legend_title='Staking Txs', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='volume_usd', names='action', title='Total Value & Share of Staking Volume($)')
    fig.update_layout(legend_title='Staking Volume', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='delegators', names='action', title='Total Value & Share of Delegator Count')
    fig.update_layout(legend_title='Delegator', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='validators', names='action', title='Total Value & Share of Validator Count')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Staking Metrics in Daily Average in **:blue[2022]**')

df_query2 = """ 
WITH lunaPrice as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as "LUNA2.0 Price($)"
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tot as (
  SELECT 
  ACTION,
  count(DISTINCT block_timestamp::date) as day_cnt,
  count(DISTINCT tx_id) as tx_cnt,
  count(DISTINCT delegator_address) as delegators,
  count(DISTINCT validator_address) as validators,
  sum(amount) as volume_luna
FROM terra.core.ez_staking a join lunaPrice p on a.block_timestamp::date = p.p_date
WHERE tx_succeeded = 'TRUE'
AND block_timestamp <= '2022-12-31'
GROUP BY 1 
  )
SELECT
  	ACTION,
	avg(tx_cnt/day_cnt) as avg_tx_per_day,
	avg(delegators/day_cnt) as avg_delegators_per_day,
	avg(validators/day_cnt) as avg_validators_per_day,
	avg(volume_luna/day_cnt) as avg_volume_luna_per_day,
	avg(volume_luna/tx_cnt) as avg_volume_luna_per_tx,
	avg(volume_luna/delegators) as avg_volume_luna_per_delegators,
	avg(volume_luna/validators) as avg_volume_luna_per_validators
FROM tot
GROUP BY 1 
"""

st.experimental_memo(ttl=21600)
def compute(a):
    data=sdk.query(a)
    return data
results = compute(df_query2)
df = pd.DataFrame(results.records)
df.info()
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='avg_tx_per_day', names='action', title='Average Value & Share of Staking Txs per Day')
    fig.update_layout(legend_title='Staking Txs', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_delegators_per_day', names='action', title='Total Value & Share of Staking Volume(LUNA) per Day')
    fig.update_layout(legend_title='Staking Volume', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='avg_validators_per_day', names='action', title='Total Value & Share of Delegator Count per Day')
    fig.update_layout(legend_title='Delegator', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_volume_luna_per_day', names='action', title='Total Value & Share of Validator Count per Day')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, c3 = st.columns(3)
with c1:
    fig = px.pie(df, values='avg_volume_luna_per_tx', names='action', title='Total Amt & % of Volume(LUNA)/Tx')
    fig.update_layout(legend_title='Delegator', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_volume_luna_per_delegators', names='action', title='Total Amt & % of Volume(LUNA)/Delegator')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c3:
    fig = px.pie(df, values='avg_volume_luna_per_validators', names='action', title='Total Amt & % of Volume(LUNA)/Validator')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")
st.write("")
st.subheader('Staking Metrics in Daily Average in **:blue[2023]**')

df_query3 = """ 
WITH lunaPrice as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as "LUNA2.0 Price($)"
from terra.core.ez_swaps
where from_currency = 'uluna' 
and to_currency in ('ibc/CBF67A2BCF6CAE343FDF251E510C8E18C361FC02B23430C121116E0811835DEF',
  					'ibc/B3504E092456BA618CC28AC671A71FB08C6CA0FD0BE7C8A5B5A3E2DD933CC9E4') --USDC,USDT 
and to_amount > 0
and from_amount > 0
and tx_succeeded = TRUE
group by 1
)
  , tot as (
  SELECT 
  ACTION,
  count(DISTINCT block_timestamp::date) as day_cnt,
  count(DISTINCT tx_id) as tx_cnt,
  count(DISTINCT delegator_address) as delegators,
  count(DISTINCT validator_address) as validators,
  sum(amount) as volume_luna
FROM terra.core.ez_staking a join lunaPrice p on a.block_timestamp::date = p.p_date
WHERE tx_succeeded = 'TRUE'
AND block_timestamp >= '2023-01-01'
AND block_timestamp <= current_date - 1
GROUP BY 1 
  )
SELECT
  	ACTION,
	avg(tx_cnt/day_cnt) as avg_tx_per_day,
	avg(delegators/day_cnt) as avg_delegators_per_day,
	avg(validators/day_cnt) as avg_validators_per_day,
	avg(volume_luna/day_cnt) as avg_volume_luna_per_day,
	avg(volume_luna/tx_cnt) as avg_volume_luna_per_tx,
	avg(volume_luna/delegators) as avg_volume_luna_per_delegators,
	avg(volume_luna/validators) as avg_volume_luna_per_validators
FROM tot
GROUP BY 1 
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
    fig = px.pie(df, values='avg_tx_per_day', names='action', title='Average Value & Share of Staking Txs per Day')
    fig.update_layout(legend_title='Staking Txs', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_delegators_per_day', names='action',
                 title='Total Value & Share of Staking Volume(LUNA) per Day')
    fig.update_layout(legend_title='Staking Volume', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='avg_validators_per_day', names='action',
                 title='Total Value & Share of Delegator Count per Day')
    fig.update_layout(legend_title='Delegator', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_volume_luna_per_day', names='action',
                 title='Total Value & Share of Validator Count per Day')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

c1, c2, c3 = st.columns(3)
with c1:
    fig = px.pie(df, values='avg_volume_luna_per_tx', names='action', title='Total Amt & % of Volume(LUNA)/Tx')
    fig.update_layout(legend_title='Delegator', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c2:
    fig = px.pie(df, values='avg_volume_luna_per_delegators', names='action',
                 title='Total Amt & % of Volume(LUNA)/Delegator')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
with c3:
    fig = px.pie(df, values='avg_volume_luna_per_validators', names='action',
                 title='Total Amt & % of Volume(LUNA)/Validator')
    fig.update_layout(legend_title='Validators', legend_y=1)
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
st.write("")
st.write("")
st.write("")
st.write("")


st.subheader('**:blue[Staking]** Metrics Over Time')


df_query4 = """ 
WITH lunaPrice as (
  select 
  	block_timestamp::date as p_date,
	median(to_amount/from_amount) as "LUNA2.0 Price($)"
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
  ACTION,
  count(DISTINCT tx_id) as tx_cnt,
  count(DISTINCT delegator_address) as delegators,
  count(DISTINCT validator_address) as validators,
  sum(amount) as volume_luna,
  sum(CASE WHEN action IN ('Delegate','Redelegate') then amount
  ELSE -1*amount  END) as net_staked_volume_LUNA,
  sum(amount*"LUNA2.0 Price($)") as volume_usd,
  sum(CASE WHEN action IN ('Delegate','Redelegate') then amount*"LUNA2.0 Price($)"
  ELSE -1*amount*"LUNA2.0 Price($)" END) as net_staked_volume_usd,
  sum(tx_cnt) over (partition by action order by date) as cumu_delegation_tx_cnt,
  sum(volume_luna) over (partition by action order by date) as cumu_staked_vlume_luna,
  sum(net_staked_volume_LUNA) over (ORDER by date) as cumu_net_staked_vlume_luna,
  sum(volume_usd) over (partition by action order by date) as cumu_staked_vlume_usd,
  sum(net_staked_volume_usd) over (ORDER by date) as cumu_net_staked_vlume_usd
FROM terra.core.ez_staking a join lunaPrice p on a.block_timestamp::date = p.p_date
WHERE tx_succeeded = 'TRUE'
AND date <= CURRENT_DATE - 1
GROUP BY 1 ,2
ORDER BY 1 
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query4)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='tx_cnt', color='action')
fig.update_layout(title_text='Daily Tx Count per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='delegators', color='action')
fig.update_layout(title_text='Daily Delegators Count per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='validators', color='action')
fig.update_layout(title_text='Daily Validators Count per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='volume_luna', color='action')
fig.update_layout(title_text='Daily Volume(LUNA2.0) per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='volume_usd', color='action')
fig.update_layout(title_text='Daily Volume($) per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='net_staked_volume_luna', color='action')
fig.update_layout(title_text='Daily Net Staked Volume(LUNA2.0) per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y='net_staked_volume_usd', color='action')
fig.update_layout(title_text='Daily Net Staked Volume($) per Action')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")
st.subheader('Staking Metrics in Cumulative State')
st.write("")
st.write("")

base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
line = base.mark_line(color='orange').encode(y=alt.Y('cumu_net_staked_vlume_usd', axis=alt.Axis(grid=True)))
bar = base.mark_line(color='purple',opacity=0.5).encode(y='cumu_net_staked_vlume_luna')
st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Cumulative Net Staked Volume (in $LUNA2.0 & $USD)')),
                use_container_width=True, theme=theme_plotly)

st.subheader('New Users as **:blue[Delegator]**')


df_query5 = """ 
with first_tx as (
SELECT
  delegator_address as users,
  min(block_timestamp) as min_date
FROM terra.core.ez_staking
WHERE tx_succeeded = 'TRUE'
AND block_timestamp::date <= CURRENT_DATE - 1
and ACTION = 'Delegate'
GROUP BY 1
)  
SELECT
  min_date::date as date,
  count(DISTINCT users) as new_delegators,
  sum(new_delegators) over (order by date) as cum_new_delegators
FROM first_tx
GROUP by 1 
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query5)
df = pd.DataFrame(results.records)
df.info()

base = alt.Chart(df).encode(x=alt.X('date', axis=alt.Axis(labelAngle=325)))
line = base.mark_line(color='purple').encode(y=alt.Y('new_delegators', axis=alt.Axis(grid=True)))
bar = base.mark_line(color='orange',opacity=0.5).encode(y='cum_new_delegators')
st.altair_chart(((bar + line).resolve_scale(y='independent').properties(title='Daily New Delegators & Cumulative Over Time')),
                use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")

st.subheader('Staking Reward')

st.write("")
st.write("")

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
  select 
  block_timestamp::date as date, 
  count(DISTINCT receiver) as reciver_cnt,
  sum(amount)/pow(10,6) as reward_volume_luna,
  sum(reward_volume_luna)over(ORDER by date) as cumulatove_reward_vol_luna,
  sum(amount*USDPrice/pow(10,6)) as reward_volume_usd,
  sum(reward_volume_usd)over(ORDER by date) as cumulatove_reward_vol_usd
FROM terra.core.ez_transfers t JOIN LUNA2_price p on t.block_timestamp::date = p.p_date
WHERE MESSAGE_VALUE['@type'] ='/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward'
  AND CURRENCY='uluna'
  AND date <= CURRENT_DATE-1
GROUP BY 1
order by 1 
"""

st.experimental_memo(ttl=21600)


def compute(a):
    data = sdk.query(a)
    return data
results = compute(df_query6)
df = pd.DataFrame(results.records)
df.info()
fig = px.bar(df, x='date', y='reciver_cnt')
fig.update_layout(title_text='Daily Staking Reward Reciver Count')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.bar(df, x='date', y=['reward_volume_luna', 'reward_volume_usd'])
fig.update_layout(title_text='Daily Staking Reciver Volume(in LUNA2.0 & $)')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

fig = px.area(df, x='date', y=['cumulatove_reward_vol_luna', 'cumulatove_reward_vol_usd'])
fig.update_layout(title_text='Cumulative Staking Reciver Volume(in LUNA2.0 & $)')
st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

st.write("")
st.write("")
st.write("")
st.write("")

st.subheader('Top 10 Delegator & Validators by the Most Net Staking Volume(LUNA2.0)')

st.write("")
st.write("")
@st.cache(ttl=10000)
def gat_data(query):
    if query == 'Top T0 Delegators':
        return pd.read_json(
            'https://node-api.flipsidecrypto.com/api/v2/queries/cac46f57-ba7c-416c-8dbc-c75aa06997fa/data/latest'
        )
    elif query == 'Top T0 Validators':
        return pd.read_json(
            'https://node-api.flipsidecrypto.com/api/v2/queries/19de1452-a2b8-4ca5-8879-eafee8c6950c/data/latest'
        )

top10_delegators = gat_data('Top T0 Delegators')
df = top10_delegators
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='Net Staked Volume', names='Delegators', title='Top T0 Delegators Address')
    fig.update_traces(textinfo='value+percent', textposition='inside', showlegend=False)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

top10_validators = gat_data('Top T0 Validators')
df = top10_validators
with c2:
    fig = px.pie(df, values='Net Staked Volume', names='Validators', title='Top T0 Validators Address')
    fig.update_traces(textinfo='value+percent', textposition='inside', showlegend=False)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


st.write("")
st.write("")
st.write("")
st.write("")

st.subheader('Top 10 Delegator by the Most Reward Volume($) & Distribution of Reward Recivers')

st.write("")
st.write("")
@st.cache(ttl=10000)
def gat_data(query):
    if query == 'Top T0 Reward Recivers':
        return pd.read_json(
            'https://node-api.flipsidecrypto.com/api/v2/queries/1ef97301-22b8-4c05-8402-a204a68422f7/data/latest'
        )
    elif query == 'Distribution of Reward Recivers':
        return pd.read_json(
            'https://node-api.flipsidecrypto.com/api/v2/queries/645b5810-23c2-4112-9774-3d1d5ff6ebc5/data/latest'
        )

top10_reciver = gat_data('Top T0 Reward Recivers')
df = top10_reciver
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(df, values='Reward Volume($)', names='Reciver', title='Top T0 Reward Recivers Address')
    fig.update_traces(textinfo='value+percent', textposition='inside', showlegend=False)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

distribution = gat_data('Distribution of Reward Recivers')
df = distribution
with c2:
    fig = px.pie(df, values='Reciver Count', names='DITRIBUTION', title='Distribution of Rewards Reciver')
    fig.update_traces(textinfo='value+percent', textposition='inside')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)



