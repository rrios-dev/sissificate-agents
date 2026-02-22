#!/usr/bin/env python
"""
Sissificate Development Crew
Autonomous agents for implementing DEV-TASKs from GitHub Projects
"""

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from typing import List
import os
import subprocess
import json
import requests


# Custom Tools for Sissificate Development
@tool
def read_file(file_path: str) -> str:
    """Read a file from the Sissificate project."""
    project_path = os.environ.get("SISSIFICATE_PROJECT_PATH", "/Users/roberto/Documents/projects/sissificate")
    full_path = os.path.join(project_path, file_path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {full_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file in the Sissificate project."""
    project_path = os.environ.get("SISSIFICATE_PROJECT_PATH", "/Users/roberto/Documents/projects/sissificate")
    full_path = os.path.join(project_path, file_path)
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def run_command(command: str) -> str:
    """Run a shell command in the Sissificate project directory."""
    project_path = os.environ.get("SISSIFICATE_PROJECT_PATH", "/Users/roberto/Documents/projects/sissificate")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds"
    except Exception as e:
        return f"Error running command: {str(e)}"


@tool
def github_rest_request(method: str, endpoint: str, data: str = "{}") -> str:
    """Make a GitHub REST API request. Data should be JSON string."""
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        return "Error: GITHUB_TOKEN not set"
    
    url = f"https://api.github.com{endpoint}"
    
    try:
        import json as json_lib
        json_data = json_lib.loads(data) if data else None
        
        response = requests.request(
            method=method,
            url=url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json=json_data,
            timeout=30
        )
        
        return json_lib.dumps({
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }, indent=2)
    except Exception as e:
        return f"Error making GitHub request: {str(e)}"


class SissificateDevCrew:
    """Sissificate Development Crew"""
    
    def __init__(self):
        self.agents = self._create_agents()
        self.tasks = []
    
    def _create_agents(self) -> List[Agent]:
        """Create all agents"""
        
        devops_coordinator = Agent(
            role="DevOps Coordinator",
            goal="Coordinate task execution, manage GitHub issues, and prevent conflicts between agents",
            backstory="""You are a DevOps coordinator who manages the workflow between multiple agents. 
            You query GitHub Projects for available tasks, assign them to appropriate agents, and ensure 
            no conflicts occur. You update GitHub issues with progress and completion status.""",
            tools=[read_file, write_file, run_command, github_rest_request],
            verbose=True,
            allow_delegation=True
        )
        
        frontend_engineer = Agent(
            role="Senior Frontend Engineer",
            goal="Implement UI components, pages, and user-facing features with React, Next.js, and Tailwind CSS",
            backstory="""You are a senior frontend engineer with 10+ years of experience in React, Next.js App Router, 
            TypeScript, and Tailwind CSS. You follow mobile-first design principles, implement proper a11y 
            attributes, and write clean, maintainable code. You always read existing files before modifying them.""",
            tools=[read_file, write_file, run_command],
            verbose=True,
            allow_delegation=False
        )
        
        backend_engineer = Agent(
            role="Senior Backend Engineer",
            goal="Implement API routes, database schemas, and server-side logic with Supabase/InsForge",
            backstory="""You are a senior backend engineer specializing in Next.js API routes, PostgreSQL with Supabase,
            Row Level Security (RLS), and RESTful API design. You ensure data integrity, proper validation,
            and secure implementations.""",
            tools=[read_file, write_file, run_command],
            verbose=True,
            allow_delegation=False
        )
        
        qa_engineer = Agent(
            role="QA Engineer",
            goal="Write tests, verify implementations, and ensure quality standards are met",
            backstory="""You are a QA engineer who ensures code quality through Playwright E2E tests, 
            accessibility audits, and manual verification. You verify that implementations match specifications and meet acceptance criteria.""",
            tools=[read_file, write_file, run_command],
            verbose=True,
            allow_delegation=False
        )
        
        return [devops_coordinator, frontend_engineer, backend_engineer, qa_engineer]
    
    def create_task(self, task_id: str = None, epic: str = None) -> List[Task]:
        """Create tasks for the crew"""
        
        tasks = []
        
        # Task 1: Fetch available task from GitHub
        fetch_task = Task(
            description=f"""Query GitHub for available DEV-TASKs with status "Ready".
            
            Use github_rest_request to GET /repos/rrios-dev/sissificate/issues with:
            - state: open
            - labels: (empty to get all)
            
            Find issues starting with "DEV-" that have no assignee.
            Target task: {task_id or "Any available"}
            Target epic: {epic or "Any"}
            
            Return the task ID, title, and issue number for the first available task matching criteria.
            """,
            expected_output="JSON object with task_id, title, epic, issue_number, status",
            agent=self.agents[0]  # devops_coordinator
        )
        tasks.append(fetch_task)
        
        # Task 2: Implement the task
        implement_task = Task(
            description="""Based on the task fetched, implement the code changes:
            
            1. Read the DEV-TASK specification from docs/workboard/development/tasks/DEV-XXXX.md
            2. Read any existing related files
            3. Implement the required changes following the specification
            4. Write tests if required
            5. Run validation commands (lint, build, test)
            
            Follow all project conventions and patterns found in existing code.
            """,
            expected_output="Summary of files created/modified and validation results",
            agent=self.agents[1]  # frontend_engineer (will delegate to backend if needed)
        )
        tasks.append(implement_task)
        
        # Task 3: Validate and report
        validate_task = Task(
            description="""Validate the implementation:
            
            1. Run: bun run lint
            2. Run: bun run build
            3. Run: bun run test:a11y
            4. Verify acceptance criteria from the DEV-TASK
            
            Report pass/fail for each criterion.
            """,
            expected_output="Validation report with pass/fail status for each criterion",
            agent=self.agents[3]  # qa_engineer
        )
        tasks.append(validate_task)
        
        return tasks
    
    def crew(self, task_id: str = None, epic: str = None) -> Crew:
        """Creates the Sissificate Development crew"""
        
        tasks = self.create_task(task_id, epic)
        
        return Crew(
            agents=self.agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )