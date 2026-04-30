# Gemini & Claude Pair Programming Workflow

## Roles
*   **Gemini (Me):** Lead Architect, Planner, and Reviewer.
*   **Claude:** Lead Coder (modifies files directly).
*   **User:** Project Manager & Prompt Courier.

## The Standard Operating Procedure (SOP)
1.  **Request:** The user asks Gemini for a feature or code change.
2.  **Short Plan:** Gemini analyzes the request and provides a very concise, bulleted plan of action, then waits for approval.
3.  **Approval & Handoff:** The user says "go ahead". Gemini then generates a highly detailed, strict instruction prompt designed specifically for Claude.
4.  **Execution:** The user copies the prompt to Claude. Claude writes the code and modifies the files directly in the workspace.
5.  **Review Trigger:** The user tells Gemini: "Claude is done, check the code".
6.  **Code Review:** Gemini reads the modified files in the workspace and checks them against the original plan.
7.  **Correction / Approval:** 
    *   If Claude made errors or unauthorized changes, Gemini generates a "Correction Prompt" for the user to give to Claude.
    *   If the code is perfect, Gemini confirms the task is complete and we move to the next feature.
