import streamlit as st
from streamlit_option_menu import option_menu
import pycountry
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(layout="wide", initial_sidebar_state="expanded" )
#covid = pd.read_csv("data/covid_cases.csv") #For offline 
covid = pd.read_csv("https://covid19.who.int/WHO-COVID-19-global-data.csv")
latest_covid = pd.read_csv("https://covid19.who.int/WHO-COVID-19-global-table-data.csv", index_col=False)
vaccination_data = pd.read_csv("https://covid19.who.int/who-data/vaccination-data.csv", index_col=False)
vaccination_data['DATE_UPDATED']=vaccination_data['DATE_UPDATED'].astype('datetime64[ns]') #Convert vaccine DATE_UPDATED column to date type

def get_iso3(iso2):
    #Function takes in iso_alpha2 country codes and returns the iso_alpha 3 codes"""
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except:
        #In case we have errors that row of data will be left out.
        #Try except is a good way to handle possible errors that might occur while running a function"""
        pass

#Functions to generate visualizations
#choropleth
def generateMap(case, hover):
    covid['iso_alpha'] = covid.Country_code.apply(lambda x: get_iso3(x))
    fig_Cases= px.choropleth(covid,
                locations="iso_alpha",
                color=case, 
                hover_name="Country", # column to add to hover information
                hover_data=['Date_reported', case, hover],
                color_continuous_scale=px.colors.sequential.Viridis_r,
                animation_frame="Date_reported" # animation based on the dates
                )
    fig_Cases.update_layout(mapbox_style='carto-positron', height=700) #Enlarge the figure
    fig_Cases.update_layout(margin={"r":0, "l":0, "t":0, "b":0})
    fig_Cases.update_geos(visible=False)
    st.plotly_chart(fig_Cases, use_container_width=True, theme='streamlit')
    st.markdown('<p style="color:grey; font-size:26px; font-family: Helvetica, Arial"> <span style="color:#3B71CA; font-weight:bold">Globally</span>, as of <span style="color:#3B71CA; font-weight:bold">'+date.today().strftime("%H:%M %Z %d %B %Y")+'</span>, there have been <span style="color:#3B71CA; font-weight:bold">'+format(latest_covid.loc[0, "Cases - cumulative total"], ",d")+ ' confirmed</span> cases of COVID-19, including <span style="color:#DC4C64; font-weight:bold">' + format(latest_covid.loc[0, "Deaths - cumulative total"], ",d") +' deaths</span>, reported to WHO. As of <span style="color:#14A44D; font-weight:bold">'+vaccination_data['DATE_UPDATED'].max().strftime("%d %B %Y")+'</span>, a total of <span style="color:#14A44D; font-weight:bold">' + format(vaccination_data['TOTAL_VACCINATIONS'].sum().astype(int), ",d") + ' vaccine doses</span> have been administered.</P>', unsafe_allow_html=True)

current_date = date.today() 
current_date = current_date.strftime("%Y-%m-%d")
covidToday=covid.query("Date_reported==@current_date")

#Function for Generating area chart
def generateAreaChart(data, x_asis, y_axis, title):
    fig_Cases=px.histogram(data, 
                          x=x_asis,
                          y=y_axis, 
                          hover_name=x_asis, 
                          hover_data=[y_axis], 
                          color_discrete_sequence = ['grey'], 
                          title=title
                         )
    fig_Cases.update_yaxes(title=None)
    fig_Cases.update_xaxes(title=None)
    fig_Cases.update_layout(height=350, barmode='group', bargap=0.30, bargroupgap=0.0)
    st.plotly_chart(fig_Cases, use_container_width=True, theme='streamlit')

#Function for Generating chart for cases per region
def generateRegionChart(region, regionCode, color):
    st.subheader(':grey['+ region +']')
    covidFiltered=covid[covid['WHO_region']==regionCode]
    st.write('<p style="font-weight:bold; font-size:21px">'+format(covidFiltered['New_cases'].sum(), ",d")+'<br><span style="font-weight:normal; font-size:14px">confirmed cases</span></p>', unsafe_allow_html=True)
    fig_Region_Cases=px.histogram(covidFiltered, 
                        x="Date_reported", 
                        y="New_cases", 
                        hover_name="Date_reported", 
                        hover_data=["New_cases", "New_deaths"], 
                        color_discrete_sequence = [color]
                        )
    fig_Region_Cases.update_yaxes(title=None)
    fig_Region_Cases.update_xaxes(title=None)
    fig_Region_Cases.update_layout(height=400, barmode='group', bargap=0.30, bargroupgap=0.0)
    st.plotly_chart(fig_Region_Cases, use_container_width=True, theme='streamlit')
#END of function

st.header(':blue[WHO Coronavirus (COVID-19) Dashboard]')
colMenu, colBody = st.columns([1, 6])
with colMenu:
    st.write('<p style="margin-top:100%"></p>', unsafe_allow_html=True)
    menus=['New Cases', 'Cumulative Cases', 'New Deaths']
    selected = st.selectbox(' ', menus)
    st.write('<h2 style="text-align:right; font-weight:bold;">' +format(latest_covid.loc[0, "Cases - newly reported in last 24 hours"], ",d")+ '<br><span style="text-decoration:none; font-weight:normal; font-size:18px">New cases in last 24hrs</span></h2>', unsafe_allow_html=True)
    st.write('<h2 style="text-align:right; font-weight:bold;">'  +format(latest_covid.loc[0, "Cases - cumulative total"], ",d")+ '<br><span style="text-decoration:none; font-weight:normal; font-size:18px">cumulative cases</span></h2>', unsafe_allow_html=True)
    st.write('<h2 style="text-align:right; font-weight:bold;">'  +format(latest_covid.loc[0, "Deaths - cumulative total"], ",d")+ '<br><span style="text-decoration:none; font-weight:normal; font-size:18px">Deaths</span></h2>', unsafe_allow_html=True)
with colBody:
    if selected =='Cumulative Cases':
        st.subheader(':grey[Cumulative Covid19 Cases]')
        generateMap('Cumulative_cases', 'Cumulative_deaths')
    elif selected =='New Cases':
        st.subheader(':grey[New Covid19 Cases]')
        generateMap('New_cases', 'New_deaths')
    elif selected =='New Deaths':
        st.subheader(':grey[New Covid19 Deaths]')
        generateMap('New_deaths', 'New_cases')
    else:
        pass

spaceCol, colCasesNum, colCasesVisual = st.columns([1, 2, 5])
with colCasesNum:
    st.write('<br>', unsafe_allow_html=True)
with colCasesNum:
    st.write('<br>', unsafe_allow_html=True)
    st.header(':grey[Global Situation]')
    st.write('<h2 style="text-align:center; font-weight:bold;">' +format(latest_covid.loc[0, "Cases - cumulative total"], ",d")+ '<br><span style="text-decoration:none; font-weight:normal; font-size:30px">Confirmed cases</span></h2>', unsafe_allow_html=True)

    st.write('<br><br><br><br><br><br><br><h2 style="text-align:center; font-weight:bold;">' +format(latest_covid.loc[0, "Deaths - cumulative total"], ",d")+ '<br><span style="text-decoration:none; font-weight:normal; font-size:30px">Deaths</span></h2>', unsafe_allow_html=True)
with colCasesVisual:
    generateAreaChart(covid, 'Date_reported', 'New_cases', '')


    generateAreaChart(covid, 'Date_reported', 'New_cases', '')

spaceCol, colRegionNum, colRegionvisual = st.columns([1, 2, 4])
with colCasesNum:
    st.write('<br>', unsafe_allow_html=True)
with colRegionNum:
    st.subheader(':grey[Situation by WHO Region]')
    fig_Region_Cases=px.histogram(covid, 
                        x="New_cases", 
                        y="WHO_region", 
                        color="WHO_region",
                        hover_data=["New_cases", "New_deaths"], 
                        text_auto=True
                        )
    fig_Region_Cases.update_yaxes(title=None)
    fig_Region_Cases.update_xaxes(title=None)
    fig_Region_Cases.update_traces(textfont_size=18)
    fig_Region_Cases.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_Region_Cases, use_container_width=True, theme='streamlit')
with colRegionvisual:
        fig_Region_Cases=px.histogram(covid, 
                            x="Date_reported", 
                            y="New_cases", 
                            color="WHO_region"
                            )
        fig_Region_Cases.update_yaxes(title=None)
        fig_Region_Cases.update_xaxes(title=None)
        fig_Region_Cases.update_layout(height=500, bargap=0.30, bargroupgap=0.0)
        st.plotly_chart(fig_Region_Cases, use_container_width=True, theme='streamlit')

colCasesNum, colRegionalvisual1, colRegionalvisual2 = st.columns([1, 3, 3])
with colCasesNum:
    st.write('<br>', unsafe_allow_html=True)
with colRegionalvisual1:
    generateRegionChart('Europe', 'EURO', 'palegreen')
    generateRegionChart('Western Pacific', 'WPRO', 'deeppink')
    generateRegionChart('Eastern Mediterranean', 'EMRO', 'limegreen')
with colRegionalvisual2:
    generateRegionChart('Americas', 'AMRO', 'goldenrod')
    generateRegionChart('South-East Asia', 'SEARO', 'purple')
    generateRegionChart('Africa', 'AFRO', 'royalblue')


st.write('<br><p style="text-align:center; font-weight:light; font-size:14px"> Geoffrey\'s ADS Assignment(Replicate <a href="https://covid19.who.int/">WHO COVID19 Dashboard</a>)<br>Data sourced from <a href="https://covid19.who.int/data/">https://covid19.who.int/data/</a></p>', unsafe_allow_html=True)


### TASKS
## 1. GENERATE THREE MORE ANIMATED GRAPHS i.e. new cases, cumulative deaths, new deaths
## 2. Give your graphs titles and if possible add explanative text after each graph
## 3. Use widgets in the sidebar to help the user chooose between the four animations: e.g. select box, button, radio 
## 4. create bar graphs to show the cumulative cases per day and cumulative daeaths per day 
## 5. deploy your app to streamlit cloud
## 6. submit the link to your streamlit app on dexvirtual


