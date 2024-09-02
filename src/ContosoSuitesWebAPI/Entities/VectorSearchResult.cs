namespace ContosoSuitesWebAPI.Entities
{
    public class VectorSearchResult
    {
        public required int HotelId { get; set; }
        public required string Hotel { get; set; }
        public required string Details { get; set; }
        public required string Source { get; set; }
        public required float SimilarityScore { get; set; }
    }
}
