<!-- Parent: sf-integration/SKILL.md -->
   1 # Named Credentials Automation Guide
   2 
   3 This guide explains how to automate Named Credential configuration using the sf-integration helper scripts.
   4 
   5 > **Key Insight:** Enhanced Named Credentials (API 60+) can be configured programmatically using `ConnectApi.NamedCredentials` - no UI required!
   6 
   7 ---
   8 
   9 ## Overview
  10 
  11 Enhanced Named Credentials = **External Credential** + **Named Credential** + **Endpoint Security**
  12 
  13 ```
  14 External Credential (stores the API key securely)
  15          ↓
  16 Named Credential (references the External Credential)
  17          ↓
  18 Your HTTP Callout (uses callout:NamedCredentialName)
  19 ```
  20 
  21 ### Why Enhanced Named Credentials?
  22 
  23 | Benefit | Description |
  24 |---------|-------------|
  25 | **Security** | AES-256 encryption by Salesforce platform |
  26 | **Flexibility** | Supports Custom, Basic, OAuth, JWT protocols |
  27 | **Portability** | Easier to manage across multiple orgs |
  28 | **Automation** | Configurable via ConnectApi (no UI required) |
  29 | **Compliance** | Passes PCI-DSS, SOC 2 audits |
  30 
  31 ---
  32 
  33 ## Deployment Order
  34 
  35 **CRITICAL:** Deploy components in this exact order:
  36 
  37 ```bash
  38 # 1. Deploy External Credential (defines the credential structure)
  39 sf project deploy start \
  40   --source-dir force-app/main/default/externalCredentials/YourAPI.externalCredential-meta.xml \
  41   --target-org YourOrg
  42 
  43 # 2. Deploy Named Credential (references the External Credential)
  44 sf project deploy start \
  45   --source-dir force-app/main/default/namedCredentials/YourAPI.namedCredential-meta.xml \
  46   --target-org YourOrg
  47 
  48 # 3. Deploy endpoint security (allows outbound HTTP calls)
  49 sf project deploy start \
  50   --source-dir force-app/main/default/cspTrustedSites/YourAPI.cspTrustedSite-meta.xml \
  51   --target-org YourOrg
  52 
  53 # 4. Set the API key using our automation script
  54 ./scripts/configure-named-credential.sh YourOrg
  55 ```
  56 
  57 ---
  58 
  59 ## Automation Scripts
  60 
  61 ### `configure-named-credential.sh`
  62 
  63 **Purpose:** Sets API keys for Enhanced Named Credentials using ConnectApi
  64 
  65 **Usage:**
  66 ```bash
  67 ./scripts/configure-named-credential.sh <org-alias>
  68 ```
  69 
  70 **What it does:**
  71 1. Validates org connection via `sf org display`
  72 2. Checks External Credential exists via SOQL
  73 3. Prompts for API key securely (input hidden)
  74 4. Generates Apex using `ConnectApi.NamedCredentials.createCredential()`
  75 5. Handles create vs. patch automatically
  76 
  77 **Under the hood:**
  78 ```apex
  79 ConnectApi.CredentialInput creds = new ConnectApi.CredentialInput();
  80 creds.externalCredential = 'YourExternalCredential';
  81 creds.principalName = 'yourPrincipalName';
  82 creds.authenticationProtocol = ConnectApi.CredentialAuthenticationProtocol.Custom;
  83 
  84 Map<String, ConnectApi.CredentialValueInput> params = new Map<String, ConnectApi.CredentialValueInput>();
  85 ConnectApi.CredentialValueInput apiKey = new ConnectApi.CredentialValueInput();
  86 apiKey.encrypted = true;
  87 apiKey.value = 'YOUR_API_KEY';
  88 params.put('apiKey', apiKey);
  89 
  90 creds.credentials = params;
  91 ConnectApi.NamedCredentials.createCredential(creds);
  92 ```
  93 
  94 ### `set-api-credential.sh`
  95 
  96 **Purpose:** Stores API keys in Custom Settings (legacy/dev approach)
  97 
  98 **Usage:**
  99 ```bash
 100 # Secure input (recommended)
 101 ./scripts/set-api-credential.sh <setting-name> - <org-alias>
 102 
 103 # Direct input
 104 ./scripts/set-api-credential.sh <setting-name> <api-key> <org-alias>
 105 ```
 106 
 107 **When to use:**
 108 - Dev/test environments
 109 - CI/CD pipelines (no Apex execution)
 110 - Simple API key auth via query parameters
 111 
 112 **Not recommended for production** - use Enhanced Named Credentials instead.
 113 
 114 ---
 115 
 116 ## Complete Example: Weather API
 117 
 118 ### Step 1: Create Metadata
 119 
 120 **External Credential:**
 121 ```xml
 122 <?xml version="1.0" encoding="UTF-8"?>
 123 <ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
 124     <authenticationProtocol>Custom</authenticationProtocol>
 125     <externalCredentialParameters>
 126         <parameterGroup>weatherAPIKey</parameterGroup>
 127         <parameterName>weatherAPIKey</parameterName>
 128         <parameterType>NamedPrincipal</parameterType>
 129         <sequenceNumber>1</sequenceNumber>
 130     </externalCredentialParameters>
 131     <label>Weather API</label>
 132 </ExternalCredential>
 133 ```
 134 
 135 **Named Credential:**
 136 ```xml
 137 <?xml version="1.0" encoding="UTF-8"?>
 138 <NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
 139     <allowMergeFieldsInBody>false</allowMergeFieldsInBody>
 140     <allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
 141     <calloutStatus>Enabled</calloutStatus>
 142     <label>Weather API</label>
 143     <namedCredentialParameters>
 144         <parameterName>Url</parameterName>
 145         <parameterType>Url</parameterType>
 146         <parameterValue>https://api.weather.com</parameterValue>
 147     </namedCredentialParameters>
 148     <namedCredentialParameters>
 149         <externalCredential>WeatherAPI</externalCredential>
 150         <parameterName>ExternalCredential</parameterName>
 151         <parameterType>Authentication</parameterType>
 152     </namedCredentialParameters>
 153     <namedCredentialType>SecuredEndpoint</namedCredentialType>
 154 </NamedCredential>
 155 ```
 156 
 157 ### Step 2: Deploy and Configure
 158 
 159 ```bash
 160 # Deploy all metadata
 161 sf project deploy start --metadata ExternalCredential:WeatherAPI \
 162   --metadata NamedCredential:WeatherAPI \
 163   --metadata CspTrustedSite:WeatherAPI \
 164   --target-org MyOrg
 165 
 166 # Configure API key
 167 ./scripts/configure-named-credential.sh MyOrg
 168 ```
 169 
 170 ### Step 3: Use in Apex
 171 
 172 ```apex
 173 HttpRequest req = new HttpRequest();
 174 req.setEndpoint('callout:WeatherAPI/forecast?city=London');
 175 req.setMethod('GET');
 176 
 177 HttpResponse res = new Http().send(req);
 178 System.debug(res.getBody());
 179 ```
 180 
 181 The API key is automatically included - no manual credential handling!
 182 
 183 ---
 184 
 185 ## Troubleshooting
 186 
 187 | Error | Cause | Fix |
 188 |-------|-------|-----|
 189 | "External Credential not found" | Not deployed or wrong name | Deploy first, check spelling |
 190 | "Named Credential not found" | Not deployed | Deploy after External Credential |
 191 | "No existing credentials to update" | Using patch instead of create | Script handles automatically |
 192 | "Unable to connect" | Missing endpoint security | Deploy CSP Trusted Site |
 193 
 194 ---
 195 
 196 ## Related Documentation
 197 
 198 - [named-credentials-guide.md](./named-credentials-guide.md) - Template reference
 199 - [external-services-guide.md](./external-services-guide.md) - OpenAPI integration
 200 - [security-best-practices.md](./security-best-practices.md) - Security patterns
