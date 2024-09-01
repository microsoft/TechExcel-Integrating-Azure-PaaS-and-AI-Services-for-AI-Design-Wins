import requests
import streamlit as st

st.set_page_config(layout="wide")

@st.cache_data
def get_hotels():
    """Return a list of hotels from the API."""
    api_endpoint = st.secrets["api"]["endpoint"]
    response = requests.get(f"{api_endpoint}/Hotels", timeout=10)
    return response

@st.cache_data
def get_hotel_bookings(hotel_id):
    """Return a list of bookings for the specified hotel."""
    api_endpoint = st.secrets["api"]["endpoint"]
    response = requests.get(f"{api_endpoint}/Hotels/{hotel_id}/Bookings", timeout=10)
    return response

def main():
    """Main function for the Chat with Data Streamlit app."""

    st.write(
    """
    # API Integration via Semantic Kernel

    This Streamlit dashboard is intended to demonstrate how we can use
    the Semantic Kernel library to generate SQL statements from natural language
    queries and display them in a Streamlit app.

    ## Select a Hotel
    """
    )

    # Display the list of hotels as a drop-down list
    hotels_json = get_hotels().json()
    # Reshape hotels to an object with hotelID and hotelName
    hotels = [{"id": hotel["hotelID"], "name": hotel["hotelName"]} for hotel in hotels_json]
    
    selected_hotel = st.selectbox("Hotel:", hotels, format_func=lambda x: x["name"])

    # Display the list of bookings for the selected hotel as a table
    if selected_hotel:
        hotel_id = selected_hotel["id"]
        bookings = get_hotel_bookings(hotel_id).json()
        st.write("### Bookings")
        st.table(bookings)

if __name__ == "__main__":
    main()
