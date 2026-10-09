/** Formatea una fecha ISO como tiempo relativo corto ("hace 22 min", "hace 3 h"). */
export function haceTiempo(fechaIso: string): string {
  const minutos = Math.max(0, Math.round((Date.now() - new Date(fechaIso).getTime()) / 60000));

  if (minutos < 1) return "hace instantes";
  if (minutos < 60) return `hace ${minutos} min`;

  const horas = Math.round(minutos / 60);
  if (horas < 24) return `hace ${horas} h`;

  const dias = Math.round(horas / 24);
  return `hace ${dias} d`;
}
