namespace ContosoSuitesWebAPI.Services;

public interface ICosmosService
{
    Task<IEnumerable<Customer>> GetCustomersByName(string name);
    Task<IEnumerable<Customer>> GetCustomersByLoyaltyTier(string loyaltyTier);
    Task<IEnumerable<Customer>> GetCustomersWithStaysAfterDate(DateTime dt);
}