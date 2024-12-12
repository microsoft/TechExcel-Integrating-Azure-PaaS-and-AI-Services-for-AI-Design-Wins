using global::ContosoSuitesWebAPI.Entities;

namespace ContosoSuitesWebAPI.Services;

public interface IDatabaseService
{
    Task<IEnumerable<Hotel>> GetHotels();
    Task<IEnumerable<Booking>> GetBookingsForHotel(int hotelId);
    Task<IEnumerable<Booking>> GetBookingsByHotelAndMinimumDate(int hotelId, DateTime dt);
    Task<IEnumerable<Booking>> GetBookingsMissingHotelRooms();
    Task<IEnumerable<Booking>> GetBookingsWithMultipleHotelRooms();
}