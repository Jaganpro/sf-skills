<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow Governance Checklist
   2 
   3 ## Overview
   4 
   5 This checklist ensures that Salesforce Flows meet enterprise governance standards for security, performance, maintainability, and compliance. Use this before deploying flows to production.
   6 
   7 ## Pre-Development Phase
   8 
   9 ### 📋 Requirements Review
  10 
  11 - [ ] **Business requirement documented** with clear success criteria
  12 - [ ] **Stakeholders identified** (business owner, technical owner, security reviewer)
  13 - [ ] **Scope defined** (which objects, which scenarios, which users)
  14 - [ ] **Existing automation reviewed** (no conflicts with other flows, process builders, workflows)
  15 - [ ] **Alternative solutions considered** (Apex trigger vs Flow vs declarative field updates)
  16 
  17 ### 🏗️ Architecture Planning
  18 
  19 - [ ] **Orchestration pattern selected** (Parent-Child, Sequential, Conditional, or standalone)
  20 - [ ] **Subflow reuse identified** (can use existing subflows from library?)
  21 - [ ] **Data volume estimated** (how many records will this process?)
  22 - [ ] **Governor limits reviewed** (will this exceed SOQL/DML limits?)
  23 - [ ] **Integration points identified** (external callouts, platform events, Apex actions)
  24 
  25 ---
  26 
  27 ## Development Phase
  28 
  29 ### 💻 Technical Implementation
  30 
  31 #### Naming & Organization
  32 - [ ] **Flow name follows convention**: `{Type}_{Object}_{Purpose}` (e.g., `RTF_Account_UpdateIndustry`)
  33 - [ ] **Description is clear and complete** (one-sentence summary of what flow does)
  34 - [ ] **Elements have meaningful names** (no "Decision_0162847" default names)
  35 - [ ] **Variables use type prefixes** (`var` for single, `col` for collection)
  36 - [ ] **API version is current** (65.0 for Summer '26)
  37 
  38 #### Performance & Bulkification
  39 - [ ] **No DML inside loops** (CRITICAL - causes bulk failures)
  40 - [ ] **Bulkified operations** (handles collections, not single records)
  41 - [ ] **Transform element used** where applicable (faster than loops for field mapping)
  42   - Use Transform for: bulk field mapping, collection conversion, simple formulas
  43   - Use Loop for: per-record IF/ELSE, counters/flags, varying business rules
  44   - See `references/transform-vs-loop-guide.md` for decision criteria
  45   - ⚠️ Create Transform in Flow Builder UI, then deploy (complex XML)
  46 - [ ] **SOQL queries minimized** (get all needed data in fewest queries)
  47 - [ ] **Record lookups have appropriate filters** (don't query unnecessary records)
  48 
  49 #### Error Handling
  50 - [ ] **All DML operations have fault paths** connected
  51 - [ ] **Fault paths connect to error logging** (Sub_LogError or custom)
  52 - [ ] **Error messages are descriptive** (help with troubleshooting)
  53 - [ ] **Critical failures stop execution** (fail-fast pattern)
  54 - [ ] **Non-critical failures logged but don't block** (fire-and-forget for notifications)
  55 
  56 #### Security & Permissions
  57 - [ ] **Running mode documented** (System vs User mode - why?)
  58 - [ ] **Sensitive fields identified** (SSN, credit card, passwords, etc.)
  59 - [ ] **Object access documented** (which objects CREATE/READ/UPDATE/DELETE)
  60 - [ ] **Field-level security considered** (will users have access to all fields?)
  61 - [ ] **No hardcoded credentials** or sensitive data in flow
  62 
  63 #### Reusability & Maintainability
  64 - [ ] **Complex logic extracted to subflows** (>200 lines suggests need for subflow)
  65 - [ ] **Subflows are single-purpose** (do one thing well)
  66 - [ ] **Input/output variables clearly defined** (documented with descriptions)
  67 - [ ] **Magic numbers avoided** (use named constants or custom metadata)
  68 - [ ] **Auto-layout enabled** (locationX/Y = 0 for cleaner diffs)
  69 
  70 ---
  71 
  72 ## Testing Phase
  73 
  74 ### 🧪 Unit Testing
  75 
  76 - [ ] **Flow tested independently** with representative data
  77 - [ ] **All decision paths tested** (every branch, every outcome)
  78 - [ ] **Error scenarios tested** (what happens when DML fails?)
  79 - [ ] **Edge cases tested** (null values, empty strings, zero quantities)
  80 - [ ] **Variable values verified** at each step (using debug mode)
  81 
  82 ### 📊 Bulk Testing
  83 
  84 - [ ] **Tested with 200+ records** (Data Loader or bulk API)
  85 - [ ] **No governor limit errors** (SOQL, DML, CPU time all under limits)
  86 - [ ] **Performance acceptable** (<5 seconds per batch)
  87 - [ ] **Debug logs reviewed** for warnings or inefficiencies
  88 - [ ] **Simulation mode passed** (if using flow_simulator.py)
  89 
  90 ### 🔒 Security Testing
  91 
  92 - [ ] **Tested with Standard User profile** (most restrictive)
  93 - [ ] **Tested with custom profiles** that have limited object access
  94 - [ ] **Tested with different permission sets** assigned
  95 - [ ] **Verified FLS is respected** (fields without access don't cause errors)
  96 - [ ] **Verified CRUD is respected** (operations without access fail gracefully)
  97 
  98 ### 🔗 Integration Testing
  99 
 100 - [ ] **Tested with related flows** (no conflicts or race conditions)
 101 - [ ] **Tested with existing automation** (Process Builder, Workflow Rules, Apex triggers)
 102 - [ ] **Tested with Apex actions** (if flow calls Apex)
 103 - [ ] **Tested with external integrations** (platform events, HTTP callouts)
 104 - [ ] **End-to-end user acceptance testing** completed
 105 
 106 ---
 107 
 108 ## Pre-Production Phase
 109 
 110 ### 📝 Documentation
 111 
 112 - [ ] **Flow documentation generated** (using documentation template)
 113 - [ ] **Dependencies documented** (which subflows, objects, fields are required)
 114 - [ ] **Configuration notes provided** (any required custom settings, metadata)
 115 - [ ] **Rollback plan documented** (how to deactivate if issues arise)
 116 - [ ] **Support documentation created** (for help desk/support team)
 117 
 118 ### 🔍 Code Review
 119 
 120 - [ ] **Peer review completed** (another developer reviewed)
 121 - [ ] **Security review completed** (if accessing sensitive data)
 122 - [ ] **Architecture review completed** (if complex orchestration)
 123 - [ ] **Best practices validated** (all items in this checklist)
 124 - [ ] **Auto-fix recommendations applied** (from enhanced_validator.py)
 125 
 126 ### 🚦 Deployment Preparation
 127 
 128 - [ ] **Deployment plan documented** (sandbox → UAT → production)
 129 - [ ] **Change set or package created** (includes all dependencies)
 130 - [ ] **Validation deployment successful** (--dry-run passed)
 131 - [ ] **Activation strategy defined** (deploy as Draft, activate after monitoring)
 132 - [ ] **Monitoring plan in place** (how to track errors post-deployment)
 133 
 134 ---
 135 
 136 ## Production Deployment
 137 
 138 ### 🚀 Deployment Day
 139 
 140 - [ ] **Backup current automation** (export existing flows as reference)
 141 - [ ] **Deploy during low-traffic window** (minimize user impact)
 142 - [ ] **Deploy as Draft initially** (not activated until verified)
 143 - [ ] **Verify deployment successful** (flow appears in Setup → Flows)
 144 - [ ] **Test basic functionality** in production (with test records)
 145 
 146 ### 🔦 Monitoring
 147 
 148 - [ ] **Activate flow** after initial verification
 149 - [ ] **Monitor error logs** (Flow_Error_Log__c or debug logs)
 150 - [ ] **Monitor performance** (Setup → Apex Jobs, flow interview records)
 151 - [ ] **Monitor user feedback** (support tickets, user questions)
 152 - [ ] **Review after 24 hours** (any unexpected behavior?)
 153 
 154 ### 🛠️ Post-Deployment
 155 
 156 - [ ] **Document any issues** encountered during deployment
 157 - [ ] **Update documentation** with production-specific notes
 158 - [ ] **Communicate to users** (release notes, training, announcements)
 159 - [ ] **Schedule follow-up review** (1 week, 1 month)
 160 - [ ] **Archive old automation** (deactivate replaced Process Builders/Workflows)
 161 
 162 ---
 163 
 164 ## Ongoing Maintenance
 165 
 166 ### 📅 Regular Reviews
 167 
 168 - [ ] **Monthly error log review** (any recurring failures?)
 169 - [ ] **Quarterly performance review** (execution time trends)
 170 - [ ] **Bi-annual security review** (still appropriate permissions?)
 171 - [ ] **Annual architecture review** (still meets business needs?)
 172 - [ ] **Update for new API versions** (leverage latest features)
 173 
 174 ### 🔄 Change Management
 175 
 176 - [ ] **Change requests tracked** (JIRA, Salesforce cases, etc.)
 177 - [ ] **Impact analysis documented** (what will change affect?)
 178 - [ ] **Testing repeated** for changes (full checklist for major changes)
 179 - [ ] **Version history maintained** (change log in flow description)
 180 - [ ] **Deprecation plan** for old flows (when will they be deactivated?)
 181 
 182 ---
 183 
 184 ## Governance Scoring
 185 
 186 ### Calculate Your Governance Score
 187 
 188 Assign points for completed items:
 189 - **Pre-Development**: 10 items × 2 points = 20 points
 190 - **Development**: 25 items × 2 points = 50 points
 191 - **Testing**: 15 items × 3 points = 45 points
 192 - **Pre-Production**: 15 items × 3 points = 45 points
 193 - **Deployment**: 10 items × 2 points = 20 points
 194 - **Ongoing**: 10 items × 2 points = 20 points
 195 
 196 **Total Possible**: 200 points
 197 
 198 ### Governance Rating
 199 
 200 | Score | Rating | Description |
 201 |-------|--------|-------------|
 202 | 180-200 | ⭐⭐⭐⭐⭐ Excellent | Enterprise-grade governance |
 203 | 160-179 | ⭐⭐⭐⭐ Very Good | Strong governance with minor gaps |
 204 | 140-159 | ⭐⭐⭐ Good | Acceptable governance, some improvements needed |
 205 | 120-139 | ⭐⭐ Fair | Significant gaps, address before production |
 206 | < 120 | ⭐ Poor | Not ready for production deployment |
 207 
 208 **Minimum for Production**: 140+ (Good rating)
 209 
 210 ---
 211 
 212 ## Exception Process
 213 
 214 ### When to Request Exception
 215 
 216 Sometimes strict governance isn't feasible. Request exception for:
 217 - **Proof-of-concept flows** (not production-critical)
 218 - **Emergency hotfixes** (security issues, critical bugs)
 219 - **Temporary workarounds** (permanent solution in progress)
 220 
 221 ### Exception Request Template
 222 
 223 ```
 224 Flow Name: [Name]
 225 Exception Requested For: [Which checklist items?]
 226 Reason: [Why can't you comply?]
 227 Risk Assessment: [What's the risk of proceeding?]
 228 Mitigation Plan: [How will you reduce risk?]
 229 Timeline: [When will full compliance be achieved?]
 230 Approver: [Who approved this exception?]
 231 ```
 232 
 233 ---
 234 
 235 ## Quick Reference Guide
 236 
 237 ### Priority Checks (Must-Do)
 238 
 239 ✅ **Top 5 Critical Items**:
 240 1. No DML inside loops
 241 2. All DML operations have fault paths
 242 3. Tested with 200+ records (bulk testing)
 243 4. Security testing with Standard User profile
 244 5. Deployment plan and rollback documented
 245 
 246 ### Common Pitfalls
 247 
 248 ❌ **Top 5 Common Mistakes**:
 249 1. Deploying directly to production (skip sandbox testing)
 250 2. Activating immediately after deployment (skip verification)
 251 3. No error logging (can't debug production issues)
 252 4. Not testing bulk scenarios (fails with >200 records)
 253 5. Ignoring security implications (system mode without review)
 254 
 255 ---
 256 
 257 ## Resources
 258 
 259 ### Tools
 260 - **enhanced_validator.py**: Comprehensive 6-category validation (includes naming, security, performance, architecture)
 261 - **flow_simulator.py**: Bulk testing simulation
 262 
 263 ### Documentation
 264 - [Subflow Library](subflow-library.md): Reusable components
 265 - [Orchestration Guide](orchestration-guide.md): Architecture patterns
 266 - [Flow Best Practices](flow-best-practices.md): Security guidelines
 267 - [Architecture Review Template](../assets/architecture-review-template.md): Formal review process
 268 
 269 ### Salesforce Resources
 270 - [Flow Best Practices](https://help.salesforce.com/s/articleView?id=sf.flow_prep_bestpractices.htm)
 271 - [Flow Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_flows.htm)
 272 - [Security Guide](https://help.salesforce.com/s/articleView?id=sf.security_overview.htm)
 273 
 274 ---
 275 
 276 ## Version History
 277 
 278 | Version | Date | Changes |
 279 |---------|------|---------|
 280 | 1.0 | 2024-11-30 | Initial governance checklist |
 281 
 282 ---
 283 
 284 ## Support
 285 
 286 Questions about this checklist?
 287 1. Review related documentation above
 288 2. Consult with Salesforce architect or admin
 289 3. Request architecture review for complex flows
 290 
 291 **Remember**: Governance isn't gatekeeping—it's protecting your org from technical debt, security issues, and poor user experiences. Take the time to do it right! 🛡️
