namespace ContosoSuitesWebAPI.Entities;
public class HotelRoom
{
    public required int HotelRoomID { get; set; }
    public required int HotelID { get; set; }
    public required string RoomNumber { get; set; }
    public required int HOtelRoomTypeID { get; set; }
}
