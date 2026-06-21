#!/usr/bin/env python3
"""
Create all GitHub issues from issues/ directory.

Reference system:
- Milestone bodies use file reference numbers (e.g., #013 for 001.013.xxx.md)
- Sub-issue bodies use sequential position numbers (1-indexed, across all sub-issues sorted by filename)
"""

import json
import os
import re
import subprocess
import sys

ISSUES_DIR = "issues"

def run_gh(*args):
    """Run a gh command and return stdout."""
    cmd = ["gh"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR running: {' '.join(cmd)}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
        result.check_returncode()
    return result.stdout.strip()

def parse_frontmatter(filepath):
    """Parse YAML front matter from a markdown file."""
    with open(filepath) as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].strip()

    fm = {}
    lines = fm_text.split("\n")
    i = 0
    current_list_key = None
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\w+):\s*"(.+)"\s*$', line)
        if m:
            fm[m.group(1)] = m.group(2)
            current_list_key = None
            i += 1
            continue
        m = re.match(r"^(\w+):\s+(\S.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
            current_list_key = None
            i += 1
            continue
        m = re.match(r"^(\w+):\s*$", line)
        if m:
            current_list_key = m.group(1)
            fm[current_list_key] = []
            i += 1
            continue
        m = re.match(r"^\s*-\s+(.+)\s*$", line)
        if m and current_list_key:
            fm[current_list_key].append(m.group(1))
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        current_list_key = None
        i += 1

    return fm, body, content

def get_file_ref_num(filename):
    """Extract the file reference number from a filename like 001.013.xxx.md -> '013'"""
    base = filename.replace(".md", "")
    parts = base.split(".", 2)
    if len(parts) >= 2:
        return parts[1]
    return None

def create_issue(title, body, repo, labels=None):
    """Create a GitHub issue and return its number."""
    args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
    if labels:
        # gh issue create only accepts already-existing labels, so try and fallback
        args.extend(["--label", ",".join(labels)])
    result = run_gh(*args)
    m = re.search(r"/issues/(\d+)$", result)
    if m:
        return int(m.group(1))
    print(f"Warning: Could not parse issue number from: {result}", file=sys.stderr)
    return None

def edit_issue_body(issue_number, body, repo):
    """Update an issue's body."""
    tmpfile = f"/tmp/gh_body_{issue_number}.md"
    with open(tmpfile, "w") as f:
        f.write(body)
    run_gh("issue", "edit", str(issue_number), "--repo", repo, "--body-file", tmpfile)
    os.unlink(tmpfile)

def add_to_project(issue_number):
    """Add issue to project board."""
    run_gh("project", "item-add", "3", "--owner", "skkdevcraft",
           "--repo", repo, "--id", str(issue_number))

def main():
    global repo
    
    # Detect repo
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner"],
        capture_output=True, text=True, check=True
    )
    repo_data = json.loads(result.stdout)
    repo = repo_data["nameWithOwner"]
    print(f"Repo: {repo}", file=sys.stderr)

    # Get all files sorted
    files = sorted(os.listdir(ISSUES_DIR))

    # Classify
    milestone_files = {}
    sub_issue_files = []
    for f in files:
        if not f.endswith(".md"):
            continue
        if ".000-" in f or ".000-milestone" in f:
            mnum = f.split(".")[0]
            milestone_files[mnum] = f
        else:
            sub_issue_files.append(f)

    print(f"Found {len(milestone_files)} milestones, {len(sub_issue_files)} sub-issues", file=sys.stderr)

    # Build sequential position order for sub-issues
    sub_issue_order = []  # list of (filename, file_ref_num, sequential_pos)
    for i, f in enumerate(sub_issue_files, 1):
        file_ref = get_file_ref_num(f)
        sub_issue_order.append((f, file_ref, i))

    # Phase 1: Create all sub-issues
    # Two mappings: file_ref -> GH# and seq_pos -> GH#
    file_ref_to_gh = {}
    seq_to_gh = {}
    sub_issue_bodies = {}  # file_ref -> (orig_body, gh_num, filename)

    for f, file_ref, seq_pos in sub_issue_order:
        filepath = f"{ISSUES_DIR}/{f}"
        fm, body, _ = parse_frontmatter(filepath)
        title = fm.get("title", f)
        labels = fm.get("labels", [])

        print(f"Creating sub-issue #{seq_pos} (file #{file_ref}): {title}", file=sys.stderr)
        
        gh_num = create_issue(title, body, repo, labels)
        if gh_num:
            file_ref_to_gh[file_ref] = gh_num
            seq_to_gh[seq_pos] = gh_num
            sub_issue_bodies[file_ref] = (body, gh_num, f)
        
        if gh_num:
            try:
                add_to_project(gh_num)
                print(f"  -> #{gh_num} (added to project)", file=sys.stderr)
            except Exception as e:
                print(f"  -> #{gh_num} (warning: project add failed: {e})", file=sys.stderr)

    # Display mappings
    print(f"\nSequential -> GH mapping: {json.dumps(seq_to_gh)}", file=sys.stderr)
    print(f"File ref -> GH mapping: {json.dumps(file_ref_to_gh)}", file=sys.stderr)

    # Phase 2: Update sub-issue body references (they use sequential positions)
    print("\n--- Updating sub-issue body references ---", file=sys.stderr)
    for file_ref, (orig_body, gh_num, filename) in sub_issue_bodies.items():
        def replace_seq(match):
            num = match.group(1)
            if num in seq_to_gh:
                return f"#{seq_to_gh[num]}"
            return match.group(0)
        
        new_body = re.sub(r'#(\d{3})', replace_seq, orig_body)
        if new_body != orig_body:
            print(f"  Updating #{gh_num} ({filename}) with new references", file=sys.stderr)
            edit_issue_body(gh_num, new_body, repo)

    # Phase 3: Create milestone issues with updated references (they use file ref numbers)
    milestone_gh_numbers = {}
    
    for mnum in sorted(milestone_files.keys()):
        f = milestone_files[mnum]
        filepath = f"{ISSUES_DIR}/{f}"
        fm, body, _ = parse_frontmatter(filepath)
        title = fm.get("title", f)
        labels = fm.get("labels", [])

        # Replace file # references in milestone body
        def replace_file_ref(match):
            num = match.group(1)
            if num in file_ref_to_gh:
                return f"#{file_ref_to_gh[num]}"
            return match.group(0)
        
        new_body = re.sub(r'#(\d{3})', replace_file_ref, body)
        
        print(f"Creating milestone: {title}", file=sys.stderr)
        gh_num = create_issue(title, new_body, repo, labels)
        if gh_num:
            milestone_gh_numbers[mnum] = gh_num
        
        if gh_num:
            try:
                add_to_project(gh_num)
                print(f"  -> #{gh_num} (added to project)", file=sys.stderr)
            except Exception as e:
                print(f"  -> #{gh_num} (warning: project add failed: {e})", file=sys.stderr)

    # Phase 4: Add milestone reference comments to sub-issues
    print("\n--- Adding milestone references as comments ---", file=sys.stderr)
    for file_ref, (_, gh_num, filename) in sub_issue_bodies.items():
        mnum = filename.split(".")[0]
        if mnum in milestone_gh_numbers:
            milestone_num = milestone_gh_numbers[mnum]
            comment = f"This issue is part of milestone **#{milestone_num}**"
            try:
                run_gh("issue", "comment", str(gh_num), "--repo", repo, "--body", comment)
                print(f"  Added milestone ref to #{gh_num}", file=sys.stderr)
            except Exception as e:
                print(f"  Warning: Could not comment on #{gh_num}: {e}", file=sys.stderr)
    
    # Summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total: {len(file_ref_to_gh) + len(milestone_gh_numbers)} issues", file=sys.stderr)
    print(f"  Milestones: {len(milestone_gh_numbers)}", file=sys.stderr)
    print(f"  Sub-issues: {len(file_ref_to_gh)}", file=sys.stderr)
    
    for mnum in sorted(milestone_gh_numbers):
        print(f"  Milestone M{mnum} -> #{milestone_gh_numbers[mnum]}", file=sys.stderr)
    for file_ref in sorted(file_ref_to_gh, key=int):
        print(f"  Issue #{file_ref} -> #{file_ref_to_gh[file_ref]}", file=sys.stderr)

if __name__ == "__main__":
    main()