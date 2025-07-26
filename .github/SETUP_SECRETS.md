# GitHub Actions Secret Setup

This document explains how to set up the required secrets for GitHub Actions.

## Required Secrets

### API Keys (for Integration Tests)

These secrets are optional but recommended for running integration tests:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GROK_API_KEY`: Your Grok/X.AI API key

### Code Coverage (Optional)

- `CODECOV_TOKEN`: Token for uploading coverage reports to Codecov

## How to Add Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with its name and value

## Security Best Practices

1. **Never commit secrets to the repository**
2. **Use minimal permissions** - Only grant the minimum required access
3. **Rotate secrets regularly** - Update API keys periodically
4. **Monitor usage** - Check your API usage dashboards regularly
5. **Use environment-specific keys** - Don't use production keys for testing

## Local Development

For local development, create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GROK_API_KEY=your_key_here
```

Make sure `.env` is in your `.gitignore` (it already is).

## GitHub Actions Security

The workflows are configured with minimal permissions:
- Most jobs only have `contents: read`
- Only the release workflow has `contents: write`
- No workflows have access to other permissions unless explicitly needed

## Monitoring

You can monitor secret usage in:
- GitHub Settings → Secrets → "Repository secrets" (shows last used)
- Your API provider dashboards (OpenAI, Google Cloud, X.AI)
- GitHub Actions logs (secrets are masked automatically)
