from __future__ import annotations

import os
import yaml

def test_dockerfile_exists_and_valid() -> None:
    dockerfile_paths = ["Dockerfile", "mcp-server/Dockerfile", "../mcp-server/Dockerfile"]
    found_path = None
    for p in dockerfile_paths:
        if os.path.isfile(p):
            found_path = p
            break
            
    assert found_path is not None, f"Dockerfile not found in search paths: {dockerfile_paths}"
    
    with open(found_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "FROM" in content, "Dockerfile lacks FROM instruction"
    assert "CMD" in content or "ENTRYPOINT" in content, "Dockerfile lacks CMD instruction"
    assert "uvicorn" in content, "Dockerfile lacks uvicorn reference in CMD"
    assert "alembic" not in content.lower(), "Dockerfile contains forbidden alembic"

def test_deploy_workflow_valid() -> None:
    workflow_paths = [
        ".github/workflows/deploy-mcp.yml",
        "../.github/workflows/deploy-mcp.yml",
        "../../.github/workflows/deploy-mcp.yml"
    ]
    found_path = None
    for p in workflow_paths:
        if os.path.isfile(p):
            found_path = p
            break
            
    assert found_path is not None, f"deploy-mcp.yml workflow not found in search paths: {workflow_paths}"
    
    with open(found_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    on_key = "on" if "on" in data else True
    on_push = data.get(on_key, {}).get("push", {})
    paths = on_push.get("paths", [])
    assert any("mcp-server" in path for path in paths), f"Workflow on.push.paths lacks mcp-server, found {paths}"

    def _workflow_logs_into_ghcr(workflow: dict) -> bool:
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                if not str(step.get("uses", "")).startswith("docker/login-action"):
                    continue
                if step.get("with", {}).get("registry") == "ghcr.io":
                    return True
        return False

    assert _workflow_logs_into_ghcr(data), "Workflow lacks docker/login-action for ghcr.io registry"

    steps_str = yaml.dump(data)
    assert "COOLIFY_MCP_WEBHOOK" in steps_str or "COOLIFY_TOKEN" in steps_str, "Workflow lacks COOLIFY secrets reference"
    
    for job in data.get("jobs", {}).values():
        for step in job.get("steps", []):
            run_cmd = step.get("run", "")
            if "curl" in run_cmd:
                assert "http://" not in run_cmd, f"Forbidden hardcoded http:// URL in workflow run: {run_cmd}"
                if "https://" in run_cmd:
                    assert "https://mcp." not in run_cmd, "Hardcoded production webhook/domain in workflow"
