import streamlit as st

st.set_page_config(layout="wide")

def main():
    st.write(
    """
    # Contoso Suites Main Page

    This Streamlit dashboard is intended to serve as a proof of concept of Azure OpenAI functionality for Contoso Suites employees.  It is not intended to be a production-ready application.

    Use the navigation bar on the left to navigate to the different pages of the dashboard.

    Pages include:
    1. Chat with Data. Used in Exercise 01.
    2. API Integration. Used in Exercise 02.
    3. Vector Search. Used in Exercise 03.
    4. Call Center. Used in Exercise 04.
    5. Call Center Search. Used in Exercise 04.
    6. Copilot Chat. Used in Exercise 05.
    """
    )

if __name__ == "__main__":
    main()
