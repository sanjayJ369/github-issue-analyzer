import google.generativeai as genai
from .schemas import IssueAnalysis
from .config import Config

class LLMClient:
    def __init__(self):
        self.model = None
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(Config.MODEL_NAME)
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
        else:
            print("Warning: GEMINI_API_KEY not found. Analysis will fail.")

    async def analyze_issue(self, context: str, allowed_labels: list[str] = None) -> IssueAnalysis:
        """
        Analyzes the issue context using Gemini Structured Outputs.
        """
        if not self.model:
            raise RuntimeError("Gemini API Key is missing or invalid. Please configure GEMINI_API_KEY in environment variables.")
        
        system_prompt = (
            "You are an expert engineering assistant. Analyze the GitHub issue provided below. "
            "Output strictly valid JSON matching the required schema. "
            "Be concise but insightful."
        )
        
        if allowed_labels:
            labels_str = ", ".join(allowed_labels[:50]) # Limit to 50 labels to avoid context bloat
            system_prompt += f"\n\nPrefer using these existing repository labels if applicable: {labels_str}"
        
        system_prompt += (
            "\n\nOUTPUT REQUIREMENTS:"
            "\n1. priority_score: Must use the format 'X/5 - Justification'. Example: '5/5 - Critical breakage blocks all users'. The justification must be specific to the issue."
            "\n2. suggested_labels: STRICTLY 2-3 labels. Use ONLY standard, lowercase, kebab-case labels (e.g., 'bug', 'enhancement', 'documentation', 'help-wanted', 'good-first-issue', 'dependencies'). DO NOT use complex, slashed, or product-specific custom labels like 'API/Apollo'."
        )

        try:
            # Create a prompt that includes the system prompt and the user context
            full_prompt = f"{system_prompt}\n\nISSUE CONTEXT:\n{context}"

            result = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=IssueAnalysis
                )
            )
            
            # Use the Pydantic model to parse the result. 
            # The result.text should be a JSON string matching the schema.
            return IssueAnalysis.model_validate_json(result.text)
            
        except Exception as e:
            # Fallback or re-raise. For now re-raise to be handled by endpoint
            print(f"LLM Error: {e}")
            raise
