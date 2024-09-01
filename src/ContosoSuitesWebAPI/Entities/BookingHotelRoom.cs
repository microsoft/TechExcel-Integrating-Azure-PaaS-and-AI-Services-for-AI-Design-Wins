namespace ContosoSuitesWebAPI.Entities;
public class BookingHotelRoom
{
    public required int BookingHotelRoomID { get; set; }
    public required int BookingID { get; set; }
    public required int HotelRoomID { get; set; }
}
