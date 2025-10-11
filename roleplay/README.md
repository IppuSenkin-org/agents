# Roleplay Agent

超シンプルな音声会話エージェント（OpenAI Realtime API使用）

## 必要な環境変数

`.env` ファイル（ルートディレクトリにシンボリックリンク済み）:
```bash
LIVEKIT_URL=ws://172.17.0.1:7880
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=sk-...
```

## 実行方法

### Dockerで実行（推奨）

```bash
cd /home/ubuntu/ai-roleplay-exp/agents/roleplay
docker-compose up --build
```

### ローカルで実行

```bash
cd /home/ubuntu/ai-roleplay-exp
uv run agents/roleplay/agent_worker.py dev
```

## フロントエンドとの接続

このエージェントは `roleplay-agent` という名前で登録されています。

フロントエンド (`agent-starter-react/app-config.ts`) で以下のように指定:
```typescript
agentName: 'roleplay-agent',
```

エージェント名を変更する場合は、`agent_worker.py:24` の `agent_name` も合わせて変更してください。

## カスタマイズ

`agent_worker.py:16` の `instructions` を変更:
```python
instructions="あなたは〇〇です。..."
```
