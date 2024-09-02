using Azure.AI.OpenAI;
using ContosoSuitesWebAPI.Entities;
using Microsoft.Azure.Cosmos;
using System.Text.Json.Serialization;

namespace ContosoSuitesWebAPI.Services
{
    public class VectorizationService(AzureOpenAIClient openAIClient, CosmosClient cosmosCient, IConfiguration configuration) : IVectorizationService
    {
        private readonly AzureOpenAIClient _client = openAIClient;
        private readonly CosmosClient _cosmosCient = cosmosCient;
        private readonly string _deploymentName = configuration.GetValue<string>("DEPLOYMENT_NAME") ?? "text-embedding-ada-002";

        public async Task<ReadOnlyMemory<float>> GetEmbeddings(string text)
        {
            var embeddingClient = _client.GetEmbeddingClient(_deploymentName);

            try
            {
                // Generate a vector for the provided text.
                var embedding = await embeddingClient.GenerateEmbeddingAsync(text);
                var vector = embedding.Value.Vector;

                // Return the vector embeddings.
                return vector;
            }
            catch (Exception ex)
            {
                throw new Exception($"An error occurred while generating embeddings: {ex.Message}");
            }
        }

        public async Task<List<VectorSearchResult>> ExecuteVectorSearch(float[] queryVector, int count = 0)
        {
            var db = _cosmosCient.GetDatabase(configuration.GetValue<string>("COSMOS_DATABASE_NAME") ?? "ContosoSuites");
            var container = db.GetContainer(configuration.GetValue<string>("MAINTENANCE_REQUESTS_CONTAINER_NAME") ?? "MaintenanceRequests");

            var query = $"SELECT c.hotel_id AS HotelId, c.hotel AS Hotel, c.details AS Details, c.source AS Source, VectorDistance(c.request_vector, [{string.Join(",", queryVector)}]) AS SimilarityScore FROM c";
            query += $" ORDER BY VectorDistance(c.request_vector, [{string.Join(",", queryVector)}])";

            var results = new List<VectorSearchResult>();
            Console.Write($"Executing query/n/n{query}");
            using var feedIterator = container.GetItemQueryIterator<VectorSearchResult>(new QueryDefinition(query));
            while (feedIterator.HasMoreResults)
            {
                foreach(var item in await feedIterator.ReadNextAsync())
                {
                    results.Add(item);
                }
            }
            return count > 0 ? results.Take(count).ToList() : [.. results];

            //throw new NotImplementedException();
        }
    }
}
