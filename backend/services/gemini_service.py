import logging
from google import genai
from google.genai import types
from backend import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GenAI Client if API key is provided
_client = None
if config.is_gemini_configured():
    try:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
        logger.info("Gemini GenAI client successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini GenAI client: {e}")
else:
    logger.warning("GEMINI_API_KEY is not set. Gemini Service will run in MOCK mode.")

def generate_text(prompt: str, system_instruction: str = None, temperature: float = 0.7) -> str:
    """
    Generates text using Gemini 2.5 Flash. Falls back to realistic mock responses
    if the API key is not configured or in case of api errors.
    """
    if _client is not None:
        try:
            logger.info("Calling Gemini API (gemini-2.5-flash)...")
            config_params = {}
            if system_instruction:
                config_params["system_instruction"] = system_instruction
            if temperature is not None:
                config_params["temperature"] = temperature
            
            response = _client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(**config_params)
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}. Falling back to mock generator.")
            return _generate_mock_fallback(prompt, system_instruction)
    else:
        return _generate_mock_fallback(prompt, system_instruction)

def _generate_mock_fallback(prompt: str, system_instruction: str) -> str:
    """Generate realistic mock response based on the persona and topic to allow UI testing."""
    persona = "Debater"
    if system_instruction:
        if "supporting" in system_instruction.lower() or "pro" in system_instruction.lower():
            persona = "Pro Agent"
        elif "opposing" in system_instruction.lower() or "against" in system_instruction.lower():
            persona = "Against Agent"
        elif "judge" in system_instruction.lower():
            persona = "AI Judge"
            
    logger.info(f"[MOCK MODE] Generating response for {persona}...")
    
    is_rebuttal = "rebuttal" in prompt.lower()
    
    # Simple structured mock generator depending on persona and prompt
    if persona == "Pro Agent":
        if is_rebuttal:
            return (
                "The opponent exaggerates systemic risks to stall progress. "
                "Regulatory safeguards easily mitigate safety concerns, while the projected efficiency gains "
                "far outweigh any hypothetical overhead costs."
            )
        else:
            return (
                "Embracing this topic unlocks unparalleled optimization, streamlined processes, and long-term economic gains. "
                "Delaying adoption is a regression that places us behind the global standards of modern innovation. "
                "Proactive adoption is the single most logical step to secure future-proof efficiency."
            )
    elif persona == "Against Agent":
        if is_rebuttal:
            return (
                "The opponent's rebuttal ignores that theoretical safeguards routinely fail under real-world pressures. "
                "Visionary optimism cannot offset the immediate, unaddressed structural vulnerabilities we highlighted."
            )
        else:
            return (
                "We must oppose this proposition due to severe systemic risks, uncalculated economic overhead, and ignored externalities. "
                "Rushing to innovate compromises safety, ethics, and long-term security. "
                "Implementing safer, highly mitigated alternatives is the only responsible way forward."
            )
    else:  # AI Judge
        return (
            "Both debaters delivered highly focused arguments on risk versus innovation. "
            "The Pro side presented compelling visions of long-term optimization. "
            "However, the Against side successfully defended their position by deconstructing the Pro rebuttal, "
            "highlighting that theoretical safeguards fail in practice. "
            "Ultimately, the Against side demonstrated superior risk awareness and structural defense.\n\n"
            "Winner: AGAINST AGENT\n"
            "Pro Score: 7/10\n"
            "Against Score: 8/10\n\n"
            "Detailed Scores:\n"
            "* Logic Score: Pro 7/10 | Against 8/10\n"
            "* Relevance Score: Pro 8/10 | Against 8/10\n"
            "* Persuasiveness Score: Pro 6/10 | Against 8/10"
        )
