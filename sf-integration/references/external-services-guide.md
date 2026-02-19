<!-- Parent: sf-integration/SKILL.md -->
   1 # External Services Guide
   2 
   3 ## Overview
   4 
   5 External Services in Salesforce automatically generate Apex classes from OpenAPI (Swagger) specifications, enabling type-safe REST API integrations without writing HTTP code.
   6 
   7 ## How It Works
   8 
   9 ```
  10 ┌─────────────────────────────────────────────────────────────────┐
  11 │  EXTERNAL SERVICE FLOW                                          │
  12 ├─────────────────────────────────────────────────────────────────┤
  13 │                                                                 │
  14 │  1. OpenAPI Spec (JSON/YAML)                                    │
  15 │     ↓                                                           │
  16 │  2. External Service Registration (Metadata)                    │
  17 │     ↓                                                           │
  18 │  3. Auto-generated Apex Classes                                 │
  19 │     ↓                                                           │
  20 │  4. Type-safe API calls from Apex                              │
  21 │                                                                 │
  22 └─────────────────────────────────────────────────────────────────┘
  23 ```
  24 
  25 ## Prerequisites
  26 
  27 1. **Named Credential** configured for authentication
  28 2. **OpenAPI Specification** (2.0 or 3.0) for the API
  29 3. **API Version 48.0+** (Winter '20)
  30 
  31 ## Creating External Service
  32 
  33 ### Via Setup UI
  34 
  35 1. Go to **Setup → External Services**
  36 2. Click **New External Service**
  37 3. Provide name and description
  38 4. Select **Named Credential**
  39 5. Upload or paste OpenAPI spec
  40 6. Review operations
  41 7. Save
  42 
  43 ### Via Metadata API
  44 
  45 ```xml
  46 <?xml version="1.0" encoding="UTF-8"?>
  47 <ExternalServiceRegistration xmlns="http://soap.sforce.com/2006/04/metadata">
  48     <label>Stripe API</label>
  49     <description>Stripe payment processing API</description>
  50     <namedCredential>Stripe_API</namedCredential>
  51     <schemaType>OpenApi3</schemaType>
  52     <schema>
  53 {
  54   "openapi": "3.0.0",
  55   "info": { "title": "Stripe API", "version": "1.0" },
  56   "paths": { ... }
  57 }
  58     </schema>
  59     <status>Complete</status>
  60 </ExternalServiceRegistration>
  61 ```
  62 
  63 ## Generated Classes
  64 
  65 For an External Service named "StripeAPI":
  66 
  67 | Class | Purpose |
  68 |-------|---------|
  69 | `ExternalService.StripeAPI` | Main service class with operation methods |
  70 | `ExternalService.StripeAPI_createCustomer_Request` | Request wrapper |
  71 | `ExternalService.StripeAPI_createCustomer_Response` | Response wrapper |
  72 | `ExternalService.StripeAPI_Customer` | DTO matching schema |
  73 
  74 ## Usage Patterns
  75 
  76 ### Basic GET Request
  77 
  78 ```apex
  79 // Instantiate service
  80 ExternalService.StripeAPI stripe = new ExternalService.StripeAPI();
  81 
  82 // Call GET operation
  83 ExternalService.StripeAPI_getCustomer_Response response =
  84     stripe.getCustomer('cus_ABC123');
  85 
  86 // Access response data
  87 String email = response.email;
  88 ```
  89 
  90 ### POST with Request Body
  91 
  92 ```apex
  93 // Create request object
  94 ExternalService.StripeAPI_createCustomer_Request request =
  95     new ExternalService.StripeAPI_createCustomer_Request();
  96 request.email = 'customer@example.com';
  97 request.name = 'John Doe';
  98 
  99 // Make call
 100 ExternalService.StripeAPI_createCustomer_Response response =
 101     stripe.createCustomer(request);
 102 
 103 // Get created resource ID
 104 String customerId = response.id;
 105 ```
 106 
 107 ### Handling Nested Objects
 108 
 109 ```apex
 110 // Access nested data
 111 ExternalService.StripeAPI_Address address = response.address;
 112 String city = address.city;
 113 String postalCode = address.postalCode;
 114 ```
 115 
 116 ## Error Handling
 117 
 118 ```apex
 119 try {
 120     ExternalService.StripeAPI stripe = new ExternalService.StripeAPI();
 121     response = stripe.getCustomer('invalid_id');
 122 
 123 } catch (ExternalService.ExternalServiceException e) {
 124     // API returned error response
 125     System.debug('Status Code: ' + e.getStatusCode());
 126     System.debug('Error Body: ' + e.getBody());
 127     System.debug('Error Message: ' + e.getMessage());
 128 
 129 } catch (CalloutException e) {
 130     // Network/connection error
 131     System.debug('Connection failed: ' + e.getMessage());
 132 }
 133 ```
 134 
 135 ## Async Calls (Queueable)
 136 
 137 Use Queueable for calls from triggers:
 138 
 139 ```apex
 140 public class StripeCustomerSync implements Queueable, Database.AllowsCallouts {
 141 
 142     private Account account;
 143 
 144     public StripeCustomerSync(Account account) {
 145         this.account = account;
 146     }
 147 
 148     public void execute(QueueableContext context) {
 149         ExternalService.StripeAPI stripe = new ExternalService.StripeAPI();
 150 
 151         ExternalService.StripeAPI_createCustomer_Request req =
 152             new ExternalService.StripeAPI_createCustomer_Request();
 153         req.email = account.Email__c;
 154         req.name = account.Name;
 155 
 156         try {
 157             ExternalService.StripeAPI_createCustomer_Response resp =
 158                 stripe.createCustomer(req);
 159 
 160             account.Stripe_Customer_Id__c = resp.id;
 161             update account;
 162         } catch (Exception e) {
 163             System.debug('Sync failed: ' + e.getMessage());
 164         }
 165     }
 166 }
 167 ```
 168 
 169 ## OpenAPI Schema Tips
 170 
 171 ### Supported Features
 172 
 173 - GET, POST, PUT, PATCH, DELETE methods
 174 - Path and query parameters
 175 - Request and response bodies
 176 - JSON schema types (string, number, boolean, object, array)
 177 - References ($ref)
 178 - Basic authentication headers
 179 
 180 ### Limitations
 181 
 182 - **No file uploads** (multipart/form-data limited)
 183 - **No WebSockets** (HTTP only)
 184 - **No streaming responses**
 185 - **Some complex schemas** may not parse
 186 - **Maximum schema size** limited
 187 
 188 ### Schema Best Practices
 189 
 190 ```json
 191 {
 192   "openapi": "3.0.0",
 193   "info": {
 194     "title": "My API",
 195     "version": "1.0.0"
 196   },
 197   "paths": {
 198     "/customers/{id}": {
 199       "get": {
 200         "operationId": "getCustomer",
 201         "parameters": [
 202           {
 203             "name": "id",
 204             "in": "path",
 205             "required": true,
 206             "schema": { "type": "string" }
 207           }
 208         ],
 209         "responses": {
 210           "200": {
 211             "description": "Success",
 212             "content": {
 213               "application/json": {
 214                 "schema": { "$ref": "#/components/schemas/Customer" }
 215               }
 216             }
 217           }
 218         }
 219       }
 220     }
 221   },
 222   "components": {
 223     "schemas": {
 224       "Customer": {
 225         "type": "object",
 226         "properties": {
 227           "id": { "type": "string" },
 228           "email": { "type": "string" }
 229         }
 230       }
 231     }
 232   }
 233 }
 234 ```
 235 
 236 ## Updating External Service
 237 
 238 When API changes:
 239 
 240 1. Get updated OpenAPI spec
 241 2. Go to Setup → External Services
 242 3. Edit service
 243 4. Upload new schema
 244 5. Review changes to operations
 245 6. Save and validate
 246 7. Update calling code if signatures changed
 247 
 248 ## Testing
 249 
 250 ```apex
 251 @isTest
 252 private class StripeIntegrationTest {
 253 
 254     @isTest
 255     static void testCreateCustomer() {
 256         // Set mock
 257         Test.setMock(HttpCalloutMock.class, new StripeMock());
 258 
 259         Test.startTest();
 260 
 261         ExternalService.StripeAPI stripe = new ExternalService.StripeAPI();
 262         ExternalService.StripeAPI_createCustomer_Request req =
 263             new ExternalService.StripeAPI_createCustomer_Request();
 264         req.email = 'test@example.com';
 265 
 266         ExternalService.StripeAPI_createCustomer_Response resp =
 267             stripe.createCustomer(req);
 268 
 269         Test.stopTest();
 270 
 271         System.assertEquals('cus_test123', resp.id);
 272     }
 273 
 274     private class StripeMock implements HttpCalloutMock {
 275         public HttpResponse respond(HttpRequest request) {
 276             HttpResponse response = new HttpResponse();
 277             response.setStatusCode(201);
 278             response.setBody('{"id": "cus_test123", "email": "test@example.com"}');
 279             return response;
 280         }
 281     }
 282 }
 283 ```
 284 
 285 ## Use with Agentforce
 286 
 287 External Services are ideal for Agent Actions:
 288 
 289 1. Create External Service from API spec
 290 2. Create Flow that calls External Service
 291 3. Reference Flow in Agent Script action
 292 
 293 ```agentscript
 294 actions:
 295     lookup_customer:
 296         description: "Looks up customer in payment system"
 297         inputs:
 298             customer_email: string
 299         outputs:
 300             customer_id: string
 301         target: "flow://Lookup_Stripe_Customer"
 302 ```
