using Azure.AI.OpenAI;
using ContosoSuitesWebAPI.Entities;
using Microsoft.Azure.Cosmos;
using System.Globalization;

namespace ContosoSuitesWebAPI.Services
{
    /// <summary>
    /// The vectorization service for generating embeddings and executing vector searches.
    /// </summary>
    public class VectorizationService(AzureOpenAIClient openAIClient, CosmosClient cosmosClient, IConfiguration configuration) : IVectorizationService
    {
        private readonly AzureOpenAIClient _client = openAIClient;
        private readonly CosmosClient _cosmosClient = cosmosClient;
        private readonly string _embeddingDeploymentName = configuration.GetValue<string>("AzureOpenAI:EmbeddingDeploymentName") ?? "text-embedding-ada-002";

        /// <summary>
        /// Translate a text string into a vector embedding.
        /// This uses the embedding deployment name in your configuration, or defaults to text-embedding-ada-002.
        /// </summary>
        public async Task<float[]> GetEmbeddings(string text)
        {
            var embeddingClient = _client.GetEmbeddingClient(_embeddingDeploymentName);

            try
            {
                // Generate a vector for the provided text.
                var embeddings = await embeddingClient.GenerateEmbeddingAsync(text);

                var vector = embeddings.Value.Vector.ToArray();

                // Return the vector embeddings.
                return vector;
            }
            catch (Exception ex)
            {
                throw new Exception($"An error occurred while generating embeddings: {ex.Message}");
            }
        }

        // Exercise 3 Task 3 TODO #2: Uncomment the following code block to execute a vector search query against Cosmos DB.
        ///// <summary>
        ///// Perform a vector search query against Cosmos DB.
        ///// This requires that you have already performed vectorization on your input text using the GetEmbeddings() method.
        ///// </summary>
        //public async Task<List<VectorSearchResult>> ExecuteVectorSearch(float[] queryVector, int max_results = 0, double minimum_similarity_score = 0.8)
        //{
        //    var db = _cosmosClient.GetDatabase(configuration.GetValue<string>("CosmosDB:DatabaseName") ?? "ContosoSuites");
        //    var container = db.GetContainer(configuration.GetValue<string>("CosmosDB:MaintenanceRequestsContainerName") ?? "MaintenanceRequests");

        //    var vectorString = string.Join(", ", queryVector.Select(v => v.ToString(CultureInfo.InvariantCulture)).ToArray());

        //    var query = $"SELECT c.hotel_id AS HotelId, c.hotel AS Hotel, c.details AS Details, c.source AS Source, VectorDistance(c.request_vector, [{vectorString}]) AS SimilarityScore FROM c";
        //    query += $" WHERE VectorDistance(c.request_vector, [{vectorString}]) > {minimum_similarity_score.ToString(CultureInfo.InvariantCulture)}";
        //    query += $" ORDER BY VectorDistance(c.request_vector, [{vectorString}])";

        //    var results = new List<VectorSearchResult>();

        //    using var feedIterator = container.GetItemQueryIterator<VectorSearchResult>(new QueryDefinition(query));
        //    while (feedIterator.HasMoreResults)
        //    {
        //        foreach (var item in await feedIterator.ReadNextAsync())
        //        {
        //            results.Add(item);
        //        }
        //    }
        //    return max_results > 0 ? results.Take(max_results).ToList() : [.. results];
        //}
    }
}
