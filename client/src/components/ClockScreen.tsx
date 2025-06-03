import { useEffect, useRef, useState } from "react";
import { msToTime } from "../utils/functions";
import { BodiesDict, awimTag } from "../types/interfaces";

function radiusFromMagnitude(mag: number): number {
  const minMag = -1.46;
  const maxMag = 5.17; // AKA limiting magnitude. This should come from the minimum visibility being shown, but currently this comes from the 2000th brightest star.
  const minRadius = 3;
  const maxRadius = 20;
  const magRange = maxMag - minMag;
  const radRange = maxRadius - minRadius;

  const radius = maxRadius - (mag - minMag) * radRange / magRange;
  const clampedRad = Math.min(Math.max(radius, minRadius), maxRadius);

  return clampedRad;
}

function getSkyColorFromArtifae(angle: number): string {
  if (angle < -18) return "#000000"; // deep night
  if (angle < -12) return "#00051b"; // astronomical twilight
  if (angle < -6)  return "#01266c"; // nautical twilight
  if (angle < 0)   return "#1e1e6e"; // civil twilight
  if (angle < 6)  return "#46148c"; // sunrise/sunset
  return "#000fda"; // day
}

  const skyColorMap: { [key: string]: string } = {
    night: "#",
    AT: "#",
    NT: "#",
    CT: "#",
    transition: "#",
    evening: "#3214af",
    day: "#",
  };


interface ClockScreenProps {
  imageSrc: string; // can the whole image itself be passed in here, not just the src url?
  awimtag: awimTag;
  astroData: BodiesDict;
  bodiesInImage: BodiesDict;
  MomentsArray: string[];
  nowMS: number;
  onAnimationComplete?: () => void;
}

function ClockScreen({ imageSrc, awimtag, astroData, bodiesInImage, MomentsArray, nowMS, onAnimationComplete }: ClockScreenProps) {
  const frameDuration = 0.75;
  const totalFrames = MomentsArray.length;
  const totalDuration = frameDuration * totalFrames;

  const animationRef = useRef<SVGAnimateElement | null>(null);
  const repeatCount = useRef(0);

  useEffect(() => {
    const anim = animationRef.current;
    if (!anim) return;

    const handleRepeat = () => {
      repeatCount.current += 1;
      if (repeatCount.current === 2 && onAnimationComplete) {
        onAnimationComplete();
      }
    };

    anim.addEventListener("repeatEvent", handleRepeat);
    return () => anim.removeEventListener("repeatEvent", handleRepeat);
  }, [onAnimationComplete]);

  const [frameIndex, setFrameIndex] = useState(0);

useEffect(() => {
  const interval = setInterval(() => {
    setFrameIndex((prev) => (prev + 1) % totalFrames);
  }, frameDuration * 1000);

  return () => clearInterval(interval);
}, [frameDuration, totalFrames]);
  
  const momentsMS = Date.parse(MomentsArray[frameIndex])

  const bodyStyleMap: { [key: string]: { fill: string; radius: number; stroke?: string } } = {
    sun: { fill: "yellow", radius: 50 },
    moon: { fill: "#e8e8e8", radius: 50 },
    mercury: { fill: "#b0b0b0", radius: 20 },
    venus: { fill: "#e6c07b", radius: 20 },
    mars: { fill: "#d95f02", radius: 20 },
    jupiter: { fill: "#c49c94", radius: 20 },
    saturn: { fill: "#deb887", radius: 20 },
    uranus: { fill: "#76d7ea", radius: 20 },
    neptune: { fill: "#4169e1", radius: 20 },
  };

  if (!awimtag) return <p>Loading image, awimtag, astrodata, bodiesInImage data...</p>;

  const refDims = awimtag['awim Ref Image Size in Pixels']; // unless the awimtag was broken, this will always be type number[] with two numbers in it
  const [refWidth, refHeight] = refDims;

  const artifaeArr: number[] = astroData?.sun?.artifaes || [];
  const skyColorValues = artifaeArr.map(getSkyColorFromArtifae).join(";");

  return (
    <div
      className="aspect-container"
      style={{
        aspectRatio: `${refWidth} / ${refHeight}`,
      }}
    >
      {astroData && bodiesInImage && (
        <svg
          className="celestial-overlay"
          viewBox={`0 0 ${refWidth} ${refHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          <rect x="0" y="0" width={refWidth} height={refHeight} fill={artifaeArr.length ? getSkyColorFromArtifae(artifaeArr[0]) : "black"}>
            <animate ref={animationRef} attributeName="fill" values={skyColorValues} dur={`${totalDuration}s`} repeatCount="indefinite" calcMode="linear"/>
          </rect>
          {Object.entries(bodiesInImage).map(([bodyName, bodyData], index) => {
            const xArr: number[] = bodyData['pixelpos x'];
            const yArr: number[] = bodyData['pixelpos y'];
            const type: string = (bodyData['type'] || "").toLowerCase();
            const nameKey = bodyName.toLowerCase();
            const baseStyle = bodyStyleMap[nameKey] || bodyStyleMap[type] || { fill: "white", radius: 3 };

            let radius = baseStyle.radius;
            if (type === "star") {
              const visualMag = bodyData['VisualMagnitude'] !== undefined
                ? parseFloat(bodyData['VisualMagnitude'])
                : 6;
              radius = radiusFromMagnitude(visualMag);
            }

            const fill = baseStyle.fill;
            const stroke = baseStyle.stroke || "none";

            const visibleArr = xArr.map((x, i) => {
              const y = yArr[i];
              return (x >= 0 && x <= refWidth && y >= 0 && y <= refHeight) ? 1 : 0;
            });

            if (visibleArr.every((v) => v === 0)) return null;

            const pathId = `motionPath-${index}`;
            const pathD = xArr.map((x, i) => {
              const y = yArr[i];
              return i === 0 ? `M ${x},${y}` : `L ${x},${y}`;
            }).join(" ");

            return (
              <g key={bodyName}>
                <path id={pathId} d={pathD} fill="none" stroke="none" />

                <circle r={radius} fill={fill} stroke={stroke}>
                  <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                    <mpath href={`#${pathId}`} />
                  </animateMotion>
                  <animate
                    attributeName="opacity"
                    values={visibleArr.join(";")}
                    dur={`${totalDuration}s`}
                    repeatCount="indefinite"
                    calcMode="discrete"
                  />
                </circle>

                <g>
                  <g transform="translate(0, -30)">
                    {bodyData['ReadableName'] && (<text fill="white" fontSize="30" textAnchor="middle" dominantBaseline="middle">
                      {bodyData['ReadableName']?.trim() || ''}
                    </text> )}
                    {bodyData['MagRankConstellation'] === 1 && bodyData['ConstellationFullName'] && (<text fill="lightblue" fontSize="30" textAnchor="middle" dominantBaseline="middle" transform="translate(0, 60)">
                    α {bodyData['ConstellationFullName']}
                    </text>
)}

                  </g>
                  <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite" rotate="auto">
                    <mpath href={`#${pathId}`} />
                  </animateMotion>
                </g>
              </g>
            );
          })}
        </svg>
      )}

      {imageSrc && (
        <img src={imageSrc} className="clock-image" alt="Clock" />
      )}
      <div
        style={{ position: "absolute", bottom: 10, left: 10, color: "white", fontSize: "20px", backgroundColor: "rgba(0, 0, 0, 0.4)", padding: "4px 8px", borderRadius: "6px",}}>
        {'Now ' + (Date.parse(MomentsArray[frameIndex]) - nowMS < 0 ? '-' : '+') + msToTime(Math.abs(Date.parse(MomentsArray[frameIndex]) - nowMS))}

      </div>
    </div>
  );
}

export default ClockScreen;
