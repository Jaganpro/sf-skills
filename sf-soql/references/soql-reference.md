<!-- Parent: sf-soql/SKILL.md -->
   1 # SOQL Quick Reference
   2 
   3 ## Query Structure
   4 
   5 ```sql
   6 SELECT fields
   7 FROM object
   8 [WHERE conditions]
   9 [WITH filter]
  10 [GROUP BY fields]
  11 [HAVING conditions]
  12 [ORDER BY fields [ASC|DESC] [NULLS FIRST|LAST]]
  13 [LIMIT number]
  14 [OFFSET number]
  15 [FOR UPDATE]
  16 ```
  17 
  18 ---
  19 
  20 ## Operators
  21 
  22 ### Comparison Operators
  23 
  24 | Operator | Description | Example |
  25 |----------|-------------|---------|
  26 | `=` | Equal | `Name = 'Acme'` |
  27 | `!=` | Not equal | `Status != 'Closed'` |
  28 | `<` | Less than | `Amount < 1000` |
  29 | `<=` | Less than or equal | `Amount <= 1000` |
  30 | `>` | Greater than | `Amount > 1000` |
  31 | `>=` | Greater than or equal | `Amount >= 1000` |
  32 | `LIKE` | Pattern match | `Name LIKE 'Acme%'` |
  33 | `IN` | In list | `Status IN ('New', 'Open')` |
  34 | `NOT IN` | Not in list | `Type NOT IN ('Other')` |
  35 | `INCLUDES` | Multi-select contains | `Skills__c INCLUDES ('Java')` |
  36 | `EXCLUDES` | Multi-select excludes | `Skills__c EXCLUDES ('Java')` |
  37 
  38 ### Logical Operators
  39 
  40 | Operator | Description | Example |
  41 |----------|-------------|---------|
  42 | `AND` | Both conditions | `A = 1 AND B = 2` |
  43 | `OR` | Either condition | `A = 1 OR B = 2` |
  44 | `NOT` | Negate condition | `NOT (A = 1)` |
  45 
  46 ### LIKE Patterns
  47 
  48 | Pattern | Matches |
  49 |---------|---------|
  50 | `'Acme%'` | Starts with "Acme" |
  51 | `'%Corp'` | Ends with "Corp" |
  52 | `'%test%'` | Contains "test" |
  53 | `'A_me'` | "A" + any char + "me" |
  54 
  55 ---
  56 
  57 ## Date Literals
  58 
  59 ### Relative Dates
  60 
  61 | Literal | Description |
  62 |---------|-------------|
  63 | `TODAY` | Current day |
  64 | `YESTERDAY` | Previous day |
  65 | `TOMORROW` | Next day |
  66 | `THIS_WEEK` | Current week (Sun-Sat) |
  67 | `LAST_WEEK` | Previous week |
  68 | `NEXT_WEEK` | Next week |
  69 | `THIS_MONTH` | Current month |
  70 | `LAST_MONTH` | Previous month |
  71 | `NEXT_MONTH` | Next month |
  72 | `THIS_QUARTER` | Current quarter |
  73 | `LAST_QUARTER` | Previous quarter |
  74 | `NEXT_QUARTER` | Next quarter |
  75 | `THIS_YEAR` | Current year |
  76 | `LAST_YEAR` | Previous year |
  77 | `NEXT_YEAR` | Next year |
  78 | `THIS_FISCAL_QUARTER` | Current fiscal quarter |
  79 | `THIS_FISCAL_YEAR` | Current fiscal year |
  80 
  81 ### N Days/Weeks/Months/Years
  82 
  83 | Literal | Description |
  84 |---------|-------------|
  85 | `LAST_N_DAYS:n` | Last n days |
  86 | `NEXT_N_DAYS:n` | Next n days |
  87 | `LAST_N_WEEKS:n` | Last n weeks |
  88 | `NEXT_N_WEEKS:n` | Next n weeks |
  89 | `LAST_N_MONTHS:n` | Last n months |
  90 | `NEXT_N_MONTHS:n` | Next n months |
  91 | `LAST_N_QUARTERS:n` | Last n quarters |
  92 | `NEXT_N_QUARTERS:n` | Next n quarters |
  93 | `LAST_N_YEARS:n` | Last n years |
  94 | `NEXT_N_YEARS:n` | Next n years |
  95 
  96 ### Specific Dates
  97 
  98 ```sql
  99 -- Date only
 100 WHERE CloseDate = 2024-12-31
 101 
 102 -- DateTime
 103 WHERE CreatedDate >= 2024-01-01T00:00:00Z
 104 ```
 105 
 106 ---
 107 
 108 ## Aggregate Functions
 109 
 110 | Function | Description | Example |
 111 |----------|-------------|---------|
 112 | `COUNT()` | Count all rows | `SELECT COUNT() FROM Account` |
 113 | `COUNT(field)` | Count non-null values | `SELECT COUNT(Email) FROM Contact` |
 114 | `COUNT_DISTINCT(field)` | Count unique values | `SELECT COUNT_DISTINCT(Industry) FROM Account` |
 115 | `SUM(field)` | Sum of values | `SELECT SUM(Amount) FROM Opportunity` |
 116 | `AVG(field)` | Average of values | `SELECT AVG(Amount) FROM Opportunity` |
 117 | `MIN(field)` | Minimum value | `SELECT MIN(Amount) FROM Opportunity` |
 118 | `MAX(field)` | Maximum value | `SELECT MAX(Amount) FROM Opportunity` |
 119 
 120 ---
 121 
 122 ## Date Functions
 123 
 124 | Function | Returns | Example |
 125 |----------|---------|---------|
 126 | `CALENDAR_YEAR(date)` | Year (e.g., 2024) | `SELECT CALENDAR_YEAR(CloseDate) FROM Opportunity` |
 127 | `CALENDAR_QUARTER(date)` | Quarter (1-4) | `SELECT CALENDAR_QUARTER(CloseDate) FROM Opportunity` |
 128 | `CALENDAR_MONTH(date)` | Month (1-12) | `SELECT CALENDAR_MONTH(CloseDate) FROM Opportunity` |
 129 | `DAY_IN_MONTH(date)` | Day (1-31) | `SELECT DAY_IN_MONTH(CreatedDate) FROM Account` |
 130 | `DAY_IN_WEEK(date)` | Day (1=Sun, 7=Sat) | `SELECT DAY_IN_WEEK(CreatedDate) FROM Account` |
 131 | `DAY_IN_YEAR(date)` | Day (1-366) | `SELECT DAY_IN_YEAR(CreatedDate) FROM Account` |
 132 | `WEEK_IN_MONTH(date)` | Week (1-5) | `SELECT WEEK_IN_MONTH(CreatedDate) FROM Account` |
 133 | `WEEK_IN_YEAR(date)` | Week (1-53) | `SELECT WEEK_IN_YEAR(CreatedDate) FROM Account` |
 134 | `HOUR_IN_DAY(date)` | Hour (0-23) | `SELECT HOUR_IN_DAY(CreatedDate) FROM Account` |
 135 | `FISCAL_YEAR(date)` | Fiscal year | `SELECT FISCAL_YEAR(CloseDate) FROM Opportunity` |
 136 | `FISCAL_QUARTER(date)` | Fiscal quarter | `SELECT FISCAL_QUARTER(CloseDate) FROM Opportunity` |
 137 | `FISCAL_MONTH(date)` | Fiscal month | `SELECT FISCAL_MONTH(CloseDate) FROM Opportunity` |
 138 
 139 ---
 140 
 141 ## Relationship Queries
 142 
 143 ### Child-to-Parent (Dot Notation)
 144 
 145 ```sql
 146 -- Standard objects
 147 SELECT Contact.Name, Contact.Account.Name FROM Contact
 148 
 149 -- Custom objects (use __r)
 150 SELECT Child__c.Name, Child__c.Parent__r.Name FROM Child__c
 151 ```
 152 
 153 ### Parent-to-Child (Subquery)
 154 
 155 ```sql
 156 -- Standard objects
 157 SELECT Id, (SELECT Id FROM Contacts) FROM Account
 158 
 159 -- Custom objects (use __r)
 160 SELECT Id, (SELECT Id FROM Children__r) FROM Parent__c
 161 ```
 162 
 163 ---
 164 
 165 ## WITH Clauses
 166 
 167 | Clause | Description |
 168 |--------|-------------|
 169 | `WITH SECURITY_ENFORCED` | Enforce FLS (throws exception if no access) |
 170 | `WITH USER_MODE` | Respect sharing and FLS |
 171 | `WITH SYSTEM_MODE` | Bypass sharing rules |
 172 
 173 ---
 174 
 175 ## Governor Limits
 176 
 177 | Limit | Synchronous | Asynchronous |
 178 |-------|-------------|--------------|
 179 | Total SOQL Queries | 100 | 200 |
 180 | Records Retrieved | 50,000 | 50,000 |
 181 | QueryLocator Rows | 10,000,000 | 10,000,000 |
 182 | OFFSET Maximum | 2,000 | 2,000 |
 183 | Subqueries | 20 | 20 |
 184 | Relationship Depth | 5 levels | 5 levels |
 185 
 186 ---
 187 
 188 ## Index Usage
 189 
 190 ### Always Indexed
 191 
 192 - `Id`
 193 - `Name`
 194 - `OwnerId`
 195 - `CreatedDate`
 196 - `LastModifiedDate`
 197 - `RecordTypeId`
 198 - External ID fields
 199 - Master-Detail fields
 200 
 201 ### Selective Query Rules
 202 
 203 - Query is selective if WHERE returns < 10% of first 1M records
 204 - Or uses an indexed field with < 1M matching records
 205 - Non-selective queries on large tables fail
 206 
 207 ---
 208 
 209 ## CLI Commands
 210 
 211 ```bash
 212 # Basic query
 213 sf data query --query "SELECT Id, Name FROM Account LIMIT 10" --target-org my-org
 214 
 215 # JSON output
 216 sf data query --query "SELECT Id, Name FROM Account" --target-org my-org --json
 217 
 218 # CSV output
 219 sf data query --query "SELECT Id, Name FROM Account" --result-format csv --target-org my-org
 220 
 221 # Bulk export (for large results, > 2,000 records)
 222 sf data export bulk --query "SELECT Id, Name FROM Account" --target-org my-org --output-file accounts.csv
 223 
 224 # Query plan
 225 sf data query --query "SELECT Id FROM Account WHERE Name = 'Test'" --use-tooling-api --plan --target-org my-org
 226 ```
