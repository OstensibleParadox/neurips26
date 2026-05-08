"""Generate 3000 tool-selection episodes for §7.2 proxy certificate experiment.

Each episode is a user query requiring one of 5 tools:
  search, calculator, email, calendar, weather

Labels are deterministic based on keyword matching (no LLM needed for labeling).
The agent's task is to select the correct tool.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

TEMPLATES = {
    "search": [
        "what is {topic}",
        "find information about {topic}",
        "search for {topic}",
        "look up {topic} online",
        "tell me about {topic}",
        "who is {topic}",
        "when was {topic} invented",
        "where is {topic} located",
        "how does {topic} work",
        "why is {topic} important",
        "explain {topic} to me",
        "give me a summary of {topic}",
        "what are the main causes of {topic}",
        "history of {topic}",
        "definition of {topic}",
        "{topic} explained simply",
        "compare {topic} and {topic2}",
        "difference between {topic} and {topic2}",
        "best {topic} in the world",
        "top 10 {topic}",
        "how to {topic}",
        "what year did {topic} happen",
        "what is the population of {topic}",
        "capital of {topic}",
        "currency of {topic}",
        "what does {topic} mean",
        "translate {topic} to English",
        "{topic} latest news",
        "reviews of {topic}",
        "how much does {topic} cost",
    ],
    "calculator": [
        "calculate {expr}",
        "what is {expr}",
        "compute {expr}",
        "solve {expr}",
        "evaluate {expr}",
        "{expr} = ?",
        "what is {expr} equal to",
        "add {a} and {b}",
        "multiply {a} by {b}",
        "divide {a} by {b}",
        "{a} plus {b}",
        "{a} minus {b}",
        "{a} times {b}",
        "{a} divided by {b}",
        "square root of {a}",
        "{a} to the power of {b}",
        "what is {a}% of {b}",
        "average of {a_list}",
        "sum of {a_list}",
        "convert {a} {unit1} to {unit2}",
        "if a product costs ${a} and is {b}% off, what is the final price",
        "what is the area of a rectangle with sides {a} and {b}",
        "how many {unit1} in {a} {unit2}",
        "what is {a} in binary",
        "what is the factorial of {a}",
        "find the hypotenuse of a triangle with legs {a} and {b}",
        "{a} kg to pounds",
        "what is the volume of a cube with side {a}",
        "compound interest on ${a} at {b}% for {c} years",
        "tip amount for a ${a} bill at {b}%",
    ],
    "email": [
        "send an email to {recipient} about {subject}",
        "email {recipient} regarding {subject}",
        "compose a message to {recipient}",
        "write an email to the {recipient} team",
        "draft an email about {subject}",
        "send a follow-up email to {recipient}",
        "reply to the email from {recipient}",
        "forward the {subject} email to {recipient}",
        "send meeting notes to {recipient}",
        "email the report to {recipient}",
        "notify {recipient} about {subject} via email",
        "send the invoice to {recipient}",
        "email my boss about {subject}",
        "send a reminder email to {recipient}",
        "broadcast an announcement to the team about {subject}",
    ],
    "calendar": [
        "schedule a meeting with {person} on {day}",
        "add {event} to my calendar for {day}",
        "when is my next meeting with {person}",
        "reschedule the {event} to {day}",
        "cancel the meeting on {day}",
        "what is on my calendar for {day}",
        "create a recurring event: {event} every {day}",
        "find a free slot for a meeting with {person}",
        "schedule a {duration}-minute call with {person}",
        "add {event} to my schedule",
        "check if I'm free on {day} afternoon",
        "block time for {event} on {day}",
        "set a reminder for {event} at {time}",
        "move my {day} appointments to {day2}",
        "schedule a team standup every morning",
    ],
    "weather": [
        "what is the weather in {city} today",
        "weather forecast for {city}",
        "will it rain in {city} tomorrow",
        "temperature in {city} right now",
        "how hot is it in {city}",
        "is it sunny in {city} this weekend",
        "what is the humidity in {city}",
        "will it snow in {city} next week",
        "what should I wear in {city} today based on weather",
        "UV index in {city}",
        "wind speed in {city}",
        "is there a storm warning for {city}",
        "best time to visit {city} based on weather",
        "compare weather: {city} vs {city2}",
        "14-day forecast for {city}",
    ],
}

TOPICS = [
    "quantum computing", "climate change", "machine learning", "blockchain",
    "artificial intelligence", "cryptocurrency", "renewable energy", "neuroscience",
    "ancient Rome", "World War II", "the French Revolution", "Shakespeare",
    "DNA", "black holes", "the stock market", "vegan diet", "meditation",
    "photography", "jazz music", "impressionist art",
]

CITIES = [
    "Tokyo", "London", "New York", "Paris", "Sydney", "Berlin", "Mumbai",
    "Toronto", "Seoul", "Dubai", "Singapore", "Moscow", "Rio de Janeiro",
    "Cape Town", "Bangkok", "Istanbul", "Mexico City", "Lagos", "Chicago",
    "San Francisco", "Beijing", "Shanghai", "Osaka", "Amsterdam", "Barcelona",
]

RECIPIENTS = ["john", "sarah", "the marketing team", "professor chen", "dr. patel",
              "alex", "the client", "HR department", "my manager", "the board"]

SUBJECTS = ["project update", "budget approval", "Q4 report", "hiring decision",
            "contract renewal", "quarterly review", "travel itinerary",
            "proposal draft", "invoice #452", "meeting minutes"]

EVENTS = ["dentist appointment", "team standup", "project review", "lunch with client",
          "conference call", "design sprint", "product demo", "birthday party"]

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

UNITS = [("km", "miles"), ("kg", "pounds"), ("celsius", "fahrenheit"),
         ("meters", "feet"), ("liters", "gallons")]


def generate_expr() -> str:
    a = random.randint(2, 999)
    b = random.randint(2, 99)
    ops = ["+", "-", "*", "/"]
    op = random.choice(ops)
    return f"{a} {op} {b}"


def generate_email_prompt() -> str:
    t = random.choice(TEMPLATES["email"])
    recipient = random.choice(RECIPIENTS)
    subject = random.choice(SUBJECTS)
    return t.format(recipient=recipient, subject=subject)


def generate_search_prompt() -> str:
    t = random.choice(TEMPLATES["search"])
    topic = random.choice(TOPICS)
    topic2 = random.choice(TOPICS)
    return t.format(topic=topic, topic2=topic2)


def generate_calculator_prompt() -> str:
    t = random.choice(TEMPLATES["calculator"])
    a = random.randint(2, 999)
    b = random.randint(2, 99)
    c = random.randint(2, 50)
    unit1, unit2 = random.choice(UNITS)
    a_list = ", ".join(str(random.randint(10, 200)) for _ in range(random.randint(3, 6)))
    return t.format(expr=generate_expr(), a=a, b=b, c=c,
                    unit1=unit1, unit2=unit2, a_list=a_list)


def generate_calendar_prompt() -> str:
    t = random.choice(TEMPLATES["calendar"])
    person = random.choice(RECIPIENTS)
    day = random.choice(DAYS)
    day2 = random.choice(DAYS)
    event = random.choice(EVENTS)
    duration = random.choice([15, 30, 45, 60])
    time = f"{random.randint(9,17)}:{random.choice(['00','30'])}"
    return t.format(person=person, day=day, day2=day2, event=event,
                    duration=duration, time=time)


def generate_weather_prompt() -> str:
    t = random.choice(TEMPLATES["weather"])
    city = random.choice(CITIES)
    city2 = random.choice(CITIES)
    return t.format(city=city, city2=city2)


GENERATORS = {
    "search": generate_search_prompt,
    "calculator": generate_calculator_prompt,
    "email": generate_email_prompt,
    "calendar": generate_calendar_prompt,
    "weather": generate_weather_prompt,
}


def main():
    out_dir = Path("/Users/ostensible_paradox/Documents/neurips26-anon/data/tool_selection")
    out_dir.mkdir(parents=True, exist_ok=True)

    random.seed(42)
    n_per_class = 600  # 5 classes × 600 = 3000 total

    for tool, gen_fn in GENERATORS.items():
        for i in range(n_per_class):
            prompt = gen_fn()
            episode_id = f"{tool}_{i:04d}"
            # Format: prompt + label marker for downstream processing
            content = f"Select the best tool from: search, calculator, email, calendar, weather.\nUser query: {prompt}\n---\nTOOL: {tool}\n"
            with open(out_dir / f"{episode_id}.txt", "w") as f:
                f.write(content)

        print(f"  {tool}: {n_per_class} episodes")

    print(f"Total: {n_per_class * 5} episodes in {out_dir}")


if __name__ == "__main__":
    main()
