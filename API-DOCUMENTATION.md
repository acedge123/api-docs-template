# Lead Scoring API Documentation

## Authentication

All API requests require an `X-API-Key` header with your API key obtained from onboarding.

```bash
curl -X POST https://api-docs-template-production.up.railway.app/api/manage \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Actions

### `domain.leadscoring.questions.upsert_bulk`

Create or update questions for your tenant.

**Required Parameters:**
- `questions` (array): List of question objects

**Question Object Fields:**
- `field_name` (string, **required**): Unique identifier for the question (letters, numbers, underscore only)
- `number` (integer, **required**): Question number (must be >= 1, unique per owner)
- `text` (string, **required**): Question text (max 200 characters)
- `type` (string, **required**): Question type - one of:
  - `"MC"` - Multiple choices
  - `"CH"` - Choices (single choice)
  - `"O"` - Open (text input)
  - `"I"` - Integer
  - `"S"` - Slider
  - `"D"` - Date
- `choices` (array, **required for MC/CH types**): Array of choice objects
  - `text` (string, **required**): Choice display text
  - `value` (number, **required**): Choice value for scoring
  - `slug` (string, optional): Auto-generated from text if not provided
- `min_value` (integer, optional): For SLIDER/INTEGER types
- `max_value` (integer, optional): For SLIDER/INTEGER types
- `multiple_values` (boolean, optional): Default false

**Example Request:**
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
          {"text": "$0-10k", "value": 1},
          {"text": "$10k-50k", "value": 2},
          {"text": "$50k+", "value": 3}
        ]
      },
      {
        "field_name": "employees",
        "number": 2,
        "text": "How many employees?",
        "type": "I",
        "min_value": 1,
        "max_value": 10000
      },
      {
        "field_name": "notes",
        "number": 3,
        "text": "Additional notes",
        "type": "O"
      }
    ]
  }
}
```

**Common Errors:**
- `question_number` field doesn't exist → Use `number` instead
- `question` field doesn't exist → Use `text` instead
- `options` field doesn't exist → Use `choices` array with `text` and `value`
- `number` must be >= 1 → Start from 1, not 0
- `field_name` validation error → Use only letters, numbers, underscore

## Question Types Reference

### Multiple Choice (MC)
```json
{
  "field_name": "budget",
  "number": 1,
  "text": "What is your budget?",
  "type": "MC",
  "choices": [
    {"text": "Option 1", "value": 1},
    {"text": "Option 2", "value": 2}
  ]
}
```

### Single Choice (CH)
```json
{
  "field_name": "priority",
  "number": 2,
  "text": "What is your priority?",
  "type": "CH",
  "choices": [
    {"text": "High", "value": 3},
    {"text": "Medium", "value": 2},
    {"text": "Low", "value": 1}
  ]
}
```

### Open Text (O)
```json
{
  "field_name": "notes",
  "number": 3,
  "text": "Additional notes",
  "type": "O"
}
```

### Integer (I)
```json
{
  "field_name": "employees",
  "number": 4,
  "text": "How many employees?",
  "type": "I",
  "min_value": 1,
  "max_value": 10000
}
```

### Slider (S)
```json
{
  "field_name": "satisfaction",
  "number": 5,
  "text": "Satisfaction level (1-10)?",
  "type": "S",
  "min_value": 1,
  "max_value": 10
}
```

### Date (D)
```json
{
  "field_name": "start_date",
  "number": 6,
  "text": "When do you want to start?",
  "type": "D"
}
```
