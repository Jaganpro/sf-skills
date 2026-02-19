<!-- Parent: sf-apex/SKILL.md -->
   1 # Apex Security Guide
   2 
   3 ## Sharing Modes
   4 
   5 ### with sharing (Default)
   6 
   7 Use for most classes. Enforces record-level security (OWD, sharing rules).
   8 
   9 ```apex
  10 public with sharing class AccountService {
  11     public List<Account> getAccounts() {
  12         // Only returns records user has access to
  13         return [SELECT Id, Name FROM Account];
  14     }
  15 }
  16 ```
  17 
  18 ### inherited sharing
  19 
  20 Use for utility/helper classes. Inherits sharing mode from caller.
  21 
  22 ```apex
  23 public inherited sharing class QueryHelper {
  24     public static List<SObject> query(String soql) {
  25         // Sharing determined by calling class
  26         return Database.query(soql);
  27     }
  28 }
  29 ```
  30 
  31 ### without sharing
  32 
  33 Use sparingly. Only for specific system operations that require full access.
  34 
  35 ```apex
  36 public without sharing class SystemService {
  37     // DOCUMENT WHY this needs without sharing
  38     public static void updateSystemRecords(List<Record__c> records) {
  39         // Updates regardless of sharing rules
  40         update records;
  41     }
  42 }
  43 ```
  44 
  45 **Rule**: Keep `without sharing` classes small and isolated. Never expose directly to users.
  46 
  47 ---
  48 
  49 ## CRUD/FLS Enforcement
  50 
  51 ### USER_MODE (Recommended)
  52 
  53 ```apex
  54 // SOQL with USER_MODE - enforces CRUD and FLS
  55 List<Account> accounts = [
  56     SELECT Id, Name, AnnualRevenue
  57     FROM Account
  58     WITH USER_MODE
  59 ];
  60 
  61 // Database methods with AccessLevel
  62 Database.insert(records, AccessLevel.USER_MODE);
  63 Database.update(records, AccessLevel.USER_MODE);
  64 Database.delete(records, AccessLevel.USER_MODE);
  65 
  66 // Database.query with USER_MODE
  67 String query = 'SELECT Id FROM Account WHERE Name = :name';
  68 List<Account> accounts = Database.query(query, AccessLevel.USER_MODE);
  69 ```
  70 
  71 ### Security.stripInaccessible()
  72 
  73 Remove inaccessible fields before DML or returning to user:
  74 
  75 ```apex
  76 // Strip inaccessible fields before insert
  77 List<Account> accounts = getAccountsFromExternalSource();
  78 SObjectAccessDecision decision = Security.stripInaccessible(
  79     AccessType.CREATABLE,
  80     accounts
  81 );
  82 insert decision.getRecords();
  83 
  84 // Strip before returning to user
  85 List<Account> accounts = [SELECT Id, Name, Secret_Field__c FROM Account];
  86 SObjectAccessDecision decision = Security.stripInaccessible(
  87     AccessType.READABLE,
  88     accounts
  89 );
  90 return decision.getRecords();  // Secret_Field__c removed if not accessible
  91 
  92 // Check which fields were removed
  93 Set<String> removedFields = decision.getRemovedFields().get('Account');
  94 ```
  95 
  96 ### Manual Checks (Legacy)
  97 
  98 ```apex
  99 // Object-level
 100 if (!Schema.sObjectType.Account.isCreateable()) {
 101     throw new SecurityException('No create access to Account');
 102 }
 103 
 104 // Field-level
 105 if (!Schema.sObjectType.Account.fields.Name.isUpdateable()) {
 106     throw new SecurityException('No update access to Account.Name');
 107 }
 108 ```
 109 
 110 ---
 111 
 112 ## SOQL Injection Prevention
 113 
 114 ### Use Bind Variables (Preferred)
 115 
 116 ```apex
 117 // SAFE: Bind variable
 118 String name = userInput;
 119 List<Account> accounts = [SELECT Id FROM Account WHERE Name = :name];
 120 
 121 // SAFE: Dynamic query with bind
 122 String query = 'SELECT Id FROM Account WHERE Name = :name';
 123 List<Account> accounts = Database.query(query);
 124 ```
 125 
 126 ### Escape User Input (If Dynamic)
 127 
 128 ```apex
 129 // If you must build dynamic SOQL
 130 String safeName = String.escapeSingleQuotes(userInput);
 131 String query = 'SELECT Id FROM Account WHERE Name = \'' + safeName + '\'';
 132 ```
 133 
 134 ### Never Do This
 135 
 136 ```apex
 137 // VULNERABLE: Direct concatenation
 138 String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';
 139 // Attacker input: ' OR Name != '
 140 // Results in: SELECT Id FROM Account WHERE Name = '' OR Name != ''
 141 ```
 142 
 143 ---
 144 
 145 ## Named Credentials
 146 
 147 ### Never Hardcode Credentials
 148 
 149 ```apex
 150 // BAD: Hardcoded credentials
 151 Http http = new Http();
 152 HttpRequest req = new HttpRequest();
 153 req.setEndpoint('https://api.example.com');
 154 req.setHeader('Authorization', 'Bearer sk_live_abc123');  // EXPOSED!
 155 
 156 // GOOD: Named Credential
 157 HttpRequest req = new HttpRequest();
 158 req.setEndpoint('callout:MyNamedCredential/api/resource');
 159 // Authorization handled automatically
 160 ```
 161 
 162 ### Setting Up Named Credentials
 163 
 164 1. Setup → Named Credentials
 165 2. Configure authentication (OAuth, Password, etc.)
 166 3. Reference in code: `callout:CredentialName/path`
 167 
 168 ---
 169 
 170 ## Custom Settings for Bypass Flags
 171 
 172 Enable admins to disable automation without code changes:
 173 
 174 ```apex
 175 public class TriggerConfig {
 176     private static Trigger_Settings__c settings;
 177 
 178     public static Boolean isDisabled(String triggerName) {
 179         if (settings == null) {
 180             settings = Trigger_Settings__c.getInstance();
 181         }
 182 
 183         return settings?.Disable_All_Triggers__c == true ||
 184                (Boolean)settings.get('Disable_' + triggerName + '__c') == true;
 185     }
 186 }
 187 
 188 // Usage in trigger action
 189 if (TriggerConfig.isDisabled('Account')) {
 190     return;
 191 }
 192 ```
 193 
 194 ---
 195 
 196 ## Secure Apex for LWC/Aura
 197 
 198 ### AuraHandledException
 199 
 200 ```apex
 201 @AuraEnabled
 202 public static Account getAccount(Id accountId) {
 203     try {
 204         // Use USER_MODE for security
 205         return [SELECT Id, Name FROM Account WHERE Id = :accountId WITH USER_MODE];
 206     } catch (QueryException e) {
 207         throw new AuraHandledException('Account not found');
 208     } catch (Exception e) {
 209         // Log for debugging
 210         System.debug(LoggingLevel.ERROR, e.getMessage());
 211         // Return user-friendly message
 212         throw new AuraHandledException('An error occurred. Please contact support.');
 213     }
 214 }
 215 ```
 216 
 217 ### Cacheable Methods
 218 
 219 ```apex
 220 @AuraEnabled(cacheable=true)
 221 public static List<Account> getAccounts() {
 222     // Cacheable methods cannot have DML
 223     // Must be idempotent
 224     return [SELECT Id, Name FROM Account WITH USER_MODE LIMIT 100];
 225 }
 226 ```
 227 
 228 ---
 229 
 230 ## Permission Checks
 231 
 232 ### Custom Permissions
 233 
 234 ```apex
 235 public static Boolean hasCustomPermission(String permissionName) {
 236     return FeatureManagement.checkPermission(permissionName);
 237 }
 238 
 239 // Usage
 240 if (!hasCustomPermission('Access_Sensitive_Data')) {
 241     throw new SecurityException('Insufficient permissions');
 242 }
 243 ```
 244 
 245 ### Profile/Permission Set Checks
 246 
 247 ```apex
 248 // Check if user has specific permission
 249 public static Boolean canModifyAllData() {
 250     return [
 251         SELECT PermissionsModifyAllData
 252         FROM Profile
 253         WHERE Id = :UserInfo.getProfileId()
 254     ].PermissionsModifyAllData;
 255 }
 256 ```
 257 
 258 ---
 259 
 260 ## Security Review Checklist
 261 
 262 | Check | Status |
 263 |-------|--------|
 264 | Uses `with sharing` by default | ☐ |
 265 | `without sharing` justified and documented | ☐ |
 266 | SOQL uses USER_MODE or manual CRUD/FLS checks | ☐ |
 267 | No SOQL injection vulnerabilities | ☐ |
 268 | No hardcoded credentials | ☐ |
 269 | Sensitive data not exposed in debug logs | ☐ |
 270 | AuraEnabled methods have proper error handling | ☐ |
 271 | Custom permissions used for sensitive operations | ☐ |
