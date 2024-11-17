import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Function to display summary and insights
def display_summary(data):
    st.markdown("""
        <div style="background-color:#262730;padding:10px;margin-bottom:20px;border-radius:8px;">
            <h3>Data Summary</h3>
            <p>{}</p>
        </div>
        """.format(data.describe().to_html()), unsafe_allow_html=True)

    # Add actionable tips based on data
    st.markdown("""
        <div style="background-color:#262730;padding:10px;margin-bottom:20px;border-radius:8px;">
            <h3>Actionable Tips: 💡</h3>
            <ul>
                <li>If "Profit" is negative, consider reducing expenses or increasing revenue.</li>
                <li>If "Revenue" is below target, consider boosting sales.</li>
                <li>If "Expenses" are high, consider cutting unnecessary costs.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Correlation Heatmap
def display_correlation_heatmap(data):
    st.markdown("""
        <div style="background-color:#262730;padding:10px;margin-bottom:20px;border-radius:8px;">
            <h3>Correlation Heatmap</h3>
        </div>
    """, unsafe_allow_html=True)
    numeric_cols = data.select_dtypes(include="number").columns
    corr_matrix = data[numeric_cols].corr()

    # Use Plotly Express to create the correlation heatmap with better color scaling
    fig = px.imshow(corr_matrix, text_auto=True, 
                    color_continuous_scale='RdBu', 
                    title="Correlation Heatmap",
                    color_continuous_midpoint=0)  # Use a midpoint of 0 for better visual clarity

    st.plotly_chart(fig)

# Function to handle visualizations based on the chart type
def display_visualizations(data, year_colors):
    st.markdown("""
        <div style="background-color:#262730;padding:10px;margin-bottom:20px;border-radius:8px;">
            <h3>Visualizations</h3>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar for chart selection
    chart_type = st.sidebar.selectbox("Choose Chart Type", ["Bar Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"])
    x_axis = st.sidebar.selectbox("Select X-axis", data.columns)
    y_axis = st.sidebar.selectbox("Select Y-axis", data.columns)
    
    # Define a color column if 'Year' or 'Month' exists and user has customized colors
    color_column = None
    if "Year" in data.columns and year_colors:
        color_column = "Year"
    elif "Month" in data.columns and year_colors:
        color_column = "Month"

    # Dynamic visualization creation based on chart type
    if chart_type == "Bar Chart":
        fig = px.bar(
            data, 
            x=x_axis, 
            y=y_axis, 
            color=color_column,  # Add the color column for grouping
            color_discrete_map=year_colors  # Use the customized colors
        )
    
    elif chart_type == "Scatter Plot":
        fig = px.scatter(
            data, 
            x=x_axis, 
            y=y_axis, 
            color=color_column,  # Add the color column for grouping
            color_discrete_map=year_colors
        )
    elif chart_type == "Pie Chart":
        # Aggregating data for Pie chart
        if x_axis != y_axis:
            data_pie = data.groupby(x_axis).sum().reset_index()  # Grouping data by the X-axis for the pie chart
            fig = px.pie(
                data_pie, 
                names=x_axis, 
                values=y_axis, 
                color=x_axis,  # Use x-axis for color groups
                color_discrete_map=year_colors
            )
        else:
            st.warning("⚠️ For Pie Chart, X-axis and Y-axis should not be the same.")
            return
    elif chart_type == "Histogram":
        fig = px.histogram(
            data, 
            x=x_axis, 
            color=color_column,  # Add the color column for grouping
            color_discrete_map=year_colors
        )
    elif chart_type == "Box Plot":
        fig = px.box(
            data, 
            x=x_axis, 
            y=y_axis, 
            color=color_column,  # Add the color column for grouping
            color_discrete_map=year_colors
        )

    st.plotly_chart(fig)

# Function to handle color customization for Year or Month
def customize_colors(data):
    st.sidebar.subheader("Customize Year/Month Colors")
    year_colors = {}
    if "Year" in data.columns:
        years = data["Year"].unique()
        for year in years:
            year_colors[year] = st.sidebar.color_picker(f"Color for {year}", "#636EFA")
    elif "Month" in data.columns:
        months = data["Month"].unique()
        for month in months:
            year_colors[month] = st.sidebar.color_picker(f"Color for {month}", "#636EFA")
    else:
        st.warning("⚠️ No 'Year' or 'Month' column found to customize colors. Default colors will be used.")
    return year_colors

# Function to automatically calculate the profit if not present
def calculate_profit(data):
    if "Profit" not in data.columns:
        if "Revenue" in data.columns and "Expenses" in data.columns:
            data["Profit"] = data["Revenue"] - data["Expenses"]
    return data

# Main function
def main():
    
    st.title("InsightViz: Dynamic Business Data Insights📊")
    st.sidebar.title("Options")

    # File Uploads
    data_file = st.sidebar.file_uploader("Upload Your Data CSV", type=["csv"])

    # Manual Color Customization Option
    personalize_colors = st.sidebar.checkbox("Want to Personalize Colors?")
    year_colors = {}

    if data_file is not None:
        data = pd.read_csv(data_file)

        # Automatically calculate Profit if not present
        data = calculate_profit(data)

        # Display Data Preview
        st.markdown("""
            <div style="background-color:#262730;padding:10px;margin-bottom:20px;border-radius:8px;">
                <h3>Data Preview</h3>
            </div>
        """, unsafe_allow_html=True)
        st.write(data.head())

        # Customize Colors for Year or Month
        if personalize_colors:
            year_colors = customize_colors(data)
        else:
            # Default color scheme for Year or Month
            if "Year" in data.columns:
                year_colors = {year: "#636EFA" for year in data["Year"].unique()}
            elif "Month" in data.columns:
                year_colors = {month: "#636EFA" for month in data["Month"].unique()}
            else:
                year_colors = {}

        # Display summary and tips
        display_summary(data)

        # Display Correlation Heatmap
        display_correlation_heatmap(data)

        # Visualizations
        display_visualizations(data, year_colors)
    else:
        st.info("Please upload a CSV file to proceed.")

if __name__ == "__main__":
    main()
