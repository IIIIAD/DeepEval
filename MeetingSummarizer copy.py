import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class MeetingSummarizer:
    def __init__(
        self, 
        model: str = "llama-3.1-8b-instant", 
        system_prompt: str = "",
    ):
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.system_prompt = system_prompt or (
            "Summarize this meeting transcript clearly and accurately, capturing key points and action items. Be concise and factual."
        )

    def summarize(self, transcript: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": transcript}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        return content
    
transcript_path = Path(__file__).parent / "meeting_transcript.txt"
with open(transcript_path, "r", encoding="utf-8") as file:
    transcript = file.read().strip()

summarizer = MeetingSummarizer()
summary = summarizer.summarize(transcript)
print(summary)