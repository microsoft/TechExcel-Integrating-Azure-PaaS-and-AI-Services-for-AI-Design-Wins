import re
import tiktoken
import streamlit as st



st.set_page_config(layout="wide")

def normalize_text(s):
    """Normalize text for tokenization."""

    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()

    return s

@st.cache_data
def make_cosmos_db_vector_search_request(query_embedding):
    ## TODO: this doesn't work?
    """Create and return a new vector search request. Key assumptions:
    - Query embedding is a list of floats.
    - Cosmos DB endpoint, key, and database name stored in Streamlit secrets."""

    cosmos_endpoint = st.secrets["cosmos"]["endpoint"]
    cosmos_key = st.secrets["cosmos"]["key"]
    cosmos_database_name = st.secrets["cosmos"]["database_name"]

    # Create a CosmosClient
    client = tiktoken.CosmosClient(cosmos_endpoint, cosmos_key)

    # Create a database and a container
    client.create_database(cosmos_database_name)

    # Create a container
    client.create_container(cosmos_database_name, "embeddings")

    # Create and return a new vector search request
    return client.vector_search(cosmos_database_name, "embeddings", query_embedding)


def main():
    """Main function for the call center search dashboard."""

    st.write(
    """
    # Call Center Search

    This Streamlit dashboard is intended to support vector search as part
    of a call center monitoring solution. It is not intended to be a
    production-ready application.
    """
    )

    st.write("## Search for Text")

    ## TODO: incorporate search box and button. Display query results.

if __name__ == "__main__":
    main()
