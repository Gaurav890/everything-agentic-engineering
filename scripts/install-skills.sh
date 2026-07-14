#!/usr/bin/env bash
set -euo pipefail

echo "Installing a restrained core skill set for Claude Code..."
echo

npx skills@latest add anthropics/skills \
  --skill frontend-design \
  --agent claude-code \
  --yes

npx skills@latest add vercel-labs/agent-skills \
  --skill react-best-practices \
  --skill web-design-guidelines \
  --skill react-native-guidelines \
  --agent claude-code \
  --yes

cat <<'EOF'

Core external skills installed.

Optional workflow plugin in Claude Code:
  /plugin install superpowers@claude-plugins-official

Optional Expo plugin when mobile/Expo is active:
  /plugin install expo@claude-plugins-official

Do not install large overlapping skill collections by default.
Review third-party skills before enabling their hooks or shell behavior.
EOF
