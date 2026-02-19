<!-- Parent: sf-flow/SKILL.md -->
   1 # Flow + LWC Integration Guide
   2 
   3 This guide covers embedding custom Lightning Web Components in Flow Screens.
   4 
   5 ---
   6 
   7 ## Overview
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────────┐
  11 │                   FLOW SCREEN + LWC ARCHITECTURE                    │
  12 ├─────────────────────────────────────────────────────────────────────┤
  13 │                                                                      │
  14 │   ┌─────────────────────────────────────────────────────────────┐   │
  15 │   │                      FLOW (Screen)                           │   │
  16 │   │  ┌──────────────────────────────────────────────────────┐   │   │
  17 │   │  │                  screens element                      │   │   │
  18 │   │  │    ┌──────────────────────────────────────────────┐  │   │   │
  19 │   │  │    │           fields > componentInstance         │  │   │   │
  20 │   │  │    │                                              │  │   │   │
  21 │   │  │    │   extensionName="c:myComponent"              │  │   │   │
  22 │   │  │    │                                              │  │   │   │
  23 │   │  │    │   inputParameters ────────────▶ @api (in)    │  │   │   │
  24 │   │  │    │   outputParameters ◀────────── @api (out)    │  │   │   │
  25 │   │  │    │                                              │  │   │   │
  26 │   │  │    └──────────────────────────────────────────────┘  │   │   │
  27 │   │  └──────────────────────────────────────────────────────┘   │   │
  28 │   └─────────────────────────────────────────────────────────────┘   │
  29 │                                                                      │
  30 └─────────────────────────────────────────────────────────────────────┘
  31 ```
  32 
  33 ---
  34 
  35 ## Quick Reference
  36 
  37 | Flow Element | LWC Requirement | Purpose |
  38 |--------------|-----------------|---------|
  39 | `extensionName` | `target="lightning__FlowScreen"` | Identify LWC component |
  40 | `inputParameters` | `@api` with `role="inputOnly"` | Flow → LWC data |
  41 | `outputParameters` | `@api` with `role="outputOnly"` | LWC → Flow data |
  42 | N/A | `FlowAttributeChangeEvent` | LWC updates outputs |
  43 | N/A | `FlowNavigationFinishEvent` | LWC controls navigation |
  44 
  45 ---
  46 
  47 ## Flow XML Structure
  48 
  49 ### Basic Screen with LWC
  50 
  51 ```xml
  52 <screens>
  53     <name>My_LWC_Screen</name>
  54     <label>Custom Component Screen</label>
  55     <locationX>176</locationX>
  56     <locationY>158</locationY>
  57     <connector>
  58         <targetReference>Next_Element</targetReference>
  59     </connector>
  60     <showFooter>true</showFooter>
  61     <showHeader>true</showHeader>
  62 
  63     <fields>
  64         <name>myLwcField</name>
  65         <!-- Component reference: namespace:componentName -->
  66         <extensionName>c:myFlowComponent</extensionName>
  67         <fieldType>ComponentInstance</fieldType>
  68 
  69         <!-- Flow → LWC (inputs) -->
  70         <inputParameters>
  71             <name>recordId</name>
  72             <value>
  73                 <elementReference>var_RecordId</elementReference>
  74             </value>
  75         </inputParameters>
  76 
  77         <!-- LWC → Flow (outputs) -->
  78         <outputParameters>
  79             <assignToReference>var_SelectedId</assignToReference>
  80             <name>selectedRecordId</name>
  81         </outputParameters>
  82     </fields>
  83 </screens>
  84 ```
  85 
  86 ---
  87 
  88 ## Input Parameters
  89 
  90 Pass data from Flow variables to LWC `@api` properties.
  91 
  92 ### Value Types
  93 
  94 ```xml
  95 <!-- String literal -->
  96 <inputParameters>
  97     <name>mode</name>
  98     <value>
  99         <stringValue>edit</stringValue>
 100     </value>
 101 </inputParameters>
 102 
 103 <!-- Boolean literal -->
 104 <inputParameters>
 105     <name>showDetails</name>
 106     <value>
 107         <booleanValue>true</booleanValue>
 108     </value>
 109 </inputParameters>
 110 
 111 <!-- Number literal -->
 112 <inputParameters>
 113     <name>maxRecords</name>
 114     <value>
 115         <numberValue>10</numberValue>
 116     </value>
 117 </inputParameters>
 118 
 119 <!-- Flow variable reference -->
 120 <inputParameters>
 121     <name>recordId</name>
 122     <value>
 123         <elementReference>var_CurrentRecordId</elementReference>
 124     </value>
 125 </inputParameters>
 126 
 127 <!-- Record variable (SObject) -->
 128 <inputParameters>
 129     <name>account</name>
 130     <value>
 131         <elementReference>get_Account</elementReference>
 132     </value>
 133 </inputParameters>
 134 
 135 <!-- Collection variable -->
 136 <inputParameters>
 137     <name>selectedIds</name>
 138     <value>
 139         <elementReference>col_SelectedRecordIds</elementReference>
 140     </value>
 141 </inputParameters>
 142 ```
 143 
 144 ### LWC Property Declaration
 145 
 146 ```javascript
 147 // LWC must declare matching @api properties
 148 @api recordId;      // Maps to inputParameter name="recordId"
 149 @api mode;          // Maps to inputParameter name="mode"
 150 @api showDetails;   // Maps to inputParameter name="showDetails"
 151 @api maxRecords;    // Maps to inputParameter name="maxRecords"
 152 ```
 153 
 154 ---
 155 
 156 ## Output Parameters
 157 
 158 Receive data from LWC `@api` properties into Flow variables.
 159 
 160 ### Flow XML
 161 
 162 ```xml
 163 <!-- Simple value output -->
 164 <outputParameters>
 165     <assignToReference>var_SelectedRecordId</assignToReference>
 166     <name>selectedRecordId</name>
 167 </outputParameters>
 168 
 169 <!-- Boolean output -->
 170 <outputParameters>
 171     <assignToReference>var_IsComplete</assignToReference>
 172     <name>isComplete</name>
 173 </outputParameters>
 174 
 175 <!-- Collection output -->
 176 <outputParameters>
 177     <assignToReference>col_SelectedIds</assignToReference>
 178     <name>selectedIds</name>
 179 </outputParameters>
 180 ```
 181 
 182 ### LWC Dispatching Updates
 183 
 184 **CRITICAL**: LWC must dispatch `FlowAttributeChangeEvent` for outputs to update.
 185 
 186 ```javascript
 187 import { FlowAttributeChangeEvent } from 'lightning/flowSupport';
 188 
 189 @api selectedRecordId;
 190 
 191 handleSelection(event) {
 192     this.selectedRecordId = event.detail.id;
 193 
 194     // REQUIRED: Notify Flow of the change
 195     this.dispatchEvent(new FlowAttributeChangeEvent(
 196         'selectedRecordId',    // Property name (must match meta.xml)
 197         this.selectedRecordId  // New value
 198     ));
 199 }
 200 ```
 201 
 202 ---
 203 
 204 ## Variable Types Mapping
 205 
 206 | Flow Type | LWC Type | XML Declaration |
 207 |-----------|----------|-----------------|
 208 | `String` | `String` | `<dataType>String</dataType>` |
 209 | `Number` | `Number` | `<dataType>Number</dataType>` |
 210 | `Currency` | `Number` | `<dataType>Currency</dataType>` |
 211 | `Boolean` | `Boolean` | `<dataType>Boolean</dataType>` |
 212 | `Date` | `String` | `<dataType>Date</dataType>` |
 213 | `DateTime` | `String` | `<dataType>DateTime</dataType>` |
 214 | `Record` | `Object` | `<objectType>Account</objectType>` |
 215 | `Collection` | `Array` | `<isCollection>true</isCollection>` |
 216 
 217 ### Variable Declaration Examples
 218 
 219 ```xml
 220 <!-- String variable -->
 221 <variables>
 222     <name>var_SelectedId</name>
 223     <dataType>String</dataType>
 224     <isCollection>false</isCollection>
 225     <isInput>false</isInput>
 226     <isOutput>false</isOutput>
 227 </variables>
 228 
 229 <!-- Boolean variable with default -->
 230 <variables>
 231     <name>var_IsComplete</name>
 232     <dataType>Boolean</dataType>
 233     <isCollection>false</isCollection>
 234     <isInput>false</isInput>
 235     <isOutput>false</isOutput>
 236     <value>
 237         <booleanValue>false</booleanValue>
 238     </value>
 239 </variables>
 240 
 241 <!-- Collection of strings -->
 242 <variables>
 243     <name>col_SelectedIds</name>
 244     <dataType>String</dataType>
 245     <isCollection>true</isCollection>
 246     <isInput>false</isInput>
 247     <isOutput>false</isOutput>
 248 </variables>
 249 
 250 <!-- Record variable -->
 251 <variables>
 252     <name>var_Account</name>
 253     <dataType>SObject</dataType>
 254     <isCollection>false</isCollection>
 255     <isInput>false</isInput>
 256     <isOutput>false</isOutput>
 257     <objectType>Account</objectType>
 258 </variables>
 259 ```
 260 
 261 ---
 262 
 263 ## Validation Patterns
 264 
 265 ### Check LWC Output Before Proceeding
 266 
 267 ```xml
 268 <screens>
 269     <name>LWC_Screen</name>
 270     <!-- ... -->
 271     <connector>
 272         <targetReference>Validate_Output</targetReference>
 273     </connector>
 274 </screens>
 275 
 276 <decisions>
 277     <name>Validate_Output</name>
 278     <label>Validate LWC Output</label>
 279     <defaultConnector>
 280         <targetReference>Show_Error</targetReference>
 281     </defaultConnector>
 282     <defaultConnectorLabel>Invalid</defaultConnectorLabel>
 283     <rules>
 284         <name>Is_Valid</name>
 285         <conditionLogic>and</conditionLogic>
 286         <conditions>
 287             <leftValueReference>var_SelectedId</leftValueReference>
 288             <operator>IsNull</operator>
 289             <rightValue>
 290                 <booleanValue>false</booleanValue>
 291             </rightValue>
 292         </conditions>
 293         <connector>
 294             <targetReference>Continue_Flow</targetReference>
 295         </connector>
 296         <label>Valid Selection</label>
 297     </rules>
 298 </decisions>
 299 ```
 300 
 301 ### LWC-Side Validation
 302 
 303 ```javascript
 304 @api validate() {
 305     // Flow calls this when user clicks Next
 306     if (!this.selectedRecordId) {
 307         return {
 308             isValid: false,
 309             errorMessage: 'Please select a record before continuing.'
 310         };
 311     }
 312     return { isValid: true };
 313 }
 314 ```
 315 
 316 ---
 317 
 318 ## Screen Configuration
 319 
 320 ### Navigation Options
 321 
 322 ```xml
 323 <screens>
 324     <name>My_Screen</name>
 325     <allowBack>true</allowBack>      <!-- Show Back button -->
 326     <allowFinish>true</allowFinish>  <!-- Allow Finish (last screen) -->
 327     <allowPause>true</allowPause>    <!-- Show Pause button -->
 328     <showFooter>true</showFooter>    <!-- Show button bar -->
 329     <showHeader>true</showHeader>    <!-- Show screen label -->
 330 </screens>
 331 ```
 332 
 333 ### Hiding Standard Navigation
 334 
 335 When LWC handles its own navigation:
 336 
 337 ```xml
 338 <screens>
 339     <name>Custom_Nav_Screen</name>
 340     <showFooter>false</showFooter>  <!-- LWC provides buttons -->
 341     <!-- ... -->
 342 </screens>
 343 ```
 344 
 345 LWC then uses:
 346 ```javascript
 347 import { FlowNavigationFinishEvent } from 'lightning/flowSupport';
 348 
 349 handleNext() {
 350     this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
 351 }
 352 ```
 353 
 354 ---
 355 
 356 ## Multiple LWCs in One Screen
 357 
 358 ```xml
 359 <screens>
 360     <name>Multi_LWC_Screen</name>
 361     <label>Multiple Components</label>
 362 
 363     <!-- First LWC -->
 364     <fields>
 365         <name>headerComponent</name>
 366         <extensionName>c:flowHeader</extensionName>
 367         <fieldType>ComponentInstance</fieldType>
 368         <inputParameters>
 369             <name>title</name>
 370             <value><stringValue>Select Options</stringValue></value>
 371         </inputParameters>
 372     </fields>
 373 
 374     <!-- Standard Flow field between LWCs -->
 375     <fields>
 376         <name>instructions</name>
 377         <fieldText>&lt;p&gt;Choose from the options below&lt;/p&gt;</fieldText>
 378         <fieldType>DisplayText</fieldType>
 379     </fields>
 380 
 381     <!-- Second LWC -->
 382     <fields>
 383         <name>selectorComponent</name>
 384         <extensionName>c:recordSelector</extensionName>
 385         <fieldType>ComponentInstance</fieldType>
 386         <outputParameters>
 387             <assignToReference>var_SelectedId</assignToReference>
 388             <name>selectedId</name>
 389         </outputParameters>
 390     </fields>
 391 </screens>
 392 ```
 393 
 394 ---
 395 
 396 ## Error Handling
 397 
 398 ### Capture LWC Error Output
 399 
 400 ```xml
 401 <fields>
 402     <outputParameters>
 403         <assignToReference>var_ErrorMessage</assignToReference>
 404         <name>errorMessage</name>
 405     </outputParameters>
 406 </fields>
 407 
 408 <!-- Check for errors after screen -->
 409 <decisions>
 410     <name>Check_Errors</name>
 411     <rules>
 412         <name>Has_Error</name>
 413         <conditions>
 414             <leftValueReference>var_ErrorMessage</leftValueReference>
 415             <operator>IsNull</operator>
 416             <rightValue>
 417                 <booleanValue>false</booleanValue>
 418             </rightValue>
 419         </conditions>
 420         <connector>
 421             <targetReference>Error_Handler</targetReference>
 422         </connector>
 423     </rules>
 424 </decisions>
 425 ```
 426 
 427 ### LWC Dispatching Errors
 428 
 429 ```javascript
 430 handleError(error) {
 431     this.errorMessage = this.reduceErrors(error);
 432     this.dispatchEvent(new FlowAttributeChangeEvent(
 433         'errorMessage',
 434         this.errorMessage
 435     ));
 436 }
 437 ```
 438 
 439 ---
 440 
 441 ## Context Variables
 442 
 443 Pass Flow context to LWC using record context:
 444 
 445 ```xml
 446 <!-- In Flow: Map $Record context -->
 447 <inputParameters>
 448     <name>recordId</name>
 449     <value>
 450         <elementReference>$Record.Id</elementReference>
 451     </value>
 452 </inputParameters>
 453 <inputParameters>
 454     <name>objectApiName</name>
 455     <value>
 456         <elementReference>$Record.Object</elementReference>
 457     </value>
 458 </inputParameters>
 459 ```
 460 
 461 ---
 462 
 463 ## Templates
 464 
 465 | Template | Use Case |
 466 |----------|----------|
 467 | `assets/screen-flow-with-lwc.xml` | Complete LWC screen integration |
 468 | `assets/apex-action-template.xml` | Calling Apex from Flow |
 469 
 470 ---
 471 
 472 ## Cross-Skill Integration
 473 
 474 | Integration | See Also |
 475 |-------------|----------|
 476 | LWC Component Setup | [sf-lwc/references/flow-integration-guide.md](../../sf-lwc/references/flow-integration-guide.md) |
 477 | Full Triangle Architecture | [triangle-pattern.md](triangle-pattern.md) |
 478 | LWC FlowAttributeChangeEvent | [sf-lwc/assets/flow-screen-component/](../../sf-lwc/assets/flow-screen-component/) |
 479 
 480 ---
 481 
 482 ## Troubleshooting
 483 
 484 | Issue | Cause | Solution |
 485 |-------|-------|----------|
 486 | LWC not appearing in Flow Builder | Missing `isExposed` or target | Add `isExposed=true` and `target="lightning__FlowScreen"` |
 487 | Properties not showing in builder | Missing `targetConfigs` | Add `targetConfig` with property definitions |
 488 | Outputs not updating | Missing FlowAttributeChangeEvent | Dispatch event when value changes |
 489 | Type mismatch error | Wrong dataType | Match Flow variable type to LWC property type |
 490 | LWC not receiving inputs | Property name mismatch | Ensure `name` matches `@api` property exactly |
 491 | Navigation not working | Wrong event type | Use `FlowNavigationFinishEvent` with action string |
