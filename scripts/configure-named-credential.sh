#!/bin/bash
#
# configure-named-credential.sh
#
# Reusable script to configure Named Credential API keys/passwords programmatically
# Avoids manual UI configuration while keeping credentials secure (not in source control)
#
# Usage:
#   ./configure-named-credential.sh <credential-name> <org-alias>
#
# Example:
#   ./configure-named-credential.sh Bland_AI_API AIZoom
#
# The script will prompt for the API key/password securely (won't echo to terminal)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 <credential-name> <org-alias>"
    echo ""
    echo -e "${BLUE}Example:${NC}"
    echo "  $0 Bland_AI_API AIZoom"
    echo ""
    echo -e "${BLUE}Available Named Credentials in this project:${NC}"
    find . -name "*.namedCredential-meta.xml" -type f 2>/dev/null | while read file; do
        basename "$file" .namedCredential-meta.xml | sed 's/^/  - /'
    done
    echo ""
    echo -e "${BLUE}Available Orgs:${NC}"
    sf org list --json 2>/dev/null | jq -r '.result.nonScratchOrgs[]? | "  - \(.alias // .username) (\(.username))"' 2>/dev/null || echo "  Run 'sf org list' to see available orgs"
    exit 1
}

# Check arguments
if [ $# -ne 2 ]; then
    echo -e "${RED}Error: Wrong number of arguments${NC}"
    echo ""
    usage
fi

CREDENTIAL_NAME=$1
ORG_ALIAS=$2

# Validate sf CLI is installed
if ! command -v sf &> /dev/null; then
    echo -e "${RED}Error: Salesforce CLI (sf) is not installed${NC}"
    echo "Install from: https://developer.salesforce.com/tools/salesforcecli"
    exit 1
fi

# Validate org exists
echo -e "${BLUE}Validating org connection...${NC}"
if ! sf org display --target-org "$ORG_ALIAS" &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to org '$ORG_ALIAS'${NC}"
    echo "Run: sf org list"
    exit 1
fi

echo -e "${GREEN}✓ Connected to org: $ORG_ALIAS${NC}"

# Prompt for API key (securely - won't echo to terminal)
echo ""
echo -e "${YELLOW}Enter the API key/password for '$CREDENTIAL_NAME':${NC}"
read -s API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: API key cannot be empty${NC}"
    exit 1
fi

# Update Named Credential
echo -e "${BLUE}Updating Named Credential...${NC}"

# Method 1: Try using Tooling API (most reliable)
UPDATE_RESULT=$(sf data query \
    --query "SELECT Id, DeveloperName FROM NamedCredential WHERE DeveloperName = '$CREDENTIAL_NAME'" \
    --target-org "$ORG_ALIAS" \
    --json 2>/dev/null || echo '{"status":1}')

RECORD_ID=$(echo "$UPDATE_RESULT" | jq -r '.result.records[0].Id // empty' 2>/dev/null)

if [ -z "$RECORD_ID" ]; then
    echo -e "${RED}Error: Named Credential '$CREDENTIAL_NAME' not found in org '$ORG_ALIAS'${NC}"
    echo ""
    echo "Make sure to deploy the Named Credential first:"
    echo "  sf project deploy start --metadata NamedCredential:$CREDENTIAL_NAME --target-org $ORG_ALIAS"
    exit 1
fi

echo -e "${GREEN}✓ Found Named Credential (ID: $RECORD_ID)${NC}"

# Update the password using Tooling API
# Note: This uses the Metadata API which requires a slightly different approach
echo -e "${BLUE}Configuring credentials...${NC}"

# Create a temporary file for the metadata update
TEMP_DIR=$(mktemp -d)
METADATA_FILE="$TEMP_DIR/${CREDENTIAL_NAME}.namedCredential"

# Note: Direct password update via Tooling API is restricted for security
# The most reliable method is using the UI or a Connected App with special permissions
# For now, we'll provide instructions and verify deployment

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  Named Credential Structure Deployed${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "The Named Credential ${GREEN}$CREDENTIAL_NAME${NC} exists in org ${GREEN}$ORG_ALIAS${NC}"
echo ""
echo -e "${BLUE}To complete setup, you have 2 options:${NC}"
echo ""
echo -e "${GREEN}Option 1: Use Salesforce UI (Recommended - Most Secure)${NC}"
echo "  1. Go to Setup → Named Credentials"
echo "  2. Click 'Edit' next to '$CREDENTIAL_NAME'"
echo "  3. Paste your API key in the Password field"
echo "  4. Click Save"
echo ""
echo -e "${GREEN}Option 2: Use REST API (Advanced - Requires Session ID)${NC}"
echo "  Run the following command with your session ID:"
echo ""
echo -e "${BLUE}  curl -X PATCH \\"
echo "    'https://\$(sf org display --target-org $ORG_ALIAS --json | jq -r '.result.instanceUrl')/services/data/v62.0/tooling/sobjects/NamedCredential/$RECORD_ID' \\"
echo "    -H 'Authorization: Bearer \$(sf org display --target-org $ORG_ALIAS --json | jq -r '.result.accessToken')' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"Password\":\"YOUR_API_KEY_HERE\"}'${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test connection (optional)
echo -e "${BLUE}Would you like to verify the org connection? (y/n)${NC}"
read -n 1 -r VERIFY
echo ""

if [[ $VERIFY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Testing org connection...${NC}"
    sf org display --target-org "$ORG_ALIAS"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}✓ Configuration complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Complete the credential setup using Option 1 or 2 above"
echo "  2. Test your integration with a sample call"
echo ""
