# -*- coding: utf-8 -*-
"""Unit IV — Convolutional neural networks."""

UNIT_INFO = {
    'unit': 4,
    'roman': 'IV',
    'label': 'UNIT IV',
    'title': 'Convolutional Neural Networks',
    'subtitle': 'Layer design, output geometry, parameter sharing and the prior that '
                'makes vision learnable',
}

GLANCE = [
    (1, "Designing a CNN: layers, kernels, strides, pooling",
     "Choose the geometry first — kernel, stride, padding — then let the numbers fall "
     "out of the output formula."),
    (2, "How kernel, stride and padding set the output size and the cost",
     "The output formula and the FLOP count; always give the worked numbers."),
    (3, "Fully connected versus convolutional layers",
     "Local connectivity and shared weights turn a quadratic parameter bill into a "
     "constant one."),
    (4, "Convolution and pooling as architectural priors",
     "They encode translation equivariance and local tolerance — powerful when true, "
     "harmful when false."),
    (5, "Pooling when the exact location matters",
     "Max-pooling throws away position; use stride-1 convolutions, dilated kernels or "
     "attention when coordinates are the answer."),
    (6, "Flatten versus global average pooling in a multiclass CNN",
     "GAP removes the position-dependent dense block and the parameter explosion that "
     "comes with it."),
    (7, "Underfitting caused by pooling, and what to do instead",
     "Aggressive pooling destroys the evidence before the classifier sees it."),
    (8, "Justifying a CNN architecture for a real application",
     "Derive the design from the data: resolution, invariance, class count, compute "
     "budget."),
]

REVISION = [
    (1, "A CNN is a stack that shrinks spatial size and grows channel count, ending in "
        "global average pooling and a small softmax.",
     "Forgetting to say how the kernel size and the receptive field relate to the "
        "object size in the data."),
    (2, "Output size by the floor formula; FLOPs are twice the product of output size, "
        "kernel area and both channel counts.",
     "Mixing FLOPs with multiply–accumulate operations, or forgetting that padding "
        "must preserve the size when the stride is one."),
    (3, "Local connectivity plus weight sharing: the same filter slides over the image, "
        "so parameters are independent of the image size.",
     "Saying a CNN 'has fewer layers' — it does not; it has fewer parameters."),
    (4, "Convolution encodes translation equivariance and locality; pooling encodes "
        "small-shift tolerance.",
     "Claiming a CNN is fully translation invariant — it is equivariant, and only "
        "approximately invariant after pooling."),
    (5, "Max-pooling is compatible with 'is there a cat' and incompatible with 'where "
        "is the cat'.",
     "Answering 'use more pooling' — the question asks for the opposite."),
    (6, "Flatten gives height × width × channels inputs to the dense layer; GAP gives "
        "one average per channel.",
     "Forgetting that GAP is what makes the network input-size agnostic."),
    (7, "Excess pooling removes the fine detail the label depends on; replace it with "
        "stride-1 or dilated convolutions.",
     "Reducing capacity is the wrong reflex when the model is already underfitting."),
    (8, "Justify each block by a property of the data, then by the compute budget.",
     "Quoting a famous architecture without connecting it to the problem's "
        "resolution, invariance or class count."),
]

SCRIPTS = {}

SCRIPTS[1] = r"""
#A 1::Design a CNN for an image classification task — layers, kernel sizes, strides and pooling::CO4 · Apply–Create · 10 marks · ~3 pages::CNN design: layers, kernels, strides and pooling
## The design problem
A convolutional network is a sequence of stages. Each stage applies convolutions that **shrink the spatial grid and grow the channel count**, and the network ends with a classifier head that maps a feature vector to class scores. Designing the network means choosing five numbers per stage: the kernel size $K$, the number of filters $C_{out}$, the stride $S$, the padding $P$, and whether a pooling layer follows. Every choice has a consequence that must be stated.
@fig fig4_arch||A canonical design: three convolution stages with pooling, then global average pooling and a softmax head.
## Layer by layer
### Convolutional layer
A filter of size $K\times K\times C_{in}$ slides over the input; at every position it computes a dot product plus a bias, producing one value of one output channel. With $C_{out}$ filters the layer learns $C_{out}$ different detectors. The output is
@@ y_{i,j,c}=\sum_{u=0}^{K-1}\sum_{v=0}^{K-1}\sum_{d=0}^{C_{in}-1}w_{u,v,d,c}\,x_{i+u,\,j+v,\,d}+b_{c}
Key design points:
- **Kernel size.** A $3\times3$ kernel is the default: two stacked $3\times3$ convolutions see a $5\times5$ region with $2\cdot9=18$ weights per channel pair instead of $25$, so depth buys receptive field more cheaply than width. $1\times1$ convolutions mix channels and are used to change depth; $5\times5$ or $7\times7$ appear only in the first layer, where the input has three channels and a large kernel is affordable.
- **Number of filters.** Grow geometrically with depth ($32\to64\to128$) while the spatial size halves, so that the total activation volume — and therefore the memory — stays roughly constant.
- **Stride.** A stride of two halves the resolution inside the convolution itself and is the modern replacement for a pooling layer; a stride of one preserves resolution.
- **Padding.** Padding of about half the kernel with a unit stride keeps the size unchanged ("same"), no padding shrinks it ("valid").
### Activation
ReLU, applied elementwise: cheap, and it does not saturate for positive inputs, which keeps gradients alive in deep stacks. Its known failure is the dead unit; leaky ReLU or ELU is the fix when it appears.
### Pooling
Max-pooling with a $2\times2$ window and stride two halves both dimensions and keeps the strongest response in each window, giving small-shift tolerance. Average pooling is used instead at the very end of some architectures; global average pooling collapses each channel to one number.
### Normalisation
Batch normalisation after the convolution and before the activation stabilises the distribution of pre-activations, allows a learning rate roughly ten times larger, and acts as a mild regulariser.
### Classifier head
Global average pooling, then one dense layer of width equal to the number of classes, then softmax. Dropout is optional; with global pooling there are very few parameters left to overfit.
## A complete specification
@table 66,96,66,66,90,113
@hdr Stage | Layer | Kernel | Stride/pad | Output | Parameters
@row 0 | input | — | — | $224^{2}\times3$ | 0
@row 1 | conv + BN + ReLU | $3\times3$, 32 | 1 / same | $224^{2}\times32$ | 896
@row 2 | max-pool | $2\times2$ | 2 / valid | $112^{2}\times32$ | 0
@row 3 | conv + BN + ReLU | $3\times3$, 64 | 1 / same | $112^{2}\times64$ | 18,496
@row 4 | max-pool | $2\times2$ | 2 / valid | $56^{2}\times64$ | 0
@row 5 | conv + BN + ReLU | $3\times3$, 128 | 1 / same | $56^{2}\times128$ | 73,856
@row 6 | max-pool | $2\times2$ | 2 / valid | $28^{2}\times128$ | 0
@row 7 | global average pool | — | — | $128$ | 0
@row 8 | dense + softmax | — | — | $10$ | 1,290
@end
The parameter count of a convolution is
@@ \#\text{params}=K^{2}\,C_{in}\,C_{out}+C_{out}
so stage 3 costs $9\cdot32\cdot64+64=18{,}496$ — independent of the image size, which is the whole point of the architecture.
## The rules that keep a design sane
+ Start from the data: object size in pixels fixes the receptive field, and the receptive field fixes the depth.
+ Keep the output volume (height × width × channels) roughly constant across stages; halve the spatial size when you double the channel count.
+ Prefer $3\times3$ kernels and stack them; use stride or pooling for the downsampling, not both at once.
+ Check every stage with the output-size formula on paper before writing code.
+ End with global average pooling rather than flatten; the parameter saving is a factor of tens.
@box tip||Receptive field arithmetic
The receptive field after $l$ layers grows as the kernel size plus the accumulated product of the strides: $r_{l}=r_{l-1}+(K_{l}-1)\prod_{i<l}S_{i}$ with $r_{0}=1$. Two $3\times3$ convolutions give $5\times5$; three give $7\times7$. A design that never exceeds the object size in pixels cannot see the object as a whole.
@end
@key Design a CNN outward from the data: the object size sets the receptive field, the receptive field sets the depth, and the compute budget sets the channel widths — with the output-size formula checked at every stage.
@box ok||Examiner's checklist
- Lists the layer types and gives a concrete kernel, stride and padding for each.
- Justifies $3\times3$ kernels by the parameter arithmetic of stacked filters.
- Uses the output-size formula and the parameter formula.
- Explains the shrink-space / grow-channel pattern.
- Ends with global pooling plus softmax and says why.
@end
@kw convolution; kernel; stride; padding; pooling; receptive field; channel depth; batch normalisation; global average pooling; softmax head
"""

SCRIPTS[2] = r"""
#A 2::Derive the effect of kernel size, stride and padding on output size and computational cost, with a worked example::CO4 · Apply–Analyse · 10 marks · ~3 pages::Kernel, stride and padding: output size and cost
## Counting the positions
A kernel of width $K$ placed on an input of width $W$ with padding $P$ on both sides moves in steps of $S$. The number of positions at which the kernel fits completely is the number of integers $i\geq0$ with $iS\leq W-K+2P$, so that
@@ O=\left\lfloor\frac{W-K+2P}{S}\right\rfloor+1
The floor is essential: a kernel that would hang over the edge is simply not placed. The same formula applies independently to height and width, and it is the single most useful line in the whole unit.
## The three regimes
@table 96,120,120,161
@hdr Regime | Setting | Output size | Typical use
@row valid | no padding | smaller than the input | shrinking at every layer
@row same | half-kernel padding, unit stride | equal to the input | keeping resolution while adding depth
@row full | maximum padding | larger than the input | transposed convolution, upsampling
@row strided | stride above one | about the input over the stride | learned downsampling
@row dilated | spacing between taps | effective kernel grows with spacing | wide context, no resolution loss
@end
@fig fig4_sizes||The same $6\times6$ input with a $3\times3$ kernel: valid stride 1 gives $4\times4$, valid stride 2 gives $2\times2$, and padding 1 with stride 1 keeps $6\times6$.
## Worked example
Take an input of $224\times224\times3$ and a convolutional layer with $K=3$, $S=1$, $P=1$ and $C_{out}=64$.
+ **Output size.** $O=(224-3+2)/1+1=224$, so the map is $224\times224\times64$ — a "same" convolution.
+ **Parameters.** $K^{2}C_{in}C_{out}+C_{out}=9\cdot3\cdot64+64=1{,}792$.
+ **Multiply–accumulate operations.** Each output element needs $K^{2}C_{in}=27$ such operations, so
@@ \text{MACs}=H_{out}W_{out}C_{out}K^{2}C_{in}=224\cdot224\cdot64\cdot27=86.7\times10^{6}
+ **Floating-point operations.** One multiply–accumulate is one multiply and one add, so
@@ \text{FLOPs}=2\,H W K^{2}C_{in}C_{out}=173.4\times10^{6}
+ **Effect of stride.** With a stride of two the output becomes $112\times112\times64$ and the cost falls by a factor of four — downsampling early is the cheapest optimisation available.
+ **Effect of doubling the kernel.** A $5\times5$ kernel at the same output size multiplies both the parameters and the cost by $25/9\approx2.8$.
## The general cost model
For a whole network the cost is the sum over layers of
@@ C_{l}=2\,H_{l}W_{l}K_{l}^{2}C_{l}^{in}C_{l}^{out}
and the memory is dominated by the activations that must be stored for the backward pass, $H_{l}W_{l}C_{l}$ per layer per example. Two consequences worth stating:
- Cost is **linear in the number of pixels and quadratic in the kernel width**, so stacks of small kernels are strictly cheaper than one wide kernel for the same receptive field.
- Cost is **linear in both channel counts**, so the first layer — three input channels — is cheap, while the last convolutional layer with many channels is expensive even though its map is small.
@box note||Why this matters in an exam
Numbers separate a real answer from a recitation. If you can say "a $3\times3$ convolution on a $224\times224\times3$ input with 64 filters costs 87 million multiply–accumulates and 1,792 weights", you have demonstrated that you understand both the geometry and the parameter sharing.
@end
@key Output size is the floor of the padded width minus the kernel over the stride, plus one; cost is twice the product of output size, kernel area and both channel counts — stride is the cheap way to cut cost, kernel width is the expensive one, and the parameter count does not depend on the image size at all.
@box ok||Examiner's checklist
- Derives the output formula from the count of valid kernel positions, floor included.
- Distinguishes valid, same, full, strided and dilated.
- Works one full numeric example: output size, parameters, operations, FLOPs.
- Shows the effect of changing stride and changing kernel size.
- States the general cost model and the memory term.
@end
@kw output size formula; valid padding; same padding; stride; dilation; receptive field; multiply–accumulate; FLOPs; parameter count; activation memory
"""

SCRIPTS[3] = r"""
#A 3::Compare fully connected and convolutional layers in terms of parameter sharing, local connectivity and scalability::CO4 · Understand–Analyse · 10 marks · ~2.5 pages::FC versus CNN: sharing, locality, scalability
## The parameter arithmetic
Consider an input image of $256\times256\times3$ and a hidden layer of 1,000 units.
- **Fully connected:** every input element connects to every unit, so the weight matrix is $196{,}608\times1{,}000$ — about 196 million parameters in one layer.
- **Convolutional:** a bank of 64 filters of size $3\times3\times3$ has $9\cdot3\cdot64=1{,}728$ weights, and the layer still produces $256^{2}\times64$ activations.
The ratio is five orders of magnitude, and it comes entirely from two structural choices.
## Local connectivity
A convolutional unit sees only a $K\times K$ neighbourhood, so
@@ y_{i,j}=\sum_{u,v}w_{u,v}\,x_{i+u,j+v}+b
instead of a sum over the whole input. The assumption is that nearby pixels are the ones that matter for a local feature — an edge, a corner, a colour transition. The receptive field grows with depth, so locality at each layer does not limit the global context the network can eventually represent: three $3\times3$ layers already see $7\times7$.
## Weight sharing
The same $K^{2}C_{in}$ weights are reused at every spatial position. Equivalently, a convolution is a fully connected layer in which most weights are tied to each other: the weight from input position offset by $(u,v)$ to an output position is the same for every output position. Three consequences follow:
+ **Parameter count is independent of the image size.** Doubling the resolution does not change the number of weights at all; it only changes the number of activations.
+ **Translation equivariance is built in.** If the input shifts by one pixel, the output shifts by one pixel, because the same filter is applied everywhere.
+ **Statistical strength.** Every position provides a training example for the same filter, so a filter is learned from millions of patches rather than from one.
@fig fig4_fc_cnn||Left: a fully connected layer, one weight per input–output pair. Right: a convolutional layer, a few weights shared across positions.
## Scalability
@table 96,130,130,141
@hdr Property | Fully connected | Convolutional
@row parameters | grow with the square of the input size | independent of resolution
@row memory for weights | can exceed the device memory | a few kilobytes per filter
@row inductive bias | none; must learn locality | locality and translation equivariance
@row data efficiency | needs many examples per pixel | exploits every patch
@row sensitivity to a shift | the input vector changes entirely | the output shifts, the values do not
@row best used for | tabular data, final classifier | images, spectrograms, sequences
@end
## What is lost
The two priors are assumptions, and they are wrong when the data does not respect them:
- **Global relationships** are not modelled by a small kernel; distant parts of the image interact only after many layers, or never.
- **Arbitrary orientation** is not encoded — a filter trained on upright digits will not fire on rotated ones unless augmentation teaches it.
- **Exact coordinates** are progressively destroyed by strided convolutions and pooling, which is fatal for tasks such as keypoint localisation.
A modern network therefore mixes the two: convolutional trunks for the local structure, and a small fully connected or attention head for the global decision.
@box key||The one-sentence answer
A fully connected layer treats every input position as an independent feature, so its parameter count explodes with resolution and it must learn from scratch that nearby pixels are related; a convolutional layer hard-codes locality and shares weights across positions, which cuts the parameters by orders of magnitude and buys translation equivariance for free.
@end
@key Local connectivity says "look here", weight sharing says "look for the same thing everywhere" — together they reduce the parameter bill from quadratic in the input size to a constant, and make the model independent of image size.
@box ok||Examiner's checklist
- Puts real numbers on the parameter counts.
- Defines local connectivity and weight sharing formally.
- Shows the parameter count is independent of resolution.
- States equivariance, and why it is equivariance rather than invariance.
- Names the situations where the priors fail.
@end
@kw local receptive field; weight sharing; parameter tying; translation equivariance; inductive bias; data efficiency; scalability; resolution independence
"""

SCRIPTS[4] = r"""
#A 4::Discuss convolution and pooling as architectural priors — their benefits and their limitations::CO4 · Analyse–Evaluate · 10 marks · ~2.5 pages::Convolution and pooling as architectural priors
## What a prior is
A prior is a constraint on the hypothesis space that is imposed before any data is seen. Convolution and pooling impose two:
+ **Locality and stationarity:** the same feature detector is useful at every position, and it only needs a small neighbourhood. This is the prior of *translation equivariance*.
+ **Local tolerance:** small shifts, and small deformations, should not change the answer much. This is the prior of *approximate invariance*, implemented by pooling and stride.
Inserting a correct prior reduces the number of examples needed to learn; inserting a wrong one caps the achievable accuracy.
@fig fig4_prior||Top: the same filter responds at the new position when the object moves. Bottom: after $2\times2$ pooling a shift of one cell disappears, so the pooled map is identical.
## Benefits
- **Sample efficiency.** Because each filter is trained by every position, a convolutional model learns from far fewer labelled images than a dense network with the same expressive power.
- **Parameter efficiency.** A factor of $10^{4}$–$10^{5}$ in weights, which translates directly into memory, speed and the ability to run on small devices.
- **Equivariance is exact.** For a convolution without padding artefacts, shifting the input shifts the feature map exactly. Pooling, applied after, coarsens this into tolerance: a shift smaller than the pooling stride leaves the pooled map unchanged.
- **Compositionality.** Stacking builds a hierarchy — edges, then textures, then parts, then objects — which matches the statistics of natural images and is what makes deep CNNs interpretable layer by layer.
## Limitations
@table 96,196,205
@hdr Prior | Assumption | Where it fails
@row locality | relevant evidence is nearby | global context: scene classification, long-range dependencies
@row weight sharing | the same detector is useful everywhere | position-dependent classes: "sky above, road below"
@row translation equivariance | a shifted object is the same object | tasks needing coordinates: detection offsets, keypoints
@row pooling invariance | small shifts are irrelevant | fine-grained recognition, counting, localisation
@row fixed grid | data lie on a regular lattice | point clouds, graphs, meshes
@row fixed kernel | scale is known in advance | objects at wildly different scales without pyramids
@end
Each row is a real failure mode with a known remedy: global context via attention or dilated convolutions; position dependence via positional channels or by not sharing the last layers; localisation via stride-1 features and skip connections; scale via feature pyramids or multi-scale training; irregular domains via graph convolution.
## The cost of removing a prior
Capsule networks, vision transformers and dense networks with learned position embeddings all abandon one or both priors, and all pay for it: they need far more data or much stronger augmentation, and they are usually heavier to train. The empirical lesson of the last decade is that a prior is a loan against data — cheap when the assumption holds, expensive when it does not.
@box warn||Two claims that lose marks
"CNN is translation invariant." It is *equivariant*; invariance only appears approximately after pooling or global averaging, and only for shifts smaller than the pooling window.
"Pooling gives invariance to rotation and scale." It does not; it gives tolerance to small translations. Rotation and scale invariance come from augmentation, multi-scale features, or equivariant architectures.
@end
@key Convolution builds in locality and weight sharing (equivariance), pooling builds in tolerance to small shifts (approximate invariance); both are loans against data that pay off enormously on natural images and default badly on coordinates, global context or irregular domains.
@box ok||Examiner's checklist
- Defines a prior and names the two priors precisely.
- Gives benefits with mechanisms, not adjectives: sample efficiency, parameters, exact equivariance, hierarchy.
- Gives at least four limitations with the remedy for each.
- Distinguishes equivariance from invariance.
- Notes the data cost of abandoning the prior.
@end
@kw inductive bias; translation equivariance; approximate invariance; locality; stationarity; pooling; sample efficiency; receptive field; attention as a global prior
"""

SCRIPTS[5] = r"""
#A 5::A task needs the exact location of an object — discuss pooling and propose a better strategy::CO4 · Analyse–Create · 10 marks · ~2.5 pages::Pooling where localisation matters
## What pooling does to position
Max-pooling with window $k$ and stride $s$ maps each window to a single number. Every position inside a window produces the same output, so the map has lost all information finer than the stride — formally, the pooled representation is invariant to translations by less than the stride. For classification that is exactly what we want: "there is a tumour in this scan" should not depend on a two-pixel shift. For localisation it is a disaster: the answer *is* the coordinate.
@fig fig4_pool||Max-pooling halves the grid and keeps the strongest response; the peak survives in value but its position is quantised to the block.
Quantitatively, if a network has four $2\times2$ pooling stages, one output cell corresponds to $16\times16$ input pixels. Recovering the position to one pixel from such a feature map is impossible without extra machinery; the best a naive decoder can do is half a cell in each direction.
## Strategies that keep position
+ **Reduce or remove pooling.** Use stride-1 convolutions throughout the trunk and down-sample only as much as the compute budget forces. Cost rises, but the feature map keeps its resolution.
+ **Dilated (atrous) convolutions.** Insert zeros between kernel taps so the receptive field grows without any reduction in resolution; the effective kernel grows with the spacing. A stack with spacings 1, 2, 4, 8 sees a wide context while every layer stays at full resolution — the design used in semantic segmentation.
+ **Encoder–decoder with skip connections.** Pool in the encoder to get context, then upsample and concatenate the high-resolution features from the encoder. The decoder regains the detail that the encoder discarded, and the skip connections carry the coordinates.
+ **Transposed convolution instead of unpooling.** Learn the upsampling instead of repeating values; it is the standard decoder operation.
+ **Predict offsets, not masks.** Regress the box or the keypoint coordinates directly from a coarse feature map with a small head, using an offset term so that the sub-cell position is representable.
+ **Soft-argmax instead of max.** Replace the hard maximum by a weighted average over positions using a softmax of the activations, which is differentiable and returns a sub-pixel coordinate.
+ **Attention or deformable sampling.** Let the network sample features at learned offsets, so the sampling grid follows the object rather than the lattice.
## Choosing between them
@table 120,180,197
@hdr Requirement | Strategy | Cost
@row coarse localisation (bounding box) | keep the last pooling, add a regression head | small head
@row pixel-accurate segmentation | skip connections, U-Net decoder | decoder parameters
@row full-resolution, wide context | dilated convolutions | compute at full resolution
@row sub-pixel keypoints | soft-argmax or offset regression | tiny head
@row variable object scale | feature pyramid over several strides | memory
@end
@box tip||Framing the answer
Start from the trade-off in one line: *pooling buys invariance by destroying position, so any task whose label depends on position must limit it.* Then give the alternatives in order of intrusiveness — remove, replace, or recover. That structure is what earns the marks, not the list itself.
@end
@key Pooling is an invariance operator, so it is incompatible with a task whose answer is a coordinate: keep resolution with stride-1 or dilated convolutions, restore it with skip connections, or predict the offset explicitly with a sub-pixel head.
@box ok||Examiner's checklist
- Explains the quantisation of position caused by pooling, with the stride-sized figure.
- Names at least four alternatives with the mechanism of each.
- Gives the effective-kernel formula for dilation.
- Distinguishes classification, detection and segmentation requirements.
- Ends with a recommendation tied to the task.
@end
@kw localisation; invariance–equivariance trade-off; dilated convolution; atrous; skip connection; U-Net; transposed convolution; soft-argmax; offset regression; feature pyramid
"""

SCRIPTS[6] = r"""
#A 6::Describe the multiclass CNN pipeline and compare flatten with global average pooling::CO4 · Understand–Apply · 10 marks · ~2.5 pages::Multiclass CNN pipeline: flatten versus GAP
## The pipeline end to end
For a $C$-class problem the network computes a score vector and turns it into a distribution:
@@ z=W\,g(\cdot)+b,\qquad \hat{y}_{c}=\frac{e^{z_{c}}}{\sum_{k=1}^{C}e^{z_{k}}}
and is trained by minimising the categorical cross-entropy
@@ L=-\sum_{c=1}^{C}y_{c}\log\hat{y}_{c}
Because the target is one-hot this reduces to the negative log-probability of the true class. The gradient has the very clean form
@@ \frac{\partial L}{\partial z_{c}}=\hat{y}_{c}-y_{c}
which is why softmax with cross-entropy is the default head: the error signal is exactly the difference between predicted and true probability.
The full pipeline, in order:
+ Input normalisation (mean and standard deviation per channel).
+ Convolutional stages with batch normalisation and ReLU, alternating with downsampling.
+ An aggregation step that turns a height × width × channel tensor into a vector.
+ One dense layer to as many logits as there are classes.
+ Softmax, cross-entropy, backpropagation, and a mini-batch optimiser with a decaying learning rate.
## The aggregation step: flatten
Flatten reshapes the tensor into a vector of length height × width × channels and feeds it to a dense layer of $C$ units, giving the product of those two numbers as weights. For a $7\times7\times512$ map and 10 classes that is $250{,}880$ weights in the last layer alone — more than an entire small network.
@fig fig4_gap||Flatten passes every position to the classifier; global average pooling passes one number per channel.
## The aggregation step: global average pooling
Global average pooling averages each channel over its spatial extent:
@@ g_{c}=\frac{1}{HW}\sum_{i=1}^{H}\sum_{j=1}^{W}A_{i,j,c}
producing a $C$-dimensional vector, so the classifier has only the product of the channel count and the class count as weights — 5,120 in the example above, a factor of 49 fewer.
## Comparison
@table 92,180,225
@hdr Property | Flatten | Global average pooling
@row input to the head | height × width × channels | channels only
@row head parameters | large, grows with resolution | small, independent of resolution
@row position sensitivity | keeps it; can memorise layouts | discards it; treats evidence as a bag
@row overfitting risk | high, especially on small datasets | low
@row input-size flexibility | fixed; the dense layer pins the resolution | accepts any resolution
@row interpretability | none | each channel becomes a class-evidence map
@row failure mode | memorises background-position correlations | cannot localise or count
@end
## Why global pooling usually wins
Two arguments beyond the parameter count. First, the dense layer after flatten can exploit *where* a feature occurred, which on small datasets is usually a spurious correlation — the classic "cow on grass" failure — so removing the position information removes a shortcut. Second, global pooling makes the channel dimension the only interface to the classifier, which turns each channel into a class-evidence detector and yields class activation maps for free:
@@ M_{c}(i,j)=\sum_{k}w_{k,c}A_{i,j,k}
the weighted sum of the channels with the classifier's weights for class $c$. That is the standard weakly supervised localisation argument from Unit II.
@box note||Link to the earlier answer
In Unit II the softmax output layer was justified by the cross-entropy gradient; here the same head is kept and only the *aggregation* before it changes. Say this explicitly: the classifier is unchanged, the interface is what global pooling rewrites.
@end
@key Flatten hands the classifier every position and pays height × width × channels weights for the privilege; global average pooling hands it one number per channel, cutting the head by a factor of the map area, removing a shortcut, and making class activation maps possible.
@box ok||Examiner's checklist
- Writes softmax, cross-entropy and its gradient.
- Describes the pipeline in the right order.
- Gives the parameter counts for both choices on a concrete tensor.
- Compares position sensitivity, overfitting, input-size flexibility and interpretability.
- Recommends one and justifies it.
@end
@kw softmax; cross-entropy; logits; flatten; global average pooling; parameter explosion; class activation map; input-size flexibility; shortcut learning
"""

SCRIPTS[7] = r"""
#A 7::Pooling is suspected of causing underfitting — explain and propose alternatives::CO4 · Analyse–Create · 10 marks · ~2.5 pages::Underfitting caused by pooling
## How pooling can cause underfitting
Underfitting means the training loss itself is too high: the model cannot represent the training set. Pooling contributes to this in three distinct ways, and they should be separated in the answer.
+ **Information destruction.** Max-pooling keeps one value per window. If the label depends on several of the discarded values — the count of objects, the relative position of two parts, a thin structure — that evidence is gone before the classifier sees it. No amount of training can recover information that the forward pass removed.
+ **Capacity reduction.** The number of spatial positions reaching the later layers falls by four per $2\times2$ pooling stage. With fewer positions the later filters see fewer distinct contexts and the effective capacity of the network drops.
+ **Gradient sparsity.** Only the argmax position of each pooling window receives gradient. In a $2\times2$ window three quarters of the positions get nothing, which slows learning of exactly the fine detail that underfitting concerns.
A quick diagnostic: if training accuracy is low *and* the loss curve plateaus early while validation accuracy stays close to training accuracy, the problem is capacity or information, not regularisation. Removing pooling should then raise training accuracy — if it does, the diagnosis is confirmed.
## Alternatives, in order of intrusiveness
+ **Replace pooling with a strided convolution.** Downsampling is learned rather than fixed, so the network can choose to preserve whatever the task needs instead of keeping only the maximum. Costs a kernel-sized weight tensor per layer, and usually improves accuracy at equal output size.
+ **Reduce the number of pooling stages.** Keep $2\times2$ pooling only where the compute budget genuinely requires it; often one stage can be removed at a modest cost.
+ **Use average pooling or a blend.** Average pooling propagates all values, though diluted; intermediate norms interpolate between summing and taking the maximum.
+ **Dilated convolutions for context without downsampling.** The receptive field grows with the spacing of the taps while the resolution stays full.
+ **Attention pooling instead of fixed pooling.** Learn a weight per position and take a weighted average, so the network decides what to keep:
@@ g_{c}=\sum_{i,j}\alpha_{i,j,c}A_{i,j,c},\qquad \sum_{i,j}\alpha_{i,j,c}=1
+ **Increase capacity elsewhere** if the diagnosis is capacity rather than information: more channels, a deeper trunk, a higher input resolution. This is the remedy only after the pooling question is settled, because it addresses a different cause.
## What not to do
Reducing the model, adding dropout or adding weight decay are the reflexes for overfitting; applied to an underfitting model they make both curves worse. Similarly, replacing max-pooling by average pooling everywhere is rarely the answer — average pooling blurs, which on fine-grained tasks loses more than it gains.
@table 120,180,197
@hdr Remedy | Fixes | Cost
@row strided convolution | learned downsampling | weights per layer
@row fewer pooling stages | information loss | compute, memory
@row dilated convolution | context without loss | compute at full resolution
@row attention pooling | fixed, task-agnostic aggregation | small attention head
@row more channels or depth | genuine capacity shortfall | parameters
@end
@box warn||The exam trap
The question says *underfitting*, which is the opposite of the usual pooling complaint. An answer that talks about overfitting, dropout and early stopping is answering a different question. Keep the diagnosis explicit: high training error, small train–validation gap, plateau long before convergence.
@end
@key Pooling causes underfitting by deleting the evidence the label depends on and by starving most positions of gradient; replace it with strided or dilated convolutions, fewer pooling stages or learned attention pooling rather than by adding capacity blindly.
@box ok||Examiner's checklist
- Defines underfitting by the training loss, not the test loss.
- Gives the three mechanisms: information, capacity, gradient sparsity.
- Proposes at least four alternatives with costs.
- Warns against the overfitting reflexes.
- Suggests a diagnostic that distinguishes information loss from a capacity shortfall.
@end
@kw underfitting; information loss; strided convolution; dilated convolution; average pooling; attention pooling; gradient sparsity; capacity; receptive field
"""

SCRIPTS[8] = r"""
#A 8::Justify a CNN architecture for a real application, with every design decision tied to the data::CO4 · Create–Evaluate · 10 marks · ~3 pages::Justifying a CNN architecture for a real application
## The application
Take automated grading of mangoes on a conveyor: each fruit is photographed and must be sorted into one of five quality grades. The data are $640\times480$ colour images, about 12,000 labelled examples, imbalanced (the top grade is rare), and the model must run on an embedded device at 30 fruits per second. Every choice below is justified by one of these four facts: **the object is large and centred, the classes differ by texture and colour, the dataset is small and imbalanced, and the compute budget is tight.**
## Step 1 — Input resolution
The fruit occupies roughly $400\times400$ pixels, and the defects that decide the grade are millimetre-scale. Down-sampling to $128^{2}$ would erase them; keeping the full frame would multiply the cost for no gain. A crop to $320\times320$ around the detected fruit is the compromise: it keeps the defect scale and halves the cost relative to the full frame. **Decision: a $320\times320$ centre crop, with the crop box coming from a classical colour threshold rather than a second network**, because a learned detector would double the latency budget.
## Step 2 — Stem and trunk
The first layer uses a $5\times5$ convolution with stride two and 32 filters: a larger kernel and a stride at the input are the cheapest way to reduce resolution while capturing colour gradients, and the input has only three channels so the cost is trivial. The trunk then alternates $3\times3$ convolutions at 64, 128 and 256 channels with $2\times2$ max-pooling between stages. Depth is limited to 12 convolutional layers because the receptive field after that already exceeds the fruit, and additional depth would overfit 12,000 images.
@fig fig4_arch||The specification: three convolutional stages, global average pooling, and a five-way softmax with about 1,300 parameters in the head.
## Step 3 — Head
Global average pooling, then a single dense layer of five units. Flatten would add tens of thousands of weights to a head that has about 1,300 with global pooling, and with 12,000 images that difference is exactly where overfitting lives. Global pooling also makes the model independent of the exact crop size, which matters because the detector's box jitters.
## Step 4 — Training choices that follow from the data
@table 120,180,197
@hdr Data fact | Consequence | Setting
@row 12,000 images only | strong augmentation, regularisation | flips, rotations of ±15°, colour jitter, cutout
@row class imbalance | reweight the loss | class weights inverse to frequency, or focal loss
@row texture decides the grade | keep resolution late | pool only three times, not five
@row embedded device, 30 fps | small head, quantisation-aware training | global pooling head, INT8 post-training quantisation
@row crops jitter | input-size flexibility | global pooling rather than flatten
@end
The optimiser is stochastic descent with momentum $0.9$ and a cosine schedule, because the last accuracy points matter on a small dataset and it finds flatter minima than Adam here; batch normalisation is used in every block so that the learning rate can be $0.05$ without divergence. Early stopping on a stratified validation split protects the rare grade from being memorised last and forgotten first.
## Step 5 — What is deliberately not used
- No fully connected layers before the global pooling — they would add parameters without adding invariance.
- No depthwise separable convolutions in the trunk: they would halve the cost, but the trunk is not the bottleneck; the camera pipeline is.
- No pretrained backbone, because the domain (fruit skin texture) is far from natural-image pretraining and fine-tuning a large model would exceed the latency budget; a small model trained from scratch with heavy augmentation is the honest baseline. If accuracy were short, the next experiment would be a small mobile backbone fine-tuned at $320^{2}$, not a deeper custom net.
## Step 6 — How the design would be validated
+ Baseline: the 12-layer net above, measured on a stratified test split with per-class recall, not just overall accuracy, because the rare grade matters.
+ Ablations, one at a time: global pooling versus flatten; three pooling stages versus two; augmentation on and off.
+ Latency measured on the target device, not on the training GPU.
+ Error analysis by grade: confusion between adjacent grades is expected and tolerable; confusion between the best and the worst grade is a design failure.
@box tip||What "justify" means
Every sentence must connect a design choice to a property of the data or the deployment. "I used $3\times3$ kernels because they are standard" earns nothing; "I used $3\times3$ kernels because the defects are two to five pixels wide and a $7\times7$ kernel would smear them" earns the mark.
@end
@key Justify an architecture by deriving it from the data — object scale fixes the resolution and receptive field, class imbalance fixes the loss, dataset size fixes the head and the augmentation, and the deployment target fixes the depth and the quantisation.
@box ok||Examiner's checklist
- States the application's data facts before any architecture choice.
- Ties resolution and receptive field to object and defect size.
- Chooses global pooling and gives the parameter arithmetic.
- Uses the imbalance and the deployment budget to justify loss and depth.
- Names what was deliberately excluded and why, and how the design would be validated.
@end
@kw receptive field; input resolution; global average pooling; class imbalance; augmentation; edge deployment; quantisation; ablation study; per-class recall; design justification
"""
