#!/usr/bin/env python
"""
Sissificate Development Crew - Main Entry Point
Run autonomous development agents from GitHub Projects
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sissificate_dev.crew import SissificateDevCrew


def run(task_id: str = None, epic: str = None, dry_run: bool = False):
    """
    Run the Sissificate Development Crew.
    
    Args:
        task_id: Specific DEV-TASK to work on (e.g., DEV-0101)
        epic: Preferred epic to work on (e.g., PEPIC-002)
        dry_run: If True, only show what would be done without executing
    """
    # Validate environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("   Get your API key from: https://platform.openai.com/api-keys")
        print("   Then add to .env: OPENAI_API_KEY=sk-xxx")
        sys.exit(1)
    
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN not set")
        print("   Create a token at: https://github.com/settings/tokens")
        print("   Scopes required: repo, project")
        sys.exit(1)
    
    # Set agent name
    agent_id = os.environ.get("AGENT_ID", "1")
    os.environ["AGENT_NAME"] = f"agent-{agent_id}"
    
    print("=" * 60)
    print("🚀 Sissificate Development Crew")
    print("=" * 60)
    print(f"Agent: {os.environ['AGENT_NAME']}")
    print(f"Task: {task_id or 'Auto-select'}")
    print(f"Epic: {epic or 'Any'}")
    print(f"Dry Run: {dry_run}")
    print(f"Project Path: {os.environ.get('SISSIFICATE_PROJECT_PATH')}")
    print("=" * 60)
    print()
    
    if dry_run:
        print("📋 DRY RUN MODE - No changes will be made")
        print()
    
    try:
        # Create and run crew
        crew_instance = SissificateDevCrew()
        crew = crew_instance.crew(task_id=task_id, epic=epic)
        result = crew.kickoff()
        
        print()
        print("=" * 60)
        print("✅ Crew Execution Complete")
        print("=" * 60)
        print(result)
        
        return result
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Crew Execution Failed")
        print("=" * 60)
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sissificate Development Crew")
    parser.add_argument("--task", "-t", help="Specific DEV-TASK to work on (e.g., DEV-0101)")
    parser.add_argument("--epic", "-e", help="Preferred epic to work on (e.g., PEPIC-002)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run mode")
    parser.add_argument("--agent-id", "-a", default="1", help="Agent ID (default: 1)")
    
    args = parser.parse_args()
    
    # Set agent ID
    os.environ["AGENT_ID"] = args.agent_id
    
    run(task_id=args.task, epic=args.epic, dry_run=args.dry_run)