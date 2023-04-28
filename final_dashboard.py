import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# setting page configurations for the dashboard
st.set_page_config(
    page_title="Airbnb Data visualization",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This is a visualization dashboard for airbnb dataset!"
    }
)

@st.cache_resource
def load_data():
    df = pd.read_csv('train.csv')
    return df

#loading dataset
df = load_data()

st.title("Airbnb Dataset Visualization Dashboard")

#sidebar dropdowns and filters
roomtype = ['Entire home/apt', 'Private room', 'Shared room']
roomtype_default = 'Entire home/apt'
roomtype_option = st.sidebar.selectbox('Select an option', roomtype, index=roomtype.index(roomtype_default))

price_range = st.sidebar.slider('Select price range', min(df['price']), max(df['price']), (0.0, 7.7), step=0.1)

bedrooms = st.sidebar.slider('Select number of bedrooms', min(df['bedrooms']), max(df['bedrooms']), (0.0, 10.0), step=1.0)

beds = st.sidebar.slider('Select number of beds', min(df['beds']), max(df['beds']), (0.0, 18.0), step=1.0)

reviews = st.sidebar.slider('Select number of reviews', min(df['number_of_reviews']), max(df['number_of_reviews']), (0.0, 700.0), step=1.0)

# filtering the data based on the selectors
filtered_df = df[(df['room_type'] == roomtype_option) & (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) & (df['number_of_reviews'] >= reviews[0]) &  (df['number_of_reviews'] <= reviews[1]) 
                 & (df['beds'] >= beds[0]) & (df['beds'] <= beds[1]) & (df['bedrooms'] >= bedrooms[0]) & (df['bedrooms'] <= bedrooms[1])]

# visualization chart
chart = alt.Chart(filtered_df).mark_circle().encode(
    x='longitude',
    y='latitude',
    size=alt.Size('price', scale=alt.Scale(range=[0, 1000]), legend=alt.Legend(title='Price')),
    color=alt.Color('number_of_reviews', legend=alt.Legend(title='Number of Reviews')),
    tooltip=['name', 'price', 'number_of_reviews', 'beds', 'bedrooms']
).properties(
    width=800,
    height=500
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
)

st.subheader("Listings filtered based on the options and filters values ")
st.write('The listings visualization is shown based on the values selected from the filters and dropdown from the sidebar..')
st.altair_chart(chart)

# Q.1) Number of airbnb's listings in a particular city? 
st.subheader("Number of listing across major cities in USA?")
col1, col2 = st.columns(2)
col1.write('Here we are visualizing the number of listings that are listed in various cities in the US.')
city = ['Boston', 'Chicago', 'DC', 'LA', 'NYC', 'SF']
city_default = 'NYC'
city_option = col1.selectbox('Select a city', city, index=city.index(city_default))

city_data = df[df["city"] == city_option]
st.write("Number of listings in", city_option, ":", len(city_data))

line_chart = alt.Chart(city_data).mark_bar().encode(
    x=alt.X('neighbourhood', title = 'Neighbourhood'),
    y=alt.Y('count()', title = 'Number of listings'),
    tooltip = ['neighbourhood', 'count()']
).properties(
    width=600,
    height=400
)

col2.altair_chart(line_chart)

# Q.2) Average accommodates across all the listings in a particular city?
st.subheader("Accommodates, bedrooms and beds available across all the listings in a particular city?")
q2col1, q2col2 = st.columns(2)
q2col1.write('Here we are visualizing the number of listings that are listed in various cities in the US.')
q2city = ['Boston', 'Chicago', 'DC', 'LA', 'NYC', 'SF']
q2city_default = 'NYC'
q2city_option = q2col1.selectbox('Choose a city', q2city, index=q2city.index(q2city_default))

q2city_data = df[df["city"] == q2city_option]
st.write("Number of listings in", q2city_option, ":", len(q2city_data))

properties = ['Accommodates', 'Bedrooms', 'Beds', 'Bathrooms']
q2property_default= 'Accommodates'
q2property_option = q2col1.selectbox('Select a property of the listing', properties, index=properties.index(q2property_default))

attr_def = {
                    'Accommodates': 'accommodates',
                    'Bedrooms': 'bedrooms',
                    'Beds': 'beds',
                    'Bathrooms': 'bathrooms'
                }

grouped_data = q2city_data.groupby('neighbourhood')[attr_def[q2property_option]].agg(['mean','median','max','min']).reset_index()

line_chart1 = alt.Chart(grouped_data, title = 'Average number of '+ q2property_option + ' based on the neighbourhood in a city').mark_bar().encode(
    x=alt.X('neighbourhood', sort=alt.EncodingSortField(field='mean', op='mean', order='descending')),
    y='mean',
    tooltip = ['neighbourhood', 'mean','median', 'max', 'min']
).properties(
    width=600,
    height=400
)

q2col2.altair_chart(line_chart1)

qcol1, qcol2 = st.columns(2)
# Q.3) Properties in a city that has a cleaning fee?
qcol1.subheader("Number of listing having cleaning fees and no cleaning fees in USA?")
cleaning_fee = df[df["cleaning_fee"] == True].shape[0]
no_cleaning_fee = df[df['cleaning_fee'] == False].shape[0]

pie_plot = px.pie(
    values = [cleaning_fee, no_cleaning_fee],
    names=["with cleaning fees","without cleaning fees"]
)

qcol1.plotly_chart(pie_plot)

qcol2.subheader("chart for displaying various room types in the listings")
room_type1 = df[df["room_type"] == "Entire home/apt"].shape[0]
room_type2 = df[df['room_type'] == "Private room"].shape[0]
room_type3 = df[df['room_type'] == "Shared room"].shape[0]

pie_plot_room_types = px.pie(
    values = [room_type1, room_type2, room_type3],
    names=["Entire home/apt", "Private room", "Shared room"]
)

qcol2.plotly_chart(pie_plot_room_types)

st.subheader("Number of listings that have hosts verified across all the cities?")
hosts_data = df.groupby(['city', 'host_identity_verified'])['id'].count().reset_index()
hosts_data['status'] = hosts_data['host_identity_verified'].apply(lambda x: 'Verified' if 't' in x else 'Not Verified')

host_verified_chart = alt.Chart(hosts_data).mark_bar().encode(
    x=alt.X('city:N', axis=alt.Axis(title='City')),
    y=alt.Y('id:Q', axis=alt.Axis(title='Number of Hosts')),
    color=alt.Color('status:N', legend=alt.Legend(title='Host Verification Status'))
).properties(width=600, height=400)

st.altair_chart(host_verified_chart)

from pycaret.regression import *

st.subheader("Price prediction for the house based on the properties: ")
# load model
@st.cache_data 
def predict_cache(test_data):
    rf_saved = load_model('rf_model')
    predictions = predict_model(rf_saved, data = test_data)
    return predictions['prediction_label']

# Inputs
column1, column2 = st.columns(2)
room_type = column1.selectbox('Type of room', ['Entire home/apt', 'Private room', 'Shared room'])
accommodates = column1.slider('Number of accommodates', min(df['accommodates']), max(df['accommodates']), 5.0 , step=1.0)
city = column1.selectbox('City', ['Boston', 'Chicago', 'DC', 'LA', 'NYC', 'SF'])
city_dat = df[df['city'] == city]
neighbourhoods_data = city_dat['neighbourhood'].unique()
neighbourhood = column2.selectbox('Neighbourhood', neighbourhoods_data)
property_type = column2.selectbox('Property Type', df['property_type'].unique())
host_response_rate = column2.selectbox('Host response rate', df['host_response_rate'].unique())

df = pd.read_csv('test.csv')
test_data =df.head(1)
# pd.DataFrame({'room_type': [room_type], })
test_data['room_type'] = room_type
test_data['accommodates'] = accommodates
test_data['city'] = city
test_data['neighbourhood'] = neighbourhood
test_data['property_type'] = property_type
test_data['host_response_rate'] = host_response_rate

# load model
rf_saved = load_model('rf_model')

# show prediction
predictions = predict_model(rf_saved, data = test_data)
st.write('Price = $%0.2f'%predictions['prediction_label'][0])
