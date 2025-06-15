# HOLY REMIX Usage Guide

## 🚀 Quick Start

### 1. Setup
```bash
# Clone and install
git clone <repository>
cd holy-remix
make install

# Configure AWS
aws configure
```

### 2. Prepare Bible Data
```bash
# Place your Bible file in data/input/
# Supported formats: JSON, text with verse markers
make preprocess
```

### 3. Explore Personas
```bash
# See all available personas
make list-personas
```

### 4. Estimate Costs
```bash
# Get cost estimate before translation
make estimate-full-bible PERSONA="joe-rogan"
```

### 5. Start Translation
```bash
# Translate entire Bible
make translate-full-bible PERSONA="joe-rogan"
```

## 🎭 Available Personas

### Joe Rogan
- **Style**: Podcast host energy, "bro science" vibes
- **Best for**: Genesis, Exodus, Revelation
- **Example**: "Yo, check this out - in the beginning, God was like, 'Let's make some crazy stuff happen!'"

### Samuel L. Jackson
- **Style**: Intense, profanity-laced, dramatic
- **Best for**: Psalms, Revelation, dramatic passages
- **Example**: "In the beginning, God created the heaven and the earth, motherf***er!"

### Maya Angelou
- **Style**: Poetic, soulful, deeply spiritual
- **Best for**: Psalms, Song of Solomon, poetic books
- **Example**: "In the beginning, when time was but a whisper, God breathed life into the void."

## 📊 Cost Examples

### Full Bible Translation Estimates
- **Joe Rogan**: ~$150-200
- **Samuel L. Jackson**: ~$150-200
- **Maya Angelou**: ~$150-200

### Single Chapter Examples
- **Genesis 1**: ~$2-3
- **Psalm 23**: ~$1-2
- **Revelation 1**: ~$3-4

## 🔧 Common Commands

### Translation Commands
```bash
# Full Bible translation
make translate-full-bible PERSONA="joe-rogan"

# Single chapter
make translate-chapter PERSONA="samuel-l-jackson" BOOK="Genesis" CHAPTER=1

# Test with small sample
make test-translation PERSONA="maya-angelou"
```

### Utility Commands
```bash
# List personas
make list-personas

# Estimate costs
make estimate-full-bible PERSONA="joe-rogan"

# Run tests
make run-tests

# Clean up
make clean
```

## 📁 Output Files

### Translation Output
- **Full Bible**: `translated_bible_<persona>.json`
- **Chapter**: `data/processed/translations/<persona>_<book>_<chapter>.txt`
- **Logs**: `logs/translation_<persona>_<timestamp>.log`

### Checkpoint Files
- **Progress**: `checkpoint_<persona>.json`
- **Resume**: System automatically resumes from last checkpoint

## 🔍 Troubleshooting

### Common Issues

**AWS Credentials**
```bash
# Check credentials
aws sts get-caller-identity

# Configure if needed
aws configure
```

**Model Access**
```bash
# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Verify DeepSeek model
aws bedrock list-model-customization-jobs --region us-east-1
```

**Translation Errors**
```bash
# Check logs
tail -f logs/translation_<persona>_*.log

# Test with small sample
make test-translation PERSONA="joe-rogan"
```

## 💡 Tips & Best Practices

### Cost Optimization
- Use cost estimation before full translation
- Start with test translations
- Use checkpoints for resume capability
- Monitor token usage

### Quality Assurance
- Test personas with familiar chapters
- Review sample outputs before full translation
- Use appropriate personas for content type
- Monitor translation logs

### Performance
- Translation takes 8-12 hours for full Bible
- Use checkpoints for interruption recovery
- Monitor AWS Bedrock quotas
- Plan for overnight processing

## 🎯 Use Cases

### Creative Writing
- Generate unique biblical interpretations
- Create character-driven narratives
- Explore different voice styles

### Educational
- Compare traditional vs. modern interpretations
- Study language and style differences
- Explore cultural perspectives

### Entertainment
- Create humorous biblical content
- Generate persona-specific quotes
- Develop creative projects

## 📞 Support

### Getting Help
- Check troubleshooting section
- Review error logs in `logs/` directory
- Test with small samples first
- Verify AWS configuration

### Contributing
- Add new personas to `data/personas.json`
- Test with multiple Bible formats
- Report issues with detailed logs
- Suggest improvements and features

---

**Happy translating! 🎭📖** 