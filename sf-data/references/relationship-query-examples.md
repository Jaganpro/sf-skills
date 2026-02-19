<!-- Parent: sf-data/SKILL.md -->
   1 # Relationship Query Examples
   2 
   3 Comprehensive SOQL relationship patterns for complex data retrieval.
   4 
   5 ## Parent-to-Child Queries (Subqueries)
   6 
   7 ### Basic Subquery
   8 ```sql
   9 SELECT Id, Name,
  10     (SELECT Id, FirstName, LastName, Email FROM Contacts)
  11 FROM Account
  12 WHERE Industry = 'Technology'
  13 ```
  14 
  15 ```bash
  16 sf data query \
  17   --query "SELECT Id, Name, (SELECT Id, FirstName, LastName FROM Contacts) FROM Account WHERE Industry = 'Technology' LIMIT 5" \
  18   --target-org dev \
  19   --json
  20 ```
  21 
  22 ### Multiple Subqueries
  23 ```sql
  24 SELECT Id, Name,
  25     (SELECT Id, Name, Title FROM Contacts),
  26     (SELECT Id, Name, Amount, StageName FROM Opportunities),
  27     (SELECT Id, CaseNumber, Subject FROM Cases)
  28 FROM Account
  29 WHERE Id = '001XXXXXXXXXXXX'
  30 ```
  31 
  32 ### Filtered Subquery
  33 ```sql
  34 SELECT Id, Name,
  35     (SELECT Id, Name, Amount
  36      FROM Opportunities
  37      WHERE StageName = 'Closed Won'
  38      ORDER BY Amount DESC
  39      LIMIT 5)
  40 FROM Account
  41 WHERE AnnualRevenue > 1000000
  42 ```
  43 
  44 ## Child-to-Parent Queries (Dot Notation)
  45 
  46 ### Basic Relationship
  47 ```sql
  48 SELECT Id, FirstName, LastName,
  49        Account.Name, Account.Industry
  50 FROM Contact
  51 WHERE Account.Industry = 'Technology'
  52 ```
  53 
  54 ```bash
  55 sf data query \
  56   --query "SELECT Id, FirstName, LastName, Account.Name, Account.Industry FROM Contact WHERE Account.Industry = 'Technology' LIMIT 10" \
  57   --target-org dev
  58 ```
  59 
  60 ### Multi-Level Traversal
  61 ```sql
  62 SELECT Id, Name, Amount,
  63        Account.Name,
  64        Account.Owner.Name,
  65        Account.Owner.Profile.Name
  66 FROM Opportunity
  67 WHERE Account.Industry = 'Finance'
  68 ```
  69 
  70 ### Custom Object Relationships
  71 ```sql
  72 -- __r suffix for custom relationships
  73 SELECT Id, Name,
  74        Custom_Parent__r.Name,
  75        Custom_Parent__r.Custom_Field__c
  76 FROM Custom_Child__c
  77 ```
  78 
  79 ## Polymorphic Relationships (TYPEOF)
  80 
  81 ### Task Who/What Fields
  82 ```sql
  83 SELECT Id, Subject, Status,
  84     TYPEOF Who
  85         WHEN Contact THEN FirstName, LastName, Email
  86         WHEN Lead THEN FirstName, LastName, Company
  87     END,
  88     TYPEOF What
  89         WHEN Account THEN Name, Industry
  90         WHEN Opportunity THEN Name, Amount, StageName
  91     END
  92 FROM Task
  93 WHERE Status = 'Open'
  94 ```
  95 
  96 ```bash
  97 sf data query \
  98   --query "SELECT Id, Subject, TYPEOF Who WHEN Contact THEN FirstName, LastName WHEN Lead THEN FirstName, LastName END FROM Task WHERE Status = 'Open' LIMIT 5" \
  99   --target-org dev \
 100   --json
 101 ```
 102 
 103 ### Event Relationships
 104 ```sql
 105 SELECT Id, Subject, StartDateTime,
 106     TYPEOF Who
 107         WHEN Contact THEN FirstName, LastName, Account.Name
 108         WHEN Lead THEN Name, Company
 109     END
 110 FROM Event
 111 WHERE StartDateTime >= TODAY
 112 ```
 113 
 114 ## Aggregate Queries
 115 
 116 ### Basic Aggregation
 117 ```sql
 118 SELECT Industry, COUNT(Id) total, SUM(AnnualRevenue) revenue
 119 FROM Account
 120 GROUP BY Industry
 121 HAVING COUNT(Id) > 10
 122 ORDER BY SUM(AnnualRevenue) DESC
 123 ```
 124 
 125 ```bash
 126 sf data query \
 127   --query "SELECT Industry, COUNT(Id) total, SUM(AnnualRevenue) revenue FROM Account GROUP BY Industry HAVING COUNT(Id) > 5" \
 128   --target-org dev
 129 ```
 130 
 131 ### Rollup by Date
 132 ```sql
 133 SELECT CALENDAR_MONTH(CloseDate) month,
 134        SUM(Amount) total,
 135        COUNT(Id) deals
 136 FROM Opportunity
 137 WHERE CloseDate = THIS_YEAR
 138 AND StageName = 'Closed Won'
 139 GROUP BY CALENDAR_MONTH(CloseDate)
 140 ORDER BY CALENDAR_MONTH(CloseDate)
 141 ```
 142 
 143 ### Aggregate with Relationships
 144 ```sql
 145 SELECT Account.Industry,
 146        COUNT(Id) opportunities,
 147        SUM(Amount) pipeline
 148 FROM Opportunity
 149 WHERE StageName NOT IN ('Closed Won', 'Closed Lost')
 150 GROUP BY Account.Industry
 151 ```
 152 
 153 ## Semi-Joins and Anti-Joins
 154 
 155 ### Semi-Join (Records WITH Related)
 156 ```sql
 157 -- Accounts that HAVE Opportunities
 158 SELECT Id, Name
 159 FROM Account
 160 WHERE Id IN (
 161     SELECT AccountId FROM Opportunity WHERE Amount > 100000
 162 )
 163 ```
 164 
 165 ### Anti-Join (Records WITHOUT Related)
 166 ```sql
 167 -- Accounts WITHOUT Contacts
 168 SELECT Id, Name
 169 FROM Account
 170 WHERE Id NOT IN (
 171     SELECT AccountId FROM Contact WHERE AccountId != null
 172 )
 173 ```
 174 
 175 ### Complex Semi-Join
 176 ```sql
 177 -- Contacts at Accounts with large deals
 178 SELECT Id, FirstName, LastName
 179 FROM Contact
 180 WHERE AccountId IN (
 181     SELECT AccountId
 182     FROM Opportunity
 183     WHERE Amount > 500000
 184     AND StageName = 'Closed Won'
 185 )
 186 ```
 187 
 188 ## Date Functions and Filters
 189 
 190 ### Date Literals
 191 ```sql
 192 SELECT Id, Name, CreatedDate
 193 FROM Account
 194 WHERE CreatedDate = THIS_WEEK
 195 -- Also: TODAY, YESTERDAY, THIS_MONTH, LAST_MONTH, THIS_YEAR, LAST_N_DAYS:7
 196 ```
 197 
 198 ### Date Functions in SELECT
 199 ```sql
 200 SELECT DAY_IN_MONTH(CreatedDate) day,
 201        WEEK_IN_YEAR(CreatedDate) week,
 202        CALENDAR_YEAR(CreatedDate) year,
 203        COUNT(Id) count
 204 FROM Lead
 205 GROUP BY DAY_IN_MONTH(CreatedDate),
 206          WEEK_IN_YEAR(CreatedDate),
 207          CALENDAR_YEAR(CreatedDate)
 208 ```
 209 
 210 ## Query Optimization Tips
 211 
 212 ### Use Indexed Fields
 213 ```sql
 214 -- GOOD: Query on indexed fields (Id, Name, CreatedDate, SystemModstamp)
 215 SELECT Id, Name FROM Account WHERE Name LIKE 'Acme%'
 216 
 217 -- BAD: Query on non-indexed custom field (full table scan)
 218 SELECT Id, Name FROM Account WHERE Custom_Unindexed__c = 'value'
 219 ```
 220 
 221 ### Limit Records Retrieved
 222 ```sql
 223 -- Always use LIMIT for exploration
 224 SELECT Id, Name FROM Account LIMIT 100
 225 
 226 -- Use OFFSET for pagination
 227 SELECT Id, Name FROM Account LIMIT 100 OFFSET 200
 228 ```
 229 
 230 ### Select Only Needed Fields
 231 ```sql
 232 -- GOOD: Only needed fields
 233 SELECT Id, Name, Industry FROM Account
 234 
 235 -- BAD: Selecting all fields
 236 SELECT Id, Name, Industry, Description, BillingStreet, BillingCity,
 237        BillingState, BillingPostalCode, BillingCountry, ...
 238 ```
 239 
 240 ## Common Errors
 241 
 242 | Error | Cause | Solution |
 243 |-------|-------|----------|
 244 | `Invalid relationship` | Wrong relationship name | Check `__r` suffix for custom |
 245 | `MALFORMED_QUERY` | Syntax error | Validate SOQL syntax |
 246 | `SELECT too complex` | Too many levels | Max 5 levels of relationships |
 247 | `Subquery limit` | >20 subqueries | Reduce number of child queries |
 248 | `Non-selective query` | No indexed filter | Add indexed field to WHERE |
