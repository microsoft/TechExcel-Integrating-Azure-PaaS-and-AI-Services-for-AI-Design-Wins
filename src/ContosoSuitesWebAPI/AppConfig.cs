internal sealed class AppConfig
{
    /// <summary>
    /// The configuration for the Azure OpenAI chat completion.
    /// </summary>
    /// <remarks>
    /// This is not required when OpenAI configuration is provided.
    /// </remarks>
    public AzureOpenAIConfig? AzureOpenAI { get; set; }

    internal bool IsAzureOpenAIConfigured => this.AzureOpenAI?.DeploymentName is not null;

    /// <summary>
    /// Ensures that the configuration is valid.
    /// </summary>
    internal void Validate()
    {
        ArgumentNullException.ThrowIfNull(this.AzureOpenAI?.Endpoint, nameof(this.AzureOpenAI.Endpoint));
        ArgumentNullException.ThrowIfNull(this.AzureOpenAI?.ApiKey, nameof(this.AzureOpenAI.ApiKey));
    }
    internal sealed class AzureOpenAIConfig
    {
        /// <summary>
        /// Deployment name of the Azure OpenAI resource.
        /// </summary>
        public string? DeploymentName { get; set; }

        /// <summary>
        /// Endpoint of the Azure OpenAI resource.
        /// </summary>
        public string? Endpoint { get; set; }

        /// <summary>
        /// ApiKey to use for the Azure OpenAI chat completion.
        /// </summary>
        public string? ApiKey { get; set; }
    }
}