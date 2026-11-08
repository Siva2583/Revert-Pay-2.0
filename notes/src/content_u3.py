# -*- coding: utf-8 -*-
"""Unit III — Regularisation and optimisation of deep networks."""

UNIT_INFO = {
    'unit': 3,
    'roman': 'III',
    'label': 'UNIT III',
    'title': 'Regularisation and Optimisation',
    'subtitle': 'Overfitting, penalty terms, dropout, constraints and the optimiser '
                'ladder',
}

GLANCE = [
    (1, "A regularisation plan for severe overfitting",
     "Diagnose the gap, then intervene in the order data → loss → architecture → "
     "optimiser."),
    (2, "$L_1$ versus $L_2$: why only one of them is sparse",
     "The gradient of the $L_1$ penalty is constant in magnitude, so it can drive a "
     "weight to exactly zero."),
    (3, "Dropout as a training strategy",
     "A random mask per mini-batch; test-time scaling turns $2^{n}$ thinned nets into "
     "one geometric-mean ensemble."),
    (4, "Norm constraint and its Lagrangian twin",
     "A hard constraint on the norm and a penalty term are the same problem linked by "
     "the KKT multiplier."),
    (5, "An optimiser sequence for training that will not converge",
     "Fix initialisation first, then momentum, then RMSProp, then Adam — and say why "
     "each rung helps."),
    (6, "Why deep-network optimisation is not pure optimisation",
     "The objective is a surrogate for generalisation, the landscape is non-convex, "
     "and gradients are sampled."),
    (7, "AdaGrad, RMSProp and Adam compared",
     "Same adaptive step; different memory of past squared gradients."),
    (8, "Early stopping, dropout and augmentation trade-offs",
     "Three regularisers at three different levels — steps, activations, data — with "
     "different costs."),
]

REVISION = [
    (1, "Diagnose before you regularise: plot the training and validation curves; a "
        "wide gap is variance, both high is bias.",
     "Do not answer with 'add dropout' alone — the question asks for a plan, so order "
     "the interventions and say how you will measure success."),
    (2, "$L_1$ gives sparse weights because the derivative of $|w|$ is a constant "
        "sign, so a fixed threshold can reach zero; $L_2$ shrinks proportionally and "
        "never reaches it.",
     "Sparsity is a property of the geometry (corner of the diamond), not of the "
     "formula 'absolute value'."),
    (3, "Dropout = $2^{n}$ weight-sharing sub-networks; at test time multiply weights "
        "by the keep probability $q$.",
     "Forgetting inverted dropout: with it you divide by $q$ during training and do "
     "nothing at test time."),
    (4, "Constrained problem, Lagrangian, stationarity, complementary slackness: if the "
        "constraint is active then the multiplier is the penalty coefficient.",
     "Claiming the two problems are identical for the same $\\lambda$ — they are "
     "equivalent only through the map between $\\lambda$ and the radius $t$."),
    (5, "Initialisation → momentum → RMSProp → Adam, each rung fixing a specific "
        "failure: scale, ill-conditioning, per-parameter scaling.",
     "Presenting Adam as a cure-all; it still needs a sane learning rate, warm-up and "
     "clipping."),
    (6, "Deep learning optimises a surrogate, with sampled gradients, on a non-convex "
        "surface dominated by saddle points.",
     "Saying 'local minima are the problem' — in high dimensions local minima are rare "
     "and usually good; plateaus and saddle points hurt more."),
    (7, "AdaGrad accumulates from the start and stalls; RMSProp forgets; Adam forgets "
        "and adds momentum with bias correction.",
     "Forgetting Adam's bias correction of both moving averages."),
    (8, "Early stopping is free and needs a validation set; dropout costs epochs; "
        "augmentation costs compute but also enlarges the effective data.",
     "Using the test set to decide when to stop."),
]

SCRIPTS = {}

SCRIPTS[1] = r"""
#A 1::Designing a regularisation plan when a deep network overfits severely::CO3 · Apply–Analyse · 10 marks · ~3 pages::A regularisation plan for severe overfitting
## What "severe overfitting" looks like
Overfitting is present when the model has memorised the training set: the training loss keeps falling while the validation loss bottoms out and then rises. The quantitative signal is the **generalisation gap** between the two curves, and the diagnostic is the pair of learning curves. Before prescribing anything, decide which of the two failures you have, because the remedies are opposite in direction:

@table 30,230,237
@hdr Sign | What the curves show | First move
@row high variance | training loss near zero, validation loss far above it and rising | regularise, get more data, simplify
@row high bias | both losses high and flat | bigger model, train longer, better features
@row noisy labels | the training loss itself is high, validation close to it | clean labels, robust loss
@end
The question assumes severe overfitting, i.e. a large gap. The plan below attacks it in a fixed order: **data first, then the objective, then the architecture, then the optimiser**. Cheap, low-risk interventions come before expensive ones.
## Step 1 — Enlarge the effective data
- **Collect more data.** Only this changes the variance term directly; ten times more data beats any hyper-parameter.
- **Augment** with label-preserving transforms — crops, flips, small rotations, colour jitter for images; time warping, noise injection for audio; token dropout, back-translation for text.
- **Synthetic oversampling** for rare classes, used carefully because it can add noise instead of information.
The theoretical statement is the decomposition
@@ J(\theta)=\mathrm{bias}^{2}+\mathrm{variance}+\sigma_{\epsilon}^{2}
and variance falls roughly as $O(1/m)$ in the number of examples $m$. Nothing else in this plan has that guarantee.
## Step 2 — Change the objective: add a penalty
Train on the regularised objective instead of the plain empirical risk:
@@ \tilde{J}(\theta)=J(\theta)+\lambda\Omega(\theta),\qquad \Omega(\theta)=\frac{1}{2}\|\theta\|_{2}^{2}
which for plain gradient descent changes the update from a plain step to
@@ \theta\leftarrow(1-\eta\lambda)\,\theta-\eta\nabla J(\theta)
so every step multiplies the weights by a factor slightly below one — **weight decay**. The penalty is chosen to match the prior you believe: $L_2$ for "weights should be small and spread", $L_1$ for "few features matter", elastic net when features are correlated. Choose $\lambda$ on a logarithmic grid by cross-validation; the curve of validation loss against $\log\lambda$ is usually flat-bottomed and U-shaped.
## Step 3 — Regularise inside the architecture
- **Dropout** on the dense layers (rate $0.3$–$0.5$), and lower rates on convolutional layers; it is the cheapest way to stop co-adaptation.
- **Batch normalisation**, which changes the effective objective and usually allows a higher learning rate; it is a mild regulariser because of the mini-batch noise.
- **Early stopping** on the validation loss: keep the weights at the best epoch.
- **Reduce capacity** only if the gap survives everything above: fewer layers, fewer units, or a smaller kernel budget.
- **Weight tying / sharing** where the problem allows it, e.g. convolutional weights, siamese towers.
## Step 4 — Make the optimiser less greedy
Smaller mini-batches inject gradient noise, which is itself a regulariser; a decaying learning-rate schedule lets the model settle into flat regions; label smoothing replaces one-hot targets with reduced confidence and prevents over-confident logits. All three reduce the gap without touching the data or the architecture.
## Step 5 — Average models
Snapshot ensembles, checkpoint averaging and multi-seed ensembles reliably buy one to three points of accuracy at the cost of inference time. They are the last resort because they do not fix a broken training procedure, they average over it.
@fig fig3_complexity||Validation error is U-shaped in capacity; regularisation moves the minimum to the left, more data lowers the whole curve.
## Choosing the strength — a worked protocol
1. Hold out a validation split (or use $k$-fold for small data).
2. Fix everything else and sweep one knob at a time in the order data → penalty → dropout → early stopping.
3. Record both losses and the gap for each setting; stop when the gap is small and the validation loss has stopped improving.
4. Re-check on the untouched test set exactly once.
@table 150,180,167
@hdr Intervention | Cost | Typical effect on the gap
@row more/augmented data | data collection or CPU per epoch | largest, most durable
@row $L_2$ penalty | one extra term in the gradient | 1–3 points, monotone in the strength
@row dropout | 2–3× epochs to converge | large on dense nets
@row early stopping | needs a validation split | free, prevents the tail of the curve
@row smaller model | capacity | can convert variance into bias
@row ensembling | inference time | 1–3 points, no training cost
@end
@box warn||The order matters
Do not start with "use dropout". If the gap is caused by 500 labelled images and a 20-million-parameter backbone, the honest first answer is *more data or a smaller backbone*; dropout applied to an already-underfitting model will simply make both curves worse. State your diagnosis, then the intervention, then the measurement that tells you it worked.
@end
@key A regularisation plan is a diagnosis followed by an ordered list of interventions — data, objective, architecture, optimiser, ensembling — each with a predicted effect and a way to measure it.
@box ok||Examiner's checklist
- Names the symptom quantitatively (the gap between the two losses, learning curves).
- Gives at least four levels of intervention and justifies the ordering.
- Writes the regularised objective and the weight-decay update.
- Mentions that more data attacks variance with an $O(1/m)$ guarantee.
- Ends with a measurement protocol: validation split, one knob at a time, test set used once.
@end
@kw generalisation gap; weight decay; data augmentation; dropout; early stopping; capacity; bias–variance decomposition; validation protocol; ensemble averaging
"""

SCRIPTS[2] = r"""
#A 2::Compare $L_1$ and $L_2$ penalties and explain why only $L_1$ produces sparse solutions::CO3 · Understand–Analyse · 10 marks · ~3 pages::L1 versus L2 penalties and sparsity
## The two penalties
Both add a term to the empirical risk that penalises large weights, differing only in the norm used:
@@ \tilde{J}_{2}(\theta)=J(\theta)+\frac{\lambda}{2}\|\theta\|_{2}^{2}=J(\theta)+\frac{\lambda}{2}\sum_{i}\theta_{i}^{2}
@@ \tilde{J}_{1}(\theta)=J(\theta)+\lambda\|\theta\|_{1}=J(\theta)+\lambda\sum_{i}|\theta_{i}|
$L_2$ is called **ridge** regression in the linear case and **weight decay** in a network; $L_1$ is **lasso**. The corresponding gradients are qualitatively different:
@@ \nabla_{\theta}\tilde{J}_{2}=\nabla J+\lambda\theta,\qquad \nabla_{\theta}\tilde{J}_{1}=\nabla J+\lambda\,\mathrm{sgn}(\theta)
## Why $L_2$ shrinks but $L_1$ selects
The $L_2$ gradient contribution is proportional to the weight, so it becomes weaker as the weight approaches zero and the weight only decays geometrically. In the scalar case with no data term, the differential equation gives
@@ \theta(t)=\theta_{0}\,e^{-\lambda t}
which is asymptotic to zero and never equal to it.
The $L_1$ gradient contribution is $\lambda\,\mathrm{sgn}(\theta)$: a **constant force of size $\lambda$** directed towards zero, independent of how small the weight already is. So whenever the data gradient at a weight is smaller in magnitude than $\lambda$, the total gradient points at zero and the weight is driven there in finite time and **stays exactly at zero**. This is the analytical reason for sparsity. The closed form for a single weight with quadratic data term and target $y$ is the soft-threshold
@@ w^{\star}=\mathrm{sign}(y)\,\max\left(|y|-\lambda,\,0\right)
which is exactly zero for every $|y|\leq\lambda$ — an entire interval of data values mapped to a zero weight.
## The geometric explanation
@fig fig3_l1l2||Constraint geometry: the $L_2$ ball meets the loss contours at a generic point, the $L_1$ diamond meets them at a corner where one coordinate is zero.
Because the loss contours are smooth ellipses and the constraint set is a polytope with sharp corners on the axes, the first contact happens at a corner with probability one in high dimension. A corner of the $L_1$ ball has many zero coordinates; a point on the $L_2$ sphere has none. This is the same statement as the KKT condition of the next answer: at the solution the gradient of the loss must be a non-negative multiple of a subgradient of the norm, and only the $L_1$ norm has subgradients with zero components.
## Ridge has a closed form; lasso does not
For a linear model with design matrix $X$ and targets $y$,
@@ \hat{\theta}_{\text{ridge}}=(X^{\top}X+\lambda I)^{-1}X^{\top}y
The added $\lambda I$ makes the matrix invertible even when $X^{\top}X$ is singular (more features than samples), which is why ridge is the standard fix for collinearity. Lasso has no closed form but is solved by coordinate descent or proximal gradient, each coordinate being a soft-threshold update. In a network, $L_1$ is implemented by the same subgradient step or by the proximal operator applied after each update.
## Side-by-side comparison
@table 96,196,205
@hdr Property | $L_2$ penalty | $L_1$ penalty
@row Solution | dense, all weights small | sparse, many exact zeros
@row Effect on correlated features | shares weight between them | picks one, zeroes the rest
@row Differentiability | smooth everywhere | non-smooth at zero (subgradient)
@row Closed form (linear model) | yes, a matrix inverse | no, needs an iterative solver
@row Shrinkage profile | proportional | constant, then hard zero
@row Typical use | default in deep nets, weight decay | feature selection, compression
@row Stability | stable, unique | can be unstable with correlated inputs
@end
## The compromise: elastic net
@@ \Omega(\theta)=\lambda_{1}\|\theta\|_{1}+\lambda_{2}\|\theta\|_{2}^{2}
The $L_2$ part stabilises the solution when features are correlated — it makes the problem strictly convex and groups correlated features — while the $L_1$ part retains selection. In practice a small $L_2$ term alongside $L_1$ is almost always worth it.
@box tip||Practical note for networks
In a deep network plain $L_2$ on all weights is the default ($10^{-4}$ is a common starting value). Applying $L_1$ to a whole network rarely gives useful sparsity at the level of individual weights; structured sparsity (whole filters, whole channels, group lasso) is the version that actually shrinks models. Say this in the exam — it shows you know the difference between a textbook result and an engineering one.
@end
@key $L_2$ penalises the square, so its pull vanishes at the origin and weights only shrink asymptotically; $L_1$ penalises the absolute value, so its pull is a constant $\lambda$ that can hold a weight at exactly zero — sparsity is a consequence of the geometry, not of the algebra.
@box ok||Examiner's checklist
- Writes both objectives and both gradients.
- Explains the constant-magnitude gradient of the absolute value against the proportional gradient of the square.
- Gives the geometric corner argument.
- States the closed form for ridge and notes that lasso needs a solver.
- Compares on sparsity, correlated features, smoothness and stability.
@end
@kw ridge; lasso; weight decay; subgradient; soft thresholding; convexity; feature selection; elastic net; polytope corner
"""

SCRIPTS[3] = r"""
#A 3::Dropout as a regularisation strategy — mechanism, ensemble interpretation and computational cost::CO3 · Understand–Apply · 10 marks · ~3 pages::Dropout strategy, effective ensembles and compute cost
## Mechanism
At every training step, each unit of a chosen layer is kept with probability $q$ (the keep probability) and dropped with probability $1-q$, independently. With a mask drawn from a Bernoulli distribution the layer computes
@@ \tilde{h}=m\odot h,\qquad m_{i}\sim\mathrm{Bernoulli}(q)
and the mask is resampled for every mini-batch, so no unit can rely on a specific partner being present. The effect on the weights is that co-adaptation is broken: a feature must be useful in many random contexts, which is precisely a constraint against memorisation.
@fig fig3_dropout||Left: the full network. Right: one thinned network from a single mini-batch; the crossed units receive no gradient in that step.
## Inference: how the ensemble is collapsed
Training samples $2^{n}$ different thinned sub-networks that share weights. At test time we want the average prediction of all of them, which is intractable. The standard approximation is to use the full network with the outgoing weights scaled by the keep probability:
@@ W^{(l)}_{\text{test}}=q\,W^{(l)}
This matches the expected pre-activation of a linear unit, and for a softmax output it approximates the geometric mean of the sub-network distributions rather than the arithmetic mean — a well-known subtlety, but the approximation is good enough in practice and is what makes dropout free at inference.
The modern equivalent, **inverted dropout**, divides by $q$ during training instead:
@@ \tilde{h}=\frac{m\odot h}{q}
so that the expectation of the masked activation equals the unmasked one and nothing at all needs to change at test time. This is what every framework implements today.
## Why this is an ensemble
Each mini-batch trains one member of a family of $2^{n}$ architectures that share parameters. The prediction of the scaled network is a single evaluation that approximates the model average, so dropout buys the variance reduction of ensembling without $k$ times the inference cost. The analogy is exact enough to be examinable: *dropout is bagging of sub-networks with parameter sharing and one Monte-Carlo sample per step*.
## Cost analysis
@table 120,180,197
@hdr Cost component | During training | During inference
@row parameters | unchanged | unchanged
@row arithmetic per example | one mask multiply per unit (about 1–2%) | zero
@row memory | mask per layer per step (small) | zero
@row convergence | 2–3× more epochs, higher learning rate needed | —
@row gradient noise | variance increases, scale by $1/q$ | —
@row accuracy at test | — | free ensemble effect
@end
The real cost is therefore **optimisation time**, not arithmetic: noisy gradients mean the loss curve is jagged, the effective learning rate must often be raised, and training may need two or three times as many epochs. In exchange, nothing is added to the deployed model.
## A concrete dropout strategy
- Input layer: rate $0.1$–$0.2$ (image pixels) — rarely more, it destroys signal.
- Convolutional layers: $0.1$–$0.25$, or none if batch normalisation is already present.
- Fully connected layers: $0.3$–$0.5$ — this is where most of the parameters and most of the memorisation live.
- Output layer: never.
- Always pair with early stopping on validation loss; the best epoch usually comes later than without dropout.
- When a batch-norm layer follows, note the variance mismatch between train and test: dropout changes the activation variance, so apply dropout after the normalisation, or use a dropout variant designed for it.
@box warn||Two common mistakes
1. Applying the $1/q$ scaling at test time as well as training (double correction) — the network becomes under-confident.
2. Leaving dropout on during validation: predictions become random and the validation loss is meaningless. Always switch the model to inference mode before evaluating.
@end
@key Dropout trains $2^{n}$ weight-sharing sub-networks in one pass and evaluates their geometric mean in one pass, so it delivers ensemble-level variance reduction at essentially zero inference cost, paying instead in training epochs.
@box ok||Examiner's checklist
- Writes the Bernoulli mask and the keep probability.
- Explains both scaling conventions and why inverted dropout removes test-time work.
- Connects to the $2^{n}$ ensemble and the geometric mean.
- Quantifies the cost: no new parameters, negligible arithmetic, 2–3× epochs.
- Gives layer-wise rates and mentions the interaction with batch normalisation.
@end
@kw co-adaptation; Bernoulli mask; keep probability; inverted dropout; thinned network; geometric mean; model averaging; variance reduction; inference cost
"""

SCRIPTS[4] = r"""
#A 4::Explain the norm constraint on parameters and derive its relation to the penalty term using the Lagrangian and KKT conditions::CO3 · Apply–Analyse · 10 marks · ~3 pages::Norm constraint and its relation to the penalty term
## The two formulations
The regularised problem can be written in two apparently different ways. The **penalty** (soft) form adds a term to the loss:
@@ \theta^{\star}=\arg\min_{\theta}J(\theta)+\lambda\Omega(\theta)
The **constraint** (hard) form restricts the weights to a region:
@@ \theta^{\star}=\arg\min_{\theta}J(\theta)\quad\text{subject to}\quad\Omega(\theta)\leq t
For the squared $L_2$ norm the feasible set is a ball of radius $\sqrt{2t}$; for the $L_1$ norm it is the diamond of the previous answer. The claim to be proved is that for every radius $t$ there exists a $\lambda\geq0$ giving the same solution, and conversely.
## Lagrangian and the KKT system
Form the Lagrangian with multiplier $\lambda\geq0$:
@@ \mathcal{L}(\theta,\lambda)=J(\theta)+\lambda\left(\Omega(\theta)-t\right)
The KKT conditions for this convex problem are stationarity, dual feasibility, complementary slackness and primal feasibility:
@@ \nabla_{\theta}J(\theta^{\star})+\lambda\,\partial\Omega(\theta^{\star})\ni0
@@ \lambda\geq0,\qquad \lambda\left(\Omega(\theta^{\star})-t\right)=0
@@ \Omega(\theta^{\star})\leq t
where the partial derivative symbol denotes the subdifferential, needed because the $L_1$ norm is not differentiable at zero. The second line is **complementary slackness**. It splits the answer into the two cases that the exam wants:
+ If the unconstrained minimiser already satisfies the constraint, the constraint is inactive and $\lambda=0$: the solution is the plain maximum-likelihood estimate.
+ If the constraint is active, the radius is saturated and $\lambda>0$: the stationarity condition is exactly the stationarity condition of the penalty problem with that $\lambda$.
Hence the constraint problem and the penalty problem have the same set of solutions, and the multiplier of the constraint problem *is* the regularisation coefficient of the penalty problem.
## The one-to-one map between radius and strength
Define the achieved norm as a function of the penalty strength. Along the regularisation path this function is continuous and non-increasing: a larger $\lambda$ shrinks the weights further, so the ball that contains the solution shrinks. This gives a monotone bijection on the range where the constraint is active, which is why the two formulations are called **equivalent** — equivalent as families, parameterised differently.
@fig fig3_path||The regularisation path: as $\lambda$ grows the $L_1$ diamond grows relative to the loss contours and the solution slides along an axis, one weight at a time becoming exactly zero.
## Worked example in one dimension
Take a quadratic data term and the absolute-value penalty. The constrained problem is to minimise $\frac{1}{2}(\theta-y)^{2}$ subject to $|\theta|\leq t$. Its solution is the projection of $y$ onto the interval $[-t,t]$:
@@ \theta^{\star}_{c}(t)=\mathrm{sign}(y)\min(|y|,t)
The penalty problem gives the soft-threshold of the previous answer. Putting $t=|y|-\lambda$ makes the two expressions identical for $0\leq\lambda\leq|y|$; for $\lambda>|y|$ the penalty solution is zero while the constraint solution is zero only if $t=0$. The mapping between them is exactly the relation predicted by the theory, and at that point complementary slackness holds.
## Why keep both views
@table 120,180,197
@hdr Aspect | Constraint form | Penalty form
@row hyper-parameter | radius, interpretable as a trust region | strength, scale-dependent
@row optimisation | projection step after each update | gradient or subgradient term
@row tuning | hard to set without knowing the weight scale | straightforward log grid
@row geometry | explicit ball or diamond in weight space | implicit level sets
@row typical use | projected gradient, max-norm constraints, robustness | standard training in every framework
@end
The constraint view is what makes the geometry obvious (why $L_1$ is sparse, why a max-norm constraint is a trust region); the penalty view is what is actually implemented, because a gradient term is cheaper than a projection.
@box key||Link back to Unit I
This is the same KKT machinery used for the margin derivation of the support vector machine: there the constraint was that every point lies on the correct side of the margin with multipliers, and complementary slackness said that only support vectors have a positive multiplier. Here the constraint is on the norm of the parameter vector and the single multiplier plays the role of the whole multiplier vector; the statement "only the active constraints matter" is identical.
@end
@key A norm constraint and a norm penalty are two parameterisations of one problem: the KKT multiplier of the active constraint is the penalty coefficient, and complementary slackness says the constraint only bites when the unconstrained optimum lies outside the ball.
@box ok||Examiner's checklist
- Writes both formulations and the Lagrangian with a non-negative multiplier.
- States stationarity, dual feasibility, complementary slackness and primal feasibility.
- Treats the inactive and active cases separately.
- Shows the monotone map between radius and strength and calls the families equivalent.
- Works the one-dimensional example through to the soft-threshold.
@end
@kw Lagrangian; KKT conditions; complementary slackness; active constraint; trust region; regularisation path; projection; subdifferential; equivalence of formulations
"""

SCRIPTS[5] = r"""
#A 5::Training is unstable and the loss diverges — give the sequence of optimiser-side interventions::CO3 · Apply–Analyse · 10 marks · ~3 pages::Optimiser sequence for unstable training
## First, be sure it is an optimiser problem
Divergence has three common causes that no optimiser fixes: a mis-scaled loss (forgetting to average over the batch), a bad learning rate, and unnormalised inputs. Check these first: print the loss on a single batch, confirm it decreases when you overfit that batch, and confirm the learning rate is not larger than the reciprocal of the largest curvature. The sequence below assumes the data pipeline is sane and the architecture is correct.
The order is deliberate: each rung of the ladder addresses a failure mode that the rungs below cannot fix, and each is cheaper to reason about than the next.
## Rung 1 — Initialisation
A network with badly scaled initial weights has activations that either vanish or explode before the first update. Two standard choices, for a layer with $n_{in}$ inputs and $n_{out}$ outputs:
@@ W_{ij}\sim\mathcal{N}\left(0,\frac{2}{n_{in}}\right)\quad\text{(He, for ReLU)}
@@ W_{ij}\sim\mathcal{N}\left(0,\frac{1}{n_{in}}\right)\quad\text{(Xavier, for tanh)}
Both keep the variance of the activations constant across layers. The bias is initialised to zero (or a small positive value for ReLU to avoid dead units) and the last layer's weights are scaled down when using a softmax loss. Orthogonal initialisation for recurrent weights is the analogue for sequences.
## Rung 2 — Stochastic gradient descent with momentum
The baseline that everything is compared against:
@@ v_{t}=\mu v_{t-1}-\eta\nabla J(\theta_{t}),\qquad \theta_{t+1}=\theta_{t}+v_{t}
Momentum accumulates a running average of gradients, so it damps oscillation across steep directions and accelerates along shallow ones. It fixes **ill-conditioning** — the classic ravine — but it uses one global learning rate, so it cannot help when different parameters need different step sizes. If the loss still oscillates, reduce the learning rate; if it is flat for long stretches, momentum is not your problem.
@fig fig3_opt||Paths on an ill-conditioned quadratic. Plain descent zig-zags across the steep direction; momentum smooths it; the adaptive methods equalise the two directions.
## Rung 3 — RMSProp
Divide each coordinate's step by the root of its recent squared gradient:
@@ s_{t}=\rho s_{t-1}+(1-\rho)g_{t}^{2},\qquad \theta_{t+1}=\theta_{t}-\frac{\eta}{\sqrt{s_{t}}+\epsilon}g_{t}
with a decay of about $0.9$. A parameter with consistently large gradients gets a small effective step; a rare parameter with small gradients gets a large one. This is what fixes **per-parameter scaling**: embeddings, sparse features and biases no longer need hand-tuned rates.
## Rung 4 — Adam
Adam adds momentum to the adaptive denominator and corrects the initialisation bias of both moving averages:
@@ m_{t}=\beta_{1}m_{t-1}+(1-\beta_{1})g_{t},\qquad s_{t}=\beta_{2}s_{t-1}+(1-\beta_{2})g_{t}^{2}
@@ \hat{m}_{t}=\frac{m_{t}}{1-\beta_{1}^{t}},\qquad \hat{s}_{t}=\frac{s_{t}}{1-\beta_{2}^{t}},\qquad \theta_{t+1}=\theta_{t}-\eta\frac{\hat{m}_{t}}{\sqrt{\hat{s}_{t}}+\epsilon}
Defaults are $\beta_{1}=0.9$, $\beta_{2}=0.999$, $\epsilon=10^{-8}$ and a step size of $10^{-3}$. Adam is the composition of rungs 2 and 3 plus bias correction, which is why it is the last rung and not the first: if it fails you have no simpler fallback left.
## Rung 5 — Guards around whichever optimiser you chose
+ **Gradient clipping** at a norm of one to five: rescale the gradient when its norm exceeds the threshold, $g\leftarrow g\,c/\|g\|$. Mandatory for recurrent nets, useful everywhere.
+ **Learning-rate warm-up** over the first few hundred steps so that the adaptive estimates can settle before large steps are taken.
+ **A decay schedule** — cosine or step decay — to finish training without oscillation.
+ **Loss-scale diagnostics**: log the gradient norm per layer; a single exploding layer localises the fault.
@table 120,200,177
@hdr Symptom | Rung that fixes it | Why
@row loss becomes NaN in the first epoch | 1, then 5 | scale of initial activations, then clipping
@row oscillating loss, slow progress | 2 | momentum damps the cross-ravine component
@row some layers learn, others frozen | 3 | per-coordinate scaling
@row fast at first, then stuck | 4 | momentum plus adaptive denominator
@row periodic spikes late in training | 5 | step size too large near a minimum
@end
@box tip||How to answer the "sequence" question
The examiner is testing whether you can order interventions by *cause*, not whether you can list optimisers. Write the ladder, and against each rung write the failure it repairs and the observable that tells you to climb to the next rung. Finish with the cheap guards — clipping and warm-up — because they are what makes Adam usable in practice.
@end
@key Initialisation fixes scale, momentum fixes ill-conditioning, RMSProp fixes per-parameter scale, Adam combines the last two with bias correction, and clipping plus warm-up make any of them safe.
@box ok||Examiner's checklist
- Rules out data and learning-rate bugs before blaming the optimiser.
- Gives the He and Xavier variance formulas.
- Writes the update rule for each rung, including Adam's bias correction.
- States the failure each rung repairs.
- Adds clipping, warm-up and a schedule as guards.
@end
@kw divergence; weight initialisation; He scaling; momentum; adaptive learning rate; RMSProp; Adam; bias correction; gradient clipping; warm-up
"""

SCRIPTS[6] = r"""
#A 6::Why is optimisation in deep learning different from pure optimisation?::CO3 · Understand–Analyse · 10 marks · ~3 pages::Why deep-network optimisation differs from pure optimisation
## The formal statement of the problem
Training minimises the expected risk, which we cannot compute, so we minimise the empirical risk on a sample:
@@ J(\theta)=\frac{1}{m}\sum_{i=1}^{m}L\left(f(x_{i};\theta),y_{i}\right)+\lambda\Omega(\theta)
Pure optimisation asks for the minimiser of $J$, careless of what $J$ is a proxy for. Deep learning asks for a parameter vector that **generalises**: the quantity we care about is the population risk, and the training objective is only an estimate of it. That single sentence generates most of the differences below.
## Difference 1 — the objective is a surrogate
Minimising the training loss too well is harmful; the gap between population and training risk grows with capacity. Optimisation theory says "lower is better" at every step; deep learning says "lower on the validation set is better, and the training loss is a means". This is why early stopping, which *deliberately stops short of the minimum*, is a legitimate algorithm.
## Difference 2 — the landscape is non-convex
A network's loss is non-convex in the parameters: permuting the units of a hidden layer gives the same function, so for $k$ hidden units there are $k!$ equivalent minima, and similarly for scaling symmetries. Optimisation theory's convergence guarantees for convex problems do not transfer. Empirically, however, the picture is less grim than the theory suggests:
- **Local minima are rare in high dimension.** A critical point that is a local minimum in all $n$ directions requires all $n$ Hessian eigenvalues to be positive; for a random landscape in $n$ dimensions most critical points are saddles, because a saddle needs only one negative eigenvalue.
- **Saddle points dominate.** Their number grows exponentially with $n$, and gradient descent spends most of its time in the neighbourhood of plateaus around them, where the gradient is small but the Hessian has both signs.
- **Good minima are connected.** Many distinct minima reach the same test accuracy; mode-connectivity studies show wide flat basins that are easy to reach by stochastic descent.
@box note||The consequence for the exam answer
Say clearly: *the difficulty is not escaping bad local minima, it is the sheer number of saddle points and plateaus, plus the fact that we do not want the minimum of this particular function anyway.* This is the sentence most answers miss.
@end
## Difference 3 — gradients are stochastic
We never see the full gradient, only its estimate on a mini-batch of size $B$. The estimator is unbiased but has variance that decreases as $B$ grows:
@@ \mathbb{E}\left[\|\nabla\hat{J}_{B}-\nabla J\|^{2}\right]=\frac{\sigma^{2}}{B}
Noise acts as a regulariser (it prevents settling into sharp minima), allows escape from bad regions, and makes training scale with data. But it also means the loss curve is non-monotone and the stopping criterion must be statistical, not exact.
## Difference 4 — scale and conditioning
Networks have between a million and a billion parameters, and the condition number of the Hessian can exceed $10^{6}$: some directions are almost flat (unidentifiable combinations of weights) and some are extremely steep. First-order methods then need many steps, which is exactly the motivation for the adaptive methods of the previous answer. Parameter count also makes second-order methods (Newton, natural gradient) prohibitively expensive.
## Difference 5 — the target is not stationary
In pure optimisation the data and the objective are fixed. In deep learning the distribution of the data may drift, the loss may be non-decomposable, and the model is retrained continuously. Added to this, the objective has a huge flat region, so "convergence" must be defined by validation performance rather than by the gradient norm falling below a threshold.
@table 120,120,157
@hdr Aspect | Pure optimisation | Deep learning
@row what is minimised | the given objective | a sample estimate of it
@row landscape | convex by assumption | non-convex, symmetry, saddles
@row gradient | exact | mini-batch estimate with variance
@row dimension | moderate | $10^{6}$–$10^{9}$
@row stopping rule | gradient norm below a threshold | validation loss stops improving
@row success metric | distance to the optimum | test error on unseen data
@row local minima | the danger | rare and usually benign
@end
@key Deep learning optimises a surrogate on a sampled, non-convex, extremely ill-conditioned surface, so a good optimiser is judged by generalisation, not by how close it gets to the minimum of the training loss.
@box ok||Examiner's checklist
- States that the training loss is a proxy for the population risk.
- Mentions non-convexity and the symmetry of the parameterisation.
- Explains that saddles and plateaus, not local minima, are the practical obstruction.
- Treats stochasticity as both a cost and a regulariser, with the variance formula.
- Contrasts stopping rules and success metrics in a table.
@end
@kw empirical risk; surrogate objective; non-convexity; saddle point; plateau; mini-batch noise; ill-conditioning; parameter symmetry; generalisation gap
"""

SCRIPTS[7] = r"""
#A 7::Compare AdaGrad, RMSProp and Adam and justify which one you would choose::CO3 · Understand–Apply · 10 marks · ~2.5 pages::AdaGrad versus RMSProp versus Adam
## The common idea
All three replace the single global learning rate with a per-parameter step that is divided by a history of that parameter's gradients. Writing $g_{t}$ for the gradient at step $t$ and $s_{t}$ for the accumulator, they differ only in how the accumulator is formed and whether a momentum term is added.
## AdaGrad
@@ s_{t}=s_{t-1}+g_{t}^{2},\qquad \theta_{t+1}=\theta_{t}-\frac{\eta}{\sqrt{s_{t}+\epsilon}}g_{t}
The accumulator is a **sum over all past steps**, so it grows without bound and the effective rate decays monotonically. Parameters that have received large gradients are slowed permanently; parameters with rare, informative gradients keep a usable rate. The decay is roughly $\eta/\sqrt{t}$ for a stationary gradient, which is why AdaGrad is provably good for convex problems with sparse gradients. The same property is its weakness: in a long training run the accumulator becomes so large that learning effectively stops before the model has converged — *the learning rate dies*.
## RMSProp
@@ s_{t}=\rho s_{t-1}+(1-\rho)g_{t}^{2},\qquad \theta_{t+1}=\theta_{t}-\frac{\eta}{\sqrt{s_{t}+\epsilon}}g_{t}
RMSProp replaces the sum by an **exponential moving average** with decay around $0.9$, so the accumulator has an effective memory of about ten steps. Old gradients are forgotten, the denominator stays bounded, and learning continues indefinitely. It was designed exactly to fix the stall of AdaGrad, and it works well on non-stationary objectives such as mini-batch training.
## Adam
@@ m_{t}=\beta_{1}m_{t-1}+(1-\beta_{1})g_{t},\qquad s_{t}=\beta_{2}s_{t-1}+(1-\beta_{2})g_{t}^{2}
@@ \hat{m}_{t}=\frac{m_{t}}{1-\beta_{1}^{t}},\qquad \hat{s}_{t}=\frac{s_{t}}{1-\beta_{2}^{t}},\qquad \theta_{t+1}=\theta_{t}-\eta\frac{\hat{m}_{t}}{\sqrt{\hat{s}_{t}}+\epsilon}
Adam is RMSProp plus **momentum on the numerator** plus **bias correction**. The bias correction matters: since the moving averages start at zero, the raw average is biased towards zero by a factor that is severe for the first few dozen steps — with a decay of $0.999$ the factor is $0.001$ at the first step. Dividing by the correction factor makes the estimate unbiased and allows a default step size of $10^{-3}$ to work from step one.
## Comparison
@table 82,120,140,155
@hdr | AdaGrad | RMSProp | Adam
@row accumulator | sum of squares | moving average of squares | moving averages of gradient and square
@row memory of past | infinite | about ten steps | hundreds to thousands of steps
@row momentum | no | no | yes, bias-corrected
@row behaviour late in training | stalls | steady | steady
@row extra memory | one scalar per parameter | one scalar | two scalars
@row hyper-parameters | step size | step size, decay | step size, two decays, epsilon
@row best for | sparse features, convex, short runs | non-stationary, recurrent nets | default for most deep nets
@row known weakness | premature stall | needs a tuned decay | can generalise slightly worse than plain momentum
@end
## Which to choose, and why
+ **Default:** Adam with a step size of $10^{-3}$, because it is robust to the scale of each parameter and converges quickly on most architectures; it is the right first attempt on an unfamiliar problem.
+ **Sparse or bag-of-words style inputs with a convex model:** AdaGrad, where its long memory is an advantage rather than a stall.
+ **Recurrent networks and non-stationary objectives:** RMSProp or Adam; RMSProp's single accumulator is cheaper and sometimes more stable on long sequences.
+ **When the last fraction of accuracy matters (vision):** stochastic descent with momentum and a cosine schedule often generalises better than Adam, because the per-parameter scaling can lead it into sharper minima.
@box tip||A defensible exam answer
State the update rules, then reduce all three to one sentence: *AdaGrad divides by the root of the accumulated squared gradient, RMSProp divides by the root of a decaying average of it, and Adam also averages the gradient itself and corrects for the zero-initialisation bias.* Then justify a choice by the property that matters: sparsity → AdaGrad, non-stationarity → RMSProp, general default → Adam.
@end
@key The three algorithms are one family: Adam is RMSProp plus momentum plus bias correction, and RMSProp is AdaGrad with a forgetting factor; the choice is decided by whether you need long memory of sparse gradients or a bounded, adaptive step.
@box ok||Examiner's checklist
- Writes all three update rules with the accumulator defined.
- Explains the stall of AdaGrad and the effective memory of RMSProp.
- Derives the need for Adam's bias correction.
- Compares memory, hyper-parameters and regime of use.
- Commits to a recommendation with a reason.
@end
@kw adaptive learning rate; accumulator; exponential moving average; effective memory; bias correction; sparse gradients; non-stationary objective; momentum; generalisation
"""

SCRIPTS[8] = r"""
#A 8::Discuss the trade-offs between early stopping, dropout and data augmentation::CO3 · Analyse–Evaluate · 10 marks · ~3 pages::Early stopping, dropout and augmentation
## Three regularisers at three levels
All three fight overfitting, but they act on different objects, and that is what makes the trade-offs examinable:
@table 96,196,205
@hdr | Operates on | Mechanism
@row early stopping | the number of optimisation steps | restricts the distance travelled from the initialisation
@row dropout | the activations | injects multiplicative noise, trains an ensemble
@row augmentation | the training data | enlarges the support of the empirical distribution
@end
## Early stopping
Train, monitor the validation loss each epoch, and return the parameters from the epoch with the lowest validation loss. Its theoretical justification is a Taylor expansion of the training loss around the initialisation: for a quadratic objective, stopping after a number of steps is equivalent to a ridge penalty with
@@ \lambda\approx\frac{1}{\tau\eta}
where $\tau$ is the number of steps and $\eta$ the step size, so limiting the number of steps limits how far the weights can grow — early stopping *is* $L_2$ regularisation with a step-count hyper-parameter. Its cost is that it needs a validation split, and that split is data removed from training. It is otherwise free: no change to the model, no extra compute at inference, no extra hyper-parameter beyond the patience.
@fig fig3_early||Validation loss bottoming out; the weights at that epoch are the ones to keep. Everything after the dotted line is memorisation.
## Dropout
Discussed in detail earlier; for the trade-off what matters is that dropout is a *training-time* intervention with a *training-time* cost: two to three times more epochs, a noisier loss curve, and a need to raise the learning rate and lengthen the schedule. At inference it costs nothing. It is most effective when the overfitting is driven by co-adaptation among many dense units, and least effective in convolutional stacks, where weight sharing already limits capacity.
## Data augmentation
Generate new labelled examples by applying transformations that leave the label invariant: crops, flips, rotations, colour jitter, cutout; for audio, time shifts and masking; for text, synonym replacement and back-translation. Augmentation changes the *effective* dataset size, which is the only intervention with a guarantee that variance falls as the data grows. Its cost is domain knowledge — choosing a transform that is genuinely label-preserving — plus compute per epoch, and a risk: an aggressive transform (large rotations on digit recognition, horizontal flip on character recognition) teaches the model an invariance the task does not have, converting variance into bias.
## Head-to-head trade-offs
@table 84,124,140,149
@hdr | Early stopping | Dropout | Augmentation
@row extra data needed | validation split | none | none, but domain knowledge
@row training cost | none | 2–3× epochs | compute per epoch
@row inference cost | none | none (inverted) | none
@row main risk | noisy validation → wrong epoch | underfitting if the rate is too high | label-destroying transform
@row interacts with | learning-rate schedule | batch norm, weight decay | batch norm statistics
@row best when | any model, always safe | wide dense layers | images, audio, text
@row theoretical link | $L_2$ with a step-count coefficient | ensemble of $2^{n}$ nets | enlarged empirical distribution
@end
## Combining them
The three are complementary and are used together, but not blindly:
- Choose augmentation first — it is the only one that adds information rather than restricting the model.
- Add early stopping always, because it is free and protects against the tail of the curve.
- Add dropout only where capacity is concentrated: the classifier head, wide fully connected blocks. Skip it in convolutional trunks that already use batch normalisation.
- Re-tune the schedule after adding any of them: all three lengthen the time to convergence, and a schedule tuned without dropout will stop training too early with it.
@box warn||What the exam is really testing
Not the definitions — those are one line each — but whether you can say *what each one costs and what it can break*. A candidate who writes "use all three for best accuracy" without mentioning the validation split, the epoch multiplier, or the label-destroying transform has not answered the question.
@end
@key Early stopping limits how far the weights travel, dropout averages over sub-networks at training time, and augmentation enlarges the data; the first is free but needs a validation split, the second costs epochs, the third costs compute and domain knowledge — and only the third adds information.
@box ok||Examiner's checklist
- Assigns each method to the level it acts on: steps, activations, data.
- Derives the early-stopping relation to the $L_2$ coefficient.
- Quantifies dropout's cost as training epochs, not arithmetic.
- Names the failure mode of an aggressive augmentation.
- Gives an order for combining them and says why.
@end
@kw early stopping; patience; effective $L_2$; dropout rate; data augmentation; label-preserving transform; effective dataset size; co-adaptation; convergence time
"""
