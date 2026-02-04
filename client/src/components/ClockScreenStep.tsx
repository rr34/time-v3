import { useEffect, useRef, useState } from "react";
import { moonSVGPath } from "../utils/functions";
import { BodiesDict, awimTag } from "../types/interfaces";
import ClockScreenFrame from "./ClockScreenFrame";
import { bodyStyleMap, getSkyColorFromArtifae, radiusFromMagnitude } from "./clockScreenUtils";

interface ClockScreenStepProps {
  MomentsArray: string[];
  imageSrc: string;
  awimtag: awimTag;
  astroData: BodiesDict;
  bodiesInImage: BodiesDict;
  MagRankAllMax: number;
  onAnimationComplete?: () => void;
  RepeatLimit: number;
  frameDuration: number;
  GSTitle?: string;
}

function ClockScreenStep({ MomentsArray, imageSrc, awimtag, astroData, bodiesInImage, MagRankAllMax, onAnimationComplete, RepeatLimit, frameDuration, GSTitle }: ClockScreenStepProps) {
  const totalFrames = MomentsArray.length;
  const [frameIndex, setFrameIndex] = useState(0);
  const repeatCount = useRef(0);

  useEffect(() => {
    if (totalFrames === 0) return;

    const interval = setInterval(() => {
      setFrameIndex((prev) => {
        const next = (prev + 1) % totalFrames;
        if (next === 0) {
          repeatCount.current += 1;
          if (repeatCount.current >= RepeatLimit && onAnimationComplete) {
            onAnimationComplete();
          }
        }
        return next;
      });
    }, frameDuration * 1000);

    return () => clearInterval(interval);
  }, [frameDuration, totalFrames, RepeatLimit, onAnimationComplete]);

  const [refWidth, refHeight] = awimtag["awim Ref Image Size in Pixels"];
  const sunArtifaesArr: number[] = astroData?.sun?.artifaes || [];
  const skyColorIndex = Math.min(frameIndex, Math.max(0, sunArtifaesArr.length - 1));
  const skyColor = sunArtifaesArr.length ? getSkyColorFromArtifae(sunArtifaesArr[skyColorIndex]) : "black";
  const phaseAnglesArr: number[] = bodiesInImage?.moon?.phaseangles || [];
  const brightSideDirectionsArr: number[] = bodiesInImage?.moon?.brightsidedirections || [];

  return (
    <ClockScreenFrame refWidth={refWidth} refHeight={refHeight} imageSrc={imageSrc} MomentsArray={MomentsArray} frameIndex={frameIndex} GSTitle={GSTitle}>
      {astroData && bodiesInImage && (
        <svg key={imageSrc} className="celestial-overlay" viewBox={`0 0 ${refWidth} ${refHeight}`} preserveAspectRatio="xMidYMid meet">
          <rect x="0" y="0" width={refWidth} height={refHeight} fill={skyColor} />
          {Object.entries(bodiesInImage).map(([bodyName, bodyData]) => {
            const xArr: number[] | undefined = bodyData["pixelpos x"];
            const yArr: number[] | undefined = bodyData["pixelpos y"];
            if (!xArr || !yArr || xArr.length !== yArr.length) return null;

            const x = xArr[frameIndex];
            const y = yArr[frameIndex];
            if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
            if (x < 0 || x > refWidth || y < 0 || y > refHeight) return null;

            const type = (bodyData["type"] || "").toLowerCase();
            const nameKey = bodyName.toLowerCase();
            const baseStyle = bodyStyleMap[nameKey] || bodyStyleMap[type] || { fill: "white", radius: 3 };

            let radius = baseStyle.radius;
            let effectiveFill = baseStyle.fill;
            if (type === "star") {
              const visualMag = bodyData["VisualMagnitude"] !== undefined ? bodyData["VisualMagnitude"] : 6;
              radius = radiusFromMagnitude(visualMag);

              const rank = Number(bodyData["MagRankAll"]);
              if (!Number.isFinite(rank)) {
                effectiveFill = "gray";
              } else if (rank > MagRankAllMax) {
                effectiveFill = "lightblue";
              }
            }

            const fill = effectiveFill;
            const stroke = baseStyle.stroke || "none";
            const isMoon = nameKey === "moon";

            if (isMoon) {
              const phaseAngleSingle: number = phaseAnglesArr[frameIndex] || 90;
              const brightSideDirectionSingle: number = brightSideDirectionsArr[frameIndex] || 0;
              const moonSVG = moonSVGPath(phaseAngleSingle, bodyStyleMap.moon.radius);

              return (
                <g key={bodyName} transform={`translate(${x}, ${y})`}>
                  <path d={moonSVG} fill={fill} transform={`rotate(${-brightSideDirectionSingle})`} stroke={stroke} />
                  <g transform="translate(0, -120)">
                    {bodyData["ReadableName"] && (
                      <text fill="rgba(255, 255, 255, 0.3)" fontSize="140" textAnchor="middle" dominantBaseline="middle">
                        {bodyData["ReadableName"]?.trim()}
                      </text>
                    )}
                  </g>
                </g>
              );
            }

            return (
              <g key={bodyName} transform={`translate(${x}, ${y})`}>
                <circle r={radius} fill={fill} stroke={stroke} />
                <g transform="translate(0, -90)">
                  {bodyData["ReadableName"] && (
                    <text fill="rgba(255, 255, 255, 0.3)" fontSize="140" textAnchor="middle" dominantBaseline="middle">
                      {(bodyData["MagRankAll"] !== undefined && Number(bodyData["MagRankAll"]) <= 20)
                        ? `${bodyData["MagRankAll"]}. ${bodyData["ReadableName"]?.trim()}`
                        : bodyData["ReadableName"]?.trim()}
                    </text>
                  )}
                  {bodyData["MagRankConstellation"] === 1 && bodyData["ConstellationFullName"] && (
                    <text fill="rgba(173, 216, 230, 0.3)" fontSize="140" textAnchor="middle" dominantBaseline="middle" transform="translate(0, 180)">
                      {"\u03b1"} {bodyData["ConstellationFullName"]}
                    </text>
                  )}
                </g>
              </g>
            );
          })}
        </svg>
      )}
    </ClockScreenFrame>
  );
}

export default ClockScreenStep;
export type { ClockScreenStepProps };
