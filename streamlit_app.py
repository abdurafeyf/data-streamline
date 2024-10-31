import pandas as pd
import streamlit as st
import json
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Financial Metrics",
    layout="wide",  # This sets the layout to wide
)

# Custom CSS to increase the height of the container
st.markdown(
    """
    <style>
    .reportview-container {
        height: 800px;  /* Adjust this value for desired height */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function to load and extract 'Value' and 'EndDate' data from nested JSON
def extract_values(filename, series_key):
    try:
        with open(filename) as f:
            data = json.load(f)
        # Navigate to the series list and extract 'EndDate' and 'Value' from each entry
        if series_key == "HistoryDetail":
            history = data["TimeSeries"]["Security"][0]["HistoryDetail"]
            values = [(item["EndDate"], float(item["Value"])) for item in history]
        else:
            history = data["TimeSeries"]["Security"][0][series_key][0]["HistoryDetail"]
            values = [(item["EndDate"], float(item["Value"])) for item in history]
        return values
    except (KeyError, IndexError, json.JSONDecodeError):
        st.error(f"Error extracting data from {filename}")
        return []

# Load and extract data for each metric
growth_data = extract_values("growth.json", "GrowthSeries")
cumulative_return_data = extract_values("cumulativereturn.json", "CumulativeReturnSeries")
price_data = extract_values("price.json", "HistoryDetail")
return_data = extract_values("return.json", "ReturnSeries")
rollingreturn_data = extract_values("rollingreturn.json", "RollingReturn")

# Create a dictionary to structure the data
data = {
    "Metric": ["Growth", "Cumulative Return", "Price", "Return", "Rolling Return"],
    "Latest Value": [
        growth_data[-1][1] if growth_data else None,
        cumulative_return_data[-1][1] if cumulative_return_data else None,
        price_data[-1][1] if price_data else None,
        return_data[-1][1] if return_data else None,
        rollingreturn_data[-1][1] if rollingreturn_data else None,
    ],
    "Time Series": [
        growth_data,
        cumulative_return_data,
        price_data,
        return_data,
        rollingreturn_data,
    ]
}

# Convert to DataFrame for Latest Value only
df_latest = pd.DataFrame(data).dropna(subset=['Latest Value'])

# Display the Latest Values in a dataframe
st.dataframe(
    df_latest[["Metric", "Latest Value"]],
    hide_index=True
)

# Display time series line charts for each metric with altair for better control over x-axis
st.subheader("Time Series Charts")
for i, metric in enumerate(data['Metric']):
    st.write(f"**{metric} Time Series**")
    if data["Time Series"][i]:  # Check if data is available
        # Create a DataFrame for time series data with date and value
        ts_data = data["Time Series"][i]
        ts_df = pd.DataFrame(ts_data, columns=["Date", metric])
        ts_df["Date"] = pd.to_datetime(ts_df["Date"])  # Convert Date to datetime format
        
        # Create an Altair line chart with formatted date axis
        line_chart = alt.Chart(ts_df).mark_line().encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%B %Y", title="Timeline")),  # Month Year format
            y=alt.Y(f"{metric}:Q", title="Value")
        ).properties(
            width=700,  # Adjust width for better layout
            height=400
        )
        
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.warning(f"No data available for {metric}.")
