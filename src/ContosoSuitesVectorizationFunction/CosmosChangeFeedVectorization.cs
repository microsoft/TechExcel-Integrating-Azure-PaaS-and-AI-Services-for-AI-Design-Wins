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
    public class CosmosChangeFeedVectorization
    {
        private readonly ILogger _logger;
        private readonly EmbeddingClient _embeddingClient;
        private const string DatabaseName = "ContosoSuites";
        private const string ContainerName = "MaintenanceTasks";

        public CosmosChangeFeedVectorization(ILoggerFactory loggerFactory)
        {
            var endpointUrl = Environment.GetEnvironmentVariable("AzureOpenAIEndpont");
            if (string.IsNullOrEmpty(endpointUrl))
                throw new ArgumentNullException("AzureOpenAIEndpont", "AzureOpenAIEndpont is required to run this function.");

            var azureOpenAIKey = Environment.GetEnvironmentVariable("AzureOpenAIKey");
            if (string.IsNullOrEmpty(azureOpenAIKey))
                throw new ArgumentNullException("AzureOpenAIKey", "AzureOpenAIKey is required to run this function.");

            var deploymentName = Environment.GetEnvironmentVariable("DeploymentName");
            if (string.IsNullOrEmpty(deploymentName))
                throw new ArgumentNullException("DeploymentName", "DeploymentName is required to run this function.");

            _logger = loggerFactory.CreateLogger<CosmosChangeFeedVectorization>();
            var oaiEndpoint = new Uri(endpointUrl);
            var credentials = new AzureKeyCredential(azureOpenAIKey);
            var openAIClient = new AzureOpenAIClient(oaiEndpoint, credentials);
            _embeddingClient = openAIClient.GetEmbeddingClient(deploymentName);
            
        }

        [Function("VectorizeMaintenanceTasks")]
        [CosmosDBOutput(DatabaseName, ContainerName, Connection = "CosmosDBConnectionString")]
        public object Run([CosmosDBTrigger(
            databaseName: DatabaseName,
            containerName: ContainerName,
            Connection = "CosmosDBConnectionString",
            LeaseContainerName = "leases",
            CreateLeaseContainerIfNotExists = true)] IReadOnlyList<MaintenanceTask> input)
        {
            var documentsToVectorize = input.Where(t => t.Type != "Vectorized");
            if (documentsToVectorize.Count() == 0) return null;

            foreach (var task in documentsToVectorize)
            {
                try
                {
                    // Generate the content vector for the maintenance task.
                    var embedding = _embeddingClient.GenerateEmbedding(task.Details);
                    var requestVector = embedding.Value.Vector;

                    // Add the vector embeddings to the maintenance task and mark it as vectorized.
                    task.RequestVector = requestVector.ToArray();
                    task.Type = "Vectorized";
                    _logger.LogInformation($"Generated vector embeddings for maintenance task {task.Id}");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Error generating vector embeddings for maintenance task {task.Id}");
                }
            }

            // Write the updated documents back to Cosmos DB.
            return input;
        }
    }

    /// <summary>
    /// Represents a maintenance task.
    /// </summary>
    public class MaintenanceTask
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
