# Verification record

2026-11-25, development environment Python 3.14.5:

- `python3 -m unittest discover -s tests -v`: 12 tests passed. The HTTP contract test uses a real ephemeral loopback server; the local sandbox required loopback permission.
- Offline CLI agent, Q&A with `returns`, and Q&A with `volcanoes` passed, visibly labelled `OFFLINE FIXTURE`.
- Tests were written before their corresponding implementations. Initial runs failed for missing modules/unimplemented behaviors, then passed after implementation.
- Basic credential-pattern scan found no private keys, GitHub tokens, AWS access-key identifiers or OpenAI-style secrets. The repository was authored independently from the approved public starter requirements; no private course files were copied.
- Live Ollama inference **not verified**: no `ollama` executable was found; `http://127.0.0.1:11434/api/tags` refused the connection; Docker inspection found no containers from `ollama/ollama`, including stopped containers. No runtime/model was installed or downloaded.
- Official API and model references were checked at https://docs.ollama.com/api/chat and https://ollama.com/library/qwen3 .

Offline fixtures validate orchestration and failure handling only, not model quality. CI targets Python 3.12.12 and 3.13; that matrix has not been run locally. Citation validation checks permitted identifiers, not semantic entailment. Workflow files assume a trusted, single-user local workspace and do not provide concurrency/crash-transaction guarantees.

Review follow-up: adversarial HTTP tests reproduced trickled-header and Connection: close body deadline overruns (about 0.40 s and 0.18 s against a 0.10 s budget). A deadline-aware socket now recalculates the remaining time for connect, sendall and every recv_into, including HTTP header parsing and response-owned sockets. Both tests and the complete 12-test suite pass. No client worker thread is used; sockets/responses close in finally.
