using ContosoSuitesWebAPI.Entities;

namespace ContosoSuitesWebAPI.Services
{
    public interface IVectorizationService
    {
        Task<float[]> GetEmbeddings(string text); 

        // Exercise 3 Task 3 TODO #1: Uncomment the following line of code to provide an execute a vector search method against Cosmos DB.
        //Task<List<VectorSearchResult>> ExecuteVectorSearch(float[] queryVector, int max_results = 0, double minimum_similarity_score = 0.8);
    }
}
