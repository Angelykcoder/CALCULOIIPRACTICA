#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lorenz_gini.py
--------------
Programa de verificación y generación de gráficas para el Proyecto Final
de Cálculo II: Curva de Lorenz e Índice de Gini (Sectores A y B).

Uso:
    python lorenz_gini.py

Genera la carpeta salida/ con resultados numéricos, tablas CSV y 6 figuras PNG.
Todo el cálculo simbólico se realiza con fracciones exactas (sympy.Rational).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sympy as sp
from scipy.integrate import quad

# ---------------------------------------------------------------------------
# Configuración global
# ---------------------------------------------------------------------------
SALIDA = Path("salida")
DPI = 300
FIGSIZE = (6, 5)  # aprox. 6 x 5 pulgadas para insertar en Word

# Estilo uniforme de gráficas
rcParams.update({
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "grid.alpha": 0.4,
})

# Símbolo simbólico
x = sp.symbols("x", real=True, nonnegative=True)

# ---------------------------------------------------------------------------
# Definición de las curvas con fracciones exactas (Paso 1)
# ---------------------------------------------------------------------------
L1 = sp.Rational(7, 10) * x**2 + sp.Rational(3, 10) * x**3
L2 = sp.Rational(15, 16) * x**4 + sp.Rational(1, 16) * x

SECTORES = {
    "A": {"L": L1, "nombre": "Sector A", "color": "#1f77b4"},
    "B": {"L": L2, "nombre": "Sector B", "color": "#d62728"},
}

# Valores esperados (sección 4 de la especificación) para asserts
ESPERADO = {
    "A": {
        "A_exact": sp.Rational(23, 120),
        "G_exact": sp.Rational(23, 60),
        "L05": sp.Rational(17, 80),          # 0.2125
        "L08": sp.Rational(1504, 2500),      # 0.6016  (calculado abajo)
        "L09": None,                        # se calcula
        "factor": "x*(1 - x)*(1 + 3*x/10)",
    },
    "B": {
        "A_exact": sp.Rational(9, 32),
        "G_exact": sp.Rational(9, 16),
        "L05": sp.Rational(23, 256),         # ≈ 0.08984375
        "L08": None,
        "L09": None,
        "factor": "(15/16)*(x - x**4)",
    },
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def crear_carpeta_salida() -> None:
    """Crea la carpeta salida/ si no existe."""
    SALIDA.mkdir(parents=True, exist_ok=True)


def imprimir_titulo(texto: str) -> None:
    """Imprime un encabezado visual en consola."""
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def float_6(val) -> float:
    """Convierte a float con 6 cifras significativas para mostrar."""
    return float(val)


# ---------------------------------------------------------------------------
# Paso 2: Verificar propiedades de Lorenz
# ---------------------------------------------------------------------------
def verificar_propiedades(clave: str, L: sp.Expr) -> dict:
    """
    Comprueba L(0)=0, L(1)=1, creciente, convexa y L(x) ≤ x.
    Devuelve un diccionario con los resultados y mensajes CUMPLE/NO CUMPLE.
    """
    resultados = {}

    # L(0) y L(1)
    L0 = sp.simplify(L.subs(x, 0))
    L1_val = sp.simplify(L.subs(x, 1))
    resultados["L0"] = L0
    resultados["L1"] = L1_val
    cumple_L0 = L0 == 0
    cumple_L1 = L1_val == 1
    print(f"  L(0) = {L0}  →  {'CUMPLE' if cumple_L0 else 'NO CUMPLE'} (debe ser 0)")
    print(f"  L(1) = {L1_val}  →  {'CUMPLE' if cumple_L1 else 'NO CUMPLE'} (debe ser 1)")

    # Derivada primera (creciente)
    Lp = sp.diff(L, x)
    Lp_simp = sp.simplify(Lp)
    # Evaluamos en algunos puntos del intervalo y comprobamos no negatividad
    # Analíticamente: Lp >= 0 en [0,1]
    # Para L1: 1.4x + 0.9x^2 = x(1.4 + 0.9x) >= 0
    # Para L2: (15/4)x^3 + 1/16 > 0
    # Usamos sp.minimum en [0,1] si es posible, o evaluación de extremos
    try:
        min_Lp = sp.minimum(Lp, x, domain=sp.Interval(0, 1))
        creciente = min_Lp is not None and min_Lp >= 0
    except Exception:
        # Fallback: evaluar en malla densa
        pts = np.linspace(0, 1, 201)
        fLp = sp.lambdify(x, Lp, "numpy")
        creciente = bool(np.all(fLp(pts) >= -1e-12))
        min_Lp = "evaluación numérica"
    resultados["Lp"] = Lp_simp
    print(f"  L'(x) = {Lp_simp}")
    print(f"  L'(x) ≥ 0 en [0,1]  →  {'CUMPLE' if creciente else 'NO CUMPLE'} (creciente)")

    # Derivada segunda (convexa)
    Lpp = sp.diff(Lp, x)
    Lpp_simp = sp.simplify(Lpp)
    try:
        min_Lpp = sp.minimum(Lpp, x, domain=sp.Interval(0, 1))
        convexa = min_Lpp is not None and min_Lpp >= 0
    except Exception:
        pts = np.linspace(0, 1, 201)
        fLpp = sp.lambdify(x, Lpp, "numpy")
        convexa = bool(np.all(fLpp(pts) >= -1e-12))
        min_Lpp = "evaluación numérica"
    resultados["Lpp"] = Lpp_simp
    print(f"  L''(x) = {Lpp_simp}")
    print(f"  L''(x) ≥ 0 en [0,1]  →  {'CUMPLE' if convexa else 'NO CUMPLE'} (convexa)")

    # x - L(x) ≥ 0  (bajo la diagonal)
    gap = sp.simplify(x - L)
    gap_fact = sp.factor(gap)
    resultados["gap"] = gap
    resultados["gap_fact"] = gap_fact
    try:
        min_gap = sp.minimum(gap, x, domain=sp.Interval(0, 1))
        bajo_diag = min_gap is not None and min_gap >= 0
    except Exception:
        pts = np.linspace(0, 1, 201)
        fgap = sp.lambdify(x, gap, "numpy")
        bajo_diag = bool(np.all(fgap(pts) >= -1e-12))
    print(f"  x − L(x) = {gap}")
    print(f"  Factorizado: {gap_fact}")
    print(f"  x − L(x) ≥ 0 en [0,1]  →  {'CUMPLE' if bajo_diag else 'NO CUMPLE'} (bajo la diagonal)")

    resultados["cumple_todo"] = cumple_L0 and cumple_L1 and creciente and convexa and bajo_diag
    return resultados


# ---------------------------------------------------------------------------
# Paso 3: Área de equidad paso a paso
# ---------------------------------------------------------------------------
def calcular_area(clave: str, L: sp.Expr) -> dict:
    """
    Calcula A = ∫₀¹ (x − L(x)) dx mostrando integrando, antiderivada y evaluación.
    """
    integrando = sp.simplify(x - L)
    print(f"  Integrando: x − L(x) = {integrando}")

    # Antiderivada indefinida
    H = sp.integrate(integrando, x)
    H_simp = sp.simplify(H)
    print(f"  Antiderivada H(x) = {H_simp}")

    H1 = sp.simplify(H.subs(x, 1))
    H0 = sp.simplify(H.subs(x, 0))
    print(f"  H(1) = {H1}")
    print(f"  H(0) = {H0}")

    A = sp.simplify(H1 - H0)
    A_float = float(A)
    print(f"  A = H(1) − H(0) = {A}  ≈  {A_float:.6f}")

    return {"integrando": integrando, "H": H_simp, "A": A, "A_float": A_float}


# ---------------------------------------------------------------------------
# Paso 4: Índice de Gini
# ---------------------------------------------------------------------------
def calcular_gini(A: sp.Expr) -> dict:
    """G = 2A en forma exacta y decimal (4 cifras)."""
    G = sp.simplify(2 * A)
    G_float = float(G)
    return {"G": G, "G_float": G_float}


# ---------------------------------------------------------------------------
# Paso 5: Verificación numérica (quad + Riemann)
# ---------------------------------------------------------------------------
def verificar_numerico(L: sp.Expr, A_exact: sp.Expr) -> dict:
    """
    Comprueba el valor analítico con scipy.quad y sumas de Riemann (punto medio).
    """
    f_gap = sp.lambdify(x, x - L, "numpy")

    # scipy.integrate.quad
    quad_val, quad_err = quad(f_gap, 0, 1)
    err_quad = abs(quad_val - float(A_exact))
    print(f"  scipy.quad:          A ≈ {quad_val:.10f}  (error abs = {err_quad:.2e})")

    # Sumas de Riemann (punto medio)
    ns = [10, 100, 1000, 10000]
    riemann = {}
    print("  Suma de Riemann (punto medio):")
    print(f"  {'n':>8}  {'A_approx':>14}  {'error abs':>12}")
    for n in ns:
        dx = 1.0 / n
        midpoints = np.linspace(dx / 2, 1 - dx / 2, n)
        suma = float(np.sum(f_gap(midpoints)) * dx)
        err = abs(suma - float(A_exact))
        riemann[n] = {"aprox": suma, "error": err}
        print(f"  {n:8d}  {suma:14.10f}  {err:12.2e}")

    return {"quad": quad_val, "err_quad": err_quad, "riemann": riemann}


# ---------------------------------------------------------------------------
# Paso 6: Tabla de percentiles
# ---------------------------------------------------------------------------
def tabla_percentiles() -> None:
    """
    Evalúa L(x) para x = 0.1, 0.2, ..., 1.0 y genera CSV + impresión formateada.
    """
    xs = np.arange(0.1, 1.01, 0.1)
    f1 = sp.lambdify(x, L1, "numpy")
    f2 = sp.lambdify(x, L2, "numpy")

    filas = []
    print(f"\n  {'x (pob.)':>10}  {'L1 acum.':>12}  {'1-L1 rico':>12}  "
          f"{'L2 acum.':>12}  {'1-L2 rico':>12}")
    print("  " + "-" * 62)
    for xv in xs:
        l1 = float(f1(xv))
        l2 = float(f2(xv))
        filas.append({
            "x": round(float(xv), 1),
            "L1_acumulado": l1,
            "L1_rico": 1 - l1,
            "L2_acumulado": l2,
            "L2_rico": 1 - l2,
        })
        print(f"  {xv*100:8.0f}%  {l1*100:11.2f}%  {(1-l1)*100:11.2f}%  "
              f"{l2*100:11.2f}%  {(1-l2)*100:11.2f}%")

    # Guardar CSV
    csv_path = SALIDA / "tabla_percentiles.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("x,L1_acumulado,L1_rico,L2_acumulado,L2_rico\n")
        for r in filas:
            f.write(f"{r['x']:.1f},{r['L1_acumulado']:.8f},{r['L1_rico']:.8f},"
                    f"{r['L2_acumulado']:.8f},{r['L2_rico']:.8f}\n")
    print(f"\n  Tabla guardada en {csv_path}")

    return filas


# ---------------------------------------------------------------------------
# Paso 7: Gráficas
# ---------------------------------------------------------------------------
def graficar_sector(clave: str, L: sp.Expr, A: sp.Expr, G: sp.Expr, color: str) -> None:
    """Genera fig1 (A) o fig2 (B): diagonal, curva y área sombreada."""
    fL = sp.lambdify(x, L, "numpy")
    xs = np.linspace(0, 1, 400)
    ys = fL(xs)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(xs, xs, "k--", linewidth=1.5, label="Equidad perfecta  y = x")
    ax.plot(xs, ys, color=color, linewidth=2, label=f"L(x) — Sector {clave}")
    ax.fill_between(xs, ys, xs, alpha=0.25, color=color, label="Área de equidad A")

    # Texto con valores exactos calculados por el programa
    texto = f"A = {A}\nG = {G}"
    ax.text(0.05, 0.75, texto, transform=ax.transAxes, fontsize=11,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.85))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Proporción acumulada de población (x)")
    ax.set_ylabel("Proporción acumulada de ingresos (y)")
    ax.set_title(f"Curva de Lorenz — Sector {clave}")
    ax.legend(loc="lower right")
    ax.set_aspect("equal")
    fig.tight_layout()
    ruta = SALIDA / f"fig{1 if clave == 'A' else 2}_sector_{clave}.png"
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def graficar_comparativa(A_A: sp.Expr, A_B: sp.Expr) -> None:
    """fig3: ambas curvas y ambas áreas sombreadas."""
    f1 = sp.lambdify(x, L1, "numpy")
    f2 = sp.lambdify(x, L2, "numpy")
    xs = np.linspace(0, 1, 400)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(xs, xs, "k--", linewidth=1.5, label="Equidad perfecta  y = x")
    ax.plot(xs, f1(xs), color="#1f77b4", linewidth=2, label="Sector A: L1(x)")
    ax.plot(xs, f2(xs), color="#d62728", linewidth=2, label="Sector B: L2(x)")
    ax.fill_between(xs, f1(xs), xs, alpha=0.2, color="#1f77b4", label="A1")
    ax.fill_between(xs, f2(xs), xs, alpha=0.2, color="#d62728", label="A2")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Proporción acumulada de población (x)")
    ax.set_ylabel("Proporción acumulada de ingresos (y)")
    ax.set_title("Curvas de Lorenz — Comparativa Sectores A y B")
    ax.legend(loc="lower right")
    ax.set_aspect("equal")
    fig.tight_layout()
    ruta = SALIDA / "fig3_comparativa.png"
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def graficar_brecha() -> None:
    """fig4: brecha x − L(x) para ambos sectores."""
    f1 = sp.lambdify(x, x - L1, "numpy")
    f2 = sp.lambdify(x, x - L2, "numpy")
    xs = np.linspace(0, 1, 400)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(xs, f1(xs), color="#1f77b4", linewidth=2, label="Brecha Sector A: x - L1(x)")
    ax.plot(xs, f2(xs), color="#d62728", linewidth=2, label="Brecha Sector B: x - L2(x)")
    ax.axhline(0, color="k", linewidth=0.8)

    ax.set_xlim(0, 1)
    ax.set_xlabel("Proporción acumulada de población (x)")
    ax.set_ylabel("Brecha de equidad  x − L(x)")
    ax.set_title("Brecha de desigualdad por cuantil")
    ax.legend(loc="upper right")
    fig.tight_layout()
    ruta = SALIDA / "fig4_brecha.png"
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def graficar_percentiles() -> None:
    """fig5: barras del 50 % más pobre y del 10 % más rico."""
    f1 = sp.lambdify(x, L1, "numpy")
    f2 = sp.lambdify(x, L2, "numpy")

    # 50 % más pobre → L(0.5); 10 % más rico → 1 − L(0.9)
    datos = {
        "50 % más pobre": [float(f1(0.5)) * 100, float(f2(0.5)) * 100],
        "10 % más rico": [(1 - float(f1(0.9))) * 100, (1 - float(f2(0.9))) * 100],
    }

    categorias = list(datos.keys())
    vals_A = [datos[c][0] for c in categorias]
    vals_B = [datos[c][1] for c in categorias]

    x_pos = np.arange(len(categorias))
    ancho = 0.35

    fig, ax = plt.subplots(figsize=FIGSIZE)
    barras_A = ax.bar(x_pos - ancho / 2, vals_A, ancho, label="Sector A", color="#1f77b4")
    barras_B = ax.bar(x_pos + ancho / 2, vals_B, ancho, label="Sector B", color="#d62728")

    ax.set_ylabel("Porcentaje del ingreso (%)")
    ax.set_title("Distribución del ingreso: 50 % más pobre y 10 % más rico")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.set_ylim(0, max(max(vals_A), max(vals_B)) * 1.25)

    # Etiquetas encima de las barras
    for bar in list(barras_A) + list(barras_B):
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    ruta = SALIDA / "fig5_percentiles.png"
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  Guardada: {ruta}")


def graficar_riemann(riemann_A: dict, riemann_B: dict, A_A: float, A_B: float) -> None:
    """fig6: convergencia de la suma de Riemann (escala log en n)."""
    ns = sorted(riemann_A.keys())
    err_A = [riemann_A[n]["error"] for n in ns]
    err_B = [riemann_B[n]["error"] for n in ns]

    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.loglog(ns, err_A, "o-", color="#1f77b4", linewidth=2, markersize=7, label="Error |An - A| Sector A")
    ax.loglog(ns, err_B, "s-", color="#d62728", linewidth=2, markersize=7, label="Error |An - A| Sector B")

    ax.set_xlabel("Número de subintervalos n (escala log)")
    ax.set_ylabel("Error absoluto (escala log)")
    ax.set_title("Convergencia de la suma de Riemann (punto medio)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.4)
    fig.tight_layout()
    ruta = SALIDA / "fig6_riemann.png"
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  Guardada: {ruta}")


# ---------------------------------------------------------------------------
# Paso 8: Reporte de texto
# ---------------------------------------------------------------------------
def escribir_reporte(res_A: dict, res_B: dict, filas: list) -> None:
    """Guarda salida/resultados.txt con resumen completo."""
    ruta = SALIDA / "resultados.txt"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("RESULTADOS — Curva de Lorenz e Índice de Gini\n")
        f.write("=" * 60 + "\n\n")

        for clave, res in [("A", res_A), ("B", res_B)]:
            f.write(f"SECTOR {clave}\n")
            f.write("-" * 40 + "\n")
            f.write(f"  L(0) = {res['props']['L0']},  L(1) = {res['props']['L1']}\n")
            f.write(f"  L'(x) = {res['props']['Lp']}\n")
            f.write(f"  L''(x) = {res['props']['Lpp']}\n")
            f.write(f"  x − L(x) factorizado = {res['props']['gap_fact']}\n")
            f.write(f"  Área A = {res['area']['A']}  ≈  {res['area']['A_float']:.6f}\n")
            f.write(f"  Gini G = {res['gini']['G']}  ≈  {res['gini']['G_float']:.4f}\n\n")

        f.write("COMPARACIÓN\n")
        f.write("-" * 40 + "\n")
        GA = res_A["gini"]["G_float"]
        GB = res_B["gini"]["G_float"]
        f.write(f"  G_A ≈ {GA:.4f},  G_B ≈ {GB:.4f}\n")
        f.write(f"  Diferencia G_B − G_A ≈ {GB - GA:.4f}\n")
        f.write(f"  Sector más desigual: {'B' if GB > GA else 'A'}\n\n")

        f.write("TABLA DE PERCENTILES (resumen)\n")
        f.write("-" * 40 + "\n")
        f.write(f"  {'x':>6}  {'L1 %':>8}  {'L2 %':>8}\n")
        for r in filas:
            f.write(f"  {r['x']*100:5.0f}%  {r['L1_acumulado']*100:7.2f}%  "
                    f"{r['L2_acumulado']*100:7.2f}%\n")

        f.write("\nCONCLUSIÓN\n")
        f.write("-" * 40 + "\n")
        f.write("El Sector B presenta mayor desigualdad de ingresos (G ≈ 0.5625 > 0.3833).\n")
        f.write("La curva de Lorenz de B se aleja más de la diagonal de equidad perfecta.\n")

    print(f"  Guardado: {ruta}")


# ---------------------------------------------------------------------------
# Asserts de valores esperados
# ---------------------------------------------------------------------------
def comprobar_assert(clave: str, A: sp.Expr, G: sp.Expr) -> None:
    """Verifica que los resultados coincidan con la tabla de la especificación."""
    esp = ESPERADO[clave]
    ok = True

    if A != esp["A_exact"]:
        print(f"  ERROR: A del Sector {clave} = {A}  ≠  {esp['A_exact']} (esperado)")
        ok = False
    if G != esp["G_exact"]:
        print(f"  ERROR: G del Sector {clave} = {G}  ≠  {esp['G_exact']} (esperado)")
        ok = False

    # Comprobar puntos característicos
    L = SECTORES[clave]["L"]
    L05 = sp.simplify(L.subs(x, sp.Rational(1, 2)))
    if L05 != esp["L05"]:
        print(f"  ERROR: L(0.5) Sector {clave} = {L05}  ≠  {esp['L05']}")
        ok = False

    if ok:
        print(f"  Asserts Sector {clave}: OK (coinciden con valores esperados)")
    else:
        print(f"  ¡ATENCIÓN! Algunos valores del Sector {clave} no coinciden.")
        # No abortamos; solo avisamos (según especificación: avisar y no continuar en silencio)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    crear_carpeta_salida()
    print("Programa de verificación — Curva de Lorenz e Índice de Gini")
    print("Sectores A y B | Cálculo II | Proyecto Final")

    resultados = {}

    # ---- Paso 1 (ya definido globalmente) ----
    imprimir_titulo("PASO 1 — Definición de las funciones (fracciones exactas)")
    print(f"  L₁(x) = {L1}")
    print(f"  L₂(x) = {L2}")

    # ---- Pasos 2–5 por sector ----
    for clave in ["A", "B"]:
        L = SECTORES[clave]["L"]
        nombre = SECTORES[clave]["nombre"]

        imprimir_titulo(f"PASO 2 — Propiedades de Lorenz ({nombre})")
        props = verificar_propiedades(clave, L)

        imprimir_titulo(f"PASO 3 — Área de equidad ({nombre})")
        area = calcular_area(clave, L)

        imprimir_titulo(f"PASO 4 — Índice de Gini ({nombre})")
        gini = calcular_gini(area["A"])
        print(f"  G = 2A = {gini['G']}  ≈  {gini['G_float']:.4f}")

        imprimir_titulo(f"PASO 5 — Verificación numérica ({nombre})")
        num = verificar_numerico(L, area["A"])

        # Asserts
        imprimir_titulo(f"Verificación de asserts ({nombre})")
        comprobar_assert(clave, area["A"], gini["G"])

        resultados[clave] = {
            "props": props,
            "area": area,
            "gini": gini,
            "num": num,
        }

    # Comparación global
    imprimir_titulo("COMPARACIÓN DE SECTORES")
    GA = resultados["A"]["gini"]["G"]
    GB = resultados["B"]["gini"]["G"]
    GA_f = resultados["A"]["gini"]["G_float"]
    GB_f = resultados["B"]["gini"]["G_float"]
    print(f"  G_A = {GA}  ≈  {GA_f:.4f}")
    print(f"  G_B = {GB}  ≈  {GB_f:.4f}")
    print(f"  Diferencia G_B − G_A = {sp.simplify(GB - GA)}  ≈  {GB_f - GA_f:.4f}")
    if GB_f > GA_f:
        print("  → El Sector B es más desigual.")
    else:
        print("  → El Sector A es más desigual.")

    # ---- Paso 6 ----
    imprimir_titulo("PASO 6 — Tabla de percentiles")
    filas = tabla_percentiles()

    # ---- Paso 7 ----
    imprimir_titulo("PASO 7 — Generación de gráficas")
    graficar_sector("A", L1, resultados["A"]["area"]["A"], resultados["A"]["gini"]["G"],
                    SECTORES["A"]["color"])
    graficar_sector("B", L2, resultados["B"]["area"]["A"], resultados["B"]["gini"]["G"],
                    SECTORES["B"]["color"])
    graficar_comparativa(resultados["A"]["area"]["A"], resultados["B"]["area"]["A"])
    graficar_brecha()
    graficar_percentiles()
    graficar_riemann(resultados["A"]["num"]["riemann"],
                     resultados["B"]["num"]["riemann"],
                     resultados["A"]["area"]["A_float"],
                     resultados["B"]["area"]["A_float"])

    # ---- Paso 8 ----
    imprimir_titulo("PASO 8 — Reporte de texto")
    escribir_reporte(resultados["A"], resultados["B"], filas)

    print("\n" + "=" * 70)
    print("Proceso terminado. Todos los archivos se encuentran en la carpeta salida/")
    print("=" * 70)


if __name__ == "__main__":
    main()
