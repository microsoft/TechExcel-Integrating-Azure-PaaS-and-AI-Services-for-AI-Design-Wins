namespace ContosoSuitesWebAPI.Services
{
    public interface IVectorizationService
    {
        Task<ReadOnlyMemory<float>> GetEmbeddings(string text); 
    }
}
