# Description: This file contains the messages and responses used by the Discord bot.

# Available commands for the bot
commands_info = [
    "`/ask [question]` - Ask any question, and ChatGPT will respond with an insightful answer.",
    "`/upload_audio [file] [language]` - Upload an audio file for analysis in the specified language. Supported formats are `mp3`, `wav`, and `ogg`. The bot will transcribe and summarize the audio content based on the selected language.",
    "`/summarize`- Summarize the provided text extracted from the audio file.",
    "`/clear` - Clears your chat history, removing all previous interactions and responses.",
    "`/save_session` - Save the current conversation to the memory persistance."
    "`/delete_session [session_id]` - Delete a specific session using the provided session ID.",
    "`/restore_session [session_id]` - Restore a previous session using the provided session ID.",
    "`/get_all_sessions` - Get a list of all available sessions."
    "`/help` - Displays this list of commands, helping you understand how to interact with the agent.",
]

# How to use the bot
usage_info = [
    "1. **Start a New Conversation:** Begin by initiating a conversation with the bot. This will set the context for your interaction.",
    "2. **Clear Chat History (if necessary):** Use the `/clear` command to start fresh and remove any previous interactions that might clutter your chat history.",
    "3. **Upload Your Podcast Audio:** Use the `/upload_audio [file] [language]` command to upload the audio file of your podcast. Ensure the file is in a supported audio format (mp3, wav, or ogg).",
    "4. **Analyze and Discuss:** After uploading, you can ask specific questions about the unstructured data from the audio using the `/ask [question]` command. This allows for interactive analysis and clarification of the content.",
]

# Copyright and project information
copyright_info = ["Created by **Matias Vallejos**. OpenSource project."]