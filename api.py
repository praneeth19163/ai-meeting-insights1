from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class TextInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    summary: str
    action_items: list[str]
    risks: list[str]
    priority_tasks: list[str]
    input_tokens: int
    output_tokens: int

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    text = input_data.text
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Please provide text to analyze")
    
    if len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text should be minimum of 50 characters")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are an expert meeting analyst. Extract key information from meeting notes, documents, or text and return a structured JSON response.

Your task:
1. Create a concise summary highlighting main points
2. Extract action items (specific tasks to be done)
3. Identify risks (potential problems, blockers, or concerns)
4. List priority tasks (urgent or high-importance items)

Rules:
- Return valid JSON only
- If a section has no items, use an empty array []
- Be specific and actionable
- Avoid duplicates across sections
- Priority tasks should be subset of action items that are most urgent"""},
                {"role": "user", "content": f"""Analyze the following text and return a JSON object with this exact structure:

{{
  "summary": "concise summary here",
  "action_items": ["item1", "item2"],
  "risks": ["risk1", "risk2"],
  "priority_tasks": ["task1", "task2"]
}}

Text to analyze:
{text}"""}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Handle None or empty content
        if not content:
            raise HTTPException(status_code=500, detail="AI returned empty response")
        
        parsed_data = json.loads(content)
        print("\n" + "="*50)
        print("JSON OUTPUT:")
        print(json.dumps(parsed_data, indent=2))
        print("="*50 + "\n")
        
        return {
            "summary": parsed_data.get("summary", ""),
            "action_items": parsed_data.get("action_items", []),
            "risks": parsed_data.get("risks", []),
            "priority_tasks": parsed_data.get("priority_tasks", []),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        print(f"Content received: {content}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
