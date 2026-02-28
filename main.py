from call_function import call_function
from call_function import available_functions
from prompts import system_prompt
import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError("GEMINI_API_KEY not found. Make sure it is set in your .env file.")

# Argument parsing
parser = argparse.ArgumentParser(description="Gemini CLI Chatbot")
parser.add_argument("user_prompt", type=str, help="The prompt to send to Gemini")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

# Conversation history
messages = [
    types.Content(
        role="user",
        parts=[types.Part(text=args.user_prompt)]
    )
]

# Create client
client = genai.Client(api_key=api_key)

# Agent loop (max 20 iterations)
for _ in range(20):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=types.Content(
                role="system",
                parts=[types.Part(text=system_prompt)]
            ),
            temperature=0
        ),
    )

    # Add model responses to history
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    # If model wants to call functions
    if response.function_calls:

        function_responses = []

        for function_call in response.function_calls:
            function_call_result = call_function(function_call, verbose=args.verbose)

            if not function_call_result.parts:
                raise RuntimeError("No parts returned from function call.")

            function_response = function_call_result.parts[0].function_response

            if function_response is None or function_response.response is None:
                raise RuntimeError("Invalid function response.")

            function_responses.append(function_call_result.parts[0])

            if args.verbose:
                print(f" - Calling function: {function_call.name}")
                print(f" -> {function_response.response}")

        # Give tool results back to model
        messages.append(types.Content(role="user", parts=function_responses))

    else:
        # No more function calls → final answer
        print("Final response:")
        print(response.text)
        break

else:
    print("Agent stopped after 20 iterations without producing a final answer.")
    exit(1)