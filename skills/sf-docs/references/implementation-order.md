# sf-docs Implementation Order

Recommended implementation order for v1:

1. Define the `sf-docs` skill contract and make it a core skill
2. Define local-first / Salesforce-aware runtime behavior
3. Add `sf-docs` to `README.md` and `skills-registry.json`
4. Define local corpus layout and runtime detection rules
5. Build the discovery manifest and seed guide set
6. Define targeted HTML/PDF normalization policy
7. Define local artifact retrieval instructions
8. Define Salesforce-aware fallback instructions
9. Validate the benchmark against real failing queries
10. Expand only after the pilot corpus is healthy

## Notes

- `sf-docs` remains mandatory as part of the skill suite
- the pilot corpus should be kept intentionally small until benchmark results are healthy
- broad crawling and parallel retrieval are deferred until after v1 validation
- external index-specific logic is intentionally removed from the design
