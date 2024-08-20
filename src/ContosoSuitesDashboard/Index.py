import streamlit as st

st.set_page_config(layout="wide")

def main():
    st.write(
    """
    # Contoso Suites Main Page

    This Streamlit dashboard is intended to serve as a proof of concept of Azure OpenAI functionality for Contoso Suites employees.  It is not intended to be a production-ready application.

    Use the navigation bar on the left to navigate to the different pages of the dashboard.

    Pages include:
    1. Chat with Data. Used in Exercises 02 through 04.
    2. Call Center. Used in Exercises 05 and 06.
    """
    )

if __name__ == "__main__":
    main()
