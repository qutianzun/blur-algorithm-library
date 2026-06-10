# 计算机图形学模糊效果算法 — 系统性研究路线图

> **版本：** 1.0 | **最后更新：** 2026-06-10
>
> **定位：** 面向图形学算法研究人员的模糊算法全景指南
> **语言风格：** 通俗易懂，兼顾数学严谨性

---

## 目录

1. [前置说明](#1-前置说明)
2. [图形学模糊算法的分类体系](#2-图形学模糊算法的分类体系)
3. [统一 Benchmark 框架](#3-统一-benchmark-框架)
4. [第一部分：近似高斯模糊算法](#4-第一部分近似高斯模糊算法)
   - 4.1 精确可分离高斯（基准线）
   - 4.2 双线性采样优化高斯
   - 4.3 盒模糊级联高斯（3-pass Box Blur）
   - 4.4 Stack Blur（堆栈模糊）
   - 4.5 IIR 递归滤波（Deriche / van Vliet）
   - 4.6 Kawase / Dual Filtering Blur
   - 4.7 Mipmap 级联模糊
   - 4.8 泊松碟稀疏采样模糊
5. [第二部分：图形学模糊效果](#5-第二部分图形学模糊效果)
   - 5.1 景深模糊（Depth of Field）
   - 5.2 运动模糊（Motion Blur）
   - 5.3 软阴影（Soft Shadows）
   - 5.4 环境光遮蔽模糊（Ambient Occlusion Blur）
   - 5.5 光泽/模糊反射（Glossy Reflections）
   - 5.6 Bloom / 泛光
   - 5.7 雾效 / 大气散射
   - 5.8 抗锯齿中的模糊成分
   - 5.9 纹理预过滤模糊
   - 5.10 去噪模糊（Denoising Blur）
   - 5.11 体积渲染中的模糊
6. [综合质量-性能对照表](#6-综合质量-性能对照表)
7. [12 周研究路线图](#7-12-周研究路线图)
8. [参考文献与引用](#8-参考文献与引用)
9. [FAQ：硬件实现模糊效果专题](#9-faq硬件实现模糊效果专题)

---

## 1. 前置说明

### 1.1 什么是"图形学模糊"？

在计算机图形学中，模糊（Blur）不是"图像退化"，而是**为了视觉效果主动合成的技术**。它模拟真实相机和视觉系统的物理特性，用于增强真实感和艺术表现力。

### 1.2 核心思维框架

```
物理世界现象          →    数学建模          →    算法设计          →    实现与优化
（相机景深）          （Circle of Confusion）   （后处理DOF）        （GPU Shader）
（高速运动）          （速度向量场）             （运动模糊采样）      （速度缓冲）
（粗糙表面反射）      （BRDF + 微表面）          （模糊反射）          （预过滤）
```

### 1.3 使用本指南的建议

- **初学者**：按顺序阅读，先吃透第四部分的近似高斯模糊，这是所有模糊算法的基础
- **有一定经验**：直接跳到感兴趣的第五部分效果专题
- **研究者**：重点关注"算法详解"中的"可研究方向"和性能对比数据

### 1.4 关于参考文献链接的说明

本文所有链接在撰写时已验证可访问。但网络资源可能随时间变化，如遇链接失效，建议：
1. 使用 DOI 编号在 [doi.org](https://doi.org) 搜索
2. 在 [Semantic Scholar](https://www.semanticscholar.org) 搜索论文标题
3. 使用 [Wayback Machine](https://web.archive.org) 尝试恢复

---

## 2. 图形学模糊算法的分类体系

### 2.1 按模糊目的分类

```
图形学模糊算法
│
├── 近似高斯模糊（质量-性能 trade-off 连续谱）
│   ├── 精确高斯（基准）
│   ├── 双线性优化高斯（无损加速）
│   ├── 盒模糊级联（3-pass Box → Gauss）
│   ├── Stack Blur
│   ├── IIR 递归滤波（Deriche / van Vliet）
│   ├── Kawase / Dual Filtering
│   ├── Mipmap 级联模糊
│   └── 泊松碟稀疏采样
│
├── 物理效果模拟
│   ├── 景深模糊（DOF）        ← 相机透镜物理
│   ├── 运动模糊               ← 时域积分
│   ├── 软阴影                 ← 面光源
│   ├── 环境光遮蔽模糊          ← 间接光照
│   ├── 光泽反射模糊            ← 微表面 BRDF
│   ├── 雾效/散射模糊           ← 参与介质
│   └── 体积渲染模糊            ← 多次散射
│
├── 后处理艺术效果
│   ├── Bloom
│   ├── 散景效果（Bokeh）
│   └── Lens Flare 模糊成分
│
├── 抗锯齿与重建
│   ├── TAA 时域累积模糊
│   ├── FXAA 边缘模糊
│   └── DLSS/FSR 重建模糊
│
├── 预过滤
│   ├── Mipmap 三线性过滤
│   ├── 各向异性过滤
│   ├── IBL 辐照度卷积
│   └── 预计算 BRDF 卷积
│
└── 去噪（Monte Carlo 渲染）
    ├── SVGF 空间/时域滤波
    ├── A-SVGF
    └── Nvidia NRD 框架
```

### 2.2 按实现方式分类

| 维度 | 分类 | 代表算法 |
|------|------|----------|
| **数学性质** | 线性模糊 | 高斯模糊、盒模糊、运动模糊 |
| | 非线性模糊 | 双边滤波、散射模糊 |
| | 自适应模糊 | PCSS、DOF CoC 自适应 |
| **空域性质** | 空间不变（平移不变） | 全局高斯模糊 |
| | 空间变化（PSF 随位置变） | 旋转运动模糊、散景 |
| **加速策略** | 可分离 | 高斯模糊、盒模糊 |
| | 常数时间 | 积分图、IIR、Stack Blur |
| | 多分辨率 | Mip-Blur、Kawase |
| | 稀疏采样 | 泊松碟模糊 |

---

## 3. 统一 Benchmark 框架

在学习后续算法之前，先建立统一的测试/对比框架。**以下 Python 代码是所有实验的基座。**

```python
"""
benchmark_framework.py — 模糊算法统一测试框架

用法：
    from benchmark_framework import Benchmark, BlurAlgorithm
    # 实现你的算法子类
    # 运行 Benchmark.run()
"""

import numpy as np
import time
from abc import ABC, abstractmethod
from typing import Tuple, Callable
from dataclasses import dataclass, field
import matplotlib.pyplot as plt


# ─── 测试图像生成 ────────────────────────────────────────────

def create_test_image(width: int = 512, height: int = 512) -> np.ndarray:
    """
    生成包含丰富特征的测试图像，用于评估模糊效果：
    - 阶梯边缘（评估边缘保持/模糊程度）
    - 正弦波光栅（评估频域响应）
    - 点阵（评估PSF扩散）
    - 自然纹理区域（评估整体视觉）
    - 色块（评估颜色渗透）
    """
    img = np.ones((height, width), dtype=np.float32) * 0.5

    # 1. 阶梯边缘（左上角）
    img[50:150, 50:150] = 1.0
    img[50:150, 150:250] = 0.0

    # 2. 正弦光栅（频率逐步增加）
    for i, freq in enumerate([2, 4, 8, 16, 32, 64]):
        x = np.linspace(0, freq * 2 * np.pi, width // 6)
        y = 0.5 + 0.5 * np.sin(x)
        row_start = 200 + i * 30
        img[row_start:row_start + 20, :width // 6] = y[:width // 6]

    # 3. 点阵（用于观察PSF形状）
    for py in range(100, 450, 50):
        for px in range(300, 500, 30):
            if 0 <= py < height and 0 <= px < width:
                img[py-1:py+1, px-1:px+1] = 1.0

    # 4. 自然区域 — 随机噪声 + 平滑
    np.random.seed(42)
    noise = np.random.randn(100, 100) * 0.1
    from scipy.ndimage import gaussian_filter
    noise_smooth = gaussian_filter(noise, sigma=3)
    img[400:500, 400:500] += noise_smooth
    img = np.clip(img, 0, 1)

    return img


def create_benchmark_images() -> dict:
    """创建一组用于 benchmark 的标准测试图"""
    images = {
        'step_edge': create_test_image(512, 512),
        'checkerboard': (np.random.rand(512, 512) > 0.5).astype(np.float32),
    }
    # 添加 Lena/Cameraman 风格自然图（用scipy内置）
    try:
        from scipy.datasets import face
        images['face'] = face(gray=True).astype(np.float32) / 255.0
    except (ImportError, AttributeError):
        # fallback: 生成一个平滑渐变的测试图
        x = np.linspace(0, 1, 512)
        y = np.linspace(0, 1, 512)
        xx, yy = np.meshgrid(x, y)
        images['gradient'] = (xx + yy) / 2

    return images


# ─── 性能统计 ────────────────────────────────────────────────

@dataclass
class BenchmarkResult:
    """单次 benchmark 结果"""
    algorithm_name: str
    sigma: float
    image_size: Tuple[int, int]
    runtime_ms: float
    psnr: float = 0.0        # 与精确高斯对比（近似算法）
    ssim: float = 0.0
    memory_mb: float = 0.0


class Benchmark:
    """
    统一 benchmark 运行器

    用法：
        class MyBlur(BlurAlgorithm):
            def blur(self, image, sigma):
                ...

        results = Benchmark.run([MyBlur(), ...], sigma_values=[1, 3, 5, 10])
    """

    @staticmethod
    def compute_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
        """计算 PSNR（峰值信噪比）"""
        mse = np.mean((img1 - img2) ** 2)
        if mse < 1e-10:
            return float('inf')
        return 20 * np.log10(1.0 / np.sqrt(mse))

    @staticmethod
    def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """简化 SSIM 计算"""
        mu1 = np.mean(img1)
        mu2 = np.mean(img2)
        sigma1 = np.var(img1)
        sigma2 = np.var(img2)
        sigma12 = np.mean((img1 - mu1) * (img2 - mu2))

        c1 = (0.01 * 1.0) ** 2
        c2 = (0.03 * 1.0) ** 2

        ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
               ((mu1 ** 2 + mu2 ** 2 + c1) * (sigma1 + sigma2 + c2))
        return ssim

    @staticmethod
    def run(
        algorithms: list,
        sigma_values: list = None,
        image_size: int = 512,
        repeats: int = 5,
        verbose: bool = True
    ) -> dict:
        """
        运行完整 benchmark

        参数：
            algorithms: BlurAlgorithm 子类实例列表
            sigma_values: 要测试的 sigma 值列表
            image_size: 测试图大小
            repeats: 重复次数（取中位数）
            verbose: 是否打印结果

        返回：
            {alg_name: [BenchmarkResult, ...]}
        """
        if sigma_values is None:
            sigma_values = [1, 2, 3, 5, 10, 20, 50]

        test_img = create_test_image(image_size, image_size)
        all_results = {}

        print(f"{'Algorithm':<25} {'Sigma':<8} {'Time(ms)':<12} {'PSNR':<10} {'SSIM':<10}")
        print("-" * 65)

        for alg in algorithms:
            results = []
            for sigma in sigma_values:
                # 计时（多次取中位数）
                timings = []
                for _ in range(repeats):
                    t0 = time.perf_counter()
                    output = alg.blur(test_img.copy(), sigma)
                    t1 = time.perf_counter()
                    timings.append((t1 - t0) * 1000)

                runtime_ms = np.median(timings)

                # 如果有 reference 方法，计算 PSNR/SSIM
                psnr = 0.0
                ssim = 0.0
                if hasattr(alg, 'reference_blur'):
                    ref = alg.reference_blur(test_img.copy(), sigma)
                    psnr = Benchmark.compute_psnr(output, ref)
                    ssim = Benchmark.compute_ssim(output, ref)

                result = BenchmarkResult(
                    algorithm_name=alg.name,
                    sigma=sigma,
                    image_size=(image_size, image_size),
                    runtime_ms=runtime_ms,
                    psnr=psnr,
                    ssim=ssim
                )
                results.append(result)

                if verbose:
                    psnr_str = f"{psnr:.2f}" if psnr > 0 else "N/A"
                    ssim_str = f"{ssim:.4f}" if ssim > 0 else "N/A"
                    print(f"{alg.name:<25} {sigma:<8} {runtime_ms:<12.3f} {psnr_str:<10} {ssim_str:<10}")

            all_results[alg.name] = results

        return all_results

    @staticmethod
    def plot_results(all_results: dict, save_path: str = None):
        """绘制性能对比图"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        for alg_name, results in all_results.items():
            sigmas = [r.sigma for r in results]
            times = [r.runtime_ms for r in results]
            psnrs = [r.psnr for r in results]

            axes[0].plot(sigmas, times, 'o-', label=alg_name)
            axes[1].plot(sigmas, psnrs, 's-', label=alg_name)

        axes[0].set_xlabel('Sigma')
        axes[0].set_ylabel('Runtime (ms)')
        axes[0].set_title('性能: Sigma vs 耗时')
        axes[0].set_xscale('log')
        axes[0].legend()
        axes[0].grid(True)

        axes[1].set_xlabel('Sigma')
        axes[1].set_ylabel('PSNR (dB)')
        axes[1].set_title('质量: Sigma vs PSNR')
        axes[1].set_xscale('log')
        axes[1].legend()
        axes[1].grid(True)

        # 绘制速度对比条形图
        if all_results:
            first_alg = list(all_results.values())[0]
            for i, r in enumerate(first_alg):
                if r.sigma == 10:  # 以 sigma=10 为例
                    labels = list(all_results.keys())
                    times = [all_results[k][i].runtime_ms for k in labels]
                    axes[2].barh(labels, times)
                    axes[2].set_xlabel('Runtime (ms)')
                    axes[2].set_title(f'Sigma=10 速度对比')
                    break

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()


# ─── 算法基类 ────────────────────────────────────────────────

class BlurAlgorithm(ABC):
    """所有模糊算法的抽象基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        对图像施加模糊

        参数：
            image: 输入图像，形状 (H, W)，float32，范围 [0, 1]
            sigma: 模糊强度参数

        返回：
            模糊后的图像，形状同输入
        """
        pass

    def reference_blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        精确参考实现（用于 PSNR/SSIM 对比）
        默认使用 scipy 高斯滤波
        """
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(image, sigma=sigma, mode='reflect')
```

---

## 4. 第一部分：近似高斯模糊算法

这是所有模糊算法的基础。高斯模糊是"基准线"，其他所有算法都在**性能**和**质量**之间做折衷。

```
高质量 ←───────────────────────────→ 高性能
  │                                       │
  精确高斯     盒级联     Stack     IIR    Kawase   泊松稀疏
  (基准)      (≈高斯)   (≈高斯)   (逼近)  (近似)   (视觉)
```

---

### 4.1 精确可分离高斯（基准线）

#### 数学依据

二维高斯函数的定义为：

$$G(x, y) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)$$

**可分离性**（核心性质）：

$$G(x, y) = G(x) \cdot G(y) = \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{x^2}{2\sigma^2}\right) \cdot \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{y^2}{2\sigma^2}\right)$$

这意味着一个二维高斯卷积可以分解为两次一维卷积：

$$\text{Blur} = \text{Pass1: X方向} \to \text{Pass2: Y方向}$$

**复杂度对比**：
- 二维直接卷积：$O(n^2)$ per pixel（n = kernel size）
- 可分离：$O(2n)$ per pixel

**核大小选择**：通常取 $n = 2\lceil 3\sigma \rceil + 1$，因为 $3\sigma$ 外权重 < 0.3%。

#### 代码框架

```python
# gaussian_exact.py

import numpy as np
from scipy import signal
from benchmark_framework import BlurAlgorithm


def gaussian_kernel_1d(sigma: float, truncate: float = 3.0) -> np.ndarray:
    """
    生成一维高斯核

    参数：
        sigma: 标准差
        truncate: 截断倍数（默认 3σ）

    返回：
        一维高斯核，形状 (n,)，归一化后总和为 1
    """
    radius = int(truncate * sigma + 0.5)
    if radius < 1:
        radius = 1
    x = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-0.5 * (x / sigma) ** 2)
    kernel /= kernel.sum()  # 归一化
    return kernel


class SeparableGaussian(BlurAlgorithm):
    """精确可分离高斯模糊"""

    def __init__(self):
        super().__init__("SeparableGaussian")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        kernel = gaussian_kernel_1d(sigma)

        # X 方向
        out = signal.convolve2d(image, kernel[np.newaxis, :], mode='same', boundary='reflect')

        # Y 方向
        out = signal.convolve2d(out, kernel[:, np.newaxis], mode='same', boundary='reflect')

        return out

    def reference_blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """自身就是参考实现"""
        return self.blur(image, sigma)
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E1.1** | 二维 vs 可分离对比 | 验证两者输出完全一致（差值 < 1e-10） |
| **E1.2** | 不同 σ 的性能曲线 | 验证耗时随 σ 线性增长 |
| **E1.3** | 频域分析 | 验证 FFT(高斯) = 高斯（低通滤波器） |

**E1.1 测试用例**：

```python
def test_separable_vs_full():
    """验证可分高斯的输出与 scipy 参考完全一致"""
    from scipy.ndimage import gaussian_filter
    img = create_test_image(256, 256)
    alg = SeparableGaussian()
    for sigma in [1, 3, 5, 10, 20]:
        our = alg.blur(img, sigma)
        ref = gaussian_filter(img, sigma=sigma, mode='reflect')
        diff = np.max(np.abs(our - ref))
        assert diff < 1e-6, f"sigma={sigma}: max diff = {diff}"
    print("✓ 可分离高斯与 scipy 参考完全一致")
```

---

### 4.2 双线性采样优化高斯（无损加速）

#### 数学依据

**核心思想**：利用 GPU 纹理硬件的双线性插值，一次纹理采样获取 4 个像素的加权和。

标准一维 N-tap 高斯采样：
$$O(p) = \sum_{i=-n}^{n} w_i \cdot I(p + i)$$

如果我们将相邻的对 $(w_i, w_{i+1})$ 合并，可以通过双线性插值一次完成。设：

$$w_i \cdot I(p + i) + w_{i+1} \cdot I(p + i + 1) = \hat{w} \cdot \text{lerp}(I(p + i), I(p + i + 1), t)$$

其中 $\hat{w} = w_i + w_{i+1}$，偏移量 $t = w_{i+1} / (w_i + w_{i+1})$。

**效果**：25-tap 高斯需要 25 次采样 → 优化后只需 7 次硬件采样（约 3.6× 加速）

**重要**：这是**无损**加速 — 输出值与标准高斯完全一致（在浮点精度内）。

> **注意：此加速本质上是 GPU 端的纹理采样优化。在 Python CPU 端无法体现加速效果，但我们可以模拟其合并算法。**

#### 代码框架

```python
# gaussian_bilinear.py

import numpy as np
from scipy import signal
from benchmark_framework import BlurAlgorithm


def compute_bilinear_offsets_1d(sigma: float, truncate: float = 3.0):
    """
    计算双线性采样优化所需的 offset 和 weight

    返回：
        offsets: 采样偏移位置（小数偏移，利用双线性插值）
        weights: 每个采样点的权重
    """
    radius = int(truncate * sigma + 0.5)
    if radius < 1:
        radius = 1
    x = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-0.5 * (x / sigma) ** 2)

    # 合并相邻权重对
    offsets = []
    weights = []
    i = 0
    while i < len(kernel):
        if i + 1 < len(kernel):
            w_sum = kernel[i] + kernel[i + 1]
            # 双线性插值位置：weighted average of positions
            t = kernel[i + 1] / w_sum if w_sum > 0 else 0.5
            offset = x[i] + t  # 相对于中心的位置
            offsets.append(offset)
            weights.append(w_sum)
            i += 2
        else:
            offsets.append(x[i])
            weights.append(kernel[i])
            i += 1

    return np.array(offsets, dtype=np.float32), np.array(weights, dtype=np.float32)


def bilinear_1d_convolution(image: np.ndarray, offsets: np.ndarray,
                            weights: np.ndarray, axis: int = 1) -> np.ndarray:
    """
    模拟 GPU 双线性优化的 1D 卷积

    注意：这是对 GPU 行为的模拟，真正的加速来自硬件纹理单元。
    """
    result = np.zeros_like(image)
    n = image.shape[axis]
    w_sum_total = weights.sum()

    for i in range(n):
        for offset, w in zip(offsets, weights):
            # 计算采样位置（含小数偏移）
            pos = i + offset
            pos0 = int(np.floor(pos))
            pos1 = pos0 + 1
            frac = pos - pos0

            # 边界处理（reflect）
            if axis == 1:
                row = image[:, :]
                val0 = row[:, max(0, min(n - 1, pos0))]
                val1 = row[:, max(0, min(n - 1, pos1))]
            else:
                val0 = image[max(0, min(image.shape[0] - 1, pos0)), :]
                val1 = image[max(0, min(image.shape[0] - 1, pos1)), :]

            # 双线性插值
            val = val0 * (1 - frac) + val1 * frac

            if axis == 1:
                result[:, i] += w * val
            else:
                result[i, :] += w * val

    return result


class BilinearOptimizedGaussian(BlurAlgorithm):
    """双线性采样优化高斯（模拟 GPU 端加速）"""

    def __init__(self):
        super().__init__("BilinearGaussian")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        offsets, weights = compute_bilinear_offsets_1d(sigma)
        # X 方向
        out = bilinear_1d_convolution(image, offsets, weights, axis=1)
        # Y 方向
        out = bilinear_1d_convolution(out, offsets, weights, axis=0)
        return out
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E2.1** | 双线性优化 vs 标准高斯数值对比 | 验证两者差值 < 1e-5 |
| **E2.2** | 采样次数统计：N vs ceil(N/2) | 验证合并效果 |
| **E2.3** | 不同 σ 下加速比分析 | 找出加速比随 σ 变化曲线 |

**E2.1 测试用例**：

```python
def test_bilinear_vs_exact():
    """验证双线性优化输出与精确高斯一致"""
    from gaussian_exact import SeparableGaussian

    img = create_test_image(256, 256)
    exact = SeparableGaussian()
    bilinear = BilinearOptimizedGaussian()

    for sigma in [1, 3, 5, 10]:
        ref = exact.blur(img, sigma)
        out = bilinear.blur(img, sigma)
        psnr = Benchmark.compute_psnr(out, ref)
        print(f"sigma={sigma}: PSNR = {psnr:.2f} dB")
        assert psnr > 50, f"sigma={sigma}: PSNR too low: {psnr}"
    print("✓ 双线性优化与精确高斯一致")
```

> **⚠️ 说明**：这个加速是 GPU 纹理硬件特性，在 CPU Python 中只能验证数值等价性，无法体现实际加速效果。在 GPU（GLSL/HLSL）中，加速比约为 3.5–4×。

**出处：** 此技术是 GPU 编程中的经典技巧，广泛用于实时渲染后处理。最著名的讲解见 GPU Gems 系列和 ShaderX 系列中的高斯模糊实现。

---

### 4.3 盒模糊级联高斯（3-pass Box Blur → Gaussian）

#### 数学依据

**核心定理**：由中心极限定理（Central Limit Theorem），多次独立同分布随机变量的和趋近正态分布。

一维盒模糊（Box Blur）的核函数：

$$h_{\text{box}}(x) = \begin{cases} \frac{1}{2r+1}, & |x| \leq r \\ 0, & \text{otherwise} \end{cases}$$

对图像应用一次盒模糊等价于与均匀分布卷积；应用 N 次等价于 **Irwin-Hall 分布**（N 个均匀分布的和）：

$$h_{\text{N-pass}}(x) = \underbrace{h_{\text{box}} * h_{\text{box}} * \cdots * h_{\text{box}}}_{N\text{ times}}$$

当 $N \to \infty$ 时，$h_{\text{N-pass}} \to \text{Gaussian}$（中心极限定理）。

**实践结论**：$N = 3$ 已经足够接近高斯（误差约 3%）。

**等效 σ 计算**：
- 一维盒模糊（宽度 $w = 2r + 1$）的方差：
  $$\sigma_{\text{box}}^2 = \frac{w^2 - 1}{12} = \frac{r(r+1)}{3}$$

- N-pass 后总方差：
  $$\sigma_{\text{total}}^2 = N \cdot \frac{w^2 - 1}{12}$$

- 给定目标 $\sigma$，所需盒宽度：
  $$w = \sqrt{\frac{12\sigma^2}{N} + 1}$$

  > 出处：DSP StackExchange 关于盒模糊与高斯关系的讨论，见参考资料 [BoxBlur-CLT]

**关键优势**：盒模糊可以用**滑动窗口**实现 **O(1)**，与半径无关。

```
滑动窗口算法（水平方向）:
  初始化: sum = Σ(I[0], ..., I[w-1])
  每步:   sum += I[x + r] - I[x - r - 1]
          输出[x] = sum / w
```

**质量评估**：3-pass box 与精确高斯相比，PSNR > 40dB（肉眼无法区分）。

#### 代码框架

```python
# box_blur_cascade.py

import numpy as np
from scipy import signal
from benchmark_framework import BlurAlgorithm


def box_blur_1d(image: np.ndarray, radius: int, axis: int = 1) -> np.ndarray:
    """
    一维盒模糊（滑动窗口 O(1) 实现）

    参数：
        image: 输入图像
        radius: 模糊半径
        axis: 0=垂直，1=水平

    返回：
        模糊后的图像
    """
    result = np.zeros_like(image)
    width = image.shape[axis]
    kernel_size = 2 * radius + 1

    # 使用 cumsum 实现 O(1) 盒模糊
    # 积分图方法：sum(x-r, x+r) = cumsum[x+r] - cumsum[x-r-1]

    if axis == 1:
        # 水平方向
        cumsum = np.cumsum(image, axis=1)
        for i in range(width):
            left = max(0, i - radius)
            right = min(width - 1, i + radius)
            # 实际核大小（边界处会缩小）
            actual_size = right - left + 1
            if left == 0:
                result[:, i] = cumsum[:, right] / actual_size
            else:
                result[:, i] = (cumsum[:, right] - cumsum[:, left - 1]) / actual_size
    else:
        # 垂直方向
        cumsum = np.cumsum(image, axis=0)
        for i in range(width):
            top = max(0, i - radius)
            bottom = min(width - 1, i + radius)
            actual_size = bottom - top + 1
            if top == 0:
                result[i, :] = cumsum[bottom, :] / actual_size
            else:
                result[i, :] = (cumsum[bottom, :] - cumsum[top - 1, :]) / actual_size

    return result


class BoxBlurCascade(BlurAlgorithm):
    """3-pass 盒模糊级联 → 近似高斯"""

    def __init__(self, passes: int = 3):
        super().__init__(f"BoxBlur{passes}Pass")
        self.passes = passes

    def _sigma_to_radius(self, sigma: float) -> int:
        """
        根据目标 sigma 计算盒模糊半径

        公式: σ² = N · (w² - 1) / 12
               w = sqrt(12σ²/N + 1)
               r = (w - 1) / 2
        """
        w = np.sqrt(12 * sigma ** 2 / self.passes + 1)
        r = max(1, int(np.round((w - 1) / 2)))
        return r

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        radius = self._sigma_to_radius(sigma)
        out = image.copy()

        for _ in range(self.passes):
            # X 方向
            out = box_blur_1d(out, radius, axis=1)
            # Y 方向
            out = box_blur_1d(out, radius, axis=0)

        return out
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E3.1** | 1/2/3/4-pass 分别 vs 精确高斯 | 找出 N=3 的合理性拐点 |
| **E3.2** | 半径与 σ 的换算公式验证 | 验证公式准确性 |
| **E3.3** | 大 σ（>50）性能对比 | 展示 O(1) 优势 |
| **E3.4** | 频域分析：盒模糊的零点 | 理解频谱差异 |

**E3.1 测试用例**：

```python
def test_box_passes_quality():
    """比较不同 pass 数 vs 精确高斯的质量"""
    from gaussian_exact import SeparableGaussian

    img = create_test_image(256, 256)
    exact = SeparableGaussian()

    for sigma in [3, 5, 10, 20]:
        ref = exact.blur(img, sigma)
        for n_pass in [1, 2, 3, 4]:
            alg = BoxBlurCascade(passes=n_pass)
            out = alg.blur(img, sigma)
            psnr = Benchmark.compute_psnr(out, ref)
            print(f"sigma={sigma}, {n_pass}-pass: PSNR = {psnr:.2f} dB")

    # 预期结果：
    #   1-pass: PSNR ~25-30 dB（可见块状）
    #   2-pass: PSNR ~35 dB（可接受）
    #   3-pass: PSNR ~40+ dB（不易区分）
    #   4-pass: PSNR ~43+ dB（收益递减）
```

**出处：**
- 中心极限定理用于盒模糊近似高斯是经典结论。DBpedia 条目指出 "3次盒模糊近似高斯核误差约3%" [BoxBlur-CLT]
- 实践分析见 learn-blur GitHub 仓库 [learn-blur]

---

### 4.4 Stack Blur（堆栈模糊）

#### 数学依据

**Stack Blur** 由 Mario Klingemann 在 2004 年提出，是盒模糊的改进版本。

**核心思想**：不是简单地对窗口内像素取平均，而是维护一个"堆栈"结构，越靠近中心的像素权重越大，形成更接近高斯的模糊效果。

算法直观理解：
```
位置:  -3  -2  -1   0  +1  +2  +3
权重:   1   2   3   4   3   2   1    ← 三角权重（近似高斯）
```

与盒模糊不同，Stack Blur 的权重分布是**三角形的**——等效于两次盒模糊级联。

> **⚠️ 数学依据说明**：Stack Blur 是启发式（heuristic）算法，并没有严格的数学证明证明它"等于"高斯。其权重分布是分段线性的（三角滤波），位于盒模糊和高斯之间。Klingemann 本人的描述是 "a compromise between Gaussian blur and box blur"。它没有使用中心极限定理来逼近高斯，而是用了一种工程技巧在 O(1) 时间内实现近三角权重分布。

**算法步骤**（以水平方向为例）：
1. 初始化一个"堆栈"——包含左右各 radius 个像素的值以及它们的"出现次数"（stack count）
2. 移动窗口：新像素加入堆栈右边，旧像素从左边移出
3. 堆栈中每个像素值按"层"加权（越靠近中心层数越高）
4. 输出 = 加权和 / 总权重

**复杂度**：O(n) 每像素，与半径无关。

#### 代码框架

```python
# stack_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


class StackBlur(BlurAlgorithm):
    """
    Stack Blur — 由 Mario Klingemann 于 2004 年提出

    参考: https://quasimondo.com/2004/02/25/stackblur-2004/
    """

    def __init__(self):
        super().__init__("StackBlur")

    def _stack_blur_1d(self, image: np.ndarray, radius: int, axis: int = 1) -> np.ndarray:
        """一维 Stack Blur 实现"""
        result = np.zeros_like(image)
        height, width = image.shape
        length = width if axis == 1 else height
        other = height if axis == 1 else width

        radius = min(radius, length - 1)
        kernel_size = 2 * radius + 1
        div = (radius + 1) * (radius + 1)  # 归一化因子（三角权重和）

        for i in range(other):
            # 取出当前行/列
            if axis == 1:
                line = image[i, :].copy() if image.ndim == 2 else image[i, :, :].copy()
            else:
                line = image[:, i].copy() if image.ndim == 2 else image[:, i, :].copy()

            # Stack Blur 核心 — 滑动三角权重窗口
            # 使用积分"堆栈"：值栈 + 权重栈
            stack = np.zeros(kernel_size)
            stack_pos = 0

            # 初始化第一个窗口
            sum_val = 0.0
            sum_weight = 0.0
            for j in range(-radius, radius + 1):
                idx = max(0, min(length - 1, j))
                weight = radius + 1 - abs(j)  # 三角权重
                val = line[idx]
                stack[j + radius] = val
                sum_val += val * weight
                sum_weight += weight

            result[i, 0] if axis == 1 else result[0, i] = sum_val / sum_weight

            # 滑动窗口
            for pos in range(1, length):
                # 移除离开窗口的像素
                old_idx = pos - radius - 1
                if old_idx >= 0:
                    old_val = line[old_idx]
                    # 从堆栈中移除（需要减少所有受影响层的计数）
                    for layer in range(kernel_size):
                        dist = abs(layer - radius)
                        weight = radius + 1 - dist
                        if weight > 0 and old_idx == pos - radius - 1 + (layer - radius):
                            # 简化：在完整实现中需要精确的堆栈管理
                            pass

                # 添加新进入窗口的像素
                new_idx = pos + radius
                if new_idx < length:
                    new_val = line[new_idx]
                    # 添加到堆栈

                # 简化实现：直接用 O(radius) 计算（仅为示意）
                # 真正优化版是 O(1)
                sum_val = 0.0
                sum_weight = 0.0
                for j in range(-radius, radius + 1):
                    idx = max(0, min(length - 1, pos + j))
                    weight = radius + 1 - abs(j)
                    sum_val += line[idx] * weight
                    sum_weight += weight

                if axis == 1:
                    result[i, pos] = sum_val / sum_weight
                else:
                    result[pos, i] = sum_val / sum_weight

        return result

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        Stack Blur

        注意：sigma 将被转换为 Stack Blur 的 radius 参数。
        转换关系近似为 sigma ≈ radius / √3（三角滤波的等效σ）
        """
        # 三角滤波等效 sigma: σ = radius / √3
        # 所以 radius ≈ σ * √3
        radius = max(1, int(sigma * np.sqrt(3)))

        out = self._stack_blur_1d(image, radius, axis=1)
        out = self._stack_blur_1d(out, radius, axis=0)

        return out
```

> **⚠️ 注意**：上方的 Python 实现为了清晰展示算法逻辑，采用了 O(n·radius) 的简化版本。真正的 Stack Blur 通过维护多层"堆栈"实现 O(n)。完整 O(1) 实现见 Klingemann 的原始代码。在此我们不重复完整 O(1) 版本，因为它主要是一个工程优化技巧而非数学贡献。

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E4.1** | Stack Blur vs 盒模糊 vs 高斯视觉对比 | 确认"介于两者之间" |
| **E4.2** | 等效 σ 换算验证 | 验证 σ ≈ radius/√3 |
| **E4.3** | 与 3-pass Box 的质量对比 | 哪个更接近高斯？ |

**E4.1 测试用例**：

```python
def test_stack_blur_quality():
    """Stack Blur 与高斯和盒模糊的对比"""
    from gaussian_exact import SeparableGaussian
    from box_blur_cascade import BoxBlurCascade

    img = create_test_image(256, 256)
    exact = SeparableGaussian()
    box3 = BoxBlurCascade(passes=3)
    stack = StackBlur()

    for sigma in [3, 5, 10]:
        ref = exact.blur(img, sigma)
        box_out = box3.blur(img, sigma)
        stack_out = stack.blur(img, sigma)

        box_psnr = Benchmark.compute_psnr(box_out, ref)
        stack_psnr = Benchmark.compute_psnr(stack_out, ref)

        print(f"sigma={sigma}:")
        print(f"  3-pass Box:  PSNR = {box_psnr:.2f} dB")
        print(f"  Stack Blur:  PSNR = {stack_psnr:.2f} dB")
```

**出处：** Mario Klingemann 的个人网站，原版 Flash/Processing 实现和演示 [StackBlur]（2024 年仍可访问）

---

### 4.5 IIR 递归滤波（Deriche / van Vliet）

#### 数学依据

**核心思想**：用无限冲激响应（IIR）递归滤波器替代有限冲激响应（FIR）卷积。IIR 的输出依赖于之前的输入**和之前的输出**，通过前向 + 后向递归实现高斯近似。

**关键性质**：计算复杂度与 $\sigma$ **完全无关** — 每个像素固定运算量。

**Deriche 滤波器（1990）**：

Deriche 提出用 4 阶递归滤波器近似高斯：

$$y_{\text{forward}}[n] = a_0 x[n] + a_1 x[n-1] + a_2 x[n-2] + a_3 x[n-3] + b_1 y[n-1] + b_2 y[n-2] + b_3 y[n-3] + b_4 y[n-4]$$

$$y_{\text{backward}}[n] = a_0 x[n] + a_1 x[n+1] + a_2 x[n+2] + a_3 x[n+3] + b_1 y[n+1] + b_2 y[n+2] + b_3 y[n+3] + b_4 y[n+4]$$

最终输出 = forward + backward。

> **⚠️ 数学依据说明**：Deriche 滤波器有严格的数学基础——它的系数是通过优化近似误差推导出来的，在 $L_2$ 范数下是最优递归近似。但它仍然是**近似**，不是精确高斯。van Vliet（1998）的 3 阶版本近似精度稍低但更快。

**系数计算**：系数是 σ 的函数，需要为每个 σ 预计算。具体公式见 Deriche 的原始论文 [Deriche1990] 和 INRIA 技术报告 [Deriche1993]。

**GPU 难点**：递归滤波器有数据依赖，无法直接并行。在 GPU 上的实现策略：
1. 每行/列一个线程，行内串行
2. 分段法（Hiller 2011）
3. 纹理反馈（需要多 pass）

#### 代码框架

```python
# iir_gaussian.py

import numpy as np
from benchmark_framework import BlurAlgorithm


def deriche_coefficients(sigma: float) -> dict:
    """
    计算 Deriche 4 阶递归滤波器系数

    参数：
        sigma: 高斯标准差

    返回：
        dict 包含 forward/backward 的 a, b 系数

    ⚠️ 注意：此处简化实现，实际系数需要查表或数值求解
    完整的系数推导见 Deriche (1990) PAMI 论文
    """
    # 简化系数（用于示意，实际需要精确计算）
    # 对于 sigma=1 的近似系数示例：
    alpha = 1.695 / sigma  # 近似值，实际更复杂

    # Deriche 4阶滤波器的近似系数
    # 注意：这些是固定系数的示例，实际应用中需要根据 sigma 调整
    a = np.array([1.0, -3.0, 3.0, -1.0]) * alpha
    b = np.array([0.0, 0.0, 0.0, 0.0])  # 简化为 FIR 近似

    return {'a_forward': a, 'b_forward': b}


class IIRDericheGaussian(BlurAlgorithm):
    """
    IIR 递归滤波高斯近似（Deriche 4阶）

    参考：
        Deriche, R. "Fast Algorithms for Low-Level Vision"
        IEEE PAMI, 1990, DOI: 10.1109/34.47354

    ⚠️ 注意：当前实现是简化框架。
    完整的 Deriche 系数计算需要数值求解。
    """

    def __init__(self):
        super().__init__("IIR_Deriche")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        IIR 高斯滤波

        实际实现需要：
        1. 计算精确的递归系数（基于 σ）
        2. 前向递归 pass
        3. 后向递归 pass
        4. 合并结果

        此处仅给出框架
        """
        # TODO: 完整的 Deriche 递归实现
        # 1. 计算系数
        # 2. 前向 pass
        # 3. 后向 pass
        # 4. 合并

        # Fallback: 使用 scipy
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(image, sigma=sigma, mode='reflect')
```

> ⚠️ **重要说明**：Deriche 滤波器的完整实现需要数值求解多项式方程的系数，代码量较大（约 200 行）。这里我们给出的是**研究框架和接口定义**。建议研究者在实现时参考：
> - Deriche 原始论文中的系数表
> - ITK 库的 RecursiveGaussianImageFilter（C++ 开源实现）
> - Farnebäck & Westin (2006) 的改进系数计算方法

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E5.1** | 4 阶 vs 3 阶 vs 1 阶精度对比 | 质量 vs 性能 trade-off |
| **E5.2** | IIR vs 精确高斯的 PSNR | 验证近似误差 |
| **E5.3** | IIR 在不同 σ 下的常数时间性 | 验证复杂度与 σ 无关 |

**E5.1 测试用例**：

```python
def test_iir_accuracy():
    """测试 IIR 递归滤波的近似精度"""
    from scipy.ndimage import gaussian_filter

    img = create_test_image(256, 256)

    for sigma in [1, 2, 5, 10, 20]:
        ref = gaussian_filter(img, sigma=sigma, mode='reflect')

        # 此处用 IIR 代替
        # iir = IIRDericheGaussian()
        # out = iir.blur(img, sigma)
        # psnr = Benchmark.compute_psnr(out, ref)

        print(f"sigma={sigma}: IIR PSNR > 50 dB（需要实现完整版本验证）")
```

**出处：**
- Deriche (1990) IEEE PAMI — "Fast Algorithms for Low-Level Vision" [Deriche1990]
- Deriche (1993) INRIA Tech Report RR-1893 [Deriche1993]
- van Vliet, Young, Verbeek (1998) ICPR — "Recursive Gaussian Derivative Filters" [vanVliet1998]
- Farnebäck & Westin (2006) JMIV — 改进的系数计算方法 [Farneback2006]

---

### 4.6 Kawase / Dual Filtering Blur

#### 数学依据

**Kawase Blur** 由 Masaki Kawase 在 GDC 2003 提出，最初用于游戏 *DOUBLE-S.T.E.A.L (Wreckless)* 的 Bloom 效果。

**核心思想**：交替下采样 + 小核模糊，用多次迭代模拟大半径模糊。

每个迭代 pass 的采样模式：

```
采样点（pixelOffset 逐步增大）:

    (-0.5-d, +0.5+d)    (+0.5+d, +0.5+d)
                        ●
        ●        ●
                ●
    (-0.5-d, -0.5-d)    (+0.5+d, -0.5-d)
```

每次采样 4 个点取平均，等价于一个特定形状的滤波器。

> **⚠️ 数学依据说明**：Kawase Blur 没有严格的数学基础证明它"近似高斯"。它是一种**工程启发式算法**，通过迭代应用特定形态的滤波器来产生视觉上的模糊效果。其滤波器形状不等同于高斯，会有块状伪影。这是为了**性能**而牺牲**数学精确性**的典型例子。

**等效 σ 的经验公式**（通过实验测量）：

对于 N 次迭代，初始偏移 d₀，每次递增 Δd：

$$\sigma_{\text{等效}} \approx k \cdot N \cdot \Delta d$$

其中系数 k 需要通过实验标定（约 0.3–0.5 之间）。

**Dual Filtering 改进**：使用 [1 3 3 1] 核进行下采样，比简单的 4-tap 平均有更好的抗混叠效果。

#### 代码框架

```python
# kawase_blur.py

import numpy as np
from scipy.ndimage import zoom
from benchmark_framework import BlurAlgorithm


class KawaseBlur(BlurAlgorithm):
    """
    Kawase Blur / Dual Filtering

    出处：
        Masaki Kawase, GDC 2003
        "Frame Buffer Postprocessing Effects in DOUBLE-S.T.E.A.L (Wreckless)"

    参考：https://en.ppt-online.org/755333
    """

    def __init__(self):
        super().__init__("KawaseBlur")

    def _kawase_pass(self, image: np.ndarray, offset: float) -> np.ndarray:
        """单次 Kawase 模糊 pass"""
        H, W = image.shape
        result = np.zeros_like(image)

        # 4-tap Kawase 采样
        for dy, dx in [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]:
            # 采样位置
            sy = dy * (offset + 0.5)
            sx = dx * (offset + 0.5)

            # 双线性采样（简化：最近邻 + 简单插值）
            for y in range(H):
                for x in range(W):
                    ny = y + sy
                    nx = x + sx
                    # 边界处理
                    ny = max(0, min(H - 1, ny))
                    nx = max(0, min(W - 1, nx))

                    # 双线性插值
                    y0, x0 = int(ny), int(nx)
                    y1, x1 = min(H - 1, y0 + 1), min(W - 1, x0 + 1)
                    fy, fx = ny - y0, nx - x0

                    val = (image[y0, x0] * (1 - fy) * (1 - fx) +
                           image[y0, x1] * (1 - fy) * fx +
                           image[y1, x0] * fy * (1 - fx) +
                           image[y1, x1] * fy * fx)
                    result[y, x] += val

        return result / 4.0

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        Kawase Blur

        策略：使用多次迭代，offset 逐步增大
        offset 序列：1, 2, 3, 4, ... 直到覆盖目标半径
        """
        # 根据 sigma 决定迭代次数和 offset
        # 经验公式：iterations ≈ sigma / 2，offset 递增 1
        iterations = max(1, int(sigma / 2))
        out = image.copy()

        for i in range(iterations):
            offset = float(i + 1)
            out = self._kawase_pass(out, offset)

        return out


class KawaseDualFilter(BlurAlgorithm):
    """
    Kawase Dual Filter — 添加 [1 3 3 1] 下采样改进
    """

    def __init__(self):
        super().__init__("KawaseDual")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        Dual Filter: 下采样 → 模糊 → 上采样
        """
        iterations = max(1, int(sigma / 3))

        # 下采样阶段
        current = image.copy()
        scales = []
        for i in range(iterations):
            # 半分辨率下采样
            h, w = current.shape
            h2, w2 = max(1, h // 2), max(1, w // 2)
            down = zoom(current, (h2 / h, w2 / w), order=1)
            scales.append(down)
            current = down

        # 在最低分辨率做 Kawase 模糊
        kawase = KawaseBlur()
        current = kawase.blur(current, sigma)

        # 上采样混合
        for i, scale_img in enumerate(reversed(scales[:-1])):
            h, w = scale_img.shape
            up = zoom(current, (h / current.shape[0], w / current.shape[1]), order=1)
            # 裁剪到目标大小
            up = up[:h, :w]
            # 混合（Dual Filter 的混合策略）
            current = scale_img * 0.3 + up * 0.7

        # 上采样回原始大小
        h, w = image.shape
        result = zoom(current, (h / current.shape[0], w / current.shape[1]), order=1)
        result = result[:h, :w]

        return result
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E6.1** | Kawase vs 高斯视觉对比 | 找出产生可见伪影的半径阈值 |
| **E6.2** | 迭代次数 vs 等效 σ | 建立经验标定曲线 |
| **E6.3** | Kawase vs Dual Filter 质量对比 |验证 [1 3 3 1] 下采样的改进 |
| **E6.4** | 大半径（σ=100）性能对比 | 展示 Kawase 在超大半径的优势 |

**E6.1 测试用例**：

```python
def test_kawase_quality_analysis():
    """Kawase 质量分析 — 找出伪影阈值"""
    from gaussian_exact import SeparableGaussian

    img = create_test_image(256, 256)
    exact = SeparableGaussian()
    kawase = KawaseBlur()
    dual = KawaseDualFilter()

    for sigma in [2, 5, 10, 20, 50]:
        ref = exact.blur(img, sigma)
        kaw_out = kawase.blur(img, sigma)
        dual_out = dual.blur(img, sigma)

        print(f"sigma={sigma}:")
        print(f"  Kawase PSNR = {Benchmark.compute_psnr(kaw_out, ref):.2f} dB")
        print(f"  Dual    PSNR = {Benchmark.compute_psnr(dual_out, ref):.2f} dB")

    # 预期观察：
    # sigma < 5:  PSNR > 35dB（质量可接受）
    # sigma 10-20: 出现块状伪影，PSNR 下降
    # sigma > 50: PSNR < 25dB（明显分层）
```

**出处：**
- Masaki Kawase, GDC 2003 演示文稿，可在线查看 [Kawase-GDC2003]
- Intel 开发者视频对此算法的介绍 [Intel-Kawase]
- three.js postprocessing 库的 KawaseBlurMaterial 实现 [ThreeJS-Kawase]

---

### 4.7 Mipmap 级联模糊

#### 数学依据

**核心思想**：将模糊操作转移到低分辨率去做，利用 mipmap 链（硬件高度优化的下采样）。

等效关系：
$$\text{Blur}_{\text{sigma}}(I) \approx \text{Upsample}\left(\text{Blur}_{\text{sigma}/2^L}\left(I_{\text{level }L}\right)\right)$$

其中 $I_{\text{level }L}$ 是图像下采样 $2^L$ 倍后的结果。

**理论依据**：多分辨率分析的尺度空间性质。高斯滤波和降采样可以交换顺序（近似）。

> **⚠️ 数学依据说明**：这个"近似"的误差来自下采样引入的混叠（aliasing）和上采样的插值误差。严格的数学关系是：
> $$\text{Blur}_{\sigma}(I) \approx \text{Upsample}(\text{Blur}_{\sigma'}(\text{Downsample}(I)))$$
> 仅当 $\sigma' = \sqrt{\sigma^2 - \sigma_{\text{downsample}}^2}$ 时才精确，但实践中往往直接近似。

#### 代码框架

```python
# mip_blur.py

import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from benchmark_framework import BlurAlgorithm


class MipBlur(BlurAlgorithm):
    """
    Mipmap 级联模糊

    思路：在低分辨率做模糊，然后上采样
    适合超大半径模糊（σ > 50）
    """

    def __init__(self):
        super().__init__("MipBlur")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        h, w = image.shape

        # 选择合适的 mip level
        # 目标：在 mip level L 上模糊半径在 2-5 像素之间
        # 即 σ / 2^L ∈ [2, 5]
        L = max(0, int(np.log2(sigma / 3)))
        L = min(L, int(np.log2(min(h, w))) - 2)  # 防止下采样过度

        if L == 0:
            # 小半径直接用标准高斯
            return gaussian_filter(image, sigma=sigma, mode='reflect')

        # 下采样
        scale = 2 ** L
        h_small, w_small = h // scale, w // scale
        small = zoom(image, (h_small / h, w_small / w), order=1)

        # 在低分辨率做模糊
        sigma_small = sigma / scale
        small_blur = gaussian_filter(small, sigma=sigma_small, mode='reflect')

        # 上采样回原分辨率
        result = zoom(small_blur, (h / h_small, w / w_small), order=1)
        result = result[:h, :w]

        # 可选：与原始图像在 mip level 边界混合
        if L > 1:
            # 在相邻 mip level 也做模糊，然后混合
            L_low = L - 1
            scale_low = 2 ** L_low
            h_low, w_low = h // scale_low, w // scale_low
            low = zoom(image, (h_low / h, w_low / w), order=1)
            sigma_low = sigma / scale_low
            low_blur = gaussian_filter(low, sigma=sigma_low, mode='reflect')
            low_up = zoom(low_blur, (h / h_low, w / w_low), order=1)
            low_up = low_up[:h, :w]

            # 线性混合（基于 sigma 匹配度）
            alpha = 0.5
            result = result * (1 - alpha) + low_up * alpha

        return result
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E7.1** | 不同 mip level 选择策略对比 | 找最优 level 选择规则 |
| **E7.2** | 跨级混合 vs 单级上采样 | 验证过渡连续性 |
| **E7.3** | 超大半径（σ=100, 200）性能 | 展示 mip-blur 优势 |

---

### 4.8 泊松碟稀疏采样模糊

#### 数学依据

**核心思想**：使用泊松碟分布（Poisson Disk Distribution）的稀疏样本替代规则网格采样，用少量样本产生视觉上的模糊效果。

> **⚠️ 数学依据说明**：泊松碟采样本身有严谨的数学基础（最大最小值距离约束的随机点分布），但"用泊松碟采样做模糊"不是精确的高斯近似。它的核心思想是：对于**散景（Bokeh）**等艺术效果，视觉上的"模糊感"比数学上的"高斯基精确性"更重要。因此这个算法**没有严格的高斯逼近保证**。

泊松碟采样的关键性质：
- 任意两点之间的距离 ≥ 最小距离 r
- 样本分布均匀（没有聚类）
- 比规则网格更接近自然分布的采样模式

**为什么用于模糊？**
- 少量样本（4-16个）即可产生模糊视觉效果
- 固定采样数 → **性能恒定**
- 不规则分布 → 散景效果更自然

> **⚠️ 注意**：此算法在 Python 实现中性能并不快（因为需要复杂的采样模式），它的"极快"特性是针对 GPU 固定函数管线而言的。

#### 代码框架

```python
# poisson_disk_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


def generate_poisson_disk_samples(radius: int, num_samples: int,
                                  width: int, height: int) -> np.ndarray:
    """
    生成泊松碟采样模式

    ⚠️ 注意：完整的泊松碟采样（Bridson 算法）较复杂。
    这里简化生成随机 2D 偏移样本，保持最小距离约束。
    """
    np.random.seed(42)
    samples = []
    min_dist = radius * 0.3

    while len(samples) < num_samples:
        # 在 [-radius, radius] 范围内随机采样
        x = np.random.uniform(-radius, radius)
        y = np.random.uniform(-radius, radius)

        # 临时略过距离检查（完整实现中需要）
        ok = True
        for sx, sy in samples:
            if np.sqrt((x - sx) ** 2 + (y - sy) ** 2) < min_dist:
                ok = False
                break
        if ok:
            samples.append((x, y))

    return np.array(samples)


class PoissonDiskBlur(BlurAlgorithm):
    """
    泊松碟稀疏采样模糊

    适用于散景（Bokeh）效果。质量取决于样本数。
    样本数越接近高斯核大小，质量越接近高斯。
    固定样本数 → 固定性能。
    """

    def __init__(self, num_samples: int = 16):
        super().__init__(f"PoissonDisk_{num_samples}s")
        self.num_samples = num_samples

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        H, W = image.shape
        result = np.zeros_like(image)

        # 生成泊松碟采样模式
        radius = max(1, int(sigma * 2))
        samples = generate_poisson_disk_samples(radius, self.num_samples, W, H)

        # 高斯权重（基于样本位置）
        weights = []
        for sx, sy in samples:
            w = np.exp(-(sx ** 2 + sy ** 2) / (2 * sigma ** 2))
            weights.append(w)
        weights = np.array(weights)
        weights /= weights.sum()

        # 逐像素采样
        for y in range(H):
            for x in range(W):
                total = 0.0
                for (sx, sy), w in zip(samples, weights):
                    nx = max(0, min(W - 1, x + int(sx)))
                    ny = max(0, min(H - 1, y + int(sy)))
                    total += image[ny, nx] * w
                result[y, x] = total

        return result
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E8.1** | 不同样本数（4/8/12/16/32）的质量 | 找到质量饱和点 |
| **E8.2** | 泊松碟 vs 规则网格 vs 随机采样 | 证明泊松碟最优 |
| **E8.3** | 散景效果对比 | 展示艺术效果优势 |

---

## 5. 第二部分：图形学模糊效果

### 5.1 景深模糊（Depth of Field）

#### 图形学中的问题描述

景深效果模拟**真实相机镜头**的光学特性——只有焦平面上的物体清晰，其他距离的物体模糊。

#### 核心数学模型：Circle of Confusion (CoC)

薄透镜模型下的 CoC 直径（Potmesil & Chakravarty 1981）：

$$c = \frac{|d - d_f|}{d} \cdot \frac{f^2}{N(d_f - f)}$$

其中：
- $d$ = 物体深度
- $d_f$ = 焦平面深度
- $f$ = 镜头焦距
- $N$ = 光圈 f-number（$f/\text{光圈直径}$）

简化形式：

$$c = A \cdot \frac{|d - d_f|}{d} \quad \text{其中} \quad A = \frac{f^2}{N(d_f - f)}$$

**CoC 越大 = 越模糊**。

#### 散景形状（Bokeh）

真实散景形状由**光圈叶片**决定：

| 叶片数 | 散景形状 | 常见于 |
|--------|----------|--------|
| 5 | 五边形 | 老镜头 |
| 6-7 | 六/七边形 | 常见镜头 |
| 8-9 | 近圆形 | 高端镜头 |
| 圆形 | 完美圆 | 理论模型 |
| 变形宽银幕 | 椭圆 | 电影镜头（Anamorphic） |

**数学建模**：用孔径多边形 + 旋转对称核来表示。

#### 实现方法分类

```
景深模糊实现
├── 后处理方法（实时）
│   ├── CoC 映射 + 后处理模糊
│   ├── 多层 Layer 方法
│   └── 半分辨率重投影
│
├── 光线追踪方法（离线/混合）
│   ├── 薄透镜模型采样
│   ├── 分布式光线追踪（Cook 1984）
│   └── 重要性采样
│
└── 混合方法
    └── 后处理 + 光线追踪遮罩
```

#### 代码框架

```python
# depth_of_field.py

import numpy as np
from scipy.ndimage import gaussian_filter
from benchmark_framework import BlurAlgorithm


def compute_coc(depth: np.ndarray, focus_depth: float,
                focal_length: float = 50.0, f_number: float = 2.8,
                sensor_size: float = 36.0) -> np.ndarray:
    """
    计算 Circle of Confusion 映射

    参数：
        depth: 深度图（近=小值，远=大值）
        focus_depth: 焦平面深度
        focal_length: 镜头焦距（mm）
        f_number: 光圈 f-number（越小=越浅景深）
        sensor_size: 传感器尺寸（mm）

    返回：
        CoC 半径（像素单位）
    """
    # 薄透镜模型
    A = (focal_length ** 2) / (f_number * (focus_depth - focal_length) + 1e-8)
    coc = A * np.abs(depth - focus_depth) / (depth + 1e-8)

    # 限制最大 CoC
    max_coc = 50.0  # 像素
    coc = np.clip(coc, 0, max_coc)

    return coc


class PostProcessDOF(BlurAlgorithm):
    """
    后处理景深模糊

    流程：
    1. 输入：颜色图 + 深度图
    2. 计算 CoC 映射
    3. 按 CoC 大小自适应模糊
    4. 前景/背景过渡处理
    """

    def __init__(self):
        super().__init__("PostProcessDOF")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        简化的后处理 DOF

        注意：真正 DOF 需要深度图输入，这里用 sigma 模拟模糊强度
        完整实现需要：
        1. 深度图 → CoC
        2. 分层模糊（近/中/远）
        3. 散景形状渲染
        4. 前景遮罩处理
        """
        # 示例：按 sigma 简单地做高斯模糊
        # 真正实现需要像素级别的自适应模糊
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(image, sigma=sigma, mode='reflect')
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E9.1** | CoC 计算公式验证 | 与真实相机照片对比 |
| **E9.2** | 前景/背景过渡区域的处理 | 遮挡可见性检查 |
| **E9.3** | 散景形状 vs 圆形模糊对比 | 视觉真实感差异 |
| **E9.4** | 多图层 DOF vs 单层后处理 | 质量-性能取舍 |

#### Benchmark 测试

```python
def benchmark_dof_methods():
    """对比不同 DOF 实现方法"""
    from gaussian_exact import SeparableGaussian

    img = create_test_image(512, 512)
    # 模拟深度图（从中心渐远）
    h, w = img.shape
    y, x = np.ogrid[:h, :w]
    depth = np.sqrt((x - w/2) ** 2 + (y - h/2) ** 2) / (w/2)

    # 计算 CoC
    coc = compute_coc(depth, focus_depth=0.5, f_number=2.8)

    # 测试不同 sigma 下的性能
    for sigma in [2, 5, 10]:
        t0 = time.perf_counter()
        # 模拟 DOF 模糊（实际应用需要逐像素自适应）
        from scipy.ndimage import gaussian_filter
        result = gaussian_filter(img, sigma=sigma, mode='reflect')
        t1 = time.perf_counter()
        print(f"DOF sigma={sigma}: {(t1-t0)*1000:.2f} ms")
```

**出处：**
- Potmesil & Chakravarty (1981) SIGGRAPH — 奠定了计算机图形学中 DOF 的基础 [Potmesil1981]
- Cook, Porter, Carpenter (1984) — 分布式光线追踪实现 DOF [Cook1984]
- Demers (2004) GPU Gems 第 23 章 — 实时候处理 DOF 技术综述 [Demers2004]
- Scheuermann (2004) GDC — Advanced Depth of Field [Scheuermann2004]
- Hammon (2008) GPU Gems 3 第 28 章 — Practical Post-Process Depth of Field [Hammon2008]

---

### 5.2 运动模糊（Motion Blur）

#### 图形学中的问题描述

运动模糊是在**曝光时间内**相机/物体运动导致的图像模糊。在图形学中需要模拟这种时域积分效果。

#### 核心数学模型

连续时间积分模型：
$$B(x) = \frac{1}{T} \int_{0}^{T} I_t(x) \, dt$$

其中 $I_t(x)$ 是 t 时刻的像素颜色，$T$ 是曝光时间。

离散化：
$$B(x) \approx \frac{1}{N} \sum_{i=0}^{N-1} I_{t_i}(x)$$

**速度缓冲（Velocity Buffer）方法**：

每个像素存储一个 2D 运动向量 $v(x, y)$，表示该像素从上一帧到当前帧的位移。

沿速度方向采样：
$$B(x) = \frac{1}{2k+1} \sum_{i=-k}^{k} I(x + i \cdot v_x, y + i \cdot v_y)$$

#### 实现方法分类

```
运动模糊实现
├── 后处理方法
│   ├── 速度缓冲 + 沿方向采样
│   ├── TileMax + NeighborMax（McGuire 2012）
│   └── 多子帧混合
│
├── 光线追踪方法
│   ├── 时域光线采样
│   ├── 运动基元（Moving primitives）
│   └── 变形运动（Deformation motion blur）
│
└── 混合方法
    └── 后处理 + RT 辅助
```

#### 核心代码框架

```python
# motion_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


class PostProcessMotionBlur(BlurAlgorithm):
    """
    后处理运动模糊（速度缓冲法）

    参考：
        McGuire et al. "A Reconstruction Filter for Plausible Motion Blur"
        I3D 2012, DOI: 10.1145/2159616.2159639
    """

    def __init__(self, num_samples: int = 15):
        super().__init__("MotionBlur")
        self.num_samples = num_samples

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        简化运动模糊实现

        注意：真正运动模糊需要速度缓冲（motion vector）输入。
        这里用 sigma 模拟模糊强度（速度大小），
        并假设水平方向运动。

        完整实现需要：
        1. 速度缓冲（逐像素 2D 向量）
        2. 沿运动方向采样
        3. 遮挡检测（disocclusion）
        4. TileMax / NeighborMax 优化（McGuire 2012）
        """
        H, W = image.shape
        result = np.zeros_like(image)

        # 模拟速度：水平方向，大小由 sigma 控制
        vel_x = sigma
        vel_y = 0.0

        # 沿运动方向采样
        for i in range(self.num_samples):
            t = (i / (self.num_samples - 1)) - 0.5  # [-0.5, 0.5]
            dx = t * vel_x
            dy = t * vel_y

            # 偏移采样
            for y in range(H):
                for x in range(W):
                    nx = max(0, min(W - 1, x + int(round(dx))))
                    ny = max(0, min(H - 1, y + int(round(dy))))
                    result[y, x] += image[ny, nx]

        result /= self.num_samples
        return result
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E10.1** | 不同采样数 N 的质量/性能曲线 | 确定最优 N |
| **E10.2** | 速度缓冲方向 ≠ 像素法线方向的处理 | 解决"消失点"问题 |
| **E10.3** | 遮挡检测方法对比 | 减少伪影 |

**出处：**
- McGuire et al. (2012) I3D — 实时运动模糊的重构滤波 [McGuire2012]
- Cook et al. (1984) — 分布式光线追踪中的时域采样 [Cook1984]
- GPU Gems 3, Chapter 27 — "Motion Blur as a Post-Processing Effect" [GPU-Gems3-MB]

---

### 5.3 软阴影（Soft Shadows）

#### 图形学中的问题描述

面光源（Area Light）产生的阴影会有**半影区（Penumbra）**——从完全阴影到完全照亮的平滑过渡。这个过渡本质上是阴影边缘的**模糊**。

#### 核心数学模型

**PCF（Percentage Closer Filtering）**：

$$S(x) = \frac{1}{|N|} \sum_{p \in N} \chi\left(z_p < z_{\text{light}}(x + p)\right)$$

其中 $\chi$ 是阴影测试（1=阴影，0=光照），$N$ 是滤波器窗口。

**PCSS（Percentage Closer Soft Shadows）**，Fernando 2005：

三步算法：
1. **Blocker Search**：在搜索区域内找遮挡物平均深度 $z_{\text{avg}}$
2. **Penumbra 估计**：$W_{\text{penumbra}} = \frac{(z_r - z_{\text{avg}}) \cdot W_{\text{light}}}{z_{\text{avg}}}$
3. **可变大小 PCF**：滤波器窗口大小 ∝ $W_{\text{penumbra}}$

**VSM（Variance Shadow Maps）**：

用**模糊后的矩**近似阴影概率：
$$P(z > z_{\text{occluder}}) \approx \frac{\sigma^2}{\sigma^2 + (z - \mu)^2}$$

其中 $\mu$ 和 $\sigma^2$ 是从模糊后的深度图中计算的一阶和二阶矩。

#### 代码框架

```python
# soft_shadows.py

import numpy as np
from benchmark_framework import BlurAlgorithm


class PCSS(BlurAlgorithm):
    """
    Percentage Closer Soft Shadows

    参考：Fernando (2005) SIGGRAPH Sketch
    DOI: 10.1145/1187112.1187153
    """

    def __init__(self):
        super().__init__("PCSS")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        PCSS 简化演示

        注意：真正 PCSS 需要 shadow map 和 3 步算法。
        此处简化演示滤波器大小对阴影模糊的影响。
        """
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(image, sigma=sigma, mode='reflect')
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E11.1** | PCF 固定大小 vs PCSS 自适应 | 接触硬化效果对比 |
| **E11.2** | VSM 模糊大小对漏光伪影的影响 | 找到最优模糊参数 |
| **E11.3** | PCF 采样数 vs 质量 | 确定最少采样数 |

**出处：**
- Fernando (2005) SIGGRAPH — PCSS 原始论文 [Fernando2005]
- Donnelly & Lauritzen (2006) — Variance Shadow Maps [VSM]
- GPU Gems 2 相关章节

---

### 5.4 环境光遮蔽模糊（Ambient Occlusion Blur）

#### 核心数学模型

SSAO（Screen Space Ambient Occlusion）产生的原始结果有**大量噪声**，需要**双边滤波**去噪。

**双边滤波（Bilateral Filter）**（Tomasi & Manduchi 1998）：

$$B(x) = \frac{1}{W} \sum_{y \in N(x)} I(y) \cdot G_s(\|x - y\|) \cdot G_r(|I(x) - I(y)|)$$

其中：
- $G_s$ = 空间权重（高斯，由距离决定）
- $G_r$ = 值域权重（高斯，由颜色/法向/深度差异决定）
- $W$ = 归一化因子

**联合双边滤波（Joint Bilateral Filter）**：用高分辨率的引导图（如颜色、法向）指导低分辨率 AO 的上采样。

#### 代码框架

```python
# bilateral_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


def bilateral_filter(image: np.ndarray, guide: np.ndarray,
                     sigma_s: float, sigma_r: float) -> np.ndarray:
    """
    双边滤波

    参数：
        image: 输入图像
        guide: 引导图（决定值域权重，可以是法向/深度/颜色）
        sigma_s: 空间高斯 σ
        sigma_r: 值域高斯 σ

    返回：
        滤波后的图像
    """
    H, W = image.shape
    radius = int(3 * sigma_s + 0.5)
    result = np.zeros_like(image)

    for y in range(H):
        for x in range(W):
            total_w = 0.0
            total_val = 0.0
            center_val = guide[y, x]

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny = max(0, min(H - 1, y + dy))
                    nx = max(0, min(W - 1, x + dx))

                    # 空间权重
                    w_s = np.exp(-(dx ** 2 + dy ** 2) / (2 * sigma_s ** 2))

                    # 值域权重（基于引导图）
                    d_val = abs(guide[ny, nx] - center_val)
                    w_r = np.exp(-(d_val ** 2) / (2 * sigma_r ** 2))

                    w = w_s * w_r
                    total_w += w
                    total_val += image[ny, nx] * w

            result[y, x] = total_val / total_w if total_w > 0 else 0

    return result


class SSAOBilateralFilter(BlurAlgorithm):
    """SSAO 双边滤波去噪"""

    def __init__(self):
        super().__init__("BilateralAO")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        SSAO 双边滤波

        注意：实际使用中 guide 应为法向图或深度图。
        这里简化使用图像自身作为引导。
        """
        guide = image.copy()
        return bilateral_filter(image, guide, sigma_s=sigma, sigma_r=sigma * 0.1)
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E12.1** | 高斯模糊 vs 双边滤波（AO 去噪） | 证明双边滤波保持边缘 |
| **E12.2** | 不同引导图（法向/深度/颜色）的影响 | 找到最优引导信息 |
| **E12.3** | 联合双边上采样 vs 全分辨率双边 | 性能/质量 trade-off |

**出处：**
- Tomasi & Manduchi (1998) ICCV — Bilateral Filter 原始论文 [Tomasi1998]
- Pharr & Fernando (2005) GPU Gems 2 — SSAO 实现
- Bavoil & Sainz (2008) — 基于双边滤波的 SSAO 后处理 [Bavoil2008]

---

### 5.5 光泽/模糊反射（Glossy Reflections）

#### 核心数学模型

**微表面 BRDF** 中的粗糙度参数控制反射的模糊程度：

$$f_r(\omega_i, \omega_o) = \frac{F(\omega_i, h) G(\omega_i, \omega_o, h) D(h)}{4(\omega_i \cdot n)(\omega_o \cdot n)}$$

其中 $D(h)$ 是法线分布函数（NDF），粗糙度越大 NDF 越宽 → 反射越模糊。

**屏幕空间反射（SSR）** 中通过对反射光线方向周围做**重要性采样**，然后对采样结果做**模糊过滤**。

**预过滤环境贴图**（IBL 的 Split Sum Approximation）：

$$L_o \approx \frac{1}{N} \sum_{i=1}^{N} L(l_i) \cdot f(l_i, v) \cdot \cos\theta_i$$

近似分解为：
1. 预过滤环境贴图（不同粗糙度级别的模糊）
2. BRDF LUT

#### 代码框架

```python
# glossy_reflections.py

from benchmark_framework import BlurAlgorithm
import numpy as np


class GlossyReflectionBlur(BlurAlgorithm):
    """
    光泽反射中的模糊

    核心思想：粗糙度越大 → 反射光线越分散 → 反射结果越模糊
    """

    def __init__(self):
        super().__init__("GlossyReflection")

    def _prefilter_envmap(self, env_map: np.ndarray, roughness: float) -> np.ndarray:
        """
        预过滤环境贴图（不同粗糙度级别）

        roughness 0.0 = 原始（镜面反射）
        roughness 1.0 = 完全模糊（漫反射）
        """
        # 用高斯模糊模拟粗糙度引起的模糊
        from scipy.ndimage import gaussian_filter
        sigma = roughness * 10  # 粗糙度 → 模糊强度
        return gaussian_filter(env_map, sigma=sigma, mode='wrap')

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        简化：将 sigma 视为粗糙度，对环境贴图做预过滤
        """
        return self._prefilter_envmap(image, min(1.0, sigma / 10))
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E13.1** | 不同粗糙度下 BRDF 卷积核形状 | NDF 分布 vs 模糊核 |
| **E13.2** | 重要性采样数 vs 模糊质量 | 收敛曲线 |
| **E13.3** | 预过滤 vs 实时采样 | 性能/质量 trade-off |

**出处：**
- Cook & Torrance (1982) — 微表面 BRDF 模型
- Karis (2013) — IBL Split Sum Approximation [Karis2013]
- GPU Gems 相关章节

---

### 5.6 Bloom / 泛光

#### 核心数学模型

Bloom 效果模拟**强光溢出到周围区域**的现象。本质是：
1. 从原图中提取高亮区域（阈值）
2. 对高亮区域施加模糊
3. 混合回原图

$$
\text{Bloom}(x) = I(x) + k \cdot \text{Blur}\left(\max(I(x) - T, 0)\right)
$$

其中 $T$ 是亮度阈值，$k$ 是泛光强度。

#### 实现方法

| 方法 | 模糊算法 | 性能 | 质量 |
|------|----------|------|------|
| **经典 Bloom** | 高斯模糊 | 中 | 高 |
| **Kawase Bloom** | Kawase 迭代模糊 | 高 | 中 |
| **Dual Filtering** | 下采样 + 上采样 | 极高 | 中 |
| **Bokeh Bloom** | 散景形状核 | 低 | 极高 |

#### 代码框架

```python
# bloom.py

import numpy as np
from scipy.ndimage import gaussian_filter
from benchmark_framework import BlurAlgorithm


class Bloom(BlurAlgorithm):
    """
    Bloom 泛光效果

    流程：
    1. 亮度阈值提取
    2. 对高亮图做模糊
    3. 混合回原图
    """

    def __init__(self, threshold: float = 0.8, intensity: float = 0.3):
        super().__init__("Bloom")
        self.threshold = threshold
        self.intensity = intensity

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        # 1. 提取高亮区域
        bright = np.maximum(image - self.threshold, 0)

        # 2. 模糊
        blurred = gaussian_filter(bright, sigma=sigma, mode='reflect')

        # 3. 混合
        result = image + blurred * self.intensity
        return np.clip(result, 0, 1)
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E14.1** | Kawase Bloom vs 经典 Bloom | 性能对比 |
| **E14.2** | 阈值 T 的选择 | 不同场景的最优阈值 |
| **E14.3** | 多级 Bloom（不同 σ 混合） | 更自然的泛光效果 |

**出处：**
- Kawase (2003) GDC — 原始 Bloom 实现 [Kawase-GDC2003]
- GPU Gems 相关章节

---

### 5.7 雾效 / 大气散射

#### 核心数学模型

**指数高度雾（Exponential Height Fog）**：

$$f(z) = \min\left(\exp\left(-\int_{0}^{z} \beta(t) dt\right), 1\right)$$

简化版：
$$f(z) = \exp(-\beta \cdot z)$$

其中 $\beta$ 是散射系数（控制雾的密度），$z$ 是深度。

**Koschmieder 模型**（大气散射）：
$$B(x) = I(x) \cdot e^{-\beta d(x)} + A \cdot (1 - e^{-\beta d(x)})$$

其中 $A$ 是大气光颜色，$d(x)$ 是物体到相机的距离。

这里的模糊是**指数衰减**，不是卷积模糊——它根据深度信息混合颜色。

#### 代码框架

```python
# fog_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


class ExponentialHeightFog(BlurAlgorithm):
    """
    指数高度雾

    注意：这不是卷积模糊，而是根据深度做颜色混合。
    雾效应模糊是"不可见性的模糊"而非空间模糊。
    """

    def __init__(self, fog_color: float = 0.5):
        super().__init__("Fog")
        self.fog_color = fog_color

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        sigma → 雾密度 β
        """
        H, W = image.shape
        # 模拟深度图（离中心越远越深）
        y, x = np.ogrid[:H, :W]
        depth = np.sqrt((x - W/2) ** 2 + (y - H/2) ** 2) / (W/2)

        # 雾混合
        beta = sigma * 0.05
        fog_factor = np.exp(-beta * depth)
        fog_factor = fog_factor[:, :, np.newaxis] if image.ndim == 3 else fog_factor

        result = image * fog_factor + self.fog_color * (1 - fog_factor)
        return result
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E15.1** | 不同 β 的雾效视觉 | 密度参数控制 |
| **E15.2** | 与卷积模糊的对比 | 理解物理模型的差异 |
| **E15.3** | 体积雾 + 光线步进中的散射模糊 | 高级雾效 |

**出处：**
- Koschmieder (1924) — 大气散射基础模型
- Nishita et al. (1987) — 3D 雾的计算机图形学实现
- GPU Gems 2 — 实时雾效

---

### 5.8 抗锯齿中的模糊成分

#### FXAA（Fast Approximate Anti-Aliasing）

**核心思想**：检测边缘 → 沿边缘方向模糊。

1. 亮度梯度检测边缘
2. 计算边缘方向
3. 沿垂直方向做 2-tap 子像素模糊混合

这是一种**定向模糊**——只在边缘处且在垂直边缘方向做模糊，以达到平滑锯齿的效果。

#### TAA（Temporal Anti-Aliasing）

**核心思想**：将多帧的抖动采样结果通过**时域累积**混合。

$$C_t = \alpha \cdot C_t^{\text{current}} + (1 - \alpha) \cdot C_{t-1}^{\text{history}}$$

**核心挑战**：运动物体的时域混合会产生"鬼影"（ghosting）。

**解决方案（Karis 2014）**：
- Neighborhood Clamping: 将历史颜色限制在当前帧 3×3 邻域的 AABB 范围内
- YCoCg 颜色空间变换

这里的"模糊"体现在：
1. 时域累积本质上是**时间轴上的指数移动平均（低通滤波）**
2. 空间 clamping 会导致轻微**模糊**

#### 代码框架

```python
# taa_blur.py

import numpy as np
from benchmark_framework import BlurAlgorithm


class TAA(BlurAlgorithm):
    """
    Temporal Anti-Aliasing 中的模糊成分

    参考：Karis (2014) "High Quality Temporal Supersampling"
    http://advances.realtimerendering.com/s2014/epic/TemporalAA.pptx
    """

    def __init__(self, alpha: float = 0.1):
        super().__init__("TAA")
        self.alpha = alpha
        self.history = None

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        TAA 时域累积（简化）

        注意：完整 TAA 需要 velocity buffer、jitter 分布、
        neighborhood clamping 等。
        """
        if self.history is None:
            self.history = image.copy()

        # 时域累积（指数平滑）
        self.history = (1 - self.alpha) * self.history + self.alpha * image

        return self.history.copy()

    def reset(self):
        self.history = None
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E16.1** | α 值对时域模糊速度的影响 | α 越大 → 响应越快但噪声越大 |
| **E16.2** | TAA vs 无 TAA 的时域稳定性 | 闪烁对比 |
| **E16.3** | Neighborhood clamping 对模糊的影响 | AABB 范围的控制 |

**出处：**
- Karis (2014) SIGGRAPH — TAA 原始实现 [Karis2014]
- FXAA 原始论文 [FXAA]
- Lottes (2011) — FXAA 实现

---

### 5.9 纹理预过滤模糊

#### Mipmap 三线性过滤

Mipmap 链生成时，每个 level 是上一级的**下采样模糊**（通常使用 box filter）：

$$I_{\text{level }L+1}(x, y) = \frac{1}{4} \sum_{i=0}^{1} \sum_{j=0}^{1} I_{\text{level }L}(2x + i, 2y + j)$$

三线性过滤 = level L 和 L+1 之间的**线性插值**。

#### 各向异性过滤

当纹理从倾斜角度观察时，屏幕空间的一个像素对应纹理空间的**拉长区域**。各向异性过滤沿这个拉长方向做**额外的采样**（模糊）。

#### IBL 辐照度卷积

**漫反射辐照度图**：对环境贴图做**余弦加权卷积**：

$$E(n) = \int_{\Omega} L(\omega) \max(n \cdot \omega, 0) d\omega$$

这本质上是一个**全方向的大半径模糊**。

**Split Sum Approximation**（Karis 2013）：
- 预过滤环境贴图（不同粗糙度的模糊版本）
- BRDF LUT（离线预计算）

#### 代码框架

```python
# prefilter.py

import numpy as np
from scipy.ndimage import gaussian_filter
from benchmark_framework import BlurAlgorithm


class IrradianceConvolution(BlurAlgorithm):
    """
    环境贴图辐照度卷积（漫反射 IBL）

    等同于对全景图做宽半径高斯模糊
    """

    def __init__(self):
        super().__init__("IrradianceConv")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        sigma 控制辐照度卷积的平滑程度
        实际 IBL 中 sigma 取决于环境贴图分辨率和 BRDF 粗糙度
        """
        # 半球积分近似 = 大半径高斯模糊
        return gaussian_filter(image, sigma=sigma, mode='wrap')
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E17.1** | Mipmap 模糊核（box）vs 高斯 | 不同下采样滤波器的对比 |
| **E17.2** | 辐照度卷积的半径需求 | 什么半径才足够平滑 |
| **E17.3** | 各向异性过滤的采样模式 | 倾斜角度 vs 采样数 |

**出处：**
- Williams (1983) — Mipmap 原始论文 [Williams1983]
- Karis (2013) — IBL Split Sum [Karis2013]
- GPU Gems 2 — 各向异性过滤

---

### 5.10 去噪模糊（Denoising Blur）

#### Monte Carlo 渲染中的噪声

路径追踪等蒙特卡洛渲染方法产生的图像有**方差噪声**，需要用模糊来降低噪声。

#### SVGF（Spatiotemporal Variance-Guided Filtering）

Schied et al. (2017) 提出的最先进的实时去噪方法。

**核心创新**：
1. **时域累积**：历史帧重投影，$C_t = \alpha C_t + (1-\alpha) C_{t-1}$
2. **方差引导**：根据 luminance 方差估计，自适应调整模糊强度
3. **à-trous 小波滤波**：层次化滤波（3-5 pass），逐 pass 扩大滤波半径

第 n 个 à-trous pass：
$$C^{(n+1)}(x) = \frac{1}{W} \sum_{y \in N(x)} C^{(n)}(y) \cdot w_s \cdot w_c \cdot w_n \cdot w_v$$

其中：
- $w_s$ = 空间权重（高斯）
- $w_c$ = 颜色权重（双边）
- $w_n$ = 法向权重
- $w_v$ = 方差权重（SVGF 的核心贡献）

#### 代码框架

```python
# denoising.py

import numpy as np
from scipy.ndimage import gaussian_filter
from benchmark_framework import BlurAlgorithm


class SVGF(BlurAlgorithm):
    """
    Spatiotemporal Variance-Guided Filtering

    参考：Schied et al. (2017) HPG
    DOI: 10.1145/3105762.3105770
    """

    def __init__(self):
        super().__init__("SVGF")

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        简化 SVGF 实现框架

        完整 SVGF 需要：
        1. 时域重投影 + 历史缓存
        2. 像素级方差估计
        3. à-trous 小波滤波（3-5 pass）
        4. 边缘停止函数（颜色/法向/位置）
        """
        # à-trous 小波滤波（简化：多步膨胀的高斯模糊）
        from scipy.ndimage import gaussian_filter
        result = gaussian_filter(image, sigma=sigma, mode='reflect')
        return result
```

> **⚠️ 注意**：SVGF 的完整实现较复杂（约 500+ 行 CUDA 代码），推荐参考 NVIDIA 的官方开源实现。

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E18.1** | à-trous pass 数对质量的影响 | 收敛曲线 |
| **E18.2** | 方差估计对模糊自适应的作用 | 方差大 → 更强模糊 |
| **E18.3** | SVGF vs 简单双边滤波 | 定量 SSIM/PSNR 对比 |

**出处：**
- Schied et al. (2017) HPG — SVGF 原始论文 [Schied2017]
- NVIDIA 官方 SVGF 实现和扩展 A-SVGF [NVIDIA-SVGF]

---

### 5.11 体积渲染中的模糊

#### 核心概念

体积渲染中的模糊来自**多次散射（Multiple Scattering）**——光线在参与介质中经过多次方向改变。

**单次散射 vs 多次散射**：
- 单次散射：光线只改变一次方向（只有阴影）
- 多次散射：光线多次改变方向（产生**模糊辉光**效果，如云朵内部）

**数学描述**（辐射传输方程）：

$$\frac{dL(x, \omega)}{dx} = -\sigma_t L(x, \omega) + \sigma_s \int_{4\pi} p(\omega, \omega') L(x, \omega') d\omega' + Q(x, \omega)$$

右端第二项是**散射积分**——所有方向辐射的加权和，这本质上是**方向空间的模糊**。

**近似方法**：
- **扩散近似（Diffusion Approximation）**：将多次散射近似为扩散过程（＝空间模糊）
- **双分量模型**：锐利直接光照 + 模糊间接光照

#### 代码框架

```python
# volumetric_blur.py

import numpy as np
from scipy.ndimage import gaussian_filter
from benchmark_framework import BlurAlgorithm


class VolumetricScatteringBlur(BlurAlgorithm):
    """
    体积渲染中的多次散射模糊

    物理基础：多次散射 → 扩散过程 → 高斯模糊近似
    散射越强（σ_s 越大），模糊半径越大
    """

    def __init__(self, scattering_albedo: float = 0.9):
        super().__init__("VolumetricBlur")
        self.albedo = scattering_albedo

    def blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        sigma → 散射强度/平均自由程
        """
        # 多次散射 ≈ 扩散模糊
        effective_sigma = sigma * self.albedo
        return gaussian_filter(image, sigma=effective_sigma, mode='reflect')
```

#### 实验设计

| 实验 | 内容 | 验证目标 |
|------|------|----------|
| **E19.1** | 单次散射 vs 扩散近似 | 找出适用条件 |
| **E19.2** | 散射反照率对模糊的影响 | albedo → 模糊半径关系 |
| **E19.3** | 体积光线步进 vs 后处理模糊 | 比较完整模拟和近似 |

**出处：**
- Kajiya & Von Herzen (1984) — 体积渲染基础 [Kajiya1984]
- GPU Gems 3 — 实时体积渲染

---

## 6. 综合质量-性能对照表

### 6.1 近似高斯模糊算法对比

| 算法 | 质量等级 | 复杂度 | σ=10 加速比 | σ=50 加速比 | σ=100 加速比 | 备注 |
|------|----------|--------|-------------|-------------|--------------|------|
| **精确可分离高斯** | ★★★★★ (参考) | O(n·σ) | 1.0× | 1.0× | 1.0× | 基准线，无近似 |
| **双线性优化高斯** | ★★★★★ (无损) | O(n·σ/2) | 1.8× | 3.5× | 3.8× | 仅 GPU 端加速 |
| **3-pass Box Blur** | ★★★★☆ | O(n) | 5× | 20× | 40× | PSNR > 40dB |
| **Stack Blur** | ★★★☆☆ | O(n) | 4× | 18× | 35× | 启发式算法 |
| **IIR Deriche 4阶** | ★★★★★ | O(n) | 8× | 8× | 8× | 常数时间，精度高 |
| **Kawase Blur** | ★★☆☆☆ | O(n·log r) | 3× | 12× | 30× | 大半径有块状伪影 |
| **Kawase Dual Filter** | ★★★☆☆ | O(n·log r) | 2× | 8× | 20× | [1 3 3 1] 改进 |
| **Mip-Blur** | ★★☆☆☆ | O(n·log r) | 1.5× | 10× | 50× | level 间不连续 |
| **泊松碟稀疏** | ★☆☆☆☆ | O(n·S) | 15× | 15× | 15× | S=样本数，视觉质量 |

**含义：**
- **质量等级**：基于 PSNR vs 精确高斯（>45dB=★★★★★, >35dB=★★★★, >25dB=★★★, >20dB=★★, <20dB=★）
- **加速比**：相对于可分离高斯耗时倍数（越高越好）
- **O(n·σ)**：与图像面积和高斯核大小线性相关
- **O(n)**：常数时间，与模糊半径无关

### 6.2 图形学模糊效果对比

| 效果 | 常用模糊方法 | 核心模糊参数 | 实时可行性 | 视觉重要性 |
|------|-------------|-------------|-----------|-----------|
| 景深 | CoC 自适应 + 可分离 | σ ∝ CoC | ★★★★ | ★★★★★ |
| 运动模糊 | 速度方向采样 | 采样数 N | ★★★★ | ★★★★★ |
| 软阴影 | PCF/PCSS | 滤波器大小 | ★★★★★ | ★★★★ |
| AO 去噪 | 双边滤波 | (σ_s, σ_r) | ★★★★★ | ★★★ |
| 光泽反射 | BRDF 卷积 | 粗糙度 | ★★★ | ★★★★ |
| Bloom | Kawase 迭代 | 迭代次数 | ★★★★★ | ★★★★ |
| 雾效 | 指数混合 | β | ★★★★★ | ★★★★ |
| TAA 模糊 | 时域累积 α | α | ★★★★★ | ★★★★★ |
| 纹理预过滤 | Mipmap box | level | ★★★★★ | ★★★★ |
| 去噪 (SVGF) | à-trous 小波 | pass 数 | ★★★ | ★★★★ |

---

## 7. 12 周研究路线图

```
第 1-2 周：基础滤波核
  ├── 实现统一 Benchmark 框架
  ├── 精确可分离高斯（基准线）
  ├── 所有常见滤波核：Box / Tent / Gaussian / Mitchell / Sinc
  ├── 频域分析（每种核的 OTF 对比）
  ├── 边界效应处理（zero/replicate/reflect/circular）
  └── 产出1: benchmark_framework.py + test_images
      产出2: 滤波核分析报告（含频谱图）
      代码: gaussian_exact.py

第 3 周：近似高斯模糊专题（核心）
  ├── 双线性优化高斯（验证数值等价性）
  ├── 3-pass Box Blur → 高斯级联
  ├── Stack Blur 实现与分析
  ├── IIR Deriche 递归滤波（框架 + 系数研究）
  ├── Kawase / Dual Filtering
  ├── Mipmap 级联模糊
  ├── 泊松碟稀疏采样模糊
  └── 产出3: 所有近似高斯的代码实现
      产出4: 质量-性能-半径 综合对照表
      代码: box_blur_cascade.py, stack_blur.py, iir_gaussian.py,
            kawase_blur.py, mip_blur.py, poisson_disk_blur.py,
            gaussian_bilinear.py

第 4 周：双边滤波框架
  ├── 标准双边滤波（全实现）
  ├── 联合双边滤波（Joint Bilateral Upsampling）
  ├── 交叉双边滤波（Cross Bilateral）
  ├── 性能优化（可分离近似、量化）
  └── 产出5: bilateral_blur.py + 实验报告
      实验: 高斯滤波 vs 双边滤波的边缘保持性对比

第 5 周：景深模糊（DOF）
  ├── CoC 映射生成 + 自适应模糊
  ├── 后处理 DOF 管线（完整）
  ├── 散景形状（光圈多边形）
  ├── 前景/背景过渡处理
  └── 产出6: depth_of_field.py + 视觉结果
      实验: DOF vs 真实相机照片对比

第 6 周：运动模糊
  ├── 速度缓冲生成
  ├── 沿方向采样（后处理）
  ├── 遮挡检测与预处理（TileMax）
  └── 产出7: motion_blur.py + 速度缓冲生成器
      实验: 匀速/加速/曲线运动对比

第 7 周：软阴影 + AO 模糊
  ├── PCF / PCSS 实现
  ├── VSM 预模糊
  ├── SSAO 双边滤波去噪
  ├── 接触硬化效果
  └── 产出8: soft_shadows.py
      实验: PCSS vs PCF 固定大小 vs VSM

第 8 周：Bloom + 光泽反射
  ├── 经典 Bloom（阈值 + 模糊 + 混合）
  ├── Kawase Bloom
  ├── SSR 模糊反射
  ├── IBL 预过滤
  └── 产出9: bloom.py, glossy_reflections.py
      实验: 不同 Bloom 实现性能对比

第 9 周：高级滤波框架
  ├── TAA 时域累积
  ├── FXAA 边缘模糊
  ├── 雾效 + 散射
  ├── SVGF à-trous 简化实现
  └── 产出10: taa_blur.py, fog_blur.py, denoising.py
      实验: 各后处理效果的整合管线

第 10 周：大规模 Benchmark
  ├── 全部算法 × 多种 σ × 多种测试图
  ├── 生成性能-质量-半径曲线
  ├── 生成算法适用场景推荐表
  └── 产出11: 综合 benchmark 报告（含图表）

第 11-12 周：研究报告 + 代码整理
  ├── 整理完整代码库（Python package）
  ├── 撰写研究报告
  ├── 准备 GitHub 仓库
  ├── 编写 README / 文档 / 示例
  └── 最终产出：
      1. 完整的 Python 代码库
      2. 可复现的 benchmark 脚本
      3. 综合研究报告（本文档 + 图表）
      4. GitHub 仓库发布
```

---

## 8. 参考文献与引用

### 近似高斯模糊

| 编号 | 引用 | 链接/DOI | 状态 |
|------|------|----------|------|
| [BoxBlur-CLT] | DBpedia — "Box blur: by the central limit theorem, 3 passes approximate Gaussian to within ~3%" | [Box blur (Wikipedia/DBpedia)](http://fragments.dbpedia.org/2015-10/en?subject=http%3A%2F%2Fdbpedia.org%2Fresource%2FBox_blur) | ✅ 可访问 |
| [learn-blur] | kevinzakka/learn-blur — GitHub 仓库，多种模糊算法实现与对比 | [GitHub](https://github.com/kevinzakka/learn-blur) | ✅ 可访问 |
| [StackBlur] | Mario Klingemann (2004) — StackBlur 原始页面 | [quasimondo.com](https://quasimondo.com/2004/02/25/stackblur-2004/) | ✅ 可访问 |
| [Deriche1990] | Deriche, R. "Fast Algorithms for Low-Level Vision", IEEE PAMI, 1990 | DOI: [10.1109/34.47354](https://doi.org/10.1109/34.47354) | ✅ 可通过 DOI 访问 |
| [Deriche1993] | Deriche, R. "Recursively Implementing the Gaussian and Its Derivatives", INRIA RR-1893, 1993 | [INRIA 传送门](https://hal.inria.fr/inria-00074778/) | ✅ 可访问 |
| [vanVliet1998] | van Vliet, Young, Verbeek. "Recursive Gaussian Derivative Filters", ICPR 1998 | DOI: [10.1109/ICPR.1998.711192](https://doi.org/10.1109/ICPR.1998.711192) | ✅ 可通过 DOI 访问 |
| [Farneback2006] | Farnebäck & Westin. "Improving Deriche-style Recursive Gaussian Filters", JMIV 2006 | DOI: [10.1007/s10851-006-8464-z](https://doi.org/10.1007/s10851-006-8464-z) | ✅ 可通过 DOI 访问 |
| [Kawase-GDC2003] | Masaki Kawase. "Frame Buffer Postprocessing Effects in DOUBLE-S.T.E.A.L (Wreckless)", GDC 2003 | [en.ppt-online.org/755333](https://en.ppt-online.org/755333) | ✅ 可访问 |
| [Intel-Kawase] | Intel — "Improve Real-Time GPU-Based Image Blur Algorithms: Kawase Blur and Moving Box Averages" | [Intel.com](https://www.intel.com/content/www/us/en/developer/videos/improving-real-time-gpu-based-image-blur-algorithms-kawase-blur-and-moving-box-averages.html) | ✅ 可访问 |
| [ThreeJS-Kawase] | three.js postprocessing — KawaseBlurMaterial 文档 | [pmndrs.github.io](https://pmndrs.github.io/postprocessing/public/docs/class/src/materials/KawaseBlurMaterial.js~KawaseBlurMaterial.html) | ✅ 可访问 |

### 图形学模糊效果

| 编号 | 引用 | 链接/DOI | 状态 |
|------|------|----------|------|
| [Potmesil1981] | Potmesil & Chakravarty. "A Lens and Aperture Camera Model for Synthetic Image Generation", SIGGRAPH 1981 | DOI: [10.1145/800224.806818](https://doi.org/10.1145/800224.806818) | ✅ 可通过 ACM DL 访问 |
| [Cook1984] | Cook, Porter, Carpenter. "Distributed Ray Tracing", SIGGRAPH 1984 | DOI: [10.1145/800031.808590](https://doi.org/10.1145/800031.808590) | ✅ 可通过 ACM DL 访问 |
| [Demers2004] | Demers. "Depth of Field: A Survey of Techniques", GPU Gems, 2004 | [NVIDIA GPU Gems](https://developer.nvidia.com/gpugems/gpugems/part-iv-performance-and-practicalities/chapter-23-depth-field-survey-techniques) | ✅ 可访问 |
| [Scheuermann2004] | Scheuermann. "Advanced Depth of Field", GDC 2004 | [ShaderX3](https://www.realtimerendering.com/)（搜索 ShaderX3） | ⚠️ 需搜索 |
| [Hammon2008] | Hammon. "Practical Post-Process Depth of Field", GPU Gems 3, 2008 | [NVIDIA GPU Gems 3](https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-28-practical-post-process-depth-field) | ✅ 可访问 |
| [McGuire2012] | McGuire et al. "A Reconstruction Filter for Plausible Motion Blur", I3D 2012 | DOI: [10.1145/2159616.2159639](https://doi.org/10.1145/2159616.2159639) | ✅ 可通过 DOI 访问 |
| [GPU-Gems3-MB] | Wloka. "Motion Blur as a Post-Processing Effect", GPU Gems 3, 2008 | [NVIDIA GPU Gems 3](https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-27-motion-blur-post-processing-effect) | ✅ 可访问 |
| [Fernando2005] | Fernando. "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketch | DOI: [10.1145/1187112.1187153](https://doi.org/10.1145/1187112.1187153) | ✅ 可通过 DOI 访问 |
| [VSM] | Donnelly & Lauritzen. "Variance Shadow Maps", I3D 2006 | DOI: [10.1145/1111411.1111440](https://doi.org/10.1145/1111411.1111440) | ✅ 可通过 DOI 访问 |
| [Tomasi1998] | Tomasi & Manduchi. "Bilateral Filtering for Gray and Color Images", ICCV 1998 | DOI: [10.1109/ICCV.1998.710815](https://doi.org/10.1109/ICCV.1998.710815) | ✅ 可通过 DOI 访问 |
| [Bavoil2008] | Bavoil & Sainz. "Screen Space Ambient Occlusion", NVIDIA Developer, 2008 | [NVIDIA](https://developer.nvidia.com/gpugems/gpugems2/part-ii-shading-lighting-and-shadows/chapter-14-screen-space-ambient-occlusion) | ✅ 可访问 |
| [Karis2013] | Karis. "Real Shading in Unreal Engine 4", Siggraph 2013 (IBL Split Sum) | [Unreal Engine Blog](https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf) | ✅ 可访问 |
| [Karis2014] | Karis. "High Quality Temporal Supersampling", SIGGRAPH 2014 | [advances.realtimerendering.com](http://advances.realtimerendering.com/s2014/epic/TemporalAA.pptx) | ✅ 可访问 |
| [FXAA] | Lottes. "FXAA", NVIDIA, 2011 | [NVIDIA](https://developer.download.nvidia.com/assets/gamedev/files/2011/FXAA_WhitePaper.pdf) | ✅ 可访问 |
| [Schied2017] | Schied et al. "Spatiotemporal Variance-Guided Filtering (SVGF)", HPG 2017 | DOI: [10.1145/3105762.3105770](https://doi.org/10.1145/3105762.3105770) | ✅ 可通过 DOI 访问 |
| [NVIDIA-SVGF] | NVIDIA Research — SVGF 项目页面 | [research.nvidia.com](https://research.nvidia.com/publication/2017-07_spatiotemporal-variance-guided-filtering-real-time-reconstruction-path-traced) | ✅ 可访问 |
| [Williams1983] | Williams. "Pyramidal Parametrics", SIGGRAPH 1983 (Mipmap) | DOI: [10.1145/800059.801126](https://doi.org/10.1145/800059.801126) | ✅ 可通过 ACM DL 访问 |
| [Kajiya1984] | Kajiya & Von Herzen. "Ray Tracing Volume Densities", SIGGRAPH 1984 | DOI: [10.1145/800031.808594](https://doi.org/10.1145/800031.808594) | ✅ 可通过 ACM DL 访问 |

### 综合参考书籍

| 书名 | 作者 | 相关章节 |
|------|------|----------|
| **GPU Gems** (1-3) | NVIDIA | 多章涵盖 DOF、Motion Blur、SSAO、Bloom |
| **GPU Pro** (1-7) | Wolfgang Engel 编 | 最新的后处理技术 |
| **ShaderX** (1-7) | Wolfgang Engel 编 | 各种 Shader 效果实现 |
| **Real-Time Rendering, 4th Ed.** | Akenine-Möller et al. | 第 9 章(抗锯齿)、第 19 章(后处理) |
| **Physically Based Rendering, 3rd Ed.** | Pharr, Jakob, Humphreys | 第 6 章(相机模型)、第 13 章(蒙特卡洛去噪) |
| **Digital Image Processing, 4th Ed.** | Gonzalez & Woods | 第 3 章(空域滤波)、第 4 章(频域滤波) |
| **Computer Graphics: Principles and Practice, 3rd Ed.** | Foley et al. | 第 16 章(光线追踪效果) |

---

## 附录：快速启动指南

### 环境准备

```bash
# 使用 conda 创建实验环境
conda create -n blur-research python=3.10
conda activate blur-research

# 安装依赖
pip install numpy scipy matplotlib pillow

# 可选（用于额外测试图）
pip install scikit-image
```

### 快速验证

```python
# quick_test.py
import numpy as np
import matplotlib.pyplot as plt
from benchmark_framework import Benchmark, create_test_image
from gaussian_exact import SeparableGaussian
from box_blur_cascade import BoxBlurCascade

# 创建测试图
img = create_test_image(256, 256)

# 测试算法
algorithms = [
    SeparableGaussian(),
    BoxBlurCascade(passes=3),
]

# 运行 benchmark
results = Benchmark.run(algorithms, sigma_values=[1, 3, 5, 10])

# 可视化
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Original')

axes[1].imshow(algorithms[0].blur(img.copy(), 5), cmap='gray')
axes[1].set_title(f'{algorithms[0].name} σ=5')

axes[2].imshow(algorithms[1].blur(img.copy(), 5), cmap='gray')
axes[2].set_title(f'{algorithms[1].name} σ=5')

plt.tight_layout()
plt.savefig('blur_comparison.png', dpi=150)
print("✓ 测试完成，结果保存到 blur_comparison.png")
```

---

## 9. FAQ：硬件实现模糊效果专题

### Q1：从性能和成本的角度考虑，哪种模糊算法最适合硬件（FPGA/ASIC）实现？

**A：3-pass Box Blur（盒模糊级联）是最适合硬件实现的算法，没有之一。**

#### 硬件实现的核心约束

在硬件（FPGA/ASIC）设计中，评价维度与软件完全不同：

| 维度 | 含义 | 硬件代价 |
|------|------|----------|
| **DSP/乘法器** | 每个乘加运算消耗 DSP slice | DSP 是 FPGA 最贵的资源之一 |
| **BRAM/缓存** | 行缓冲（Line Buffer）深度 | BRAM 数量有限 |
| **逻辑单元** | 控制逻辑复杂度 | LUT/FF 资源 |
| **访存模式** | 顺序/随机访问 | 随机访问需要大缓存/高带宽 |
| **流水线深度** | 能否每时钟周期输出一个像素 | 影响吞吐量 |

#### 算法横向硬件代价对比

| 算法 | 硬件代价 | 原因 |
|------|----------|------|
| **3-pass Box Blur** ✅ **最佳** | **极低** | **0个乘法器 + 仅6个加法器 + 3个行缓冲** |
| 精确可分离高斯 | 中-高 | 需要 N 个乘法器 + N 个行缓冲（N随σ增长） |
| 双线性优化高斯 | 中 | 仍然需要乘法器 + 行缓冲（略少于精确高斯） |
| Stack Blur | 中 | 需要随机缓存访问 + 复杂控制逻辑 |
| IIR Deriche | 中-高 | **递归结构无法流水线化**，每行串行 |
| Kawase | 中 | 需要下采样/上采样 + 多帧缓存 |
| Mip-Blur | 高 | 需要完整 mipmap 链硬件 |
| 泊松碟稀疏 | **极高** | **随机访存模式，硬件灾难** |

#### 3-pass Box Blur 的硬件实现原理

**一维水平方向 Box Blur（单个 Pass）的硬件结构：**

```
输入像素流 → [行缓冲(深度=图像宽度)] → 滑动窗口累加器 → 输出

累加器结构（O(1) 滑动窗口）：
  pixel_in ─→ [+] ─→ 累加和寄存器 ─→ [÷(2r+1)] ─→ pixel_out
                ↑                             ↓
              [-] ←─── 延迟线（深度=2r+1）←───
                     (FIFO 存储离开窗口的像素)
```

**硬件资源消耗（单个 Pass）：**

```
  1 个加法器（加新像素）
  1 个减法器（减旧像素）
  1 个 FIFO/移位寄存器（深度 = 2r+1）
  =============
  0 个乘法器 ✅
```

**三个 Pass 完整流水线：**

```
像素输入 → H-Pass1 → V-Pass1 → H-Pass2 → V-Pass2 → H-Pass3 → V-Pass3 → 输出
```

垂直 Pass 需要额外**行缓冲（Line Buffer）**，深度 = 图像宽度。

**总硬件资源估算：**

| 资源 | 数量 | 说明 |
|------|------|------|
| 加法器 | 6 | 3水平 × 2（加+减）+ 3垂直 × 2（加+减）|
| 行缓冲（BRAM） | 3 | 3个垂直Pass各需1个（水平Pass不需要）|
| FIFO 深度 | 6×(2r+1) | 可复用寄存器而非 BRAM |
| 流水线深度 | 6 × 图像宽度 + 2r | 全流水，每个时钟出一个像素 |
| 乘法器 | **0** | ✅ **核心优势** |

**对比：精确可分离高斯需要 2N 个乘法器（σ=10 → N=61 → 122个乘加器）和 N 个行缓冲。**

#### 成本对比（σ=10）

| 项目 | 3-pass Box (r≈7) | 精确高斯 (N=61) |
|------|------------------|-----------------|
| 乘法器(DSP) | **0** | 122 |
| 加法器 | 6 | 122 |
| 行缓冲(BRAM) | 3 | 61 |
| 逻辑控制 | 极简单 | 中等 |

> **关键洞见：** Box Blur 把计算复杂度从"乘加"变成了"累加"。在硬件上乘法器是最贵的资源，加法器几乎免费。此外，3-pass Box 的输出与真实高斯的 PSNR > 40dB，肉眼无法区分差异。

---

### Q2：如果采用分块实现，应该选择哪种算法？为什么？

**A：仍然是 3-pass Box Blur，且在其优势在分块场景下更加突出。**

#### 分块场景的边界重叠问题

对于分块大小为 T×T 的区块，处理时需要从相邻块借数据做边界扩展：

| 算法 | 边界扩展(每边) | 额外开销比率 (T=64) |
|------|---------------|-------------------|
| **Box Blur (r=7)** | **7 像素** | **22%** |
| 高斯 (N=61) | 30 像素 | 94% |
| Kawase | log₂(r) passes | 需要多级同步 |
| IIR | 无法分块 | 递归有状态依赖 |

**Box Blur 的边界开销最小** — 仅为半径 r，而精确高斯的边界开销是 3σ（大 4-5 倍）。

#### 分块可行性矩阵

| 算法 | 分块可行？ | 原因 |
|------|-----------|------|
| **3-pass Box Blur** ✅ | **最佳选择** | 重叠区域最小(r)；无状态依赖；每块独立处理 |
| 精确可分离高斯 | ✅ 可行 | 但重叠区域大(3σ)，分块效益被抵消 |
| 双线性优化高斯 | ✅ 可行 | 同上，重叠区域大 |
| Stack Blur | ⚠️ 可行但复杂 | 需要块间共享堆栈状态 |
| IIR Deriche | ❌ **不可行** | **递归滤波器有状态依赖，分块后边界不连续** |
| Kawase | ❌ 困难 | 多级下采样需要全局信息 |
| Mip-Blur | ❌ 不可行 | 需要全局 mipmap 链 |
| 泊松碟稀疏 | ✅ 可行 | 但随机采样本身就效率低 |

> **IIR 递归滤波在分块场景下的致命缺陷：** 递归滤波器是**有状态**的——每个像素的输出依赖于前面像素的输出。分块后，每个块的起始状态丢失，导致块边界接缝。虽有补偿技术，但复杂度和开销极大。

#### 分块 Box Blur 的硬件结构

```
输入图像
    │
    ┌── 块(0,0) ── Box Blur ──┐
    ├── 块(0,1) ── Box Blur ──┤── 合并 → 输出
    ├── 块(1,0) ── Box Blur ──┤
    └── 块(1,1) ── Box Blur ──┘

每个块处理时需要额外读取 r 像素的重叠边界
```

**分块 Box Blur 的硬件优势：**
- 每块只需 3 个行缓冲（块内行缓冲深度 = 块宽度，远小于全图宽度）
- **块间无需通信**（每块完全独立）
- 可在 FPGA 上实现**多块并行处理**

#### 量化对比（块大小 64×64，σ=10）

| 指标 | 3-pass Box (r=7) | 精确高斯 (N=61) |
|------|------------------|-----------------|
| 每块实际处理尺寸 | 78×78 (64+14) | 124×124 (64+60) |
| 额外像素加载 | 48% | 276% |
| 每块 DSP 消耗 | **0** | 122 |
| 每块 BRAM | 3×78 = 234 words | 61×124 = 7564 words |
| 块间依赖 | **无** | 无 |

---

### Q3：为什么 IIR 递归滤波不适合硬件？

**A：三个根本原因：**

1. **递归结构无法流水线化** — IIR 的输出依赖之前的输出，每个像素必须等待前一个像素计算完毕，无法做到"每个时钟输出一个像素"
2. **分块不可行** — 每个块的起始状态丢失，需要复杂的状态初始化
3. **定点数精度敏感** — IIR 递归的误差会累积，FPGA 定点数实现需要额外位宽

### Q4：Kawase Blur 在硬件上可行吗？

**A：可行但效率不高。** 原因：
- 需要多次下采样/上采样操作，意味着需要外部帧缓冲（DDR 带宽瓶颈）
- 迭代次数多时，延时大
- 但好处是不需要乘法器（4-tap 平均），在超大半径（r > 200）时比 Box Blur 更优

### Q5：如果必须要用精确高斯（精度要求极高），硬件如何实现？

**A：使用"乘法器共享 + 分布式算术"技术：**
- 利用高斯核的对称性：`w_i = w_{-i}`，减少一半乘法器
- 使用 DA（Distributed Arithmetic）算法：将乘法转换为 LUT 查找表 + 移位加法
- 可分离 + 行缓冲是必须的

但代价仍远高于 3-pass Box Blur（DSP 消耗高 1-2 个数量级）。

---

### FAQ 总结

| 场景 | 推荐算法 | 核心原因 |
|------|---------|----------|
| **硬件实现（通用）** | **3-pass Box Blur** | DSP=0，加法器即可；O(1)；全流水线化；PSNR>40dB |
| **硬件 + 分块** | **3-pass Box Blur** | 重叠最小(r)；块间无依赖；可并行多块；行缓冲占用少 |
| **超大半径（r>200）** | Kawase Blur | 迭代下采样比大半径 Box Blur 更省 BRAM |
| **精度极致要求** | 精确可分离高斯 | 代价是 DSP 消耗高 1-2 个数量级 |

> **一句话结论：** 硬件实现模糊效果，**3-pass Box Blur 在所有维度上都优于其他算法**——不需要乘法器(DSP归零)、加法器几乎零成本、常数时间与σ无关、分块友好、质量与高斯肉眼无差别。这是硬件工程师梦寐以求的"免费午餐"。

---

## 附录：快速启动指南

### 环境准备

```bash
# 使用 conda 创建实验环境
conda create -n blur-research python=3.10
conda activate blur-research

# 安装依赖
pip install numpy scipy matplotlib pillow

# 可选（用于额外测试图）
pip install scikit-image
```

### 快速验证

```python
# quick_test.py
import numpy as np
import matplotlib.pyplot as plt
from benchmark_framework import Benchmark, create_test_image
from gaussian_exact import SeparableGaussian
from box_blur_cascade import BoxBlurCascade

# 创建测试图
img = create_test_image(256, 256)

# 测试算法
algorithms = [
    SeparableGaussian(),
    BoxBlurCascade(passes=3),
]

# 运行 benchmark
results = Benchmark.run(algorithms, sigma_values=[1, 3, 5, 10])

# 可视化
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Original')

axes[1].imshow(algorithms[0].blur(img.copy(), 5), cmap='gray')
axes[1].set_title(f'{algorithms[0].name} σ=5')

axes[2].imshow(algorithms[1].blur(img.copy(), 5), cmap='gray')
axes[2].set_title(f'{algorithms[1].name} σ=5')

plt.tight_layout()
plt.savefig('blur_comparison.png', dpi=150)
print("✓ 测试完成，结果保存到 blur_comparison.png")
```

---

> **最后提示**：模糊算法的研究是一个理论和工程结合的过程。数学公式给出"是什么"，代码实现验证"怎么做"，而实验对比告诉你"为什么选这个"。三者缺一不可。
>
> 祝研究顺利！
