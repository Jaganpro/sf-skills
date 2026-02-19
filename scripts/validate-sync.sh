#!/bin/bash
# Validates that plugin.json descriptions match SKILL.md frontmatter descriptions
# Exit with error if mismatches are found

set -e

echo "🔄 Validating plugin.json ↔ SKILL.md sync..."

mismatches=0

for skill in sf-apex sf-flow sf-diagram-mermaid sf-diagram-nanobananapro sf-metadata sf-data sf-deploy sf-ai-agentforce sf-ai-agentforce-testing sf-ai-agentforce-observability sf-ai-agentforce-conversationdesign sf-ai-agentscript sf-connected-apps sf-integration sf-lwc sf-debug sf-soql sf-testing sf-permissions skill-builder util-youtube-analyzer; do
  plugin_file="./skills/$skill/.claude-plugin/plugin.json"
  skill_file="./skills/$skill/SKILL.md"

  if [ ! -f "$plugin_file" ]; then
    echo "⚠️  $skill: No plugin.json found"
    continue
  fi

  if [ ! -f "$skill_file" ]; then
    echo "⚠️  $skill: No SKILL.md found"
    continue
  fi

  # Extract description from plugin.json
  plugin_desc=$(jq -r '.description // ""' "$plugin_file" 2>/dev/null | head -1)

  # Extract first line of description from SKILL.md frontmatter
  # The description is after "description:" and may span multiple lines with ">"
  skill_desc=$(sed -n '/^description:/,/^[a-z]/p' "$skill_file" | head -3 | tail -2 | tr -d '\n' | sed 's/^  //' | head -c 100)

  # Compare first 50 characters (descriptions may be formatted differently)
  plugin_prefix="${plugin_desc:0:50}"
  skill_prefix="${skill_desc:0:50}"

  if [ -z "$plugin_desc" ] || [ -z "$skill_desc" ]; then
    echo "⚠️  $skill: Could not extract descriptions for comparison"
  elif [ "$plugin_prefix" != "$skill_prefix" ]; then
    echo "❌ $skill: Description mismatch detected"
    echo "   plugin.json: ${plugin_desc:0:80}..."
    echo "   SKILL.md:    ${skill_desc:0:80}..."
    mismatches=$((mismatches + 1))
  else
    echo "✅ $skill: Descriptions in sync"
  fi
done

if [ $mismatches -gt 0 ]; then
  echo ""
  echo "❌ Found $mismatches description mismatch(es)"
  echo "   Update plugin.json descriptions to match SKILL.md frontmatter"
  exit 1
fi

echo ""
echo "✅ All plugin.json files are in sync with SKILL.md"
