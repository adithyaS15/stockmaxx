import streamlit as st
from google.cloud import bigquery
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title = "Stockmaxxing Time")

client = bigquery.Client(project = "stockmaxx")

@st.cache_data(ttl=3600)
def load_data():
    query = ""
    return client.query(query).to_dataframe()

df = load_data()

# check the documentation for more info
st.title("Stockmaxx : Market and Sentiment Analysis")
# st.markdown..?

ticker = st.sidebar.selectbox("Select ticker symbol: ", df["ticker"].unique())
ticker_df = df[df["ticker"] == ticker]

# Summary Metrics Row
if not ticker_df.empty:
    latest = ticker_df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Closing Price", f"${latest['closing_price']:.2f}")
    col2.metric("Sentiment Score", f"{latest['avg_sentiment']:.4f}")
    col3.metric("Direction Signal", str(latest["predicted_direction"]))
    
    up_prob = latest["up_probability"]
    col4.metric("Up Probability", f"{up_prob:.2%}" if up_prob is not None else "N/A")

# Dual-Axis Price & Sentiment Overlay Chart
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=ticker_df["date"], y=ticker_df["closing_price"], name="Close Price", line=dict(color="#1f77b4")),
    secondary_y=False
)
fig.add_trace(
    go.Bar(x=ticker_df["date"], y=ticker_df["avg_sentiment"], name="Headline Sentiment", opacity=0.3),
    secondary_y=True
)
fig.update_layout(title=f"{ticker} Price vs. News Sentiment Trend", hovermode="x unified")
fig.update_yaxes(title_text="Stock Price ($)", secondary_y=False)
fig.update_yaxes(title_text="Sentiment Score", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# Historical Data Table
st.subheader("Recent Asset Logs")
st.dataframe(
    ticker_df[["date", "closing_price", "avg_sentiment", "predicted_direction", "up_probability"]].tail(15),
    use_container_width=True
)