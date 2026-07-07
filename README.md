# Miscellaneous AI Projects

This repository is a collection of miscellaneous AI-related projects. The repository is currently being populated, and the list of projects will grow over the next few weeks.

## Projects Overview

| Project | Description |
| :--- | :--- |
| [Chatsito](./Chatsito) | A multi-project solution designed to bring local Large Language Models (LLMs) into the developer workflow. |
| [Fixito](./Fixito) | A standalone, lightweight, CLI-based code review assistant designed to analyze Git diffs and commits. |
| Additional projects will be added soon | |

## Chatsito

[Chatsito](./Chatsito) is an AI-powered coding assistant designed to bring local Large Language Models (LLMs) into the developer workflow. By leveraging local execution environments like Ollama, Chatsito offers a highly responsive, private, and capable AI pair programmer that integrates deeply with your codebase.

### Component Architecture

The Chatsito solution is structured into three primary components:

- **[chatsito.Core](./Chatsito/chatsito.Core)**: The foundational library providing strongly-typed C# models, configuration, and API network logic to interface with local Ollama instances.
- **[chatsito.Web](./Chatsito/chatsito.Web)**: An ASP.NET Core backend/UI that acts as a secure API proxy and provides an interactive web-based chat interface.
- **[chatsito.VsCode](./Chatsito/chatsito.VsCode)**: A Visual Studio Code extension that embeds developer controls, allowing the AI to read workspace files, execute terminal commands, and apply code patches.

## Fixito

[Fixito](./Fixito) is a standalone, lightweight, CLI-based code review assistant designed to analyze Git diffs and commits. By connecting to a local LLM server (like Chatsito), it performs private, context-aware code reviews right from your terminal.

### Key Capabilities

- **Git Integration**: Reviews working changes via `git diff` or specific historical commits via `git show`.
- **Autonomous Context Gathering**: Uses a tool execution loop to query files, search symbols, and analyze dependencies, ensuring accurate feedback.
- **Workflow Automation**: Integrates easily with Git pre-commit hooks, CI/CD pipelines, and editor tasks. For detailed integration and configuration instructions, refer to the [Fixito README](./Fixito/README.md).
