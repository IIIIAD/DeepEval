import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class MeetingSummarizer:
    def __init__(
        self, 
        model: str = "llama-3.1-8b-instant", 
        system_prompt: str = "",
        summary_system_prompt: str = "",
        action_item_system_prompt: str = ""
    ):
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.system_prompt = system_prompt or (
            "Summarize this meeting transcript clearly and accurately, capturing key points and action items. Be concise and factual."
        )
        self.summary_system_prompt = summary_system_prompt or (
            "You are an AI assistant summarizing meeting transcripts. Provide a clear and concise summary of the following conversation, avoiding interpretation and unnecessary details. Focus on the main discussion points only. Do not include any action items. Respond with only the summary as plain text — no headings, formatting, or explanations."
        )
        self.action_item_system_prompt = action_item_system_prompt or (
            """Extract all action items from the following meeting transcript. Identify individual 
and team-wide action items in the following format:

{
  "individual_actions": {
    "Alice": ["Task 1", "Task 2"],
    "Bob": ["Task 1"]
  },
  "team_actions": ["Task 1", "Task 2"],
  "entities": ["Alice", "Bob"]
}

Only include what is explicitly mentioned. Do not infer. You must respond strictly in 
valid JSON format — no extra text or commentary."""
        )

    def get_summary(self, transcript: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.summary_system_prompt},
                    {"role": "user", "content": transcript}
                ]
            )
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error: Could not generate summary due to API issue: {e}"
    
    def get_action_items(self, transcript: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.action_item_system_prompt},
                    {"role": "user", "content": transcript}
                ]
            )
            action_items = response.choices[0].message.content.strip()
            try:
                return json.loads(action_items)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON returned from model", "raw_output": action_items}
        except Exception as e:
            print(f"Error generating action items: {e}")
            return {"error": f"API call failed: {e}", "raw_output": ""}
        
    # def summarize(self, transcript: str) -> str:
    #     response = self.client.chat.completions.create(
    #         model=self.model,
    #         messages=[
    #             {"role": "system", "content": self.system_prompt},
    #             {"role": "user", "content": transcript}
    #         ]
    #     )
        
    #     content = response.choices[0].message.content.strip()
    #     return content
    def summarize(self, transcript: str) -> tuple[str, dict]:
        summary = self.get_summary(transcript)
        action_items = self.get_action_items(transcript)
        return summary, action_items
    

# summarizer = MeetingSummarizer()
# summary = summarizer.summarize(transcript)
# print(summary)

summarizer = MeetingSummarizer()

transcript_path = Path(__file__).parent / "meeting_transcript.txt"
with open(transcript_path, "r", encoding="utf-8") as file:
    transcript = file.read().strip()

summary, action_items = summarizer.summarize(transcript)
print(summary)
print("JSON:")
print(json.dumps(action_items, indent=2))