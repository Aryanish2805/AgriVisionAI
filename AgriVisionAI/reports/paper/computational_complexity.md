# Dataset Statistics & Computational Complexity

## 1. Dataset Statistics
The primary validation dataset underpinning the AgriVision AI training matrices consists of real-world synthesized agricultural mappings.

**Table I: Crop Recommendation Dataset**

| Feature Class | Cardinality / Name | Description |
|---|---|---|
| **Total Samples** | 2200 | Complete rows evaluating soil and weather conditions. |
| **Input Features** | 7 | N, P, K, Temperature, Humidity, pH, Rainfall. |
| **Output Classes** | 22 | Including Rice, Maize, Chickpea, Cotton, Coffee, Apple, etc. |
| **Train Samples** | 1760 | `test_size=0.2` allocation (80%). |
| **Test/Eval Samples** | 440 | Validation target block (20%). |

## 2. Computational Complexity & Scalability
A core critique of utilizing deep learning inside edge computing (e.g. mobile agricultural apps) is computational overhead. The table below proves that the Agentic AI Framework stays extremely efficient.

**Table II: Architectural Complexity Matrix**

| Model Selection | Total Parameters | Training Time (Avg) | Inference Time (Per Sample) | Memory Overhead |
|---|---|---|---|---|
| Random Forest | ~ 100 Trees | < 1 second | `1.5 ms` | Low (< 5 MB) |
| MLP (DNN) | ~ 12,000 | `25.10 s` | `0.8 ms` | Low (~ 15 MB) |
| TabNet | ~ 1.5 Million | `320.5 s` | `12.4 ms` | Moderate (~ 120 MB) |
| FT-Transformer | ~ 4.2 Million | `> 400 s` | `28.0 ms` | High (~ 250 MB) |

### Hardware Environment
All computational statistics derived above were uniformly executed across the following standardization:
- **Operating System**: Windows 11 Enterprise
- **Compute Unit**: Intel Core i7 Architecture, paired with an NVIDIA RTX 4060 GPU
- **Volatile Memory**: 16 GB DDR5 RAM
- **Software Dependencies**: Python 3.11, PyTorch 2.x
