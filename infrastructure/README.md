# 🏗️ Infrastructure Planning - API Serving Phase

This document outlines the infrastructure plan for serving pre-generated Bible translations via API.

## 🎯 Overview

**Phase 2 Goal**: Deploy a scalable API that serves pre-generated persona translations without real-time AI calls.

## 🏛️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│   API Gateway   │───▶│   Lambda/ECS    │
│   (Web/Mobile)  │    │   (Rate Limit)  │    │   (API Server)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CloudFront    │    │   DynamoDB      │
                       │   (CDN Cache)   │    │   (Translations)│
                       └─────────────────┘    └─────────────────┘
```

## 📋 Infrastructure Components

### 1. **API Layer**
- **AWS API Gateway**: RESTful API with rate limiting and authentication
- **AWS Lambda** or **ECS Fargate**: Serverless or containerized API server
- **CloudFront**: CDN for caching and global distribution

### 2. **Data Layer**
- **DynamoDB**: Store pre-generated translations
- **S3**: Backup and archive translations
- **CloudWatch**: Monitoring and logging

### 3. **Security & Access**
- **Cognito**: User authentication and management
- **IAM**: Service permissions and access control
- **WAF**: Web application firewall

## 🗄️ DynamoDB Table Structure

### Table Name: `bible-verses` (or similar)

#### Primary Key Structure:
- **Partition Key**: `version` (String) - e.g., "NIV", "ESV", "KJV", "joe-rogan", "samuel-l-jackson", etc.
- **Sort Key**: `book_chapter` (String) - e.g., "Genesis_1", "Matthew_5", etc.

#### Item Structure:
```json
{
  "version": "joe-rogan",
  "book_chapter": "Genesis_1",
  "book": "Genesis",
  "chapter": "1",
  "verses": {
    "1": "In the beginning God created the heavens and the earth, man. That's wild.",
    "2": "Now the earth was formless and empty, dude. You gotta understand...",
    "3": "And God said, Let there be light, and there was light. Check this out!",
    // ... all verses for that chapter
  }
}
```

### Why This Structure Works

- **Efficient Queries**: Your Lambda can query exactly one item using `version` and `book_chapter` to get all verses for a chapter
- **Matches Your API**: Perfectly aligns with your `/api/{version}/{book}/{chapter}` endpoint
- **Cost Effective**: Single read operation per chapter request
- **Frontend Compatible**: The `verses` object structure matches exactly what your frontend expects from the `bibleData` structure

## 🎨 Frontend Integration Needed

You'll need to modify your app to:

- **Replace static imports**: Replace the static `bibleData` import with API calls to your Lambda
- **Add loading states**: Show loading indicators while fetching chapter data
- **Handle async nature**: Manage the asynchronous data fetching (probably in your `useBibleApp` hook)
- **Implement caching**: Cache fetched chapters to avoid repeated API calls

The current frontend structure with testaments, books, and chapters will work perfectly - you'll just need to fetch the actual verse data when a chapter is selected rather than reading from the static data file.

## 🚀 Deployment Options

### Option A: Serverless (Recommended)
```
API Gateway → Lambda → DynamoDB
```
**Pros**: Auto-scaling, pay-per-use, minimal maintenance
**Cons**: Cold starts, execution time limits

### Option B: Containerized
```
API Gateway → ECS Fargate → DynamoDB
```
**Pros**: No cold starts, longer execution times, more control
**Cons**: Higher base costs, more complex management

### Option C: Hybrid
```
API Gateway → Lambda (cached) → ECS (heavy processing) → DynamoDB
```
**Pros**: Best of both worlds
**Cons**: More complex architecture

## 📊 API Endpoints

### Core Endpoints
```
GET /api/v1/translations/{version}/{book}/{chapter}
GET /api/v1/translations/{version}/{book}/{chapter}/{verse}
GET /api/v1/personas
GET /api/v1/books
GET /api/v1/health
```

### Example Requests
```bash
# Get Genesis 1 in Samuel L. Jackson's voice
curl "https://api.holyremix.com/v1/translations/samuel-l-jackson/Genesis/1"

# Get specific verse
curl "https://api.holyremix.com/v1/translations/joe-rogan/John/3/16"

# List available personas
curl "https://api.holyremix.com/v1/personas"
```

## 💾 Legacy Data Schema (For Reference)

### Previous DynamoDB Table: `BibleTranslations`
```json
{
  "pk": "persona#samuel_l_jackson",
  "sk": "book#Genesis#1",
  "verses": {
    "1": "You best believe in the beginning...",
    "2": "And it was a mess, pure chaos...",
    "3": "And God said, Let there be light..."
  },
  "metadata": {
    "persona": "samuel_l_jackson",
    "book": "Genesis",
    "chapter": 1,
    "verse_count": 31,
    "translation_date": "2024-01-01T00:00:00Z",
    "model_used": "us.deepseek.r1-v1:0"
  }
}
```

## 🔧 Implementation Roadmap

### Phase 2.1: Basic API (Week 1-2)
- [ ] Set up API Gateway
- [ ] Create Lambda function for basic endpoints
- [ ] Connect to existing DynamoDB
- [ ] Basic authentication

### Phase 2.2: Caching & Performance (Week 3-4)
- [ ] Add CloudFront CDN
- [ ] Implement response caching
- [ ] Add rate limiting
- [ ] Performance monitoring

### Phase 2.3: Advanced Features (Week 5-6)
- [ ] User management (Cognito)
- [ ] Advanced search/filtering
- [ ] Analytics and usage tracking
- [ ] Admin dashboard

### Phase 2.4: Production Ready (Week 7-8)
- [ ] Security hardening
- [ ] Load testing
- [ ] Documentation
- [ ] Monitoring and alerting

## 💰 Cost Estimation

### Monthly Costs (estimated)
- **API Gateway**: $1-5/month
- **Lambda**: $5-20/month (depending on usage)
- **DynamoDB**: $10-50/month (depending on storage)
- **CloudFront**: $5-15/month
- **Total**: $20-90/month

### Scaling Considerations
- **10,000 requests/day**: ~$50/month
- **100,000 requests/day**: ~$200/month
- **1,000,000 requests/day**: ~$1,000/month

## 🔒 Security Considerations

### Authentication
- API keys for basic access
- Cognito for user accounts
- JWT tokens for session management

### Data Protection
- All data encrypted at rest
- HTTPS for all API calls
- Rate limiting to prevent abuse
- Input validation and sanitization

### Monitoring
- CloudWatch for metrics and logs
- AWS WAF for DDoS protection
- Custom alerts for unusual activity

## 🧪 Testing Strategy

### Unit Tests
- API endpoint functionality
- Data validation
- Error handling

### Integration Tests
- End-to-end API flows
- Database operations
- Authentication flows

### Load Tests
- Performance under load
- Rate limiting effectiveness
- Database performance

## 📈 Monitoring & Analytics

### Key Metrics
- API response times
- Error rates
- Usage by persona/book
- User engagement
- Cost per request

### Dashboards
- Real-time API health
- Usage analytics
- Cost tracking
- Performance metrics

## 🚀 Deployment Strategy

### Environment Setup
- **Development**: Local testing
- **Staging**: Pre-production testing
- **Production**: Live API

### CI/CD Pipeline
- GitHub Actions for automation
- Infrastructure as Code (CDK/Terraform)
- Automated testing and deployment
- Blue-green deployments

## 📚 Next Steps

1. **Choose deployment option** (recommend serverless)
2. **Set up basic API Gateway and Lambda**
3. **Create API server code**
4. **Test with existing DynamoDB data**
5. **Add caching and optimization**
6. **Deploy to production**

## 🔗 Related Files

- `cdk/` - Infrastructure as Code (when implemented)
- `api/` - API server code (when implemented)
- `tests/` - API tests (when implemented) 