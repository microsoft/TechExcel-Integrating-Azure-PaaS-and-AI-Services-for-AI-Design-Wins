using Azure.Identity;
using Microsoft.Azure.Cosmos;
using ContosoSuitesWebAPI.Entities;
using ContosoSuitesWebAPI.Services;
using Microsoft.Data.SqlClient;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddSingleton<ICosmosService, CosmosService>();
builder.Services.AddSingleton<IDatabaseService, DatabaseService>();

builder.Services.AddSingleton<CosmosClient>((_) =>
{
    CosmosClient client = new(
        connectionString: builder.Configuration["AZURE_COSMOS_DB_CONNECTION_STRING"]!
    );
    return client;
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.MapGet("/Customer", async (string searchCriterion, string searchValue) => 
{
    
    // TODO: implement search.
    // TODO: Replace with a call to Cosmos DB.
    var customer = new Customer
    {
        FirstName = "John",
        LastName = "Doe",
        FullName = "John Doe",
        LoyaltyTier = LoyaltyTier.Gold,
        YearsAsMember = 2,
        DateOfMostRecentStay = DateTime.Now.AddDays(-1),
        AverageRating = 4.5
    };
    return customer;
})
    .WithName("GetCustomer")
    .WithOpenApi();

app.MapGet("/Hotels", async () => 
{
    throw new NotImplementedException();
})
    .WithName("GetHotels")
    .WithOpenApi();

app.MapGet("/Hotels/{hotelId}/Bookings/", async (int hotelId) => 
{
    throw new NotImplementedException();
})
    .WithName("GetBookingsForHotel")
    .WithOpenApi();

app.MapGet("/Hotels/{hotelId}/Bookings/{min_date}", async (int hotelId, DateTime min_date) => 
{
    throw new NotImplementedException();
})
    .WithName("GetRecentBookingsForHotel")
    .WithOpenApi();

app.Run();
