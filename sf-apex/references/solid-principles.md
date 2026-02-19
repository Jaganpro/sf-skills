<!-- Parent: sf-apex/SKILL.md -->
   1 # SOLID Principles in Apex
   2 
   3 ## Overview
   4 
   5 SOLID principles guide object-oriented design for maintainable, flexible code.
   6 
   7 | Principle | Summary |
   8 |-----------|---------|
   9 | **S**ingle Responsibility | One reason to change |
  10 | **O**pen/Closed | Open for extension, closed for modification |
  11 | **L**iskov Substitution | Subtypes must be substitutable |
  12 | **I**nterface Segregation | Small, specific interfaces |
  13 | **D**ependency Inversion | Depend on abstractions |
  14 
  15 ---
  16 
  17 ## S - Single Responsibility Principle
  18 
  19 > "A module should have one, and only one, reason to change."
  20 
  21 ### Problem: Multiple Responsibilities
  22 
  23 ```apex
  24 // BAD: Class has multiple reasons to change
  25 public class OrderProcessor {
  26     public void processOrder(Order__c order) {
  27         // Validate order (reason 1: validation rules change)
  28         if (order.Total__c <= 0) {
  29             throw new ValidationException('Invalid total');
  30         }
  31 
  32         // Calculate tax (reason 2: tax rules change)
  33         Decimal tax = order.Total__c * 0.08;
  34         order.Tax__c = tax;
  35 
  36         // Send email (reason 3: notification requirements change)
  37         Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
  38         email.setToAddresses(new List<String>{order.Customer_Email__c});
  39         Messaging.sendEmail(new List<Messaging.Email>{email});
  40 
  41         // Save to database (reason 4: persistence logic changes)
  42         update order;
  43     }
  44 }
  45 ```
  46 
  47 ### Solution: Separate Responsibilities
  48 
  49 ```apex
  50 // GOOD: Each class has single responsibility
  51 public class OrderValidator {
  52     public void validate(Order__c order) {
  53         if (order.Total__c <= 0) {
  54             throw new ValidationException('Invalid total');
  55         }
  56     }
  57 }
  58 
  59 public class TaxCalculator {
  60     public Decimal calculate(Decimal amount) {
  61         return amount * 0.08;
  62     }
  63 }
  64 
  65 public class OrderNotificationService {
  66     public void sendConfirmation(Order__c order) {
  67         // Email logic
  68     }
  69 }
  70 
  71 public class OrderService {
  72     private OrderValidator validator;
  73     private TaxCalculator taxCalc;
  74     private OrderNotificationService notifier;
  75 
  76     public void processOrder(Order__c order) {
  77         validator.validate(order);
  78         order.Tax__c = taxCalc.calculate(order.Total__c);
  79         update order;
  80         notifier.sendConfirmation(order);
  81     }
  82 }
  83 ```
  84 
  85 ---
  86 
  87 ## O - Open/Closed Principle
  88 
  89 > "Software entities should be open for extension, but closed for modification."
  90 
  91 ### Problem: Modifying Existing Code
  92 
  93 ```apex
  94 // BAD: Must modify class to add new discount type
  95 public class DiscountCalculator {
  96     public Decimal calculate(String discountType, Decimal amount) {
  97         if (discountType == 'PERCENTAGE') {
  98             return amount * 0.1;
  99         } else if (discountType == 'FIXED') {
 100             return 50;
 101         } else if (discountType == 'VIP') {  // Added later
 102             return amount * 0.2;
 103         }
 104         // Keep adding else-if for each new type...
 105         return 0;
 106     }
 107 }
 108 ```
 109 
 110 ### Solution: Extend Without Modifying
 111 
 112 ```apex
 113 // GOOD: Add new discount types without changing existing code
 114 public interface DiscountStrategy {
 115     Decimal calculate(Decimal amount);
 116 }
 117 
 118 public class PercentageDiscount implements DiscountStrategy {
 119     private Decimal rate;
 120 
 121     public PercentageDiscount(Decimal rate) {
 122         this.rate = rate;
 123     }
 124 
 125     public Decimal calculate(Decimal amount) {
 126         return amount * rate;
 127     }
 128 }
 129 
 130 public class FixedDiscount implements DiscountStrategy {
 131     private Decimal fixedAmount;
 132 
 133     public FixedDiscount(Decimal fixedAmount) {
 134         this.fixedAmount = fixedAmount;
 135     }
 136 
 137     public Decimal calculate(Decimal amount) {
 138         return fixedAmount;
 139     }
 140 }
 141 
 142 // To add VIP discount: create new class, no modification needed
 143 public class VIPDiscount implements DiscountStrategy {
 144     public Decimal calculate(Decimal amount) {
 145         return amount * 0.2;
 146     }
 147 }
 148 
 149 public class DiscountCalculator {
 150     private Map<String, DiscountStrategy> strategies;
 151 
 152     public Decimal calculate(String type, Decimal amount) {
 153         DiscountStrategy strategy = strategies.get(type);
 154         return strategy?.calculate(amount) ?? 0;
 155     }
 156 }
 157 ```
 158 
 159 ### Real-World Example: Trigger Actions Framework
 160 
 161 TAF follows OCP - add new behaviors via metadata configuration without modifying the trigger or handler.
 162 
 163 ---
 164 
 165 ## L - Liskov Substitution Principle
 166 
 167 > "Subtypes must be substitutable for their base types."
 168 
 169 ### Problem: Subtype Breaks Contract
 170 
 171 ```apex
 172 // BAD: Lead violates SObject update contract when converted
 173 public class RecordUpdater {
 174     public void updateRecord(SObject record) {
 175         // This fails for converted Leads!
 176         if (record instanceof Lead) {
 177             Lead l = (Lead)record;
 178             if ([SELECT IsConverted FROM Lead WHERE Id = :l.Id].IsConverted) {
 179                 return;  // Can't update converted lead
 180             }
 181         }
 182         update record;
 183     }
 184 }
 185 ```
 186 
 187 ### Solution: Design for Substitutability
 188 
 189 ```apex
 190 // GOOD: Interface defines clear contract
 191 public interface Updatable {
 192     Boolean canUpdate();
 193     void performUpdate();
 194 }
 195 
 196 public class AccountUpdater implements Updatable {
 197     private Account record;
 198 
 199     public Boolean canUpdate() {
 200         return true;  // Accounts can always be updated
 201     }
 202 
 203     public void performUpdate() {
 204         update record;
 205     }
 206 }
 207 
 208 public class LeadUpdater implements Updatable {
 209     private Lead record;
 210 
 211     public Boolean canUpdate() {
 212         return ![SELECT IsConverted FROM Lead WHERE Id = :record.Id].IsConverted;
 213     }
 214 
 215     public void performUpdate() {
 216         if (canUpdate()) {
 217             update record;
 218         }
 219     }
 220 }
 221 
 222 // Consumer doesn't need type checking
 223 public class RecordService {
 224     public void updateRecord(Updatable record) {
 225         if (record.canUpdate()) {
 226             record.performUpdate();
 227         }
 228     }
 229 }
 230 ```
 231 
 232 ---
 233 
 234 ## I - Interface Segregation Principle
 235 
 236 > "Clients should not be forced to depend on interfaces they don't use."
 237 
 238 ### Problem: Fat Interface
 239 
 240 ```apex
 241 // BAD: Interface forces unnecessary implementations
 242 public interface RecordProcessor {
 243     void validate(SObject record);
 244     void calculate(SObject record);
 245     void sendNotification(SObject record);
 246     void createAuditLog(SObject record);
 247     void syncToExternal(SObject record);
 248 }
 249 
 250 // Simple processor forced to implement everything
 251 public class SimpleProcessor implements RecordProcessor {
 252     public void validate(SObject record) { /* actual logic */ }
 253     public void calculate(SObject record) { /* actual logic */ }
 254 
 255     // Forced to implement these even though not needed
 256     public void sendNotification(SObject record) { }
 257     public void createAuditLog(SObject record) { }
 258     public void syncToExternal(SObject record) { }
 259 }
 260 ```
 261 
 262 ### Solution: Small, Focused Interfaces
 263 
 264 ```apex
 265 // GOOD: Segregated interfaces
 266 public interface Validatable {
 267     void validate(SObject record);
 268 }
 269 
 270 public interface Calculable {
 271     void calculate(SObject record);
 272 }
 273 
 274 public interface Notifiable {
 275     void sendNotification(SObject record);
 276 }
 277 
 278 public interface Auditable {
 279     void createAuditLog(SObject record);
 280 }
 281 
 282 // Implement only what you need
 283 public class SimpleProcessor implements Validatable, Calculable {
 284     public void validate(SObject record) { /* logic */ }
 285     public void calculate(SObject record) { /* logic */ }
 286 }
 287 
 288 public class FullProcessor implements Validatable, Calculable, Notifiable, Auditable {
 289     public void validate(SObject record) { /* logic */ }
 290     public void calculate(SObject record) { /* logic */ }
 291     public void sendNotification(SObject record) { /* logic */ }
 292     public void createAuditLog(SObject record) { /* logic */ }
 293 }
 294 ```
 295 
 296 ### Salesforce Example: Database.Batchable Options
 297 
 298 ```apex
 299 // Implement only what you need
 300 public class SimpleBatch implements Database.Batchable<SObject> {
 301     // Just the required interface
 302 }
 303 
 304 public class StatefulBatch implements Database.Batchable<SObject>, Database.Stateful {
 305     // Add stateful when needed
 306 }
 307 
 308 public class CalloutBatch implements Database.Batchable<SObject>, Database.AllowsCallouts {
 309     // Add callouts when needed
 310 }
 311 ```
 312 
 313 ---
 314 
 315 ## D - Dependency Inversion Principle
 316 
 317 > "High-level modules should not depend on low-level modules. Both should depend on abstractions."
 318 
 319 ### Problem: Direct Dependencies
 320 
 321 ```apex
 322 // BAD: High-level class depends on concrete implementation
 323 public class OrderService {
 324     private EmailService emailService;      // Concrete class
 325     private StripePaymentGateway gateway;   // Concrete class
 326 
 327     public OrderService() {
 328         this.emailService = new EmailService();
 329         this.gateway = new StripePaymentGateway();
 330     }
 331 
 332     public void processOrder(Order__c order) {
 333         gateway.charge(order.Total__c);
 334         emailService.send(order.Customer_Email__c);
 335     }
 336 }
 337 ```
 338 
 339 ### Solution: Depend on Abstractions
 340 
 341 ```apex
 342 // GOOD: Depend on interfaces, inject implementations
 343 public interface PaymentGateway {
 344     PaymentResult charge(Decimal amount);
 345 }
 346 
 347 public interface NotificationService {
 348     void send(String recipient, String message);
 349 }
 350 
 351 public class StripeGateway implements PaymentGateway {
 352     public PaymentResult charge(Decimal amount) {
 353         // Stripe-specific logic
 354     }
 355 }
 356 
 357 public class EmailNotification implements NotificationService {
 358     public void send(String recipient, String message) {
 359         // Email-specific logic
 360     }
 361 }
 362 
 363 // High-level class depends on abstractions
 364 public class OrderService {
 365     private PaymentGateway gateway;
 366     private NotificationService notifier;
 367 
 368     // Constructor injection
 369     public OrderService(PaymentGateway gateway, NotificationService notifier) {
 370         this.gateway = gateway;
 371         this.notifier = notifier;
 372     }
 373 
 374     public void processOrder(Order__c order) {
 375         gateway.charge(order.Total__c);
 376         notifier.send(order.Customer_Email__c, 'Order confirmed');
 377     }
 378 }
 379 
 380 // Easy to test with mocks
 381 @isTest
 382 static void testOrderService() {
 383     PaymentGateway mockGateway = new MockPaymentGateway();
 384     NotificationService mockNotifier = new MockNotificationService();
 385 
 386     OrderService service = new OrderService(mockGateway, mockNotifier);
 387     // Test without real payment or email
 388 }
 389 ```
 390 
 391 ---
 392 
 393 ## Summary
 394 
 395 | Principle | Violation Sign | Solution |
 396 |-----------|---------------|----------|
 397 | SRP | Class has multiple reasons to change | Split into focused classes |
 398 | OCP | Adding features requires modifying existing code | Use strategy pattern, interfaces |
 399 | LSP | Type checking before using base type | Redesign hierarchy, use composition |
 400 | ISP | Empty method implementations | Split into smaller interfaces |
 401 | DIP | Creating concrete dependencies in constructor | Inject dependencies via constructor |
