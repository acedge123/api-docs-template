import json

from scoringengine.templatetags.scoringengine_extras import pretty_json


class TestScoringEngineExtras:
    def test_pretty_json(self):
        data = {
            "lead_id": "uuid4",
            "answers": [
                {"field_name": "name1", "response": "1"},
                {"field_name": "name2", "response": "2"},
            ],
        }

        result = pretty_json(data)

        assert result == json.dumps(data, indent=4)
