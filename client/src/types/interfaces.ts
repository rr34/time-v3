export interface BodyData {
  // Required
  'type': 'sun' | 'moon' | 'planet' | 'star';

  // Optional astro metadata (mostly stars)
  'ReadableName'?: string;
  'RA'?: number;
  'Declination'?: number;
  'Distance'?: number;
  'VisualMagnitude'?: number;
  'MagRankAll'?: number;
  'ConstellationFullName'?: string;
  'MagRankConstellation'?: number;
  'GreekLetter'?: string;

  // Optional calculation arrays (appear only if body is in image)
  'azimuths'?: number[];
  'artifaes'?: number[];
  'xangs'?: number[];
  'yangs'?: number[];
  'dirs'?: number[];
  'arcs'?: number[];
  'pixelpos x'?: number[];
  'pixelpos y'?: number[];

  // Moon-specific optional fields
  'phaseangles'?: number[];
  'brightsidedirections'?: number[];
}


export type BodiesDict = Record<string, BodyData>;


export interface awimTag {
  "awim Version": string;
  "awim Location Coordinates": number[]; // [lat, lon]
  "awim Location Coordinates Unit": string;
  "awim Location Coordinates Source": string;
  "awim Location MSL": number;
  "awim Location MSL Unit": string;
  "awim Location MSL Source": string;
  "awim Location Terrain Elevation": number;
  "awim Location Terrain Elevation Unit": string;
  "awim Location Terrain Elevation Source": string;
  "awim Location AGL": number;
  "awim Location AGL Unit": string;
  "awim Location AGL Description": string;
  "awim Location AGL Source": string;
  "awim Capture Moment": string; // ISO 8601
  "awim Capture Moment Unit": string;
  "awim Capture Moment Source": string;
  "awim Models Type": string;
  "awim Ref Pixel": number[];
  "awim Ref Pixel Coord Type": string;
  "awim Ref Tilt": number;
  "awim Ref Tilt Unit": string;
  "awim Ref Image Size in Pixels": number[];
  "awim Ref Image Size in Pixels Note": string;
  "awim Angles Models Features": string[];
  "awim Angles Model xang_coeffs": number[];
  "awim Angles Model yang_coeffs": number[];
  "awim Pixels Model Features": string[];
  "awim Pixels Model xpx_coeffs": number[];
  "awim Pixels Model ypx_coeffs": number[];
  "awim Ref Pixel Azimuth Artifae": number[];
  "awim Ref Pixel Azimuth Artifae Source": string;
  "awim Ref Pixel Azimuth Artifae Unit": string;
  "awim Grid Pixels": number[][]; // adjust type if known
  "awim Grid Angles": number[][];
  "awim Grid Angles Unit": string;
  "awim Grid Direction and Arc": number[][];
  "awim Grid Direction and Arc Unit": string;
  "awim Grid Azimuth Artifae": number[][];
  "awim Grid RA Dec": number[][];
  "awim RA Dec Unit": string;
  "awim Grid Pixel Sizes": number[][];
  "awim Pixel Size Unit": string;
  "awim Image Field of View Fraction": number;
  "awim Image Field of View Fraction Unit": string;
}


export type ImagesSet = {
  [basename: string]: {
    awimTag: awimTag;
  };
};
