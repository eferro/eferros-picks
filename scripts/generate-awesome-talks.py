import json

def generate_awesome_talks():
    with open('database/Resources.json', 'r') as file:
        resources = json.load(file)
    
    awesome_talks = [
        resource for resource in resources
        if resource.get("Resource type") == "talk" and resource.get("Rating") == 5
    ]
    
    with open('database/awesome-talks.json', 'w') as file:
        json.dump(awesome_talks, file, indent=4)

generate_awesome_talks()
