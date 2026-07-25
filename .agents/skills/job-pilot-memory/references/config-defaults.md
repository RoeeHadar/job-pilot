# Memory config defaults

```yaml
# memory/config.yml
recency_decay_days: 45
min_confidence_to_persist: 0.55
recall_top_k: 12
embed:
  provider: user-configured  # never use a bundled free key
  model: null
llm:
  provider: user-configured
  model: null
market_scope: israel  # IL + remote-for-IL only
languages: [he, en]
```
