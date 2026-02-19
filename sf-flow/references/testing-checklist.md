<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow Testing Checklist
   2 
   3 > **Version**: 2.0.0
   4 > **Purpose**: Quick-reference checklist for flow testing
   5 > **Usage**: Copy and use for each flow deployment
   6 
   7 ---
   8 
   9 ## Pre-Testing Setup
  10 
  11 - [ ] Flow XML validates without errors
  12 - [ ] All decision paths documented
  13 - [ ] Test data prepared in sandbox
  14 - [ ] Debug logs enabled for test user
  15 
  16 ---
  17 
  18 ## Path Coverage
  19 
  20 - [ ] All decision branches tested (including default)
  21 - [ ] All loop scenarios tested:
  22   - [ ] 0 items (empty collection)
  23   - [ ] 1 item
  24   - [ ] Many items (10+)
  25 - [ ] All fault paths tested
  26 - [ ] Positive cases pass (valid inputs)
  27 - [ ] Negative cases handled gracefully (invalid inputs)
  28 
  29 ---
  30 
  31 ## Bulk Testing
  32 
  33 - [ ] Single record works correctly
  34 - [ ] 10-20 records work (basic bulkification)
  35 - [ ] 200+ records work (no governor limit errors)
  36 - [ ] No DML-in-loop errors in debug logs
  37 
  38 ---
  39 
  40 ## Edge Cases
  41 
  42 - [ ] Null values handled (no crashes)
  43 - [ ] Empty collections handled (loops skip gracefully)
  44 - [ ] Max field lengths work (no truncation)
  45 - [ ] Special characters work (`<>&"'`)
  46 - [ ] Date edge cases work (leap years, boundaries)
  47 
  48 ---
  49 
  50 ## User Context
  51 
  52 - [ ] Works as System Administrator
  53 - [ ] Works as Standard User
  54 - [ ] FLS restrictions enforced (User mode flows)
  55 - [ ] Sharing rules respected
  56 - [ ] Custom permissions work (`$Permission`)
  57 
  58 ---
  59 
  60 ## Error Handling
  61 
  62 - [ ] All DML elements have fault paths
  63 - [ ] Error messages are user-friendly
  64 - [ ] Rollback logic works (if multi-step DML)
  65 - [ ] Error logging captures context
  66 
  67 ---
  68 
  69 ## Screen Flow Specific
  70 
  71 - [ ] All navigation works (Next/Previous/Finish)
  72 - [ ] Input validation works on each screen
  73 - [ ] Conditional visibility works
  74 - [ ] Progress indicator updates (if applicable)
  75 - [ ] Back button behavior correct
  76 
  77 ---
  78 
  79 ## Record-Triggered Specific
  80 
  81 - [ ] Entry conditions filter correctly
  82 - [ ] Before-save vs After-save timing correct
  83 - [ ] `$Record` values accessible
  84 - [ ] Re-entry prevention works (if applicable)
  85 
  86 ---
  87 
  88 ## Scheduled Flow Specific
  89 
  90 - [ ] Schedule configuration verified
  91 - [ ] Manual run test passes
  92 - [ ] Empty result set handled
  93 - [ ] Batch processing works
  94 
  95 ---
  96 
  97 ## Deployment
  98 
  99 - [ ] `checkOnly=true` deployment succeeds
 100 - [ ] package.xml API version matches flow
 101 - [ ] Test in sandbox complete
 102 - [ ] Activation plan documented
 103 
 104 ---
 105 
 106 ## Post-Deployment
 107 
 108 - [ ] Flow status verified (Active/Draft)
 109 - [ ] Correct version is active
 110 - [ ] No errors in Flow Errors log
 111 - [ ] First execution monitored
 112 
 113 ---
 114 
 115 ## Sign-Off
 116 
 117 | Item | Completed | Date | Tester |
 118 |------|-----------|------|--------|
 119 | Development Testing | | | |
 120 | UAT Testing | | | |
 121 | Bulk Testing | | | |
 122 | Security Review | | | |
 123 | Production Deployment | | | |
 124 
 125 ---
 126 
 127 ## Notes
 128 
 129 _Add any flow-specific notes or exceptions here_
