# 🤖 Podcast Agent Bot

[![GitHub top language](https://img.shields.io/github/languages/top/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai?color=1081c2)](https://github.com/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai/search?l=c%23)
![License](https://img.shields.io/github/license/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai?label=license&logo=github&color=f80&logoColor=fff)
![Forks](https://img.shields.io/github/forks/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai.svg)
![Stars](https://img.shields.io/github/stars/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai.svg)
![Watchers](https://img.shields.io/github/watchers/matiasvallejosdev/podcast-agent-gpt-discord-bot-ai.svg)

Experience Podcast Agent Bot in action: [View Demo](https://youtu.be/bBJazG26p0k)

## 📘 Introduction

The Podcast Agent Bot is an innovative Discord bot designed to analyze and summarize podcasts. Utilizing OpenAI's powerful GPT and Whisper models, it offers users a seamless way to interact with audio content, providing insights, summaries, and responses to queries based on the podcast's content.

## 🎯 Purpose

The creation of the Podcast Agent Bot was inspired by the challenge of consuming and retaining the wealth of information available in podcasts. Often, while listening to podcasts, taking notes and revisiting key points later can be cumbersome. This bot simplifies the process by providing tools to summarize, highlight important information, translate content, and offer an interactive Q&A feature based on the podcast, making the wealth of knowledge in podcasts more accessible and engaging.

## ✨ Features

- **Audio Analysis**: Upload your podcast audio files and get a detailed analysis of the content.
- **Transcription**: Convert audio content into text using Whisper for further analysis.
- **Summarization**: Get concise summaries of your podcast episodes, highlighting the key points.
- **Interactive Q&A**: Ask questions about the podcast content and receive accurate answers.
- **Support for Multiple Audio Formats**: Supports mp3, wav, and ogg audio formats.

## 🔧 Interaction Design & Architecture

Podcast Agent Bot integrates real-time WebSocket communication with Discord's API, allowing users to start conversations, upload audio files, and interact with podcast content seamlessly. It harnesses OpenAI's GPT-4 for intelligent chat completion and uses Whisper for accurate audio transcriptions. The bot's memory system ensures continuity in conversations. Commands like `/upload_audio`, `/clear`, and `/summarize` empower users to fully engage with and analyze their favorite podcasts within Discord. This diagram gives a visual overview of the bot's structure and interaction flow.

![Podcast Agent Bot Design System](docs/design-system.png)

## 📥 Installation

To set up the Podcast Agent Bot for development and testing, follow these steps:

1. **Clone the Repository**
   Clone the project to your local machine:

```bash
   git clone https://github.com/your-username/podcast-agent-bot.git
   cd podcast-agent-bot
```

2. **Create a New Discord Bot Application**
   - Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click on "New Application", name your application, and then click "Create".

3. **Generate Your Discord Token**
   - In the Discord Developer Portal, select your application, go to the "Bot" tab, and click "Add Bot".
   - Under the "Token" section, click "Copy" to get your Discord bot token.
   - Set the necessary permissions for your bot to function correctly.

4. **Add Your Environment Variables**
   Configure the environment variables in your system or a `.env` file:

   ```bash
   DISCORD_TOKEN="your_discord_token"
   DISCORD_GUILD_ID=your_guild_id
   DISCORD_GUILD_CHANNEL=your_channel_id
   OPENAI_API_KEY="your_openai_api_key"
   OPENAI_GPTMODEL="gpt-4-turbo-preview"
   OPENAI_TEMPERATURE=0
   OPENAI_TOKENS=4096
   ```

5. **Install Dependencies**
   Run the following command to install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. **Run Your Project**
   Launch the bot with the following command:

   ```bash
   python3 main.py
   ```

**Note:** To run tests, use the `pytest` command in your terminal.

## ❓ How to use it?

### 📖 User Guide

To interact with the Podcast Agent Bot effectively, follow these steps:

1. **Start a New Conversation**: Initiate your interaction with the bot to set the context.
2. **Clear Chat History (if necessary)**: Use the `/clear` command to remove old interactions and start with a clean slate.
3. **Upload Podcast Audio**: Execute the `/upload_audio [file] [language]` command to upload your podcast file in a supported format (mp3, wav, or ogg) for analysis.
4. **Analyze and Interact**: Post-upload, ask the bot specific questions about the podcast's content with the `/ask [question]` command or request a summary using `/summarize`.

### ⌨️ Commands

Utilize the following commands to interact with the bot:

- `/ask [question]`: Inquire about specific podcast content.
- `/help`: Display a list of available commands and their functions.
- `/clear`: Clear the chat history to clean up the conversation space.
- `/upload_audio [file] [language]`: Upload an audio file for detailed transcription and analysis.
- `/purge`: Remove all messages in the current channel for a fresh start.
- `/summarize`: Summarize the main points extracted from the uploaded audio file.

## 🛠️ Pre-Prompted Model Configuration

To enhance the Podcast Agent Bot's capabilities, we've crafted a specialized assistant profile using a `system.json` configuration. This profile informs the bot's behavior and sets the stage for its advanced analytical tasks.

## 💻 Technologies Used

- 📊 Utilizes OpenAI's GPT-4 via the API for advanced content analysis and engagement.
- 🎙️ Employs OpenAI's Whisper for high-accuracy podcast transcription.
- 🤖 Integrates with Discord using the Python API for interactive bot capabilities.

## 🤝 Contributing

The Podcast Agent Bot is an open-source project, and contributions are welcome. Feel free to fork the repository, make your changes, and submit a pull request.

## 📞 Contact

If you have any questions or need further assistance, you can contact the project maintainer:

- Name: Matias Vallejos
- 🌐 [matiasvallejos.com](https://matiasvallejos.com/)

Feel free to reach out if you have any inquiries or need any additional information about the project.

## 📄 License

This project is open source and available under the [GNU Affero General Public License v3.0](LICENSE).
