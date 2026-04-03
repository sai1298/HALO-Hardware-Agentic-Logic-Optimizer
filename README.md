# 🚀 Agentic High-Level Synthesis (HLS) Optimization Framework

An autonomous AI-driven **High-Level Synthesis (HLS) optimization pipeline** that transforms standard C/C++ code into highly optimized hardware-ready implementations using **LangGraph-based agent orchestration** and iterative synthesis feedback loops with the **Bambu HLS compiler**.

---

## 🖼️ System Workflow

> Add your workflow image here

![HLS Workflow](./assets/workflow.png)

---

## 🔥 Key Idea

This system automatically converts unoptimized C code into optimized RTL-ready hardware by:

- Injecting correct `#pragma HLS` directives
- Running synthesis using Bambu HLS
- Detecting compiler/synthesis errors
- Iteratively fixing issues using an LLM agent
- Validating final output using simulation
- Reporting performance improvements

---

## 🧠 Architecture Overview

Input C Code  
→ Load File Node  
→ LLM Pragma Injection Node  
→ Agentic Synthesis Loop (ReAct Agent)  
→ Bambu HLS Compiler Execution  
→ Error Feedback Loop (LLM Fixes)  
→ Simulation Node  
→ Final Optimized RTL Output  

---

## ⚙️ LangGraph Workflow

load_file → add_pragma → synthesis_agent → run_simulation

Each node performs:

- load_file_node → Reads C source code  
- add_pragma_llm_node → Injects HLS pragmas  
- synthesis_agent_node → Iterative compile + fix loop  
- run_simulation_node → RTL validation  

---

## 🤖 Agentic Synthesis Loop

Generate Code → Compile (Bambu) → Error? → Fix Code → Retry → Success

Key constraints:

- No `#pragma HLS pipeline`
- Strict pragma placement rules
- Label-aware loop handling
- Automatic retry limit enforcement

---

## ⚙️ Core System Design

### 🧠 LLM Engine
- Gemini via LangChain
- Generates HLS-aware optimized C code

### 🔁 LangGraph Orchestration
- Controls execution flow
- Manages state transitions and retries

### ⚙️ Bambu HLS Compiler
- Synthesizes hardware from C code
- Returns compilation/synthesis feedback

### 🧪 Simulation Node
- Validates final RTL behavior using testbench
- Ensures correctness before completion

---

## 📊 Performance Results (AES Benchmark)

| Metric | Unoptimized | Optimized | Improvement |
|------|------------|-----------|-------------|
| Execution Cycles | 1477 | 331 | ~77% faster |
| Max Frequency | 112 MHz | 255 MHz | ~128% increase |
| Memory Usage | 1536 B | 256 B | ~83% reduction |
| Functions | 2 | 1 | Inlining applied |
| Flip-Flops | 5,158 | 12,310 | Higher parallelism |
| Registers | 284 | 1,018 | Increased hardware concurrency |
| Multiplexers | 233 | 566 | More parallel datapaths |
| Area Usage | Low | High | Trade-off for performance |

---

## ⚖️ Key Insight

This system replaces manual RTL tuning with an **autonomous AI-driven synthesis loop**, enabling:

- Faster hardware iteration cycles
- Automatic pragma optimization
- Reduced debugging effort
- Significant performance gains

---

## 🧩 Agent Capabilities

The autonomous agent can:

- Detect compilation errors
- Fix pragma placement issues
- Correct HLS constraint violations
- Retry synthesis automatically
- Stop only on successful hardware generation

---

## 🚀 Future Enhancements

- Multi-objective optimization (latency / area / power)
- Reinforcement learning for pragma selection
- Multi-kernel hardware pipelines
- Verilog/VHDL backend generation
- Distributed synthesis across cloud nodes

---

## 🏁 Conclusion

This project demonstrates an **agentic hardware design system** that integrates:

- Large Language Models (LLMs)
- Compiler-in-the-loop optimization
- Hardware synthesis feedback
- Automated RTL validation

It bridges the gap between high-level programming and efficient hardware design, dramatically reducing manual HLS effort while improving performance outcomes.
