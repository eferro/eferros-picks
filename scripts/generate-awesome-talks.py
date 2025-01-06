import json
from datetime import datetime
from collections import defaultdict

def generate_awesome_talks():
    with open('database/Resources.json', 'r') as file:
        resources = json.load(file)
    
    awesome_talks = [
        resource for resource in resources
        if resource.get("Resource type") == "talk" and resource.get("Rating") == 5 and resource.get("Language") == "English"
    ]

    awesome_talks.sort(key=lambda x: datetime.strptime(x.get("Created"), "%Y-%m-%dT%H:%M:%S.%fZ"))

    with open('database/awesome-talks.json', 'w') as file:
        json.dump(awesome_talks, file, indent=4)

    stats = {
        "total_talks": len(awesome_talks),
        "talks_per_topic": defaultdict(int),
        "talks_per_speaker": defaultdict(int)
    }

    for talk in awesome_talks:
        for topic in talk.get("Topics_Names", []):
            stats["talks_per_topic"][topic] += 1
        for speaker in talk.get("Speakers_Names", []):
            stats["talks_per_speaker"][speaker] += 1

    stats["talks_per_topic"] = dict(sorted(stats["talks_per_topic"].items(), key=lambda item: item[1], reverse=True))
    stats["talks_per_speaker"] = dict(sorted(stats["talks_per_speaker"].items(), key=lambda item: item[1], reverse=True))

    with open('database/awesome-talks-stats.json', 'w') as file:
        json.dump(stats, file, indent=4)

generate_awesome_talks()
