namespace ContosoSuitesWebAPI.Entities;
public class Booking
{
    public required int BookingID { get; set; }
    public required int CustomerID { get; set; }
    public required int HotelID { get; set; }
    public required DateTime StayBeginDate { get; set; }
    public required DateTime StayEndDate { get; set; }
    public required int NumberOfGuests { get; set; }
}
