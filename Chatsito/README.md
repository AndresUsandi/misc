# Chatsito AI Coding Assistant

Chatsito is a multi-project solution designed to bring powerful, local Large Language Models (LLMs) into the developer workflow. By leveraging local execution environments like Ollama, Chatsito offers a highly responsive, private, and capable AI pair programmer that integrates deeply with your codebase.

## Solution Architecture

The repository is structured into three primary projects, each handling a distinct layer of the architecture:

1. **[chatsito.Core](./chatsito.Core/README.md)**  
   *The foundational library.* Provides the strongly-typed C# models, global configuration constants, and the network communication logic necessary to interface directly with local LLMs via Ollama APIs.

2. **[chatsito.Web](./chatsito.Web/README.md)**  
   *The backend and standalone UI.* An ASP.NET Core application that acts as a secure proxy API for the IDE extensions. It centralizes tool definitions and hosts an interactive web-based chat interface with real-time streaming capabilities.

3. **[chatsito.VsCode](./chatsito.VsCode/README.md)**  
   *The developer interface.* A Visual Studio Code extension that embeds the AI directly into the IDE. It has deep workspace context, capable of reading files, navigating code graphs, executing terminal commands, and applying intelligent code patches directly to your active editor.

## Getting Started

To learn more about the internal logic, class hierarchies, and specific capabilities of each component, please refer to their respective README files linked above. For additional information, the project-level documents error on the side of providing extensive architectural diagrams and functional summaries.
