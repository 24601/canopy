# Setting Up API Keys and Secrets

This guide explains how to configure API keys for MassGen both locally and in GitHub Actions.

## Required API Keys

MassGen supports multiple AI providers. You'll need at least one of the following:

- **OpenRouter API Key**: For accessing multiple models through a single API
- **OpenAI API Key**: For GPT models
- **Anthropic API Key**: For Claude models
- **Google Gemini API Key**: For Gemini models
- **XAI API Key**: For Grok models

## Local Development Setup

### Using Environment Variables

1. Create a `.env` file in your project root:

```bash
cp .env.example .env
```

2. Add your API keys to the `.env` file:

```bash
# OpenRouter (recommended for multi-model access)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Individual providers (optional)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
XAI_API_KEY=your_xai_api_key_here
```

3. The application will automatically load these from the environment.

### Using Configuration Files

Alternatively, you can set API keys in your configuration YAML:

```yaml
agents:
  - name: "Agent1"
    backend: "openrouter"
    model_config:
      api_key: ${OPENROUTER_API_KEY}  # Uses env var
      # Or directly (not recommended):
      # api_key: "your_api_key_here"
```

## GitHub Actions Setup

To run tests and CI/CD pipelines, you need to configure secrets in your GitHub repository.

### Adding Secrets to GitHub

1. Go to your repository on GitHub
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Description |
|-------------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENAI_API_KEY` | Your OpenAI API key (optional) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (optional) |
| `GEMINI_API_KEY` | Your Google Gemini API key (optional) |
| `XAI_API_KEY` | Your XAI API key (optional) |

### Using Secrets in Workflows

The secrets are automatically available in GitHub Actions workflows:

```yaml
env:
  OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## OpenRouter Configuration

OpenRouter provides access to multiple AI models through a single API. This is the recommended approach for flexibility.

### Getting an OpenRouter API Key

1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Go to your [API Keys page](https://openrouter.ai/keys)
3. Create a new API key
4. Copy the key and add it to your environment

### Configuring OpenRouter Models

In your `config_openrouter.yaml`:

```yaml
agents:
  - name: "GPT-4 Agent"
    backend: "openrouter"
    model_config:
      model: "openai/gpt-4-turbo"
      api_key: ${OPENROUTER_API_KEY}

  - name: "Claude Agent"
    backend: "openrouter"
    model_config:
      model: "anthropic/claude-3-opus"
      api_key: ${OPENROUTER_API_KEY}

  - name: "Gemini Agent"
    backend: "openrouter"
    model_config:
      model: "google/gemini-pro"
      api_key: ${OPENROUTER_API_KEY}
```

### Available Models on OpenRouter

OpenRouter supports a wide range of models. Some popular options:

- **OpenAI**: `openai/gpt-4-turbo`, `openai/gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- **Google**: `google/gemini-pro`, `google/gemini-pro-vision`
- **Meta**: `meta-llama/llama-3-70b-instruct`
- **Mistral**: `mistralai/mixtral-8x7b-instruct`

See the full list at [openrouter.ai/models](https://openrouter.ai/models)

## Security Best Practices

1. **Never commit API keys**: Always use environment variables or secrets
2. **Use `.gitignore`**: Ensure `.env` files are in your `.gitignore`
3. **Rotate keys regularly**: Change your API keys periodically
4. **Use minimal permissions**: Only grant the permissions needed
5. **Monitor usage**: Check your API usage regularly for anomalies

## Troubleshooting

### API Key Not Found

If you get an error about missing API keys:

1. Check that your `.env` file exists and contains the keys
2. Ensure the environment variables are exported:
   ```bash
   export OPENROUTER_API_KEY="your_key_here"
   ```
3. Verify the key names match exactly (case-sensitive)

### Permission Denied

If you get permission errors:

1. Check that your API key has the necessary permissions
2. Verify your account has sufficient credits/quota
3. Ensure you're using the correct API endpoint

### Rate Limiting

If you encounter rate limits:

1. Add delays between requests
2. Use the `max_concurrent_agents` setting to limit parallelism
3. Consider upgrading your API plan

## Example: Complete Setup

Here's a complete example of setting up MassGen with OpenRouter:

1. **Get your API key** from [openrouter.ai](https://openrouter.ai)

2. **Create `.env` file**:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

3. **Create `config.yaml`**:
   ```yaml
   algorithm: "massgen"
   max_concurrent_agents: 3

   agents:
     - name: "Fast Thinker"
       backend: "openrouter"
       model_config:
         model: "openai/gpt-3.5-turbo"
         temperature: 0.7

     - name: "Deep Thinker"
       backend: "openrouter"
       model_config:
         model: "anthropic/claude-3-opus"
         temperature: 0.5

     - name: "Creative Thinker"
       backend: "openrouter"
       model_config:
         model: "google/gemini-pro"
         temperature: 0.9
   ```

4. **Run MassGen**:
   ```bash
   python -m massgen.main --config config.yaml "Your question here"
   ```
