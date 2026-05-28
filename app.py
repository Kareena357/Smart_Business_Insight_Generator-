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
    if question != "":

        question_lower = question.lower()
        # Revenue by month
        if "month" in question_lower or "trend" in question_lower:


         # Convert date column
             df['Date'] = pd.to_datetime(df['Date'])

         # Create month column
             df['Month'] = df['Date'].dt.month_name()

             summary = filtered_df.groupby(
              'Month'
             )['Revenue'].sum()

        # Product analysis
        elif "product" in question_lower:
            summary=filtered_df.groupby(
                'Product'
            )['Revenue'].sum().sort_values(
                ascending=False 
            )
        # Region analysis
        elif "region" in question_lower:
            summary=filtered_df.groupby(
                'Region'
            )['Revenue'].sum().sort_values(
                ascending=False
            )
        #Profit analysis 
        elif "profit" in question_lower:
            summary = filtered_df.groupby(
                'Product'
            )['Profit'].sum().sort_values(
                ascending=False
            )
        # Cost analysis
        elif "cost" in question_lower:
            summary= filtered_df.groupby(
               'Product' 
            )['Cost'].sum().sort_values(
                ascending=False
            )
        #SalesPerson analysis
        elif "salesperson" in question_lower:
            summary = filtered_df.groupby(
                'salesperson'

            )['revenue'].sum().sort_values(
                ascending=False
            )
        #Default
        else:
            summary=filtered_df.to_string()
        
        # Convert summary to text
        data_sample = str(summary)

        # Prompt
        prompt = f"""
        You are a  professional business data analyst.

        Dataset Summary:
        {data_sample}

        User Question:
        {question}

        IMPORTANT:
        - Answer only using provided dataset
        - Do not create fake information
        - Analyze products, regions, profit, cost ,revenue, and salesperson if 
        relevant 
        - Give concise business insights
        - Explain trends and patterns 
        - Avoid repeating too many raw numbers
        - Explain possible reasons behind poor performance 
        - If revenue, profit is decreasing , provide recommendations
        - If products perform poorly, suggest improvement stratergies
        -keep answer concise and professional
        """

        # AI response
        with st.spinner("Analyzing data..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            

        st.subheader("AI Insight")

        st.write(response.text)

        st.download_button(
            label = "Download AI Insight",
            data= response.text,
            file_name="AI_Insight_Report.txt",
            mime= "text/plain"
        )
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filetered Data CSV",
            data=csv,
            file_name= "Filtered_Data.csv",
            mime="text/csv"
        )

        