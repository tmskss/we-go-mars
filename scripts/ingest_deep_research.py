#!/usr/bin/env python3
"""
Script to automate the deep research process with a hardcoded question.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.deep_researcher import DeepResearcherAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

HARDCODED_QUESTION = "Summarize the mission context for a crewed Mars expedition with emphasis on radiation protection: dominant radiation hazards per phase, and current NASA/ESA/CNSA dose limits."

async def main():
    try:
        agent = DeepResearcherAgent()
        logger.info(f"Starting Deep Research with question: {HARDCODED_QUESTION}")
        
        # Run interactively so the user can see progress and provide input if needed (though we automate most)
        hypothesis = await agent.execute(HARDCODED_QUESTION, interactive_mode=True)
        
        if hypothesis.report_path:
            logger.info(f"Deep Research complete. Report generated at: {hypothesis.report_path}")
        else:
            logger.error("Deep Research finished but no report path was returned.")
            
    except Exception as e:
        logger.error(f"An error occurred during deep research: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
