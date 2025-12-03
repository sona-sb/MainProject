"""
Courtroom Simulation with Multi-Agent System

This module implements a courtroom simulation with three participants:
1. Judge Agent - Presides over the case, can modify judgment predictions, delivers final verdict
2. Opposite Party Lawyer Agent - Defends the opposite party with synthetic arguments
3. User (Consumer) - Types their arguments manually

The simulation uses a judgment prediction JSON file as the basis for the case.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from niyam_guru_backend.config import LLM_MODEL, SIMULATION_DIR


# ============================================================================
# Type Definitions
# ============================================================================

class CaseState(TypedDict):
    """State of the courtroom simulation."""
    judgment_data: dict
    case_phase: Literal["opening", "arguments", "evidence", "closing", "verdict"]
    hearing_number: int
    proceedings_log: list[dict]
    case_concluded: bool


# ============================================================================
# Prompts
# ============================================================================

JUDGE_SYSTEM_PROMPT = """You are an experienced Judge presiding over a Consumer Protection case in an Indian Consumer Court.

CASE DETAILS:
{case_summary}

LEGAL GROUNDS:
{legal_grounds}

CURRENT JUDGMENT REASONING:
{judgment_reasoning}

CURRENT RELIEF PROPOSED:
{relief_granted}

Your responsibilities:
1. Maintain courtroom decorum and ensure fair proceedings
2. Ask relevant questions to both parties to clarify facts
3. Evaluate arguments and evidence presented by both sides
4. You may modify the judgment prediction based on new arguments or evidence presented
5. When you feel the case has been sufficiently argued, deliver the final verdict

Guidelines:
- Be impartial and fair to both parties
- Apply legal principles from the Consumer Protection Act, 2019
- Consider precedents cited in the case
- Give weight to evidence presented
- If modifying the judgment, explain your reasoning clearly
- Use formal courtroom language

When you are ready to conclude the case, start your response with "[VERDICT]" and deliver a formal judgment.

When you want to modify the judgment prediction, include a JSON block in your response like:
```json_update
{{"field": "path.to.field", "value": "new value", "reason": "explanation"}}
```

Current hearing: #{hearing_number}
Case phase: {case_phase}
"""

OPPOSITE_PARTY_LAWYER_PROMPT = """You are an experienced defense lawyer representing the Opposite Party (the seller/service provider) in a Consumer Protection case.

CASE AGAINST YOUR CLIENT:
{case_summary}

YOUR CLIENT'S POSITION:
{defense_arguments}

LEGAL SECTIONS INVOKED BY COMPLAINANT:
{applicable_sections}

CONSUMER'S KEY ARGUMENTS:
{consumer_arguments}

Your responsibilities:
1. Defend your client vigorously but ethically
2. Generate synthetic but realistic defense materials (witness statements, expert opinions, documents)
3. Challenge the consumer's evidence and arguments
4. Present counter-arguments based on legal principles
5. Highlight gaps in the consumer's case

SYNTHETIC DEFENSE MATERIALS YOU MAY GENERATE:
- Expert technical reports (e.g., from mobile technicians)
- Warranty terms and conditions
- Store policy documents
- CCTV footage descriptions
- Customer service call logs
- Technical manuals and user guidelines
- Statements from store employees

Guidelines:
- Your synthetic materials should be plausible but not outlandish
- Acknowledge weaknesses in your case where obvious
- Use proper legal terminology
- Address the specific facts of this case
- Be respectful to the court and opposing party

Current hearing: #{hearing_number}
Last statement from Court/Consumer: {last_statement}
"""


# ============================================================================
# Helper Functions
# ============================================================================

def load_judgment_json(file_path: str) -> dict:
    """Load the judgment prediction JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_judgment_json(data: dict, file_path: str) -> None:
    """Save the updated judgment JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def format_case_summary(data: dict) -> str:
    """Format case summary for prompts."""
    cs = data.get("Case_Summary", {})
    return f"""
Title: {cs.get('Title', 'N/A')}
Case Type: {cs.get('Case_Type', 'N/A')}

Consumer Details:
- Description: {cs.get('Consumer_Details', {}).get('Description', 'N/A')}
- Claim Amount: Rs. {cs.get('Consumer_Details', {}).get('Claim_Amount', 'N/A')}
- Key Grievances: {', '.join(cs.get('Consumer_Details', {}).get('Key_Grievances', []))}

Facts of Case:
{chr(10).join('- ' + fact for fact in cs.get('Facts_of_Case', []))}

Evidence Available:
{chr(10).join('- ' + ev for ev in cs.get('Evidence_Available', []))}

Evidence Missing:
{chr(10).join('- ' + ev for ev in cs.get('Evidence_Missing', []))}
"""


def format_legal_grounds(data: dict) -> str:
    """Format legal grounds for prompts."""
    lg = data.get("Legal_Grounds", {})
    sections = lg.get("Applicable_Sections", [])
    precedents = lg.get("Precedents_Cited", [])
    
    sections_text = "\n".join([
        f"- Section {s.get('Section')} of {s.get('Act')}: {s.get('Description')}"
        for s in sections
    ])
    
    precedents_text = "\n".join([
        f"- {p.get('Case_Name')} ({p.get('Year')}): {p.get('Key_Holding')}"
        for p in precedents
    ])
    
    return f"""
Applicable Sections:
{sections_text}

Precedents:
{precedents_text}

Legal Principles:
{chr(10).join('- ' + p for p in lg.get('Legal_Principles', []))}
"""


def format_judgment_reasoning(data: dict) -> str:
    """Format judgment reasoning for prompts."""
    jr = data.get("Judgment_Reasoning", {})
    issues = jr.get("Issues_Framed", [])
    
    issues_text = "\n".join([
        f"Issue {i.get('Issue_Number')}: {i.get('Issue')}\nFinding: {i.get('Finding')}"
        for i in issues
    ])
    
    return f"""
Issues Framed:
{issues_text}

Overall Findings: {jr.get('Findings', 'N/A')}
Liability Status: {jr.get('Liability_Status', 'N/A')}
Liability Confidence: {jr.get('Liability_Confidence', 'N/A')}
"""


def format_relief_granted(data: dict) -> str:
    """Format relief granted for prompts."""
    rg = data.get("Relief_Granted", {})
    primary = rg.get("Primary_Relief", {})
    additional = rg.get("Additional_Relief", [])
    
    additional_text = "\n".join([
        f"- {r.get('Type')}: Rs. {r.get('Amount')} ({r.get('Justification')})"
        for r in additional
    ])
    
    total = rg.get("Total_Compensation_Range", {})
    
    return f"""
Primary Relief: {primary.get('Type')} - Rs. {primary.get('Amount')}

Additional Relief:
{additional_text}

Total Compensation Range: Rs. {total.get('Minimum', 'N/A')} - Rs. {total.get('Maximum', 'N/A')}
Most Likely: Rs. {total.get('Most_Likely', 'N/A')}

Recommended Forum: {rg.get('Recommended_Forum', 'N/A')}
"""


def format_defense_arguments(data: dict) -> str:
    """Format defense arguments for opposite party lawyer."""
    cs = data.get("Case_Summary", {})
    op = cs.get("Opposite_Party_Details", {})
    sm = data.get("Simulation_Metadata", {})
    
    return f"""
Client Description: {op.get('Description', 'N/A')}

Defense Arguments:
{chr(10).join('- ' + arg for arg in op.get('Defense_Arguments', []))}

Key Counter-Arguments Available:
{chr(10).join('- ' + arg for arg in sm.get('Key_Arguments_For_Opposite_Party', []))}

Critical Moments to Watch:
{chr(10).join('- ' + m for m in sm.get('Critical_Moments', []))}
"""


def format_applicable_sections(data: dict) -> str:
    """Format applicable sections for defense."""
    lg = data.get("Legal_Grounds", {})
    sections = lg.get("Applicable_Sections", [])
    
    return "\n".join([
        f"- {s.get('Section')}: {s.get('Description')} (Relevance: {s.get('Relevance_to_Case')})"
        for s in sections
    ])


def format_consumer_arguments(data: dict) -> str:
    """Format consumer arguments for defense."""
    sm = data.get("Simulation_Metadata", {})
    return "\n".join([
        f"- {arg}" for arg in sm.get("Key_Arguments_For_Consumer", [])
    ])


def update_judgment_field(data: dict, field_path: str, value: any) -> dict:
    """Update a nested field in the judgment data."""
    keys = field_path.split(".")
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return data


def parse_judge_updates(response: str, data: dict) -> tuple[str, dict, list[dict]]:
    """Parse judge's response for any JSON updates and extract clean response."""
    import re
    
    updates = []
    clean_response = response
    
    # Find all json_update blocks
    pattern = r"```json_update\s*(\{.*?\})\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    for match in matches:
        try:
            update_info = json.loads(match)
            field = update_info.get("field", "")
            value = update_info.get("value")
            reason = update_info.get("reason", "No reason provided")
            
            if field and value is not None:
                data = update_judgment_field(data, field, value)
                updates.append({"field": field, "value": value, "reason": reason})
        except json.JSONDecodeError:
            pass
    
    # Remove the json_update blocks from the response
    clean_response = re.sub(pattern, "", response).strip()
    
    return clean_response, data, updates


def print_courtroom_header():
    """Print courtroom header."""
    print("\n" + "=" * 80)
    print("                    DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION")
    print("                              COURTROOM SIMULATION")
    print("=" * 80)


def print_phase_header(phase: str, hearing_num: int):
    """Print phase header."""
    print(f"\n{'─' * 80}")
    print(f"  HEARING #{hearing_num} | PHASE: {phase.upper()}")
    print(f"{'─' * 80}\n")


def print_speaker(speaker: str, message: str, color_code: str = ""):
    """Print a speaker's message with formatting."""
    prefix_map = {
        "JUDGE": "⚖️  HON'BLE JUDGE:",
        "DEFENSE": "👔 DEFENSE COUNSEL:",
        "CONSUMER": "👤 COMPLAINANT:",
        "SYSTEM": "📋 COURT CLERK:"
    }
    prefix = prefix_map.get(speaker, speaker + ":")
    print(f"\n{prefix}")
    print("-" * 40)
    # Word wrap the message
    words = message.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 76:
            line += (" " if line else "") + word
        else:
            print(f"  {line}")
            line = word
    if line:
        print(f"  {line}")
    print()


# ============================================================================
# Agent Classes
# ============================================================================

class JudgeAgent:
    """The Judge Agent that presides over the case."""
    
    def __init__(self, judgment_data: dict):
        self.llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.3)
        self.judgment_data = judgment_data
        self.hearing_number = 1
        self.case_phase = "opening"
        
    def get_system_prompt(self) -> str:
        """Generate the system prompt with current case state."""
        return JUDGE_SYSTEM_PROMPT.format(
            case_summary=format_case_summary(self.judgment_data),
            legal_grounds=format_legal_grounds(self.judgment_data),
            judgment_reasoning=format_judgment_reasoning(self.judgment_data),
            relief_granted=format_relief_granted(self.judgment_data),
            hearing_number=self.hearing_number,
            case_phase=self.case_phase
        )
    
    def respond(self, conversation_history: list, last_message: str) -> tuple[str, list[dict], bool]:
        """
        Generate judge's response.
        
        Returns:
            Tuple of (response_text, updates_made, case_concluded)
        """
        messages = [SystemMessage(content=self.get_system_prompt())]
        messages.extend(conversation_history)
        messages.append(HumanMessage(content=last_message))
        
        response = self.llm.invoke(messages)
        response_text = response.content
        
        # Check if verdict is being delivered
        case_concluded = "[VERDICT]" in response_text
        if case_concluded:
            response_text = response_text.replace("[VERDICT]", "").strip()
        
        # Parse any judgment updates
        clean_response, self.judgment_data, updates = parse_judge_updates(
            response_text, self.judgment_data
        )
        
        return clean_response, updates, case_concluded
    
    def advance_phase(self):
        """Advance the case phase."""
        phases = ["opening", "arguments", "evidence", "closing", "verdict"]
        current_idx = phases.index(self.case_phase)
        if current_idx < len(phases) - 1:
            self.case_phase = phases[current_idx + 1]
    
    def new_hearing(self):
        """Start a new hearing."""
        self.hearing_number += 1


class OppositePartyLawyer:
    """The Opposite Party Lawyer Agent."""
    
    def __init__(self, judgment_data: dict):
        self.llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.5)
        self.judgment_data = judgment_data
        self.synthetic_materials = []
        
    def get_system_prompt(self, last_statement: str, hearing_number: int) -> str:
        """Generate the system prompt."""
        return OPPOSITE_PARTY_LAWYER_PROMPT.format(
            case_summary=format_case_summary(self.judgment_data),
            defense_arguments=format_defense_arguments(self.judgment_data),
            applicable_sections=format_applicable_sections(self.judgment_data),
            consumer_arguments=format_consumer_arguments(self.judgment_data),
            hearing_number=hearing_number,
            last_statement=last_statement
        )
    
    def respond(self, conversation_history: list, last_statement: str, hearing_number: int) -> str:
        """Generate defense lawyer's response."""
        messages = [SystemMessage(content=self.get_system_prompt(last_statement, hearing_number))]
        messages.extend(conversation_history)
        
        response = self.llm.invoke(messages)
        return response.content


# ============================================================================
# Main Simulation
# ============================================================================

def run_courtroom_simulation(judgment_file_path: str):
    """
    Run the courtroom simulation.
    
    Args:
        judgment_file_path: Path to the judgment prediction JSON file
    """
    # Load judgment data
    print_courtroom_header()
    print(f"\n📁 Loading case file: {judgment_file_path}")
    
    judgment_data = load_judgment_json(judgment_file_path)
    original_data = json.loads(json.dumps(judgment_data))  # Deep copy
    
    # Initialize agents
    judge = JudgeAgent(judgment_data)
    defense = OppositePartyLawyer(judgment_data)
    
    # Case information
    case_title = judgment_data.get("Case_Summary", {}).get("Title", "Consumer Case")
    print(f"\n📋 CASE: {case_title}")
    print(f"📅 Date: {datetime.now().strftime('%d %B %Y')}")
    
    # Conversation history for context
    conversation_history = []
    proceedings_log = []
    
    # Opening statement from Judge
    print_phase_header("Opening", judge.hearing_number)
    
    opening_prompt = """The court is now in session. This case concerns a consumer complaint regarding 
a defective product. I have reviewed the case file and the preliminary judgment assessment.

I call upon the Complainant to present their case first. Please state your grievance clearly 
for the record."""
    
    judge_response, updates, concluded = judge.respond(conversation_history, opening_prompt)
    print_speaker("JUDGE", judge_response)
    conversation_history.append(AIMessage(content=f"[JUDGE]: {judge_response}"))
    proceedings_log.append({"speaker": "JUDGE", "message": judge_response, "hearing": 1})
    
    # Main simulation loop
    turn_count = 0
    max_turns = 20  # Safety limit
    
    while not concluded and turn_count < max_turns:
        turn_count += 1
        
        # Consumer's turn (user input)
        print("\n" + "─" * 40)
        print("YOUR TURN (Consumer/Complainant)")
        print("─" * 40)
        print("Options:")
        print("  - Type your argument/statement")
        print("  - Type 'evidence' to present evidence")
        print("  - Type 'rest' to rest your case")
        print("  - Type 'quit' to exit simulation")
        print()
        
        user_input = input("Your statement: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n⚠️  Simulation terminated by user.")
            break
        
        if user_input.lower() == 'rest':
            user_input = "Your Honor, I rest my case. I believe the evidence and arguments presented clearly establish the defect in the product and the seller's deficiency in service."
        
        print_speaker("CONSUMER", user_input)
        conversation_history.append(HumanMessage(content=f"[CONSUMER]: {user_input}"))
        proceedings_log.append({"speaker": "CONSUMER", "message": user_input, "hearing": judge.hearing_number})
        
        # Defense's turn
        print("\n💭 Defense counsel is preparing response...")
        defense_response = defense.respond(
            conversation_history, 
            user_input, 
            judge.hearing_number
        )
        print_speaker("DEFENSE", defense_response)
        conversation_history.append(AIMessage(content=f"[DEFENSE]: {defense_response}"))
        proceedings_log.append({"speaker": "DEFENSE", "message": defense_response, "hearing": judge.hearing_number})
        
        # Judge's turn
        print("\n💭 The Hon'ble Judge is considering...")
        combined_input = f"""
The Consumer has stated: "{user_input}"

The Defense Counsel has responded: "{defense_response}"

Please provide your observations, questions, or if you feel the case is ready, proceed to deliver judgment.
"""
        judge_response, updates, concluded = judge.respond(conversation_history, combined_input)
        
        # Report any judgment modifications
        if updates:
            print("\n📝 COURT RECORD UPDATE:")
            for update in updates:
                print(f"   • Field '{update['field']}' modified")
                print(f"     Reason: {update['reason']}")
        
        print_speaker("JUDGE", judge_response)
        conversation_history.append(AIMessage(content=f"[JUDGE]: {judge_response}"))
        proceedings_log.append({
            "speaker": "JUDGE", 
            "message": judge_response, 
            "hearing": judge.hearing_number,
            "updates": updates if updates else None
        })
        
        # Check for phase advancement hints
        if "next hearing" in judge_response.lower():
            judge.new_hearing()
            print_phase_header(judge.case_phase, judge.hearing_number)
        elif any(word in judge_response.lower() for word in ["closing arguments", "final arguments"]):
            judge.case_phase = "closing"
    
    # Final verdict handling
    if concluded:
        print("\n" + "=" * 80)
        print("                              FINAL JUDGMENT")
        print("=" * 80)
        
        # Generate formal verdict
        verdict_prompt = f"""Based on all proceedings, please deliver the final formal judgment in the following format:

1. Case Summary
2. Issues for Determination
3. Findings on Each Issue
4. Order/Relief Granted
5. Costs (if any)

Current Relief in Record:
{format_relief_granted(judge.judgment_data)}

Deliver the verdict in a formal, judicial tone."""

        final_verdict, _, _ = judge.respond(conversation_history, verdict_prompt)
        print(final_verdict)
    
    # Save updated judgment and proceedings
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = SIMULATION_DIR / f"courtroom_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save final judgment
    final_judgment_path = output_dir / "final_judgment.json"
    save_judgment_json(judge.judgment_data, str(final_judgment_path))
    print(f"\n✅ Final judgment saved to: {final_judgment_path}")
    
    # Save proceedings log
    proceedings_path = output_dir / "proceedings_log.json"
    with open(proceedings_path, "w", encoding="utf-8") as f:
        json.dump({
            "case_title": case_title,
            "simulation_date": datetime.now().isoformat(),
            "total_hearings": judge.hearing_number,
            "total_turns": turn_count,
            "case_concluded": concluded,
            "proceedings": proceedings_log
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Proceedings log saved to: {proceedings_path}")
    
    # Save comparison
    comparison_path = output_dir / "judgment_comparison.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump({
            "original_prediction": original_data,
            "final_judgment": judge.judgment_data
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Judgment comparison saved to: {comparison_path}")
    
    print("\n" + "=" * 80)
    print("                         SIMULATION COMPLETE")
    print("=" * 80)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a courtroom simulation based on a judgment prediction JSON file."
    )
    parser.add_argument(
        "--case-file", "-f",
        type=str,
        required=True,
        help="Path to the judgment prediction JSON file"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    case_path = Path(args.case_file)
    if not case_path.exists():
        print(f"❌ Error: Case file not found: {args.case_file}")
        exit(1)
    
    if not case_path.suffix == ".json":
        print(f"❌ Error: Case file must be a JSON file: {args.case_file}")
        exit(1)
    
    run_courtroom_simulation(str(case_path))
