export function radiusFromMagnitude(mag: number): number {
  const minMag = -1.46; // Brightest star (Sirius).
  const maxMag = 5.17; // Limiting magnitude for display.
  const minRadius = 3;
  const maxRadius = 20;
  const magRange = maxMag - minMag;
  const radRange = maxRadius - minRadius;

  const radius = maxRadius - (mag - minMag) * radRange / magRange;
  const clampedRad = Math.min(Math.max(radius, minRadius), maxRadius);

  return clampedRad;
}

export function getSkyColorFromArtifae(angle: number): string {
  if (angle < -18) return "#000000"; // deep night
  if (angle < -12) return "#00051b"; // astronomical twilight
  if (angle < -6) return "#01266c"; // nautical twilight
  if (angle < 0) return "#1e1e6e"; // civil twilight
  if (angle < 6) return "#46148c"; // sunrise/sunset
  return "#000fda"; // day
}

export const bodyStyleMap: { [key: string]: { fill: string; radius: number; stroke?: string } } = {
  sun: { fill: "yellow", radius: 80 },
  moon: { fill: "#e8e8e8", radius: 80 },
  mercury: { fill: "#b0b0b0", radius: 25 },
  venus: { fill: "#e6c07b", radius: 25 },
  mars: { fill: "#d95f02", radius: 25 },
  jupiter: { fill: "#c49c94", radius: 25 },
  saturn: { fill: "#deb887", radius: 25 },
  uranus: { fill: "#76d7ea", radius: 25 },
  neptune: { fill: "#4169e1", radius: 25 },
};
