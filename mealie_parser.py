import os
import json
import re
import unicodedata

from datetime import datetime, UTC
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_CATEGORIES = [
    "Entrée",
    "Plat principal",
    "Dessert",
    "Apéritif",
    "Petit-déjeuner",
    "Goûter",
    "Soupe & potage",
    "Salade",
    "Sauce & condiment",
    "Boisson",
]

ALLOWED_TAGS = [
    "Rapide",
    "Facile",
    "Végétarien",
    "Vegan",
    "Sans gluten",
    "Healthy",
    "Économique",
    "Anti-gaspillage",
    "Batch cooking",
    "Fait maison",
]

def now_iso_z():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")

def to_iso8601_duration_fallback(text: str) -> str:
    """
    Fallback léger si le modèle n'a rien donné.
    Convertit des durées simples FR: "10 min", "1 h 15", "2 heures", etc -> "PT.."
    (Le modèle est censé fournir directement du ISO 8601, mais ça sécurise.)
    """
    if not text:
        return "PT0M"
    t = text.lower().strip()
    # minutes
    m = re.search(r"(\d+)\s*(min|minute|minutes)\b", t)
    h = re.search(r"(\d+)\s*(h|heure|heures)\b", t)
    hours = int(h.group(1)) if h else 0
    mins = int(m.group(1)) if m else 0
    if hours == 0 and mins == 0:
        # parfois "1h15"
        m2 = re.search(r"(\d+)\s*h\s*(\d+)", t)
        if m2:
            hours = int(m2.group(1))
            mins = int(m2.group(2))
    return f"PT{hours}H{mins}M" if hours or mins else "PT0M"

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    return text.strip("-").lower()

RECIPE_JSON_SCHEMA = {
  "name": "schema_org_recipe",
  "schema": {
    "type": "object",
    "additionalProperties": False,
    "required": ["@context", "@type", "name", "description", "recipeIngredient", "recipeInstructions"],
    "properties": {
      "@context": {"type": "string", "enum": ["https://schema.org"]},
      "@type": {"type": "string", "enum": ["Recipe"]},

      "name": {"type": "string"},
      "description": {"type": "string"},
      "image": {
        "anyOf": [
          {"type": "string"},
          {"type": "array", "items": {"type": "string"}}
        ]
      },
      "url": {"type": "string"},

      "recipeYield": {"type": "string"},
      "recipeCategory": {
        "anyOf": [
          {"type": "string"},
          {"type": "array", "items": {"type": "string"}}
        ]
      },
      "keywords": {"type": "string"},

      # ISO 8601 (eg: PT10M, PT1H15M)
      "prepTime": {"type": "string"},
      "cookTime": {"type": "string"},
      "totalTime": {"type": "string"},
      "performTime": {"type": "string"},

      "recipeIngredient": {"type": "array", "items": {"type": "string"}},

      "recipeInstructions": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": False,
          "required": ["@type", "text"],
          "properties": {
            "@type": {"type": "string", "enum": ["HowToStep"]},
            "name": {"type": "string"},
            "text": {"type": "string"}
          }
        }
      },

      "nutrition": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
          "@type": {"type": "string", "enum": ["NutritionInformation"]},
          "calories": {"type": "string"},
          "carbohydrateContent": {"type": "string"},
          "cholesterolContent": {"type": "string"},
          "fatContent": {"type": "string"},
          "fiberContent": {"type": "string"},
          "proteinContent": {"type": "string"},
          "saturatedFatContent": {"type": "string"},
          "sodiumContent": {"type": "string"},
          "sugarContent": {"type": "string"},
          "transFatContent": {"type": "string"},
          "unsaturatedFatContent": {"type": "string"},
        }
      }
    }
  }
}

SYSTEM = (
  "Tu extrais des recettes et tu dois produire un JSON-LD strictement conforme au type schema.org/Recipe. "
  "Règles importantes : "
  "1) Les durées prepTime/cookTime/totalTime/performTime doivent être en ISO 8601 Duration (ex: PT10M, PT1H15M). "
  "2) recipeIngredient doit être une liste de strings (quantité + ingrédient). "
  "3) recipeInstructions doit être une liste de HowToStep, chaque item avec @type='HowToStep' et 'text'. "
  "4) Ne mets AUCUN texte hors JSON."
)

def parse_recipe_to_schema_org(recipe_text: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": RECIPE_JSON_SCHEMA
        },
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": recipe_text}
        ],
    )

    data = json.loads(resp.choices[0].message.content)

    # Sécurisation: si jamais un temps n'est pas ISO, on tente un fallback
    for k in ["prepTime", "cookTime", "totalTime", "performTime"]:
        if k in data and isinstance(data[k], str):
            # très light check ISO 8601 duration
            if not data[k].startswith("P"):
                data[k] = to_iso8601_duration_fallback(data[k])

    # nutrition @type si nutrition existe
    if "nutrition" in data and isinstance(data["nutrition"], dict):
        data["nutrition"].setdefault("@type", "NutritionInformation")

    data.setdefault("@context", "https://schema.org")
    data.setdefault("@type", "Recipe")
    return data

if __name__ == "__main__":
    with open("recette.txt", "r", encoding="utf-8") as f:
        txt = f.read()

    out = parse_recipe_to_schema_org(txt)
    out["performTime"] = out["cookTime"]

    recipe_name = out.get("name", "recette")
    filename = slugify(recipe_name) + ".json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"OK -> {filename}")
