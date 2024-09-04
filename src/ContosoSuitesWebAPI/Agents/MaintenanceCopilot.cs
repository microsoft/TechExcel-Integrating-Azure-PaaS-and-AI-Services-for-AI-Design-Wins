// Exercise 5 Task 2 TODO #1: Add the library references to support Semantic Kernel, Chat Completion,
// and OpenAI Prompt Execution settings declarations.

namespace ContosoSuitesWebAPI.Agents
{
    // Exercise 5 Task 2 TODO #2: Inject the Kernel service into the MaintenanceCopilot class.
    public class MaintenanceCopilot
    {
        // Exercise 5 Task 2 TODO #3: Uncomment the two lines below to declare the Kernel and ChatHistory objects.
        //public readonly Kernel _kernel = kernel;
        //private ChatHistory _history = new();

        public async Task<string> Chat(string userPrompt)
        {
            // Exercise 5 Task 2 TODO #4: Comment out or delete the throw exception line below,
            // and then uncomment the remaining code in the function.
            throw new NotImplementedException();

            //var chatCompletionService = _kernel.GetRequiredService<IChatCompletionService>();

            //var openAIPromptExecutionSettings = new OpenAIPromptExecutionSettings()
            //{
            //    ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
            //};

            //_history.AddUserMessage(userPrompt);

            //var result = await chatCompletionService.GetChatMessageContentAsync(
            //    _history,
            //    executionSettings: openAIPromptExecutionSettings,
            //    _kernel
            //);

            //_history.AddAssistantMessage(result.Content!);

            //return result.Content!;
        }
    }
}
