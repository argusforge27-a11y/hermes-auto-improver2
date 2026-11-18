# JSON Schemas for Skill Creator

## evals.json
```json
{
  "evals": [
    {
      "id": "string",
      "query": "string",
      "should_trigger": "boolean",
      "expectations": [
        {
          "text": "string",
          "passed": "boolean",
          "evidence": "string"
        }
      ]
    }
  ]
}
```

## grading.json
```json
{
  "skill": "string",
  "runs": [
    {
      "run_number": "integer",
      "configuration": "string",
      "eval_id": "integer",
      "result": {
        "pass_rate": "number",
        "time_seconds": "number",
        "tokens": "number"
      },
      "expectations": [
        {
          "text": "string",
          "passed": "boolean",
          "evidence": "string"
        }
      ]
    }
  ]
}
```

## benchmark.json (run_summary)
```json
{
  "metadata": {
    "skill_name": "string",
    "executor_model": "string",
    "timestamp": "number"
  },
  "run_summary": {
    "config_name": {
      "pass_rate": {"mean": "number", "stddev": "number"},
      "time_seconds": {"mean": "number", "stddev": "number"},
      "tokens": {"mean": "number", "stddev": "number"}
    },
    "delta": {
      "pass_rate": "string",
      "time_seconds": "string",
      "tokens": "string"
    }
  },
  "runs": [...],
  "notes": ["string"]
}
```

## improve_description.py input
```json
{
  "skill_name": "string",
  "current_description": "string",
  "train_queries": [{"query": "string", "should_trigger": "boolean"}],
  "test_queries": [{"query": "string", "should_trigger": "boolean"}],
  "iterations": "integer"
}
```
