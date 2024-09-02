using Azure.AI.OpenAI;

namespace ContosoSuitesWebAPI.Services
{
    public class VectorizationService(AzureOpenAIClient client, IConfiguration configuration) : IVectorizationService
    {
        private readonly AzureOpenAIClient _client = client;
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
    }
}
