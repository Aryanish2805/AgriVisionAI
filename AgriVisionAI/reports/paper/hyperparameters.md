# Hyperparameter Configuration

The following table (Table IV in the manuscript) details the exact hyperparameter selections utilized across the Deep Learning architectural evaluations. Values were determined through a mix of default heuristic testing and localized grid-search epochs.

| Architecture | Parameter Space | Value Selected | Justification / Context |
|---|---|---|---|
| **MLP (DNN)** | Hidden Layers | (128, 64, 32) | Captures highly non-linear environmental mappings. |
|  | Activation | ReLU | Prevents vanishing gradients in deeper layers. |
|  | Optimizer / LR | Adam (Default) | Adaptive momentum suitable for generalized tabular data. |
|  | Epochs | 500 (Max) | Early stopping configured if convergence stabilizes. |
| **TabNet** | Optimizer | Adam | Industry standard for TabNet integrations. |
|  | Learning Rate (LR) | `2e-2` | Aggressive LR due to `StepLR` scheduling. |
|  | Scheduler | StepLR | `step_size=50`, `gamma=0.9` ensures fine boundary convergence. |
|  | Batch Sizing | Batch: 256, Virtual: 128 | Balances GPU memory handling with batch normalization stability. |
| **FT-Transformer** | Embedding Dim (`d_token`) | 192 | Sufficient capacity for NPK/Weather token translations. |
|  | Network Depth | 3 Blocks | Standard for $<10,000$ sample tabular datasets. |
|  | Dropout | 0.1 | Minimal dropout selected given the dataset density. |
|  | Optimizer | AdamW | Integrated weight-decay outperforms Adam for Transformer blocks. |
|  | Learning Rate | `1e-4` | Prevents shattering gradient matrices on small batch sets. |
