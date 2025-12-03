# Salesforce Flow Testing Guide

Type-specific testing checklists and verification steps for deployed flows.

## Screen Flows

**Launch**: Setup → Flows → Run, or via URL:
```
https://[org].lightning.force.com/lightning/setup/Flows/page?address=%2F[FlowId]
```

**Test Checklist**:
- [ ] All navigation paths (Next/Previous/Finish)
- [ ] Input validation on each screen
- [ ] Multiple user profiles (Standard User, Custom, Permission Sets)
- [ ] Field visibility per profile
- [ ] Error handling displays correctly

## Record-Triggered Flows

**CRITICAL**: Always bulk test with 200+ records.

**Test Checklist**:
- [ ] Create single test record - verify trigger fires
- [ ] Bulk test via Data Loader (200+ records)
- [ ] Check Debug Logs for execution
- [ ] Verify entry conditions work correctly
- [ ] Test with different record types (if applicable)

**Query Recent Executions**:
```bash
sf data query --query "SELECT Id, Status FROM FlowInterview WHERE FlowDefinitionName='[FlowName]' ORDER BY CreatedDate DESC LIMIT 10" --target-org [org]
```

## Autolaunched Flows

**Test via Apex**:
```apex
Flow.Interview.[FlowName] flowInstance = new Flow.Interview.[FlowName](inputVars);
flowInstance.start();
```

**Test Checklist**:
- [ ] Create Apex test class with assertions
- [ ] Test edge cases: nulls, empty collections, max values
- [ ] Bulkification test (200+ records)
- [ ] Verify governor limits not exceeded

## Scheduled Flows

**Test Checklist**:
- [ ] Verify schedule configuration in Setup → Scheduled Jobs
- [ ] Manual "Run" test first (before enabling schedule)
- [ ] Monitor Debug Logs during execution
- [ ] Check batch processing works correctly
- [ ] Verify cleanup/completion logic

## Platform Event-Triggered Flows

**Test Checklist**:
- [ ] Publish test event via Apex/API
- [ ] Verify flow triggers on event
- [ ] Test high-volume scenarios
- [ ] Check replay ID handling (if applicable)

## Security & Profile Testing

**User Mode Flows**: Test with multiple profiles to verify FLS/CRUD respected.

```bash
sf org login user --username standard.user@company.com --target-org [org]
```

**System Mode Flows**: Requires security review - document justification for bypassing FLS/CRUD.

**Test Checklist**:
- [ ] Standard User profile - verify restricted access
- [ ] Admin profile - verify full access
- [ ] Custom profiles with Permission Sets
- [ ] Guest User (if public-facing)

## Governor Limits Testing

For record-triggered and scheduled flows, verify limits:

| Limit | Threshold | Action if Exceeded |
|-------|-----------|-------------------|
| SOQL Queries | 100 | Consolidate queries |
| DML Statements | 150 | Batch operations |
| Records Retrieved | 50,000 | Add filters |
| CPU Time | 10,000 ms | Optimize logic |

**Simulation** (optional):
```bash
python3 ~/.claude/skills/sf-flow-builder/validators/flow_simulator.py \
  force-app/main/default/flows/[FlowName].flow-meta.xml --test-records 200
```

## Post-Deployment Verification

1. **Check Flow Status**: Setup → Process Automation → Flows
2. **Review Debug Logs**: Developer Console → Debug Logs
3. **Monitor Flow Interviews**: Setup → Process Automation → Paused Flow Interviews
4. **Check Errors**: Setup → Process Automation → Flow Errors
