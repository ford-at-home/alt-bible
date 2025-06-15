# alt-bible-backend
This backend stack supports a creative AI-powered Bible web app that reimagines scripture in the voices of modern personas (e.g., Joe Rogan, Cardi B, Ram Dass, Samuel L. Jackson, Hunter S. Thompson, Maya Angelou). It provides storage, structure, and AI translation logic to generate and serve verse-level scripture, indexed by chapter.

---

## ✅ Features

- 🧠 Translates Bible chapters into custom personas using `us.deepseek.r1-v1:0` via Amazon Bedrock
- 📦 Stores verse-level translations in DynamoDB
- 🔁 Idempotent translation job with checkpointing
- 🔍 Indexed by `book`, `chapter`, and `verse`, per persona
- 🗂 Preloaded KJV baseline via one-time loader script

---

## 📁 Structure

- `cdk/` – CDK stack for provisioning DynamoDB
- `translate_bible.py` – Main translation script using Bedrock + DeepSeek
- `download_kjv.py` – Downloads and restructures the KJV into JSON
- `load_kjv_to_dynamodb.py` – Loads KJV into DynamoDB in proper schema
- `checkpoint_<persona>.json` – Tracks translation progress for idempotency
- `kjv_bible.json` – Reorganized Bible by book → chapter → verse

---

## 🚀 Setup Instructions

### 1. Deploy the Infrastructure

```bash
cd cdk/
cdk deploy
This provisions the BibleTranslations DynamoDB table.

2. Download the Bible
bash
Copy
Edit
python download_kjv.py
This outputs a structured kjv_bible.json.

3. (Optional) Load the KJV as a baseline
bash
Copy
Edit
python load_kjv_to_dynamodb.py
4. Translate to Persona Voice
bash
Copy
Edit
python translate_bible.py
This will:

Translate each chapter using DeepSeek

Split it back into verse-level segments

Store each verse under:

pk = persona#samuel_l_jackson

sk = book#Genesis#1#1

🔧 Configurable
Supports multiple personas

Modular model selection (Claude, DeepSeek, etc.)

Easy to extend with audio generation or API serving

📦 DynamoDB Schema
pk	sk	translated_text	metadata
persona#samuel_l_jackson	book#Genesis#1#1	“God kicked it off real loud…”	{ book, chapter, verse, persona }

📌 Notes
Translation uses a cost-effective model (us.deepseek.r1-v1:0)

Checkpoint files ensure restartability

All verse data stored per persona

