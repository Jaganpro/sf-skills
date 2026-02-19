<!-- Parent: sf-data/SKILL.md -->
   1 # sf CLI Data Commands Reference
   2 
   3 Complete reference for Salesforce CLI v2 data commands.
   4 
   5 ## Query Commands
   6 
   7 ### SOQL Query
   8 ```bash
   9 sf data query \
  10   --query "SELECT Id, Name FROM Account LIMIT 10" \
  11   --target-org myorg \
  12   --json
  13 ```
  14 
  15 ### SOSL Search
  16 ```bash
  17 sf data search \
  18   --query "FIND {Acme}" \
  19   --target-org myorg
  20 ```
  21 
  22 ### Bulk Export
  23 ```bash
  24 sf data export bulk \
  25   --query "SELECT Id, Name FROM Account" \
  26   --output-file accounts.csv \
  27   --target-org myorg \
  28   --wait 30
  29 ```
  30 
  31 ## Record Operations
  32 
  33 ### Create Record
  34 ```bash
  35 sf data create record \
  36   --sobject Account \
  37   --values "Name='Acme' Industry='Technology'" \
  38   --target-org myorg
  39 ```
  40 
  41 ### Update Record
  42 ```bash
  43 sf data update record \
  44   --sobject Account \
  45   --record-id 001XXXXXXXXXXXX \
  46   --values "Industry='Healthcare'" \
  47   --target-org myorg
  48 ```
  49 
  50 ### Delete Record
  51 ```bash
  52 sf data delete record \
  53   --sobject Account \
  54   --record-id 001XXXXXXXXXXXX \
  55   --target-org myorg
  56 ```
  57 
  58 ### Get Record
  59 ```bash
  60 sf data get record \
  61   --sobject Account \
  62   --record-id 001XXXXXXXXXXXX \
  63   --target-org myorg
  64 ```
  65 
  66 ## Bulk Operations
  67 
  68 ### Bulk Import
  69 ```bash
  70 sf data import bulk \
  71   --file data.csv \
  72   --sobject Account \
  73   --target-org myorg \
  74   --wait 30
  75 ```
  76 
  77 ### Bulk Update
  78 ```bash
  79 sf data update bulk \
  80   --file updates.csv \
  81   --sobject Account \
  82   --target-org myorg \
  83   --wait 30
  84 ```
  85 
  86 ### Bulk Upsert
  87 ```bash
  88 sf data upsert bulk \
  89   --file data.csv \
  90   --sobject Account \
  91   --external-id External_Id__c \
  92   --target-org myorg \
  93   --wait 30
  94 ```
  95 
  96 ### Bulk Delete
  97 ```bash
  98 sf data delete bulk \
  99   --file ids.csv \
 100   --sobject Account \
 101   --target-org myorg \
 102   --wait 30
 103 ```
 104 
 105 ## Tree Operations
 106 
 107 ### Export Tree
 108 ```bash
 109 sf data export tree \
 110   --query "SELECT Id, Name, (SELECT Id, Name FROM Contacts) FROM Account" \
 111   --output-dir ./data \
 112   --target-org myorg
 113 ```
 114 
 115 ### Import Tree
 116 ```bash
 117 sf data import tree \
 118   --files data.json \
 119   --target-org myorg
 120 ```
 121 
 122 ## Common Flags
 123 
 124 | Flag | Description |
 125 |------|-------------|
 126 | `--target-org`, `-o` | Target org alias |
 127 | `--json` | JSON output format |
 128 | `--result-format` | human, csv, json |
 129 | `--wait` | Minutes to wait for bulk jobs |
 130 | `--use-tooling-api` | Query Tooling API |
 131 
 132 ## Apex Execution
 133 
 134 ```bash
 135 sf apex run --file script.apex --target-org myorg
 136 ```
