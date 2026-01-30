"""
Symptom analysis service using Claude API.
Analyzes patient transcriptions to extract and cluster symptoms.
"""

import json
import anthropic


def analyze_symptoms(transcriptions: dict, api_key: str, model: str = "claude-sonnet-4-20250514", symptom_categories: list = None) -> dict:
    """
    Analyze patient transcriptions to extract and categorize symptoms.

    Args:
        transcriptions: Dict with question_id keys and transcription text values
        api_key: Anthropic API key
        model: Claude model to use
        symptom_categories: List of symptom category definitions

    Returns:
        Structured analysis dict with symptom clusters, timeline, and impact
    """
    if not api_key:
        raise ValueError("Claude API key not configured")

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Format symptom categories for the prompt
    categories_text = ""
    if symptom_categories:
        print(f"[ANALYZER DEBUG] Received {len(symptom_categories)} symptom categories")
        categories_text = "\n## Available Symptom Categories\n\n"
        for cat in symptom_categories:
            categories_text += f"- **{cat['name']}** (ID: {cat['id']})\n"
            categories_text += f"  {cat['description']}\n\n"
        print(f"[ANALYZER DEBUG] Categories text length: {len(categories_text)} chars")
    else:
        print("[ANALYZER DEBUG] WARNING: No symptom categories provided!")

    # Build analysis prompt
    analysis_prompt = f"""You are a medical intake analyst for a Long-COVID clinic. Analyze these patient responses and extract structured information about their symptoms.

{categories_text}

## Patient Responses

### TRANSCRIPTION RECEIVED:
Question 1: {transcriptions.get(1, '[No response recorded]')}

---

## Patient Interview Responses

### Question 1: Main Concerns
"What are the top three things you'd most like help with right now?"

Patient's response:
{transcriptions.get(1, '[No response recorded]')}

### Question 2: Timeline
"How long have you been experiencing these symptoms?"

Patient's response:
{transcriptions.get(2, '[No response recorded]')}

### Question 3: Daily Impact
"How are these symptoms affecting your day-to-day life?"

Patient's response:
{transcriptions.get(3, '[No response recorded]')}

---

## Analysis Task

Please analyze these responses and match the patient's symptoms to the appropriate categories listed above. 

CRITICAL: Match symptoms ONLY to the predefined category IDs and names provided above. Use the exact category_id and category_name from the list.

Be thorough but stick to what the patient actually said - do not infer symptoms they didn't mention.

You MUST return ONLY valid JSON in this EXACT format (no markdown code blocks, no backticks, no explanation text):

{{
    "matched_categories": [
        {{
            "category_id": "use exact ID from list above (e.g., brain_fog, energy_crash)",
            "category_name": "use exact name from list above",
            "confidence": "high",
            "patient_symptoms": ["specific symptom 1 they mentioned", "specific symptom 2"],
            "severity_indicators": ["direct quote showing severity"]
        }}
    ],
    "priority_concerns": ["their top concern 1", "their top concern 2", "their top concern 3"],
    "clinical_notes": "Brief 1-2 sentence summary for the clinical team"
}}

IMPORTANT: Return ONLY the JSON object. No other text before or after."""

    # Send to Claude for analysis
    print(f"[ANALYZER DEBUG] Sending prompt to Claude (length: {len(analysis_prompt)} chars)")
    print(f"[ANALYZER DEBUG] First 300 chars of prompt: {analysis_prompt[:300]}")
    
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": analysis_prompt
            }
        ]
    )
    
    print(f"[ANALYZER DEBUG] Claude responded successfully")

    # Parse JSON response
    response_text = message.content[0].text.strip()
    print(f"[CLAUDE DEBUG] Raw response (first 500 chars): {response_text[:500]}")

    # Try to extract JSON if wrapped in markdown
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith('```') and not in_json:
                in_json = True
                continue
            elif line.startswith('```') and in_json:
                break
            elif in_json:
                json_lines.append(line)
        response_text = '\n'.join(json_lines)
        print(f"[CLAUDE DEBUG] Extracted from markdown: {response_text[:500]}")

    try:
        analysis = json.loads(response_text)
        print(f"[CLAUDE DEBUG] Parsed analysis keys: {list(analysis.keys())}")
        if "matched_categories" in analysis:
            print(f"[CLAUDE DEBUG] Number of matched categories: {len(analysis['matched_categories'])}")
        if "symptom_clusters" in analysis:
            print(f"[CLAUDE DEBUG] Has old symptom_clusters format with {len(analysis['symptom_clusters'])} items")
        
        # If old format returned, convert to new format (fallback compatibility)
        if "symptom_clusters" in analysis and "matched_categories" not in analysis:
            print("[WARNING] Converting old symptom_clusters format to matched_categories")
            analysis["matched_categories"] = []
            for cluster in analysis.get("symptom_clusters", []):
                analysis["matched_categories"].append({
                    "category_id": "unknown",
                    "category_name": cluster.get("category", "Other"),
                    "confidence": "medium",
                    "patient_symptoms": cluster.get("symptoms", []),
                    "severity_indicators": cluster.get("severity_indicators", [])
                })
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Claude response: {e}")
        print(f"[ERROR] Response text: {response_text[:500]}")
        # Return a basic structure if parsing fails
        analysis = {
            "error": "Failed to parse analysis",
            "raw_response": response_text[:500],
            "matched_categories": [],
            "timeline": {"onset": "unknown", "trigger": "unknown", "progression": "unknown"},
            "impact_summary": {},
            "priority_concerns": [],
            "clinical_notes": "Analysis parsing failed - manual review needed"
        }

    return analysis
