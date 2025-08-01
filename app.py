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
