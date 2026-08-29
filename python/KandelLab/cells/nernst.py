"""Nernst 方程：离子浓度差决定平衡电位。

核心概念 #1：细胞膜两侧离子浓度差 + 选择性通透 → 膜电位。

模型
----
    E = (RT / zF) · ln([X]_o / [X]_i)

其中 R 为气体常数、T 为绝对温度、z 为离子价态、F 为法拉第常数、
[X]_o / [X]_i 为膜外/膜内浓度。

教科书锚点（37 °C，Kandel 标准浓度）：
    K⁺  ≈ −90 mV，Na⁺ ≈ +60 mV，Cl⁻ ≈ −90 mV，Ca²⁺ ≈ +132 mV
"""

from __future__ import annotations

import numpy as np

from .. import config


def nernst_potential(z, c_out, c_in, T=None):
    """计算单个离子的 Nernst 平衡电位（mV）。

    Parameters
    ----------
    z : int | float
        离子价态（K⁺/Na⁺ 取 +1，Ca²⁺ 取 +2，Cl⁻ 取 −1）。
    c_out, c_in : float
        膜外 / 膜内浓度（mM，同单位即可）。
    T : float | None
        绝对温度（K）；None 使用 config 生理温度 37 °C。

    Returns
    -------
    float : 平衡电位（mV）。
    """
    if z == 0:
        raise ValueError("z 不能为 0")
    if c_in <= 0 or c_out <= 0:
        raise ValueError("浓度必须为正数")
    T = config.T_KELVIN if T is None else T
    rt_f = config.R * T / config.F   # 单位 V
    return rt_f * 1000.0 / z * np.log(c_out / c_in)


def ion_equilibrium(ion, T=None):
    """使用 config 默认浓度计算某离子的平衡电位（mV）。

    Parameters
    ----------
    ion : str
        "K" / "Na" / "Ca" / "Cl"。
    """
    if ion not in config.ION_CONCENTRATIONS:
        raise KeyError(f"未知离子: {ion}")
    spec = config.ION_CONCENTRATIONS[ion]
    return nernst_potential(spec["z"], spec["o"], spec["i"], T)


def all_equilibria(T=None):
    """返回全部离子的平衡电位 dict。"""
    return {ion: ion_equilibrium(ion, T) for ion in config.ION_CONCENTRATIONS}


def concentration_scan(ion, c_out_range, T=None):
    """扫描膜外浓度并返回 (浓度数组, 电位数组)。

    用于实验 #1：改变 [K⁺]_o → 观察静息电位（Nernst 预测）。
    """
    spec = config.ION_CONCENTRATIONS[ion]
    c_out = np.asarray(c_out_range, dtype=float)
    E = np.array([nernst_potential(spec["z"], co, spec["i"], T) for co in c_out])
    return c_out, E


def temperature_scan(c_out, c_in, z=1, T_range=(280.0, 320.0, 41)):
    """温度扫描：返回 (温度数组, 电位数组)。"""
    T = np.linspace(T_range[0], T_range[1], T_range[2])
    E = np.array([nernst_potential(z, c_out, c_in, Ti) for Ti in T])
    return T, E
