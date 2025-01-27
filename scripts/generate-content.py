import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from collections import defaultdict

@dataclass
class Talk:
    id: str
    name: str
    url: str
    duration: int
    topics: List[str]
    speakers: List[str]
    description: Optional[str]


introduction_html = """
<p>These recommended talks represent my personal take on software delivery and product development, shaped by both my real-world experiences and my guiding principles around Agile, XP, Continuous Delivery, and Lean thinking. They aren’t meant to be a comprehensive or neutral collection—rather, they showcase how I’ve seen teams thrive when we embrace flow, high-quality code, and tight feedback loops. If you’d like to learn about the premises that form the backbone of my approach, please check out <a href="https://www.eferro.net/p/my-premises-about-software-development.html">My Premises About Software Development</a>.</p>
<p>Because I firmly believe in going fast by maintaining high quality and always remembering that software is a means to an end, you’ll notice a theme of close collaboration, small safe steps, and continuous learning throughout these talks. These beliefs stem directly from my hands-on experience, and I’ve seen their impact across multiple projects. For more insights into my approach, visit my <a href="https://www.eferro.net">Blog (eferro's random stuff)</a>, where I delve deeper into Lean Software Development, Lean Product Development, XP practices, and the value of reliable, evolving code.</p>
"""
image_html = '<center><img src="images/honey_badger-eferro-no-bg-small.png" alt="eferro logo" /></center>'
librecounter_html = """
<a href="https://librecounter.org/referer/show" target="_blank">
<img src="https://librecounter.org/counter.svg" referrerPolicy="unsafe-url" />
</a>'
"""
footer_html = """
<br>
<br>
<p>
© 2024 Edu Ferro (<b>eferro</b>). All rights reserved. <a href="https://www.eferro.net">Visit my website</a>
</p>
"""

class TalkRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.talks = []
        self.talks_by_speaker = defaultdict(list)
        self.talks_by_topic = defaultdict(list)
        self.speaker_count = defaultdict(int)
        self.topic_count = defaultdict(int)
        self._cache_talks()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _cache_talks(self):
        query = """
        SELECT airtable_id, Name, Url, Duration, Topics_Names, Speakers_Names, Description 
        FROM Resources 
        WHERE Rating=5 AND "Resource type" == 'talk' AND "Language" == 'English'
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                talk = self._row_to_talk(row)
                self.talks.append(talk)
                for speaker in talk.speakers:
                    self.talks_by_speaker[speaker].append(talk)
                    self.speaker_count[speaker] += 1
                for topic in talk.topics:
                    self.talks_by_topic[topic].append(talk)
                    self.topic_count[topic] += 1

    def get_all_talks(self):
        return self.talks

    def get_talks_by_speaker(self):
        return self.talks_by_speaker

    def get_talks_by_topic(self):
        return self.talks_by_topic

    def _row_to_talk(self, row) -> Talk:
        return Talk(
            id=row[0],
            name=row[1],
            url=row[2],
            duration=row[3],
            topics=self._extract_from_list(row[4]),
            speakers=self._extract_from_list(row[5]),
            description=row[6]
        )

    def _extract_from_list(self, data: str) -> List[str]:
        data = data.replace('[', '').replace(']','').replace('"','').strip() if data else ''
        result = [s.strip() for s in  data.split(',')] if data else []
        return result

def generate_html_from_repository_by_topic(repo):
    talks_by_topic = repo.get_talks_by_topic()

    with open('index-by-topic.html', 'w') as file:
        file.write("<html>\n")
        file.write("  <head>\n")
        file.write("    <title>eferro's picks by Topic</title>\n")
        file.write("  </head>\n")
        file.write("  <body>\n")
        file.write("    <h1>Recomended Talks by Topic</h1>\n")

        file.write(image_html)
        file.write(introduction_html)

        file.write("    <h2>Talks by Topic</h2>\n")
        file.write(f"    <ul>\n")
        generate_html_for_topics(file, talks_by_topic, include_speakers=True)
        file.write(f"    </ul>\n")

        file.write(footer_html)
        file.write(librecounter_html)

        file.write("  </body>\n")
        file.write("</html>\n")

def generate_html_from_repository(repo):
    talks_by_speaker = repo.get_talks_by_speaker()

    with open('index.html', 'w') as file:
        file.write("<html>\n")
        file.write("  <head>\n")
        file.write("    <title>eferro's picks</title>\n")
        file.write("  </head>\n")
        file.write("  <body>\n")
        file.write("    <h1>Recomended Talks</h1>\n")

        file.write(image_html)
        file.write(introduction_html)


        file.write("    <h2>Talks by speaker</h2>\n")
        file.write(f"    <ul>\n")
        generate_html_for_top_speakers(file, talks_by_speaker, include_speakers=False)
        file.write(f"    </ul>\n")

        file.write(f"    <br>\n")
        file.write(f"    <br>\n")
        file.write(f"    <h2>Other speakers</h2>\n")
        file.write(f"    <ul>\n")        
        generate_html_for_other_speakers(file, talks_by_speaker, include_speakers=True)
        file.write(f"    </ul>\n")

        file.write(f"    </ul>\n")

        file.write(footer_html)
        file.write(librecounter_html)

        file.write("  </body>\n")
        file.write("</html>\n")


def generate_html_for_top_speakers(file, talks_by_speaker, include_speakers):
    sorted_speakers = sorted(talks_by_speaker.items(), key=lambda item: len(item[1]), reverse=True)
    for speaker, talks in sorted_speakers:
        if len(talks) == 1:
            continue
        generate_html_for_a_speaker(file, speaker, talks, include_speakers)

def generate_html_for_other_speakers(file, talks_by_speaker, include_speakers):
    other_talks = []
    for _, talks in talks_by_speaker.items():
        if len(talks) == 1:
            other_talks.extend(talks)
    for talk in other_talks:
        generate_html_for_a_talk(file, talk, include_speakers=True)

def generate_html_for_a_speaker(file, speaker, talks, include_speakers):
    sanitized_speaker = speaker.replace(' ', '_').replace('.','_').lower()
    file.write(f"    <li><a name=\"{sanitized_speaker}\">{speaker}</a></li>\n")
    file.write(f"      <ul>\n")
    for talk in talks:
        generate_html_for_a_talk(file, talk, include_speakers)
    file.write(f"      </ul>\n")

def generate_html_for_topics(file, talks_by_topic, include_speakers):
    sorted_topics = sorted(talks_by_topic.items(), key=lambda item: len(item[1]), reverse=True)
    for topic, talks in sorted_topics:
        if len(talks) == 1:
            continue
        generate_html_for_a_topic(file, topic, talks, include_speakers)

def generate_html_for_a_topic(file, topic, talks, include_speakers):
    sanitized_topic = topic.replace(' ', '_').replace('.','_').lower()
    file.write(f"    <li><a name=\"{sanitized_topic}\">{topic}</a></li>\n")
    file.write(f"      <ul>\n")
    for talk in talks:
        generate_html_for_a_talk(file, talk, include_speakers)
    file.write(f"      </ul>\n")

def generate_html_for_a_talk(file, talk, include_speakers):
    speakers = generate_speakers_html(talk, include_speakers)
    topics = f"<strong>[{', '.join(talk.topics)}]</strong>"
    duration = f"<strong>[Duration: {talk.duration // 60:02}:{talk.duration % 60:02}]</strong>" if talk.duration else ""
    description = talk.description if hasattr(talk, 'description') else ''
    file.write(f"      <li><a href=\"{talk.url}\">{talk.name}</a> {speakers} {topics} {duration} {description}</li>\n")

def generate_speakers_html(talk, include_speakers):
    if include_speakers and talk.speakers:
        speakers = f"(<strong>{', '.join(talk.speakers)}</strong>)"
    else:
        speakers = ""
    return speakers

def main():
    repo = TalkRepository('database/picks.db')
    generate_html_from_repository(repo)
    generate_html_from_repository_by_topic(repo)

if __name__ == "__main__":
    main()
