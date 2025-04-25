# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:5173"] for Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Yoruba Bible data
with open("yoruba_bible_named.json", "r", encoding="utf-8") as f:
    bible = json.load(f)

# --- Helper ---
def parse_ref(ref: str):
    try:
        book, chapter_verse = ref.strip().split(" ")
        chapter, verse = chapter_verse.split(":")
        return book, int(chapter), int(verse)
    except:
        return None

# --- API Routes ---
@app.get("/passage")
def get_passage(start: str = Query(...), end: str = Query(...)):
    start_ref = parse_ref(start)
    end_ref = parse_ref(end)
    results = []
    in_range = False

    for section in ["Old", "New"]:
        for book, chapters in bible.get(section, {}).items():
            for chapter_str in sorted(chapters, key=int):
                chapter = int(chapter_str)
                for verse_data in chapters[chapter_str]:
                    verse_num = verse_data["verse"]
                    current_ref = (book, chapter, verse_num)

                    if current_ref == start_ref:
                        in_range = True
                    if in_range:
                        results.append({
                            "book": book,
                            "chapter": chapter,
                            "verse": verse_num,
                            "text": verse_data["text"]
                        })
                    if current_ref == end_ref:
                        return {"passage": results}
    return {"passage": results}

@app.get("/search")
def word_search(query: str = Query(...)):
    results = []
    for section in ["Old", "New"]:
        for book, chapters in bible.get(section, {}).items():
            for chapter_str, verses in chapters.items():
                for verse_data in verses:
                    if query.lower() in verse_data["text"].lower():
                        results.append({
                            "book": book,
                            "chapter": int(chapter_str),
                            "verse": verse_data["verse"],
                            "text": verse_data["text"]
                        })
    return {"results": results}
