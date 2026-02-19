<!-- Parent: sf-debug/SKILL.md -->
   1 # Apex Benchmarking Guide
   2 
   3 Performance testing is essential for writing efficient Apex code. This guide covers reliable benchmarking techniques and real-world performance data.
   4 
   5 > **Sources**:
   6 > - [James Simone - Benchmarking Matters](https://www.jamessimone.net/blog/joys-of-apex/benchmarking-matters/)
   7 > - [Dan Appleman - Advanced Apex Programming](https://www.advancedapex.com/)
   8 > - [Justus van den Berg - Heap & CPU Optimization](https://medium.com/@justusvandenberg)
   9 
  10 ---
  11 
  12 ## Why Benchmark?
  13 
  14 "Premature optimization is the root of all evil" - but **informed optimization** is essential. Benchmarking answers:
  15 
  16 1. **Which approach is faster?** (Loop styles, data structures)
  17 2. **Will this scale?** (200 records vs 10,000)
  18 3. **Where are the bottlenecks?** (CPU, heap, SOQL)
  19 
  20 ---
  21 
  22 ## Dan Appleman's Benchmarking Technique
  23 
  24 The gold standard for Apex performance testing:
  25 
  26 ### The Pattern
  27 
  28 ```apex
  29 // Run in Anonymous Apex for consistent environment
  30 Long startTime = System.currentTimeMillis();
  31 
  32 // Your code to benchmark
  33 for (Integer i = 0; i < 10000; i++) {
  34     // Operation being tested
  35 }
  36 
  37 Long endTime = System.currentTimeMillis();
  38 System.debug('Duration: ' + (endTime - startTime) + 'ms');
  39 ```
  40 
  41 ### Key Principles
  42 
  43 | Principle | Why It Matters |
  44 |-----------|----------------|
  45 | **Use Anonymous Apex** | Consistent execution environment, no trigger interference |
  46 | **Run Multiple Iterations** | Averages out JIT compilation and garbage collection |
  47 | **Test at Scale** | 200 records ≠ 10,000 records in terms of performance |
  48 | **Isolate the Operation** | Test one thing at a time |
  49 | **Run Multiple Times** | First run often slower due to JIT compilation |
  50 
  51 ### Example: Complete Benchmark
  52 
  53 ```apex
  54 // Comprehensive benchmark template
  55 public class BenchmarkRunner {
  56 
  57     public static void compareMethods() {
  58         Integer iterations = 10000;
  59 
  60         // Warm-up run (JIT compilation)
  61         warmUp();
  62 
  63         // Method A
  64         Long startA = System.currentTimeMillis();
  65         for (Integer i = 0; i < iterations; i++) {
  66             methodA();
  67         }
  68         Long durationA = System.currentTimeMillis() - startA;
  69 
  70         // Method B
  71         Long startB = System.currentTimeMillis();
  72         for (Integer i = 0; i < iterations; i++) {
  73             methodB();
  74         }
  75         Long durationB = System.currentTimeMillis() - startB;
  76 
  77         // Results
  78         System.debug('Method A: ' + durationA + 'ms');
  79         System.debug('Method B: ' + durationB + 'ms');
  80         System.debug('Difference: ' + Math.abs(durationA - durationB) + 'ms');
  81         System.debug('Winner: ' + (durationA < durationB ? 'Method A' : 'Method B'));
  82     }
  83 
  84     private static void warmUp() {
  85         for (Integer i = 0; i < 100; i++) {
  86             methodA();
  87             methodB();
  88         }
  89     }
  90 
  91     private static void methodA() { /* Implementation A */ }
  92     private static void methodB() { /* Implementation B */ }
  93 }
  94 ```
  95 
  96 ---
  97 
  98 ## Real-World Benchmark Results
  99 
 100 ### String Concatenation vs String.join()
 101 
 102 From Justus van den Berg's testing:
 103 
 104 | Method | Records | Duration | Result |
 105 |--------|---------|----------|--------|
 106 | String `+=` in loop | 1,750 | 11,767ms | CPU LIMIT HIT |
 107 | `String.join()` | 7,500 | 539ms | Still running |
 108 | **Improvement** | - | **22x faster** | - |
 109 
 110 ```apex
 111 // ❌ SLOW: String concatenation in loop (O(n²) string copies)
 112 String result = '';
 113 for (Account acc : accounts) {
 114     result += acc.Name + '\n';  // Creates new string each time!
 115 }
 116 
 117 // ✅ FAST: String.join() (O(n) single allocation)
 118 List<String> names = new List<String>();
 119 for (Account acc : accounts) {
 120     names.add(acc.Name);
 121 }
 122 String result = String.join(names, '\n');
 123 ```
 124 
 125 ### Loop Performance Comparison
 126 
 127 From Beyond the Cloud benchmarking (10,000 iterations):
 128 
 129 | Loop Type | Duration | Notes |
 130 |-----------|----------|-------|
 131 | While loop | ~0.4s | Fastest |
 132 | Cached iterator | ~0.8s | Good alternative |
 133 | For loop (index) | ~1.4s | Acceptable |
 134 | Enhanced for-each | ~2.4s | Convenient but slower |
 135 | Uncached iterator | CPU LIMIT | Avoid |
 136 
 137 ```apex
 138 // 🏆 FASTEST: While loop
 139 Iterator<Account> iter = accounts.iterator();
 140 while (iter.hasNext()) {
 141     Account acc = iter.next();
 142     // process
 143 }
 144 
 145 // ✅ GOOD: Traditional for loop
 146 for (Integer i = 0; i < accounts.size(); i++) {
 147     Account acc = accounts[i];
 148     // process
 149 }
 150 
 151 // ⚠️ CONVENIENT BUT SLOWER: Enhanced for-each
 152 for (Account acc : accounts) {
 153     // process - OK for small collections
 154 }
 155 ```
 156 
 157 ### Map vs List Lookup
 158 
 159 | Operation | Complexity | 10,000 lookups |
 160 |-----------|------------|----------------|
 161 | List.contains() | O(n) | ~500ms |
 162 | Set.contains() | O(1) | ~5ms |
 163 | Map.containsKey() | O(1) | ~5ms |
 164 
 165 ```apex
 166 // ❌ SLOW: List lookup
 167 List<Id> processedIds = new List<Id>();
 168 for (Account acc : accounts) {
 169     if (!processedIds.contains(acc.Id)) {  // O(n) each time!
 170         processedIds.add(acc.Id);
 171     }
 172 }
 173 
 174 // ✅ FAST: Set lookup
 175 Set<Id> processedIds = new Set<Id>();
 176 for (Account acc : accounts) {
 177     if (!processedIds.contains(acc.Id)) {  // O(1) constant time
 178         processedIds.add(acc.Id);
 179     }
 180 }
 181 ```
 182 
 183 ---
 184 
 185 ## Governor Limit Ceilings
 186 
 187 ### Official Limits
 188 
 189 | Limit | Synchronous | Asynchronous |
 190 |-------|-------------|--------------|
 191 | CPU Time | 10,000 ms | 60,000 ms |
 192 | Heap Size | 6 MB | 12 MB |
 193 | SOQL Queries | 100 | 200 |
 194 | DML Statements | 150 | 150 |
 195 
 196 ### Practical Thresholds
 197 
 198 | Limit | Warning (80%) | Critical (95%) |
 199 |-------|---------------|----------------|
 200 | CPU Time | 8,000 ms | 9,500 ms |
 201 | Heap Size | 4.8 MB | 5.7 MB |
 202 | SOQL Queries | 80 | 95 |
 203 
 204 ### Runtime Limit Checking
 205 
 206 ```apex
 207 public void processWithSafety(List<Account> accounts) {
 208     Integer cpuWarning = 8000;
 209     Integer heapWarning = 4800000;
 210 
 211     for (Account acc : accounts) {
 212         // Check before each operation
 213         if (Limits.getCpuTime() > cpuWarning) {
 214             System.debug(LoggingLevel.WARN,
 215                 'CPU approaching limit: ' + Limits.getCpuTime() + 'ms');
 216             // Consider switching to async or chunking
 217             break;
 218         }
 219 
 220         if (Limits.getHeapSize() > heapWarning) {
 221             System.debug(LoggingLevel.WARN,
 222                 'Heap approaching limit: ' + Limits.getHeapSize() + ' bytes');
 223             break;
 224         }
 225 
 226         processAccount(acc);
 227     }
 228 }
 229 ```
 230 
 231 ---
 232 
 233 ## Benchmarking Anti-Patterns
 234 
 235 ### ❌ Don't Do These
 236 
 237 | Anti-Pattern | Problem | Solution |
 238 |--------------|---------|----------|
 239 | Testing in triggers | Inconsistent environment | Use Anonymous Apex |
 240 | Single iteration | JIT variance affects results | Run 1000+ iterations |
 241 | Testing with 10 records | Doesn't reveal O(n²) issues | Test with 200+ records |
 242 | Ignoring warm-up | First run skewed by JIT | Add warm-up phase |
 243 | Mixing operations | Can't isolate bottleneck | Test one thing at a time |
 244 
 245 ---
 246 
 247 ## Benchmarking Checklist
 248 
 249 Before optimizing, verify:
 250 
 251 - [ ] Ran benchmark multiple times (3-5 runs)
 252 - [ ] Used 1000+ iterations for micro-benchmarks
 253 - [ ] Tested with production-scale data (200+ records)
 254 - [ ] Included warm-up phase
 255 - [ ] Ran in Anonymous Apex (not test context)
 256 - [ ] Compared both approaches fairly
 257 - [ ] Considered readability trade-offs
 258 
 259 ---
 260 
 261 ## When NOT to Optimize
 262 
 263 Sometimes clarity beats performance:
 264 
 265 ```apex
 266 // More readable, negligible performance difference for small collections
 267 for (Account acc : accounts) {
 268     acc.Description = acc.Name + ' - Updated';
 269 }
 270 
 271 // vs micro-optimized but harder to read
 272 Iterator<Account> iter = accounts.iterator();
 273 while (iter.hasNext()) {
 274     Account acc = iter.next();
 275     acc.Description = acc.Name + ' - Updated';
 276 }
 277 ```
 278 
 279 **Rule of thumb**: Optimize when:
 280 1. Processing 200+ records regularly
 281 2. Approaching governor limits
 282 3. User experience is affected
 283 4. Benchmarks show measurable improvement
 284 
 285 ---
 286 
 287 ## Related Resources
 288 
 289 - [assets/benchmarking-template.cls](../assets/benchmarking-template.cls) - Ready-to-use benchmark template
 290 - [assets/cpu-heap-optimization.cls](../assets/cpu-heap-optimization.cls) - Optimization patterns
 291 - [Apex Log Analyzer](./log-analysis-tools.md) - Visual performance analysis
