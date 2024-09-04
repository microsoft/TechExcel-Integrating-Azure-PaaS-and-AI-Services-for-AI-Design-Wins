using Azure.Identity;
using Microsoft.Azure.Cosmos;
using ContosoSuitesWebAPI.Entities;
using ContosoSuitesWebAPI.Services;
using Microsoft.Data.SqlClient;
using Azure.AI.OpenAI;
using Azure;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddSingleton<IDatabaseService, DatabaseService>();
builder.Services.AddSingleton<IVectorizationService, VectorizationService>();

builder.Services.AddSingleton<CosmosClient>((_) =>
{
    CosmosClient client = new(
        connectionString: builder.Configuration["CosmosDBConnectionString"]!
    );
    return client;
});

builder.Services.AddSingleton<AzureOpenAIClient>((_) =>
{
    var endpoint = new Uri(builder.Configuration["AzureOpenAI:Endpoint"]!);
    var credentials = new AzureKeyCredential(builder.Configuration["AzureOpenAI:ApiKey"]!);

    var client = new AzureOpenAIClient(endpoint, credentials);
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

app.MapPost("/Chat", async Task<string> (HttpRequest request) =>
{
    var message = await Task.FromResult(request.Form["message"]);
    
    return "This endpoint is not yet available.";
})
    .WithName("Chat")
    .WithOpenApi();

app.MapGet("/Vectorize", async (string text, [FromServices] IVectorizationService vectorizationService) =>
{
    var embeddings = await vectorizationService.GetEmbeddings(text);
    return embeddings;
})
    .WithName("Vectorize")
    .WithOpenApi();

app.MapPost("/VectorSearch", async ([FromBody] float[] queryVector, [FromServices] IVectorizationService vectorizationService, int max_results = 0, double minimum_similarity_score = 0.8) =>
{
    // Exercise 3 Task 3 TODO #3: Insert code to call the ExecuteVectorSearch function on the Vectorization Service. Don't forget to remove the NotImplementedException.
    throw new NotImplementedException();
})
    .WithName("VectorSearch")
    .WithOpenApi();

app.Run();
