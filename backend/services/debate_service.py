import time
from typing import Generator, Dict, Any
from backend.services.gemini_service import generate_text

def run_debate_stream(topic: str) -> Generator[Dict[str, Any], None, None]:
    """
    Orchestrates a 2-round multi-agent debate (Opening + Rebuttal) and an evaluation.
    Yields dictionary updates representing the live debate progression for streaming UI.
    """
    debate_state = {
        "topic": topic,
        "pro_opening": "",
        "against_opening": "",
        "pro_rebuttal": "",
        "against_rebuttal": "",
        "verdict": "",
        "winner": "",
        "scores": {},
        "status": "Starting debate..."
    }
    
    yield debate_state
    time.sleep(0.5)

    # ----------------------------------------------------
    # Round 1: Opening Arguments
    # ----------------------------------------------------
    
    # 1. Pro Agent Opening
    debate_state["status"] = "Pro Agent is formulating opening argument..."
    yield debate_state
    
    pro_inst = (
        "You are the Pro Agent: a world-class, punchy debater. Your sole mandate is to argue passionately "
        "and persuasively IN FAVOR of the topic. Your response must be extremely concise and fast-paced: "
        "maximum 3 to 4 sentences, and strictly maximum 80 words. Focus only on your single strongest argument."
    )
    pro_prompt = f"Topic: {topic}\n\nDeliver your opening argument supporting this topic. Keep it powerful, clear, and ensure it is maximum 3-4 sentences (max 80 words)."
    debate_state["pro_opening"] = generate_text(pro_prompt, pro_inst, temperature=0.7)
    
    debate_state["status"] = "Pro Agent has finished their opening argument."
    yield debate_state
    time.sleep(1.0)
    
    # 2. Against Agent Opening
    debate_state["status"] = "Against Agent is formulating opening argument..."
    yield debate_state
    
    against_inst = (
        "You are the Against Agent: a sharp, highly critical debater. Your sole mandate is to argue strongly "
        "and persuasively AGAINST the topic. Your response must be extremely concise and fast-paced: "
        "maximum 3 to 4 sentences, and strictly maximum 80 words. Focus only on your single strongest counter-argument."
    )
    against_prompt = (
        f"Topic: {topic}\n\n"
        f"Here is the Pro Agent's opening argument for reference:\n{debate_state['pro_opening']}\n\n"
        f"Deliver your opening argument opposing this topic. Keep it robust, sharp, and ensure it is maximum 3-4 sentences (max 80 words)."
    )
    debate_state["against_opening"] = generate_text(against_prompt, against_inst, temperature=0.7)
    
    debate_state["status"] = "Against Agent has finished their opening argument."
    yield debate_state
    time.sleep(1.0)

    # ----------------------------------------------------
    # Round 2: Rebuttal Round
    # ----------------------------------------------------
    
    # 3. Pro Agent Rebuttal
    debate_state["status"] = "Pro Agent is constructing rebuttal..."
    yield debate_state
    
    pro_rebuttal_prompt = (
        f"Topic: {topic}\n\n"
        f"Your Opening: {debate_state['pro_opening']}\n\n"
        f"Opponent's Opening: {debate_state['against_opening']}\n\n"
        f"Provide a sharp rebuttal directly challenging one specific point from the opponent. "
        f"Do not repeat your opening argument. Keep it strictly to 2-3 sentences and maximum 50 words."
    )
    pro_inst_rebuttal = (
        "You are the Pro Agent. Construct a sharp, rapid-fire rebuttal. Your response must be maximum 2 to 3 sentences "
        "and maximum 50 words. Directly challenge one specific point from the opponent, and do not repeat your opening."
    )
    debate_state["pro_rebuttal"] = generate_text(pro_rebuttal_prompt, pro_inst_rebuttal, temperature=0.8)
    
    debate_state["status"] = "Pro Agent has completed their rebuttal."
    yield debate_state
    time.sleep(1.0)
    
    # 4. Against Agent Rebuttal
    debate_state["status"] = "Against Agent is constructing rebuttal..."
    yield debate_state
    
    against_rebuttal_prompt = (
        f"Topic: {topic}\n\n"
        f"Your Opening: {debate_state['against_opening']}\n\n"
        f"Opponent's Rebuttal: {debate_state['pro_rebuttal']}\n\n"
        f"Provide your final rebuttal, directly deconstructing the Pro Agent's rebuttal by challenging one specific point. "
        f"Do not repeat your opening. Keep it strictly to 2-3 sentences and maximum 50 words."
    )
    against_inst_rebuttal = (
        "You are the Against Agent. Construct a sharp, rapid-fire rebuttal. Your response must be maximum 2 to 3 sentences "
        "and maximum 50 words. Directly challenge one specific point from the opponent's rebuttal, and do not repeat your opening."
    )
    debate_state["against_rebuttal"] = generate_text(against_rebuttal_prompt, against_inst_rebuttal, temperature=0.8)
    
    debate_state["status"] = "Against Agent has completed their rebuttal."
    yield debate_state
    time.sleep(1.0)

    # ----------------------------------------------------
    # Round 3: Evaluation (The AI Judge)
    # ----------------------------------------------------
    debate_state["status"] = "AI Judge is analyzing arguments and formulating the verdict..."
    yield debate_state
    
    judge_inst = (
        "You are the AI Judge: an ultra-objective, concise intellectual referee. "
        "Your task is to deliver a sharp, highly structured verdict on the debate in a maximum of 6 sentences total. "
        "Briefly explain who won, assess their logical consistency, relevance of points, and persuasiveness."
    )
    
    judge_prompt = (
        f"Evaluate the debate on the topic: '{topic}'\n\n"
        f"=== DEBATE TRANSCRIPT ===\n\n"
        f"PRO AGENT OPENING:\n{debate_state['pro_opening']}\n\n"
        f"AGAINST AGENT OPENING:\n{debate_state['against_opening']}\n\n"
        f"PRO AGENT REBUTTAL:\n{debate_state['pro_rebuttal']}\n\n"
        f"AGAINST AGENT REBUTTAL:\n{debate_state['against_rebuttal']}\n\n"
        f"=== END OF TRANSCRIPT ===\n\n"
        f"Deliver your brief verdict (maximum 6 sentences total) explaining the winner clearly.\n"
        f"At the very end of your verdict, output the following structured summary lines exactly:\n\n"
        f"Winner: [PRO AGENT or AGAINST AGENT or DRAW]\n"
        f"Pro Score: [X/10]\n"
        f"Against Score: [Y/10]\n\n"
        f"Detailed Scores:\n"
        f"* Logic Score: Pro [X/10] | Against [Y/10]\n"
        f"* Relevance Score: Pro [X/10] | Against [Y/10]\n"
        f"* Persuasiveness Score: Pro [X/10] | Against [Y/10]"
    )
    
    verdict = generate_text(judge_prompt, judge_inst, temperature=0.4)
    debate_state["verdict"] = verdict
    
    # Parse winner and scores from the verdict text for structural logging
    winner = "DRAW"
    pro_score = 5
    against_score = 5
    
    for line in verdict.split("\n"):
        line_clean = line.strip().upper()
        if "WINNER:" in line_clean:
            if "PRO" in line_clean:
                winner = "PRO AGENT"
            elif "AGAINST" in line_clean or "CON" in line_clean:
                winner = "AGAINST AGENT"
            else:
                winner = "DRAW"
        elif "PRO SCORE:" in line_clean:
            try:
                # Extracts the digits
                pro_score = int(''.join(filter(str.isdigit, line_clean.split("PRO SCORE:")[1].split("/")[0])))
            except Exception:
                pass
        elif "AGAINST SCORE:" in line_clean:
            try:
                against_score = int(''.join(filter(str.isdigit, line_clean.split("AGAINST SCORE:")[1].split("/")[0])))
            except Exception:
                pass

    debate_state["winner"] = winner
    debate_state["scores"] = {"pro": pro_score, "against": against_score}
    debate_state["status"] = "Debate Completed Successfully!"
    yield debate_state
