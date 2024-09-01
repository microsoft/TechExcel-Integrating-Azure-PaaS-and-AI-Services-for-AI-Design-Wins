namespace ContosoSuitesWebAPI.Entities;
public class Customer
{
    public required int CustomerID { get; set; }
    public required string FirstName { get; set; }
    public required string LastName { get; set; }
    public required int MembershipBeginYear { get; set; }
}