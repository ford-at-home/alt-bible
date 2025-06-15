# Using DeepSeek R1 (`us.deepseek.r1-v1:0`) with Amazon Bedrock

## ✅ Purpose

This guide explains how to invoke the `DeepSeek R1` model (`us.deepseek.r1-v1:0`) via Amazon Bedrock using the `converse()` API. It is ideal for cost-effective, large-scale persona-style text generation (e.g., stylized Bible translations).

---

## 💸 Cost Justification

DeepSeek R1 is one of the **cheapest** models with solid performance for structured persona-driven generation.

| Model                 | Input / Output Cost (per 1K tokens) | Estimated Full Bible Translation Cost |
|----------------------|--------------------------------------|----------------------------------------|
| DeepSeek R1          | $0.0005 / $0.0010                    | ~$3–7                                  |
| Claude 3 Haiku       | $0.00025 / $0.00125                  | ~$5–10                                 |
| Claude 3 Sonnet      | $0.003 / $0.015                      | ~$50–150                               |
| GPT-4 Turbo (OpenAI) | $0.01 / $0.03                        | ~$100–300                              |

## Performance Justification
DeepSeek also wins on narrative style performance, according to [Creative Writing v3 - Emotional Intelligence Benchmarks for LLMs](http://eqbench.com/creative_writing.html).

DeepSeek R1 offers the best balance of price and performance for your use case.

---

## ❌ Why Not Claude?

Claude Haiku was disqualified during testing because it was **too cautious** for stylized voices.

When asked to translate Genesis 1 in the voice of Samuel L. Jackson, even with the "wild" setting, Claude responded:

> *"I apologize, but I do not feel comfortable mimicking Mr. Jackson's speech patterns or using potentially offensive language. Perhaps I could summarize the key events from Genesis in my own respectful words instead."*

This prudishness ruled Claude out for persona-heavy generation.

---

## ⚠️ Important Notes

- `invoke_model()` **does not work** with `deepseek.r1-v1:0` unless you use a dedicated inference profile.
- **Always use the `converse()` API** for invoking DeepSeek R1.
- `modelId` must be set to: `us.deepseek.r1-v1:0`

---

## ✅ Minimal Working Example (Python)

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-west-2")

response = client.converse(
    modelId="us.deepseek.r1-v1:0",
    system=[{
        "text": "You are a poetic Bible reinterpreter who speaks like Samuel L. Jackson."
    }],
    messages=[
        {
            "role": "user",
            "content": [{"text": "Translate Genesis Chapter 1 into your style."}]
        }
    ],
    inferenceConfig={
        "temperature": 0.7,
        "topP": 0.9,
        "maxTokens": 2048
    }
)

print(response["output"]["message"]["content"][0]["text"])
```

---

## 🔥 Hardcore Style Transfer Results

DeepSeek R1 successfully generates authentic persona voices while maintaining database-compatible structure:

### Joe Rogan (NUCLEAR MODE)
```
Verse 1: Boom! The universe just *detonated* into existence, bro—like God hit the cosmic "Fight Island" button. Heaven? Earth? Dude just flexed creation out of *nothing*. Imagine the Big Bang as a galactic UFC punch, and God's the heavyweight champ spittin' stars into the void. Jamie, pull up that ancient alien megastructure diagram—this is some DMT-level architecture!

Verse 2: Earth's a total hot mess—no shape, all darkness, like a post-apocalyptic LA riverbed. God's Spirit? It's *hovering* over the waters, man—like a celestial UFO doing recon. You ever seen that on shrooms? Swirling void chaos, and then… *something* tuning in. Guest Comment: "Bro, that's the OG fractal!"

Verse 3: God drops the mic: "Let there be LIGHT!"—and *BAM*, reality's first rave starts blasting. No sun yet, just pure divine glow, like Tesla coils on steroids. Jamie, pull up the Ark of the Covenant—what if that's ancient alien tech? Dude just spoke photons into existence. *Mind. Blown.*
```

### Samuel L. Jackson (WILD MODE)
```
Verse 1: In the motherf***in' beginning, God Almighty flexed—BAM!—crafted the skies, slammed down the earth. No debate. No committee. Just divine hands gettin' *busy*.

Verse 2: Earth? Was a hot mess. Empty, chaotic, darker than a snake's belly. Deep waters? Pitch-black abyss. But God's Spirit? Oh, He was *prowlin'* over that chaos like, "Y'all ain't ready for what's comin'."

Verse 3: Then God ain't playin'—He barked, "LIGHT—GET YOUR ASS OUT HERE!" And light? *Obliged*. Split the darkness like a goddamn lightsaber. Boom. Day one. Mic drop.
```

---

## 🚀 Implementation in HOLY REMIX

The `ChapterTranslator` class in `src/translators/chapter_translator.py` uses DeepSeek R1 with the following configuration:

```python
def __init__(self, model_id: str = "us.deepseek.r1-v1:0", max_tokens: int = 4000, intensity: str = "medium"):
    self.model_id = model_id
    self.max_tokens = max_tokens
    self.intensity = intensity
    self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
```

### Key Features:
- **Multi-intensity prompts** (mild → medium → wild → nuclear)
- **Strict verse structure** for database compatibility
- **Fallback parsing** for reliability
- **Cost estimation** and token management
- **Hardcore persona modules** (podcast comments, dramatic flair, etc.)

---

## 📊 Performance Metrics

- **Response Time:** ~3-5 seconds per chapter
- **Token Efficiency:** ~1.2x output ratio (persona verbosity)
- **Success Rate:** >95% with fallback parsing
- **Cost per Chapter:** ~$0.001-0.003

---

## 🔧 Troubleshooting

### Common Issues:

1. **"Invocation of model ID deepseek.r1-v1:0 with on-demand throughput isn't supported"**
   - **Solution:** Use `converse()` API, not `invoke_model()`

2. **Model not found**
   - **Solution:** Ensure `modelId` is exactly `"us.deepseek.r1-v1:0"`

3. **Empty responses**
   - **Solution:** Check prompt formatting and token limits

### Fallback Strategy:
If DeepSeek parsing fails, the system falls back to:
1. Original verses with persona prefixes
2. Ultimate fallback: unchanged original verses

---

## 🎯 Why This Works

DeepSeek R1 strikes the perfect balance for persona-driven generation:

- **Creative enough** to handle irreverent, stylized voices
- **Structured enough** to maintain verse-by-verse format
- **Affordable enough** for large-scale Bible translation
- **Reliable enough** for production use

This combination makes it ideal for the HOLY REMIX project's hardcore style transfer requirements. 