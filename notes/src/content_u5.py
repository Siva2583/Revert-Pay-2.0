# -*- coding: utf-8 -*-
"""Unit V — Recurrent networks, LSTM, sequence-to-sequence and autoencoders."""

UNIT_INFO = {
    'unit': 5,
    'roman': 'V',
    'label': 'UNIT V',
    'title': 'Recurrent Networks and Autoencoders',
    'subtitle': 'Unrolling over time, the vanishing gradient, gated memory, sequence '
                'transduction and learned representations',
}

GLANCE = [
    (1, "An unfolded simple RNN and parameter sharing over time",
     "One cell reused at every step: the same recurrent matrix appears everywhere, "
     "which is both the point and the problem."),
    (2, "Vanishing and exploding gradients, and why the LSTM helps",
     "The Jacobian is a product of many matrices; gates replace that product by an "
     "elementwise one."),
    (3, "Standard, bidirectional, deep RNN and LSTM compared",
     "Four answers to 'which recurrence?', differing in direction, depth and state "
     "update."),
    (4, "LSTM gates and the cell state",
     "Forget, input and output gates acting on a conveyor-belt state."),
    (5, "A strategy for long sequences where a simple RNN fails",
     "Clip, truncate, gate, restructure, then attend — in that order."),
    (6, "Encoder–decoder sequence-to-sequence design and its training objective",
     "The decoder factorises the target distribution autoregressively, conditioned on "
     "the context vector."),
    (7, "An autoencoder for dimensionality reduction",
     "A bottleneck plus a reconstruction loss; a linear autoencoder spans the PCA "
     "subspace."),
    (8, "Autoencoders and representation learning",
     "Denoising, sparse and contractive variants learn features that transfer."),
]

REVISION = [
    (1, "Unrolling replaces the loop by repeated copies of one cell with tied weights, "
        "so parameters are constant in the length but the graph has depth $T$.",
     "Forgetting that the same weights are used at every step — that is the whole "
        "reason backpropagation through time accumulates into one matrix."),
    (2, "The gradient contains a product of $T$ Jacobians; its norm shrinks or grows "
        "geometrically with the distance.",
     "Saying the LSTM 'removes' the product — it replaces the repeated matrix by a "
        "diagonal gate path, which is not the same thing."),
    (3, "Bidirectional doubles the parameters and needs the whole sequence; depth "
        "stacks layers; the LSTM changes the cell, not the topology.",
     "Confusing 'deep' with 'long': depth is over layers, length is over time."),
    (4, "The forget gate acts on the cell line, the input gate writes, the output gate "
        "exposes a squashed copy of the state.",
     "Forgetting that the cell state is not the hidden output; the output gate is what "
        "separates them."),
    (5, "Truncated backpropagation, clipping, gating, restructuring, attention — in "
        "that order of cost.",
     "Training on sequences longer than memory allows without truncation."),
    (6, "The decoder factorises the joint probability autoregressively, conditioned on "
        "the context vector.",
     "Training with the model's own predictions instead of teacher forcing, then "
        "wondering why it diverges."),
    (7, "A bottleneck forces compression; without a bottleneck the network learns the "
        "identity.",
     "Claiming an autoencoder is 'the same as' PCA in general — only the linear, "
        "squared-error case coincides."),
    (8, "Tie the encoder to a downstream task, or use denoising to force useful "
        "features.",
     "Assuming any autoencoder produces transferable features; an over-complete one "
        "often memorises."),
]

SCRIPTS = {}

SCRIPTS[1] = r"""
#A 1::Draw a simple RNN unfolded over time and explain parameter sharing across the time steps::CO5 · Understand–Apply · 10 marks · ~2.5 pages::Unfolded simple RNN and parameter sharing
## The recurrence
A simple (Elman) recurrent network processes a sequence one element at a time, carrying a hidden state:
@@ h_{t}=\tanh\left(W_{xh}x_{t}+W_{hh}h_{t-1}+b_{h}\right)
@@ y_{t}=\mathrm{softmax}\left(W_{hy}h_{t}+b_{y}\right)
The state is a fixed-length summary of everything seen up to time $t$; the output is computed from that summary. The same three matrices are used at every step — that is the definition of a recurrent layer, and everything else follows from it.
## Unfolding
"Unfolding" means drawing the computation graph for all $T$ steps explicitly. The cycle from one state to the next becomes a chain of copies of the same cell, each with its own input and output, and with the weights **tied** across the copies:
@fig fig5_unfold||The same cell drawn three times; the input, recurrent and output weight matrices are shared, and the state is the only thing that passes between copies.
The unfolded graph is a feedforward network of depth equal to the sequence length, whose layers happen to share parameters. This is why a recurrent network can be trained by ordinary backpropagation: there is no new algorithm, only a new graph.
## Parameter sharing
Write the parameter set as the three weight matrices and two bias vectors, with sizes
@@ |W_{xh}|=d_{x}d_{h},\qquad |W_{hh}|=d_{h}^{2},\qquad |W_{hy}|=d_{h}d_{y}
so the total is fixed by the hidden width and the vocabulary, and **independent of the sequence length**. Four consequences, all examinable:
+ **A variable-length input is handled by one model.** A sequence of 10 or 10,000 steps uses the same weights; there is no need to change the architecture, only the batch.
+ **Statistical strength.** Every time step is a training example for the same transition function, exactly as every image position is a training example for a shared filter. This is weight sharing in time, and it is why recurrent models generalise across lengths.
+ **Constant memory.** The model size does not grow with the sequence, unlike a dense model over a fixed window of $T$ steps, whose parameter count grows linearly in $T$.
+ **The Markov assumption is replaced by a learned state.** The state is not a fixed window; it is a learned compression of the past, refreshed at every step.
## Backpropagation through time
The loss sums over time, and the gradient with respect to the shared weights is the sum of the contributions from every step:
@@ \frac{\partial L}{\partial W_{hh}}=\sum_{t=1}^{T}\frac{\partial L_{t}}{\partial W_{hh}},\qquad \frac{\partial L_{t}}{\partial h_{k}}=\frac{\partial L_{t}}{\partial h_{t}}\prod_{i=k+1}^{t}\frac{\partial h_{i}}{\partial h_{i-1}}
@@ \frac{\partial h_{i}}{\partial h_{i-1}}=\mathrm{diag}\left(1-h_{i}^{2}\right)W_{hh}
So backpropagation through time is ordinary backpropagation on the unfolded graph, accumulating into a single gradient for the tied weights. The product in the second equation is the origin of the vanishing-gradient problem of the next answer: it is a product of many matrices, and products of matrices either shrink or blow up.
@box note||Why the state matters
The hidden state plays the role of a program's memory. The difference from an n-gram model is that the state is continuous and learned, so the model can represent unbounded dependencies in principle — though in practice the gradient decay described next bounds what a simple recurrent net can learn.
@end
@key Unfolding turns a loop into a chain of identical cells with tied weights, so the parameter count is fixed regardless of sequence length, and training is ordinary backpropagation on that chain — with gradients accumulated over all time steps.
@box ok||Examiner's checklist
- Draws the folded cell and the unfolded chain, labelling the shared matrices.
- Writes the state and output equations.
- States that the parameter count is independent of the length, with the sizes.
- Explains why unfolding allows ordinary backpropagation.
- Writes the gradient through time as a product of Jacobians.
@end
@kw recurrence; hidden state; unfolding; weight tying; backpropagation through time; parameter sharing in time; variable-length input; Jacobian product
"""

SCRIPTS[2] = r"""
#A 2::Explain the vanishing and exploding gradient problem and how the LSTM mitigates it::CO5 · Understand–Analyse · 10 marks · ~3 pages::Vanishing and exploding gradients
## The product that causes it
From backpropagation through time, the gradient of the loss at a late step with respect to an early state is a product of Jacobians:
@@ \frac{\partial L_{t}}{\partial h_{k}}=\frac{\partial L_{t}}{\partial h_{t}}\prod_{i=k+1}^{t}\mathrm{diag}\left(1-h_{i}^{2}\right)W_{hh}
Taking norms and using submultiplicativity,
@@ \left\|\frac{\partial L_{t}}{\partial h_{k}}\right\|\leq\left\|\frac{\partial L_{t}}{\partial h_{t}}\right\|\prod_{i=k+1}^{t}\left\|\mathrm{diag}\left(1-h_{i}^{2}\right)\right\|\left\|W_{hh}\right\|\leq C\,\gamma^{\,t-k}
where the base $\gamma$ is the product of the largest derivative of the squashing function and the spectral norm of the recurrent matrix, and the derivative of the tanh is at most one. The bound is geometric in the distance between the two steps, and that is the whole story:
- if the base is below one the gradient **vanishes** exponentially, so the network cannot learn dependencies longer than roughly the reciprocal of the decay;
- if the base is above one the gradient **explodes** exponentially, so the update overshoots and the loss becomes not-a-number.
@fig fig5_vanish||Gradient magnitude against separation in time. The vanilla recurrence decays geometrically; the LSTM path with a forget gate near 1 is almost flat.
## The vanishing case, in words
The chain rule multiplies a factor smaller than one at every step. After 50 steps a per-step factor of $0.9$ leaves only about $0.005$ of the original signal; after 100 steps, about $2\times10^{-5}$. The consequence is not merely slow learning: the parameters that would capture a long-range dependency receive no gradient at all, so the model *cannot* represent the dependency. This is why a simple recurrent network appears to work on short sequences and fails on long ones.
## The exploding case
The same product with a base above one makes the gradient huge, and a single large step can destroy the weights. The standard remedy is simple and effective — **gradient clipping**:
@@ g\leftarrow g\cdot\min\left(1,\frac{c}{\|g\|}\right)
with the threshold $c$ typically between one and five. It bounds the step without changing its direction. Clipping fixes exploding gradients; it cannot fix vanishing ones, because scaling a tiny gradient up amplifies noise.
## Why the LSTM helps
The LSTM adds a cell state with an almost additive update:
@@ c_{t}=f_{t}\odot c_{t-1}+i_{t}\odot g_{t}
Differentiating with respect to the previous state,
@@ \frac{\partial c_{t}}{\partial c_{t-1}}=\mathrm{diag}\left(f_{t}\right)+\text{terms through the gates}
and when the forget gate is near one, this Jacobian is close to the identity. The crucial difference from the simple recurrence is structural: the path from one cell state back to an earlier one is a product of **diagonal** matrices, not a product of the same dense matrix. A product of diagonal matrices is just an elementwise product of scalars, so
@@ \frac{\partial c_{t}}{\partial c_{k}}=\prod_{i=k+1}^{t}\mathrm{diag}\left(f_{i}\right)
has no repeated mixing of directions: each cell of the state can carry its own memory with its own decay rate. A cell whose forget gate learns to sit at $0.99$ has an effective memory of about a hundred steps; one at $0.5$ has a memory of two steps. The network therefore *learns per-channel time constants* rather than being forced into a single global one.
Two further details complete the answer:
+ **The forget gate bias is initialised to one** (or a positive constant), so that at the start of training the gates are open and the gradient flows; the model then learns to close them.
+ **The gates are sigmoids**, so the forget values lie between zero and one and the product cannot explode by itself; exploding gradients in an LSTM come from the input path, which is why clipping is still used.
@box warn||The precise claim
The LSTM does not abolish the product of Jacobians; it replaces a product of dense mixing matrices by a product of diagonal gates, and it lets the network choose gate values near one. That is the sentence that distinguishes a correct answer from a slogan.
@end
@key A dependency across many steps passes through as many Jacobians, so the gradient scales geometrically; the LSTM replaces the repeated dense product by a diagonal gate product on an additive cell-state path, giving each channel its own learnable time constant, and clipping handles the exploding case.
@box ok||Examiner's checklist
- Writes the Jacobian product and derives the geometric bound.
- Distinguishes vanishing (cannot learn) from exploding (unstable).
- Gives gradient clipping as the remedy for one and explains why it cannot fix the other.
- Shows the additive cell-state update and its diagonal Jacobian.
- Mentions the forget-gate bias initialisation and that clipping is still used.
@end
@kw backpropagation through time; Jacobian product; spectral norm; vanishing gradient; exploding gradient; gradient clipping; cell state; forget gate; diagonal Jacobian; time constant
"""

SCRIPTS[3] = r"""
#A 3::Compare standard, bidirectional, deep and LSTM recurrent networks::CO5 · Understand–Analyse · 10 marks · ~2.5 pages::Standard vs bidirectional vs deep RNN vs LSTM
## Standard recurrent network
@@ h_{t}=\tanh\left(W_{xh}x_{t}+W_{hh}h_{t-1}+b\right)
One direction, one layer, one state. The parameter count is quadratic in the hidden width, the memory is constant per step, and the geometric gradient decay of the previous answer applies. It is the reference point against which the other three are described.
## Bidirectional recurrent network
Run two independent recurrences, one left-to-right and one right-to-left, and concatenate their states at every step:
@@ \overrightarrow{h}_{t}=f\left(x_{t},\overrightarrow{h}_{t-1}\right),\qquad \overleftarrow{h}_{t}=f\left(x_{t},\overleftarrow{h}_{t+1}\right)
@@ h_{t}=\left[\overrightarrow{h}_{t};\overleftarrow{h}_{t}\right]
The representation at each step now depends on the whole sequence, not only on the past, which is exactly right for tasks where the answer is available at once: part-of-speech tagging, named-entity recognition, speech recognition over a completed utterance. The costs are that parameters double, that the entire sequence must be available before the first output (so it cannot be used in streaming or causal settings), and that a bidirectional layer cannot sit under a causal decoder.
## Deep (stacked) recurrent network
Stack recurrent layers, the output sequence of one becoming the input sequence of the next:
@@ h_{t}^{(l)}=f\left(W^{(l)}h_{t-1}^{(l)}+U^{(l)}h_{t}^{(l-1)}+b^{(l)}\right)
Depth buys a hierarchy over time: lower layers capture local patterns, higher layers capture longer structure, exactly as in a convolutional network but along the time axis. The costs are memory (all states at every layer must be kept for the backward pass), longer training, and a greater tendency to overfit on small data. Residual connections between layers are the standard stabiliser.
## Long short-term memory
Keep the topology of a standard recurrence but change the cell to a gated one with a separate cell state:
@@ f_{t}=\sigma\left(W_{f}[h_{t-1},x_{t}]+b_{f}\right),\qquad i_{t}=\sigma\left(W_{i}[h_{t-1},x_{t}]+b_{i}\right)
@@ c_{t}=f_{t}\odot c_{t-1}+i_{t}\odot\tanh\left(W_{c}[h_{t-1},x_{t}]+b_{c}\right)
@@ o_{t}=\sigma\left(W_{o}[h_{t-1},x_{t}]+b_{o}\right),\qquad h_{t}=o_{t}\odot\tanh\left(c_{t}\right)
The parameter count per layer rises to four times the product of the hidden width and the sum of hidden and input widths — four gates instead of one transition — and the memory roughly doubles. In exchange, the gradient path through the cell state is diagonal, and long-range dependencies become learnable. The gated recurrent unit is the lighter variant with two gates and no separate cell state, usually within a point of the LSTM's accuracy.
@fig fig5_variants||The four topologies side by side: one direction, two directions, stacked layers, and the gated cell.
## Comparison
@table 78,110,116,150
@hdr Criterion | Standard | Bidirectional | Deep | LSTM
@row direction | forward only | both | forward (or both) | forward (or both)
@row parameters per layer | base | doubled | multiplied by depth | four times base
@row long dependencies | poor | poor | poor | good
@row needs the full sequence | no | yes | no | no
@row streaming or online use | yes | no | yes | yes
@row memory per step | low | doubled | times the depth | doubled and times the depth
@row typical use | toy models, short series | tagging, speech encoding | large corpora | general sequence modelling
@end
## Choosing
+ Short sequences, tight compute, or a baseline: a standard recurrence.
+ A completed sequence and a per-token label: bidirectional, and bidirectional *plus* gating if the dependencies are long.
+ A large corpus and a need for hierarchy: deep, usually with residual connections.
+ Long dependencies in a streaming setting: LSTM or gated recurrent unit.
+ Modern default: a gated stack, with attention if the sequence is long; a transformer if the dataset is large.
@box tip||Answer structure
Describe each variant by the one axis it changes — direction, depth, or the state update — then compare them in a table on parameters, memory and dependency length. That organisation answers the question directly and avoids a list of definitions.
@end
@key The four models differ along three axes: direction (bidirectional), depth (stacked) and the state update (gated LSTM); only the last changes how far a gradient can travel, and only the bidirectional one requires the whole sequence in advance.
@box ok||Examiner's checklist
- Writes the recurrence for each variant.
- Assigns parameter counts and memory per variant.
- Explains what each axis buys and what it costs.
- Notes that the bidirectional model needs the entire sequence, so it is not causal.
- Ends with a selection rule.
@end
@kw recurrence; bidirectional; stacked RNN; LSTM; gated recurrent unit; parameter count; causal constraint; long-range dependency; residual connection
"""

SCRIPTS[4] = r"""
#A 4::Explain the gates of an LSTM and the role of the internal cell state::CO5 · Understand–Analyse · 10 marks · ~3 pages::LSTM gates and the internal state
## Why a gate at all
The simple recurrence overwrites its state at every step with a full matrix multiplication, so there is no way for the network to *decide* to keep something. A gate is a multiplicative, learned valve: a sigmoid produces a vector with entries between zero and one that scales another vector elementwise, and the network learns how far to open it. Three gates and one candidate constitute the LSTM.
## The equations
@@ f_{t}=\sigma\left(W_{f}\left[h_{t-1},x_{t}\right]+b_{f}\right)
@@ i_{t}=\sigma\left(W_{i}\left[h_{t-1},x_{t}\right]+b_{i}\right)
@@ \tilde{c}_{t}=\tanh\left(W_{c}\left[h_{t-1},x_{t}\right]+b_{c}\right)
@@ c_{t}=f_{t}\odot c_{t-1}+i_{t}\odot\tilde{c}_{t}
@@ o_{t}=\sigma\left(W_{o}\left[h_{t-1},x_{t}\right]+b_{o}\right)
@@ h_{t}=o_{t}\odot\tanh\left(c_{t}\right)
@fig fig5_lstm||The cell: the horizontal line at the top is the cell state, written by the input gate and read through the output gate, with the forget gate deciding what survives.
## What each gate does
- **Forget gate.** Scales the previous cell state. A value near one keeps the memory, a value near zero erases it. It is the gate that gives the LSTM its long memory, and its bias is initialised positive so that memory is preserved at the start of training.
- **Input gate.** Scales the new candidate, deciding how much of the current input to write into the state. Together with the candidate it forms the "write" operation.
- **Candidate.** The actual content proposed by the current input and previous hidden state, squashed into the interval from minus one to one so that it can be added or subtracted.
- **Output gate.** Decides how much of the cell state to expose as the hidden output. This is the separation that a simple recurrence lacks: the internal memory and the external representation are different objects.
## The internal cell state
The cell state runs along the top of the diagram, modified only by elementwise multiplication and addition:
@@ c_{t}=f_{t}\odot c_{t-1}+i_{t}\odot\tilde{c}_{t}
Three properties follow directly from the plus sign:
+ **Additive, not multiplicative, update.** Adding is what makes the gradient path linear. The Jacobian is diagonal, so no direction is mixed and no matrix power appears.
+ **Per-channel memory.** Each coordinate of the state has its own forget gate, hence its own decay constant. The network can keep one feature for hundreds of steps and another for two.
+ **Constant error carousel.** With the forget gate at one and the input gate at zero the state is copied unchanged and the gradient is exactly one — the property that made LSTMs able to learn dependencies of hundreds of steps at all.
The hidden state is the *interface* to the rest of the network: it is bounded by the tanh, so it can be fed forward or into a classifier without scaling problems, and it can choose to reveal only part of the memory.
## Gates as learned control
It is worth stating what the gates are *not*: they are not attention weights over positions, and they do not see the future. They are functions of the current input and the previous hidden state, so all their decisions are causal. Reading a gated cell as a small differentiable program — keep, write, read — is the most compact correct mental model.
@box note||Common exam slip
Writing the output as the output gate times the cell state, without the tanh. The tanh is not cosmetic: it bounds the exposed state, and it is part of why the output layer stays well conditioned.
@end
@key The forget gate decides what survives, the input gate what is written, the output gate what is exposed, and the additive cell-state path is what turns a product of dense Jacobians into a product of diagonal gates.
@box ok||Examiner's checklist
- Writes all six equations with the gate ranges.
- Explains each gate as a multiplicative valve with a role.
- Explains the diagonal Jacobian and the constant error carousel.
- Distinguishes the cell state from the hidden state and says why the tanh matters.
- Notes causality: the gates see only past and present.
@end
@kw forget gate; input gate; output gate; candidate state; cell state; hidden state; sigmoid; constant error carousel; diagonal Jacobian; gating
"""

SCRIPTS[5] = r"""
#A 5::A simple RNN fails on very long sequences — give a complete strategy::CO5 · Apply–Create · 10 marks · ~3 pages::Strategy for long sequences
## Diagnose the failure first
"Fails on long sequences" has four distinct causes, and the remedy differs for each. Say which one you are fixing:
@table 110,190,197
@hdr Symptom | Cause | Remedy family
@row cannot learn a dependency far back | vanishing gradient | gating, attention
@row loss spikes then becomes not-a-number | exploding gradient | clipping, smaller step
@row trains but memory overflows | the backward pass stores every state | truncated backpropagation
@row good on short, bad on long test sequences | distribution shift, no length generalisation | curriculum, chunking
@end
@fig fig5_long||Two ways to shorten the path: bound the window over which gradients flow, or let the decoder reach any step directly.
## The strategy, in order of cost
### Step 1 · Clip and truncate
Backpropagation through time needs every state of the sequence in memory, so cost grows linearly in the length and quadratically in the backward pass through time. **Truncated backpropagation** backpropagates only a fixed number of steps (typically 32–128), carrying the state forward without gradient across chunk boundaries. This bounds memory and is the standard engineering answer for long audio or sensor streams. Combine it with gradient-norm clipping, which is not optional for recurrent nets.
### Step 2 · Change the cell
Replace the simple recurrence by a gated one — LSTM or gated recurrent unit — so that the gradient path is a product of diagonal gates rather than of the same dense matrix. Initialise the forget-gate bias to one and use orthogonal initialisation for the recurrent weights, which keeps the initial Jacobian's singular values near one. This is the single highest-value change when the failure is a long-range dependency.
### Step 3 · Normalise and schedule
Layer normalisation inside the recurrence stabilises the state statistics across time steps; a learning-rate warm-up followed by a decay schedule prevents early divergence; noise or dropout applied to the *inputs and outputs* of the recurrent layer, not to the recurrent connections, regularises without breaking the memory.
### Step 4 · Restructure the problem
- **Downsample or chunk the input.** Ten minutes of audio at 16 kHz is almost ten million steps; frame-level features at 100 Hz reduce it by two orders of magnitude, and a hierarchical model (frames, then phones, then words) reduces the dependency length the recurrence must span.
- **Stateful batching.** Keep the hidden state across consecutive batches so that the model effectively sees the whole stream, while each batch is trained independently.
- **Sliding windows with overlap** for inference, so that no prediction depends on a context the model never saw.
### Step 5 · Add attention
When the dependency really is long, no recurrence keeps it reliably. Attention computes each output directly from a weighted sum of *all* encoder states,
@@ \alpha_{t,s}=\frac{\exp\left(e_{t,s}\right)}{\sum_{s'}\exp\left(e_{t,s'}\right)},\qquad e_{t,s}=v^{\top}\tanh\left(W_{h}h_{s}+W_{s}s_{t-1}\right)
so the path length between any two positions is one, not the length of the sequence. This removes the gradient decay entirely at the cost of compute quadratic in the length, and it is the reason transformers replaced recurrent models for long sequences.
### Step 6 · Replace the recurrence
If the sequence is long, the data are plentiful and latency is not critical, a transformer or a state-space model is the modern default. Say this as a recommendation, not as a dismissal: recurrent models remain the right choice for streaming inference with constant memory.
@box tip||The shape of a good answer
The examiner wants an ordered plan, not a list of tricks. Write: *clip, gate, normalise, restructure, attend*, and against each step the symptom it fixes and the cost it adds. Then state the decision rule: if the sequence fits in memory and the dependency is under a few hundred steps, a gated model with truncated backpropagation suffices; beyond that, attention is the answer.
@end
@key For long sequences: bound the memory with truncated backpropagation, bound the step with clipping, replace the cell by a gated one, restructure with hierarchical or stateful processing, and if the dependency is still too long, use attention so that the path length stops depending on the sequence.
@box ok||Examiner's checklist
- Separates the four failure causes before prescribing.
- Explains truncated backpropagation and what it gives up.
- Justifies the gated cell by the diagonal Jacobian.
- Gives at least two restructurings: hierarchy, stateful batching.
- Ends with attention and states its cost.
@end
@kw truncated backpropagation; gradient clipping; orthogonal initialisation; layer normalisation; hierarchical model; stateful batching; attention; path length; quadratic cost
"""

SCRIPTS[6] = r"""
#A 6::Design an encoder–decoder sequence-to-sequence model and derive its training objective::CO5 · Apply–Analyse · 10 marks · ~3 pages::Encoder–decoder seq2seq
## The problem it solves
A single recurrent network maps a sequence to a label, or to a sequence of the same length. Translation, summarisation and speech transcription map a sequence to a sequence of a **different** length and a different vocabulary. The encoder–decoder architecture handles this by separating "read" from "write".
## The encoder
A recurrent network consumes the source sequence and produces a hidden state per step; the final state is the context vector:
@@ h_{t}=f_{enc}\left(h_{t-1},x_{t}\right),\qquad c=h_{T}
With a bidirectional encoder the context is the concatenation of the two final states, so the summary sees the sentence from both ends.
## The decoder
A second recurrent network is initialised from the context and generates the target one token at a time, conditioned on the context and on what it has already produced:
@@ s_{t'}=f_{dec}\left(s_{t'-1},y_{t'-1},c\right)
@@ P\left(y_{t'}\mid y_{<t'},x\right)=\mathrm{softmax}\left(W_{o}s_{t'}+b_{o}\right)
@fig fig5_seq2seq||Encoder compresses the source into the context vector; the decoder unrolls the target conditioned on it and on its own previous output.
## The training objective
The model defines a conditional distribution over whole target sequences by the chain rule:
@@ P\left(y\mid x\right)=\prod_{t'=1}^{T'}P\left(y_{t'}\mid y_{<t'},x\right)
Training maximises the log-likelihood of the reference translation — equivalently minimises the negative log-likelihood, summed over the corpus:
@@ \mathcal{L}(\theta)=-\sum_{n=1}^{N}\sum_{t'=1}^{T'_{n}}\log P_{\theta}\left(y^{(n)}_{t'}\mid y^{(n)}_{<t'},x^{(n)}\right)
This is **cross-entropy with the previous target tokens as input**, and it factorises exactly like a language model; the only difference is that every conditional is also conditioned on the context. Because each factor is a softmax, the gradient with respect to the decoder logits is again predicted minus target probability, and the whole model is trained by backpropagation through both networks.
## Teacher forcing and its consequence
During training the previous target token is the *true* one, not the model's own prediction — this is **teacher forcing**. It makes every step's gradient well defined and allows the computation to be parallel over the target positions within a sequence. The mismatch is that at inference the model must consume its own outputs, which it has never seen during training; the resulting error accumulation is called **exposure bias**. Remedies: scheduled sampling (feed the model's own output with a probability that increases over training), beam search at inference, and sequence-level objectives such as minimum risk training.
## Inference
Greedy decoding takes the most probable token at each step; beam search keeps the best few partial sequences and maximises
@@ \hat{y}=\arg\max_{y}\sum_{t'}\log P\left(y_{t'}\mid y_{<t'},x\right)
which is a better approximation of the most probable sequence but does not guarantee it, since the most probable sequence is not the sequence of most probable tokens.
## The bottleneck and the fix
A single fixed-length context vector must carry the entire source, so performance degrades with length. **Attention** lets the decoder look at all encoder states with weights recomputed at every step:
@@ c_{t'}=\sum_{s}\alpha_{t',s}h_{s},\qquad \alpha_{t',s}=\mathrm{softmax}_{s}\left(e_{t',s}\right)
so the decoder can align to the relevant part of the input. This is the same mechanism that, without the recurrence, becomes the transformer.
@box warn||Two derivations to keep straight
The chain rule gives a product over *output* positions, each conditioned on the prefix. The negative log turns the product into a sum over positions, which is why the loss adds over time rather than multiplying.
@end
@key An encoder compresses the source into a context vector and a decoder factorises the target distribution autoregressively, conditioned on that vector, trained by maximising log-likelihood under teacher forcing.
@box ok||Examiner's checklist
- Describes the encoder, the context vector and the decoder separately.
- Writes the factorisation and the negative log-likelihood loss over a corpus.
- Explains teacher forcing and exposure bias.
- Distinguishes greedy from beam search.
- Identifies the fixed-context bottleneck and gives attention as the fix.
@end
@kw encoder–decoder; context vector; autoregressive factorisation; teacher forcing; exposure bias; cross-entropy over time; beam search; attention alignment; sequence transduction
"""

SCRIPTS[7] = r"""
#A 7::Design an autoencoder for dimensionality reduction — bottleneck, objective, and how to avoid the identity mapping::CO5 · Apply–Create · 10 marks · ~3 pages::Autoencoder for dimensionality reduction
## The architecture
An autoencoder is two networks trained together: an encoder that maps the input to a low-dimensional code, and a decoder that reconstructs the input from the code.
@@ z=E_{\phi}(x)\in\mathbb{R}^{d},\qquad \hat{x}=D_{\theta}(z),\qquad d\ll n
@fig fig5_ae||The bottleneck is the only constraint that forces compression; without it the network can learn the identity.
The objective is the reconstruction error, averaged over the dataset:
@@ \mathcal{L}(\phi,\theta)=\frac{1}{m}\sum_{i=1}^{m}\left\|x^{(i)}-D_{\theta}\left(E_{\phi}\left(x^{(i)}\right)\right)\right\|^{2}
For binary or normalised inputs the cross-entropy form is used instead. Training is ordinary backpropagation through both halves; no labels are needed, which is why the method is unsupervised.
## Why the bottleneck matters
If the code is at least as wide as the input and both halves are expressive, the trivial solution — the composition being the identity — attains zero loss and the code is useless. The bottleneck is therefore not an implementation detail: it is the constraint that creates the representation. Three ways to enforce it:
+ **Undercomplete** (a code narrower than the input): the code cannot hold the input, so the network must keep the directions of greatest variation.
+ **Sparse** (a wide code with a penalty on its activity): few units are active per input.
+ **Denoising**: corrupt the input and require the clean input back, which prevents copying even when the code is wide.
## The linear case is exactly PCA
Consider a linear encoder and a linear decoder with squared error. The optimum of the reconstruction objective is attained when the composition of the two matrices is the orthogonal projector onto the top-$d$ principal subspace of the data covariance. The argument: the composition is a rank-$d$ matrix, and the squared reconstruction error of a rank-$d$ projector is the sum of the discarded eigenvalues, minimised by keeping the $d$ largest. The decoder's columns then span the same subspace as the first $d$ principal components, and if they are constrained to be orthonormal the autoencoder recovers PCA exactly.
The corollary is the examinable statement: *a linear autoencoder with a linear decoder and squared error is PCA with extra parameters; the value of the autoencoder is that it generalises PCA to nonlinear manifolds.*
## Design choices that matter
@table 110,180,207
@hdr Choice | Recommendation | Reason
@row code size | sweep; pick the elbow of reconstruction error | same role as the number of components in PCA
@row depth | two to four layers per half | enough nonlinearity, still trainable
@row activation | ReLU in the encoder, linear or sigmoid at the output | match the input range
@row loss | squared error for continuous, cross-entropy for probabilities | matches the noise model
@row bottleneck unit | linear for a "PCA-like" code | keeps the geometry interpretable
@row regularisation | denoising or sparsity penalty | prevents identity, improves features
@row validation | held-out reconstruction error | the only honest signal without labels
@end
## Using it for dimensionality reduction
Train on the full dataset (or on a training split and apply to the rest), then discard the decoder and keep the code as the reduced representation. Two practical points:
+ **Standardise first** — otherwise the first principal direction is dominated by the variable with the largest units.
+ **Compare with PCA at the same code size**: if the data are close to linear, PCA wins on speed and interpretability; autoencoders win when the data lie on a curved manifold, which is typical for images and spectra.
@box tip||The single sentence that earns the mark
"A linear autoencoder with squared error spans the PCA subspace; the nonlinear version is a generalisation of PCA to curved manifolds, and the bottleneck is what forces it to learn the manifold rather than the identity."
@end
@key An autoencoder minimises the squared reconstruction error under a bottleneck; the bottleneck, or a denoising or sparsity constraint, is what prevents the identity map, and in the linear squared-error case the learned subspace is exactly the PCA subspace.
@box ok||Examiner's checklist
- Draws the encoder, bottleneck and decoder, and writes the loss.
- Explains why the code must be narrower and what the identity solution is.
- Names two other ways to prevent triviality: sparsity, denoising.
- Derives or states the linear-autoencoder / PCA equivalence.
- Gives practical choices: standardisation, code-size sweep, comparison with PCA.
@end
@kw autoencoder; bottleneck; undercomplete; reconstruction loss; identity mapping; denoising autoencoder; sparse coding; PCA equivalence; manifold learning
"""

SCRIPTS[8] = r"""
#A 8::How do autoencoders learn representations, and when are those representations useful?::CO5 · Understand–Evaluate · 10 marks · ~2.5 pages::Autoencoders and representation learning
## What is learned, and why it is not just compression
The encoder must map every input to a code from which the decoder can rebuild it. Any information the encoder throws away is lost for every input, so it is forced to keep the *factors that vary systematically* and discard the noise that is specific to each example. That selection is what makes the code a representation rather than a compression: the network is learning the generative factors of the data, because those are what reconstruction requires.
Formally, the autoencoder learns a manifold: if the data concentrate near a low-dimensional surface, then a narrow code can reconstruct them only if the encoder charts that surface and the decoder inverts the chart. The code is then a coordinate system on the data manifold.
## Three ways to shape the representation
+ **Denoising autoencoder.** Corrupt the input and minimise the error against the clean original. The network cannot copy, so it must learn the structure that allows recovery. This is the most reliable way to get useful features from a wide code.
+ **Sparse autoencoder.** Penalise the activity of the code so that each input activates few units. The units become more selective and closer to the "one concept per unit" ideal; interpretability improves.
+ **Contractive or variational.** A contractive penalty on the encoder Jacobian makes the code insensitive to small input perturbations; a variational autoencoder makes the encoder output a distribution and trains with the evidence lower bound, which additionally yields a usable generative model.
## When the representation is useful
@table 120,180,197
@hdr Use | Why the code helps | Caveat
@row downstream classifier with few labels | features trained on all data, labelled or not | the code may discard label-relevant detail
@row visualisation and clustering | low-dimensional coordinates | clusters are of the data, not of the classes
@row denoising and inpainting | projection onto the manifold | blurry for large corruptions
@row anomaly detection | unusual inputs reconstruct badly | the threshold needs calibration
@row initialisation for a deep net | features start in a good region | usually beaten by supervised pretraining
@row generative modelling | sampling in code space | posterior collapse in variational models
@end
The key caveat is stated in the table's first row: an autoencoder is trained to preserve *everything* that is reconstructible, whereas a classifier needs only what separates the classes. A representation that is excellent for reconstruction can be poor for classification — the classic counter-example is a code that keeps the background texture and discards the object. This is why representation learning moved toward objectives that are *discriminative by construction*: contrastive learning, masked-token prediction, and their descendants.
## Evaluating a learned representation
Three honest tests, in increasing order of cost:
+ **Linear probe.** Freeze the encoder and train a linear classifier on the code; accuracy measures how linearly separable the concepts have become.
+ **Transfer.** Fine-tune on a small labelled set and compare with training from scratch on the same budget.
+ **Task-aligned reconstruction.** Check that improved reconstruction actually improves the task; often it does not, and the gap is the evidence that the objective is misaligned.
@box warn||The over-complete trap
If the code is at least as wide as the input and nothing else constrains it, the autoencoder learns the identity and the "representation" is the input. Any claim about learned features must therefore come with the mechanism that prevented copying: a bottleneck, a sparsity penalty, or noise.
@end
@key An autoencoder learns the generative factors of the data because reconstruction forces it to keep what varies systematically and drop what is idiosyncratic; the representation is useful when it is constrained (bottleneck, sparsity, noise) and when the downstream task needs what reconstruction preserves.
@box ok||Examiner's checklist
- Explains representation learning as manifold charting, not compression.
- Describes denoising, sparse and variational variants and what each changes.
- Lists downstream uses with a caveat for each.
- States the reconstruction-versus-discrimination mismatch.
- Gives concrete evaluation: linear probe, transfer, task-aligned reconstruction.
@end
@kw representation learning; manifold; generative factors; denoising autoencoder; sparsity; contractive penalty; variational autoencoder; evidence lower bound; linear probe; transfer learning
"""
