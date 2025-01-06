import json



def generate_index():
    with open('database/awesome-talks-by-speaker.json', 'r') as file:
        talks_by_speaker = json.load(file)

    with open('index.html', 'w') as file:
        file.write("<html>\n")
        file.write("  <head>\n")
        file.write("    <title>eferro's picks</title>\n")
        file.write("  </head>\n")
        file.write("  <body>\n")
        file.write("    <h1>Recomended Talks</h1>\n")
        
        generate_html_for_top_speakers(file, talks_by_speaker, include_speakers=False)
        generate_html_for_a_speaker(file, "other speakers", talks_by_speaker["others"], include_speakers=True)

        file.write(f"    </ul>\n")
        file.write("  </body>\n")
        file.write("</html>\n")

def generate_html_for_top_speakers(file, talks_by_speaker, include_speakers):
    file.write(f"    <ul>\n")
    for speaker, talks in talks_by_speaker.items():
        if speaker == "others":
            continue
        generate_html_for_a_speaker(file, speaker, talks, include_speakers)

def generate_html_for_a_speaker(file, speaker, talks, include_speakers):
    file.write(f"    <li>{speaker}</li>\n")
    file.write(f"      <ul>\n")
    for talk in talks:
        generate_html_for_a_talk(file, talk, include_speakers)
    file.write(f"      </ul>\n")

def generate_html_for_a_talk(file, talk, include_speakers):
    speakers = generate_speakers_html(talk, include_speakers)
    topics = f"<strong>[{', '.join(talk['Topics_Names'])}]</strong>"
    duration = f"<strong>[Duration: {talk['Duration'] // 60:02}:{talk['Duration'] % 60:02}]</strong>" if 'Duration' in talk else ""
    description = talk.get('Description', '')
    file.write(f"      <li><a href=\"{talk['Url']}\">{talk['Name']}</a> {speakers} {topics} {duration} {description}</li>\n")

def generate_speakers_html(talk, include_speakers):
    if include_speakers and 'Speakers_Names' in talk and talk['Speakers_Names']:
        speakers = f"(<strong>{', '.join(talk['Speakers_Names'])}</strong>)"
    else:
        speakers = ""
    return speakers

generate_index()
