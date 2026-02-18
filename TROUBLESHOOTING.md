# Troubleshooting Guide for Lead Scoring API

## Onboarding Issues

### Error: "agent_id is required" or "email is required"
**Solution:** Make sure your request includes both `agent_id` and `email` fields:
```json
{
  "agent_id": "your-unique-agent-id",
  "email": "your-email@example.com"
}
```

### Error: "Onboarding service not configured"
**Solution:** This is a server-side issue. Contact support or try again later.

### Error: "Failed to create tenant"
**Solution:** 
- Check that your `agent_id` is unique
- Verify your email is valid
- Try again - the service may be temporarily unavailable

## API Call Issues

### Error: "Missing or invalid X-API-Key"
**Solution:** 
- Make sure you're including the `X-API-Key` header (not `x-api-key` or `API-Key`)
- Verify you're using the API key from the onboarding response
- Check for extra spaces or newlines in the API key

### Error: "Invalid API Key"
**Solution:**
- The API key may have been revoked or doesn't exist
- Re-onboard to get a new API key
- Make sure you're using the key from the most recent onboarding

### Error: "Authorization check failed" or Timeout
**Solution:**
- This usually means the authorization service is slow or unavailable
- Wait a few seconds and try again
- If it persists, contact support

### Error: "UPGRADE_REQUIRED"
**Solution:**
- You've reached your free tier limit (100 calls)
- Add a payment method to continue using the API
- Check your usage: `GET /api/usage` with your API key

## Question Creation Issues

### Error: "Question field_name is required"
**Solution:** Every question must have a `field_name`:
```json
{
  "field_name": "budget",
  "number": 1,
  "text": "What is your budget?",
  "type": "MC"
}
```

### Error: "question_number constraint violation" or "number must be >= 1"
**Solution:**
- Use `number` (not `question_number`)
- `number` must be 1 or greater (not 0)
- Each question number must be unique per owner

**Correct format:**
```json
{
  "field_name": "budget",
  "number": 1,  // Must be >= 1
  "text": "What is your budget?",
  "type": "MC"
}
```

### Error: "choice value required"
**Solution:** For MC/CH type questions, each choice must have both `text` and `value`:
```json
{
  "field_name": "budget",
  "number": 1,
  "text": "What is your budget?",
  "type": "MC",
  "choices": [
    {"text": "$0-10k", "value": 1},  // Both text and value required
    {"text": "$10k-50k", "value": 2}
  ]
}
```

### Error: "field_name validation error"
**Solution:** `field_name` can only contain:
- Letters (a-z, A-Z)
- Numbers (0-9)
- Underscores (_)
- No spaces, hyphens, or special characters

**Valid examples:**
- `budget`
- `employee_count`
- `priority_level_1`

**Invalid examples:**
- `budget-range` (hyphen not allowed)
- `employee count` (space not allowed)
- `priority@level` (special character not allowed)

### Error: "Invalid type" or "type must be one of..."
**Solution:** Use the correct type codes:
- `"MC"` - Multiple choices
- `"CH"` - Single choice
- `"O"` - Open text
- `"I"` - Integer
- `"S"` - Slider
- `"D"` - Date

**Common mistakes:**
- ❌ `"multiple_choice"` → ✅ `"MC"`
- ❌ `"multiple choice"` → ✅ `"MC"`
- ❌ `"text"` → ✅ `"O"` (for open text)

## Common Field Name Mistakes

### Wrong Field Names (Don't Use These)
- ❌ `question` → ✅ `text`
- ❌ `question_number` → ✅ `number`
- ❌ `options` → ✅ `choices` (and it must be an array of objects, not strings)

### Correct Format Example
```json
{
  "action": "domain.leadscoring.questions.upsert_bulk",
  "params": {
    "questions": [
      {
        "field_name": "budget",           // ✅ Required
        "number": 1,                       // ✅ Required, must be >= 1
        "text": "What is your budget?",    // ✅ Required
        "type": "MC",                      // ✅ Required, use codes: MC, CH, O, I, S, D
        "choices": [                       // ✅ Required for MC/CH types
          {"text": "$0-10k", "value": 1}, // ✅ Each choice needs text and value
          {"text": "$10k-50k", "value": 2}
        ]
      }
    ]
  }
}
```

## Usage and Limits

### How to Check Your Usage
```bash
curl -X GET https://api-docs-template-production.up.railway.app/api/usage \
  -H "X-API-Key: YOUR_API_KEY"
```

### Free Tier Limits
- **100 calls per month** included free
- After 100 calls, you'll get `UPGRADE_REQUIRED` error
- Add a payment method to continue

### Warning Messages
If you see a warning in the response like:
```json
{
  "ok": true,
  "data": {...},
  "warning": {
    "message": "You have 9 free calls remaining..."
  }
}
```
This means you're approaching your limit. Add a payment method soon.

## Getting Help

### Check the API Documentation
See `API-DOCUMENTATION.md` for complete API reference with examples for all question types.

### Verify Your Request Format
1. Check that you're using the correct field names (see "Common Field Name Mistakes" above)
2. Verify your JSON is valid
3. Make sure required fields are present

### Still Having Issues?
1. **Check the error message** - it usually tells you what's wrong
2. **Verify your API key** - make sure it's from the onboarding response
3. **Check field names** - use the exact names from the documentation
4. **Try a simple request first** - start with one question to verify your setup

## Quick Reference

### Minimal Valid Request
```json
{
  "action": "domain.leadscoring.questions.upsert_bulk",
  "params": {
    "questions": [
      {
        "field_name": "test",
        "number": 1,
        "text": "Test question?",
        "type": "O"
      }
    ]
  }
}
```

### Multiple Choice Example
```json
{
  "action": "domain.leadscoring.questions.upsert_bulk",
  "params": {
    "questions": [
      {
        "field_name": "budget",
        "number": 1,
        "text": "What is your budget?",
        "type": "MC",
        "choices": [
          {"text": "Low", "value": 1},
          {"text": "Medium", "value": 2},
          {"text": "High", "value": 3}
        ]
      }
    ]
  }
}
```

### Complete Request with Headers
```bash
curl -X POST https://api-docs-template-production.up.railway.app/api/manage \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "domain.leadscoring.questions.upsert_bulk",
    "params": {
      "questions": [{
        "field_name": "budget",
        "number": 1,
        "text": "What is your budget?",
        "type": "MC",
        "choices": [
          {"text": "$0-10k", "value": 1},
          {"text": "$10k-50k", "value": 2},
          {"text": "$50k+", "value": 3}
        ]
      }]
    }
  }'
```
