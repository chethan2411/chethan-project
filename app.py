import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# Set page config
st.set_page_config(page_title="📈 Live Stock Market Dashboard", layout="wide")

st.title("📊 Live Stock Market Dashboard")
st.markdown("View real-time stock prices, trends, volume, and comparisons.")

# Sidebar controls
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT", "GOOGL"]
)

start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
ma_days = st.sidebar.multiselect("Select Moving Averages (days)", [7, 14, 30], default=[7, 30])
dark_mode = st.sidebar.checkbox("Enable Dark Mode", value=True)
plotly_template = "plotly_dark" if dark_mode else "plotly_white"

# Sector mapping (basic example)
sector_map = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "AMZN": "Consumer Discretionary",
    "TSLA": "Automotive",
    "META": "Technology",
    "NVDA": "Technology",
    "NFLX": "Communication Services",
    "IBM": "Technology",
    "INTC": "Technology"
}

if symbols:
    all_data = yf.download(symbols, start=start_date, end=end_date)
    all_data.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in all_data.columns]
    all_data.reset_index(inplace=True)

    st.subheader("📅 Raw Data Preview")
    st.dataframe(all_data.head(), use_container_width=True)
    st.download_button("⬇️ Download Data as CSV", all_data.to_csv(index=False), file_name="stock_data.csv")

    # Chart 1: Closing Price with Moving Averages
    st.subheader("📈 Closing Price Trend")
    fig1 = px.line(template=plotly_template)
    for symbol in symbols:
        fig1.add_scatter(x=all_data["Date"], y=all_data[f"Close_{symbol}"], mode="lines", name=f"{symbol} Close")
        for ma in ma_days:
            ma_col = f"{symbol}_MA{ma}"
            all_data[ma_col] = all_data[f"Close_{symbol}"].rolling(window=ma).mean()
            fig1.add_scatter(x=all_data["Date"], y=all_data[ma_col], mode="lines", name=f"{symbol} MA{ma}", line=dict(dash="dot"))
    fig1.update_layout(title="Closing Price & Moving Averages", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Volume Traded
    st.subheader("📊 Volume Traded")
    fig2 = px.area(template=plotly_template)
    for symbol in symbols:
        fig2.add_scatter(x=all_data["Date"], y=all_data[f"Volume_{symbol}"], mode="lines", stackgroup='one', name=symbol)
    fig2.update_layout(title="Daily Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Candlestick (Single Stock)
    st.subheader("🕯️ Candlestick Chart (Single Stock)")
    single_stock = st.selectbox("Choose a stock for candlestick chart", options=symbols)
    candle_data = yf.download(single_stock, start=start_date, end=end_date)
    fig3 = go.Figure(data=[go.Candlestick(
        x=candle_data.index,
        open=candle_data['Open'],
        high=candle_data['High'],
        low=candle_data['Low'],
        close=candle_data['Close'],
        name=single_stock
    )])
    fig3.update_layout(template=plotly_template, title=f"{single_stock} Candlestick Chart", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig3, use_container_width=True)

    # Chart 4: Daily Price Change (Close - Open)
    st.subheader("📉 Daily Price Change (Close - Open)")
    fig4 = go.Figure()
    for symbol in symbols:
        price_change = all_data[f'Close_{symbol}'] - all_data[f'Open_{symbol}']
        fig4.add_trace(go.Bar(x=all_data['Date'], y=price_change, name=symbol))
    fig4.update_layout(
        template=plotly_template,
        title="Daily Price Change",
        xaxis_title="Date",
        yaxis_title="Price Change (USD)",
        barmode='overlay'
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: Daily Percentage Change (%)
    st.subheader("📈 Daily Percentage Change (%)")
    fig5 = px.line(template=plotly_template)
    for symbol in symbols:
        pct_change = all_data[f"Close_{symbol}"].pct_change() * 100
        fig5.add_scatter(x=all_data["Date"], y=pct_change, mode="lines", name=f"{symbol} % Change")
    fig5.update_layout(title="Daily Percentage Change", xaxis_title="Date", yaxis_title="Change (%)")
    st.plotly_chart(fig5, use_container_width=True)

    # Chart 6: Sector Performance Comparison
    st.subheader("🏭 Sector Performance Comparison")
    sector_changes = {}
    for symbol in symbols:
        sector = sector_map.get(symbol, "Unknown")
        pct_change = all_data[f"Close_{symbol}"].pct_change()
        if sector in sector_changes:
            sector_changes[sector].append(pct_change)
        else:
            sector_changes[sector] = [pct_change]

    sector_avg = {
        "Sector": [],
        "Average Daily % Change": []
    }
    for sector, changes in sector_changes.items():
        combined = pd.concat(changes, axis=1).mean(axis=1)
        sector_avg["Sector"].append(sector)
        sector_avg["Average Daily % Change"].append(round(combined.mean() * 100, 4))

    df_sector = pd.DataFrame(sector_avg)
    fig6 = px.bar(df_sector, x="Sector", y="Average Daily % Change", template=plotly_template)
    fig6.update_layout(title="Average Daily % Change by Sector", yaxis_title="Avg Daily % Change (%)")
    st.plotly_chart(fig6, use_container_width=True)

    # Summary Table
    st.subheader("📋 Stock Comparison Summary")
    summary_data = {
        "Symbol": [],
        "Min Close": [],
        "Max Close": [],
        "Mean Close": [],
        "Last Close": []
    }
    for symbol in symbols:
        close_series = all_data[f"Close_{symbol}"]
        summary_data["Symbol"].append(symbol)
        summary_data["Min Close"].append(round(close_series.min(), 2))
        summary_data["Max Close"].append(round(close_series.max(), 2))
        summary_data["Mean Close"].append(round(close_series.mean(), 2))
        summary_data["Last Close"].append(round(close_series.iloc[-1], 2))
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

else:
    st.warning("👈 Please select at least one stock symbol to view data.")
