import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class UserSimulator:
    def __init__(self, persona="A detail-oriented coin investor evaluating a website."):
        self.persona = persona
        self.model = genai.GenerativeModel('gemini-pro')

    def evaluate_genome(self, genome):
        """
        Simulates a user visiting a site with this genome (UI config).
        Returns a fitness score (0.0 to 1.0) and a rationale.
        """
        prompt = f"""
        Role: {self.persona}
        Task: You are visiting a website with the following UI Configuration (Genome):
        {json.dumps(genome, indent=2)}

        Context:
        - Density: Low means spacious (Collector), High means dense (Investor).
        - Primary Color: Affects trust and emotion.
        - Border Radius: Affects modern vs classic feel.

        Question: On a scale of 0.0 to 1.0, how likely are you to TRUST and BUY from this simulated interface? 
        Consider readability, aesthetic harmony, and persona alignment.

        Output JSON only:
        {{
            "score": 0.8,
            "rationale": "The high density suits my need for data, but the neon pink color reduces trust."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Simple cleanup to handle potential markdown code blocks in response
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"Simulator Error: {e}")
            return {"score": 0.5, "rationale": "Simulation crashed, returning neutral score."}

if __name__ == "__main__":
    # Test run
    sim = UserSimulator()
    test_genome = {"primaryColor": "#ff0000", "density": "compact", "borderRadius": "0px"}
    print(sim.evaluate_genome(test_genome))
