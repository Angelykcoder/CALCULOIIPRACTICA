<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Curva de Lorenz e Índice de Gini — Cálculo II</title>
  <style>
    :root {
      --bg: #0f1419;
      --card: #1a2332;
      --text: #e7ecf3;
      --muted: #9aa8bc;
      --accent: #3b82f6;
      --accent2: #ef4444;
      --border: #2a3648;
      --ok: #22c55e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
      padding: 2rem 1rem 4rem;
    }
    .wrap { max-width: 820px; margin: 0 auto; }
    header {
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.5rem;
      margin-bottom: 2rem;
    }
    h1 {
      font-size: 1.85rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.4rem;
    }
    .subtitle { color: var(--muted); font-size: 0.95rem; }
    h2 {
      font-size: 1.25rem;
      margin: 2rem 0 0.85rem;
      color: var(--accent);
      border-left: 3px solid var(--accent);
      padding-left: 0.65rem;
    }
    p, li { color: var(--text); margin-bottom: 0.6rem; }
    ul, ol { padding-left: 1.4rem; margin-bottom: 1rem; }
    a { color: #60a5fa; text-decoration: none; }
    a:hover { text-decoration: underline; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0 1.5rem;
      font-size: 0.92rem;
      background: var(--card);
      border-radius: 8px;
      overflow: hidden;
    }
    th, td {
      padding: 0.65rem 0.9rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }
    th { background: #243044; color: #cbd5e1; font-weight: 600; }
    tr:last-child td { border-bottom: none; }
    code, pre {
      font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
      font-size: 0.85rem;
    }
    code {
      background: #243044;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      color: #e2e8f0;
    }
    pre {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.15rem;
      overflow-x: auto;
      margin: 0.8rem 0 1.4rem;
      color: #d1d9e6;
    }
    .badge {
      display: inline-block;
      background: #1e3a5f;
      color: #93c5fd;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      margin-right: 0.35rem;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.15rem 1.25rem;
      margin: 1rem 0;
    }
    .highlight { color: var(--ok); font-weight: 600; }
    .warn { color: #fbbf24; }
    footer {
      margin-top: 3rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.85rem;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Curva de Lorenz e Índice de Gini</h1>
      <p class="subtitle">
        Proyecto Final — Cálculo II<br />
        Universidad Mariano Gálvez de Guatemala · Ingeniería en Sistemas de Información
      </p>
      <p style="margin-top:0.8rem">
        <span class="badge">Python</span>
        <span class="badge">SymPy</span>
        <span class="badge">Matplotlib</span>
        <span class="badge">SciPy</span>
      </p>
    </header>

    <p>
      Programa de <strong>verificación analítica y generación de gráficas</strong>
      para dos sectores de distribución del ingreso modelados con curvas de Lorenz.
    </p>

    <table>
      <thead>
        <tr><th>Sector</th><th>Función de Lorenz</th></tr>
      </thead>
      <tbody>
        <tr><td><strong>A</strong></td><td><code>L₁(x) = 0.7x² + 0.3x³</code></td></tr>
        <tr><td><strong>B</strong></td><td><code>L₂(x) = (15/16)x⁴ + (1/16)x</code></td></tr>
      </tbody>
    </table>

    <h2>Resultados principales</h2>
    <table>
      <thead>
        <tr>
          <th>Concepto</th>
          <th>Sector A</th>
          <th>Sector B</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Área de equidad A</td>
          <td>23/120 ≈ 0.1917</td>
          <td>9/32 = 0.2813</td>
        </tr>
        <tr>
          <td>Índice de Gini G = 2A</td>
          <td>23/60 ≈ 0.3833</td>
          <td>9/16 = 0.5625</td>
        </tr>
        <tr>
          <td>Más desigual</td>
          <td>—</td>
          <td class="highlight">Sector B</td>
        </tr>
      </tbody>
    </table>
    <p>Diferencia: <code>G<sub>B</sub> − G<sub>A</sub> ≈ 0.1792</code></p>

    <h2>Requisitos</h2>
    <ul>
      <li>Python 3.10 o superior</li>
      <li>Librerías: <code>sympy</code>, <code>numpy</code>, <code>matplotlib</code>, <code>scipy</code></li>
    </ul>

    <h2>Instalación y ejecución</h2>
    <div class="card">
      <p><strong>Entorno virtual (recomendado)</strong></p>
<pre># Crear y activar (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias DENTRO del venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Ejecutar
.\.venv\Scripts\python.exe lorenz_gini.py</pre>
      <p class="warn" style="font-size:0.9rem;margin-top:0.5rem">
        Si pip instala fuera del venv (“Defaulting to user installation…”), usa siempre
        <code>.\.venv\Scripts\python.exe -m pip ...</code>
      </p>
    </div>

    <div class="card">
      <p><strong>Sin entorno virtual</strong></p>
<pre>pip install -r requirements.txt
python lorenz_gini.py</pre>
    </div>

    <div class="card">
      <p><strong>Google Colab</strong></p>
<pre>!pip install sympy numpy matplotlib scipy
!python lorenz_gini.py</pre>
    </div>

    <h2>Qué hace el programa</h2>
    <ol>
      <li>Define <code>L₁</code> y <code>L₂</code> con fracciones exactas (<code>sympy.Rational</code>).</li>
      <li>Verifica propiedades de Lorenz: L(0)=0, L(1)=1, creciente, convexa y L(x) ≤ x.</li>
      <li>Calcula el área de equidad paso a paso:
        <br /><code>A = ∫₀¹ [x − L(x)] dx</code>
      </li>
      <li>Obtiene el Índice de Gini <code>G = 2A</code> (exacto y decimal).</li>
      <li>Verifica con <code>scipy.quad</code> y sumas de Riemann (n = 10, 100, 1000, 10000).</li>
      <li>Genera tabla de percentiles (ingreso del x% más pobre y del (1−x)% más rico).</li>
      <li>Produce 6 gráficas PNG a 300 dpi.</li>
      <li>Escribe un reporte de texto con el resumen completo.</li>
    </ol>
    <p>El desarrollo analítico se muestra en consola; el programa <strong>no sustituye</strong> el trabajo a mano.</p>

    <h2>Archivos generados (<code>salida/</code>)</h2>
    <table>
      <thead>
        <tr><th>Archivo</th><th>Descripción</th></tr>
      </thead>
      <tbody>
        <tr><td><code>fig1_sector_A.png</code></td><td>Curva de Lorenz Sector A + área</td></tr>
        <tr><td><code>fig2_sector_B.png</code></td><td>Curva de Lorenz Sector B + área</td></tr>
        <tr><td><code>fig3_comparativa.png</code></td><td>Ambas curvas superpuestas</td></tr>
        <tr><td><code>fig4_brecha.png</code></td><td>Brecha x − L(x) por cuantil</td></tr>
        <tr><td><code>fig5_percentiles.png</code></td><td>Barras 50% más pobre / 10% más rico</td></tr>
        <tr><td><code>fig6_riemann.png</code></td><td>Convergencia suma de Riemann</td></tr>
        <tr><td><code>tabla_percentiles.csv</code></td><td>Percentiles 10% – 100%</td></tr>
        <tr><td><code>resultados.txt</code></td><td>Resumen textual completo</td></tr>
      </tbody>
    </table>

    <h2>Verificación en GeoGebra</h2>
<pre>L1(x) = 0.7x^2 + 0.3x^3
L2(x) = (15/16)x^4 + (1/16)x
f(x) = x
Integral(f - L1, 0, 1)
Integral(f - L2, 0, 1)</pre>

    <h2>Estructura del repositorio</h2>
<pre>.
├── lorenz_gini.py
├── requirements.txt
├── README.md
└── salida/          ← se crea al ejecutar
    ├── fig1_sector_A.png … fig6_riemann.png
    ├── tabla_percentiles.csv
    └── resultados.txt</pre>

    <h2>Referencias</h2>
    <ul>
      <li>Stewart, J. <em>Cálculo</em>. Capítulo 6.1.</li>
      <li>Documentación de SymPy, NumPy, Matplotlib y SciPy.</li>
    </ul>

    <footer>
      Uso académico — Proyecto Final de Cálculo II<br />
      Universidad Mariano Gálvez de Guatemala
    </footer>
  </div>
</body>
</html>
