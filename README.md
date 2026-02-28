#  AI Coding Agent with Tool Calling

A sophisticated **Gemini-powered CLI agent** that leverages Google's Gemini API to autonomously execute file operations and Python code via a structured tool-calling interface. The agent can list directories, read files, write files, and execute Python scripts—all in response to natural language commands.

---

##  Key Features

- ** Multi-turn Agent Loop**: Maintains conversation history and iteratively calls functions until reaching a final answer (max 20 iterations).
- **Structured Tool Calling**: Four core tools with schema validation via Google's `genai` library:
  - `get_files_info` – list directory contents with metadata
  - `get_file_content` – read file contents (with truncation at 10k chars)
  - `run_python_file` – execute Python scripts with optional arguments
  - `write_file` – create/overwrite files safely
- **Security**: All paths are normalized and validated to stay within a designated working directory (`./calculator`).
- **Integrated Calculator**: Ships with a working infix expression evaluator supporting operator precedence (`+`, `-`, `*`, `/`).
- **Comprehensive Tests**: Unit tests for the calculator and integration tests for each tool.

---

## Quick Start

### Prerequisites
- Python 3.8+
- `uv` (or `pip` for package management)
- A valid `GEMINI_API_KEY` environment variable

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd meow

# Install dependencies
uv sync
# or: pip install -r requirements.txt
```

### Basic Usage

```bash
# Ask the agent to list the calculator directory
uv run main.py "list the contents of calculator"

# Ask it to read a file
uv run main.py "show me the contents of calculator/main.py"

# Ask it to run the calculator
uv run main.py "calculate 3 + 7 * 2"

# Enable verbose output to see function calls
uv run main.py "calculate 3 + 7 * 2" --verbose
```

---

##  Architecture

### Core Components

#### `main.py` – Agent Entry Point
The heartbeat of the system. It:
1. Parses user input from CLI arguments
2. Initializes conversation history
3. Calls the Gemini API with available tools
4. Extracts function calls from the model's response
5. Dispatches them via `call_function`
6. Feeds results back to the model
7. Repeats until a final answer or 20 iterations

#### `functions.py` – Tool Implementations
A unified module containing all four tool functions plus their schema declarations. Each function:
- Accepts a `working_directory` parameter
- Uses `os.path.normpath()` and `os.path.commonpath()` to prevent path traversal attacks
- Returns human‑readable success/error messages

**Schemas** define the tool interface for Gemini:
```python
schema_get_files_info
schema_get_file_content
schema_run_python_file
schema_write_file
available_functions  # types.Tool wrapping all schemas
```

#### `call_function.py` – Tool Dispatcher
Maps function names to implementations and:
- Validates the requested function exists
- Injects `working_directory="./calculator"`
- Wraps results in `types.Content` for the agent loop
- Returns structured response objects

#### `prompts.py` – System Instruction
Provides the model with a clear directive:
> "You are a helpful AI coding agent. When a user makes a request that matches one of the available operations, respond with a function call instead of text."

#### `config.py` – Configuration
Houses settable constants like `MAX_FILE_CHARS = 10000` to limit file read sizes.

---

## Directory Structure

```
.
├── calculator/                 # Working directory for the agent
│   ├── main.py                # CLI calculator script
│   ├── tests.py               # Unit tests for Calculator class
│   ├── lorem.txt              # Sample file for testing
│   └── pkg/
│       ├── calculator.py       # Core infix evaluator (operator precedence)
│       ├── render.py          # JSON output formatter
│       └── morelorem.txt      # Another test file
│
├── functions/                 # Legacy directory (consolidated into functions.py)
│   ├── get_file_content.py
│   ├── get_files_info.py
│   ├── run_python_file.py
│   └── write_file.py
│
├── call_function.py           # Function dispatcher
├── config.py                  # Configuration constants
├── functions.py               # Consolidated tool implementations ⭐
├── main.py                    # Agent loop entry point ⭐
├── prompts.py                 # System prompt for Gemini
├── pyproject.toml             # Project metadata & dependencies
│
├── test_*.py                  # Integration tests
│   ├── test_get_files_info.py
│   ├── test_get_file_content.py
│   ├── test_run_python_file.py
│   └── test_write_file.py
│
└── README.md                  # This file
```

---

## 🔄 Agent Workflow

```
User Input
    ↓
main.py parses CLI args
    ↓
Gemini API call with:
  - User message
  - available_functions (schemas)
  - system_prompt
    ↓
Model Returns Response
    ├─ Text → Print & Exit
    └─ Function Calls → call_function()
        ↓
    Dispatcher validates function name
        ↓
    Execute tool (get_files_info, read, run, write)
        ↓
    Wrap result as types.Content
        ↓
    Add tool response to conversation
        ↓
    Loop back to Gemini (max 20 iterations)
```

---

## 🛠️ Tools in Detail

### `get_files_info(working_directory, directory=".")`
Lists files in a directory relative to the working directory.

**Example:**
```python
get_files_info("./calculator", "pkg")
# Output:
# - calculator.py: file_size=1234 bytes, is_dir=False
# - render.py: file_size=567 bytes, is_dir=False
# - __pycache__: file_size=4096 bytes, is_dir=True
```

**Security:** Validates path stays within the working directory.

---

### `get_file_content(working_directory, file_path)`
Reads file contents, truncated at `MAX_FILE_CHARS` (10,000 by default).

**Example:**
```python
get_file_content("./calculator", "main.py")
# Returns the full contents of main.py
# If exceeded char limit, marks with: [...File "..." truncated at 10000 characters]
```

**Security:** Prevents reading files outside the working directory; validates the target is a regular file.

---

### `run_python_file(working_directory, file_path, args=None)`
Executes a Python script with optional arguments. Captures stdout, stderr, and exit code.

**Example:**
```python
run_python_file("./calculator", "main.py", ["3 + 5"])
# Output:
# STDOUT:
# {"expression": "3 + 5", "result": 8}
```

**Security:** Validates file path, enforces `.py` extension, sandboxes execution to the working directory.

---

### `write_file(working_directory, file_path, content)`
Creates or overwrites a file relative to the working directory.

**Example:**
```python
write_file("./calculator", "new_file.txt", "Hello, world!")
# Output:
# Successfully wrote to "new_file.txt" (13 characters written)
```

**Security:** Prevents writing outside the working directory; blocks overwriting directories.

---

## 🧮 Calculator Implementation

The `calculator.pkg.Calculator` class implements the **Shunting Yard algorithm** for infix expression evaluation:

- **Tokenization**: Splits input on whitespace
- **Precedence**: `*`, `/` (level 2) before `+`, `-` (level 1)
- **Left Associativity**: `5 - 3 - 1` evaluates as `(5 - 3) - 1 = 1`
- **Error Handling**: Validates syntax and operand counts

**Example:**
```python
calc = Calculator()
calc.evaluate("3 + 7 * 2")  # Returns 17 (not 20!)
calc.evaluate("(2 + 3) * 4")  # Would work with parentheses (not yet supported)
```

---

## ✅ Testing

### Unit Tests (Calculator)
```bash
cd calculator
python -m unittest tests.py -v
```

Covers:
- Basic arithmetic (+, −, ×, ÷)
- Operator precedence
- Complex expressions
- Edge cases (empty input, invalid tokens, insufficient operands)

### Integration Tests (Tools)
```bash
uv run test_get_files_info.py
uv run test_get_file_content.py
uv run test_run_python_file.py
uv run test_write_file.py
```

Each script validates:
- Success cases (valid paths/operations)
- Security (path traversal attempts blocked)
- Edge cases (non-existent files, truncation)

---

## 🔐 Security Model

All four tools enforce **path sandboxing**:

1. **Absolute Path Normalization**: Convert relative paths to absolute
2. **Common Path Validation**: Ensure the target shares a common prefix with the working directory
3. **Type Checks**: Confirm files are regular files (not directories) and scripts end in `.py`

**Example Block:**
```python
working_dir_abs = os.path.abspath(working_directory)
target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
valid_target = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
if not valid_target:
    return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
```

This prevents:
- `../../../etc/passwd` attacks
- Absolute path escapes like `/tmp/malicious.txt`
- Symlink traversal within the sandbox

---

## 📝 Example Session

```bash
$ uv run main.py "Fix the bug: 3 + 7 * 2 shouldn't be 20." --verbose
 - Calling function: get_file_content
  - path: calculator/pkg/calculator.py
 -> {"result": "# calculator/pkg/calculator.py\n\nclass Calculator:\n    def __init__(self):\n        self.operators = {..."}
 - Calling function: run_python_file
  - path: calculator/main.py
  - args: ["3 + 7 * 2"]
 -> {"result": "STDOUT:\n{\"expression\": \"3 + 7 * 2\", \"result\": 17}"}

Final response:
The expression "3 + 7 * 2" correctly evaluates to 17. The calculator properly applies operator precedence ...
```

---

## 🚀 Future Enhancements

- **Parentheses Support**: Extend the evaluator to handle `(3 + 4) * 2`
- **More Operations**: Add exponentiation (`**`), modulo (`%`), bitwise ops
- **Better Error Messages**: Include suggestions for common typos
- **File Editor Mode**: Interactive file editing rather than whole-file operations
- **Multi-workspace Support**: Allow switching between different sandboxed directories
- **Conversation Persistence**: Save and load chat history
- **Tool Expansions**: Add web scraping, API calls, database queries

---

## 🛠️ Development

### Running Locally

```bash
# Set your API key
export GEMINI_API_KEY="sk-..."

# Run the agent
uv run main.py "your prompt here" --verbose

# Run tests
uv run test_get_files_info.py
python -m unittest calculator/tests.py
```

### Adding New Tools

1. **Define the schema** in `functions.py`:
   ```python
   schema_my_tool = types.FunctionDeclaration(
       name="my_tool",
       description="...",
       parameters=types.Schema(...)
   )
   ```

2. **Implement the function**:
   ```python
   def my_tool(working_directory, **kwargs):
       # Implementation here
       return result
   ```

3. **Register in `available_functions`**:
   ```python
   available_functions = types.Tool(
       function_declarations=[
           schema_my_tool,  # Add here
           ...
       ]
   )
   ```

4. **Add to `function_map`** in `call_function.py`:
   ```python
   function_map = {
       "my_tool": my_tool,
       ...
   }
   ```

---

## 📦 Dependencies

- **google-genai**: Google's Generative AI SDK for Gemini API calls
- **python-dotenv**: Load environment variables from `.env`
- **Standard Library**: `os`, `subprocess`, `json`, `argparse`, `unittest`

---

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests welcome! This is an active learning project.

---

## 💡 Key Takeaways

This codebase demonstrates:
- **LLM Integration**: How to structure tool schemas and function calling
- **Agentic Loops**: Multi-turn conversation with autonomous tool dispatch
- **Security**: Safe file system operations with path validation
- **Modular Design**: Clear separation between agent logic, tools, and domain logic
- **Testing**: Comprehensive coverage of normal and edge cases

Perfect for learning how to build AI agents that interact with the real world safely and predictably!

---

**Questions?** Check the individual test files for usage examples, or inspect `main.py` to see the agent loop in action.
