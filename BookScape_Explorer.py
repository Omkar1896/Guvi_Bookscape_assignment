import streamlit as st
import pymysql
import pandas as pd
import altair as alt

# Function to create a database connection
def create_db_connection():
    return pymysql.connect(
        host="localhost",       # Replace with your MySQL host
        user="root",            # Replace with your MySQL username
        password="Rumki@1819",  # Replace with your MySQL password
        database="books_db",    # Replace with your database name
        cursorclass=pymysql.cursors.DictCursor  # Use DictCursor for dictionary results
    )

# Function to execute a query
def execute_query(query):
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        return {"error": str(e)}

# Function to set the background image
def set_bg_hack_url(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{image_url}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit App
# Title and Background Image
st.set_page_config(page_title="BookScape Explorer", layout="wide")
set_bg_hack_url("https://www.publicdomainpictures.net/pictures/320000/velka/book-background.jpg")  # Replace with a valid image URL

st.title("📚 BookScape Explorer")

# Sidebar with Radio Buttons
with st.sidebar:
    st.header("Choose an Option")
    option = st.radio("Navigation", ["Search", "Extract"])

# Search Functionality
if option == "Search":
    st.header("🔍 Search for a Book")
    book_id = st.text_input("Enter Book ID:")
    if st.button("Submit"):
        if book_id:
            query = f"SELECT * FROM books WHERE id = '{book_id}'"
            result = execute_query(query)
            if result and "error" not in result:
                st.success("Book Found!")
                st.json(result)  # Display book details in JSON format
            else:
                st.error("No book found with the given ID.")
        else:
            st.error("Please enter a valid Book ID.")

# Extract Functionality
if option == "Extract":
    st.header("📊 Extract Data and Visualizations")

    # List of predefined queries
    queries = {
        "Top 5 Most Expensive Books": "SELECT title, retail_price FROM books ORDER BY retail_price DESC LIMIT 5",
        "Books Published by Most Popular Publisher": """
            SELECT publisher, COUNT(*) as book_count
            FROM books
            GROUP BY publisher
            ORDER BY book_count DESC
            LIMIT 1
        """,
        "Books Published After 2000": "SELECT title, published_date FROM books WHERE published_date > '2000-01-01'",
        "Checking Availability of eBooks vs Physical Books": "select count(*) from books_db.test4 WHERE is_ebook = 1",
        "Books Published After 2010 with at Least 500 Pages": """
        select book_id,retail_price,title,authors,published_date,page_count 
        from books_db.test4 where published_date > '2010-01-01' 
        and page_count <= 500
        """,
        "Top 3 Authors with the Most Books":"""
        select authors,title,count(*) as cnt_auth
        from books_db.test4
        group by authors
        order by cnt_auth desc
        limit 4
        """,
        "List Publishers with More than 10 Books": """
        select publisher,count(*) as published_book_count
        from books_db.test4
        group by authors
        having count(*) > 10
        """,
        "Books with More than 3 Authors": """
        SELECT id, title, authors
        FROM books_db.test4
        WHERE LENGTH(authors) - LENGTH(REPLACE(authors, ',', '')) + 1 > 3;
        """,
        "Books with the Same Author Published in the Same Year": """
        SELECT 
        authors, 
        published_date, 
        GROUP_CONCAT(title SEPARATOR ', ') AS book_titles,
        COUNT(*) AS book_count
        FROM books_db.test4
        GROUP BY authors, published_date
        HAVING COUNT(*) > 1
        """,
        "Books with a Specific Keyword in the Title": """
        Select title from
        books_db.test4
        Where title like '%Python%'
        """
    }                                                      

    # Display queries in a selectbox
    query_option = st.selectbox("Select a Query to Execute", list(queries.keys()))

    if st.button("Run Query"):
        query = queries[query_option]
        result = execute_query(query)

        # Handle query result
        if result and "error" not in result:
            st.success("Query executed successfully!")

            # Convert result to DataFrame
            df = pd.DataFrame(result)

            # Display data or visualizations based on query
            st.write("### Query Result:")
            st.dataframe(df)

            # Add a visualization if applicable
            if query_option == "Top 5 Most Expensive Books":
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X("title", sort="-y", title="Book Title"),
                    y=alt.Y("retail_price", title="Price"),
                    tooltip=["title", "retail_price"]
                ).properties(title="Top 5 Most Expensive Books")
                st.altair_chart(chart, use_container_width=True)

            elif query_option == "Books Published by Most Popular Publisher":
                st.write("### Most Popular Publisher")
                st.json(result)

            elif query_option == "Books Published After 2000":
                chart = alt.Chart(df).mark_circle(size=60).encode(
                    x=alt.X("published_date:T", title="Published Date"),
                    y=alt.Y("title", title="Book Title"),
                    tooltip=["title", "published_date"]
                ).properties(title="Books Published After 2000")
                st.altair_chart(chart, use_container_width=True)

            elif query_option == "Checking Availability of eBooks vs Physical Books":
                st.write("### The count of Ebooks is")
                st.json(result)

            elif query_option == "List Publishers with More than 10 Books":
                st.write("### The Publishers Are")
                st.json(result)

        else:
            st.error(f"An error occurred: {result.get('error')}")

