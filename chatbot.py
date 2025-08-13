import os
from datetime import datetime
from dotenv import load_dotenv
import spacy
from cohere import Client as CohereClient
from spacy.matcher import PhraseMatcher

# Load environment variables
load_dotenv()
api_key = os.getenv("CO_API_KEY")
cohere_client = CohereClient(api_key)

# Load SpaCy
nlp = spacy.load("en_core_web_sm")

YOUTUBE_VIDEOS = {
    "how to play": {
        "keywords": ["how to play", "play takraw", "rules", "learn takraw"],
        "reply": "Here's a great video on how to play Sepak Takraw:",
        "iframe": """
            <div class="video-container">
              <iframe src="https://www.youtube.com/embed/N-ZInLq317c" 
                      title="How to Play Sepak Takraw" 
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                      allowfullscreen></iframe>
            </div>
        """
    },
    "history": {
        "keywords": ["history", "origin", "where did takraw start","history of Takraw"],
        "reply": "Here's a video on the history of Sepak Takraw:",
        "iframe": """
            <div class="video-container">
              <iframe src="https://www.youtube.com/embed/In2eUbpb8kg" 
                      title="History of Sepak Takraw"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                      allowfullscreen></iframe>
            </div>
        """
    },
    "classic": {
        "keywords": ["classic", "sea games", "old takraw", "vintage", "highlight"],
        "reply": "Check out this classic Sepak Takraw match footage:",
        "iframe": """
            <div class="video-container">
              <iframe src="https://www.youtube.com/embed/bQ1XvE1sp0Q" 
                      title="Classic Sepak Takraw Footage"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                      allowfullscreen></iframe>
            </div>
        """
    },
    "recent match": {
        "keywords": ["latest match", "recent game", "malaysia vs thailand", "finals"],
        "reply": "Watch this recent high-stakes match between Malaysia and Thailand:",
        "iframe": """
            <div class="video-container">
              <iframe src="https://www.youtube.com/embed/pewgkEy1fT0" 
                      title="Thailand vs Malaysia Final"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                      allowfullscreen></iframe>
            </div>
        """
    },
    "ankle recovery": {
        "keywords": ["ankle", "sprain", "treatment"],
        "reply": "Here’s a helpful video on treating ankle sprains at home:",
        "iframe": """
            <div class="video-container">
              <iframe width="100%" height="315" src="https://www.youtube.com/embed/_6hjIWhB8Yc" 
                    title="[RECOVER FASTER!] How To Treat Your Ankle Sprain At Home!" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
            </div>
        """
    }
}

# Keywords
SEPAK_TAKRAW_KEYWORDS = [
    "sepak takraw", "takraw", "kick volleyball",
    "history", "origin", "start", "invention", "who invented","what is the history",
    "how to play", "rules of the game", "game rules", "how to play takraw",
    "where is it from", "how did it start", "when did it begin",
    "rules", "regulations", "how to play", "gameplay", "how is it played",
    "basic rules", "serve", "kick", "spike", "net", "court", "ball", "rotation",
    "positions", "scoring", "score", "sets", "rounds", "duration", "referee",
    "court size", "gear", "equipment", "uniform",
    "roll spike", "header", "toe kick", "sunback spike", "horse kick", "block", "service",
    "tekong", "feeder", "striker", "team", "player",
    "match", "tournament", "SEA Games", "Asian Games", "Olympics", "competition",
    "compare", "difference", "vs", "volleyball", "football", "soccer",
    "famous players", "countries", "popular in", "played in", "Malaysia", "Thailand", "Indonesia"
    "injury", "treatment", "recovery", "rehab", "exercise",
    "is it true", "is it real", "is it a myth", "is it fake", "is it true that",
    "is it a sport", "is it dangerous", "is it easy to learn", "is it popular",
    "how to improve", "how to get better", "training", "practice", "skills",
    "techniques", "strategies", "tips", "advice",
    "famous matches", "highlights", "best moments", "top plays", "greatest games",
    "motivation", "inspiration", "quotes", "stories", "legends"
    "time", "when", "day", "date", "today", "now", "current"
    "name", "who", "what is your name", "who are you", "identity", "my name is", "call me",
]

# PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
sepak_phrases = [nlp(text) for text in SEPAK_TAKRAW_KEYWORDS]
matcher.add("SEPAK_TAKRAW", sepak_phrases)

# In-memory memory store
user_memory = {}
user_insistence = {}

# Static images
image_keywords = {
    "serve": {"url": "/static/images/serve.jpg", "caption": "Here's how a Sepak Takraw serve looks like."},
    "team": {"url": "/static/images/team.jpg", "caption": "A typical Sepak Takraw team formation."},
    "spike": {"url": "/static/images/spike.jpg", "caption": "A powerful Sepak Takraw spike in action!"},
    "court": {"url": "/static/images/court.jpg", "caption": "This is what a Sepak Takraw court looks like."},
    "ball": {"url": "/static/images/ball.jpg", "caption": "The official Sepak Takraw ball."}
}

DETAIL_KEYWORDS = [
    "explain", "why", "how does", "what is the reason", "in detail",
    "tell me more", "elaborate", "break it down", "deep dive"
]

def wants_detail(user_input: str) -> bool:
    lower_input = user_input.lower()
    return any(keyword in lower_input for keyword in DETAIL_KEYWORDS)

def shorten_response(text):
    sentences = text.split('. ')
    short = '. '.join(sentences[:2])
    return short if short.endswith('.') else short + '.'

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def is_about_sepak_takraw(text):
    doc = nlp(text)
    matches = matcher(doc)
    if matches:
        return True
    simple_check = any(keyword in text.lower() for keyword in ["takraw", "sepak", "kick volleyball"])
    return simple_check

def classify_sepak_topic(text):
    doc = nlp(text.lower())
    topic_keywords = {
        "rules": ["rule", "regulation", "play", "how", "gameplay"],
        "history": ["history", "origin", "start", "begin", "invent", "when", "who"],
        "equipment": ["ball", "net", "gear", "equipment", "court", "uniform"],
        "techniques": ["spike", "kick", "block", "header", "toe", "serve"],
        "roles": ["tekong", "feeder", "striker", "position", "player", "team"],
        "competitions": ["match", "tournament", "SEA Games", "Olympics"],
        "compare": ["compare", "difference", "vs", "volleyball", "football", "soccer"],
        "famous players": ["famous", "players", "countries", "popular", "played in"]
    }
    for token in doc:
        for category, keywords in topic_keywords.items():
            if token.lemma_ in keywords:
                return category
    return None

def get_image_path(user_input):
    user_input = user_input.lower()
    for keyword, info in image_keywords.items():
        if keyword in user_input:
            return info
    if any(word in user_input for word in ["image", "photo", "picture", "show me"]):
        return {"url": "/static/images/general.jpg", "caption": "Here’s an image related to Sepak Takraw."}
    return None

         
def get_response(user_input, user_id="default_user"):
    if not user_input or not user_input.strip():
        return {"text": "Please enter a message.", "suggestions": []}

    user_input_clean = user_input.strip().lower()
    exit_keywords = ["bye", "exit", "goodbye", "see you", "quit", "end chat"]
    if any(kw in user_input_clean for kw in exit_keywords):
        return {
            "text": "Before you go, would you mind filling out a quick survey to help us improve BolaBot?",
            "suggestions": ["Yes, take me to the survey", "No thanks"],
            "survey_link": "https://your-survey-link.com"
    }
    if user_input_clean in ["bye", "exit", "goodbye"]:
        return {
            "text": "Before you go, would you mind taking a quick survey to help improve BolaBot?",
            "suggestions": [
                {"text": "Yes, take me to the survey", "link": "https://forms.gle/your-survey-link"},
                {"text": "No thanks"}
        ]
    }
    if user_input_clean == "yes, take me to the survey":
        return {
            "text": "Great! Please click the link below to fill out the survey:<br><a href='https://docs.google.com/forms/d/e/1FAIpQLSdBgUQxuZi6AKn4md1vvYQGZf33mGzP85eJpAuvxa29ImiPGA/viewform?usp=sharing&ouid=116108412332228221224' target='_blank'>Take the Survey</a>",
            "suggestions": ["Start over", "What can you do?"]
    }
    if user_input_clean == "no thanks":
        return {
        "text": "No worries at all! Thanks for chatting with me today.",
        "suggestions": ["Start over", "What can you do?"]
    }


    # Initialize memory
    if user_id not in user_memory:
        user_memory[user_id] = {"name": None, "history": []}
    if user_id not in user_insistence:
        user_insistence[user_id] = False
    # Greetings
    if user_input_clean in ["hi", "hello", "hey"]:
        return {
            "text": "Hello! I’m BolaBot, your guide to Sepak Takraw. Ask me anything about the sport.",
            "suggestions": ["How to play Sepak Takraw?", "What is the history?", "Show me a Sepak Takraw ball."]
        }
    time_keywords = ["time", "current time", "date", "day", "today", "what time", "what's the time", "now"]
    if any(kw in user_input_clean for kw in time_keywords):
        now = datetime.now().strftime("%A, %d %B %Y %I:%M %p")
        return {
            "text": f"The current date and time is {now}.",
            "suggestions": ["What is the history of Takraw?", "Show me a video", "Rules of the game"]
        }
    # Name detection
    if user_memory[user_id]["name"] is None:
        name = extract_name(user_input)
        if name:
            user_memory[user_id]["name"] = name
            return f"Nice to meet you, {name}! What would you like to know about Sepak Takraw?"
        
    # Bot identity
    if "your name" in user_input_clean or "who are you" in user_input_clean:
        return {
            "text": "My name is BolaBot. I'm here to help you explore the sport of Sepak Takraw.",
            "suggestions": ["How do you help?", "Tell me a fun fact", "What can you do?"]
        }

    # Image check
    image_info = get_image_path(user_input_clean)
    if image_info:
        return {
            "text": image_info["caption"],
            "image": image_info["url"],
            "suggestions": ["Show a spike image", "How do players serve?", "Rules of the game"]
        }

    # Filter non-Sepak Takraw topics
    if not is_about_sepak_takraw(user_input_clean):
        if not user_insistence[user_id]:
            user_insistence[user_id] = True
            return {
                "text": "I'm focused only on Sepak Takraw. If you still want an answer, please ask again.",
                "suggestions": ["Tell me about Sepak Takraw", "What is it?", "Show a video"]
            }

    # YouTube video matches
    for topic, data in YOUTUBE_VIDEOS.items():
        if any(keyword in user_input_clean for keyword in data["keywords"]):
            return {
                "text": data["reply"],
                "iframe": data["iframe"],
                "suggestions": ["Show more videos", "Explain the technique", "Show an image"]
            }

    # If "video" is mentioned generically
    if "video" in user_input_clean or "show me a video" in user_input_clean:
        return {
            "text": "Would you like a tutorial, match highlight, or history video?",
            "suggestions": ["How to play video", "History of Takraw", "Malaysia vs Thailand"]
        }

    # Use Cohere AI to generate response
    try:
        system_prompt = (
            f"You are BolaBot, an expert on Sepak Takraw. "
            f"Answer questions clearly and helpfully about Sepak Takraw."
        )

        prompt = (
            f"Explain in detail: {user_input}" if wants_detail(user_input)
            else f"Give a brief answer to: {user_input}"
        )

        response = cohere_client.chat(
            message=f"{system_prompt}\n\n{prompt}",
            chat_history=user_memory[user_id]["history"],
            model="command-r",
            temperature=0.5
        )


        user_memory[user_id]["history"].append({"role": "USER", "message": user_input})
        user_memory[user_id]["history"].append({"role": "CHATBOT", "message": response.text})

        suggestions = ["Show a video", "Show an image", "Tell me more", "Who invented Sepak Takraw?"]
        return {
            "text": response.text if wants_detail(user_input) else shorten_response(response.text),
            "suggestions": suggestions
        }

    except Exception as e:
        print(f"[Error] {e}")
        return {
            "text": "Sorry, something went wrong while generating my response.",
            "suggestions": ["Try again", "Ask another question"]
        }

