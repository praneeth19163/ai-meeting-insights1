# AI Meeting Insights Analyzer

Extract structured insights from meeting notes and documents using OpenAI GPT-4o-mini.

## Features

- **Summary**: Concise overview of main points
- **Action Items**: Specific tasks to be completed
- **Risks**: Potential problems or blockers
- **Priority Tasks**: Urgent high-importance items
- **File Upload**: Support for PDF and DOCX files
- **JSON Output**: Structured response format

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_key_here
     ```

## Running the Application

1. **Start the API server:**
   ```bash
   uvicorn api:app --reload --port 8000
   ```

2. **Start the Streamlit app (in a new terminal):**
   ```bash
   streamlit run app.py
   ```

3. **Access the app:**
   - Open browser to `http://localhost:8501`

## API Endpoint

**POST /analyze**

Request:
```json
{
  "text": "your meeting notes here"
}
```

Response:
```json
{
  "summary": "concise summary",
  "action_items": ["task1", "task2"],
  "risks": ["risk1", "risk2"],
  "priority_tasks": ["urgent task1"],
  "input_tokens": 150,
  "output_tokens": 200
}
```

## Model Configuration

- **Model**: gpt-4o-mini
- **Temperature**: 0.2 (deterministic, consistent output)
- **Response Format**: JSON object
- **Max Tokens**: 1000

## Edge Cases Handled

- Empty text input
- Missing sections (returns empty arrays)
- Invalid file formats
- JSON parsing errors
- API connection failures
