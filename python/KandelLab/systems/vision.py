"""视觉：Gabor 滤波器与方位选择性（简单细胞感受野）。

核心概念 #10a：感觉系统按特征调谐（视觉方位选择性）。

模型
----
    2D Gabor：
        g(x,y) = exp(−(x'² + γ²y'²)/(2σ²)) · cos(2π·f·x' + φ)
    其中 x' = x·cosθ + y·sinθ，y' = −x·sinθ + y·cosθ。

    简单细胞响应 = 感受野与图像的内积（点积）。

验证锚点：
    响应峰值出现在滤波器朝向 θ 处；
    调谐曲线半宽 ≈ 朝向带宽（σ 控制）的量级。
"""

from __future__ import annotations

import numpy as np

from .. import config


def gabor_2d(size=None, sf=None, sigma=None, theta=0.0, phi=None, kappa=None,
             gamma=None):
    """生成 2D Gabor 滤波器核。

    Parameters
    ----------
    size : int
        核边长（像素）。
    sf : float
        空间频率（cycles/pixel）。
    sigma : float
        高斯包络标准差。
    theta : float
        朝向（弧度）。
    phi : float
        相位（弧度）。
    gamma : float
        纵横比（γ）；None 用 kappa 或 config 默认。
    """
    p = config.GABOR_DEFAULTS
    size = int(p["size"]) if size is None else int(size)
    sf = p["sf"] if sf is None else sf
    sigma = p["sigma"] if sigma is None else sigma
    phi = p["phi"] if phi is None else phi
    gamma = p["kappa"] if gamma is None else (kappa if gamma is None else gamma)

    half = (size - 1) / 2.0
    y, x = np.mgrid[0:size, 0:size].astype(float) - half
    xr = x * np.cos(theta) + y * np.sin(theta)
    yr = -x * np.sin(theta) + y * np.cos(theta)
    envelope = np.exp(-(xr ** 2 + gamma ** 2 * yr ** 2) / (2 * sigma ** 2))
    grating = np.cos(2 * np.pi * sf * xr + phi)
    kernel = envelope * grating
    return kernel - kernel.mean()


def gabor_bank(n_orientations=8, size=None, sf=None, sigma=None, phi=0.0,
               gamma=None):
    """朝向数组（0..π）均匀分布的 Gabor 滤波器组。

    Returns
    -------
    (orientations, filters) : 朝向列表与滤波器列表。
    """
    thetas = np.linspace(0.0, np.pi, n_orientations, endpoint=False)
    filters = [gabor_2d(size, sf, sigma, th, phi, gamma=gamma)
               for th in thetas]
    return thetas, filters


def simple_cell_response(image, kernel):
    """简单细胞响应：图像与核的内积（线性滤波，取绝对值整流）。"""
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    return float(np.abs(np.sum(image * kernel)))


def orientation_tuning(image, thetas=None, filters=None, n_orientations=8,
                       **gabor_kwargs):
    """计算图像在各朝向上的响应 → 调谐曲线。

    Returns
    -------
    (angles, responses) : 朝向（弧度）与响应。
    """
    if thetas is None or filters is None:
        thetas, filters = gabor_bank(n_orientations, **gabor_kwargs)
    responses = np.array([simple_cell_response(image, k) for k in filters])
    return np.asarray(thetas), responses


def tuning_halfwidth(angles, responses):
    """调谐曲线半宽（度）：相对峰值 1/√2 处的半峰全宽 / 2。

    通过包络插值在峰值两侧定位响应降到峰值的 1/√2 处的角度，
    取两者距离的一半。
    """
    angles = np.asarray(angles, dtype=float)
    responses = np.asarray(responses, dtype=float)
    deg = np.degrees(angles)
    resp = responses - responses.min()
    if resp.max() <= 0:
        return float("nan")
    resp = resp / resp.max()

    peak_idx = int(np.argmax(resp))
    target = 1.0 / np.sqrt(2.0)
    left = right = None

    # 向峰值左侧找第一次跨过 target 的区间并线性插值
    for i in range(peak_idx, 0, -1):
        if min(resp[i - 1], resp[i]) <= target <= max(resp[i - 1], resp[i]):
            frac = (target - resp[i]) / (resp[i - 1] - resp[i])
            left = deg[i - 1] + frac * (deg[i] - deg[i - 1])
            break
    # 向峰值右侧找
    for i in range(peak_idx, len(resp) - 1):
        if min(resp[i], resp[i + 1]) <= target <= max(resp[i], resp[i + 1]):
            frac = (target - resp[i]) / (resp[i + 1] - resp[i])
            right = deg[i] + frac * (deg[i + 1] - deg[i])
            break

    if left is None or right is None:
        return float("nan")
    return float(0.5 * (right - left))


def grating_image(size=(64, 64), sf=0.08, theta=np.pi / 4, phi=0.0,
                  contrast=1.0, mean=0.5):
    """生成正弦光栅图像（用于刺激简单细胞）。"""
    h, w = size
    y, x = np.mgrid[0:h, 0:w].astype(float)
    xr = x * np.cos(theta) + y * np.sin(theta)
    return mean + contrast * mean * np.cos(2 * np.pi * sf * xr + phi)
