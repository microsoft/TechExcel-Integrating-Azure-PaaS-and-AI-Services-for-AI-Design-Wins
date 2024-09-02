using ContosoSuitesWebAPI.Entities;

namespace ContosoSuitesWebAPI.Services
{
    public interface IVectorizationService
    {
        Task<ReadOnlyMemory<float>> GetEmbeddings(string text); 
        Task<List<VectorSearchResult>> ExecuteVectorSearch(float[] queryVector, int count = 5);
    }
}
