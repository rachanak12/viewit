import streamlit as st 
import plotly.express as px 
import pandas as pd
import pandas as pd

from app import db, User
import warnings

# Ignoring warnings
warnings.filterwarnings('ignore')

# Streamlit page configuration
st.set_page_config(page_title="Analysis For Chemical and Petrochemical Industries", page_icon="💼", layout="wide")
st.title(" :bar_chart: Industry Insights")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


file_path = r"C:\Users\RACHANA KULKARNI\Desktop\trialdata.csv"

# Function to load data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    return df

# Function to save data to CSV
def save_to_csv(df, file_path):
    df.to_csv(file_path, index=False)


# Function to add data manually
def add_plant_data_manually():
    plant_id = st.text_input("Plant ID")
    plant_name = st.text_input("Plant Name")
    latitude = st.number_input("Latitude")
    longitude = st.number_input("Longitude")
    capacity = st.number_input("Capacity")
    production_volume = st.number_input("Production Volume")
    production_efficiency = st.number_input("Production Efficiency")
    market_share = st.number_input("Market Share")
    sales_revenue = st.number_input("Sales Revenue")
    compliance_status = st.selectbox("Compliance Status", ["Compliant", "Non-Compliant"])
    qa_metrics = st.number_input("QA Metrics")
    defect_rate = st.number_input("Defect Rate")
    product_specification = st.text_input("Product Specification")
    research_projects = st.text_input("Research Projects")
    cs_score = st.number_input("CS Score")
    revenue = st.number_input("Revenue")
    cost_of_production = st.number_input("Cost of Production")
    profit_margin = st.number_input("Profit Margin")
    carbon_emission = st.number_input("Carbon Emission")
    waste_disposal_metrics = st.number_input("Waste Disposal Metrics")
    energy_consumption = st.number_input("Energy Consumption")
    year = st.number_input("Year")

    new_plant_data = None  # Initialize to None

    if st.button("Add Plant Data"):
        new_plant_data = pd.DataFrame({
            "PlantID": [plant_id],
            "PlantName": [plant_name],
            "Latitude": [latitude],
            "Longitude": [longitude],
            "Capacity": [capacity],
            "ProductionVolume": [production_volume],
            "ProductionEfficiency": [production_efficiency],
            "MarketShare": [market_share],
            "SalesRevenue": [sales_revenue],
            "ComplianceStatus": [compliance_status],
            "QAMetrics": [qa_metrics],
            "DefectRate": [defect_rate],
            "ProductSpecification": [product_specification],
            "ResearchProjects": [research_projects],
            "CSscore": [cs_score],
            "revenue": [revenue],
            "costOfProduction": [cost_of_production],
            "ProfitMargin": [profit_margin],
            "CarbonEmmision": [carbon_emission],
            "WasteDisposalMetrics": [waste_disposal_metrics],
            "EnergyConsumption": [energy_consumption],
            "Year": [year]
        })
    return new_plant_data



df = load_data(file_path)

# Manual Data Entry
if st.checkbox("Add Data Manually"):
    new_data = add_plant_data_manually() 
    if new_data is not None:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("Data added successfully!")
        # Save the updated DataFrame to CSV file
        save_to_csv(df, file_path)


grouped_df = df.groupby("PlantName").agg({
    "ProductionEfficiency": "max"
}).reset_index()

# Displaying the treemap
fig = px.treemap(grouped_df, path=["PlantName"], values="ProductionEfficiency")

# Render the plotly figure using st.plotly_chart
st.plotly_chart(fig)



# List of parameters to analyze over time
parameters = [
    "revenue", 
    "costOfProduction"
]

# Check if the "Year" column exists in the dataframe
if "Year" in df.columns:
    st.header("Parameter Analysis Over Time for Each Plant")

    # Allow users to select parameters
    selected_parameters = st.multiselect("Select Parameters", parameters, default=parameters)

    # Allow users to select specific plant names
    plant_names = df["PlantName"].unique()
    selected_plants = st.multiselect("Select Plants", plant_names)

    # Plot selected parameters over time for each selected plant
    if selected_parameters and selected_plants:
        for parameter in selected_parameters:
            st.subheader(f"Mean {parameter} by Plant")
            # Grouping and aggregation to find the mean value of the selected parameter for each plant
            grouped_df = df[df["PlantName"].isin(selected_plants)].groupby("PlantName")[parameter].mean().reset_index()
            # Create a bar plot
            fig = px.bar(grouped_df, x="PlantName", y=parameter, title=f"Mean {parameter} by Plant")
            st.plotly_chart(fig)
        st.write("Analyzing the mean value of selected parameters for each plant can provide insights into the average performance of different aspects across plants.")
    else:
        st.write("Please select at least one parameter and one plant.")
else:
    st.write("Data for parameter analysis over time is not available.")

# Create scatter plot on map
fig = px.scatter_mapbox(df, 
                         lat="Latitude", 
                         lon="Longitude", 
                         hover_name="PlantName", 
                         zoom=5)
# Update map layout
fig.update_layout(mapbox_style="open-street-map",  # You can change the map style here if needed
                  mapbox=dict(center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean())),
                  width=800,  # Adjust the width as needed
                  height=600)

# Display map
st.title("Plant Locations")
st.plotly_chart(fig)

grouped_plants_count = df.groupby("PlantName").size().reset_index(name='Count')

# Calculate the percentage of each value
grouped_plants_count['Percentage'] = grouped_plants_count['Count'] / grouped_plants_count['Count'].sum() * 100

# Filter out values less than 3%
filtered_plants_count = grouped_plants_count[grouped_plants_count['Percentage'] >= 3]


# Grouping and aggregation for research projects taken by each plant
grouped_research_projects = df.groupby("PlantName")["researchProjects"].sum().reset_index()

# Calculate the total number of research projects
total_research_projects = grouped_research_projects["researchProjects"].sum()

# Calculate the percentage of each value
grouped_research_projects['Percentage'] = grouped_research_projects['researchProjects'] / total_research_projects * 100

# Filter out values less than 3%
filtered_research_projects = grouped_research_projects[grouped_research_projects['Percentage'] >= 3]

# Displaying the pie chart for research projects taken by each plant
fig_research_projects = px.pie(filtered_research_projects, values="researchProjects", names="PlantName", title="Research Projects taken by Plants")
st.plotly_chart(fig_research_projects)
st.write("Analyzing the research projects taken by each plant provides insights into their innovation efforts and potential for technological advancements.")

pairs = [("ProductionVolume", "SalesRevenue"), ("ProfitMargin", "Capacity")]

# Perform correlation analysis for each pair of variables
for pair in pairs:
    x_var, y_var = pair
    # Filter the DataFrame if needed
    filtered_df = df  # You can add filtering conditions here if required
    # Create scatter plot with trendline and perform linear regression (OLS)
    fig_corr = px.scatter(filtered_df, x=x_var, y=y_var, trendline="ols", title=f"Correlation between {x_var} and {y_var}")
    # Display the scatter plot
    st.plotly_chart(fig_corr)

# Additional information
st.write("Analyzing correlations helps to understand relationships between various aspects of business operations.")

grouped_df = df.groupby("PlantName").agg({
    "CarbonEmmision": "max"
}).reset_index()

# Displaying the treemap
fig = px.treemap(grouped_df, path=["PlantName"], values="CarbonEmmision",title="Treemap for Carbon Emissions Plantwise")

# Render the plotly figure using st.plotly_chart
st.plotly_chart(fig)

# Sidebar for selecting attributes
x_axis = st.sidebar.selectbox("Select X-axis Attribute", ["ProductionVolume", "SalesRevenue", "Capacity"])
y_axis = st.sidebar.selectbox("Select Y-axis Attribute", ["SalesRevenue", "Capacity", "ProfitMargin"])
bubble_size = st.sidebar.selectbox("Select Bubble Size Attribute", ["Capacity", "ProductionVolume", "SalesRevenue"])
color_by = st.sidebar.selectbox("Color By", ["ComplianceStatus", "Year"])

# Scatter plot with bubble chart
fig = px.scatter(df, x=x_axis, y=y_axis, size=bubble_size, color=color_by,
                 hover_name="PlantName", title="Bubble Chart")

# Plotly configuration
fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))

# Display the plot
st.plotly_chart(fig)

