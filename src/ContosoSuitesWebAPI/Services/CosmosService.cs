using System.Runtime.CompilerServices;
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;

namespace ContosoSuitesWebAPI.Services;

public class CosmosService : ICosmosService
{
    private readonly CosmosClient _client;
    private Container container
    {
        get => _client.GetDatabase("ContosoSuites").GetContainer("Customers");
    }

    public CosmosService()
    {
        _client = new CosmosClient(
            connectionString: Environment.GetEnvironmentVariable("AZURE_COSMOS_DB_CONNECTION_STRING")!
        );
    }

    public async Task<IEnumerable<Customer>> GetCustomersByName(string name)
    {
        throw new NotImplementedException();
    }

    public async Task<IEnumerable<Customer>> GetCustomersByLoyaltyTier(string loyaltyTier)
    {
        throw new NotImplementedException();
    }

    public async Task<IEnumerable<Customer>> GetCustomersWithStaysAfterDate(DateTime dt)
    {
        throw new NotImplementedException();
    }

    private async Task<IEnumerable<Customer>> ExecuteQuery(FeedIterator<Customer> feed)
    {
        throw new NotImplementedException();
    }
    
}