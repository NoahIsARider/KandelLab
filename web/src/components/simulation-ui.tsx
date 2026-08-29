'use client';

import { useState, useCallback } from 'react';

interface ParamFieldProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
}

export function ParamField({ label, value, onChange, unit, min, max, step = 0.1 }: ParamFieldProps) {
  return (
    <div className="flex items-center gap-3 mb-2">
      <label className="text-sm text-[var(--ink)] font-[var(--font-display)] min-w-[120px]">
        {label}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 h-1 accent-[var(--ochre)]"
      />
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="param-input"
        step={step}
      />
      {unit && <span className="text-xs text-[var(--ink-light)] font-mono">{unit}</span>}
    </div>
  );
}

interface RunSimulationProps {
  onRun: () => void;
  running?: boolean;
  label?: string;
}

export function RunButton({ onRun, running, label = '运行仿真' }: RunSimulationProps) {
  return (
    <button
      onClick={onRun}
      disabled={running}
      className="run-button"
    >
      {running ? '运算中...' : label}
    </button>
  );
}

/** CSS-only bar chart component */
interface BarChartProps {
  data: { label: string; value: number; color?: string }[];
  maxValue?: number;
  height?: number;
}

export function BarChart({ data, maxValue, height = 16 }: BarChartProps) {
  const max = maxValue || Math.max(...data.map(d => Math.abs(d.value)), 1);

  return (
    <div className="css-bar-chart">
      {data.map((d, i) => (
        <div key={i} className="css-bar-row">
          <span className="css-bar-label">{d.label}</span>
          <div className="css-bar-track" style={{ height: `${height}px` }}>
            <div
              className="css-bar-fill"
              style={{
                width: `${(Math.abs(d.value) / max) * 100}%`,
                background: d.color || 'var(--oxide)',
              }}
            />
          </div>
          <span className="css-bar-value">{d.value.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

/** CSS-only heatmap component */
interface HeatMapProps {
  data: number[][];
  minVal?: number;
  maxVal?: number;
  colorScheme?: 'sepia' | 'diverging';
}

export function HeatMap({ data, minVal, maxVal, colorScheme = 'sepia' }: HeatMapProps) {
  const min = minVal ?? Math.min(...data.flat());
  const max = maxVal ?? Math.max(...data.flat());
  const range = max - min || 1;

  const getColor = (value: number): string => {
    const normalized = (value - min) / range;
    if (colorScheme === 'diverging') {
      if (normalized < 0.5) {
        const t = normalized * 2;
        const r = Math.round(45 + t * (245 - 45));
        const g = Math.round(27 + t * (230 - 27));
        const b = Math.round(31 + t * (200 - 31));
        return `rgb(${r},${g},${b})`;
      } else {
        const t = (normalized - 0.5) * 2;
        const r = Math.round(245 + t * (107 - 245));
        const g = Math.round(230 + t * (58 - 230));
        const b = Math.round(200 + t * (42 - 200));
        return `rgb(${r},${g},${b})`;
      }
    }
    // Sepia scheme
    const r = Math.round(245 - normalized * 138);
    const g = Math.round(230 - normalized * 172);
    const b = Math.round(200 - normalized * 158);
    return `rgb(${r},${g},${b})`;
  };

  return (
    <div
      className="css-heatmap"
      style={{
        gridTemplateColumns: `repeat(${data[0]?.length || 1}, 1fr)`,
      }}
    >
      {data.map((row, i) =>
        row.map((val, j) => (
          <div
            key={`${i}-${j}`}
            className="css-heatmap-cell"
            style={{ backgroundColor: getColor(val) }}
            title={`[${i},${j}]: ${val.toFixed(3)}`}
          />
        ))
      )}
    </div>
  );
}

/** Data table component */
interface DataTableProps {
  headers: string[];
  rows: (string | number)[][];
}

export function DataTable({ headers, rows }: DataTableProps) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          {headers.map((h, i) => (
            <th key={i}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => (
              <td key={j}>{typeof cell === 'number' ? cell.toFixed(4) : cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/** Formula display component */
export function FormulaBlock({ children }: { children: React.ReactNode }) {
  return (
    <div className="formula-block">
      {children}
    </div>
  );
}

/** Section divider */
export function OrnamentDivider({ symbol = '❧ ※ ❧' }: { symbol?: string }) {
  return <div className="ornament-divider">{symbol}</div>;
}

/** Chapter heading */
export function ChapterHeading({ children }: { children: React.ReactNode }) {
  return <h2 className="chapter-heading">{children}</h2>;
}

/** Section heading */
export function SectionHeading({ children }: { children: React.ReactNode }) {
  return <h3 className="section-heading">{children}</h3>;
}

/** Result card */
export function ResultCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border border-[var(--border-old)] p-4 my-4 bg-[rgba(239,224,198,0.3)]">
      <h4 className="font-[var(--font-display)] text-sm font-semibold text-[var(--ochre)] uppercase tracking-wider mb-3">
        {title}
      </h4>
      {children}
    </div>
  );
}

/** Waveform display using CSS bars (no SVG/JS drawing) */
interface WaveformProps {
  data: number[];
  height?: number;
  color?: string;
  label?: string;
}

export function Waveform({ data, height = 80, color = 'var(--oxide)', label }: WaveformProps) {
  const max = Math.max(...data.map(Math.abs), 0.001);
  const step = Math.max(1, Math.floor(data.length / 200)); // limit bars to 200
  const sampled = data.filter((_, i) => i % step === 0);

  return (
    <div className="my-3">
      {label && <p className="text-xs text-[var(--ink-light)] mb-1 font-mono">{label}</p>}
      <div className="flex items-end gap-px border border-[var(--border-old)] p-1 bg-[rgba(250,243,230,0.5)]" style={{ height: `${height}px` }}>
        {sampled.map((val, i) => {
          const h = Math.max(1, (Math.abs(val) / max) * (height - 4));
          const isNeg = val < 0;
          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: `${h}px`,
                background: color,
                opacity: 0.7,
                alignSelf: isNeg ? 'flex-start' : 'flex-end',
                minWidth: '1px',
              }}
            />
          );
        })}
      </div>
    </div>
  );
}

/** Text-based scatter plot using a grid of characters */
interface ScatterProps {
  points: { x: number; y: number }[];
  width?: number;
  height?: number;
  xLabel?: string;
  yLabel?: string;
}

export function TextScatter({ points, width = 40, height = 15, xLabel, yLabel }: ScatterProps) {
  const grid: string[][] = Array.from({ length: height }, () => Array(width).fill(' '));

  const xMin = Math.min(...points.map(p => p.x));
  const xMax = Math.max(...points.map(p => p.x));
  const yMin = Math.min(...points.map(p => p.y));
  const yMax = Math.max(...points.map(p => p.y));
  const xRange = xMax - xMin || 1;
  const yRange = yMax - yMin || 1;

  for (const p of points) {
    const col = Math.min(width - 1, Math.max(0, Math.floor(((p.x - xMin) / xRange) * (width - 1))));
    const row = Math.min(height - 1, Math.max(0, Math.floor((1 - (p.y - yMin) / yRange) * (height - 1))));
    grid[row][col] = '◆';
  }

  return (
    <div className="my-3 font-mono text-xs leading-tight">
      {yLabel && (
        <div className="text-[var(--ink-light)] text-left mb-1">{yLabel} ↑</div>
      )}
      <div className="border border-[var(--border-old)] p-2 bg-[rgba(250,243,230,0.5)] overflow-x-auto">
        {grid.map((row, i) => (
          <div key={i} className="whitespace-pre">
            {row.join('')}
          </div>
        ))}
        <div className="text-[var(--ink-light)] text-right">→ {xLabel || 'x'}</div>
      </div>
    </div>
  );
}
