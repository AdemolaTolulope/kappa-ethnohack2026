"""CLI: print the validated ethnobotanical coverage note and each record summary."""
import json

from src.ethnobotany import coverage_note, load_claims, summarise

payload = load_claims()
print(json.dumps(coverage_note(), indent=2))
for record in payload['records']:
    print(json.dumps(summarise(record), indent=2))
