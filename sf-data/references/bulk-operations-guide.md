<!-- Parent: sf-data/SKILL.md -->
   1 # Bulk Operations Guide
   2 
   3 When and how to use Salesforce Bulk API operations.
   4 
   5 ## Decision Matrix
   6 
   7 | Record Count | Recommended API | Command |
   8 |--------------|-----------------|---------|
   9 | 1-10 | Single Record | `sf data create record` |
  10 | 11-2000 | Standard API | `sf data query` + Apex |
  11 | 2000-10M | Bulk API 2.0 | `sf data import bulk` |
  12 | 10M+ | Data Loader | External tool |
  13 
  14 ## Bulk API 2.0 Commands
  15 
  16 ### Import (Insert)
  17 ```bash
  18 sf data import bulk \
  19   --file accounts.csv \
  20   --sobject Account \
  21   --target-org myorg \
  22   --wait 30
  23 ```
  24 
  25 ### Update
  26 ```bash
  27 sf data update bulk \
  28   --file updates.csv \
  29   --sobject Account \
  30   --target-org myorg \
  31   --wait 30
  32 ```
  33 
  34 ### Upsert (Insert or Update)
  35 ```bash
  36 sf data upsert bulk \
  37   --file upsert.csv \
  38   --sobject Account \
  39   --external-id External_Id__c \
  40   --target-org myorg \
  41   --wait 30
  42 ```
  43 
  44 ### Delete
  45 ```bash
  46 sf data delete bulk \
  47   --file delete.csv \
  48   --sobject Account \
  49   --target-org myorg \
  50   --wait 30
  51 ```
  52 
  53 ### Export
  54 ```bash
  55 sf data export bulk \
  56   --query "SELECT Id, Name FROM Account" \
  57   --output-file accounts.csv \
  58   --target-org myorg \
  59   --wait 30
  60 ```
  61 
  62 ## CSV Format Requirements
  63 
  64 - First row: Field API names
  65 - UTF-8 encoding
  66 - Comma delimiter (default)
  67 - Max 100MB per file
  68 
  69 ## Bulk API Limits
  70 
  71 | Limit | Value |
  72 |-------|-------|
  73 | Batches per 24 hours | 10,000 |
  74 | Records per 24 hours | 10,000,000 |
  75 | Max file size | 100 MB |
  76 | Max concurrent jobs | 100 |
  77 
  78 ## Error Handling
  79 
  80 ```bash
  81 # Check job status
  82 sf data resume --job-id [job-id] --target-org myorg
  83 
  84 # Get results
  85 sf data bulk results --job-id [job-id] --target-org myorg
  86 ```
  87 
  88 ## Best Practices
  89 
  90 1. **Chunk large files** - Split files >100MB
  91 2. **Use --wait** - Monitor completion
  92 3. **Handle partial failures** - Check result files
  93 4. **Test in sandbox** - Validate before production
