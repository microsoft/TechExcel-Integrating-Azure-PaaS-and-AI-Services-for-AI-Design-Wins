namespace ContosoSuitesWebAPI.Entities;
public class Hotel
{
    public required int HotelID { get; set; }
    public required string HotelName { get; set; }
    public required string City { get; set; }
    public required string Country { get; set; }
}
