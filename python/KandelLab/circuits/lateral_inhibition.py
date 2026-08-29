"""侧抑制与中心-周围感受野（Difference of Gaussians, DOG）。

核心概念 #7：侧抑制增强感觉对比（边缘增强、Mach band 现象）。

模型
----
    DOG 核（中心兴奋-周围抑制）：
        K(r) = A_c · exp(−r² / 2σ_c²) − A_s · exp(−r² / 2σ_s²)

    图像经 DOG 核卷积 → 均匀区域响应平坦、边缘处被增强。

验证锚点：
    均匀亮度输入 → 输出近似为 0（平坦）；
    阶跃边缘 → 边缘两侧出现亮/暗条纹（Mach band）。
"""

from __future__ import annotations

import numpy as np


def dog_1d(r, sigma_c, sigma_s, A_c=1.0, A_s=None):
    """一维 DOG 响应。A_s 默认取 A_c·(σ_s/σ_c)² 使体积守恒（零直流分量）。"""
    if A_s is None:
        A_s = A_c * (sigma_s / sigma_c) ** 2
    r = np.asarray(r, dtype=float)
    return A_c * np.exp(-r ** 2 / (2 * sigma_c ** 2)) \
        - A_s * np.exp(-r ** 2 / (2 * sigma_s ** 2))


def dog_kernel_2d(size, sigma_c, sigma_s, A_c=1.0):
    """二维 DOG 卷积核（零均值归一化）。"""
    half = size // 2
    y, x = np.mgrid[-half:half + 1, -half:half + 1]
    r2 = x ** 2 + y ** 2
    center = A_c * np.exp(-r2 / (2 * sigma_c ** 2))
    surround = A_c * (sigma_c / sigma_s) ** 2 * np.exp(-r2 / (2 * sigma_s ** 2))
    kernel = center - surround
    return kernel - kernel.mean()


def apply_kernel(image, kernel):
    """零填充 2D 卷积（FFT 实现，处理大核更稳定）。"""
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    kh, kw = kernel.shape
    ih, iw = image.shape
    out_size = (ih + kh - 1, iw + kw - 1)
    fft_img = np.fft.fft2(image, s=out_size)
    fft_k = np.fft.fft2(kernel, s=out_size)
    conv = np.fft.ifft2(fft_img * fft_k).real
    # 裁剪回原尺寸（'same' 语义，含边界填充）
    top = kh // 2
    left = kw // 2
    return conv[top:top + ih, left:left + iw]


def step_edge_image(size=(64, 128), left_value=0.2, right_value=0.8,
                    edge_col=None):
    """构造带垂直阶跃边缘的图像（用于 Mach band 演示）。"""
    h, w = size
    img = np.full((h, w), left_value)
    if edge_col is None:
        edge_col = w // 2
    img[:, edge_col:] = right_value
    return img


def mach_bands(size=(64, 128), sigma_c=2.0, sigma_s=6.0, left=0.2, right=0.8):
    """完整 Mach band 演示：返回 (原图, 输出, DOG 核)。"""
    img = step_edge_image(size, left, right)
    kernel = dog_kernel_2d(max(3, int(size[0] * 0.3)) * 2 + 1, sigma_c, sigma_s)
    out = apply_kernel(img, kernel)
    return img, out, kernel


def lateral_inhibit(image, sigma_c=2.0, sigma_s=6.0, gain=1.0, subtract=0.0):
    """对图像应用侧抑制：输出 = 原亮度 + gain·(DOG 卷积 − subtract)。

    subtract 用于扣除均匀区域的偏移，使平坦区域响应平坦。
    """
    img = np.asarray(image, dtype=float)
    kernel = dog_kernel_2d(max(3, int(min(img.shape) * 0.3)) * 2 + 1,
                           sigma_c, sigma_s)
    filtered = apply_kernel(img, kernel)
    return img + gain * (filtered - subtract)
