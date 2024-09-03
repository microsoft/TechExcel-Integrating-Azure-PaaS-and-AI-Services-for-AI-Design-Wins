import requests
import streamlit as st

st.set_page_config(layout="wide")

def handle_query_vectorization(query):
    """Vectorize the query using the Vectorize endpoint."""
    api_endpoint = st.secrets["api"]["endpoint"]
    response = requests.get(f"{api_endpoint}/Vectorize", params={"text": query}, timeout=10, verify=False)
    return response.text

def handle_vector_search(query_vector, count):
    """Perform a vector search using the VectorSearch endpoint."""
    api_endpoint = st.secrets["api"]["endpoint"]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{api_endpoint}/VectorSearch", data=query_vector, params={"count": count}, headers=headers, timeout=10, verify=False)
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
    col1, col2, col3 = st.columns(3)

    with col1:
        query = st.text_input("Search query:", key="query")
    with col2:
        results_count = st.text_input("Number of results to return (0 will return all results):", key="results_count", value=0)
    
    if st.button("Submit"):
        with st.spinner("Performing vector search..."):
            if query:
                # Vectorize the query text.
                # Exercise 3 Task 3 TODO #4: Get the vectorized query text by calling handle_query_vectorization.
                query_vector = handle_query_vectorization(query)
                # Perform the vector search.
                # Exercise 3 Task 3 TODO #5: Get the vector search results by calling handle_vector_search.
                vector_search_results = handle_vector_search(query_vector, results_count)
                # Display the results.
                st.write("## Results")
                # Exercise 3 Task 3 TODO #6: Display the results as a table.
                st.table(vector_search_results.json())
            else:
                st.warning("Please enter a query.")


if __name__ == "__main__":
    main()