# 🇩🇪 BHARATH GERMAN PRACTICE

A vocabulary-focused German A1 and A2 learning website built with Flask, SQLite, Bootstrap 5, and JavaScript.

## What is included

- 20 A1 topics with 50 words per topic
- 20 A2 topics with 50 words per topic
- 2,000 vocabulary records total
- German → English practice as the dominant question type
- English → German questions
- Article recognition questions
- Randomized multiple-choice options
- Topic-based 50-question practice
- Three mixed-topic A1 exams
- Three mixed-topic A2 exams
- Exam feedback hidden until submission
- Wrong-word review
- Search by German word, English meaning, or topic
- Progress tracking and mastery state
- Responsive Bootstrap UI

This application intentionally does **not** include audio, listening exercises, speech recognition, or grammar lessons.

## Deploy to Vercel Free

This repository includes [`vercel.json`](./vercel.json) and [`api/index.py`](./api/index.py) for Vercel's Python serverless runtime.

1. Open [Vercel](https://vercel.com/new).
2. Import `BharathChandra4545/learn-german`.
3. Keep the framework preset as **Other**.
4. Deploy.

The free Vercel filesystem is ephemeral. The committed `database.db` is available to the deployment, but progress writes are not durable across serverless instance replacement. For durable progress, use a hosted database such as PostgreSQL or Turso.

## Windows setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed_database.py
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Deploy to Render

This repository includes [`render.yaml`](./render.yaml) and a `Procfile`. In Render, choose **New + → Blueprint**, connect the repository containing this project, and select `render.yaml`. Render will install dependencies, seed the SQLite database, and start Gunicorn.

For production persistence, attach a Render persistent disk mounted at `/opt/render/project/src` or migrate the SQLite database to a managed database before significant use. Without a persistent disk, SQLite data can be reset when the service is redeployed.

`seed_database.py` is repeatable. It creates the SQLite schema, removes obsolete listening records from earlier versions, creates the 40 vocabulary topics, rebuilds `data/vocabulary.json`, and imports 2,000 words.

## Question distribution

Normal practice and exams use:

- 70% German → English
- 20% English → German
- 10% article recognition

Answer choices are shuffled for every question. Topic practice gives feedback after each answer. Exams hide correctness and explanations until the 50-question exam is complete.

## Mastery

Each correct answer increments the word's progress. A word becomes `LEARNING` after its first correct answer and `MASTERED` after three correct answers. Incorrect answers are placed into the review queue.

## Project structure

`app.py` contains Flask routes and JSON APIs. `seed_database.py` creates content. `database/schema.sql` defines SQLite tables. `templates/` contains the pages and `static/` contains the responsive CSS.
