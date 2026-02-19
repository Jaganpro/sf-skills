<!-- Parent: sf-data/SKILL.md -->
   1 # CRUD Workflow Example
   2 
   3 Complete end-to-end example of data operations using sf-data skill.
   4 
   5 ## Scenario
   6 
   7 Create a Deal Desk workflow test environment with:
   8 - Accounts with varying revenue tiers
   9 - Contacts as decision makers
  10 - Opportunities at different stages
  11 
  12 ## Phase 1: Discovery (sf-metadata)
  13 
  14 ```
  15 Skill(skill="sf-metadata")
  16 Request: "Describe object Account in org dev - show required fields and picklist values"
  17 ```
  18 
  19 **Response shows:**
  20 - Required: Name
  21 - Picklists: Industry, Type, Rating
  22 
  23 ## Phase 2: Create Records
  24 
  25 ### sf CLI - Single Record
  26 ```bash
  27 sf data create record \
  28   --sobject Account \
  29   --values "Name='Enterprise Corp' Industry='Technology' AnnualRevenue=5000000" \
  30   --target-org dev \
  31   --json
  32 ```
  33 
  34 **Output:**
  35 ```json
  36 {
  37   "status": 0,
  38   "result": {
  39     "id": "001XXXXXXXXXXXX",
  40     "success": true
  41   }
  42 }
  43 ```
  44 
  45 ### sf CLI - Query Created Record
  46 ```bash
  47 sf data query \
  48   --query "SELECT Id, Name, Industry, AnnualRevenue FROM Account WHERE Name = 'Enterprise Corp'" \
  49   --target-org dev \
  50   --json
  51 ```
  52 
  53 ## Phase 3: Update Records
  54 
  55 ### Update Single Record
  56 ```bash
  57 sf data update record \
  58   --sobject Account \
  59   --record-id 001XXXXXXXXXXXX \
  60   --values "Rating='Hot' Type='Customer - Direct'" \
  61   --target-org dev
  62 ```
  63 
  64 ### Verify Update
  65 ```bash
  66 sf data get record \
  67   --sobject Account \
  68   --record-id 001XXXXXXXXXXXX \
  69   --target-org dev
  70 ```
  71 
  72 ## Phase 4: Create Related Records
  73 
  74 ### Create Contact for Account
  75 ```bash
  76 sf data create record \
  77   --sobject Contact \
  78   --values "FirstName='John' LastName='Smith' AccountId='001XXXXXXXXXXXX' Title='CTO'" \
  79   --target-org dev
  80 ```
  81 
  82 ### Create Opportunity
  83 ```bash
  84 sf data create record \
  85   --sobject Opportunity \
  86   --values "Name='Enterprise Deal' AccountId='001XXXXXXXXXXXX' StageName='Prospecting' CloseDate=2025-03-31 Amount=250000" \
  87   --target-org dev
  88 ```
  89 
  90 ## Phase 5: Query Relationships
  91 
  92 ### Parent-to-Child (Subquery)
  93 ```bash
  94 sf data query \
  95   --query "SELECT Id, Name, (SELECT Id, Name, Title FROM Contacts), (SELECT Id, Name, Amount, StageName FROM Opportunities) FROM Account WHERE Name = 'Enterprise Corp'" \
  96   --target-org dev \
  97   --json
  98 ```
  99 
 100 ### Child-to-Parent (Dot Notation)
 101 ```bash
 102 sf data query \
 103   --query "SELECT Id, Name, Account.Name, Account.Industry FROM Contact WHERE Account.Name = 'Enterprise Corp'" \
 104   --target-org dev
 105 ```
 106 
 107 ## Phase 6: Delete Records
 108 
 109 ### Delete in Correct Order
 110 Children first, then parents:
 111 
 112 ```bash
 113 # Delete Opportunities
 114 sf data delete record \
 115   --sobject Opportunity \
 116   --record-id 006XXXXXXXXXXXX \
 117   --target-org dev
 118 
 119 # Delete Contacts
 120 sf data delete record \
 121   --sobject Contact \
 122   --record-id 003XXXXXXXXXXXX \
 123   --target-org dev
 124 
 125 # Delete Account
 126 sf data delete record \
 127   --sobject Account \
 128   --record-id 001XXXXXXXXXXXX \
 129   --target-org dev
 130 ```
 131 
 132 ## Anonymous Apex Alternative
 133 
 134 For complex operations, use Anonymous Apex:
 135 
 136 ```apex
 137 // Create complete hierarchy in one transaction
 138 Account acc = new Account(
 139     Name = 'Enterprise Corp',
 140     Industry = 'Technology',
 141     AnnualRevenue = 5000000
 142 );
 143 insert acc;
 144 
 145 Contact con = new Contact(
 146     FirstName = 'John',
 147     LastName = 'Smith',
 148     AccountId = acc.Id,
 149     Title = 'CTO'
 150 );
 151 insert con;
 152 
 153 Opportunity opp = new Opportunity(
 154     Name = 'Enterprise Deal',
 155     AccountId = acc.Id,
 156     ContactId = con.Id,
 157     StageName = 'Prospecting',
 158     CloseDate = Date.today().addDays(90),
 159     Amount = 250000
 160 );
 161 insert opp;
 162 
 163 System.debug('Created hierarchy: Account=' + acc.Id + ', Contact=' + con.Id + ', Opp=' + opp.Id);
 164 ```
 165 
 166 Execute:
 167 ```bash
 168 sf apex run --file create-hierarchy.apex --target-org dev
 169 ```
 170 
 171 ## Validation Score
 172 
 173 ```
 174 Score: 125/130 ⭐⭐⭐⭐⭐ Excellent
 175 ├─ Query Efficiency: 25/25 (indexed fields, no N+1)
 176 ├─ Bulk Safety: 23/25 (single records OK for demo)
 177 ├─ Data Integrity: 20/20 (all required fields)
 178 ├─ Security & FLS: 20/20 (no PII exposed)
 179 ├─ Test Patterns: 12/15 (single record demo)
 180 ├─ Cleanup & Isolation: 15/15 (proper delete order)
 181 └─ Documentation: 10/10 (fully documented)
 182 ```
