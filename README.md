# Temporal-Based Workflow & Agent System


## Overview

This project implements a **stateful job orchestration system** using Temporal.

In many event-driven systems (e.g., Kafka-based pipelines), failed tasks often require
reprocessing from the beginning, leading to inefficiency and increased operational cost.

To address this, this system introduces:

- Stateful workflow execution
- Step-level retry and recovery
- Long-running job orchestration

Additionally, it includes a **fault-tolerant ReAct agent system**, where each reasoning step
is persisted and recoverable.

👉 The goal is to demonstrate how Temporal can be used to build
reliable backend systems beyond stateless task queues.

---

## Key Features

### 1. Job Processing System

- Queue-based job submission
- Sequential execution with batching (no parallel processing)
- Rate limiting (100 items per 10 seconds)
- Stateful execution using Temporal (no external DB)
- Runtime control via signals: pause, resume, discard

👉 Designed to simulate real-world constraints such as:
- rate-limited external APIs
- legacy systems with low throughput



### 2. Agent System (ReAct-based)

* LLM-driven reasoning loop (ReAct pattern)
* Tool calling (web search)
* Observation-based iterative reasoning
* Max step limit to prevent infinite loops

👉 Implemented **without LangChain**, directly on Temporal




### 3. Fault Tolerance

* Workflow state persisted by Temporal
* Activity-level retry & recovery
* Execution resumes after worker restart

👉 Ensures reliability for **long-running AI workflows**

---

## Architecture


<p align="center">
  <img src="./api/img/architecture.png" width="600"/>
</p>
<p align="center"><i>System Architecture Overview</i></p>

- FastAPI acts as the entry point
- Temporal orchestrates workflows
- Job workflow handles rate-limited processing
- Agent workflow implements a ReAct-based reasoning loop



## System Design

### Job Workflow

- Maintains internal queue
- Processes jobs in chunks
- Enforces strict rate limiting
- Fully controlled via workflow signals

👉 Designed to handle long-running jobs with constrained resources

### Agent Workflow

* Implements ReAct loop inside workflow
* Each step (LLM / Tool) is an Activity
* Conversation state stored in workflow
* Fault-tolerant execution across steps

---

## Why Temporal?

Traditional task queues (e.g., Kafka consumers, cron jobs) typically:

- Do not preserve execution state
- Require full retries on failure
- Lack fine-grained control over long-running tasks

Temporal solves these problems by providing:

- Durable execution (state persisted automatically)
- Step-level retry (resume from failure point)
- Built-in workflow orchestration
- Signal-based runtime control

👉 This makes it suitable for:
- long-running job processing
- workflow-based systems
- AI agent pipelines

---

## Prompt Design

* Prompt is externalized (`/api/prompts`)
* Injected into workflow input for deterministic execution
* Designed to:

  * enforce tool usage
  * reduce hallucination
  * encourage structured output

---

## Tech Stack

* Python
* FastAPI
* Temporal
* OpenRouter (LLM)
* Firecrawl (Web Search)
* Docker Compose

---

## How to Run

```
docker-compose up --build
```

Access:

* API Docs: http://localhost:8000/docs
* Temporal UI: http://localhost:8080

---

## API

### Job System

- POST /jobs
- POST /jobs/pause
- POST /jobs/resume
- GET  /jobs/status
- POST /jobs/discard

Example:

```
curl -X POST "http://localhost:8000/jobs" \
-H "Content-Type: application/json" \
-d '{"title": "report_job", "count": 500}'
```



### Agent System

* POST /agents/crawler

Example:

```
curl -X POST "http://localhost:8000/agents/crawler" \
-H "Content-Type: application/json" \
-d '{"input": "Get company info of OpenAI"}'
```

---

## Fault Tolerance Test

1. Send request
2. Stop worker
3. Restart worker

Result:

* Workflow paused safely
* State persisted
* Execution resumed from exact step

---

## Limitations

* No external persistence beyond Temporal
* Agent output may not always be perfectly structured
* Depends on external APIs (LLM, search)

---

## Key Takeaways

- Designed a stateful job orchestration system using Temporal
- Implemented rate-limited batch processing without external DB
- Built a fault-tolerant ReAct agent system using workflow-based execution
- Demonstrated how workflow engines can overcome limitations of stateless task queues

---

## Future Improvements

* Streaming agent steps
* Better output validation
* Additional tools (beyond web search)
