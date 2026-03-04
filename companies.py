import json
import os

STARTING_PRICE = 10.0
PRICE_CHANGE = 0.001     # price moves 0.1% per share bought/sold (only active at >=100 users)
STATE_FILE = "game_state.json"

COMPANIES = [
    # ── Gen AI ──────────────────────────────────────────────────────────────
    {"name": "OpenAI",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Anthropic",           "sector": "Gen AI",          "country": "USA"},
    {"name": "xAI",                 "sector": "Gen AI",          "country": "USA"},
    {"name": "Mistral AI",          "sector": "Gen AI",          "country": "France"},
    {"name": "Character AI",        "sector": "Gen AI",          "country": "USA"},
    {"name": "Cohere",              "sector": "Gen AI",          "country": "Canada"},
    {"name": "Perplexity AI",       "sector": "Gen AI",          "country": "USA"},
    {"name": "Cursor (Anysphere)",  "sector": "Gen AI",          "country": "USA"},
    {"name": "Sierra",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Glean",               "sector": "Gen AI",          "country": "USA"},
    {"name": "Hugging Face",        "sector": "Gen AI",          "country": "USA"},
    {"name": "Together AI",         "sector": "Gen AI",          "country": "USA"},
    {"name": "Moonshot AI",         "sector": "Gen AI",          "country": "China"},
    {"name": "ElevenLabs",          "sector": "Gen AI",          "country": "USA"},
    {"name": "Harvey AI",           "sector": "Gen AI",          "country": "USA"},
    {"name": "Poolside",            "sector": "Gen AI",          "country": "USA"},
    {"name": "Cognition AI",        "sector": "Gen AI",          "country": "USA"},
    {"name": "Writer",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Runway",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Magic",               "sector": "Gen AI",          "country": "USA"},
    {"name": "Pika Labs",           "sector": "Gen AI",          "country": "USA"},
    {"name": "Imbue",               "sector": "Gen AI",          "country": "USA"},
    {"name": "Sakana AI",           "sector": "Gen AI",          "country": "Japan"},
    {"name": "Stability AI",        "sector": "Gen AI",          "country": "UK"},
    {"name": "01.AI",               "sector": "Gen AI",          "country": "China"},
    {"name": "Inflection AI",       "sector": "Gen AI",          "country": "USA"},
    {"name": "Adept AI",            "sector": "Gen AI",          "country": "USA"},
    {"name": "Aleph Alpha",         "sector": "Gen AI",          "country": "Germany"},
    {"name": "LightOn",             "sector": "Gen AI",          "country": "France"},
    {"name": "Typeface",            "sector": "Gen AI",          "country": "USA"},
    {"name": "Jasper AI",           "sector": "Gen AI",          "country": "USA"},
    {"name": "Copy.ai",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Tome",                "sector": "Gen AI",          "country": "USA"},
    {"name": "Synthesia",           "sector": "Gen AI",          "country": "UK"},
    {"name": "HeyGen",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Otter.ai",            "sector": "Gen AI",          "country": "USA"},
    {"name": "Fireflies.ai",        "sector": "Gen AI",          "country": "USA"},
    {"name": "Luma AI",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Ideogram",            "sector": "Gen AI",          "country": "USA"},
    {"name": "Midjourney",          "sector": "Gen AI",          "country": "USA"},
    {"name": "Suno AI",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Udio",                "sector": "Gen AI",          "country": "USA"},
    {"name": "Krea AI",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Coframe",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Codeium",             "sector": "Gen AI",          "country": "USA"},
    {"name": "Tabnine",             "sector": "Gen AI",          "country": "Israel"},
    {"name": "Replit",              "sector": "Gen AI",          "country": "USA"},
    {"name": "Lovable",             "sector": "Gen AI",          "country": "Sweden"},
    {"name": "Bolt.new (StackBlitz)","sector": "Gen AI",         "country": "USA"},
    {"name": "v0 (Vercel)",         "sector": "Gen AI",          "country": "USA"},

    # ── AI Infrastructure ─────────────────────────────────────────────────
    {"name": "Databricks",          "sector": "AI Infra",        "country": "USA"},
    {"name": "Scale AI",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Cerebras",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Groq",                "sector": "AI Infra",        "country": "USA"},
    {"name": "SambaNova Systems",   "sector": "AI Infra",        "country": "USA"},
    {"name": "Tenstorrent",         "sector": "AI Infra",        "country": "Canada"},
    {"name": "Modular",             "sector": "AI Infra",        "country": "USA"},
    {"name": "Weights & Biases",    "sector": "AI Infra",        "country": "USA"},
    {"name": "Anyscale",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Modal",               "sector": "AI Infra",        "country": "USA"},
    {"name": "Baseten",             "sector": "AI Infra",        "country": "USA"},
    {"name": "BentoML",             "sector": "AI Infra",        "country": "USA"},
    {"name": "Pinecone",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Weaviate",            "sector": "AI Infra",        "country": "Netherlands"},
    {"name": "Chroma",              "sector": "AI Infra",        "country": "USA"},
    {"name": "Qdrant",              "sector": "AI Infra",        "country": "Germany"},
    {"name": "LlamaIndex",          "sector": "AI Infra",        "country": "USA"},
    {"name": "LangChain",           "sector": "AI Infra",        "country": "USA"},
    {"name": "Vellum",              "sector": "AI Infra",        "country": "USA"},
    {"name": "Braintrust",          "sector": "AI Infra",        "country": "USA"},
    {"name": "Arize AI",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Galileo",             "sector": "AI Infra",        "country": "USA"},
    {"name": "Snorkel AI",          "sector": "AI Infra",        "country": "USA"},
    {"name": "Labelbox",            "sector": "AI Infra",        "country": "USA"},
    {"name": "Cleanlab",            "sector": "AI Infra",        "country": "USA"},
    {"name": "OctoAI",              "sector": "AI Infra",        "country": "USA"},
    {"name": "Replicate",           "sector": "AI Infra",        "country": "USA"},
    {"name": "Gradient",            "sector": "AI Infra",        "country": "USA"},
    {"name": "CoreWeave",           "sector": "AI Infra",        "country": "USA"},
    {"name": "Lambda Labs",         "sector": "AI Infra",        "country": "USA"},

    # ── AI Applications ───────────────────────────────────────────────────
    {"name": "Moveworks",           "sector": "AI Applications", "country": "USA"},
    {"name": "Observe.AI",          "sector": "AI Applications", "country": "USA"},
    {"name": "Gong",                "sector": "AI Applications", "country": "USA"},
    {"name": "Chorus.ai",           "sector": "AI Applications", "country": "USA"},
    {"name": "Highspot",            "sector": "AI Applications", "country": "USA"},
    {"name": "Clari",               "sector": "AI Applications", "country": "USA"},
    {"name": "Outreach",            "sector": "AI Applications", "country": "USA"},
    {"name": "Salesloft",           "sector": "AI Applications", "country": "USA"},
    {"name": "Apollo.io",           "sector": "AI Applications", "country": "USA"},
    {"name": "Clay",                "sector": "AI Applications", "country": "USA"},
    {"name": "Instantly",           "sector": "AI Applications", "country": "USA"},
    {"name": "Decagon",             "sector": "AI Applications", "country": "USA"},
    {"name": "Kore.ai",             "sector": "AI Applications", "country": "USA"},
    {"name": "Forethought",         "sector": "AI Applications", "country": "USA"},
    {"name": "Ada Support",         "sector": "AI Applications", "country": "Canada"},
    {"name": "Intercom",            "sector": "AI Applications", "country": "USA"},
    {"name": "Zendesk",             "sector": "AI Applications", "country": "USA"},
    {"name": "Leena AI",            "sector": "AI Applications", "country": "India"},
    {"name": "Uniphore",            "sector": "AI Applications", "country": "USA"},
    {"name": "ASAPP",               "sector": "AI Applications", "country": "USA"},

    # ── Fintech ───────────────────────────────────────────────────────────
    {"name": "Stripe",              "sector": "Fintech",         "country": "USA"},
    {"name": "Revolut",             "sector": "Fintech",         "country": "UK"},
    {"name": "Klarna",              "sector": "Fintech",         "country": "Sweden"},
    {"name": "Chime",               "sector": "Fintech",         "country": "USA"},
    {"name": "Brex",                "sector": "Fintech",         "country": "USA"},
    {"name": "Plaid",               "sector": "Fintech",         "country": "USA"},
    {"name": "Rippling",            "sector": "Fintech",         "country": "USA"},
    {"name": "Deel",                "sector": "Fintech",         "country": "USA"},
    {"name": "Remote",              "sector": "Fintech",         "country": "USA"},
    {"name": "Gusto",               "sector": "Fintech",         "country": "USA"},
    {"name": "Mercury",             "sector": "Fintech",         "country": "USA"},
    {"name": "Ramp",                "sector": "Fintech",         "country": "USA"},
    {"name": "Navan (TripActions)", "sector": "Fintech",         "country": "USA"},
    {"name": "Pipe",                "sector": "Fintech",         "country": "USA"},
    {"name": "Arc",                 "sector": "Fintech",         "country": "USA"},
    {"name": "Jeeves",              "sector": "Fintech",         "country": "USA"},
    {"name": "Parafin",             "sector": "Fintech",         "country": "USA"},
    {"name": "Bond",                "sector": "Fintech",         "country": "USA"},
    {"name": "Unit",                "sector": "Fintech",         "country": "USA"},
    {"name": "Synctera",            "sector": "Fintech",         "country": "USA"},
    {"name": "Marqeta",             "sector": "Fintech",         "country": "USA"},
    {"name": "Lithic",              "sector": "Fintech",         "country": "USA"},
    {"name": "Highnote",            "sector": "Fintech",         "country": "USA"},
    {"name": "Affirm",              "sector": "Fintech",         "country": "USA"},
    {"name": "Sezzle",              "sector": "Fintech",         "country": "USA"},
    {"name": "Creditas",            "sector": "Fintech",         "country": "Brazil"},
    {"name": "Nubank",              "sector": "Fintech",         "country": "Brazil"},
    {"name": "Neon",                "sector": "Fintech",         "country": "Brazil"},
    {"name": "Melio",               "sector": "Fintech",         "country": "USA"},
    {"name": "Tipalti",             "sector": "Fintech",         "country": "USA"},

    # ── Cybersecurity ─────────────────────────────────────────────────────
    {"name": "Wiz",                 "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Lacework",            "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Snyk",                "sector": "Cybersecurity",   "country": "UK"},
    {"name": "Orca Security",       "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Apiiro",              "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Cyera",               "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Torq",                "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Axonius",             "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Noname Security",     "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Salt Security",       "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Ermetic",             "sector": "Cybersecurity",   "country": "Israel"},
    {"name": "Sysdig",              "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Aqua Security",       "sector": "Cybersecurity",   "country": "Israel"},
    {"name": "Chainguard",          "sector": "Cybersecurity",   "country": "USA"},
    {"name": "RunSafe Security",    "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Abnormal Security",   "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Proofpoint",          "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Telos",               "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Secureworks",         "sector": "Cybersecurity",   "country": "USA"},
    {"name": "Dragos",              "sector": "Cybersecurity",   "country": "USA"},

    # ── Dev Tools ─────────────────────────────────────────────────────────
    {"name": "Vercel",              "sector": "Dev Tools",       "country": "USA"},
    {"name": "Netlify",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Render",              "sector": "Dev Tools",       "country": "USA"},
    {"name": "Railway",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Fly.io",              "sector": "Dev Tools",       "country": "USA"},
    {"name": "Supabase",            "sector": "Dev Tools",       "country": "USA"},
    {"name": "PlanetScale",         "sector": "Dev Tools",       "country": "USA"},
    {"name": "Neon DB",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Turso",               "sector": "Dev Tools",       "country": "USA"},
    {"name": "Xata",                "sector": "Dev Tools",       "country": "UK"},
    {"name": "Upstash",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Trigger.dev",         "sector": "Dev Tools",       "country": "UK"},
    {"name": "Inngest",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Temporal",            "sector": "Dev Tools",       "country": "USA"},
    {"name": "Encore",              "sector": "Dev Tools",       "country": "Sweden"},
    {"name": "Buf",                 "sector": "Dev Tools",       "country": "USA"},
    {"name": "Grafana Labs",        "sector": "Dev Tools",       "country": "Sweden"},
    {"name": "Datadog",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "New Relic",           "sector": "Dev Tools",       "country": "USA"},
    {"name": "Honeycomb",           "sector": "Dev Tools",       "country": "USA"},
    {"name": "Chronosphere",        "sector": "Dev Tools",       "country": "USA"},
    {"name": "LaunchDarkly",        "sector": "Dev Tools",       "country": "USA"},
    {"name": "Split.io",            "sector": "Dev Tools",       "country": "USA"},
    {"name": "Statsig",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "PostHog",             "sector": "Dev Tools",       "country": "UK"},
    {"name": "Amplitude",           "sector": "Dev Tools",       "country": "USA"},
    {"name": "Mixpanel",            "sector": "Dev Tools",       "country": "USA"},
    {"name": "Segment",             "sector": "Dev Tools",       "country": "USA"},
    {"name": "Rudderstack",         "sector": "Dev Tools",       "country": "USA"},
    {"name": "Airbyte",             "sector": "Dev Tools",       "country": "USA"},

    # ── Productivity ──────────────────────────────────────────────────────
    {"name": "Notion",              "sector": "Productivity",    "country": "USA"},
    {"name": "Airtable",            "sector": "Productivity",    "country": "USA"},
    {"name": "Coda",                "sector": "Productivity",    "country": "USA"},
    {"name": "Linear",              "sector": "Productivity",    "country": "USA"},
    {"name": "Height",              "sector": "Productivity",    "country": "USA"},
    {"name": "Loom",                "sector": "Productivity",    "country": "USA"},
    {"name": "Miro",                "sector": "Productivity",    "country": "Netherlands"},
    {"name": "Mural",               "sector": "Productivity",    "country": "USA"},
    {"name": "Whimsical",           "sector": "Productivity",    "country": "USA"},
    {"name": "Pitch",               "sector": "Productivity",    "country": "Germany"},
    {"name": "Gamma",               "sector": "Productivity",    "country": "USA"},
    {"name": "Beautiful.ai",        "sector": "Productivity",    "country": "USA"},
    {"name": "Slite",               "sector": "Productivity",    "country": "France"},
    {"name": "Craft",               "sector": "Productivity",    "country": "UK"},
    {"name": "Obsidian",            "sector": "Productivity",    "country": "USA"},
    {"name": "Roam Research",       "sector": "Productivity",    "country": "USA"},
    {"name": "Logseq",              "sector": "Productivity",    "country": "USA"},
    {"name": "Taskade",             "sector": "Productivity",    "country": "USA"},
    {"name": "ClickUp",             "sector": "Productivity",    "country": "USA"},
    {"name": "Monday.com",          "sector": "Productivity",    "country": "Israel"},

    # ── Healthcare AI ─────────────────────────────────────────────────────
    {"name": "Tempus",              "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Recursion Pharma",    "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Insilico Medicine",   "sector": "Healthcare AI",   "country": "Hong Kong"},
    {"name": "Exscientia",          "sector": "Healthcare AI",   "country": "UK"},
    {"name": "Isomorphic Labs",     "sector": "Healthcare AI",   "country": "UK"},
    {"name": "Iterion Medical",     "sector": "Healthcare AI",   "country": "USA"},
    {"name": "PathAI",              "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Viz.ai",              "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Aidoc",               "sector": "Healthcare AI",   "country": "Israel"},
    {"name": "Rad AI",              "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Paige.ai",            "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Clarify Health",      "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Bioptimus",           "sector": "Healthcare AI",   "country": "France"},
    {"name": "Insitro",             "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Owkin",               "sector": "Healthcare AI",   "country": "France"},
    {"name": "Mendel AI",           "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Abridge",             "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Ambience Healthcare", "sector": "Healthcare AI",   "country": "USA"},
    {"name": "DeepScribe",          "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Nabla",               "sector": "Healthcare AI",   "country": "France"},
    {"name": "Suki AI",             "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Corti",               "sector": "Healthcare AI",   "country": "Denmark"},
    {"name": "Hippocratic AI",      "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Glass Health",        "sector": "Healthcare AI",   "country": "USA"},
    {"name": "Forward Health",      "sector": "Healthcare AI",   "country": "USA"},

    # ── Robotics ──────────────────────────────────────────────────────────
    {"name": "Figure AI",           "sector": "Robotics",        "country": "USA"},
    {"name": "Physical Intelligence","sector": "Robotics",       "country": "USA"},
    {"name": "1X Technologies",     "sector": "Robotics",        "country": "Norway"},
    {"name": "Agility Robotics",    "sector": "Robotics",        "country": "USA"},
    {"name": "Boston Dynamics",     "sector": "Robotics",        "country": "USA"},
    {"name": "Apptronik",           "sector": "Robotics",        "country": "USA"},
    {"name": "Sanctuary AI",        "sector": "Robotics",        "country": "Canada"},
    {"name": "Unitree Robotics",    "sector": "Robotics",        "country": "China"},
    {"name": "Kepler Robotics",     "sector": "Robotics",        "country": "China"},
    {"name": "Aethon",              "sector": "Robotics",        "country": "USA"},
    {"name": "Pickle Robot",        "sector": "Robotics",        "country": "USA"},
    {"name": "Symbotic",            "sector": "Robotics",        "country": "USA"},
    {"name": "Gather AI",           "sector": "Robotics",        "country": "USA"},
    {"name": "Viam",                "sector": "Robotics",        "country": "USA"},
    {"name": "Formant",             "sector": "Robotics",        "country": "USA"},

    # ── Space ─────────────────────────────────────────────────────────────
    {"name": "SpaceX",              "sector": "Space",           "country": "USA"},
    {"name": "Planet Labs",         "sector": "Space",           "country": "USA"},
    {"name": "Rocket Lab",          "sector": "Space",           "country": "USA"},
    {"name": "Relativity Space",    "sector": "Space",           "country": "USA"},
    {"name": "Astra",               "sector": "Space",           "country": "USA"},
    {"name": "ABL Space",           "sector": "Space",           "country": "USA"},
    {"name": "Firefly Aerospace",   "sector": "Space",           "country": "USA"},
    {"name": "Spire Global",        "sector": "Space",           "country": "USA"},
    {"name": "HawkEye 360",         "sector": "Space",           "country": "USA"},
    {"name": "Pixxel",              "sector": "Space",           "country": "India"},
    {"name": "Satellogic",          "sector": "Space",           "country": "Uruguay"},
    {"name": "Iceye",               "sector": "Space",           "country": "Finland"},
    {"name": "Capella Space",       "sector": "Space",           "country": "USA"},
    {"name": "Umbra",               "sector": "Space",           "country": "USA"},
    {"name": "LeoLabs",             "sector": "Space",           "country": "USA"},

    # ── Climate Tech ──────────────────────────────────────────────────────
    {"name": "Impossible Foods",    "sector": "Climate Tech",    "country": "USA"},
    {"name": "Solugen",             "sector": "Climate Tech",    "country": "USA"},
    {"name": "Heirloom Carbon",     "sector": "Climate Tech",    "country": "USA"},
    {"name": "Charm Industrial",    "sector": "Climate Tech",    "country": "USA"},
    {"name": "Twelve",              "sector": "Climate Tech",    "country": "USA"},
    {"name": "Verdox",              "sector": "Climate Tech",    "country": "USA"},
    {"name": "Sustaera",            "sector": "Climate Tech",    "country": "USA"},
    {"name": "Terraformation",      "sector": "Climate Tech",    "country": "USA"},
    {"name": "Living Carbon",       "sector": "Climate Tech",    "country": "USA"},
    {"name": "Pachama",             "sector": "Climate Tech",    "country": "USA"},
    {"name": "Watershed",           "sector": "Climate Tech",    "country": "USA"},
    {"name": "Persefoni",           "sector": "Climate Tech",    "country": "USA"},
    {"name": "Greenly",             "sector": "Climate Tech",    "country": "France"},
    {"name": "Sweep",               "sector": "Climate Tech",    "country": "UK"},
    {"name": "Rubicon Carbon",      "sector": "Climate Tech",    "country": "USA"},
    {"name": "Arcadia",             "sector": "Climate Tech",    "country": "USA"},
    {"name": "Copper Labs",         "sector": "Climate Tech",    "country": "USA"},
    {"name": "Form Energy",         "sector": "Climate Tech",    "country": "USA"},
    {"name": "Ascend Elements",     "sector": "Climate Tech",    "country": "USA"},
    {"name": "Redwood Materials",   "sector": "Climate Tech",    "country": "USA"},

    # ── E-Commerce ────────────────────────────────────────────────────────
    {"name": "Shein",               "sector": "E-Commerce",      "country": "China"},
    {"name": "Fanatics",            "sector": "E-Commerce",      "country": "USA"},
    {"name": "Faire",               "sector": "E-Commerce",      "country": "USA"},
    {"name": "Veho",                "sector": "E-Commerce",      "country": "USA"},
    {"name": "Attentive",           "sector": "E-Commerce",      "country": "USA"},
    {"name": "Klaviyo",             "sector": "E-Commerce",      "country": "USA"},
    {"name": "Yotpo",               "sector": "E-Commerce",      "country": "USA"},
    {"name": "Gorgias",             "sector": "E-Commerce",      "country": "USA"},
    {"name": "Triple Whale",        "sector": "E-Commerce",      "country": "USA"},
    {"name": "Northbeam",           "sector": "E-Commerce",      "country": "USA"},
    {"name": "Rebuy",               "sector": "E-Commerce",      "country": "USA"},
    {"name": "Tapcart",             "sector": "E-Commerce",      "country": "USA"},
    {"name": "Rokt",                "sector": "E-Commerce",      "country": "Australia"},
    {"name": "Bazaarvoice",         "sector": "E-Commerce",      "country": "USA"},
    {"name": "Wunderkind",          "sector": "E-Commerce",      "country": "USA"},
    {"name": "Olo",                 "sector": "E-Commerce",      "country": "USA"},
    {"name": "Akeneo",              "sector": "E-Commerce",      "country": "France"},
    {"name": "Contentful",          "sector": "E-Commerce",      "country": "Germany"},
    {"name": "Storyblok",           "sector": "E-Commerce",      "country": "Austria"},
    {"name": "Sanity",              "sector": "E-Commerce",      "country": "Norway"},

    # ── Gaming ────────────────────────────────────────────────────────────
    {"name": "Epic Games",          "sector": "Gaming",          "country": "USA"},
    {"name": "Discord",             "sector": "Gaming",          "country": "USA"},
    {"name": "Unity",               "sector": "Gaming",          "country": "USA"},
    {"name": "Niantic",             "sector": "Gaming",          "country": "USA"},
    {"name": "Kabam",               "sector": "Gaming",          "country": "Canada"},
    {"name": "Nexon",               "sector": "Gaming",          "country": "South Korea"},
    {"name": "Krafton",             "sector": "Gaming",          "country": "South Korea"},
    {"name": "Roblox",              "sector": "Gaming",          "country": "USA"},
    {"name": "Immutable",           "sector": "Gaming",          "country": "Australia"},
    {"name": "Mythical Games",      "sector": "Gaming",          "country": "USA"},
    {"name": "Sky Mavis",           "sector": "Gaming",          "country": "Vietnam"},
    {"name": "Gala Games",          "sector": "Gaming",          "country": "USA"},
    {"name": "Animoca Brands",      "sector": "Gaming",          "country": "Hong Kong"},
    {"name": "Forte",               "sector": "Gaming",          "country": "USA"},
    {"name": "Inworld AI",          "sector": "Gaming",          "country": "USA"},

    # ── Design ────────────────────────────────────────────────────────────
    {"name": "Canva",               "sector": "Design",          "country": "Australia"},
    {"name": "Figma",               "sector": "Design",          "country": "USA"},
    {"name": "Framer",              "sector": "Design",          "country": "Netherlands"},
    {"name": "Webflow",             "sector": "Design",          "country": "USA"},
    {"name": "Squarespace",         "sector": "Design",          "country": "USA"},
    {"name": "Wix",                 "sector": "Design",          "country": "Israel"},
    {"name": "Bubble",              "sector": "Design",          "country": "USA"},
    {"name": "Bravo Studio",        "sector": "Design",          "country": "Spain"},
    {"name": "Penpot",              "sector": "Design",          "country": "Spain"},
    {"name": "Sketch",              "sector": "Design",          "country": "Netherlands"},
    {"name": "InVision",            "sector": "Design",          "country": "USA"},
    {"name": "Zeplin",              "sector": "Design",          "country": "USA"},
    {"name": "Abstract",            "sector": "Design",          "country": "USA"},
    {"name": "Overflow",            "sector": "Design",          "country": "Israel"},
    {"name": "Spline",              "sector": "Design",          "country": "USA"},

    # ── Autonomous Vehicles ───────────────────────────────────────────────
    {"name": "Waymo",               "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Nuro",                "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Zoox",                "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Cruise",              "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Aurora",              "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "TuSimple",            "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Kodiak Robotics",     "sector": "Autonomous Vehicles", "country": "USA"},
    {"name": "Einride",             "sector": "Autonomous Vehicles", "country": "Sweden"},
    {"name": "Gatik",               "sector": "Autonomous Vehicles", "country": "Canada"},
    {"name": "Outrider",            "sector": "Autonomous Vehicles", "country": "USA"},

    # ── Social / Consumer ─────────────────────────────────────────────────
    {"name": "ByteDance",           "sector": "Social",          "country": "China"},
    {"name": "Snap",                "sector": "Social",          "country": "USA"},
    {"name": "Pinterest",           "sector": "Social",          "country": "USA"},
    {"name": "Reddit",              "sector": "Social",          "country": "USA"},
    {"name": "Substack",            "sector": "Social",          "country": "USA"},
    {"name": "Beehiiv",             "sector": "Social",          "country": "USA"},
    {"name": "Ghost",               "sector": "Social",          "country": "UK"},
    {"name": "Geneva",              "sector": "Social",          "country": "USA"},
    {"name": "Clubhouse",           "sector": "Social",          "country": "USA"},
    {"name": "Flip",                "sector": "Social",          "country": "USA"},

    # ── HR Tech ───────────────────────────────────────────────────────────
    {"name": "Lattice",             "sector": "HR Tech",         "country": "USA"},
    {"name": "Leapsome",            "sector": "HR Tech",         "country": "Germany"},
    {"name": "Betterworks",         "sector": "HR Tech",         "country": "USA"},
    {"name": "Greenhouse",          "sector": "HR Tech",         "country": "USA"},
    {"name": "Lever",               "sector": "HR Tech",         "country": "USA"},
    {"name": "Ashby",               "sector": "HR Tech",         "country": "USA"},
    {"name": "Gem",                 "sector": "HR Tech",         "country": "USA"},
    {"name": "SeekOut",             "sector": "HR Tech",         "country": "USA"},
    {"name": "Eightfold AI",        "sector": "HR Tech",         "country": "USA"},
    {"name": "Phenom",              "sector": "HR Tech",         "country": "USA"},
    {"name": "Beamery",             "sector": "HR Tech",         "country": "UK"},
    {"name": "Workstream",          "sector": "HR Tech",         "country": "USA"},
    {"name": "Fountain",            "sector": "HR Tech",         "country": "USA"},
    {"name": "Bluecrew",            "sector": "HR Tech",         "country": "USA"},
    {"name": "Invisible Technologies", "sector": "HR Tech",      "country": "USA"},
]


def load_state():
    """Load game state from file, or create fresh state if file doesn't exist."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    else:
        return new_state()

def new_state():
    """Create a fresh game state with all companies at starting price."""
    state = {
        "companies": {},
        "vcs": {}
    }
    for c in COMPANIES:
        state["companies"][c["name"]] = {
            "price": STARTING_PRICE,
            "shares_sold": 0
        }
    return state

def save_state(state):
    """Save game state to file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_price(state, company_name):
    return state["companies"][company_name]["price"]

def buy_shares(state, company_name, amount, move_price=False):
    """Buy $amount worth of shares. Returns number of shares bought."""
    price = get_price(state, company_name)
    shares = amount / price
    state["companies"][company_name]["shares_sold"] += shares
    if move_price:
        state["companies"][company_name]["price"] = round(price * (1 + PRICE_CHANGE * shares), 2)
    return shares

def sell_shares(state, company_name, shares, move_price=False):
    """Sell shares. Returns cash received."""
    price = get_price(state, company_name)
    cash = shares * price
    state["companies"][company_name]["shares_sold"] -= shares
    if move_price:
        state["companies"][company_name]["price"] = round(price * (1 - PRICE_CHANGE * shares), 2)
    return cash

def show_all(state):
    print("\n" + "="*60)
    print(f"{'#':<4} {'Company':<22} {'Sector':<22} {'Price'}")
    print("="*60)
    for i, c in enumerate(COMPANIES):
        price = get_price(state, c["name"])
        print(f"{i+1:<4} {c['name']:<22} {c['sector']:<22} ${price}")
    print("="*60)

def search_by_sector(state, sector):
    results = [c for c in COMPANIES if sector.lower() in c["sector"].lower()]
    if not results:
        print("No companies found.")
    else:
        print(f"\n--- '{sector}' companies ---")
        for c in results:
            price = get_price(state, c["name"])
            print(f"  {c['name']:<25} ${price}")

if __name__ == "__main__":
    state = load_state()
    save_state(state)

    while True:
        print("\nCompany Database")
        print("1. Show all companies")
        print("2. Search by sector")
        print("3. Quit")

        choice = input("Enter 1, 2 or 3: ")

        if choice == "1":
            show_all(state)
        elif choice == "2":
            sector = input("Enter sector (e.g. Gen AI, Fintech, Design): ")
            search_by_sector(state, sector)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
