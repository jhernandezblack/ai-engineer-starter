# AI Engineer Starter

[Español](README.md) · [English](README.en.md)

Three small original Python templates for tool use, human control, and answers with sources. MIT code by BlackBox Big Data; no private course solutions.

| Template | Learn | Learning path connection |
|---|---|---|
| `agent` | Bounded loop, allowlisted `stock` tool, argument validation | First agents and Python |
| `workflow` | Persistent draft, pause, explicit human approval | Foundations of stateful workflows |
| `qa` | Lexical retrieval, permitted citations, abstention | Foundations of document Q&A |

These standard-library examples do not implement LangGraph, embeddings, or GraphRAG. The free course may use Claude/API providers; this repository offers a separate local Ollama runtime.

## Reproducible start without a model

Requires Python 3.12+ (pinned reference: 3.12.12). No pip dependencies, API account, or credentials.

```sh
git clone https://github.com/jhernandezblack/ai-engineer-starter.git
cd ai-engineer-starter
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m starter agent --offline --lang en
python -m starter qa --offline --question returns --lang en
python -m starter qa --offline --question volcanoes --lang en
```

`--offline` prints `OFFLINE FIXTURE` to stderr. It supplies fixed responses: **no model inference runs and no model quality is demonstrated**. The agent checks notebook stock and answers 12; Q&A cites `[policy.txt]`. A question with no matching words returns `abstained: true`. Fixture phrases are bilingual to make their nature visible.

## Human approval and resumption

```sh
python -m starter workflow --offline --workspace output/case-1 --question 'Acknowledge a support request' --lang en
cat output/case-1/state.json
python -m starter workflow --workspace output/case-1 --decision APPROVE --lang en
cat output/case-1/reply.txt
```

Review `draft` first. Only `APPROVE` creates `reply.txt`; `REJECT` closes the case without writing it. The second command loads saved state without calling a model. Use a fresh folder for each case; existing drafts and replies cannot be overwritten. The effect saves a local sample and never sends email. Keep the folder private: the state file is trusted local state, not a multiuser authorization boundary. Do not run concurrent decisions for one case.

## Run a real local model

Install [Ollama](https://ollama.com/download), start its service, then explicitly download a model:

```sh
ollama serve  # only if the application has not started the service already
ollama pull qwen3:4b
python -m starter agent --model qwen3:4b --question 'Check notebook stock' --lang en
python -m starter workflow --model qwen3:4b --workspace output/real-case --question 'A customer asks about an order' --lang en
python -m starter qa --model qwen3:4b --question 'How many days for returns?' --lang en
```

We use `POST /api/chat`, JSON output, and `stream:false` from the [official API](https://docs.ollama.com/api/chat). [qwen3:4b](https://ollama.com/library/qwen3:4b) is an option with an approximately 2.5 GB download; runtime memory and context need additional capacity. Reserve several GB of free memory and choose a smaller model if needed. Model tags may change: record `ollama list` for reproducibility. Model licenses and terms are separate from this code's MIT license. Nothing is downloaded automatically.

The total HTTP deadline covers connect, send, headers and body, including slowly trickled responses. Generation allows 30 seconds per call, up to 512 output tokens and 64 KiB per HTTP response. The agent allows four steps and 30 seconds overall. On slower hardware, preload with `ollama run qwen3:4b`; examples fail visibly rather than raising their own limits. Connections are restricted to `127.0.0.1:11434`, with no keys required.

## Limits and troubleshooting

- Connection refused: start Ollama. Missing model: explicitly run `ollama pull`. Invalid JSON or timeout: try another local model or preload it; an offline fixture is not evidence that the model works.
- Invalid tools and arguments are rejected. There is no shell execution, generated code execution, or arbitrary network request tool.
- Q&A matches shared words across up to three texts in `data/`; it is not semantic search. Rephrase using document terms. Retrieval may find irrelevant evidence.
- Citations must identify retrieved documents and appear in the answer. This validates structural provenance, **not factual support for every claim**. Read the cited text: a model can hallucinate despite a valid citation. Abstention covers no lexical matches and invalid answers/citations.
- Documents and model tool requests are untrusted data. Do not add sensitive files. These bounds do not replace operating-system isolation for untrusted code.
- Tests are deterministic and download no models. One test starts an ephemeral loopback HTTP server; sandboxes must permit loopback.

## Next step

[Explore the AI Engineer path and start free](https://blackboxbigdata.com/en/ruta-ai-engineer?utm_source=github&utm_medium=referral&utm_campaign=ruta-ai-engineer&utm_content=readme_en). The first course has free enrollment; external providers used in the course may charge for usage. The full bundle is coming soon on the website.
