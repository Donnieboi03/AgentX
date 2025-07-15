# AgentX
# 🧠 Console Assistant – AI-Powered Shell Agent

A terminal-native AI assistant that uses **OpenAI GPT models** with memory, file persistence, and dynamic tool calling. Designed to mimic a real-time command line chatbot that can also run shell commands and respond intelligently based on previous interactions.

---

## ✨ Features

### 🤖 Intelligent Conversation Flow
- Conversational memory stored in `ConsoleAssistant_History.json`
- File-based persistence enables session continuity across runs
- Uses OpenAI's `chat.completions` API with function-calling capabilities (GPT-4 tools support)

### 🛠️ Tool Calling (MCP Integration)
- Calls shell commands through `MCP` (Model-Control Protocol)
- Executes commands like `ls`, `pwd`, `curl`, etc., inside the terminal
- Output is sent back to the AI to influence the next response

### 🧱 Modular Design
- Tool system extensible through the `MCP.call_tool()` method
- Separation of config (`config.json`) and history makes the agent easy to configure and audit

---


