import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
from textblob import TextBlob
import os

from llama_index import (
    GPTVectorStoreIndex, Document, SimpleDirectoryReader,
    QuestionAnswerPrompt, LLMPredictor, ServiceContext
)
import json
import openai
from langchain import OpenAI
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine

openai.api_key = os.getenv("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")

""" function is used to configure the settings of a Streamlit page. The function takes a number of arguments, 
including the page title, the page icon, the layout, and the initial sidebar state.
The page_title argument is the title of the page, which will be displayed in the browser tab. 
If the page_title argument is set to None, the default title will be used, which is the filename of the script.
The page_icon argument is the page icon, which will be displayed in the browser tab. The page_icon argument can be a string, an image, or None. 
If the page_icon argument is set to None, no icon will be displayed. The layout argument specifies the layout of the page. 
wide: The page will use the entire width of the browser window.
The initial_sidebar_state argument specifies the initial state of the sidebar. 
auto: The sidebar will be collapsed on mobile devices and expanded on desktop devices.
The menu_items argument is a dictionary that specifies the menu items that will be displayed on the page. The dictionary keys are the names of the menu items,
 and the dictionary values are the URLs of the menu items.
"""
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# Initialize pytrends

"""The pytrends object is a Python object that can be used to access Google Trends data. The pytrends object is initialized with the hl and tz arguments.
 The hl argument specifies the language of the Google Trends data, and the tz argument specifies the timezone of the 
 Google Trends data. """
pytrends = TrendReq(hl='en-US', tz=360)

# List of initial keywords
initial_keywords = ['Galle Tourism', "Bentota Beach Hotel", 'Koggala Hotels' 'Galle', 'Hotels Galle', 'Resorts Galle','GalleTourist' ]

# Initialize session state - way to store data about a user as they navigate through a web application. 

"""The code you have provided will create two empty DataFrames, data2 and data3, in the session state. 
The session state is a way to store data about a user as they navigate through a web application
The first line of code checks if the key data2 is in the session state. If it is not, the code creates a new DataFrame and stores it in the session state. The second line of code does the same thing for the key data3.

The next line of code creates four tabs.
The next line of code creates an expander with three columns. The columns will be used to display 
the DataFrames data2 and data3.
"""
if 'data2' not in st.session_state:
    st.session_state['data2'] = pd.DataFrame()

if 'data3' not in st.session_state:
    st.session_state['data3'] = pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["Search Query Data Analytics and Forecasting", "Sentimental Analysis", "Price Optimization", "Chatbot"])

with st.expander("data"):
    col1, col2, col3 =  st.columns(3)



#####################   tab1 #@######################################################


# with tab1:
    # Create a for keyword selection
    """The code you have provided will create a multiselect widget in the tab1 tab. 
    The multiselect widget will allow the user to select one or more of the keywords 
    in the list initial_keywords. The selected keywords will be stored in the session 
    state as the variable selected_keywords."""
selected_keywords = tab1.multiselect('Select existing keywords', initial_keywords)


# When keywords are selected, fetch data from Google Trends and display it
if tab1.button('Fetch Google Trends data for selected keywords'):
    # Define the payload
    kw_list = selected_keywords

    # Get Google Trends data
    """The code pytrends.build_payload(kw_list, timeframe='today 5-y') is used to 
    build a payload for Google Trends data. The payload is a dictionary that
      contains the keywords and timeframe for the Google Trends data.
      The kw_list parameter is a list of keywords that will be used to fetch Google Trends data. The timeframe parameter specifies the timeframe for the Google Trends data. The timeframe can be specified in a number of different ways, including:

today 5-y: This will fetch Google Trends data for the past 5 years.
2022-01-01 2022-03-01: This will fetch Google Trends data for the month of January and February 2022.
all: This will fetch Google Trends data for all time."""
    pytrends.build_payload(kw_list, timeframe='today 5-y')

    # Get interest over time
    data = pytrends.interest_over_time()
    if not data.empty:
        data = data.drop(labels=['isPartial'],axis='columns')

        # Save the data to the session state
        if 'data' not in st.session_state:

# st.session_state['data'] = pd.DataFrame()
            st.session_state['data'] = data
if 'data' in st.session_state:
    col1.write("## Trends Data")

    col1.write(st.session_state['data'])







#####################   tab2 #@######################################################

# with tab2:
    # Upload file
"""The if statement is used to check if the file has been uploaded. If it has been uploaded, the code will execute the following code. 
This is because the file is already stored in the session state and does not need to be recreated.The st.session_state variable is a 
dictionary that contains the session state data. The key data2 is used to store the DataFrame data2. The data2 DataFrame can be used 
to store any data that needs to be persisted across requests.
The col2.write() function is used to write text to the expander. The st.session_state['data2'] variable is used to get the DataFrame 
data2 from the session state. The data2 DataFrame is then written to the expander."""
uploaded_file = tab2.file_uploader("Upload scraped data for reviews")
if uploaded_file is not None:
    st.session_state['data2'] = pd.read_csv(uploaded_file)
    col2.write("## Sentimental Data")
    col2.write(st.session_state['data2'])
    



#####################   tab1 #@######################################################

# with tab3:
    # Upload file 2

uploaded_file2 = tab3.file_uploader("Upload scraped data for prices")
if uploaded_file2 is not None:
    st.session_state['data3'] = pd.read_csv(uploaded_file2)
    
    col3.write("## Pricing Data")
    
    col3.write(st.session_state['data3'])
    
  


# with tab4:





if tab4.button('Save data and create index'):
    # Check if the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')

    # Save the data from session state to CSV files
    if 'data' in st.session_state:
        st.session_state['data'].to_csv('data/data.csv')
        st.success('Data saved successfully in data/data.csv')

    if not st.session_state['data2'].empty:
        st.session_state['data2'].to_csv('data/data2.csv')
        st.success('Data2 saved successfully in data/data2.csv')

    if not st.session_state['data3'].empty:
        st.session_state['data3'].to_csv('data/data3.csv')
        st.success('Data3 saved successfully in data/data3.csv')

    documents = SimpleDirectoryReader('data').load_data()
    index = GPTVectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    if "query_engine" not in st.session_state:
        st.session_state.query_engine = query_engine

tab4.write("Chat Bot")
ques = tab4.text_input("Ask Question")
ask = tab4.button("Submit Question")

if ask:
    response = st.session_state.query_engine.query(ques)
    st.write(response) 


