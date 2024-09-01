public enum LoyaltyTier
{
    Bronze,
    Silver,
    Gold,
    Platinum
};

public class Customer
{
    public required string FirstName { get; set; }
    public required string LastName { get; set; }
    public required string FullName { get; set; }
    public LoyaltyTier LoyaltyTier { get; set; }
    public int YearsAsMember { get; set; }
    public DateTime DateOfMostRecentStay { get; set; }
    public double AverageRating { get; set; }
}