"""Goldman–Hodgkin–Katz（GHK）方程：通透性加权的静息电位。

核心概念 #2：静息电位由多种离子的相对通透性共同决定。

模型
----
    V = (RT/F) · ln((P_K[K]_o + P_Na[Na]_o + P_Cl[Cl]_i)
                  / (P_K[K]_i + P_Na[Na]_i + P_Cl[Cl]_o))

P_X 为相对通透性；Cl⁻ 因价态为 −1 而取内外翻转。

验证锚点：
    单离子极限（其余 P=0）→ 还原为 Nernst 方程；
    生理通透性下静息电位 ≈ −70 mV。
"""

from __future__ import annotations

import numpy as np

from .. import config


def goldman_voltage(permeabilities, c_out, c_in, T=None, z=None):
    """GHK 方程计算静息电位（mV）。

    Parameters
    ----------
    permeabilities : dict[str, float]
        {"K": P_K, "Na": P_Na, "Cl": P_Cl, ...}，值为相对通透性。
    c_out, c_in : dict[str, float]
        {"K": …, "Na": …, "Cl": …} 膜外/膜内浓度（mM）。
    T : float | None
        绝对温度（K）。
    z : dict[str, int] | None
        各离子价态；None 时使用 config.ION_CONCENTRATIONS 的价态。

    Returns
    -------
    float : 静息电位（mV）。
    """
    T = config.T_KELVIN if T is None else T
    rt_f = config.R * T / config.F * 1000.0   # mV

    if z is None:
        z = {ion: config.ION_CONCENTRATIONS[ion]["z"] for ion in permeabilities}

    numer = 0.0
    denom = 0.0
    for ion, P in permeabilities.items():
        zi = z[ion]
        co = c_out[ion]
        ci = c_in[ion]
        if zi > 0:
            numer += P * co
            denom += P * ci
        else:
            numer += P * ci
            denom += P * co

    if numer <= 0 or denom <= 0:
        raise ValueError("GHK 分子/分母必须为正（所有 P 均为 0 时无定义）")
    return rt_f * np.log(numer / denom)


def resting_potential(T=None):
    """使用 config 生理浓度与默认通透性计算静息电位（mV）。"""
    perm = dict(config.PERMEABILITIES)
    conc = config.ION_CONCENTRATIONS
    c_out = {ion: conc[ion]["o"] for ion in perm}
    c_in = {ion: conc[ion]["i"] for ion in perm}
    return goldman_voltage(perm, c_out, c_in, T)


def single_ion_limit(ion, T=None):
    """计算"仅某离子通透"时的极限电位，应等于该离子 Nernst 电位。"""
    conc = config.ION_CONCENTRATIONS
    perm = {ion: 1.0}
    c_out = {ion: conc[ion]["o"]}
    c_in = {ion: conc[ion]["i"]}
    return goldman_voltage(perm, c_out, c_in, T)


def permeability_scan(na_frac, T=None, cl_perm=None):
    """扫描 Na⁺ 相对通透性（PK=1）对静息电位的影响。

    Parameters
    ----------
    na_frac : array_like
        P_Na 取值序列。
    T : float | None
    cl_perm : float | None
        P_Cl 固定值；None 使用 config 默认 0.45。

    Returns
    -------
    (na_frac, V) : 通透性序列与对应电位。
    """
    conc = config.ION_CONCENTRATIONS
    c_out = {ion: conc[ion]["o"] for ion in ("K", "Na", "Cl")}
    c_in = {ion: conc[ion]["i"] for ion in ("K", "Na", "Cl")}
    if cl_perm is None:
        cl_perm = config.PERMEABILITIES["Cl"]
    na_frac = np.asarray(na_frac, dtype=float)
    V = np.array([
        goldman_voltage({"K": 1.0, "Na": p, "Cl": cl_perm}, c_out, c_in, T)
        for p in na_frac
    ])
    return na_frac, V
