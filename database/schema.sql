CREATE TABLE IF NOT EXISTS topics (
 id INTEGER PRIMARY KEY, level TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL,
 UNIQUE(level, kind, name)
);
CREATE TABLE IF NOT EXISTS words (
 id INTEGER PRIMARY KEY, german TEXT NOT NULL, english TEXT NOT NULL, article TEXT,
 pronunciation TEXT, plural TEXT, level TEXT NOT NULL, cefr TEXT, topic_id INTEGER NOT NULL,
 example_de TEXT, example_en TEXT, example_german TEXT, example_english TEXT,
 FOREIGN KEY(topic_id) REFERENCES topics(id)
);
CREATE TABLE IF NOT EXISTS listening_questions (
 id INTEGER PRIMARY KEY, level TEXT NOT NULL, topic_id INTEGER NOT NULL, audio_text TEXT NOT NULL,
 english_translation TEXT NOT NULL, audio_file TEXT, question TEXT NOT NULL,
 option_a TEXT NOT NULL, option_b TEXT NOT NULL, option_c TEXT NOT NULL, option_d TEXT NOT NULL,
 correct_answer TEXT NOT NULL, difficulty TEXT NOT NULL, question_type TEXT NOT NULL,
 FOREIGN KEY(topic_id) REFERENCES topics(id)
);
CREATE TABLE IF NOT EXISTS quiz_results (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, quiz_type TEXT, level TEXT, topic_id INTEGER,
 score INTEGER, total INTEGER, accuracy REAL, duration_seconds INTEGER, created_at TEXT,
 exam_number INTEGER
);
CREATE TABLE IF NOT EXISTS user_answers (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, item_type TEXT, item_id INTEGER,
 selected_answer TEXT, correct INTEGER, answered_at TEXT
);
CREATE TABLE IF NOT EXISTS review_words (
 user_id INTEGER NOT NULL, word_id INTEGER NOT NULL, attempts INTEGER DEFAULT 0,
 correct_count INTEGER DEFAULT 0, updated_at TEXT, PRIMARY KEY(user_id, word_id)
);
CREATE TABLE IF NOT EXISTS review_listening (
 user_id INTEGER NOT NULL, question_id INTEGER NOT NULL, attempts INTEGER DEFAULT 0,
 correct_count INTEGER DEFAULT 0, updated_at TEXT, PRIMARY KEY(user_id, question_id)
);
CREATE TABLE IF NOT EXISTS progress (
 user_id INTEGER NOT NULL, item_type TEXT, item_id INTEGER, correct_count INTEGER DEFAULT 0,
 wrong_count INTEGER DEFAULT 0, last_seen TEXT, PRIMARY KEY(user_id, item_type, item_id)
);
CREATE TABLE IF NOT EXISTS audio_files (id INTEGER PRIMARY KEY, question_id INTEGER UNIQUE, path TEXT, generated_at TEXT);
