from matplotlib.pyplot import plot
import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import plotly.express as px
import io

st.set_page_config(page_title="Market Basket Analysis", layout="wide")

st.title("Market Basket Analysis App")
st.write("Upload your transaction CSV file to generate association rules.")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        st.subheader("Data Preview")
        st.dataframe(df)
        
        st.subheader("Select Columns")

        order_col = st.selectbox(
          "Select Order ID Column",
         options=df.columns
        )

        item_col = st.selectbox(
        "Select Item Column",
        options=df.columns
        )
        
        st.subheader("Top 10 Most Ordered Products")

        # Split items into rows
        exploded_df = df.assign(Items=df["Items"].str.split(", ")).explode("Items")

        # Count frequency
        top_products = exploded_df["Items"].value_counts().head(10)

        top_products_df = top_products.reset_index()
        top_products_df.columns = ["Product", "Order Count"]

        st.dataframe(top_products_df)

        st.bar_chart(top_products.sort_values(ascending=True))
        
        #Create Basket Matrix (One-Hot Encoding)
        basket = (exploded_df.assign(value=1).pivot_table(index="OrderID", columns="Items", values="value", fill_value=0))
        
        #Make sure values are 0/1:
        basket = basket.astype(bool)
        
        #Run Apriori
        frequent_itemsets = apriori(basket,
        min_support=0.01,   # adjust if needed
        use_colnames=True
        )
        
        number = st.number_input(
            "Enter a number",
            min_value=1,
            max_value=1000,
            value=10,
            step=1
        )

        st.write("You entered:", number)
        
        #Generate Association Rules
        rules = association_rules(frequent_itemsets,metric="lift",min_threshold=1)
        
        
        #Sort and Get Top Rules
        top_10_rules = (rules.sort_values(by="support", ascending=False).head(number))
        
        # Convert frozensets to readable text
        top_10_rules["antecedents"] = top_10_rules["antecedents"].apply(
            lambda x: ", ".join(list(x))
        )

        top_10_rules["consequents"] = top_10_rules["consequents"].apply(
            lambda x: ", ".join(list(x))
        )

        #output
        # Create a new DataFrame with only the columns of interest for support and lift
        top_10_rules = top_10_rules[[
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift"
        ]]

        
        
        # add a dropdown to select support lift or confidence
        metric = st.selectbox(
        "Select Metric to Display",
        options=["support", "lift", "confidence"]
        )
        
        # Filter the top_10_rules DataFrame based on the selected metric
        st.subheader(f"Top Product Combinations of {metric}")
        st.dataframe(top_10_rules[["antecedents", "consequents", metric]])
        

        import plotly.express as px
        import seaborn as sns
        import matplotlib.pyplot as plt

        #adding dropdown for x and y axis
        x_axis = st.selectbox(
        "Select X-Axis Metric",
        options=["support", "lift", "confidence"]
        )

        y_axis = st.selectbox(
        "Select Y-Axis Metric",
        options=["support", "lift", "confidence"]
        )

        
        #Lift vs Confidence
        fig = px.scatter(
        top_10_rules,
        x=x_axis,
        y=y_axis,
        size="support",
        hover_data=["antecedents", "consequents"],
        title=f"{x_axis.capitalize()} vs {y_axis.capitalize()}"
        )

        st.plotly_chart(fig, width="stretch")
        
    except Exception as e:
        st.error(f"Error: {e}")




#  use "streamlit run app.py" to run the app in terminal



