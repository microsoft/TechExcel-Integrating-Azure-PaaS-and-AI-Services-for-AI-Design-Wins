import requests
import streamlit as st

st.set_page_config(layout="wide")

def handle_query_vectorization(query):
    """Vectorize the query using the Vectorize endpoint."""
    api_endpoint = st.secrets["api"]["endpoint"]
    response = requests.get(f"{api_endpoint}/Vectorize", params={"text": query}, timeout=10, verify=False)
    return response.text

def handle_vector_search(query_vector, max_results=5, minimum_similarity_score=0.8):
    """Perform a vector search using the VectorSearch endpoint."""
    api_endpoint = st.secrets["api"]["endpoint"]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{api_endpoint}/VectorSearch", data=query_vector, params={"max_results": max_results, "minimum_similarity_score": minimum_similarity_score}, headers=headers, timeout=10, verify=False)
    return response

def main():
    """Main function for the Vector Search over Maintenance Requests Streamlit page."""

    st.write(
        """
        # Vector Search for Maintenance Requests.

        This Streamlit dashboard is intended to demonstrate how we can use
        the Vector Search to find maintenance requests that are similar to
        a given query.

        ## Enter a Maintenance Request query
        """
    )

    # Await a user message and handle the chat prompt when it comes in.
    # col1 and col2 represent two separate columns in the Streamlit app.
    # This allows us to format the application in a two-column layout.
    col1, col2 = st.columns(2)

    # The "with col1" and "with col2" blocks define the content that will be displayed in each column.
    with col1:
        query = st.text_input("Search query:", key="query")
    with col2:
        max_results = st.text_input("Max results (<=0 will return all results):", key="max_results", value=0)

    minimum_similarity_score = st.slider("Minimum Similarity Score:", min_value=0.0, max_value=1.0, value=0.8, step=0.01)
    
    if st.button("Submit"):
        with st.spinner("Performing vector search..."):
            if query:
                # Vectorize the query text.
                # Exercise 3 Task 3 TODO #4: Get the vectorized query text by calling handle_query_vectorization.
                
                # Perform the vector search.
                # Exercise 3 Task 3 TODO #5: Get the vector search results by calling handle_vector_search.
                
                # Display the results.
                st.write("## Results")
                # Exercise 3 Task 3 TODO #6: Display the results as a table.
                
            else:
                st.warning("Please enter a query.")

if __name__ == "__main__":
    main()