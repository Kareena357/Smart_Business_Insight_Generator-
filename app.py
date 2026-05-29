import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
from google import genai

USERNAME = "Kareena"
PASSWORD = "1234"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type = "password"
    )
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful")
        else:
            st.error("Invalid Username or Password ")

client= genai.Client(
    api_key="AIzaSyD2AdQjcnzlAVwONIsfO9TPT2FHj373XTY"
)

# Title
if not st.session_state.logged_in:

        login()

        st.stop()

st.title("AI Data Analyst")

# Upload file
uploaded_file = st.file_uploader(
    "Upload Excel or CSV File",
    type=["csv", "xlsx"]
)
@st.cache_data
def load_data(upload_file):

    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    else:
        return pd.read_excel(uploaded_file)
# Run only if file uploaded
if uploaded_file is not None:

    # Read dataset
    df = load_data(uploaded_file)
    filtered_df = df.copy()
    st.sidebar.header("Filters")

    selected_region =st.sidebar.selectbox(
        "Select Region",
        ['All'] +list(df['Region'].unique())
    )

    selected_product = st.sidebar.selectbox(
        "Select Product",
        ['All'] + list(df['Product'].unique())
    
    )
    selected_salesperson = st.sidebar.selectbox(
        "Select Salesperson",
        ['All']+list(df['SalesPerson'].unique())
    )
    # Apply Filters




    if selected_region != "All":

        filtered_df = filtered_df[
        filtered_df['Region'] == selected_region
    ]


    if selected_product != "All":

        filtered_df = filtered_df[
        filtered_df['Product'] == selected_product
    ]


    if selected_salesperson != "All":

        filtered_df = filtered_df[
        filtered_df['SalesPerson'] == selected_salesperson
    ]
    # Show dataset preview
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head())
    total_revenue = df['Revenue'].sum()
    total_profit = df['Profit'].sum()
    total_cost  = df['Cost'].sum()
    best_product =filtered_df.groupby(
        'Product'
    )['Revenue'].sum().idxmax()
    best_region = filtered_df.groupby(
        'Region'
    )['Revenue'].sum().idxmax()
    #KPI CArds
    col1,col2= st.columns(2)
    col3,col4 =st.columns(2)
    col5=st.container()
    col1.metric(
        "Total Revenue",
        f"${total_revenue:,.0f}"
    )
    col2.metric(
        "Total Profit",
        f"${total_profit:,.0f}"
    )
    col3.metric(
        "Total Cost",
        f"${total_cost:,.0f}"
    )
    col4.metric(
        "Best Product",
        best_product
     )
    col5.metric(
        "Best Region",
        best_region
    )
    # Show column names
    st.subheader("Columns")
    st.write(filtered_df.columns)

    # Show charts
    st.subheader("Data Chart")

    numeric_cols = filtered_df.select_dtypes(include='number').columns

    if len(numeric_cols) > 0:
        st.line_chart(filtered_df[numeric_cols])

    st.subheader("Revenue by Project")

    region_revenue = filtered_df.groupby(
        'Region'
    )['Revenue'].sum()
    st.bar_chart(region_revenue)

    st.subheader("Profit by Product")

    profit_product = filtered_df.groupby(
        'Product'
    )['Profit'].sum()
    st.bar_chart(profit_product)

    st.subheader("Profit vs Revenue")
   
    st.scatter_chart(
        filtered_df,
        x='Revenue',
        y= 'Profit'
    )

    st.subheader("Revenue Share by Product")
    product_revenue=filtered_df.groupby(
        'Product'

    )['Revenue'].sum()
    fig, ax = plt.subplots()
    ax.pie(
        product_revenue,
        labels= product_revenue.index,
        autopct='%1.1f%%'
    )
    st.pyplot(fig)

    # Question input
    question = st.text_input(
        "Ask a question about your data"
    )

    # Run AI if question entered
    # Run AI if question entered
# Run AI if question entered
if question != "":

    prompt = f"""
    You are a professional business data analyst.

    Dataset (sample):
    {filtered_df.head(50).to_string()}

    User Question:
    {question}

    Instructions:
    - Use only given dataset
    - Be concise and professional
    - Give insights, trends, and recommendations
    - Give solution , explain problems and give suggestions
    
    """

    try:
        with st.spinner("Analyzing data..."):

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

        st.subheader("AI Insight")
        st.write(response.text)

        # Download AI result
        st.download_button(
            label="Download AI Insight",
            data=response.text,
            file_name="AI_Insight_Report.txt",
            mime="text/plain"
        )

        # Download filtered CSV
        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Filtered Data CSV",
            data=csv,
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"AI Error: {e}")
        
