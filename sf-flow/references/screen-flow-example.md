<!-- Parent: sf-flow/SKILL.md -->
   1 # Screen Flow Example: Customer Feedback Form
   2 
   3 > **Version**: 2.0.0
   4 > **Demonstrates**: UX patterns, progress indicators, navigation controls, error recovery
   5 
   6 This example demonstrates creating a Screen Flow that collects customer feedback and creates a custom object record, following v2.0.0 UX best practices.
   7 
   8 ---
   9 
  10 ## Scenario
  11 
  12 Create an interactive form where users can:
  13 - Select a product from a picklist
  14 - Rate their experience (1-5 stars)
  15 - Provide comments
  16 - Submit feedback to a custom Feedback__c object
  17 
  18 ## User Request
  19 
  20 ```
  21 User: "Create a screen flow for customer feedback collection.
  22 It should have a welcome screen, collect product selection,
  23 rating (1-5), and comments, then save to the Feedback__c object."
  24 ```
  25 
  26 ---
  27 
  28 ## UX Design Patterns (v2.0.0)
  29 
  30 ### Flow Structure with Navigation
  31 
  32 ```
  33 ┌────────────────────────────────────────────────────────────────┐
  34 │  SCREEN 1: Welcome                                              │
  35 │  ─────────────────────────                                      │
  36 │  "Customer Feedback" (Step 1 of 3)                              │
  37 │                                                                 │
  38 │  Welcome message and instructions                               │
  39 │                                                                 │
  40 │  allowBack: false  │  allowFinish: true  │  Button: [Next]     │
  41 └────────────────────────────────────────────────────────────────┘
  42                               │
  43                               ▼
  44 ┌────────────────────────────────────────────────────────────────┐
  45 │  SCREEN 2: Feedback Form                                        │
  46 │  ─────────────────────────                                      │
  47 │  "Enter Your Feedback" (Step 2 of 3)                            │
  48 │                                                                 │
  49 │  Product: [Dropdown]                                            │
  50 │  Rating:  ★ ★ ★ ★ ★ (1-5)                                       │
  51 │  Comments: [Text Area]                                          │
  52 │                                                                 │
  53 │  allowBack: true  │  allowFinish: true  │  [Previous] [Next]   │
  54 └────────────────────────────────────────────────────────────────┘
  55                               │
  56                               ▼
  57                     ┌─────────────────┐
  58                     │  Create Record  │──fault──▶ Error Screen
  59                     └────────┬────────┘
  60                              │ success
  61                              ▼
  62 ┌────────────────────────────────────────────────────────────────┐
  63 │  SCREEN 3: Thank You                                            │
  64 │  ─────────────────────                                          │
  65 │  "Success!" (Step 3 of 3)                                       │
  66 │                                                                 │
  67 │  ✓ Thank you for your feedback!                                 │
  68 │                                                                 │
  69 │  allowBack: false  │  allowFinish: true  │  Button: [Finish]   │
  70 │  (prevents duplicate submissions)                               │
  71 └────────────────────────────────────────────────────────────────┘
  72 ```
  73 
  74 ### Navigation Control Rules Applied
  75 
  76 | Screen | allowBack | allowFinish | Reason |
  77 |--------|-----------|-------------|--------|
  78 | Welcome | `false` | `true` | First screen - no previous |
  79 | Feedback Form | `true` | `true` | Allow user to go back |
  80 | Thank You | `false` | `true` | **Record already created** - prevent duplicate |
  81 | Error | `true` | `true` | Let user try again |
  82 
  83 ---
  84 
  85 ## Generated Flow Structure (v2.0.0)
  86 
  87 ### Variables (with v2.0.0 Naming Prefixes)
  88 
  89 ```xml
  90 <!-- Input/Form Variables -->
  91 <variables>
  92     <name>var_ProductName</name>
  93     <dataType>String</dataType>
  94     <isCollection>false</isCollection>
  95     <isInput>false</isInput>
  96     <isOutput>false</isOutput>
  97 </variables>
  98 
  99 <variables>
 100     <name>var_Rating</name>
 101     <dataType>Number</dataType>
 102     <isCollection>false</isCollection>
 103     <isInput>false</isInput>
 104     <isOutput>false</isOutput>
 105     <scale>0</scale>
 106 </variables>
 107 
 108 <variables>
 109     <name>var_Comments</name>
 110     <dataType>String</dataType>
 111     <isCollection>false</isCollection>
 112     <isInput>false</isInput>
 113     <isOutput>false</isOutput>
 114 </variables>
 115 
 116 <!-- Error Handling Variable -->
 117 <variables>
 118     <name>var_ErrorMessage</name>
 119     <dataType>String</dataType>
 120     <isCollection>false</isCollection>
 121     <isInput>false</isInput>
 122     <isOutput>false</isOutput>
 123 </variables>
 124 
 125 <!-- Output Variable for Integration -->
 126 <variables>
 127     <name>out_FeedbackId</name>
 128     <dataType>String</dataType>
 129     <isCollection>false</isCollection>
 130     <isInput>false</isInput>
 131     <isOutput>true</isOutput>
 132 </variables>
 133 ```
 134 
 135 ### Screen 1: Welcome (with Progress Indicator)
 136 
 137 ```xml
 138 <screens>
 139     <name>Screen_Welcome</name>
 140     <label>Welcome</label>
 141     <locationX>0</locationX>
 142     <locationY>0</locationY>
 143     <allowBack>false</allowBack>
 144     <allowFinish>true</allowFinish>
 145     <allowPause>false</allowPause>
 146     <connector>
 147         <targetReference>Screen_Feedback_Form</targetReference>
 148     </connector>
 149     <fields>
 150         <!-- Progress Indicator Header -->
 151         <name>Welcome_Header</name>
 152         <fieldType>DisplayText</fieldType>
 153         <fieldText>&lt;p&gt;&lt;b style="font-size: 20px;"&gt;Customer Feedback&lt;/b&gt;&lt;/p&gt;&lt;p&gt;&lt;span style="color: rgb(107, 107, 107);"&gt;Step 1 of 3&lt;/span&gt;&lt;/p&gt;</fieldText>
 154     </fields>
 155     <fields>
 156         <!-- Instructions -->
 157         <name>Welcome_Instructions</name>
 158         <fieldType>DisplayText</fieldType>
 159         <fieldText>&lt;p&gt;Thank you for taking the time to share your feedback!&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;Your input helps us improve our products and services. This form takes approximately &lt;b&gt;2 minutes&lt;/b&gt; to complete.&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;Click &lt;b&gt;Next&lt;/b&gt; to begin.&lt;/p&gt;</fieldText>
 160     </fields>
 161     <showFooter>true</showFooter>
 162     <showHeader>true</showHeader>
 163 </screens>
 164 ```
 165 
 166 ### Screen 2: Feedback Form (with Input Validation)
 167 
 168 ```xml
 169 <screens>
 170     <name>Screen_Feedback_Form</name>
 171     <label>Feedback Form</label>
 172     <locationX>0</locationX>
 173     <locationY>0</locationY>
 174     <allowBack>true</allowBack>
 175     <allowFinish>true</allowFinish>
 176     <allowPause>false</allowPause>
 177     <connector>
 178         <targetReference>Create_Feedback_Record</targetReference>
 179     </connector>
 180     <fields>
 181         <!-- Progress Header -->
 182         <name>Form_Header</name>
 183         <fieldType>DisplayText</fieldType>
 184         <fieldText>&lt;p&gt;&lt;b style="font-size: 20px;"&gt;Enter Your Feedback&lt;/b&gt;&lt;/p&gt;&lt;p&gt;&lt;span style="color: rgb(107, 107, 107);"&gt;Step 2 of 3&lt;/span&gt;&lt;/p&gt;</fieldText>
 185     </fields>
 186     <fields>
 187         <!-- Instructions with Required Field Indicator -->
 188         <name>Form_Instructions</name>
 189         <fieldType>DisplayText</fieldType>
 190         <fieldText>&lt;p&gt;Please complete all required fields (&lt;span style="color: rgb(194, 57, 52);"&gt;*&lt;/span&gt;) below.&lt;/p&gt;</fieldText>
 191     </fields>
 192     <fields>
 193         <!-- Product Selection (Required) -->
 194         <name>Input_Product</name>
 195         <choiceReferences>choice_Product_A</choiceReferences>
 196         <choiceReferences>choice_Product_B</choiceReferences>
 197         <choiceReferences>choice_Product_C</choiceReferences>
 198         <dataType>String</dataType>
 199         <fieldText>Which product are you providing feedback for?</fieldText>
 200         <fieldType>DropdownBox</fieldType>
 201         <isRequired>true</isRequired>
 202         <inputsOnNextNavToAssocScrn>UseStoredValues</inputsOnNextNavToAssocScrn>
 203     </fields>
 204     <fields>
 205         <!-- Rating (1-5, Required) -->
 206         <name>Input_Rating</name>
 207         <dataType>Number</dataType>
 208         <fieldText>How would you rate your experience? (1-5)</fieldText>
 209         <fieldType>InputField</fieldType>
 210         <helpText>1 = Very Poor, 5 = Excellent</helpText>
 211         <isRequired>true</isRequired>
 212         <scale>0</scale>
 213         <inputsOnNextNavToAssocScrn>UseStoredValues</inputsOnNextNavToAssocScrn>
 214     </fields>
 215     <fields>
 216         <!-- Comments (Optional) -->
 217         <name>Input_Comments</name>
 218         <fieldText>Additional Comments (Optional)</fieldText>
 219         <fieldType>LargeTextArea</fieldType>
 220         <helpText>Share any additional thoughts, suggestions, or concerns.</helpText>
 221         <isRequired>false</isRequired>
 222         <inputsOnNextNavToAssocScrn>UseStoredValues</inputsOnNextNavToAssocScrn>
 223     </fields>
 224     <showFooter>true</showFooter>
 225     <showHeader>true</showHeader>
 226 </screens>
 227 ```
 228 
 229 ### Record Create (with Fault Connector)
 230 
 231 ```xml
 232 <recordCreates>
 233     <name>Create_Feedback_Record</name>
 234     <label>Create Feedback Record</label>
 235     <locationX>0</locationX>
 236     <locationY>0</locationY>
 237     <connector>
 238         <targetReference>Screen_Thank_You</targetReference>
 239     </connector>
 240     <faultConnector>
 241         <targetReference>Capture_Error</targetReference>
 242     </faultConnector>
 243     <inputAssignments>
 244         <field>Product__c</field>
 245         <value>
 246             <elementReference>Input_Product</elementReference>
 247         </value>
 248     </inputAssignments>
 249     <inputAssignments>
 250         <field>Rating__c</field>
 251         <value>
 252             <elementReference>Input_Rating</elementReference>
 253         </value>
 254     </inputAssignments>
 255     <inputAssignments>
 256         <field>Comments__c</field>
 257         <value>
 258             <elementReference>Input_Comments</elementReference>
 259         </value>
 260     </inputAssignments>
 261     <object>Feedback__c</object>
 262     <storeOutputAutomatically>true</storeOutputAutomatically>
 263 </recordCreates>
 264 ```
 265 
 266 ### Screen 3: Thank You (Back Button DISABLED)
 267 
 268 ```xml
 269 <!--
 270 CRITICAL: allowBack="false" on success screen!
 271 The record has already been created. If we allow back navigation,
 272 the user could submit again and create duplicate records.
 273 -->
 274 <screens>
 275     <name>Screen_Thank_You</name>
 276     <label>Thank You</label>
 277     <locationX>0</locationX>
 278     <locationY>0</locationY>
 279     <allowBack>false</allowBack>
 280     <allowFinish>true</allowFinish>
 281     <allowPause>false</allowPause>
 282     <!-- No connector = "Finish" button displayed -->
 283     <fields>
 284         <name>ThankYou_Header</name>
 285         <fieldType>DisplayText</fieldType>
 286         <fieldText>&lt;p&gt;&lt;b style="font-size: 20px;"&gt;Success!&lt;/b&gt;&lt;/p&gt;&lt;p&gt;&lt;span style="color: rgb(107, 107, 107);"&gt;Step 3 of 3&lt;/span&gt;&lt;/p&gt;</fieldText>
 287     </fields>
 288     <fields>
 289         <name>ThankYou_Message</name>
 290         <fieldType>DisplayText</fieldType>
 291         <fieldText>&lt;p&gt;&lt;span style="color: rgb(46, 132, 74); font-size: 24px;"&gt;✓&lt;/span&gt;&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;&lt;b&gt;Thank you for your feedback!&lt;/b&gt;&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;Your input has been recorded and will help us improve our products and services.&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;Click &lt;b&gt;Finish&lt;/b&gt; to close this form.&lt;/p&gt;</fieldText>
 292     </fields>
 293     <showFooter>true</showFooter>
 294     <showHeader>true</showHeader>
 295 </screens>
 296 ```
 297 
 298 ### Error Recovery Screen (Back Button ENABLED)
 299 
 300 ```xml
 301 <!-- Capture Error Message -->
 302 <assignments>
 303     <name>Capture_Error</name>
 304     <label>Capture Error</label>
 305     <locationX>0</locationX>
 306     <locationY>0</locationY>
 307     <assignmentItems>
 308         <assignToReference>var_ErrorMessage</assignToReference>
 309         <operator>Assign</operator>
 310         <value>
 311             <elementReference>$Flow.FaultMessage</elementReference>
 312         </value>
 313     </assignmentItems>
 314     <connector>
 315         <targetReference>Screen_Error</targetReference>
 316     </connector>
 317 </assignments>
 318 
 319 <!--
 320 ERROR SCREEN: allowBack="true"
 321 Let users go back to fix their input and try again.
 322 The record wasn't created, so no duplicate risk.
 323 -->
 324 <screens>
 325     <name>Screen_Error</name>
 326     <label>Error</label>
 327     <locationX>0</locationX>
 328     <locationY>0</locationY>
 329     <allowBack>true</allowBack>
 330     <allowFinish>true</allowFinish>
 331     <allowPause>false</allowPause>
 332     <fields>
 333         <name>Error_Header</name>
 334         <fieldType>DisplayText</fieldType>
 335         <fieldText>&lt;p&gt;&lt;span style="color: rgb(194, 57, 52);"&gt;&lt;b style="font-size: 20px;"&gt;Something Went Wrong&lt;/b&gt;&lt;/span&gt;&lt;/p&gt;</fieldText>
 336     </fields>
 337     <fields>
 338         <name>Error_Message</name>
 339         <fieldType>DisplayText</fieldType>
 340         <fieldText>&lt;p&gt;We were unable to save your feedback. The error was:&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;&lt;i style="color: rgb(194, 57, 52);"&gt;{!var_ErrorMessage}&lt;/i&gt;&lt;/p&gt;&lt;p&gt;&lt;br&gt;&lt;/p&gt;&lt;p&gt;Please click &lt;b&gt;Previous&lt;/b&gt; to review your entries and try again, or click &lt;b&gt;Finish&lt;/b&gt; to exit without saving.&lt;/p&gt;</fieldText>
 341     </fields>
 342     <showFooter>true</showFooter>
 343     <showHeader>true</showHeader>
 344 </screens>
 345 ```
 346 
 347 ---
 348 
 349 ## UX Best Practices Demonstrated
 350 
 351 ### 1. Progress Indicators
 352 Every screen shows "Step X of 3" to orient users.
 353 
 354 ### 2. Clear Instructions
 355 - Welcome screen explains time commitment (2 minutes)
 356 - Form screen explains required fields (*)
 357 - Help text on complex fields
 358 
 359 ### 3. Input Preservation
 360 `inputsOnNextNavToAssocScrn="UseStoredValues"` preserves user input when navigating back.
 361 
 362 ### 4. Strategic Back Button Control
 363 | Screen | allowBack | Reason |
 364 |--------|-----------|--------|
 365 | Welcome | false | No previous screen |
 366 | Form | true | Let users go back to re-read instructions |
 367 | Thank You | **false** | **Prevent duplicate submission** |
 368 | Error | true | Let users try again |
 369 
 370 ### 5. User-Friendly Error Messages
 371 - Technical `$Flow.FaultMessage` displayed in italic
 372 - Clear instruction on recovery options
 373 - Both "Previous" and "Finish" available
 374 
 375 ### 6. Consistent Visual Hierarchy
 376 - Large, bold headers (20px)
 377 - Subdued progress text (gray)
 378 - Success confirmation with checkmark
 379 - Error text in red
 380 
 381 ---
 382 
 383 ## Testing Checklist (v2.0.0)
 384 
 385 ### Path Coverage
 386 - [ ] Happy path: Welcome → Form → Create → Thank You
 387 - [ ] Error path: Welcome → Form → Error → (Previous) → Form → Success
 388 - [ ] Exit from error: Welcome → Form → Error → Finish
 389 
 390 ### Navigation Testing
 391 - [ ] Welcome: No "Previous" button visible
 392 - [ ] Form: Both "Previous" and "Next" visible
 393 - [ ] Thank You: No "Previous" button (prevents duplicate)
 394 - [ ] Error: Both "Previous" and "Finish" visible
 395 
 396 ### Input Validation
 397 - [ ] Empty product → validation message
 398 - [ ] Rating 0 or 6 → validation message (if min/max configured)
 399 - [ ] All required fields empty → validation messages
 400 - [ ] Long comments (32,000+ chars) → handled gracefully
 401 
 402 ### User Context
 403 - [ ] Works as System Administrator
 404 - [ ] Works as Standard User
 405 - [ ] Works as Community User (if exposed externally)
 406 
 407 ### Edge Cases
 408 - [ ] Special characters in comments: `<>&"'`
 409 - [ ] Unicode/Emoji in comments
 410 - [ ] Browser back button behavior
 411 - [ ] Session timeout handling
 412 
 413 ---
 414 
 415 ## Skill Workflow
 416 
 417 ### Phase 1: Requirements Gathering
 418 
 419 The skill asks:
 420 
 421 **Q1: What type of flow?**
 422 → Screen Flow
 423 
 424 **Q2: What is the purpose?**
 425 → "Collect customer feedback and save to Feedback__c object"
 426 
 427 **Q3: Target org?**
 428 → "sandbox"
 429 
 430 ### Phase 2: Flow Design
 431 
 432 The skill designs:
 433 - **Screen 1**: Welcome message with progress indicator
 434 - **Screen 2**: Feedback form with validation
 435 - **Create Record**: Save to Feedback__c (with fault path)
 436 - **Screen 3**: Thank you confirmation (back disabled)
 437 - **Error Screen**: Recovery option (back enabled)
 438 
 439 ### Phase 3: Validation
 440 
 441 ```
 442 Flow Validation Report: Customer_Feedback_Screen_Flow (API 65.0)
 443 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 444 
 445 Score: 108/110 ⭐⭐⭐⭐⭐ Excellent
 446 ├─ Design & Naming: 20/20 (100%) ✓
 447 ├─ Logic & Structure: 20/20 (100%) ✓
 448 ├─ Architecture: 13/15 (87%)
 449 ├─ Performance & Bulk Safety: 20/20 (100%) ✓
 450 ├─ Error Handling: 20/20 (100%) ✓
 451 └─ Security: 15/15 (100%) ✓
 452 
 453 ✓ Variable naming follows v2.0.0 prefixes (var_, out_)
 454 ✓ All DML has fault connectors
 455 ✓ Progress indicators on all screens
 456 ✓ Back button disabled on success screen
 457 
 458 ✓ VALIDATION PASSED - Flow ready for deployment
 459 ```
 460 
 461 ### Phase 4: Deployment
 462 
 463 **Step 1: Check-Only Validation**
 464 ```
 465 Deploying flow with --dry-run flag...
 466 ✓ Validation successful
 467 ✓ No org-specific errors
 468 ✓ Ready for actual deployment
 469 ```
 470 
 471 **Step 2: Actual Deployment**
 472 ```
 473 Deploying to sandbox...
 474 ✓ Deployment successful
 475 Job ID: 0Af5g00000XXXXX
 476 Flow deployed as Draft
 477 ```
 478 
 479 ### Phase 5: Testing
 480 
 481 Follow the testing checklist above, then activate when ready.
 482 
 483 ---
 484 
 485 ## Related Resources
 486 
 487 - [Screen Flow Template](../assets/screen-flow-template.xml) - Base template with UX guidance
 488 - [Flow Best Practices](../references/flow-best-practices.md) - Comprehensive UX patterns
 489 - [Testing Guide](../references/testing-guide.md) - Testing strategies
 490 - [Testing Checklist](../references/testing-checklist.md) - Quick reference
