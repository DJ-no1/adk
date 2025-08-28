from google.adk.agents import Agent

# Create the root agent
question_agent = Agent(
    name="question",
    model="gemini-2.5-flash",
    description="Question answering agent",
    instruction="""
    You are a helpful assistant that answers questions about the user's preferences.

    Here is some information about the user:
    Name: 
    {user_name}
    Preferences: 
    {user_preferences}
    """,
)