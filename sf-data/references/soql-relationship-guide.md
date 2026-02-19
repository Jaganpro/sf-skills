<!-- Parent: sf-data/SKILL.md -->
   1 # SOQL Relationship Query Guide
   2 
   3 Complete reference for querying related records in Salesforce.
   4 
   5 ## Relationship Types
   6 
   7 ### 1. Parent-to-Child (Subquery)
   8 Returns parent records with nested child records.
   9 
  10 ```sql
  11 SELECT Id, Name,
  12     (SELECT Id, FirstName, LastName FROM Contacts)
  13 FROM Account
  14 WHERE Industry = 'Technology'
  15 ```
  16 
  17 **Key Points:**
  18 - Maximum 20 subqueries per query
  19 - Use relationship name (plural): `Contacts`, `Opportunities`, `Cases`
  20 - For custom objects: `Child_Object__r`
  21 
  22 ### 2. Child-to-Parent (Dot Notation)
  23 Access parent fields from child record.
  24 
  25 ```sql
  26 SELECT Id, Name,
  27     Account.Name,
  28     Account.Industry,
  29     Account.Owner.Name
  30 FROM Contact
  31 WHERE Account.Type = 'Customer'
  32 ```
  33 
  34 **Key Points:**
  35 - Maximum 5 levels deep
  36 - Standard: `Account.Name`
  37 - Custom: `Parent__r.Name`
  38 
  39 ### 3. Polymorphic (TYPEOF)
  40 Handle fields that reference multiple object types.
  41 
  42 ```sql
  43 SELECT Id, Subject,
  44     TYPEOF Who
  45         WHEN Contact THEN FirstName, LastName
  46         WHEN Lead THEN Company
  47     END,
  48     TYPEOF What
  49         WHEN Account THEN Name, Industry
  50         WHEN Opportunity THEN Amount
  51     END
  52 FROM Task
  53 ```
  54 
  55 **Common Polymorphic Fields:**
  56 - `WhoId` → Contact, Lead
  57 - `WhatId` → Account, Opportunity, Case, etc.
  58 - `OwnerId` → User, Queue
  59 
  60 ## Relationship Names
  61 
  62 | Child Object | Parent Field | Relationship Name |
  63 |--------------|--------------|-------------------|
  64 | Contact | AccountId | Account.Contacts |
  65 | Opportunity | AccountId | Account.Opportunities |
  66 | Case | AccountId | Account.Cases |
  67 | Task | WhatId | Account.Tasks |
  68 | Contact | ReportsToId | Contact.ReportsTo |
  69 
  70 ## Limits
  71 
  72 | Limit | Value |
  73 |-------|-------|
  74 | Child-to-Parent depth | 5 levels |
  75 | Subqueries per query | 20 |
  76 | Rows per subquery | 200 (without LIMIT) |
  77 
  78 ## Best Practices
  79 
  80 1. **Use indexed fields** in WHERE clauses
  81 2. **Add LIMIT** to subqueries
  82 3. **Filter early** - push conditions into subqueries
  83 4. **Avoid N+1** - use relationship queries instead of loops
