import gradio as gr
import time
from backend.services.debate_service import run_debate_stream
from backend.database import save_debate, get_debate_history
from backend import config

# --- Custom Premium CSS Styling ---
THEME_CSS = """
/* Import premium typography */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@300;400&display=swap');

body, .gradio-container {
    font-family: 'Outfit', -apple-system, sans-serif !important;
    background: linear-gradient(135deg, #0b0b14 0%, #151528 50%, #0d0d18 100%) !important;
    color: #e2e8f0 !important;
    font-size: 1.1rem !important;
}

/* Glassmorphic card layouts */
.glass-card {
    background: rgba(20, 20, 35, 0.6) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}
.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 12px 40px 0 rgba(100, 100, 255, 0.08) !important;
}

/* Custom styles for opposing agent cards */
.pro-card {
    border-left: 5px solid #10b981 !important; /* Emerald green */
    background: rgba(16, 185, 129, 0.03) !important;
}
.against-card {
    border-left: 5px solid #f43f5e !important; /* Rose red */
    background: rgba(244, 63, 94, 0.03) !important;
}
.judge-card {
    border-left: 5px solid #fbbf24 !important; /* Amber gold */
    background: rgba(251, 191, 36, 0.03) !important;
}

/* Support larger text inside markdown / verdict views */
.glass-card p, .glass-card li, .glass-card ul, .judge-card, .judge-card p, .judge-card li {
    font-size: 1.15rem !important;
    line-height: 1.6 !important;
}

/* Headers and Titles */
h1 {
    font-weight: 800 !important;
    letter-spacing: -0.05em !important;
    background: linear-gradient(90deg, #a78bfa 0%, #ec4899 50%, #f43f5e 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center;
    margin-bottom: 0.5rem !important;
}
h2, h3 {
    font-weight: 600 !important;
    color: #f8fafc !important;
}

/* Button design */
.primary-btn {
    background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3) !important;
    transition: all 0.2s ease !important;
}
.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5) !important;
}

/* Form inputs & text boxes */
textarea, input[type="text"] {
    background: rgba(15, 15, 25, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-family: inherit !important;
    font-size: 1.15rem !important;
    line-height: 1.6 !important;
    transition: all 0.2s ease !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* Label styling */
.gr-form label, label span {
    font-weight: 600 !important;
    color: #94a3b8 !important;
    font-size: 1.05rem !important;
}

/* Status Bar */
.status-bar {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    color: #a5b4fc !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    text-align: center;
}
"""

def format_history_choices():
    """Reads history records and formats them as list entries for the select dropdown."""
    records = get_debate_history()
    choices = []
    for idx, r in enumerate(records):
        timestamp = r.get("timestamp", "").split("T")[0]
        winner = r.get("winner", "DRAW")
        topic_short = r.get("topic", "")
        if len(topic_short) > 60:
            topic_short = topic_short[:57] + "..."
        display = f"[{timestamp}] Winner: {winner} | {topic_short}"
        choices.append((display, idx))
    
    if not choices:
        return [("No historical debates saved yet.", -1)]
    return choices

def load_selected_debate(selected_idx):
    """Loads a specific past debate from history into the archives view."""
    if selected_idx is None or selected_idx == -1:
        return "", "", "", "", "", ""
    
    records = get_debate_history()
    if selected_idx >= len(records):
        return "Record not found.", "", "", "", "", ""
        
    r = records[selected_idx]
    
    archive_meta = (
        f"### Topic: {r.get('topic')}\n"
        f"**Date:** {r.get('timestamp', '').replace('T', ' ').split('.')[0]} UTC\n"
        f"**Declared Winner:** 🏆 {r.get('winner', 'DRAW')}\n"
        f"**Scores:** Pro Side: {r.get('scores', {}).get('pro', 5)}/10 | Against Side: {r.get('scores', {}).get('against', 5)}/10"
    )
    
    return (
        archive_meta,
        r.get("pro_opening", ""),
        r.get("against_opening", ""),
        r.get("pro_rebuttal", ""),
        r.get("against_rebuttal", ""),
        r.get("verdict", "")
    )

def execute_debate(topic):
    """Streams the debate progression and saves it upon final completion."""
    if not topic.strip():
        yield "", "", "", "", "", "Please input a valid debate topic.", gr.update()
        return

    # 1. Stream the live agent responses
    final_state = None
    for state in run_debate_stream(topic):
        final_state = state
        yield (
            state["pro_opening"],
            state["against_opening"],
            state["pro_rebuttal"],
            state["against_rebuttal"],
            state["verdict"],
            f"🔄 {state['status']}",
            gr.update()
        )
    
    # 2. Save completed debate record
    if final_state:
        save_debate(final_state)
        time.sleep(0.5)
        # Yield the final update with completed status and refreshed history list
        yield (
            final_state["pro_opening"],
            final_state["against_opening"],
            final_state["pro_rebuttal"],
            final_state["against_rebuttal"],
            final_state["verdict"],
            f"✅ {final_state['status']}",
            gr.update(choices=format_history_choices())
        )

# --- Gradio UI Layout Building ---
with gr.Blocks(css=THEME_CSS, title="AI Debate Arena ⚖️") as demo:
    gr.HTML("<h1>AI DEBATE ARENA ⚖️</h1>")
    gr.HTML("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>An elite multi-agent debating system powered by Gemini 2.5 Flash & Firebase Firestore</p>")
    
    # Alert message if Gemini is running in mock mode
    if not config.is_gemini_configured():
        gr.HTML(
            "<div style='background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #f59e0b; padding: 1rem; border-radius: 12px; text-align: center; margin-bottom: 1.5rem;'>"
            "⚠️ <strong>GEMINI_API_KEY environment variable is missing!</strong> "
            "The app is currently running in <strong>Mock Demonstration Mode</strong>. "
            "Please configure your .env file to unlock actual AI interactions."
            "</div>"
        )
        
    with gr.Tabs():
        # --- TAB 1: THE ARENA ---
        with gr.Tab("Debate Arena"):
            with gr.Row():
                with gr.Column(scale=4):
                    topic_input = gr.Textbox(
                        label="Enter Debate Topic",
                        placeholder="e.g., Artificial Intelligence will replace human programmers.",
                        lines=2
                    )
                with gr.Column(scale=1, min_width=150):
                    start_btn = gr.Button("Launch Debate ⚔️", elem_classes=["primary-btn"], variant="primary")
            
            # Streaming status message
            status_box = gr.HTML(
                value="<div class='status-bar'>Ready to host a debate. Enter a topic and press Launch!</div>"
            )
            
            gr.HTML("<h3>⚔️ Opening Round ⚔️</h3>")
            with gr.Row():
                with gr.Column():
                    pro_opening_box = gr.Textbox(
                        label="Pro Agent Opening Argument",
                        lines=10,
                        interactive=False,
                        elem_classes=["glass-card", "pro-card"]
                    )
                with gr.Column():
                    against_opening_box = gr.Textbox(
                        label="Against Agent Opening Argument",
                        lines=10,
                        interactive=False,
                        elem_classes=["glass-card", "against-card"]
                    )
            
            gr.HTML("<h3>🛡️ Rebuttal Round 🛡️</h3>")
            with gr.Row():
                with gr.Column():
                    pro_rebuttal_box = gr.Textbox(
                        label="Pro Agent Rebuttal",
                        lines=10,
                        interactive=False,
                        elem_classes=["glass-card", "pro-card"]
                    )
                with gr.Column():
                    against_rebuttal_box = gr.Textbox(
                        label="Against Agent Rebuttal",
                        lines=10,
                        interactive=False,
                        elem_classes=["glass-card", "against-card"]
                    )
            
            gr.HTML("<h3>⚖️ The Judge's Verdict ⚖️</h3>")
            judge_verdict_box = gr.Markdown(
                label="AI Judge Verdict",
                elem_classes=["glass-card", "judge-card"]
            )
            
        # --- TAB 2: THE ARCHIVES ---
        with gr.Tab("Debate Archives"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.HTML("<h4>Select Past Debate</h4>")
                    history_dropdown = gr.Dropdown(
                        choices=format_history_choices(),
                        label="Past Debates",
                        interactive=True
                    )
                    refresh_btn = gr.Button("Refresh History 🔄", size="sm")
                    
                    gr.HTML("<div style='margin-top: 1.5rem;'></div>")
                    archive_metadata = gr.Markdown(
                        value="Select a debate from the list to explore its transcripts.",
                        elem_classes=["glass-card", "judge-card"]
                    )
                
                with gr.Column(scale=3):
                    gr.HTML("<h4>Debate Transcripts</h4>")
                    with gr.Tabs():
                        with gr.TabItem("Opening Arguments"):
                            archive_pro_opening = gr.Textbox(label="Pro Opening", lines=8, interactive=False, elem_classes=["glass-card", "pro-card"])
                            archive_against_opening = gr.Textbox(label="Against Opening", lines=8, interactive=False, elem_classes=["glass-card", "against-card"])
                        with gr.TabItem("Rebuttals"):
                            archive_pro_rebuttal = gr.Textbox(label="Pro Rebuttal", lines=8, interactive=False, elem_classes=["glass-card", "pro-card"])
                            archive_against_rebuttal = gr.Textbox(label="Against Rebuttal", lines=8, interactive=False, elem_classes=["glass-card", "against-card"])
                        with gr.TabItem("Verdict"):
                            archive_verdict = gr.Markdown(elem_classes=["glass-card", "judge-card"])

    # --- Wire Events ---
    
    # 1. Start Debate Stream
    start_btn.click(
        fn=execute_debate,
        inputs=[topic_input],
        outputs=[
            pro_opening_box, 
            against_opening_box, 
            pro_rebuttal_box, 
            against_rebuttal_box, 
            judge_verdict_box, 
            status_box,
            history_dropdown
        ]
    )
    
    # 2. View Past Debate from History
    history_dropdown.change(
        fn=load_selected_debate,
        inputs=[history_dropdown],
        outputs=[
            archive_metadata,
            archive_pro_opening,
            archive_against_opening,
            archive_pro_rebuttal,
            archive_against_rebuttal,
            archive_verdict
        ]
    )
    
    # 3. Refresh History Dropdown List
    refresh_btn.click(
        fn=lambda: gr.update(choices=format_history_choices()),
        inputs=[],
        outputs=[history_dropdown]
    )

# --- Start app inside docker / local port ---
if __name__ == "__main__":
    # Standard Cloud Run requires listening on port 8080 and host 0.0.0.0
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=config.PORT)
