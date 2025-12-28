# Alpha Intelligence Bot - Version History

## Version 1.0.0 (2025-12-28)
**Status:** 🚀 Live on Railway

### Features
- ✅ Stock analysis with `/snapshot`
- ✅ AI-powered Q&A with `/ask`
- ✅ Stock comparison with `/compare`
- ✅ Pre-market briefing with `/premarket`
- ✅ Market selection for ambiguous tickers
- ✅ Watchlist management
- ✅ Risk profile customization
- ✅ Sector rotation analysis
- ✅ Alpha discovery

### Bug Fixes
- ✅ Fixed market selection infinite loop
- ✅ Fixed NoneType errors in `/ask`
- ✅ Fixed "too many values to unpack" in `/premarket`
- ✅ Fixed all command handlers to return tuples consistently
- ✅ Fixed duplicate responses (local + Railway bot conflict)
- ✅ Made matplotlib optional for faster deployment
- ✅ Fixed 14 commands using incorrect send_message method

### Known Issues
- ⚠️ `/chart` command disabled (matplotlib removed for faster deployment)

### Deployment
- **Platform:** Railway (wonderful-insight project)
- **Environment:** Production
- **Build Time:** ~2-3 minutes
- **Commit:** 1d08d6f
