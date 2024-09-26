using System.Runtime.CompilerServices;
using Microsoft.Data.SqlClient;
using ContosoSuitesWebAPI.Entities;
using Microsoft.SemanticKernel;
using System.ComponentModel;

namespace ContosoSuitesWebAPI.Services;

public class DatabaseService : IDatabaseService
{

    [KernelFunction]
    [Description("Get all hotels.")]
    public async Task<IEnumerable<Hotel>> GetHotels()
    {
        var sql = "SELECT HotelID, HotelName, City, Country FROM dbo.Hotel";
        using var conn = new SqlConnection(
            connectionString: Environment.GetEnvironmentVariable("SQLCONNSTR_ContosoSuites")!
        );
        conn.Open();
        using var cmd = new SqlCommand(sql, conn);
        using var reader = await cmd.ExecuteReaderAsync();
        var hotels = new List<Hotel>();
        while (await reader.ReadAsync())
        {
            hotels.Add(new Hotel
            {
                HotelID = reader.GetInt32(0),
                HotelName = reader.GetString(1),
                City = reader.GetString(2),
                Country = reader.GetString(3)
            });
        }
        conn.Close();

        return hotels;
    }

    [KernelFunction]
    [Description("Get bookings missing hotel rooms.")]
    public async Task<IEnumerable<Booking>> GetBookingsMissingHotelRooms()
    {
        var sql = """
            SELECT
                b.BookingID,
                b.CustomerID,
                b.HotelID,
                b.StayBeginDate,
                b.StayEndDate,
                b.NumberOfGuests
            FROM dbo.Booking b
            WHERE NOT EXISTS
                (
                    SELECT 1
                    FROM dbo.BookingHotelRoom h
                    WHERE
                        b.BookingID = h.BookingID
                );
            """;
        using var conn = new SqlConnection(
            connectionString: Environment.GetEnvironmentVariable("SQLCONNSTR_ContosoSuites")!
        );
        conn.Open();
        using var cmd = new SqlCommand(sql, conn);
        using var reader = await cmd.ExecuteReaderAsync();
        var bookings = new List<Booking>();
        while (await reader.ReadAsync())
        {
            bookings.Add(new Booking
            {
                BookingID = reader.GetInt32(0),
                CustomerID = reader.GetInt32(1),
                HotelID = reader.GetInt32(2),
                StayBeginDate = reader.GetDateTime(3),
                StayEndDate = reader.GetDateTime(4),
                NumberOfGuests = reader.GetInt32(5)
            });
        }
        conn.Close();
  
        return bookings;
    }

    [KernelFunction]
    [Description("Get bookings with multiple hotel rooms.")]
    public async Task<IEnumerable<Booking>> GetBookingsWithMultipleHotelRooms()
    {
        var sql = """
            SELECT
                b.BookingID,
                b.CustomerID,
                b.HotelID,
                b.StayBeginDate,
                b.StayEndDate,
                b.NumberOfGuests
            FROM dbo.Booking b
            WHERE
                (
                    SELECT COUNT(1)
                    FROM dbo.BookingHotelRoom h
                    WHERE
                        b.BookingID = h.BookingID
                ) > 1;
            """;
        using var conn = new SqlConnection(
            connectionString: Environment.GetEnvironmentVariable("SQLCONNSTR_ContosoSuites")!
        );
        conn.Open();
        using var cmd = new SqlCommand(sql, conn);
        using var reader = await cmd.ExecuteReaderAsync();
        var bookings = new List<Booking>();
        while (await reader.ReadAsync())
        {
            bookings.Add(new Booking
            {
                BookingID = reader.GetInt32(0),
                CustomerID = reader.GetInt32(1),
                HotelID = reader.GetInt32(2),
                StayBeginDate = reader.GetDateTime(3),
                StayEndDate = reader.GetDateTime(4),
                NumberOfGuests = reader.GetInt32(5)
            });
        }
        conn.Close();
  
        return bookings;
    }

    [KernelFunction]
    [Description("Get bookings for hotels.")]
    public async Task<IEnumerable<Booking>> GetBookingsForHotel(int hotelId)
    {
        var sql = "SELECT BookingID, CustomerID, HotelID, StayBeginDate, StayEndDate, NumberOfGuests FROM dbo.Booking WHERE HotelID = @HotelID";
        using var conn = new SqlConnection(
            connectionString: Environment.GetEnvironmentVariable("SQLCONNSTR_ContosoSuites")!
        );
        conn.Open();
        using var cmd = new SqlCommand(sql, conn);
        cmd.Parameters.AddWithValue("@HotelID", hotelId);
        using var reader = await cmd.ExecuteReaderAsync();
        var bookings = new List<Booking>();
        while (await reader.ReadAsync())
        {
            bookings.Add(new Booking
            {
                BookingID = reader.GetInt32(0),
                CustomerID = reader.GetInt32(1),
                HotelID = reader.GetInt32(2),
                StayBeginDate = reader.GetDateTime(3),
                StayEndDate = reader.GetDateTime(4),
                NumberOfGuests = reader.GetInt32(5)
            });
        }
        conn.Close();

        return bookings;
    }

    [KernelFunction]
    [Description("Get bookings by hotel and minimum date.")]
    public async Task<IEnumerable<Booking>> GetBookingsByHotelAndMinimumDate(int hotelId, DateTime dt)
    {
        var sql = "SELECT BookingID, CustomerID, HotelID, StayBeginDate, StayEndDate, NumberOfGuests FROM dbo.Booking WHERE HotelID = @HotelID AND StayBeginDate >= @StayBeginDate";
        using var conn = new SqlConnection(
            connectionString: Environment.GetEnvironmentVariable("SQLCONNSTR_ContosoSuites")!
        );
        conn.Open();
        using var cmd = new SqlCommand(sql, conn);
        cmd.Parameters.AddWithValue("@HotelID", hotelId);
        cmd.Parameters.AddWithValue("@StayBeginDate", dt);
        using var reader = await cmd.ExecuteReaderAsync();
        var bookings = new List<Booking>();
        while (await reader.ReadAsync())
        {
            bookings.Add(new Booking
            {
                BookingID = reader.GetInt32(0),
                CustomerID = reader.GetInt32(1),
                HotelID = reader.GetInt32(2),
                StayBeginDate = reader.GetDateTime(3),
                StayEndDate = reader.GetDateTime(4),
                NumberOfGuests = reader.GetInt32(5)
            });
        }
        conn.Close();

        return bookings;
    }
}
