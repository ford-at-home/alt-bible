# 🎭 Alt Bible

> **AI-Powered Scripture Reimagined** - Transform biblical text into the voices of modern personas using advanced AI translation with hardcore style transfer.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
<a href="https://www.deepseek.com/"><img alt="Homepage"
    src="https://github.com/deepseek-ai/DeepSeek-V2/blob/main/figures/badge.svg?raw=true"/></a>

## 🌟 Overview

Alt Bible is a creative AI-powered application that reimagines scripture in the voices of modern personas using **hardcore style transfer**. Using Amazon Bedrock and DeepSeek AI, it translates biblical chapters into unique character voices with full persona infusion:

### 🎭 Available Personas
- **Joe Rogan** - Podcast host energy with "bro science" vibes
- **Samuel L. Jackson** - Intense, profanity-laced delivery
- **Maya Angelou** - Poetic, soulful, and deeply spiritual
- **Hunter S. Thompson** - Gonzo journalism style with wild energy
- **Cardi B** - Bronx energy with modern slang and attitude
- **Ram Dass** - Spiritual teacher with psychedelic wisdom
- **Ernest Hemingway** - Terse, masculine, minimalist prose
- **Slang Spanish** - Urban Latino street culture

### ✨ Key Features

- 🧠 **Hardcore Style Transfer** - Full persona infusion, not just modern lingo
- 🎯 **Multi-Level Intensity** - Adjustable persona intensity levels
- 📦 **Full Bible Translation** - Complete Bible processing with chapter-by-chapter and verse-by-verse fallback
- 💰 **Cost Estimation** - Smart token counting and cost prediction before translation
- 🔁 **Checkpoint System** - Resume capability with progress tracking
- 🗂 **Multiple Formats** - Support for JSON, text, and nested Bible structures
- 🧮 **Intelligent Token Management** - Optimized for Bedrock token limits
- 📊 **Database-Ready Output** - Strict JSON format for DynamoDB compatibility

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bible Input   │───▶│  Hardcore Style │───▶│   Processed     │
│   (JSON/Text)   │    │  Transfer AI    │    │   Output        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   preprocessors/         translators/              storage/
   - JSON parser         - Chapter translator      - DynamoDB loader
   - Text parser         - Verse translator        - JSON validator
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **AWS CLI** - [Install AWS CLI](https://aws.amazon.com/cli/)
- **AWS Account** - With Bedrock access and DeepSeek model provisioned

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/alt-bible.git
cd alt-bible
make install
```

### 2. Configure AWS

```bash
aws configure
```

Ensure your AWS account has:
- Amazon Bedrock access
- DeepSeek model provisioned (`us.deepseek.r1-v1:0`)

### 3. Preprocess Bible Data

```bash
make preprocess
```

This processes your Bible file into the required JSON structure.

### 4. List Available Personas

```bash
make list-personas
```

See all supported personas with descriptions and style details.

### 5. Estimate Translation Cost

```bash
make estimate-full-bible PERSONA="joe-rogan"
```

Get cost estimates before starting full translation.

### 6. Translate the Bible

```bash
make translate-full-bible PERSONA="joe-rogan"
```

This translates the entire Bible with hardcore style transfer!

## 🛠️ How to Use

### Basic Commands

```bash
# Install dependencies
make install

# Preprocess Bible data
make preprocess

# List all personas
make list-personas

# Estimate translation cost
make estimate-full-bible PERSONA="joe-rogan"

# Translate entire Bible
make translate-full-bible PERSONA="joe-rogan"

# Translate single chapter
make translate-chapter BOOK="Genesis" CHAPTER=1 PERSONA="joe-rogan"

# Clean up generated files
make clean
```

### Advanced Usage

#### Cost Estimation
```bash
# Estimate full Bible translation cost
make estimate-full-bible PERSONA="joe-rogan"

# Estimate single chapter cost
make estimate-chapter BOOK="Genesis" CHAPTER=1 PERSONA="joe-rogan"
```

#### Translation Options
```bash
# Full Bible translation (recommended)
make translate-full-bible PERSONA="joe-rogan"

# Single chapter translation
make translate-chapter BOOK="Genesis" CHAPTER=1 PERSONA="joe-rogan"

# Test translation (small sample)
make test-translation PERSONA="joe-rogan"
```

#### Persona Customization
```bash
# View persona details
make list-personas

# Test specific persona
make test-translation PERSONA="samuel-l-jackson"
```

## 🎭 Persona System

### Hardcore Style Transfer

The system uses **multi-level persona infusion** rather than simple modern translation:

- **Level 1**: Basic persona voice and vocabulary
- **Level 2**: Character-specific mannerisms and catchphrases  
- **Level 3**: Full persona channeling with signature style

### Persona Metadata

Each persona includes:
- **Display Name**: Human-readable name
- **Description**: Character background and style
- **Style Guide**: Specific writing characteristics
- **Catchphrases**: Signature expressions
- **Intensity Levels**: Adjustable persona strength

### Example Personas

**Joe Rogan**
- Style: Podcast host energy, "bro science" vibes
- Catchphrases: "That's wild, man", "Check this out"
- Intensity: High energy, conversational

**Samuel L. Jackson**
- Style: Intense, profanity-laced, dramatic
- Catchphrases: "Motherf***er", "I've had it"
- Intensity: Maximum intensity, theatrical

## 📊 Translation Process

### 1. **Preprocessing**
- Loads Bible from JSON or text format
- Validates structure and content
- Prepares for AI processing

### 2. **Cost Estimation**
- Counts tokens for each chapter
- Estimates translation costs
- Identifies chapters needing verse-by-verse fallback

### 3. **Translation**
- **Chapter-by-chapter**: For shorter chapters (better narrative flow)
- **Verse-by-verse**: Fallback for long chapters (Psalm 119, etc.)
- **Hardcore style transfer**: Full persona infusion
- **Strict JSON output**: Database-compatible format

### 4. **Validation & Storage**
- JSON schema validation
- Error repair and retry logic
- Checkpoint saving for resume capability
- Progress tracking and logging

## 📁 Project Structure

```
alt-bible/
├── src/                    # Source code modules
│   ├── preprocessors/      # Bible data preprocessing
│   │   ├── json_preprocessor.py
│   │   └── text_preprocessor.py
│   ├── translators/        # AI translation logic
│   │   ├── chapter_translator.py
│   │   ├── verse_translator.py
│   │   └── full_bible_translator.py
│   ├── storage/           # Data storage operations
│   │   └── dynamodb_loader.py
│   └── utils/             # Utilities and helpers
│       ├── persona_loader.py
│       ├── cost_calculator.py
│       └── json_validator.py
├── scripts/               # Executable scripts
│   ├── preprocess_bible.py
│   ├── translate_bible.py
│   └── translate_bible_chapters.py
├── data/                  # Input and processed data
│   ├── input/            # Raw Bible files
│   ├── processed/        # Processed JSON and translations
│   └── personas.json     # Persona metadata
├── tests/                # Test files
│   ├── test_*.py
│   └── debug_*.py
├── logs/                 # Translation logs and outputs
├── infrastructure/       # AWS infrastructure docs
├── Makefile             # Build and automation commands
└── README.md            # This file
```

## 💰 Cost Management

### Token Counting
- Uses `tiktoken` for accurate token estimation
- Considers both input and output tokens
- Accounts for prompt overhead

### Cost Estimation
```bash
# Estimate full Bible translation
make estimate-full-bible PERSONA="joe-rogan"

# Estimate single chapter
make estimate-chapter BOOK="Genesis" CHAPTER=1 PERSONA="joe-rogan"
```

### Pricing
- Based on DeepSeek model pricing
- Includes AWS markup
- Shows cost per chapter and total

## 🔧 Configuration

### Supported Bible Formats

1. **JSON Format** (Recommended)
   ```json
   {
     "Genesis": {
       "1": {
         "1": "In the beginning God created...",
         "2": "And the earth was without form..."
       }
     }
   }
   ```

2. **Text Format**
   ```
   Genesis 1:1 In the beginning God created...
   Genesis 1:2 And the earth was without form...
   ```

### Model Configuration

- **Primary Model**: `us.deepseek.r1-v1:0` via Amazon Bedrock
- **API Method**: `converse()` for better conversation flow
- **Token Limits**: Optimized for Bedrock constraints
- **Fallback**: Verse-by-verse for long chapters

## 🛠️ Development

### Adding New Personas

1. **Edit `data/personas.json`**:
   ```json
   {
     "new-persona": {
       "display_name": "New Persona",
       "description": "Character description",
       "style": "Writing style guide",
       "catchphrases": ["Signature phrase 1", "Signature phrase 2"],
       "intensity_levels": {
         "1": "Basic voice",
         "2": "Enhanced mannerisms", 
         "3": "Full channeling"
       }
     }
   }
   ```

2. **Test the persona**:
   ```bash
   make test-translation PERSONA="new-persona"
   ```

### Extending Functionality

The modular architecture supports:
- **Audio Generation**: Convert translations to speech
- **REST API**: Serve translations via web API
- **Additional Models**: Support for Claude, GPT, etc.
- **New Formats**: Support for additional Bible formats

## 🔍 Troubleshooting

### Common Issues

**AWS Bedrock Access**
```bash
# Check model availability
aws bedrock list-foundation-models --region us-east-1

# Verify DeepSeek model is provisioned
aws bedrock list-model-customization-jobs --region us-east-1
```

**Translation Errors**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify model access: `make test-models`
- Check token limits: Use cost estimation first

**JSON Parsing Issues**
- Validate input format: `make validate-input`
- Check file encoding: Ensure UTF-8
- Review error logs: Check `logs/` directory

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Test specific components
make test-translation PERSONA="joe-rogan"
```

## 📊 Output Format

### Translation Output
```json
{
  "Genesis": {
    "1": {
      "1": "Yo, check this out - in the beginning, God was like, 'Let's make some crazy stuff happen!'",
      "2": "And the earth was just sitting there, all empty and dark, bro..."
    }
  }
}
```

### Log Files
- **Translation logs**: `logs/translation_<persona>_<timestamp>.log`
- **Error logs**: `logs/errors_<persona>_<timestamp>.log`
- **Progress logs**: `logs/progress_<persona>_<timestamp>.log`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Add comprehensive tests
- Update documentation for API changes
- Use meaningful commit messages
- Test with multiple personas

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bible text sources (KJV, BBE, etc.)
- Amazon Bedrock for AI capabilities
- DeepSeek for the translation model
- All persona inspirations

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review AWS Bedrock documentation

---

**Made with ❤️ for creative scripture exploration and AI-powered storytelling** 