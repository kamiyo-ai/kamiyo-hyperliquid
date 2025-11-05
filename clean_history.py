#!/usr/bin/env python3
"""Clean git history of AI references and make commits professional."""

import re
import subprocess
import sys

# Map of old commit messages to new professional ones
COMMIT_REWRITES = {
    "📚 Add Phase 3 documentation - Polish & Architecture Decision Records":
        "Add architecture decision records and technical documentation",

    "🔧 Fix critical gaps - Integrate DeFi features and instrument observability":
        "Integrate DeFi feature engineering and observability metrics",

    "📋 Document FIX_GAPS.md execution completion - 100/100 achieved":
        "Update implementation status documentation",

    "📊 Add production observability and monitoring":
        "Add Prometheus metrics and health check endpoints",

    "🧠 Add DeFi-specific ML feature engineering":
        "Implement DeFi-specific feature engineering for ML models",

    "✅ Add historical incident validation tests":
        "Add historical incident validation test suite",

    "📚 Add comprehensive test documentation and excellence journey":
        "Add testing documentation and guides",

    "🔧 Centralize Hyperliquid configuration - Fix address inconsistency":
        "Centralize Hyperliquid configuration",

    "🔧 Clean up Claude settings file":
        "Clean up configuration files",

    "📋 Add critical bugs documentation - Production ready":
        "Document critical fixes and production readiness",

    "🚨 CRITICAL FIX: Async/await bugs + timezone - Production blockers":
        "Fix async/await architecture and timezone handling",

    "Add final session summary - A+ (98/100) achieved":
        "Update project status",

    "📋 Final Handoff: Complete DEVELOPMENT_PLAN_A+++ Execution":
        "Complete implementation phase",

    "🎯 Day 14 Complete: Final Validation & Professional Infrastructure":
        "Add validation suite and infrastructure improvements",

    "🚀 Phase 1-3 Complete: Transform to A++ Grant-Ready Status":
        "Complete core monitoring features and ML integration",

    "🤖 Add ML-powered security monitoring - Phase 2 complete":
        "Implement ML-based anomaly detection",
}

def remove_emojis(text):
    """Remove all emojis from text."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

def clean_commit_message(subject, body):
    """Clean a commit message of AI references and emojis."""
    # Rewrite known subjects
    if subject in COMMIT_REWRITES:
        subject = COMMIT_REWRITES[subject]
    else:
        # Remove emojis
        subject = remove_emojis(subject)

    # Clean body
    if body:
        lines = body.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip AI-generated lines
            if any(skip in line for skip in [
                'Generated with', 'Claude Code', 'Co-Authored-By: Claude',
                'claude.com', 'anthropic.com'
            ]):
                continue
            # Remove emojis
            line = remove_emojis(line)
            if line.strip():
                cleaned_lines.append(line)
        body = '\n'.join(cleaned_lines).strip()

    return subject, body

def main():
    """Rewrite git history to remove AI traces."""
    print("This will rewrite git history. Make sure you have a backup!")
    print("Press Ctrl+C to cancel or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)

    # Create the filter script
    filter_script = """#!/usr/bin/env python3
import sys
import re

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\\U0001F600-\\U0001F64F"
        u"\\U0001F300-\\U0001F5FF"
        u"\\U0001F680-\\U0001F6FF"
        u"\\U0001F1E0-\\U0001F1FF"
        u"\\U00002702-\\U000027B0"
        u"\\U000024C2-\\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

# Read commit message
msg = sys.stdin.read()
lines = msg.split('\\n')

# Clean subject
subject = remove_emojis(lines[0])

# Clean body - remove AI references
cleaned_lines = [subject]
for line in lines[1:]:
    if any(skip in line for skip in [
        'Generated with', 'Claude Code', 'Co-Authored-By: Claude',
        'claude.com', 'anthropic.com', '🤖', '✅', '📚', '🔧'
    ]):
        continue
    line = remove_emojis(line)
    if line.strip():
        cleaned_lines.append(line)

print('\\n'.join(cleaned_lines))
"""

    # Write filter script
    with open('/tmp/git-msg-filter.py', 'w') as f:
        f.write(filter_script)
    subprocess.run(['chmod', '+x', '/tmp/git-msg-filter.py'])

    # Run git filter-repo
    cmd = [
        'git', 'filter-repo',
        '--force',
        '--commit-callback',
        '''
commit.author_name = b'KAMIYO'
commit.author_email = b'dev@kamiyo.ai'
commit.committer_name = b'KAMIYO'
commit.committer_email = b'dev@kamiyo.ai'
''',
        '--msg-filter', '/tmp/git-msg-filter.py'
    ]

    subprocess.run(cmd)
    print("\nGit history rewritten successfully!")
    print("All commits now authored by: KAMIYO <dev@kamiyo.ai>")
    print("All AI references removed.")

if __name__ == '__main__':
    main()
