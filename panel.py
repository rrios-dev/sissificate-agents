#!/usr/bin/env python
"""
Sissificate Agent Control Panel v2
Developer-first interface for autonomous agents
"""

import streamlit as st
import subprocess
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import requests
from typing import Optional, List, Dict, Any

st.set_page_config(
    page_title="Sissificate Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "Sissificate Autonomous Development Agents",
        'Report a bug': "https://github.com/rrios-dev/sissificate-agents/issues",
    }
)

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .block-container { padding-top: 1rem !important; }
    
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #262626;
    }
    
    .logo { font-size: 1.5rem; font-weight: 700; color: #fff; }
    .logo span { color: #a855f7; }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #262626 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; line-height: 1; }
    .metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
    .metric-ready .metric-value { color: #22c55e; }
    .metric-active .metric-value { color: #eab308; }
    .metric-done .metric-value { color: #3b82f6; }
    .metric-failed .metric-value { color: #ef4444; }
    .metric-time .metric-value { color: #a855f7; }
    
    .kanban-column {
        background: #0d0d0d;
        border-radius: 12px;
        padding: 0.75rem;
        min-height: 400px;
    }
    .kanban-header {
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kanban-header.ready { background: #14532d; }
    .kanban-header.active { background: #422006; }
    .kanban-header.done { background: #1e3a5f; }
    .kanban-header.failed { background: #450a0a; }
    
    .task-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .task-card:hover { border-color: #a855f7; transform: translateY(-2px); }
    .task-card.selected { border-color: #a855f7; background: #1f1a2e; }
    
    .task-id { font-size: 0.75rem; font-weight: 600; color: #a855f7; margin-bottom: 0.25rem; }
    .task-title { font-size: 0.875rem; color: #fff; margin-bottom: 0.5rem; }
    .task-meta { font-size: 0.7rem; color: #666; display: flex; gap: 0.5rem; }
    
    .quick-actions {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4); }
    
    .btn-secondary {
        background: #262626;
        color: white;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-secondary:hover { border-color: #555; }
    
    .command-palette {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .search-input {
        background: #0d0d0d;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: white;
        width: 100%;
        font-size: 0.875rem;
    }
    .search-input:focus { outline: none; border-color: #a855f7; }
    
    .sidebar-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    
    .config-section {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .status-dot.running { background: #22c55e; animation: pulse 2s infinite; }
    .status-dot.idle { background: #666; }
    .status-dot.error { background: #ef4444; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .log-panel {
        background: #0d0d0d;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 0.75rem;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .toast {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    }
    .toast.success { border-color: #22c55e; }
    .toast.error { border-color: #ef4444; }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    div[data-testid="stExpander"] { background: transparent; border: none; }
    div[data-testid="stExpander"] details { background: #1a1a1a; border-radius: 8px; }
    
    .stButton button {
        background: transparent;
        border: none;
        color: white;
        padding: 0.25rem 0.5rem;
    }
    .stButton button:hover { background: #333; }
    
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
    .empty-state-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    
    [data-testid="stVerticalBlock"] > div:has(.metric-card) {
        gap: 0.75rem;
    }
</style>
"""


def load_env() -> Dict[str, str]:
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


@st.cache_resource(ttl=30)
def fetch_github_issues(token: str, owner: str, repo: str) -> List[Dict]:
    if not token:
        return []
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers=headers,
            params={"state": "open", "per_page": 100}
        )
        if response.status_code == 200:
            issues = response.json()
            return [i for i in issues if i.get("title", "").startswith("DEV-")]
        return []
    except Exception:
        return []


def categorize_tasks(issues: List[Dict]) -> Dict[str, List[Dict]]:
    ready, active, done, failed = [], [], [], []
    for issue in issues:
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        if "in-progress" in labels:
            active.append(issue)
        elif "done" in labels or "completed" in labels:
            done.append(issue)
        elif "failed" in labels or "blocked" in labels:
            failed.append(issue)
        else:
            ready.append(issue)
    return {"ready": ready, "active": active, "done": done, "failed": failed}


def save_env(env: Dict[str, str]):
    env_content = f"""OPENAI_API_KEY={env['openai_key']}
GITHUB_TOKEN={env['github_token']}
GITHUB_OWNER={env['github_owner']}
GITHUB_REPO={env['github_repo']}
SISSIFICATE_PROJECT_PATH={env['project_path']}
"""
    with open(Path(__file__).parent / ".env", "w") as f:
        f.write(env_content)


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    
    if "selected_task" not in st.session_state:
        st.session_state.selected_task = None
    if "command_input" not in st.session_state:
        st.session_state.command_input = ""
    if "agents" not in st.session_state:
        st.session_state.agents = []
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "show_config" not in st.session_state:
        st.session_state.show_config = False
    
    env = load_env()
    
    with st.container():
        st.markdown("""
        <div class="header">
            <div class="logo">🤖 <span>Sissificate</span> Agents</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not env["openai_key"] or not env["github_token"]:
            st.warning("⚠️ Configuration required - Click ⚙️ Settings below")
    
    issues = fetch_github_issues(env["github_token"], env["github_owner"], env["github_repo"])
    categorized = categorize_tasks(issues)
    
    total_ready = len(categorized["ready"])
    total_active = len(categorized["active"])
    total_done = len(categorized["done"])
    total_failed = len(categorized["failed"])
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card metric-ready">
            <div class="metric-value">{total_ready}</div>
            <div class="metric-label">Ready</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card metric-active">
            <div class="metric-value">{total_active}</div>
            <div class="metric-label">Active</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card metric-done">
            <div class="metric-value">{total_done}</div>
            <div class="metric-label">Done</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card metric-failed">
            <div class="metric-value">{total_failed}</div>
            <div class="metric-label">Failed</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card metric-time">
            <div class="metric-value">--</div>
            <div class="metric-label">Avg Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_cmd, col_settings = st.columns([4, 1])
    with col_cmd:
        command = st.text_input(
            "Command", 
            placeholder="Type 'launch DEV-0101' or 'settings' (press Enter)...",
            key="command_input",
            label_visibility="collapsed"
        )
    with col_settings:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_config = not st.session_state.show_config
    
    if command:
        cmd_lower = command.lower().strip()
        if cmd_lower.startswith("launch "):
            task_id = command.split(" ", 1)[1].strip().upper()
            if not task_id.startswith("DEV-"):
                task_id = f"DEV-{task_id}"
            st.session_state.selected_task = task_id
            st.session_state.show_launch = True
            st.toast(f"🎯 Ready to launch: {task_id}", icon="✅")
        elif cmd_lower == "settings":
            st.session_state.show_config = True
        elif cmd_lower == "refresh":
            st.cache_resource.clear()
            st.rerun()
        elif cmd_lower == "clear":
            st.session_state.logs = []
            st.toast("Logs cleared", icon="🗑️")
    
    if st.session_state.get("show_config"):
        with st.expander("⚙️ Configuration", expanded=True):
            st.subheader("API Keys")
            c1, c2 = st.columns(2)
            with c1:
                openai_key = st.text_input("OpenAI API Key", value=env["openai_key"], type="password")
            with c2:
                github_token = st.text_input("GitHub Token", value=env["github_token"], type="password")
            
            st.subheader("Project Settings")
            c3, c4 = st.columns(2)
            with c3:
                owner = st.text_input("GitHub Owner", value=env["github_owner"])
            with c4:
                repo = st.text_input("GitHub Repo", value=env["github_repo"])
            
            project_path = st.text_input("Project Path", value=env["project_path"])
            
            if st.button("💾 Save Configuration", type="primary"):
                env.update({
                    "openai_key": openai_key,
                    "github_token": github_token,
                    "github_owner": owner,
                    "github_repo": repo,
                    "project_path": project_path
                })
                save_env(env)
                st.toast("Configuration saved!", icon="✅")
                st.session_state.show_config = False
                st.rerun()
    
    st.markdown("### 📋 Kanban Board")
    
    c1, c2, c3, c4 = st.columns(4)
    
    columns = [
        ("🟢 READY", "ready", categorized["ready"], "#14532d"),
        ("🟡 ACTIVE", "active", categorized["active"], "#422006"),
        ("🔵 DONE", "done", categorized["done"], "#1e3a5f"),
        ("🔴 FAILED", "failed", categorized["failed"], "#450a0a")
    ]
    
    for col, (title, key, tasks, color) in zip([c1, c2, c3, c4], columns):
        with col:
            st.markdown(f"""
            <div class="kanban-column">
                <div class="kanban-header {key}">
                    <span>{title}</span>
                    <span>{len(tasks)}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if not tasks:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <div>No tasks</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for task in tasks:
                    task_id = task["title"].split(":")[0]
                    task_title = ":".join(task["title"].split(":")[1:]).strip() if ":" in task["title"] else task["title"]
                    is_selected = st.session_state.selected_task == task_id
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="task-card {'selected' if is_selected else ''}" 
                             onclick="this.classList.toggle('selected')">
                            <div class="task-id">{task_id}</div>
                            <div class="task-title">{task_title[:40]}{'...' if len(task_title) > 40 else ''}</div>
                            <div class="task-meta">
                                <span>#{task['number']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if key == "ready":
                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("▶️", key=f"launch_{task['number']}", help="Launch agent"):
                                    st.session_state.selected_task = task_id
                                    st.session_state.show_launch = True
                            with btn_col2:
                                st.link_button("🔗", task["html_url"], help="View on GitHub")
    
    st.markdown("---")
    
    if st.session_state.get("show_launch") and st.session_state.selected_task:
        with st.expander(f"🚀 Launch Agent for {st.session_state.selected_task}", expanded=True):
            task_id = st.session_state.selected_task
            
            c1, c2 = st.columns(2)
            with c1:
                agent_id = st.selectbox("Agent ID", range(1, 7), index=0)
            with c2:
                epic = st.text_input("Epic Filter (optional)", placeholder="PEPIC-002")
            
            dry_run = st.checkbox("Dry Run (no changes)", value=False)
            
            b1, b2, b3 = st.columns([2, 1, 1])
            with b1:
                if st.button("🚀 Launch Agent", type="primary", use_container_width=True):
                    if not env["openai_key"]:
                        st.error("❌ OpenAI API key not configured")
                    else:
                        cmd = ["python", "src/sissificate_dev/main.py", "--task", task_id, "--agent-id", str(agent_id)]
                        if epic:
                            cmd.extend(["--epic", epic])
                        if dry_run:
                            cmd.append("--dry-run")
                        
                        st.code(" ".join(cmd), language="bash")
                        
                        st.session_state.agents.append({
                            "id": len(st.session_state.agents) + 1,
                            "task": task_id,
                            "agent_id": agent_id,
                            "status": "pending",
                            "started": datetime.now().strftime("%H:%M:%S")
                        })
                        
                        st.toast(f"🚀 Agent launched for {task_id}!", icon="✅")
                        st.session_state.show_launch = False
            
            with b2:
                if st.button("Cancel"):
                    st.session_state.show_launch = False
                    st.rerun()
    
    st.markdown("### 🤖 Active Agents")
    
    if st.session_state.agents:
        for agent in st.session_state.agents:
            c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
            with c1:
                status_icon = {"running": "🟢", "completed": "✅", "failed": "❌", "pending": "⚪"}.get(agent["status"], "⚪")
                st.write(f"{status_icon} Agent {agent['agent_id']}")
            with c2:
                st.write(f"**{agent['task']}**")
            with c3:
                st.write(agent["started"])
            with c4:
                if agent["status"] == "running":
                    if st.button("⏹️", key=f"stop_{agent['id']}"):
                        agent["status"] = "stopped"
    else:
        st.info("No agents running. Select a task from the Kanban board to launch.")
    
    st.markdown("### 📜 Recent Logs")
    
    log_col1, log_col2, log_col3 = st.columns([3, 1, 1])
    with log_col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    with log_col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.logs = []
    
    if not st.session_state.logs:
        st.session_state.logs = [
            {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "Control panel initialized"},
        ]
    
    log_text = ""
    for log in st.session_state.logs[-20:]:
        color = {"INFO": "#888", "WARNING": "#eab308", "ERROR": "#ef4444", "DEBUG": "#666"}.get(log["level"], "#888")
        log_text += f'<span style="color:{color}">[{log["time"]}] [{log["level"]}] {log["message"]}</span><br>'
    
    st.markdown(f'<div class="log-panel">{log_text}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
