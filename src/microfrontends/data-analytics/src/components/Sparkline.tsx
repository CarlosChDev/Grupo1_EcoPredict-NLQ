interface SparklineProps {
  valores: (number | null)[];
  /** Fecha `YYYY-MM-DD` de cada valor, para el tooltip. */
  etiquetas: string[];
  limite: number;
  color: string;
  unidad: string;
}

const W = 240;
const H = 38;

/** Rachas de índices consecutivos con dato — un día sin dato corta la línea. */
function tramos(valores: (number | null)[]): number[][] {
  const resultado: number[][] = [];
  let actual: number[] = [];
  valores.forEach((v, i) => {
    if (v === null) {
      if (actual.length) resultado.push(actual);
      actual = [];
    } else actual.push(i);
  });
  if (actual.length) resultado.push(actual);
  return resultado;
}

/**
 * Serie diaria con la línea del límite ECA de 24 h y un punto rojo en cada
 * día que lo excedió. Los puntos son líneas de largo cero con
 * `non-scaling-stroke` para que sigan siendo círculos aunque el SVG se estire.
 */
export function Sparkline({ valores, etiquetas, limite, color, unidad }: SparklineProps) {
  const conDato = valores.filter((v): v is number => v !== null);
  const max = Math.max(limite * 1.1, ...conDato);
  const n = valores.length;
  const X = (i: number) => (n < 2 ? W / 2 : (i / (n - 1)) * W);
  const Y = (v: number) => H - 2 - (v / max) * (H - 4);

  return (
    <svg className="da-spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img"
      aria-label={`Serie diaria; ${conDato.filter((v) => v > limite).length} días sobre el límite de ${limite} ${unidad}`}>
      <line x1={0} x2={W} y1={Y(limite)} y2={Y(limite)} className="da-spark-eca" vectorEffect="non-scaling-stroke" />
      {tramos(valores).map((t) => {
        const puntos = t.map((i) => `${X(i).toFixed(1)},${Y(valores[i]!).toFixed(1)}`).join(" ");
        if (t.length === 1) {
          const [i] = t;
          return (
            <line key={i} x1={X(i)} x2={X(i)} y1={Y(valores[i]!)} y2={Y(valores[i]!)} stroke={color}
              strokeWidth={4} strokeLinecap="round" vectorEffect="non-scaling-stroke" />
          );
        }
        return (
          <g key={t[0]}>
            <polygon points={`${X(t[0])},${H} ${puntos} ${X(t[t.length - 1])},${H}`} fill={color} fillOpacity={0.12} />
            <polyline points={puntos} fill="none" stroke={color} strokeWidth={1.8} strokeLinejoin="round"
              vectorEffect="non-scaling-stroke" />
          </g>
        );
      })}
      {valores.map((v, i) =>
        v !== null && v > limite ? (
          <line key={`x${i}`} x1={X(i)} x2={X(i)} y1={Y(v)} y2={Y(v)} className="da-spark-exc"
            vectorEffect="non-scaling-stroke" />
        ) : null,
      )}
      {valores.map((v, i) => (
        <rect key={`h${i}`} x={X(i) - W / n / 2} y={0} width={W / n} height={H} fill="transparent">
          <title>{`${etiquetas[i]} · ${v === null ? "sin dato" : `${v.toLocaleString("es-PE")} ${unidad}`}`}</title>
        </rect>
      ))}
    </svg>
  );
}
