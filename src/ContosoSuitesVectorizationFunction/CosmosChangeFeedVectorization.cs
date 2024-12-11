using Azure;
using Azure.AI.OpenAI;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using OpenAI.Embeddings;
using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ContosoSuites.Functions
{
    /// <summary>
    /// A function that listens for changes to maintenance requests in Cosmos DB and generates vector embeddings for new requests.
    /// </summary>
    public class CosmosChangeFeedVectorization
    {
        private readonly ILogger _logger;
        private readonly EmbeddingClient _embeddingClient;
        const string DatabaseName = "ContosoSuites";
        const string ContainerName = "MaintenanceRequests";

        /// <summary>
        /// Initializes a new instance of the <see cref="CosmosChangeFeedVectorization"/> class.
        /// </summary>
        /// <param name="loggerFactory">The logger factory. This comes from Program.cs as the tie-in to Application Insights.</param>
        /// <exception cref="ArgumentNullException">Thrown if necessary configuration settings are missing.</exception>
        public CosmosChangeFeedVectorization(ILoggerFactory loggerFactory)
        {
            var endpointUrl = Environment.GetEnvironmentVariable("AzureOpenAIEndpoint");
            if (string.IsNullOrEmpty(endpointUrl))
                throw new ArgumentNullException("AzureOpenAIEndpoint", "AzureOpenAIEndpoint is required to run this function.");

            var azureOpenAIKey = Environment.GetEnvironmentVariable("AzureOpenAIKey");
            if (string.IsNullOrEmpty(azureOpenAIKey))
                throw new ArgumentNullException("AzureOpenAIKey", "AzureOpenAIKey is required to run this function.");

            var deploymentName = Environment.GetEnvironmentVariable("EmbeddingDeploymentName");
            if (string.IsNullOrEmpty(deploymentName))
                throw new ArgumentNullException("EmbeddingDeploymentName", "EmbeddingDeploymentName is required to run this function.");

            _logger = loggerFactory.CreateLogger<CosmosChangeFeedVectorization>();
            var oaiEndpoint = new Uri(endpointUrl);
            var credentials = new AzureKeyCredential(azureOpenAIKey);
            var openAIClient = new AzureOpenAIClient(oaiEndpoint, credentials);
            _embeddingClient = openAIClient.GetEmbeddingClient(deploymentName);   
        }

        /// <summary>
        /// Listens for changes to maintenance requests in Cosmos DB and generates vector embeddings for new requests.
        /// </summary>
        [Function("VectorizeMaintenanceRequests")]
        [CosmosDBOutput(DatabaseName, ContainerName, Connection = "CosmosDBConnection")]
        public object Run([CosmosDBTrigger(
            databaseName: DatabaseName,
            containerName: ContainerName,
            Connection = "CosmosDBConnection",
            LeaseContainerName = "leases",
            CreateLeaseContainerIfNotExists = true)] IReadOnlyList<MaintenanceRequest> input)
        {
            var documentsToVectorize = input.Where(t => t.Type != "Vectorized");
            if (documentsToVectorize.Count() == 0) return null;

            foreach (var request in documentsToVectorize)
            {
                try
                {
                    // Combine the hotel and details fields into a single string for embedding.
                    var request_text = $"Hotel: {request.Hotel}\n Request Details: {request.Details}";
                    // Generate a vector for the maintenance request.
                    var embedding = _embeddingClient.GenerateEmbedding(request_text);
                    var requestVector = embedding.Value.Vector;

                    // Add the vector embeddings to the maintenance request and mark it as vectorized.
                    request.RequestVector = requestVector.ToArray();
                    request.Type = "Vectorized";
                    _logger.LogInformation($"Generated vector embeddings for maintenance request {request.Id}");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Error generating vector embeddings for maintenance request {request.Id}");
                }
            }

            // Write the updated documents back to Cosmos DB.
            return input;
        }
    }

    /// <summary>
    /// Represents a maintenance request.
    /// </summary>
    public class MaintenanceRequest
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("type")]
        public string? Type { get; set; }
        
        [JsonPropertyName("hotel_id")]
        public int HotelId {get;set;}
        
        [JsonPropertyName("hotel")]
        public string Hotel { get; set; }

        [JsonPropertyName("source")]
        public string Source { get; set; }

        [JsonPropertyName("date")]
        public DateTime Date { get; set; }

        [JsonPropertyName("details")]
        public string Details { get; set; }
        
        [JsonPropertyName("room_number")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public int? RoomNumber { get; set; }

        [JsonPropertyName("room_numbers_checked")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? RoomNumbersChecked { get; set; }
        
        [JsonPropertyName("meeting_room")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public int? MeetingRoom { get; set; }
        
        [JsonPropertyName("location")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Location { get; set; }

        [JsonPropertyName("request_vector")]
        public float[]? RequestVector { get; set; }
    }
}
