# Libraries
import streamlit as st

# from PIL import Image

# Layout
st.set_page_config(page_title='New Year, New LUNA?', page_icon=':bar_chart:',
                   layout='wide')
st.write("## How did 2023 begin in Terra Luna2.0? 👋")

st.write("")
st.write("")
st.write("")
st.write("")

st.write(
    """
    The crypto industry continues to progress and its development has never stopped. Contributors
    of each blockchain keep developing each segment of the industry and the whole crypto ecosystem.
    This tool is designed to allow viewers to walk through Terra LUNA2.0s' ecosystem, 
    While the entire crypto market has been bearish since earlier last year(2022), the unprecedented crash of LUNA and 
    UST stablecoin was beyond any expectations or projections. While there were many red flags in Terra’s algorithmic 
    stablecoin concept, not many investors truly anticipated the coin to lose its value entirely. 

    LUNA’s crash was largely caused by its link to TerraUSD (UST), an algorithmic stablecoin. 
    While most stablecoins are pegged against a specific dollar value or equivalent currently reserved in 
    centralised banks, the UST stablecoin maintained its value through algorithms and computer-generated codes. 
    The process of maintaining the $1 price equilibrium included burning and minting LUNA/UST to maintain the price of 
    these tokens.

    However, during the bear market, a large amount of UST was dumped, causing the stablecoin to de-peg. 
    This caused a ripple effect in an already downward market, driving more and more investors to sell and burn UST, 
    thus minting more LUNA. This excessive mining led to a massive increase in LUNA’s circulating supply, 
    thus crashing its price. The token’s circulating supply was around 345 million in April, which became 6.5 trillion 
    on May 13th.

    Following the massive crash, Terraform labs decided to revive the altcoin, but this time without any links to 
    the algorithmic stablecoin. Developers launched a new Terra blockchain called Terra 2.0

    The old Terra chain is renamed Terra Luna Classic. The new LUNA 2.0 has a total locked supply of 1.0 billion,
    which is significantly better than the 6.5 trillion supply of the classic token. 35% of the new tokens are 
    airdropped to previous and existing LUNA holders. 10% of LUNA 2.0 is sent to those who held the token before the 
    UST crash, and 25% is sent to those who still own LUNA Classic and UST. Another 30% is sent to a pool of 
    LUNA investors [Read More...](https://financefeeds.com/understanding-terra-2-0-why-luna-deserves-another-chance/). 

    This tool is designed and structured in multiple **Pages** that are accessible using the sidebar.
    Each of these Pages addresses a different category of the ecosystem. Within each category
    (Activity, Supply, Staking, etc.) you are able to access your desired class to narrow/expand the Terra LUNA2.0s' ecosystem. 

    All values for amounts, prices, and volumes are in **Terra LUNA 2.0 & U.S. dollars** and the time frequency of the
    analysis was limited to the over **Launch date by day**.
    """
)

st.subheader('Methodology')
st.write(
    """
    The data for this analysis were selected from the [**Flipside Crypto**](https://flipsidecrypto.xyz/)
    data platform by using its **shroomDK**. The codes for this tool are saved and accessible
    in its [**GitHub Repository**](https://github.com/0xHaM3d/Terradash-Part-4-Bringing-It-All-Together).

    As the queries are updated on a daily and weekly basis to cover the most data, there is a chance
    that viewers encounter inconsistent data through the app. Due to the heavy computational power required to execute
    the queries, and also the size of the raw data being too large, it may take a few minutes to reload the data,
    or by downloading the data and loading it from the repository itself. 

    Besides the codes and queries mentioned above, the following dashboards created using Flipside Crypto were used
    as the core references in developing the current tool:
    - [Terradash: Development](https://app.flipsidecrypto.com/velocity/dashboard/terra-4-terradash-part-3-development-ap_qkZ)
    - [Terradash: Staking and Supply](https://app.flipsidecrypto.com/dashboard/terradash-part-2-staking-and-supply-SxnW1i)
    - [LUNA 2.0 story](https://app.flipsidecrypto.com/dashboard/luna-2-0-story-TGTVJn)
    """
)

st.write("")
st.write("")
st.write("")
st.write("")

c1, c2 = st.columns(2)
with c1:
    st.info('**Developer/Analyst: [@0xHaM☰d](https://twitter.com/0xham3d_eth)**', icon="💻")
with c2:
    st.info('**Data: [Flipside Crypto](https://flipsidecrypto.xyz/)**', icon="🧠")