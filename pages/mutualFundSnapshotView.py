import streamlit as st
from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd

with open('mutualfundsnapshotview.json') as f:
    data = json.load(f)
    data = data[0]

# Set up Streamlit page
st.set_page_config(page_title="Financial Asset Overview", layout="wide")

# Title and Fund Overview Section
st.title("Financial Asset Overview")
st.subheader(data["LegalName"])
st.write(f"**Fund ID**: {data['Id']}")
st.write(f"**Domicile**: {data['Domicile']}")
st.write(f"**Asset Class**: {data['CategoryBroadAssetClass']['Name']}")
st.write(f"**Benchmark**: `Id` {data['Benchmark'][0]['Id']} `Global Asset Class Id` {data['Benchmark'][0]['GlobalAssetClassId']} `Type` {data['Benchmark'][0]['Type']} `Name` {data['Benchmark'][0]['Name']}")
st.write(f"**Currency**: {data['Currency']['Id']}")

# Inception Dates Section
st.markdown("### Inception Dates")
st.write(f"**Inception Date**: {datetime.strptime(data['InceptionDate'], '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')}")
st.write(f"**Performance Inception Date**: {datetime.strptime(data['PerformanceInceptionDate'], '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')}")

# Investment Strategy Section
st.markdown("### Investment Strategy")
st.write(data["InvestmentStrategy"])

# Latest Price Information Section
st.markdown("### Latest Price")
date_str = data['LastPrice']['Date']
formatted_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')
st.write(f"**Date**: {formatted_date}")
st.write(f"**Price**: {data['LastPrice']['Value']} {data['LastPrice']['Currency']['Id']}")

# Investment Requirements Section
st.markdown("### Investment Requirements")

# Display the information in Streamlit
st.write(f"**Initial Investment**: `Unit` {data['PurchaseDetails'][0]['InitialInvestment']['Unit']} `Value` {data['PurchaseDetails'][0]['InitialInvestment']['Value']} {data['Currency']['Id']}")
st.write(f"**Subsequent Investment**: `Unit` {data['PurchaseDetails'][0]['SubsequentInvestment']['Unit']} `Value` {data['PurchaseDetails'][0]['SubsequentInvestment']['Value']} {data['Currency']['Id']}")
st.write(f"**Front Load Fee**: `Unit` {data['PurchaseDetails'][0]['FrontLoad']['Unit']} `Value` {data['PurchaseDetails'][0]['FrontLoad']['Value']}%")

# Provider Information Section
st.markdown("### Provider Information")
st.write(f"**Provider**: {data['ProviderCompany']['Name']}")
st.write(f"**Address**: {data['ProviderCompany']['AddressLine1']}, {data['ProviderCompany']['City']}, {data['ProviderCompany']['Country']}")
st.write(f"**Homepage**: [Visit Website]({data['ProviderCompany']['Homepage']})")

# Documents Section
st.markdown("### Available Documents")
# Assuming 'Documents' is a list of dictionaries
documents = data['Documents']

for doc in documents:
    st.write(f"**Document Id**: {doc['DocumentId']}")
    effective_date_str = doc['EffectiveDate']
    formatted_effective_date = datetime.strptime(effective_date_str, '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')
    
    filing_date_str = doc['FilingDate']
    formatted_filing_date = datetime.strptime(filing_date_str, '%Y-%m-%dT%H:%M:%S').strftime('%d %B %Y')

    st.write(f"**Effective Date**: {formatted_effective_date}")
    st.write(f"**Filing Date**: {formatted_filing_date}")
    
    # Check if 'DownloadLink' exists before trying to access it
    if 'DownloadLink' in doc:
        st.markdown(f"[Download Document]({doc['DownloadLink']})")
    else:
        st.warning("Download link is not available for this document.")


st.title('Trailing Performance')

trailing_performance = data['TrailingPerformance']
time_periods = []
values = []
dates = []

for performance in trailing_performance:
    date = pd.to_datetime(performance['Date'])  # Extract the date from the performance
    for ret in performance['Return']:
        time_periods.append(ret['TimePeriod'])
        values.append(ret['Value'])
        dates.append(date)  # Append the date associated with each return

# Creating the DataFrame
df = pd.DataFrame({
    'TimePeriod': time_periods,
    'Value': values,
    'Date': dates  # No need to convert again, already in datetime
})

# Check if all lists have the same length
if len(time_periods) == len(values) == len(dates):
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(time_periods, values, color='skyblue')
    plt.xlabel('Time Period')
    plt.ylabel('Return Value')
    plt.title('Trailing Performance Returns')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    # Show the plot in Streamlit
    st.pyplot(plt)  # Use Streamlit's method to display the plot

    # Clear the current figure after displaying
    plt.clf()

    latest_date = df['Date'].max()
    df_latest = df[df['Date'] == latest_date]
    st.write("Performance Data Table:")
    st.write(df_latest)

else:
    st.error("Data arrays have different lengths. Please check the data.")

st.title('Risk Statistics')

risk_statistics = data['RiskStatistics']
return_types = []
information_ratios = []
tracking_errors = []
standard_deviations = []
dates = []

for stat in risk_statistics:
    date = pd.to_datetime(stat['Date'])
    return_types.append(stat['ReturnType'])
    
    # Append the first value of each statistic list
    information_ratios.append(stat['InformationRatios'][0]['Value'])
    tracking_errors.append(stat['TrackingErrors'][0]['Value'])
    standard_deviations.append(stat['StandardDeviations'][0]['Value'])
    dates.append(date)

# Create a DataFrame for plotting
df = pd.DataFrame({
    'ReturnType': return_types,
    'InformationRatio': information_ratios,
    'TrackingError': tracking_errors,
    'StandardDeviation': standard_deviations,
    'Date': dates
})

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))

# Bar chart for Information Ratios, Tracking Errors, and Standard Deviations
bar_width = 0.25
x = range(len(return_types))

# Create bars for each statistic
ax.bar(x, df['InformationRatio'], width=bar_width, label='Information Ratio', color='lightblue', align='center')
ax.bar([p + bar_width for p in x], df['TrackingError'], width=bar_width, label='Tracking Error', color='lightgreen', align='center')
ax.bar([p + bar_width * 2 for p in x], df['StandardDeviation'], width=bar_width, label='Standard Deviation', color='salmon', align='center')

# Adding labels and title
ax.set_xlabel('Return Type')
ax.set_ylabel('Value')
ax.set_title('Risk Statistics Overview')
ax.set_xticks([p + bar_width for p in x])  # Center the x-tick labels
ax.set_xticklabels(return_types)
ax.legend()
ax.grid(axis='y')

# Show the plot in Streamlit
st.pyplot(fig)  # Use Streamlit's method to display the plot

# Clear the current figure after displaying
plt.clf()

# Display the DataFrame as a table
st.write("Risk Statistics Data Table:")
st.write(df)


st.title("Historical Performance Series (SAR)")
historical_performance = data['HistoricalPerformanceSeries']

# Summary Table
summary_data = []
for entry in historical_performance:
    latest_return = entry['Return'][-1]
    summary_data.append({
        "Return Type": entry['ReturnType'],
        "Start Date": entry['StartDate'],
        "Frequency": entry['Frequency'],
        "Most Recent Return (Value)": latest_return.get('Value', 'N/A'),
        "Most Recent Date": latest_return['Date']
    })

summary_df = pd.DataFrame(summary_data)
st.subheader("Historical Performance Summary")
st.table(summary_df)

# Detailed Sections
for entry in historical_performance:
    st.subheader(f"{entry['ReturnType']} ({entry['Frequency']})")
    st.write(f"**Start Date:** {entry['StartDate']}")
    st.write("**Returns:**")
    
    return_data = entry['Return']
    return_df = pd.DataFrame(return_data)
    return_df['Date'] = pd.to_datetime(return_df['Date'])
    
    if 'Value' in return_df.columns:
        return_df = return_df.dropna(subset=['Value'])
        st.table(return_df)

        # Using Streamlit's line_chart for plotting
        st.line_chart(return_df.set_index('Date')['Value'], use_container_width=True)
    else:
        st.write("No return values available for this period.")


# Footer or any additional details
st.write("— End of Report —")