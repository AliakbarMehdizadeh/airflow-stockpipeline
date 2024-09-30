import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Load from PostgreSQL
def load_data():
    try:
        engine = create_engine('postgresql://stock_user:stock_pass@localhost:5432/stock_db')
        query = 'SELECT * FROM apple_stock_data'
        data = pd.read_sql(query, engine)
        return data
    except SQLAlchemyError as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Title of the app
st.title('Real-Time Apple Stock Data')
stock_data = load_data()

if stock_data.empty:
    st.warning("No data found in the table.")
else:
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data.set_index('date', inplace=True) 

    # Calculate the Simple Moving Average (SMA) with a window of 5
    # stock_data['SMA'] = stock_data['4. close'].rolling(window=5).mean()

    # Plot with Plotly
    fig = go.Figure()

    # Plot the Closing Price
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['4. close'], mode='lines', name='Close Price', line=dict(color='blue')))

    # Plot the Simple Moving Average (SMA)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA'], mode='lines', name='SMA (7)', line=dict(color='orange')))

    # Update the layout for the chart
    fig.update_layout(
        title='Apple Stock Closing Prices and Simple Moving Average (SMA)',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        legend_title_text='Legend'
    )

    # Display the Plotly chart
    st.plotly_chart(fig)
