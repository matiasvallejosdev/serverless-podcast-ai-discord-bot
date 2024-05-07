summarize_prompt = """
Based on the transcription text of the podcast provided, generate a concise summary that 
encapsulates all the key points and important information. The summary should not exceed 
1200 characters. Focus on the main themes, significant discussions, notable figures mentioned, 
and any critical conclusions or insights from the podcast. Ensure that the summary is 
comprehensive yet succinct, providing a clear overview of the podcast's content and its relevance.
"""

pre_transcription_prompt = """
In the next message, I will send you the transcription of an audio. This text will be unstructured. 
Once you receive it, please acknowledge by saying 'Incredible, I just received the text of your audio. 
Let's proceed to analyze the podcast together.' After that, wait for my cue to ask questions or analyze 
the text further. Do not generate a summary until I specifically request it.
"""
