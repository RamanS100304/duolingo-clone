export function Avatar({ name, color, size }: { name: string; color: string; size?: "xl" }) {
  return <div className={`avatar ${size ?? ""}`} style={{ background: color }}>{name.trim()[0]?.toUpperCase()}</div>;
}
