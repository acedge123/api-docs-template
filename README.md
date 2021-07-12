# Scoring Engine

Customizable scoring and recommendation model

## Scoring and recommendation main components

_**Warning:** After changing question's "Field name" afterwards require verification of all recommendations rules and 
scoring models formula to be sure that they are still working as intended._

### Question

Question could be one of three types:
- __Open.__ Questions without specific expected answer. Has no associated value, so can not be used in recommendations 
  rules and in scoring models formulas for X-axis, Y-axis score calculation.
- __Choices.__ Question with predefined expected answers options. Answer can be any text. Each answer option has 
  associated value. Can be used in recommendations rules and in scoring models formulas for X-axis, Y-axis score 
  calculation.
- __Slider.__ Question with predefined range of possible values. Answer is a value. Can be used in recommendations 
  rules and in scoring models formulas for X-axis, Y-axis score calculation.

### Scoring Model

There may be a scoring model associated with Choices and Slider questions. Points for that question will be determined
by calculated via formula value and defined set of value ranges. Scoring model formula may contain questions 
with values (as question's field name in curly brackets, e.g. {field_name}), in this case value for that 
question is used in scoring model formula calculation.

- X-axis score equals sum of scoring model weight multiplied by determined points for all questions with scoring model
  with x-axis equals True;
- Y-axis score equals sum of scoring model weight multiplied by determined points for all questions with scoring model
  with y-axis equals True;

Questions without choices do not affect X-axis or Y-axis scores.

### Recommendations

There may be a recommendation associated with Choices and Slider questions. Recommendation rule may contain questions 
with values (as question's field name in curly brackets, e.g. {field_name}), in this case value for that 
question is used in recommendation rule calculation. If rule is True, recommendation for associated question will be 
returned.

Recommendation can contain some of or all of:
- response text;
- affiliate name;
- affiliate image (url);
- affiliate link;
- redirect url.

Open questions may have recommendation associated with it, but can't be used in recommendation rule itself.

## Deployment

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)

### Local

#### Build the Stack

    docker-compose -f local.yml build

#### Run the Stack

    docker-compose -f local.yml up

#### Misc

    docker-compose -f local.yml run --rm django python manage.py makemigrations scoringengine
    docker-compose -f local.yml run --rm django python manage.py migrate

    docker-compose -f local.yml run --rm django python manage.py createsuperuser

    docker-compose -f local.yml run --rm django python manage.py shell

#### Run tests

    docker-compose -f local.yml run --rm django pytest

# Initial configuration

**It is not advised to use superuser for anything other than managing regular admins.**

## Creating group for regular admin

"Regular admin" group could be created manually or using script below. 
It should allow full access for Question, Choice, ScoringModel, ValueRange and Recommendation models, read access for 
Answer model and read and delete access for Lead model.

    docker-compose -f <envirovment>.yml run --rm django python manage.py shell

and execute following code:

```python
from django.contrib.auth.models import Group, Permission

permissions = []
for model in ['question', 'choice', 'recommendation', 'scoringmodel', 'valuerange']:
    for permission in ['add', 'change', 'delete', 'view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))

for model in ['lead']:
    for permission in ['delete', 'view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))
        
for model in ['answer']:
    for permission in ['view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))


g = Group.objects.create(name='Regular admin')
g.permissions.set(permissions)
g.save()
```

# Adding admin users

Login with superuser, add new user.

*For generating strong passwords you can use following command on mac and linux:*

    openssl rand -base64 16 | colrm 17

In edit, enable "Staff status" checkbox, add "Regular admin" group.
API Auth token should be created automatically. Optionally auth token related permissions can be assigned to admin user.

# Scoring engine API
## Auth
For clients to authenticate, the token key should be included in the Authorization HTTP header. 
The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```
To obtain a token clients may POST given the username and password to ```/api/token-auth/``` api endpoint.

## Endpoints

### /api/v1/leads/
#### Allowed method: POST
Using provided answers, calculate X-axis, Y-axis values and return it with recommendations according to rules.
"lead_id" is optional, if not provided it will be generated automatically.

##### Request example
```json
{
    "lead_id": "f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288",
    "answers": [
        {
            "field_name": "Credit_Score",
            "response": "581 - 620"
        },
        {
            "field_name": "Income",
            "response": "3000 - 4999"
        },
        {
            "field_name": "Rent",
            "response": "3000 - 3999"
        },
        {
            "field_name": "Car_Payment",
            "response": "300 - 399"
        }
    ]
}
```

##### Response example
```json
{
    "lead_id": "f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288",
    "x_axis": "18.00",
    "y_axis": "5.00",
    "recommendations": [
        {
            "field_name": "Rent",
            "response_text": "Q3. Your rent is too high",
            "affiliate_name": "Vendor A",
            "affiliate_image": "img src = 1",
            "affiliate_link": "https://www.vendora.com/?affiliate_id+1234",
            "redirect_url": ""
        }
    ]
}
```

### /api/v1/leads/<lead_id>/
#### Allowed method: GET
Return X-axis, Y-axis values with recommendations for provided lead.
