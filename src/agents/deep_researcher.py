"""
Deep Researcher Agent.

This agent performs initial deep research on the user's hypothesis,
gathering context from the RAG system and generating clarifying questions.

Owner: [ASSIGN TEAMMATE]
"""

from src.agents.base import BaseAgent

from src.models.hypothesis import Hypothesis
import os
import sys
import time
import select
import subprocess
import pty
import pathlib
import asyncio

SYSTEM_PROMPT = """You are a Deep Research Agent specialized in scientific literature analysis.

Your responsibilities:
1. Analyze the user's research hypothesis
2. Search the literature knowledge base for relevant context
3. Identify gaps and ambiguities in the hypothesis
4. Generate clarifying questions to refine the hypothesis

When analyzing a hypothesis:
- Look for similar research that has been done
- Identify the key variables and relationships
- Note any assumptions that need verification
- Consider feasibility and scope

Output Format:
- Provide a summary of relevant literature findings
- List specific clarifying questions (max 5)
- Suggest initial high-level requirements
"""


class DeepResearcherAgent(BaseAgent[str, Hypothesis]):
    """
    Performs deep research on the hypothesis and generates clarifying questions.

    Input: User hypothesis (str)
    Output: Hypothesis object with context and clarifying questions
    """

    def __init__(self):
        super().__init__(
            name="deep_researcher",
            instructions=SYSTEM_PROMPT,
        )

    async def execute(self, input_data: str, interactive_mode: bool = False) -> Hypothesis:
        """
        Research the hypothesis and generate clarifying questions.

        Args:
            input_data: The user's raw hypothesis text
            interactive_mode: Whether to allow manual user input during research

        Returns:
            Hypothesis object with context and questions populated
        """
        report_path = await asyncio.to_thread(self._run_deep_research_cli, input_data, interactive_mode)

        hypothesis = Hypothesis(original_text=input_data)
        if report_path:
            hypothesis.report_path = report_path
        else:
            raise ValueError("Deep research failed to generate a report.")

        return hypothesis

    def _run_deep_research_cli(self, question: str, interactive: bool) -> str:
        deep_research_dir = pathlib.Path(__file__).parents[3] / "deep-research"
        report_file = deep_research_dir / "report.md"

        if not deep_research_dir.exists():
            print(f"[!] Error: Directory {deep_research_dir} does not exist.")
            return ""

        print(f"[*] Starting Deep Research Automation")
        print(f"[*] Target Directory: {deep_research_dir}")

        master_fd, slave_fd = pty.openpty()

        process = subprocess.Popen(
            ["npm", "start"],
            cwd=str(deep_research_dir),
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            text=True
        )
        os.close(slave_fd)

        buffer = ""
        interaction_log = []
        state = "WAIT_FOR_QUESTION"

        print(f"[*] Process started (PID: {process.pid}). Automating initial steps...")

        try:
            while True:
                if process.poll() is not None:
                    print(f"\n[*] Process exited with code {process.returncode}")
                    break

                rlist = [master_fd]
                if state == "INTERACTIVE" and interactive:
                    rlist.append(sys.stdin.fileno())

                read_ready, _, _ = select.select(rlist, [], [], 0.05)

                if master_fd in read_ready:
                    try:
                        data = os.read(master_fd, 1024)
                    except OSError:
                        break
                    
                    if not data:
                        break

                    text_chunk = data.decode('utf-8', errors='replace')
                    sys.stdout.write(text_chunk)
                    sys.stdout.flush()
                    buffer += text_chunk
                    
                    if state == "INTERACTIVE":
                        if "?" in text_chunk or ":" in text_chunk:
                             interaction_log.append(f"Q: {text_chunk.strip()}\n")
                             
                             if not interactive:
                                 print(f"\n[AUTO] Non-interactive: Sending Default (Enter)")
                                 os.write(master_fd, b"\n")
                                 time.sleep(0.5)

                    if state == "WAIT_FOR_QUESTION":
                        if "?" in buffer or "question" in buffer.lower():
                            print(f"\n[AUTO] Sending Question: {question}")
                            msg = f"{question}\n".encode('utf-8')
                            os.write(master_fd, msg)
                            buffer = ""
                            state = "WAIT_FOR_BREADTH"

                    elif state == "WAIT_FOR_BREADTH":
                        if "breadth" in buffer.lower() and ":" in buffer:
                            print(f"\n[AUTO] Sending Breadth: (default)")
                            os.write(master_fd, b"\n")
                            buffer = ""
                            state = "WAIT_FOR_DEPTH"
                    
                    elif state == "WAIT_FOR_DEPTH":
                        if "depth" in buffer.lower() and ":" in buffer:
                            print(f"\n[AUTO] Sending Depth: (default)")
                            os.write(master_fd, b"\n")
                            buffer = ""
                            state = "WAIT_FOR_REPORT_TYPE"

                    elif state == "WAIT_FOR_REPORT_TYPE":
                        if "report/answer" in buffer.lower() or "generate" in buffer.lower():
                            print(f"\n[AUTO] Sending Report Type: (default)")
                            os.write(master_fd, b"\n")
                            buffer = ""
                            state = "INTERACTIVE"
                            print(f"\n[*] Initial setup complete. Entering INTERACTIVE mode. You can type now.")

                if state == "INTERACTIVE" and interactive and sys.stdin.fileno() in read_ready:
                    user_input = os.read(sys.stdin.fileno(), 1024)
                    if user_input:
                        os.write(master_fd, user_input)
                        interaction_log.append(f"A: {user_input.decode('utf-8', errors='replace').strip()}\n")

        except OSError as e:
            print(f"\n[!] OS Error: {e}")
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user.")
        
        if process.poll() is None:
            process.terminate()
            process.wait()

        os.close(master_fd)
        
        # Save log
        log_file = pathlib.Path("interaction_log.txt")
        report_content = ""
        if report_file.exists():
             report_content = report_file.read_text(encoding='utf-8')

        try:
            final_log = "".join(interaction_log)
            if report_content:
                final_log += "\n\n--- FINAL REPORT ---\n" + report_content
            log_file.write_text(final_log, encoding='utf-8')
        except Exception as e:
            print(f"[!] Error saving interaction log: {e}")

        if report_file.exists():
            timestamp = int(time.time())
            new_report_path = report_file.with_name(f"report_{timestamp}.md")
            report_file.rename(new_report_path)
            return str(new_report_path)

        return ""
