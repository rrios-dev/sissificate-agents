#!/usr/bin/env python
"""
Sissificate Agent Control Panel
Interactive dashboard for managing CrewAI agents
"""

import streamlit as st
import subprocess
import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import requests

# Configure page
st.set_page_config(
    page_title="Sissificate Agent Control Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .agent-card {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin-bottom: 0.5rem;
    }
    .task-ready {
        background: #1a3a1a;
        border-left: 4px solid #4CAF50;
    }
    .task-in-progress {
        background: #3a3a1a;
        border-left: 4px solid #FFC107;
    }
    .task-done {
        background: #1a1a3a;
        border-left: 4px solid #2196F3;
    }
    .stButton button {
        width: 100%;
    }
    .log-container {
        background: #0d1117;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)


def load_env():
    """Load environment variables"""
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    return {
        "github_token": os.environ.get("GITHUB_TOKEN", ""),
        "github_owner": os.environ.get("GITHUB_OWNER", "rrios-dev"),
        "github_repo": os.environ.get("GITHUB_REPO", "sissificate"),
        "openai_key": os.environ.get("OPENAI_API_KEY", ""),
        "project_path": os.environ.get("SISSIFICATE_PROJECT_PATH", "/Users/roberto/Documents/projects/sissificate")
    }


def fetch_github_issues(token, owner, repo, state="open"):
    """Fetch issues from GitHub"""
    if not token:
        return []
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Get issues with DEV- prefix
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers=headers,
            params={"state": state, "per_page": 100}
        )
        
        if response.status_code == 200:
            issues = response.json()
            # Filter DEV- tasks
            dev_issues = [i for i in issues if i["title"].startswith("DEV-")]
            return dev_issues
        return []
    except Exception as e:
        st.error(f"Error fetching issues: {e}")
        return []


def fetch_github_projects(token, owner):
    """Fetch GitHub Projects"""
    if not token:
        return []
    
    try:
        query = """
        query($owner: String!) {
            user(login: $owner) {
                projectsV2(first: 10) {
                    nodes {
                        id
                        number
                        title
                    }
                }
            }
        }
        """
        
        response = requests.post(
            "https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query, "variables": {"owner": owner}}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("user", {}).get("projectsV2", {}).get("nodes", [])
        return []
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return []


def run_agent(task_id, epic, agent_id, project_path):
    """Run a CrewAI agent"""
    env = load_env()
    
    cmd = [
        "python", "src/sissificate_dev/main.py",
        "--task", task_id,
        "--agent-id", str(agent_id)
    ]
    
    if epic:
        cmd.extend(["--epic", epic])
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=Path(__file__).parent,
            env={**os.environ, "SISSIFICATE_PROJECT_PATH": project_path}
        )
        return process
    except Exception as e:
        return None


def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Sissificate Agent Control Panel</h1>', unsafe_allow_html=True)
    st.markdown("Manage autonomous development agents from GitHub Projects")
    
    # Load environment
    env = load_env()
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys section
        with st.expander("🔑 API Keys", expanded=not env["openai_key"]):
            openai_key = st.text_input("OpenAI API Key", value=env["openai_key"], type="password")
            github_token = st.text_input("GitHub Token", value=env["github_token"], type="password")
            
            if st.button("Save Configuration"):
                # Update .env file
                env_content = f"""OPENAI_API_KEY={openai_key}
GITHUB_TOKEN={github_token}
GITHUB_OWNER={env['github_owner']}
GITHUB_REPO={env['github_repo']}
SISSIFICATE_PROJECT_PATH={env['project_path']}
"""
                with open(Path(__file__).parent / ".env", "w") as f:
                    f.write(env_content)
                st.success("Configuration saved!")
                st.rerun()
        
        # Project settings
        with st.expander("📁 Project Settings"):
            project_path = st.text_input("Sissificate Path", value=env["project_path"])
            owner = st.text_input("GitHub Owner", value=env["github_owner"])
            repo = st.text_input("GitHub Repo", value=env["github_repo"])
        
        # Quick stats
        st.header("📊 Quick Stats")
        if env["github_token"]:
            issues = fetch_github_issues(env["github_token"], env["github_owner"], env["github_repo"])
            dev_issues = [i for i in issues if i["title"].startswith("DEV-")]
            ready_count = len([i for i in dev_issues if not i.get("assignee")])
            st.metric("Ready Tasks", ready_count)
            st.metric("Total DEV Tasks", len(dev_issues))
        else:
            st.warning("Set GitHub token to see stats")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Tasks", "🚀 Launch Agent", "🤖 Active Agents", "📜 Logs", "📈 Analytics"
    ])
    
    # Tab 1: Tasks from GitHub
    with tab1:
        st.header("📋 Available Tasks")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_state = st.selectbox("Status", ["open", "closed", "all"], index=0)
        with col2:
            filter_epic = st.text_input("Filter by Epic (e.g., PEPIC-002)", "")
        with col3:
            search_term = st.text_input("Search", "")
        
        if env["github_token"]:
            with st.spinner("Fetching tasks from GitHub..."):
                issues = fetch_github_issues(env["github_token"], env["github_owner"], env["github_repo"], filter_state)
                
                # Filter by search and epic
                if search_term:
                    issues = [i for i in issues if search_term.lower() in i["title"].lower()]
                if filter_epic:
                    issues = [i for i in issues if filter_epic in i.get("body", "")]
                
                if issues:
                    st.subheader(f"Found {len(issues)} DEV Tasks")
                    
                    for issue in issues:
                        # Determine status style
                        has_assignee = issue.get("assignee") is not None
                        status_class = "task-in-progress" if has_assignee else "task-ready"
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="task-card {status_class}" style="padding: 1rem; margin-bottom: 0.5rem; border-radius: 0.5rem; background: #1e1e1e;">
                                <h4>{issue['title']}</h4>
                                <p>#{issue['number']} | {issue['state']} | Assignee: {issue.get('assignee', {}).get('login', 'None') if issue.get('assignee') else 'Unassigned'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_a, col_b, col_c = st.columns([2, 1, 1])
                            with col_a:
                                if st.button(f"📋 View Details", key=f"view_{issue['number']}"):
                                    st.session_state.selected_task = issue
                            with col_b:
                                if st.button(f"🚀 Launch", key=f"launch_{issue['number']}"):
                                    st.session_state.launch_task = issue['title'].split(':')[0]
                                    st.info(f"Go to 'Launch Agent' tab to configure and start")
                            with col_c:
                                st.link_button("GitHub", issue['html_url'])
                else:
                    st.info("No DEV tasks found matching criteria")
        else:
            st.warning("⚠️ GitHub token not configured. Please add it in the sidebar.")
    
    # Tab 2: Launch Agent
    with tab2:
        st.header("🚀 Launch New Agent")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Task Selection")
            
            # Manual task input or select from available
            task_input_method = st.radio("Select task by:", ["Task ID", "From Available Tasks"])
            
            if task_input_method == "Task ID":
                task_id = st.text_input("Enter Task ID (e.g., DEV-0101)", value=st.session_state.get("launch_task", ""))
            else:
                if env["github_token"]:
                    issues = fetch_github_issues(env["github_token"], env["github_owner"], env["github_repo"])
                    available = [i["title"].split(":")[0] for i in issues if not i.get("assignee")]
                    task_id = st.selectbox("Select Available Task", available) if available else ""
                else:
                    task_id = ""
                    st.warning("Configure GitHub token to see available tasks")
            
            epic_filter = st.text_input("Epic Filter (optional)", placeholder="e.g., PEPIC-002")
            
            st.subheader("Agent Configuration")
            col_a, col_b = st.columns(2)
            
            with col_a:
                agent_id = st.number_input("Agent ID", min_value=1, max_value=10, value=1)
            
            with col_b:
                agent_type = st.selectbox("Agent Type", [
                    "auto (coordinator decides)",
                    "frontend_engineer",
                    "backend_engineer",
                    "qa_engineer"
                ])
            
            dry_run = st.checkbox("Dry Run (no actual changes)", value=False)
            
            # Launch button
            if st.button("🚀 Launch Agent", type="primary", use_container_width=True):
                if not task_id:
                    st.error("Please select or enter a task ID")
                elif not env["openai_key"]:
                    st.error("OpenAI API key not configured")
                else:
                    st.session_state.agent_running = True
                    st.session_state.current_task = task_id
                    st.success(f"Agent launched for {task_id}!")
                    st.info("Check 'Active Agents' tab for progress")
        
        with col_right:
            st.subheader("Quick Presets")
            
            if st.button("🎯 Frontend Task (DEV-0101)", use_container_width=True):
                st.session_state.launch_task = "DEV-0101"
                st.rerun()
            
            if st.button("🔐 Auth Task (DEV-0102)", use_container_width=True):
                st.session_state.launch_task = "DEV-0102"
                st.rerun()
            
            if st.button("📋 Onboarding Task (DEV-0103)", use_container_width=True):
                st.session_state.launch_task = "DEV-0103"
                st.rerun()
            
            if st.button("🗺️ Map Task (DEV-0201)", use_container_width=True):
                st.session_state.launch_task = "DEV-0201"
                st.rerun()
            
            st.divider()
            
            st.subheader("Batch Launch")
            num_agents = st.number_input("Number of Agents", min_value=2, max_value=6, value=3)
            
            if st.button("🚀 Launch Swarm", use_container_width=True):
                st.info(f"Launching {num_agents} agents...")
                st.code(f"""
# Terminal commands to run:
cd {Path(__file__).parent}
source .venv/bin/activate

# Terminal 1
python src/sissificate_dev/main.py --agent-id 1 --epic PEPIC-002

# Terminal 2
python src/sissificate_dev/main.py --agent-id 2 --epic PEPIC-003

# Terminal 3
python src/sissificate_dev/main.py --agent-id 3 --epic PEPIC-004
                """, language="bash")
    
    # Tab 3: Active Agents
    with tab3:
        st.header("🤖 Active Agents")
        
        # Simulated active agents (in real implementation, this would track actual processes)
        if "agents" not in st.session_state:
            st.session_state.agents = []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Agents", len([a for a in st.session_state.agents if a.get("status") == "running"]))
        
        with col2:
            st.metric("Completed Tasks", len([a for a in st.session_state.agents if a.get("status") == "completed"]))
        
        with col3:
            st.metric("Failed Tasks", len([a for a in st.session_state.agents if a.get("status") == "failed"]))
        
        st.divider()
        
        # Agent list
        if st.session_state.agents:
            for agent in st.session_state.agents:
                with st.container():
                    col_status, col_task, col_time, col_action = st.columns([1, 3, 2, 1])
                    
                    with col_status:
                        status_emoji = {
                            "running": "🟢",
                            "completed": "✅",
                            "failed": "❌",
                            "pending": "⚪"
                        }.get(agent.get("status", "pending"), "⚪")
                        st.write(f"{status_emoji} {agent.get('status', 'unknown').title()}")
                    
                    with col_task:
                        st.write(f"**{agent.get('task', 'N/A')}**")
                        st.caption(f"Agent {agent.get('agent_id', '?')}")
                    
                    with col_time:
                        st.write(agent.get("started", "N/A"))
                    
                    with col_action:
                        if agent.get("status") == "running":
                            if st.button("⏹️ Stop", key=f"stop_{agent.get('id')}"):
                                st.warning("Agent stop requested")
        else:
            st.info("No agents have been launched yet. Go to 'Launch Agent' tab to start.")
        
        # Manual refresh
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Tab 4: Logs
    with tab4:
        st.header("📜 Agent Logs")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Filters")
            log_level = st.multiselect("Log Level", ["INFO", "WARNING", "ERROR", "DEBUG"], default=["INFO", "WARNING", "ERROR"])
            auto_refresh = st.checkbox("Auto Refresh", value=True)
            refresh_interval = st.slider("Refresh Interval (s)", 5, 60, 10)
            
            if st.button("🗑️ Clear Logs"):
                st.session_state.logs = []
        
        with col1:
            # Log display
            if "logs" not in st.session_state:
                st.session_state.logs = [
                    {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "Control Panel started"},
                    {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "Ready to launch agents"},
                ]
            
            log_text = ""
            for log in st.session_state.logs[-100:]:  # Last 100 logs
                if log["level"] in log_level:
                    color = {"INFO": "white", "WARNING": "yellow", "ERROR": "red", "DEBUG": "gray"}.get(log["level"], "white")
                    log_text += f'<span style="color: {color}">[{log["time"]}] [{log["level"]}] {log["message"]}</span><br>'
            
            st.markdown(f'<div class="log-container">{log_text}</div>', unsafe_allow_html=True)
    
    # Tab 5: Analytics
    with tab5:
        st.header("📈 Analytics & Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Task Distribution by Epic")
            # Placeholder for chart
            st.info("Chart will show task distribution across epics")
            st.bar_chart({
                "PEPIC-002 (Entry)": 4,
                "PEPIC-003 (Progression)": 2,
                "PEPIC-004 (Social)": 1,
                "PEPIC-005 (Expression)": 1,
                "PEPIC-006 (Privacy)": 1,
                "PEPIC-007 (Monetization)": 2
            })
        
        with col2:
            st.subheader("Completion Rate")
            st.metric("Completed", "0 / 11", "0%")
            st.progress(0)
            
            st.subheader("Average Task Duration")
            st.metric("Duration", "N/A", "No completed tasks yet")
        
        st.divider()
        
        st.subheader("Recent Activity")
        activity_data = [
            {"Time": "10:30", "Action": "Agent-1 started DEV-0101", "Status": "🟢 Running"},
            {"Time": "10:25", "Action": "Configuration updated", "Status": "✅ Complete"},
            {"Time": "10:20", "Action": "GitHub sync completed", "Status": "✅ Complete"},
        ]
        st.table(activity_data)


if __name__ == "__main__":
    main()