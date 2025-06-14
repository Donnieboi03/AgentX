import openai as ai
import subprocess
import json

# Read from file
def read_from_file(FILE):
    try:
        with open(FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading file {FILE}: {e}")
        return []

# Append to end of file
def append_to_file(FILE, content):
    try:
        contents = read_from_file(FILE)
        contents.append(content)
        with open(FILE, 'w') as file:
            json.dump(contents, file, indent=1)
    except Exception as e:
        print(f"Error writing to file {FILE}: {e}")
        return

# Pop from end of file
def pop_from_file(FILE):
    try:
        contents = read_from_file(FILE)
        contents.pop()
        with open(FILE, 'w') as file:
            json.dump(contents, file, indent=1)
    except Exception as e:
        print(f"Error writing to file {FILE}: {e}")
        return

# Message file path
MESSAGE_FILE = "ConsoleAssistant_History.json"
# Config file path
CONFIG_FILE = "config.json"
# Agent Name
NAME = "Assistant"

# Load config file and set API key
CONFIG = read_from_file(CONFIG_FILE)
ai.api_key = CONFIG['api_key'] if 'api_key' in CONFIG else None

# Text is Sent to ChatGpt and ChatGpt Responds
def send_to_chatGPT(message: str):
    # Format the message
    message_dict = {'role': 'user', 'content': message}
    # Write the message to the file
    append_to_file(MESSAGE_FILE, message_dict)
    # Read the file to get the conversation history
    messages = read_from_file(MESSAGE_FILE)
    try:
        # Prepare the messages for the API
        response = ai.chat.completions.create(
            messages = messages,
            model = CONFIG['model'] if 'model' in CONFIG else 'gpt-3.5-turbo',
            max_tokens = CONFIG['max_tokens'] if 'max_tokens' in CONFIG else 512,
            temperature = CONFIG['temperature'] if 'temperature' in CONFIG else 0.5,
            tools = CONFIG['tools'] if 'tools' in CONFIG else None,
            tool_choice= "auto"
        )
        # Get Message
        response_message = response.choices[0].message
        # Default Response Dictionary
        response_dict = {'role': 'assistant', 'content': 'No Response'}
        # Check if the response contains a tool call
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            # Convert each tool call to a plain dictionary
            tool_calls_raw = response_message.tool_calls
            tool_calls_dict = [tool_call.model_dump() for tool_call in tool_calls_raw]
            # Write the assistant's tool_calls message first
            tool_calls_response = {
                "role": "assistant",
                "tool_calls": tool_calls_dict
            }
            append_to_file(MESSAGE_FILE, tool_calls_response)
            
            # create MCP object and tools buffer
            mcp = MCP()
            tool_buffer = []

            # Call each requested tool
            for tool in tool_calls_raw:
                try: 
                    # Get name, args, and output
                    name = tool.function.name
                    args = json.loads(tool.function.arguments)
                    output = mcp.call_tool(name, args)
                # If any tool fails then break
                except Exception as e:
                    pop_from_file(MESSAGE_FILE)
                    print(f"Error: {e}")
                    break

                # Format the tool call response
                tool_response = {
                    'role': 'tool',
                    'tool_call_id': tool.id,
                    'content': output
                }
                # Write the tool response to the file
                append_to_file(MESSAGE_FILE, tool_response)
                # Add tool name, arg, and output to tools buffer
                tool_buffer.append({'name': name, 'arguments': args, 'output': output})

            # Get output of tool calls
            response = '\n'.join(tool['output'] for tool in tool_buffer).strip()
            # Format the response
            response_dict['content'] = response if response else "Action Completed"
        else:        
            # Format the response
            response_dict['content'] = response.choices[0].message.content

        # Write the message to the file
        append_to_file(MESSAGE_FILE, response_dict)
        return response_dict['content']
    # If OpenAI Fails then display error
    except ai.OpenAIError as error:
        print(f"Error: {error}")

class MCP:
    # Get Tool
    def call_tool(self, name: str, args: any):
        if name == "execute_command":
            return self.execute_command(args['command'])

    # Execute a command in the shell and return the output
    def execute_command(self, commands: str):
        try:
            result = subprocess.check_output(commands, shell=True, text=True, timeout=30)
            return result.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"


if __name__ == "__main__":
    while(1):
        print(f"\n{"_" * 50}")
        text = input("\nUser:\n\n")
        if text == 'exit':
            break
        else:
            print(f"\n{"_" * 50}")
            # ChatGpt Responds
            response = send_to_chatGPT(text)
            print(f"\n{NAME}:\n\n{response}")
