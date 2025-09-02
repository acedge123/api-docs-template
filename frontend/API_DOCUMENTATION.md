# Scoring Engine API Documentation

## Authentication

All API endpoints require authentication using token-based authentication.

### Get Authentication Token
```http
POST /api/token-auth/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "token": "your_auth_token_here"
}
```

### Using Authentication
Include the token in the Authorization header:
```http
Authorization: Token your_auth_token_here
```

## Lead Management APIs

### Create Lead and Get Score
```http
POST /api/v1/leads/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "lead_id": "optional-uuid4",
    "answers": {
        "credit_score": "581-620",
        "income": "5000",
        "rent": "1500",
        "car_payment": "300",
        "multiple_choices": "one, two"
    }
}
```

Response:
```json
{
    "lead_id": "f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288",
    "x_axis": "18.00",
    "y_axis": "5.00",
    "total_score": "23.0",
    "recommendations": {
        "rent": {
            "response_text": "Your rent is too high",
            "affiliate_name": "Vendor A",
            "affiliate_image": "img src = 1",
            "affiliate_link": "https://www.vendora.com/?affiliate_id+1234",
            "redirect_url": ""
        }
    }
}
```

### Get Lead Details
```http
GET /api/v1/leads/{lead_id}/
Authorization: Token your_auth_token_here
```

## Admin APIs

### Questions Management

#### List Questions
```http
GET /api/v1/questions/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "number": 1,
        "text": "What is your credit score?",
        "field_name": "credit_score",
        "multiple_values": false,
        "type": "CH",
        "min_value": null,
        "max_value": null,
        "choices": [
            {
                "id": 1,
                "text": "300-580",
                "slug": "poor",
                "value": "300.00"
            }
        ],
        "scoring_model": {
            "id": 1,
            "weight": "1.00",
            "x_axis": true,
            "y_axis": false,
            "formula": "",
            "value_ranges": [],
            "dates_ranges": []
        },
        "recommendation": {
            "id": 1,
            "rule": "If {credit_score} < 600",
            "response_text": "Consider improving your credit score",
            "affiliate_name": "Credit Repair Co",
            "affiliate_image": "",
            "affiliate_link": "",
            "redirect_url": ""
        }
    }
]
```

#### Create Question
```http
POST /api/v1/questions/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "number": 1,
    "text": "What is your credit score?",
    "field_name": "credit_score",
    "type": "CH",
    "multiple_values": false
}
```

#### Update Question
```http
PUT /api/v1/questions/{id}/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "number": 1,
    "text": "Updated question text",
    "field_name": "credit_score",
    "type": "CH",
    "multiple_values": false
}
```

#### Delete Question
```http
DELETE /api/v1/questions/{id}/
Authorization: Token your_auth_token_here
```

#### Get Question Choices
```http
GET /api/v1/questions/{id}/choices/
Authorization: Token your_auth_token_here
```

#### Get Question Scoring Model
```http
GET /api/v1/questions/{id}/scoring_model/
Authorization: Token your_auth_token_here
```

#### Get Question Recommendation
```http
GET /api/v1/questions/{id}/recommendation/
Authorization: Token your_auth_token_here
```

### Choices Management

#### List Choices
```http
GET /api/v1/choices/
Authorization: Token your_auth_token_here
```

#### Create Choice
```http
POST /api/v1/choices/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "question": 1,
    "text": "Excellent (750+)",
    "slug": "excellent",
    "value": "750.00"
}
```

### Scoring Models Management

#### List Scoring Models
```http
GET /api/v1/scoring-models/
Authorization: Token your_auth_token_here
```

#### Create Scoring Model
```http
POST /api/v1/scoring-models/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "question": 1,
    "weight": "1.00",
    "x_axis": true,
    "y_axis": false,
    "formula": "{credit_score} * 0.1"
}
```

#### Get Scoring Model Value Ranges
```http
GET /api/v1/scoring-models/{id}/value_ranges/
Authorization: Token your_auth_token_here
```

#### Get Scoring Model Date Ranges
```http
GET /api/v1/scoring-models/{id}/dates_ranges/
Authorization: Token your_auth_token_here
```

### Value Ranges Management

#### List Value Ranges
```http
GET /api/v1/value-ranges/
Authorization: Token your_auth_token_here
```

#### Create Value Range
```http
POST /api/v1/value-ranges/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "scoring_model": 1,
    "start": "300.00",
    "end": "580.00",
    "points": 10
}
```

### Date Ranges Management

#### List Date Ranges
```http
GET /api/v1/dates-ranges/
Authorization: Token your_auth_token_here
```

#### Create Date Range
```http
POST /api/v1/dates-ranges/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "scoring_model": 1,
    "start": "2023-01-01",
    "end": "2023-12-31",
    "points": 15
}
```

### Recommendations Management

#### List Recommendations
```http
GET /api/v1/recommendations/
Authorization: Token your_auth_token_here
```

#### Create Recommendation
```http
POST /api/v1/recommendations/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "question": 1,
    "rule": "If {credit_score} < 600",
    "response_text": "Consider improving your credit score",
    "affiliate_name": "Credit Repair Co",
    "affiliate_image": "https://example.com/image.jpg",
    "affiliate_link": "https://example.com/affiliate",
    "redirect_url": "https://example.com/redirect"
}
```

### User Management

#### Get User Profile
```http
GET /api/v1/users/profile/
Authorization: Token your_auth_token_here
```

Response:
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_staff": true
}
```

#### Get User API Token
```http
GET /api/v1/users/token/
Authorization: Token your_auth_token_here
```

Response:
```json
{
    "token": "your_auth_token_here"
}
```

### Analytics APIs

#### Lead Summary Analytics
```http
GET /api/v1/analytics/lead_summary/
Authorization: Token your_auth_token_here
```

Response:
```json
{
    "total_leads": 150,
    "average_scores": {
        "x_axis": 25.5,
        "y_axis": 12.3,
        "total": 37.8
    },
    "score_distribution": {
        "low": 45,
        "medium": 78,
        "high": 27
    }
}
```

#### Question Analytics
```http
GET /api/v1/analytics/question_analytics/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "number": 1,
        "text": "What is your credit score?",
        "type": "CH",
        "field_name": "credit_score",
        "answer_distribution": [
            {
                "response": "excellent",
                "count": 45
            },
            {
                "response": "good",
                "count": 67
            }
        ],
        "total_answers": 150
    }
]
```

#### Recommendation Effectiveness
```http
GET /api/v1/analytics/recommendation_effectiveness/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "question_text": "What is your credit score?",
        "rule": "If {credit_score} < 600",
        "response_text": "Consider improving your credit score",
        "affiliate_name": "Credit Repair Co",
        "triggered_count": 23
    }
]
```

## Question Types

- `O` - Open (text input)
- `CH` - Choices (single selection)
- `MC` - Multiple Choices (multiple selection)
- `S` - Slider (numeric range)
- `I` - Integer (numeric input)
- `D` - Date (date input)

## Formula and Rule Syntax

### Supported Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`, `//`
- Comparison: `>`, `<`, `==`, `!=`, `>=`, `<=`
- Logical: `and`, `or`, `not`

### Supported Functions
- Aggregate: `count()`, `max()`, `mean()`, `median()`, `min()`, `sum()`
- Math: `sqrt()`
- Date: `days()`, `today()`

### Field References
Use field names in curly braces: `{field_name}`

Example formulas:
- `{income} * 0.1`
- `If {credit_score} < 600 and {income} > 5000`
- `mean({income}) * {credit_score}`

## Error Responses

### Validation Error
```json
{
    "field_name": ["Error message"]
}
```

### Authentication Error
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Permission Error
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Not Found Error
```json
{
    "detail": "Not found."
}
```
