public enum LoyaltyTier
{
    Bronze,
    Silver,
    Gold,
    Platinum
};

public class Customer
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string FullName { get; set; }
    public LoyaltyTier LoyaltyTier { get; set; }
    public int YearsAsMember { get; set; }
    public DateTime DateOfMostRecentStay { get; set; }
    public double AverageRating { get; set; }
}