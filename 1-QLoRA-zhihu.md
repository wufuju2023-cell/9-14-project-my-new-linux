# 前言

QLoRA的作者Tim Dettmers是一个在模型量化颇有建树的大佬，而且参加了谷歌的BLOOM的工程化建设。模型量化和大模型的PEFT（Parameter-Efficient Fine-Tuning）有一个共同点是它们都希望模型计算能够更快。于是Tim将他的模型量化的能力应用到了LLM训练上，提出了QLoRA。QLoRA是一个使用量化思想对LoRA进行优化的量化算法，可以显著的降低训练大模型时所需要的显存资源。QLoRA的优化有三个核心要点：首先是定义了一种4位标准浮点数（Normal Float 4-bit，NF4）量化，基于分块的分位数量化的量化策略；其次是双重量化，包含对普通参数的一次量化和对量化常数的再一次量化，可以进一步减小缓存占用；最后是分页优化器（Page Optimizer），用来在显存过高时用一部分内存代替显存。

# 1. 背景知识

## 1.1 模型量化

模型量化（quantization）也被叫做模型的低精度表示，指的是在不大幅降低模型效果的前提下使用更低的精度来表示模型中的参数，从而缩减模型的体积和训练模型时占用的显存。量化的本质是函数映射，根据量化过程是否线性我们可以把量化分为**线性量化**和**非线性量化**。量化过程是从一种数据类型“舍入”到另一种数据类型。举个例子，如果一种数据类型的范围为 `0..9`，而另一种数据类型的范围为 `0..4`，则第一种数据类型中的值 `4` 将舍入为第二种数据类型中的 `2` 。但是，如果在第一种数据类型中有值 `3`，它介于第二种数据类型的 `1` 和 `2` 之间，那么我们通常会四舍五入为 `2`。也就是说，第一种数据类型的值 `4` 和 `3` 在第二种数据类型中具有相同的值 `2`。这充分表明量化是一个有噪过程，会导致信息丢失，是一种有损压缩。最常见的 量化技术是最大绝对值 (absolute maximum quantization，absmax) 量化，如式(1)。

$$
\mathbf{X}^{\mathrm{Int} 8}=\operatorname{round}\left(\frac{127}{\operatorname{absmax}\left(\mathbf{X}^{\mathrm{FP} 32}\right)} \mathbf{X}^{\mathrm{FP} 32}\right)=\operatorname{round}\left(c^{\mathrm{FP} 32} \cdot \mathbf{X}^{\mathrm{FP} 32}\right) \tag{1}
$$

其中c是量化常数（quantization constant），通常是这个张量的特征的绝对值的最大值。

还有一种量化技术叫做零点量化（zero-point quantization），零点量化分为两步，第一步值域映射，即通过缩放将原始的数值范围映射为量化后的数值范围; 第二步零点调整，即通过平移将映射后的数据的最小值对齐为目标值域的最小值。

量化的好处有很多，首先量化可以减小模型的大小，例如在资源有限的手机端经常使用量化后的模型。其次是量化后的模型拥有更快的速度，这在并发量比较高或者对速度要求比较高的场景非常适用。最后是因为一些硬件只支持低精度的运算单位，所以我们需求将模型也转换到相同的精度。因为量化操作不可避免的带来一些误差，例如从float32到int8的round操作带来的精度损失，超出int8范围的溢出值的截断等等。模型量化的核心工作就是在尽量保证模型准确率的前提下优化模型的推理速度和模型体积。

与量化对应的是反量化（dequantization），反量化指的是将模型的低精度恢复为高精度的过程，主要用于减少量化造成的精度损失。式(1)对应的反量化过程表示为式(2)。

$$
\operatorname{dequant}\left(c^{\mathrm{FP} 32}, \mathbf{X}^{\mathrm{In} 18}\right)=\frac{\mathbf{X}^{\mathrm{In} 18}}{c^{\mathrm{FP} 32}}=\mathbf{X}^{\mathrm{FP} 32} \tag{2}
$$

按照量化过程是否以0点为对称点量化又可以分为**对称量化**和**非对称量化**。其中对称量化将原浮点数的最小或最大值的绝对值作为映射值的范围，而非对称量化是将原浮点数的最小和最大值映射为量化数据的最小和最大值，如图1。在非对称量化中，0的映射也可能会有偏移，因此不一定会被映射到0。

![](https://pic2.zhimg.com/v2-a711fb650c70f0616a72df74013ebad1_r.jpg)

## 1.2 分位数量化

分位数量化（Quantile Quantization）是隶属于非线性量化。**分位数**（Quantile）在数学上的定义指的是把**顺序排列**的一组数据分割为若干个相等块的分割点的数值。在标准正态分布中，对于分布X给定的概率 $\alpha$ ，如果存在 $u_\alpha$ 使得它的累积分布函数（CDF） $P(X < u_\alpha ) = \alpha$ ，则称 $u_\alpha$ 是标准正态分布的 $\alpha$ 分位数，如图2。因为CDF在图3中表示的是概率值小于 $u_\alpha$ 的阴影部分的面积，因此具有严格递增的特性，所以它一定存在反函数。CDF的反函数的一个重要作用是用来生成服从该随机分布的随机变量。假设 $a$ 是 $[0,1)$ 区间上均匀分布的一个随机变量，那么 $F_X^{-1}(a)$ 服从分布 $X$ 。

![](https://pic4.zhimg.com/v2-0bef9c52dcb22639144df01967ffc4b9_r.jpg)

Tim Dettmers大佬认为，具有k-比特的有损最小熵编码具有如下特性：**当将输入数据进行量化时，每个可能的k-bit的整数值出现的频率是相等的**。这个很好理解，比如我们粗暴的使用round操作去低精度的更近的值，我们可能造成大量的数据都被量化到同一个数上，这样特征之间的差异性在量化过程中就被丢失了。

为了满足这个特性，我们可以使用分位数将张量分成了大小相同的若干个块，这样我们得到更加均匀的量化特征，这也就是分位数量化。如图3所示，对于4比特量化，我们希望需要找到15个分位数来将这个曲线下面的面积（积分）等分成16份。两个分位数的中点便是模型量化到这个区间映射的值 $q_i$ 。

![](https://pic2.zhimg.com/v2-92d30438524177648a6863dc6c2ef5b7_r.jpg)

如果我们通过图3中区域的面积来确定分位数显然很困难。但是我们知道，预训练模型的参数往往是符合正态分布的，因此我们可以通过累积分布函数的反函数 $Q_X = F^{-1}_X$ 来简化分位数的计算。假设我们要将一个张量分成15个块的分位点，我们可以把CDF曲线按照它的y等距离分割成16份，然后每个分割点对应的x轴上的值便是这个分位点，两个分位点的中心点便是 $q_i$ ，如图4所示。

![](https://picx.zhimg.com/v2-73eaf102d58842d1afd0159bac5474ef_r.jpg)

$q_i$ 的计算可以简化为式(3)。但是我们知道0和1的CDF的反函数的解分别是负无穷和正无穷，因此我们不能将0和1代入式(3)。为了解决这个问题，我们可以设置一个偏移（offset）位。使用偏移位后我们计算的区间不再是 $[0,1]$ ，而是 $[1-\text{offset},\text{offset}]$ 。

$$
q_i = \frac12\left(Q_X\left( \frac{i}{2^{k}+1} \right) + Q_X\left( \frac{i+1}{2^{k}  + 1 } \right)\right) \tag{3}
$$

有了 $q_i$ ，我们便可以进行量化计算了，它的计算过程一般分为三步：

1. 计算归一化常数 $N = \max(|T|)$ ，将输入张量T转化到目标量化数据类型的范围内；
2. 对于T/N的每个元素，使用二进制搜索在域中找到阈值最接近的对应值 $q_i$ ，其中 $Q^\text{map}$ 是 $q_i$ 的集合；

$$
T_i^Q = \mathop{\arg\min}^{2n}_{j=0} \left|Q_j^\text{map} - \frac{T_i}{N}\right| \tag{4}
$$

3. 将对应 $q_i$ 的索引 $i$ 存储在量化输出的张量中。

## 1.3 分块k位量化

在式(1)中， $\frac{127}{\text{absmax}(\mathbf X^\text{FP32})}$ 的作用是依据参数中的最大值确定缩放尺度。但是如果这个值是一个异常的极大或者极小值，那么使用它计算缩放尺度就不合适了，因为它会造成整个张量的绝大多数值在量化后都在0附近，从而破坏了量化后特征分布的均匀性。分块k位量化（block-wise k-bit quantization）的策略是通过将张量分成若干个块，让每个块都有独立的量化常数c，从而解决模型参数的极大极小的异常值的问题。分块量化的另外一个好处是减少了核之间的通信，可以实现更好的并行性，并充分利用硬件的多核的能力。

图5展示了分块k位量化的量化和反量化的一个例子。在量化过程中，状态张量被分块处理，通过每个块的最大值进行归一化，最后得到的是最近的值以及它所在块的最大值。在反量化时，我们根据存储的量化后的低精度的值以及它所在块的最大值恢复到高精度的值。

![](https://pic1.zhimg.com/v2-61d9dd22cd6c8fe1d44fad1bf0d3381c_r.jpg)

## 1.4 LoRA

关于LoRA的详细介绍我们在文章《[LoRA（Low-Rank Adaptation）详解](https://zhuanlan.zhihu.com/p/663557294)》中进行了介绍，这里简单回顾下。LoRA是一个基于适配器学习的PEFT算法。它指出模型往往是过参数化话，因此可以用两个低秩矩阵代替原来的密集连接，从而可以减少模型的参数量。另外LoRA的适配器是一个和原模型的网络块并行的结构，在推理时计算的是已经将适配器的参数加到原模型参数上的新参数，因此不会带来任何的推理时间的增加。

## 1.5 梯度检查点

梯度检查点（Gradient Checkpointing）是陈天奇大佬提出的用于解决模型训练时显存占用过高的问题的一个技术方案。我们知道在模型训练时，我们通常需要将所有前向传播的激活值保存下来以在模型进行反向传播的时候使用，但是这样就会非常占用模型显存。当然我们也可以不保存激活值，而是在计算梯度时重新计算，但是这样虽然减少了缓存占用，但是却增大了计算量，减慢了训练速度。

梯度检查点就是一个介于全不丢和全丢弃的一个这种的技术方案，即只丢弃部分梯度值。图6的动图展示了一个简单的丢弃策略：它的上半部分是前向过程，它表示模型在前向过程中计算节点的激活值并保存，在计算完下一个节点后丢弃**中间节点**的激活值。图3的下半部分是反向过程，它表示有保存的梯度我们就直接使用这个保存的值， 没有保存的梯度时我们再根据它损失函数重新计算这个梯度。

![](https://pic3.zhimg.com/v2-1679b74a85687cdb250e532931bb266a_b.gif)

PyTorch开启梯度检查点非常简单，指定TrainingArgumetns的gradient checkpoint的值为True即可。

```python
training_args = TrainingArguments(
    per_device_train_batch_size=1, gradient_accumulation_steps=4, gradient_checkpointing=True, **default_args
)
trainer = Trainer(model=model, args=training_args, train_dataset=ds)
```

# 2. QLoRA

QLoRA的工作有三个，第一个工作是结合了分位数量化和分块量化的**4位标准浮点数量化**（4-bit NormalFloat Quantization）。第二个工作是对模型进行两次量化的**双重量化**（Double Quantization），它的第二次量化只作用在第一次量化产生的量化常数上，可以进一步节约显存占用。第三个工作是**分页优化**（Paged Optimizer），使用CPU内存代替GPU显存保存部分梯度参数。下面我们来详细介绍它们。

## 2.1 4位标准浮点数量化

使用上面介绍的分位数量化方法我们可以将FP2精度量化到4bit的精度，但是直接这么用的一个问题是不能保证高精度的0一定被映射到低精度的0，但是0点又是深度学习中一个重要的值，例如在模型稀疏化，数据padding的时候一般都是使用0来完成。假设offset的值是0.99，我们可以通过下面的代码片段计算出它的16个 $q_i$ 。

```python
offset = 0.99
num_bins = 16
quantile = norm.ppf(torch.linspace(1 - offset, offset, num_bins + 1)).tolist() # 将[1-offset,offset]区间等分为16份
tmp = [(quantile[1:][idx] + val) / 2 for idx, val in enumerate(quantile[:-1])] # 计算分位数
r_max, r_min = tmp[-1], tmp[0]
S = (r_max - r_min)/(1 - (-1))
Z = 1 - r_max / S
Q = [x/S + Z for x in tmp] # 分位数量化到[-1,1]
print (Q)

>>> Q = [-1.0, -0.680534899946304, -0.5217156169574965, -0.4015399993912077, -0.299784167882981, -0.20835410767681603, -0.12291223249970012, -0.040639059218818274, 0.04063881956774142, 0.12291199284862328, 0.20835391124150712, 0.2997839714476721, 0.40153976366883704, 0.5217154126647753, 0.6805348056573558, 1.0]
```

这种方式的一个问题是0的映射值不是0，如果我们考虑奇数个bin，0是可以有个映射值但是却无法充分利用4比特的16位的信息。为了确保零点映射到0并且使用4位数据类型的全部16位，我们通过估计正负两个范围的分位数来创建一个非对称的数据类型：负数部分映射其中7位，正数部分映射8位，0占据1位，总共用满了4位数的16位。另外我们也可以使用对称的量化，其中正数和负数均使用7位，0占用2个位。我这里和论文介绍的略有不同，论文说的是正数部分取9个值，负数部分取8个值，不过它们都会取到0，所以合并时再去掉一个重复的0，这两个说法其实是一样的，只是实现方式略有差异。

接下来根据作者的源码来看下量化分位数如何计算的。其中核心代码片段摘抄如下。

```python
from scipy.stats import norm
import torch

def create_normal_map(offset=0.9677083, use_extra_value=True):

    if use_extra_value:
        # one more positive value, this is an asymmetric type
        v1 = norm.ppf(torch.linspace(offset, 0.5, 9)[:-1]).tolist() # 正数部分
        v2 = [0]*(256-15) ## we have 15 non-zero values in this data type
        v3 = (-norm.ppf(torch.linspace(offset, 0.5, 8)[:-1])).tolist() #负数部分
        v = v1 + v2 + v3
    else:
        v1 = norm.ppf(torch.linspace(offset, 0.5, 8)[:-1]).tolist()
        v2 = [0]*(256-14) ## we have 14 non-zero values in this data type
        v3 = (-norm.ppf(torch.linspace(offset, 0.5, 8)[:-1])).tolist()
        v = v1 + v2 + v3

    values = torch.Tensor(v)
    values = values.sort().values
    values /= values.max()
    assert values.numel() == 256
    return values
  
  Q = create_normal_map()
```

函数create_normal_map有两个入参：offset和use_extra_value。其中offset的作用是确定分位数的始末值。use_extra_value用来控制是使用对称量化还是非对称量化。函数体内部有两个核心功能，其中if...else...部分是用来计算分位数。其中`v1`计算正数部分，`v3`计算负数部分。`v2`直接将0映射到0，并且根据要量化的单位计算0的个数。源码是使用NF4来表示8比特的量化，如果是使用4比特的量化，我们将计算`v2`的256改成16就行。接下来最后几行用来将量化值归一化到 $[-1,1]$ 。

这里有个疑问，offset的默认值为什么是0.9677083，有人也向作者寻得了解释，具体可以看给出的解释。其实这个解释我不是很理解，我感觉这个值如果不是很不合理的话，应该对量化后的模型的效果影响不大，因为offset最直观的作用就是避免取到无穷值。如果我们最终选择源码中默认的offset的值的话，我们可以根据这段代码得到论文的附录E中的Q值。

```python
# v2 = [0]的结果
Q = [-1.0, -0.6961928009986877, -0.5250730514526367, -0.39491748809814453, -0.28444138169288635, -0.18477343022823334, -0.09105003625154495, 0.0, 0.07958029955625534, 0.16093020141124725,0.24611230194568634, 0.33791524171829224, 0.44070982933044434, 0.5626170039176941, 0.7229568362236023, 1.0]
```

在量化时，我们根据特征与Q中最接近的值，根据它的索引将特征量化到4比特的[0-255]的值。在反量化时，我们将4比特的值通过从Q中索引可以将它还原到float32精度。

如果上面的介绍你看起来一知半解，我们可以通过下面这个例子简单理解QLoRA中4位标准浮点数量化是如何计算的。QLoRA采用的也是分块量化。假设一个张量有16个值，它的被分成了4块：

```python
input_blocked_tensor = [[-1.28645003578589, -1.817660483275528, 9.889441349505042, 0.010208034676132627],
 [ -15.009014631551885, 1.4136255086268115, -7.815595761491153, 10.766760590950263], 
 [-0.731406153917959, 3.468224595908726, 2.445252541840315, -8.970824523299282], 
 [-9.641638854625175, 7.696158363188889, -5.323939281255154, 5.97160401402024]]
```

根据每个块的特征的绝对值的最大值，我们为每个块保存一个量化常数，它的计算方式是每个块中特征的绝对值中最大的那个：

```python
c1 = max(|-1.28645003578589|, |-1.817660483275528|, |9.889441349505042|, |0.010208034676132627|) = 9.889441349505042
c2 = max(|-15.009014631551885|, |1.4136255086268115|, |-7.815595761491153|, |10.766760590950263|) = 15.009014631551885
c3 = max(|-0.731406153917959|, |3.468224595908726|, |2.445252541840315|, |-8.970824523299282|) = 8.970824523299282
c4 = max(|-9.641638854625175|, |7.696158363188889|, |-5.323939281255154|, |5.97160401402024|) = 9.641638854625175
```

最后我们便可以计算这个张量的量化值了。例如第一个值`-1.28645003578589`，它除以这个块的量化常数`c1`后得到`-0.13008318572517502`，我们可以在Q中找到与它最接近的值是 `-0.09105003625154495`，这个值在Q中对应的索引是`6`，因此这个值被量化后的值是`6`。同理我们可以得到这个输入张量所有的值量化后的结果。在模型保存时，除了要保存量化后的值，我们还要保存每个块对应的量化常数 $c_i$ ，因为这个值在我们进行反量化时需要用到。

```python
[[6, 5, 15, 7],
[0, 8, 2, 14],
[6, 11, 10, 0],
[0, 14, 2, 13]]
```

在反量化时，我们以量化结果作为索引，从Q中查找到它对应的分位数，再乘以为每个块保存的量化常数c_i，便可以得到最终结果。

```python
[[-0.9004339933799617, -1.8273060011889755, 9.889441349505042, 0.0],
 [-15.009014631551885, 1.1944218804231184,  -7.880829111886221,  10.850869732860506],
 [-0.816793898052648, 3.0313783372030603, 2.2078302737800004, -8.970824523299282],
 [-9.641638854625175, 6.970488722350373, -5.062564734402345, 5.424549965245643]]
```

上面过程可以用下面代码模拟，当然在真实的量化过程中使用的是并行计算，我这里为了实现简单使用的是for循环。

```python
# 量化过程
def quantize(input_blocked_tensor):
    quantize_result = []
    quantize_constant = []
    for block in input_blocked_tensor:
        c = max([abs(val) for val in block])
        quantize_constant.append(c)
        norm_block = [val/c for val in block]
        block_result = []
        for norm_val in norm_block:
            min_sim = math.inf
            idx = -1
            for j, q in enumerate(Q): # 寻找Q中最近值的索引
                sim = abs(norm_val - q)
                if sim < min_sim:
                    min_sim = sim
                    idx = j
            block_result.append(idx)
        quantize_result.append(block_result)
    return quantize_constant, quantize_result
  
  # 反量化
  def dequantize(quantize_constant, quantize_result):
    dequantize_result = []
    for idx, quantized_block in enumerate(quantize_result):
        c = quantize_constant[idx]
        dequantize_result.append([Q[val] * c for val in quantized_block])
    return dequantize_result
  
quantize_constant, quantize_result = quantize(input_blocked_tensor)
dequantize_result = dequantize(quantize_constant, quantize_result)
```

## 2.2 双重量化

在上面我们介绍到，当我们保存模型时我们不仅要保存量化后的结果，还要保存每个块的量化常数。虽然量化后的参数只有4bit的精度，但是这个量化常量的精度是float32。在QLoRA中，每个块的大小是64，因为块中的每个值占4比特。这相当于为了存储量化常数，模型要额外占用 $32/(64*4)=12.5\%$ 的显存。

QLoRA的双重量化就是对这个量化常数再做一次8bit的量化，在进行量化常数的量化时，QLoRA以每256个量化常数为一组再做一次量化。因此它额外增加的内存消耗有两部分组成，一部分是量化后的8bit的第一层的量化常数，它额外增加的显存占比是 $8/(64*4) = 3.125\%$ ，第二部分是为量化常数做量化的第二层的32bit的量化常数，它额外增加的显存占比是 $32/(256*64*4)=0.049\%$ 。因此使用双重量化后，额外增加的显存只有 $3.17\%$ 。

因为使用了双重量化，在进行反量化时我们也需要进行两次反量化才能把量化后的值还原。

## 2.3 分页优化

分页优化是针对梯度检查点做的进一步优化，以防止在显存使用峰值时发生显存OOM的问题。QLoRA分页优化其实就是当显存不足是，将保存的部分梯度检查点转移到CPU内存上，和计算机的内存数据转移到硬盘上的常规内存分页一个道理。

## 2.4 QLoRA

QLoRA的最后一个工作则是将量化的思想和LoRA的低秩适配器的思想结合到一起拿来对大模型进行微调。具体来讲，对于LLM的参数 $\mathbf W$ ，我们首先将它量化到NF4的精度，在进行特征计算时，我们通过双重反量化将它还原到BF16精度。同LoRA一样，QLoRA也在原参数一侧添加了一个与原参数并行的低秩适配器，它的精度是BF16。

$$
\mathbf{Y}^{\mathrm{BF} 16}=\mathbf{X}^{\mathrm{BF} 16} \text { doubleDequant }\left(c_1^{\mathrm{FP} 32}, c_2^{\mathrm{k}-b i t}, \mathbf{W}^{\mathrm{NF} 4}\right)+\mathbf{X}^{\mathrm{BF} 16} \mathbf{L}_1^{\mathrm{BF} 16} \mathbf{L}_2^{\mathrm{BF} 16} \tag{5}
$$

双重量化的定义见式(6)。

$$
\operatorname{doubleDequant}\left(c_1^{\mathrm{FP} 32}, c_2^{\mathrm{k} \text {-bit }}, \mathbf{W}^{\mathrm{k}-\mathrm{bit}}\right)=\operatorname{dequant}\left(\operatorname{dequant}\left(c_1^{\mathrm{FP} 32}, c_2^{\mathrm{k}-\mathrm{bit}}\right), \mathbf{W}^{4 \mathrm{bit}}\right)=\mathbf{W}^{\mathrm{BF} 16} \tag{6}
$$

其中 $c_2$ 是用来量化 $\mathbf W$ 的量化常数， $c_1$ 是用来量化 $c_2$ 的量化常数。QLoRA有一个4NF的存储数据类型和16BF的计算数据类型。在进行前向和反向传播时，我们需要将存储数据类型反量化为计算数据类型，但是计算梯度时我们只计算添加的适配器的梯度，这一点和LoRA是一致的。

# 3. 总结

QLoRA的核心工作其实是模型量化，通过定义一个4NF的精度单位将原模型的参数精度减小了数倍，从而大幅节约了训练时占用的显存。从算法角度讲，它本身和提示学习关系不大。所以其实本不想写这篇文章的，因为本人对模型量化并没有太多的研究。但是QLoRA作为LoRA家族的重要成员已经得到了广泛应用，而且考虑到很多做算法的同学和我一样也没有太多关于模型量化的经验，这篇论文看起来也非常的晦涩难懂，更重要的是我也想通过学习QLoRA来补短自己在模型量化上的知识短板，所以还是写了这篇文章，如果有写的不对的地方还请各位给予批评指正。

# 参考

1. [^](https://zhuanlan.zhihu.com/p/666234324#ref_1_0)Dettmers T, Pagnoni A, Holtzman A, et al. Qlora: Efficient finetuning of quantized llms[J]. arXiv preprint arXiv:2305.14314, 2023.
2. [^](https://zhuanlan.zhihu.com/p/666234324#ref_2_0)Hu E J, Shen Y, Wallis P, et al. Lora: Low-rank adaptation of large language models[J]. arXiv preprint arXiv:2106.09685, 2021.
3. [^](https://zhuanlan.zhihu.com/p/666234324#ref_3_0)Dettmers T, Lewis M, Shleifer S, et al. 8-bit optimizers via block-wise quantization[J]. arXiv preprint arXiv:2110.02861, 2021.
4. [^](https://zhuanlan.zhihu.com/p/666234324#ref_4_0)Chen, Tianqi, et al. "Training deep nets with sublinear memory cost." *arXiv preprint arXiv:1604.06174* (2016).
5. [^](https://zhuanlan.zhihu.com/p/666234324#ref_5_0)https://github.com/TimDettmers/bitsandbytes/blob/main/bitsandbytes/functional.py#L236
6. [^](https://zhuanlan.zhihu.com/p/666234324#ref_6_0)https://readpaper.feishu.cn/docx/CrMGdSVPKow5d1x1XQMcJioRnQe
7. [^](https://zhuanlan.zhihu.com/p/666234324#ref_7_0)全称是brain float16，是由谷歌大脑团队研发的一个16为的浮点数，通常被用在TPU上，详细结构见 https://cloud.google.com/tpu/docs/bfloat16?hl=zh-cn
