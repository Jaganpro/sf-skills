<!-- Parent: sf-diagram-nanobananapro/SKILL.md -->
   1 # Examples
   2 
   3 Example prompts and outputs for sf-diagram-nanobananapro.
   4 
   5 ## ERD Examples
   6 
   7 ```bash
   8 # Basic CRM ERD
   9 gemini --yolo "/generate 'Salesforce ERD diagram: Account (blue), Contact (green), Opportunity (yellow). Show relationships with arrows. Clean white background.'"
  10 
  11 # Custom Object ERD
  12 gemini --yolo "/generate 'ERD diagram for custom objects: Project__c, Task__c, Resource__c. Master-detail and lookup relationships shown.'"
  13 ```
  14 
  15 ## LWC Mockup Examples
  16 
  17 ```bash
  18 # Data Table Mockup
  19 gemini --yolo "/generate 'Lightning datatable mockup showing Account records with columns: Name, Industry, Annual Revenue. Include search bar and pagination.'"
  20 
  21 # Record Form Mockup
  22 gemini --yolo "/generate 'Salesforce Lightning record form for Contact object. Show Name, Email, Phone, Account lookup fields.'"
  23 ```
  24 
  25 ## Architecture Examples
  26 
  27 ```bash
  28 # Integration Flow
  29 gemini --yolo "/generate 'Integration architecture diagram: Salesforce to ERP sync via MuleSoft. Show Platform Events, Named Credentials, External Services.'"
  30 ```
  31 
  32 ## Output Location
  33 
  34 Generated images are saved to `~/nanobanana-output/`
