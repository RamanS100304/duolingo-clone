// Hand-drawn SVG icons (original artwork): top-bar stats, sidebar navigation, path chests and trophies.
type P = { size?: number; grey?: boolean };

export const Flame = ({ size = 26, grey }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="streak">
    <path d="M12.5 1.5c.6 3.2 5.5 5.6 5.5 11a6 6 0 0 1-12 0c0-2.4 1.1-3.9 2.3-5 .1 1.8.9 2.9 2 3.3C9.4 7.4 10 4 12.5 1.5z" fill={grey ? "#afafaf" : "#ff9600"} />
    <path d="M12 12c.4 1.5 2.8 2.4 2.8 4.8a2.8 2.8 0 0 1-5.6 0c0-1.5.8-2.3 1.6-3 .2 1 .6 1.4 1.100 1.500-.1-1.100 0-2.300.1-3.300z" fill={grey ? "#cfcfcf" : "#ffc800"} />
  </svg>
);

export const Gem = ({ size = 26 }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="gems" style={{ flex: "none" }}>
    <path d="M6 3h12l4 6-10 13L2 9z" fill="#1cb0f6" />
    <path d="M6 3l-4 6h20l-4-6z" fill="#84d8ff" />
    <path d="M9 9l3 13 3-13z" fill="#1899d6" />
  </svg>
);

export const Heart = ({ size = 26, grey }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="hearts">
    <path d="M12 21.5C5 16.300 2 12.800 2 8.800 2 6 4.200 4 6.800 4c2 0 3.600 1.100 5.200 3.100C13.600 5.100 15.200 4 17.200 4 19.800 4 22 6 22 8.800c0 4-3 7.500-10 12.700z" fill={grey ? "#afafaf" : "#ff4b4b"} />
    <path d="M6.500 7.200c-1 .3-1.700 1.200-1.700 2.300" stroke="#fff" strokeOpacity=".5" strokeWidth="1.600" strokeLinecap="round" fill="none" />
  </svg>
);

export const Bolt = ({ size = 26 }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-label="xp">
    <path d="M13.500 1 4 14h6.500L9.500 23 20 9.500h-6.500z" fill="#ffc800" stroke="#e5a800" strokeWidth="1" strokeLinejoin="round" />
  </svg>
);

/** Course flag for English: a simplified striped flag. */
export const Flag = ({ size = 34 }: P) => (
  <svg width={size} height={size * 0.75} viewBox="0 0 32 24" aria-label="English course" style={{ borderRadius: 6, display: "block" }}>
    <rect width="32" height="24" fill="#fff" />
    {[0, 2, 4, 6, 8, 10, 12].map((i) => <rect key={i} y={i * 24 / 13} width="32" height={24 / 13} fill="#ff4b4b" />)}
    <rect width="14" height={24 * 7 / 13} fill="#1cb0f6" />
    {[[3, 3], [7, 3], [11, 3], [5, 6.5], [9, 6.5], [3, 10], [7, 10], [11, 10]].map(([x, y]) => <circle key={`${x}-${y}`} cx={x} cy={y} r="0.9" fill="#fff" />)}
  </svg>
);

/* ------------------------------------------------------------ navigation */
export const NavLearn = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <path d="M4 15 16 4l12 11v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z" fill="#ff9600" />
    <path d="M2.500 15.500 16 3.500l13.500 12" stroke="#ff4b4b" strokeWidth="3.500" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    <rect x="12.500" y="19" width="7" height="11" rx="1.500" fill="#ffc800" />
  </svg>
);

export const NavPractice = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <rect x="3" y="10" width="6" height="12" rx="2" fill="#1cb0f6" />
    <rect x="23" y="10" width="6" height="12" rx="2" fill="#1cb0f6" />
    <rect x="0.500" y="13" width="3.500" height="6" rx="1.500" fill="#1899d6" />
    <rect x="28" y="13" width="3.500" height="6" rx="1.500" fill="#1899d6" />
    <rect x="9" y="14" width="14" height="4" rx="2" fill="#afafaf" />
  </svg>
);

export const NavLeaderboard = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <path d="M6 4h20v10a10 10 0 0 1-20 0z" fill="#ffc800" />
    <path d="M6 7H2v3a6 6 0 0 0 5 6M26 7h4v3a6 6 0 0 1-5 6" stroke="#e5a800" strokeWidth="2.500" fill="none" />
    <rect x="13" y="23" width="6" height="4" fill="#e5a800" />
    <rect x="9" y="27" width="14" height="3.500" rx="1.500" fill="#ff9600" />
    <path d="M12 9h8" stroke="#fff" strokeWidth="2" strokeLinecap="round" opacity=".6" />
  </svg>
);

export const NavQuests = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <rect x="3" y="12" width="26" height="16" rx="3" fill="#ff9600" />
    <path d="M3 13a6 6 0 0 1 6-6h14a6 6 0 0 1 6 6v3H3z" fill="#ffc800" />
    <rect x="13" y="13" width="6" height="7" rx="1.500" fill="#fff" />
    <rect x="14.700" y="16" width="2.600" height="2.500" rx="1" fill="#e5a800" />
  </svg>
);

export const NavShop = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <rect x="4" y="13" width="24" height="16" rx="2" fill="#ce82ff" />
    <path d="M3 8l3-5h20l3 5v3a3.500 3.500 0 0 1-6.500 1.800A3.500 3.500 0 0 1 16 12.800a3.500 3.500 0 0 1-6.500 0A3.500 3.500 0 0 1 3 11z" fill="#ff4b4b" />
    <rect x="12" y="19" width="8" height="10" rx="1.500" fill="#a560d8" />
  </svg>
);

export const NavProfile = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <circle cx="16" cy="16" r="14" fill="#ddf4ff" stroke="#84d8ff" strokeWidth="2" />
    <circle cx="16" cy="13" r="5" fill="#1cb0f6" />
    <path d="M7 25.500a10 7 0 0 1 18 0" fill="#1cb0f6" />
  </svg>
);

export const NavMore = ({ size = 32 }: P) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <circle cx="16" cy="16" r="14" fill="#ce82ff" />
    {[9, 16, 23].map((x) => <circle key={x} cx={x} cy="16" r="2.600" fill="#fff" />)}
  </svg>
);

/* ------------------------------------------------------------- path nodes */
export const ChestIcon = ({ size = 64, grey, open }: P & { open?: boolean }) => {
  const body = grey ? "#d0d0d0" : "#ff9600", lid = grey ? "#e5e5e5" : "#ffc800", trim = grey ? "#b7b7b7" : "#cc6f00";
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden>
      <rect x="8" y="28" width="48" height="28" rx="5" fill={body} />
      {open
        ? <path d="M10 26 14 8h36l4 18z" fill={lid} opacity=".9" />
        : <path d="M8 30a12 12 0 0 1 12-12h24a12 12 0 0 1 12 12v4H8z" fill={lid} />}
      <rect x="8" y="34" width="48" height="4" fill={trim} opacity=".5" />
      <rect x="27" y="30" width="10" height="13" rx="2.500" fill="#fff" />
      <rect x="30" y="35" width="4" height="4" rx="1.500" fill={trim} />
    </svg>
  );
};

export const TrophyIcon = ({ size = 64, grey }: P) => {
  const cup = grey ? "#d0d0d0" : "#ffc800", dark = grey ? "#b7b7b7" : "#e5a800";
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden>
      <path d="M14 8h36v16a18 18 0 0 1-36 0z" fill={cup} />
      <path d="M14 13H5v5a11 11 0 0 0 11 11M50 13h9v5a11 11 0 0 1-11 11" stroke={dark} strokeWidth="4" fill="none" />
      <rect x="27" y="40" width="10" height="9" fill={dark} />
      <rect x="18" y="49" width="28" height="8" rx="3" fill={dark} />
      <path d="M32 16l2.400 4.800 5.300.8-3.800 3.700.9 5.300-4.800-2.500-4.800 2.500.9-5.300-3.800-3.700 5.300-.8z" fill="#fff" opacity=".85" />
    </svg>
  );
};
