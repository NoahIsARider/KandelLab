"""Hebbian 学习：Hebb 规则、Oja 归一化、BCM 滑动阈值与 LTP/LTD 曲线。

核心概念 #6：突触强度随使用改变（"一起放电的神经元连接在一起"）。

模型
----
    Hebb 规则:   Δw = η · x · y          （关联输入 x 与输出 y）
    Oja 规则:    Δw = η · y · (x − y·w)  （含权重归一化，防发散）
    BCM:         Δw = η · x · y · (y − θ_M)
                 dθ_M/dt = (1/τ_θ) · (y² − θ_M)   （滑动阈值）

验证锚点：
    相关输入定向训练 → 选择性权重增强；
    BCM 曲线：低活动 y<θ_M → LTD，高活动 y>θ_M → LTP。
"""

from __future__ import annotations

import numpy as np

from .. import config


def hebb_update(w, x, y, eta=None):
    """单步 Hebb 规则：Δw = η·x·y。返回 (新权重, 权重变化)。"""
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    dw = eta * np.asarray(x, dtype=float) * float(y)
    return np.asarray(w, dtype=float) + dw, dw


def oja_update(w, x, y, eta=None):
    """单步 Oja 规则：Δw = η·y·(x − y·w)。"""
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    w = np.asarray(w, dtype=float)
    dw = eta * float(y) * (np.asarray(x, dtype=float) - float(y) * w)
    return w + dw, dw


def run_hebb(x_train, y_train, w0=None, eta=None, rule="hebb"):
    """离线训练：逐样本应用学习规则。

    Parameters
    ----------
    x_train : np.ndarray (T, n_in)
    y_train : np.ndarray (T,)
    w0 : np.ndarray | None
    eta : float | None
    rule : str
        "hebb" / "oja" / "bcmoja"

    Returns
    -------
    w : 训练后权重
    w_history : (T, n_in)
    """
    x_train = np.asarray(x_train, dtype=float)
    y_train = np.asarray(y_train, dtype=float)
    n_in = x_train.shape[1]
    w = np.zeros(n_in) if w0 is None else np.asarray(w0, dtype=float).copy()
    hist = np.empty((x_train.shape[0], n_in))
    for i, (x, y) in enumerate(zip(x_train, y_train)):
        if rule == "hebb":
            w, _ = hebb_update(w, x, y, eta)
        elif rule == "oja":
            w, _ = oja_update(w, x, y, eta)
        else:
            raise ValueError(f"未知规则: {rule}")
        hist[i] = w
    return w, hist


def correlated_inputs(pattern, noise_level=0.1, n_samples=500, seed=None):
    """围绕一个目标模式的加噪输入流（用于定向强化训练）。"""
    from ..utils.neuro import rng
    r = rng(seed)
    pattern = np.asarray(pattern, dtype=float)
    pattern = (pattern - pattern.mean()) / (pattern.std() + 1e-9)
    x = pattern[None, :] + noise_level * r.standard_normal(
        (n_samples, pattern.size))
    y = x @ pattern   # 与模式的点积作为输出活动
    return x, y


def lt_ltp_curve(y_range=(0.0, 3.0, 201), theta_M=None, eta=None, x=1.0):
    """BCM 的 LTD/LTP 曲线：输出活动 y → 权重变化 Δw。

    Returns
    -------
    (y, dW) : y 序列与对应权重变化（η·x·y·(y−θ_M)）。
    """
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    theta_M = config.HEBBIAN_DEFAULTS["theta_M"] if theta_M is None else theta_M
    y = np.linspace(y_range[0], y_range[1], y_range[2])
    dW = eta * x * y * (y - theta_M)
    return y, dW


class BCM:
    """BCM 滑动阈值模型。"""

    def __init__(self, n_in, eta=None, tau_theta=None, theta_0=0.0):
        p = config.HEBBIAN_DEFAULTS
        self.eta = p["eta"] if eta is None else eta
        self.tau_theta = p["tau_theta"] if tau_theta is None else tau_theta
        self.w = np.zeros(n_in)
        self.theta = theta_0

    def step(self, x):
        """单步在线更新。返回 (输出 y, 权重变化 Δw)。"""
        x = np.asarray(x, dtype=float)
        y = float(self.w @ x)
        dw = self.eta * x * y * (y - self.theta)
        self.w = self.w + dw
        self.theta = self.theta + (1.0 / self.tau_theta) * (y ** 2 - self.theta)
        return y, dw

    def train(self, x_train, y_ref=None, n_epochs=5):
        """循环训练。返回 (y_history, theta_history)。"""
        x_train = np.asarray(x_train, dtype=float)
        yh, th = [], []
        for _ in range(n_epochs):
            for x in x_train:
                y, _ = self.step(x)
                yh.append(y)
                th.append(self.theta)
        return np.array(yh), np.array(th)
