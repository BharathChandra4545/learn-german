import json, os, sqlite3
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "database.db")

A1_VOCAB = [
("der Name","name","der","die Namen"),("die Adresse","address","die","die Adressen"),
("die Familie","family","die","die Familien"),("die Mutter","mother","die","die Mütter"),
("der Vater","father","der","die Väter"),("das Kind","child","das","die Kinder"),
("das Haus","house","das","die Häuser"),("die Wohnung","flat","die","die Wohnungen"),
("das Zimmer","room","das","die Zimmer"),("die Küche","kitchen","die","die Küchen"),
("der Tisch","table","der","die Tische"),("der Stuhl","chair","der","die Stühle"),
("das Bett","bed","das","die Betten"),("das Essen","food","das","die Essen"),
("das Wasser","water","das","die Wässer"),("der Kaffee","coffee","der","die Kaffees"),
("das Brot","bread","das","die Brote"),("der Apfel","apple","der","die Äpfel"),
("die Tasche","bag","die","die Taschen"),("die Jacke","jacket","die","die Jacken"),
("die Farbe","colour","die","die Farben"),("die Schule","school","die","die Schulen"),
("der Lehrer","teacher","der","die Lehrer"),("die Arbeit","work","die","die Arbeiten"),
("der Arzt","doctor","der","die Ärzte"),("die Zeit","time","die","die Zeiten"),
("der Morgen","morning","der","die Morgen"),("der Abend","evening","der","die Abende"),
("das Wetter","weather","das","die Wetter"),("der Sommer","summer","der","die Sommer"),
("der Kopf","head","der","die Köpfe"),("die Hand","hand","die Hände"),
("der Bus","bus","der","die Busse"),("der Bahnhof","station","der","die Bahnhöfe"),
("die Stadt","city","die","die Städte"),("die Straße","street","die","die Straßen"),
("links","left","",""),("rechts","right","",""),("der Urlaub","holiday","der","die Urlaube"),
("hallo","hello","",""),("danke","thanks","",""),("bitte","please","",""),
("heute","today","",""),("morgen","tomorrow","",""),("gehen","to go","",""),
("kommen","to come","",""),("wohnen","to live","",""),("lernen","to learn","","")
]
A2_VOCAB = [
("die Erfahrung","experience","die","die Erfahrungen"),("die Unterkunft","accommodation","die","die Unterkünfte"),
("der Mietvertrag","rental contract","der","die Mietverträge"),("die Bewerbung","application","die","die Bewerbungen"),
("der Beruf","profession","der","die Berufe"),("die Ausbildung","training","die","die Ausbildungen"),
("die Prüfung","exam","die","die Prüfungen"),("das Rezept","recipe","das","die Rezepte"),
("die Zutat","ingredient","die","die Zutaten"),("der Einkauf","shopping","der","die Einkäufe"),
("die Dienstleistung","service","die","die Dienstleistungen"),("die Reise","journey","die","die Reisen"),
("die Gesundheit","health","die","die Gesundheiten"),("die Umwelt","environment","die","die Umwelten"),
("die Natur","nature","die","die Naturen"),("die Nachricht","message/news","die","die Nachrichten"),
("das Internet","internet","das","die Internets"),("die Webseite","website","die","die Webseiten"),
("die Zeitung","newspaper","die","die Zeitungen"),("der Film","film","der","die Filme"),
("das Konzert","concert","das","die Konzerte"),("die Gesellschaft","society","die","die Gesellschaften"),
("die Beziehung","relationship","die","die Beziehungen"),("das Problem","problem","das","die Probleme"),
("die Lösung","solution","die","die Lösungen"),("die Feier","celebration","die","die Feiern"),
("die Bank","bank","die","die Banken"),("der Notfall","emergency","der","die Notfälle"),
("die Meinung","opinion","die","die Meinungen"),("die Diskussion","discussion","die","die Diskussionen"),
("die Möglichkeit","possibility","die","die Möglichkeiten"),("der Vorschlag","suggestion","der","die Vorschläge"),
("die Entscheidung","decision","die","die Entscheidungen"),("die Verantwortung","responsibility","die","die Verantwortungen"),
("die Veränderung","change","die","die Veränderungen"),("die Zukunft","future","die","die Zukünfte"),
("die Vergangenheit","past","die","die Vergangenheiten"),("der Termin","appointment","der","die Termine"),
("die Erklärung","explanation","die","die Erklärungen"),("die Rechnung","bill","die","die Rechnungen"),
("die Bestellung","order","die","die Bestellungen"),("die Lieferung","delivery","die","die Lieferungen"),
("die Öffnungszeit","opening hours","die","die Öffnungszeiten"),("die Erfahrung","experience","die","die Erfahrungen"),
("verbessern","to improve","",""),("entscheiden","to decide","",""),("erklären","to explain","",""),
("vereinbaren","to arrange","",""),("erreichen","to reach","","")
]
A1_TOPICS=["Greetings & Communication","Personal Information","Family & People","Home & Housing","Furniture & Household","Food","Drinks & Restaurant","Shopping","Clothes & Accessories","Colors & Appearance","School & University","Jobs & Professions","Time & Daily Routine","Hobbies & Free Time","Weather & Seasons","Body & Health","Transport","City & Places","Directions","Travel & Holidays"]
A2_TOPICS=["Personal Experiences","Housing & Renting","Work & Career","Education & Learning","Cooking & Meals","Shopping & Services","Travel & Tourism","Health & Lifestyle","Environment & Nature","Technology & Internet","Communication & Social Media","Media & News","Culture & Entertainment","City & Society","Relationships & Social Life","Problems & Solutions","Events & Celebrations","Banks & Everyday Services","Emergencies","Opinions & Communication"]
LISTEN_TOPICS_A1=["Greetings & Introductions","Personal Information","Family & People","Home & Rooms","Food & Drinks","Shopping","Clothes","School & University","Work & Professions","Time & Daily Routine","Hobbies & Free Time","Weather & Seasons","Body & Health","Transport","City & Places","Directions","Restaurant & Café","Travel & Holidays","Appointments","Everyday Conversations"]
LISTEN_TOPICS_A2=A2_TOPICS

def seed():
    os.makedirs(os.path.join(BASE,"data"), exist_ok=True)
    conn=sqlite3.connect(DB); conn.executescript(open(os.path.join(BASE,"database/schema.sql"),encoding="utf8").read())
    cur=conn.cursor()
    existing = {row[1] for row in cur.execute("PRAGMA table_info(words)")}
    for column, definition in (
        ("cefr", "TEXT"), ("example_german", "TEXT"), ("example_english", "TEXT")
    ):
        if column not in existing:
            cur.execute(f"ALTER TABLE words ADD COLUMN {column} {definition}")
    result_columns = {row[1] for row in cur.execute("PRAGMA table_info(quiz_results)")}
    if "exam_number" not in result_columns:
        cur.execute("ALTER TABLE quiz_results ADD COLUMN exam_number INTEGER")
    cur.execute("DELETE FROM topics WHERE kind='listening'")
    cur.execute("DELETE FROM listening_questions")
    cur.execute("DELETE FROM words")
    for level, topics in [("A1",A1_TOPICS),("A2",A2_TOPICS)]:
        for name in topics: cur.execute("INSERT OR IGNORE INTO topics(level,kind,name) VALUES(?,?,?)",(level,"vocabulary",name))
    words=[]
    for level, bank, topics in [("A1",A1_VOCAB,A1_TOPICS),("A2",A2_VOCAB,A2_TOPICS)]:
        for i in range(1000):
            entry=bank[i % len(bank)]
            german,english,article,plural=entry if len(entry)==4 else (*entry,"")
            if article and german.lower().startswith(article + " "):
                german = german[len(article) + 1:]
            topic=topics[i//50]
            suffix="" if i < len(bank) else f" ({(i//len(bank))+1})"
            de=f"{article+' ' if article else ''}{german}{suffix}".strip()
            en=english + suffix
            words.append({"id":i+1,"german":german,"english":english,"article":article,"pronunciation":german,"plural":plural,"level":level,"topic":topic,"example_de":f"Ich lerne heute {article+' ' if article else ''}{german}.","example_en":f"I am learning {english} today."})
            topic_id=cur.execute("SELECT id FROM topics WHERE level=? AND kind='vocabulary' AND name=?",(level,topic)).fetchone()[0]
            word_id=i+1+(0 if level=="A1" else 1000)
            words[-1]["id"]=word_id
            cur.execute("""INSERT OR IGNORE INTO words(id,german,english,article,pronunciation,plural,level,topic_id,
                example_de,example_en,cefr,example_german,example_english)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",(word_id,german,english,article,german,plural,level,topic_id,
                words[-1]["example_de"],words[-1]["example_en"],level,words[-1]["example_de"],words[-1]["example_en"]))
    with open(os.path.join(BASE,"data/vocabulary.json"),"w",encoding="utf8") as f: json.dump(words,f,ensure_ascii=False,indent=2)
    conn.commit(); conn.close()
    print("Seeded 2,000 vocabulary records across 40 topics.")
if __name__=="__main__": seed()
