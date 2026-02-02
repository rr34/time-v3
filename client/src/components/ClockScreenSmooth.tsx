import { useEffect, useRef, useState } from "react";
import { moonSVGPath } from "../utils/functions";
import { BodiesDict, awimTag } from "../types/interfaces";
import ClockScreenFrame from "./ClockScreenFrame";
import { bodyStyleMap, getSkyColorFromArtifae, radiusFromMagnitude } from "./clockScreenUtils";

interface ClockScreenSmoothProps {
  MomentsArray: string[];
  imageSrc: string; // can the whole image itself be passed in here, not just the src url?
  awimtag: awimTag;
  astroData: BodiesDict;
  bodiesInImage: BodiesDict;
  MagRankAllMax: number;
  onAnimationComplete?: () => void;
  RepeatLimit: number;
  frameDuration: number;
}

function ClockScreenSmooth({ MomentsArray, imageSrc, awimtag, astroData, bodiesInImage, MagRankAllMax, onAnimationComplete, RepeatLimit, frameDuration }: ClockScreenSmoothProps) {
  const totalFrames = MomentsArray.length;
  const totalDuration = frameDuration * totalFrames;

  const animateRef = useRef<SVGAnimateElement | null>(null);
  const repeatCount = useRef(0);

  useEffect(() => {
    const anim = animateRef.current;
    if (!anim) return;

    const handleRepeat = () => {
      repeatCount.current += 1;
      if (repeatCount.current >= RepeatLimit && onAnimationComplete) {
        onAnimationComplete();
      }
    };

    anim.addEventListener("repeatEvent", handleRepeat);
    return () => anim.removeEventListener("repeatEvent", handleRepeat);
  }, [onAnimationComplete, RepeatLimit]);

  const [frameIndex, setFrameIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % totalFrames);
    }, frameDuration * 1000);

    return () => clearInterval(interval);
  }, [frameDuration, totalFrames]);

  const [refWidth, refHeight] = awimtag["awim Ref Image Size in Pixels"]; // unless the awimtag was broken, this will always be type number[] with two numbers in it
  const sunArtifaesArr: number[] = astroData?.sun?.artifaes || [];
  const skyColorValues = sunArtifaesArr.map(getSkyColorFromArtifae).join(";");
  const phaseAnglesArr: number[] = bodiesInImage?.moon?.phaseangles || [];
  const brightSideDirectionsArr: number[] = bodiesInImage?.moon?.brightsidedirections || [];

  return (
    <ClockScreenFrame refWidth={refWidth} refHeight={refHeight} imageSrc={imageSrc} MomentsArray={MomentsArray} frameIndex={frameIndex}>
      {astroData && bodiesInImage && (
        <svg key={imageSrc} className="celestial-overlay" viewBox={`0 0 ${refWidth} ${refHeight}`} preserveAspectRatio="xMidYMid meet">
          <rect x="0" y="0" width={refWidth} height={refHeight} fill={sunArtifaesArr.length ? getSkyColorFromArtifae(sunArtifaesArr[0]) : "black"}>
            <animate ref={animateRef} attributeName="fill" values={skyColorValues} dur={`${totalDuration}s`} repeatCount="indefinite" calcMode="linear" begin="0s" />
          </rect>
          {Object.entries(bodiesInImage).map(([bodyName, bodyData], index) => {
            const xArr: number[] | undefined = bodyData["pixelpos x"];
            const yArr: number[] | undefined = bodyData["pixelpos y"];
            if (!xArr || !yArr || xArr.length !== yArr.length) return null;
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
            const visibleArr = xArr.map((x, i) => {
              const y = yArr[i];
              return (x >= 0 && x <= refWidth && y >= 0 && y <= refHeight) ? 1 : 0;
            });

            if (visibleArr.every(v => v === 0)) return null;

            const pathId = `motionPath-${index}`;
            const pathD = xArr.map((x, i) => {
              const y = yArr[i];
              return i === 0 ? `M ${x},${y}` : `L ${x},${y}`;
            }).join(" ");

            const isMoon = nameKey === "moon";

            if (isMoon) {
              const middleValue = Math.floor(phaseAnglesArr.length / 2);
              const phaseAngleSingle: number = phaseAnglesArr[middleValue] || 90;
              const brightSideDirectionSingle: number = brightSideDirectionsArr[middleValue] || 0;
              const moonSVG = moonSVGPath(phaseAngleSingle, bodyStyleMap.moon.radius);

              return (
                <g key={bodyName}>
                  <path id={pathId} d={pathD} fill="none" stroke="none" />

                  {/* Moon path with rotation */}
                  <path d={moonSVG} fill={fill} transform={`rotate(${-brightSideDirectionSingle})`} stroke={stroke}>
                    <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                      <mpath href={`#${pathId}`} />
                    </animateMotion>
                    <animate attributeName="opacity" values={visibleArr.join(";")} dur={`${totalDuration}s`} repeatCount="indefinite" calcMode="discrete" />
                  </path>

                  {/* Labels and text */}
                  <g>
                    <g transform="translate(0, -120)">
                      {bodyData["ReadableName"] && (
                        <text fill="rgba(255, 255, 255, 0.3)" fontSize="140" textAnchor="middle" dominantBaseline="middle">
                          {bodyData["ReadableName"]?.trim()}
                        </text>
                      )}
                    </g>
                    <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite" rotate="auto">
                      <mpath href={`#${pathId}`} />
                    </animateMotion>
                  </g>
                </g>
              );
            }

            return (
              <g key={bodyName}>
                <path id={pathId} d={pathD} fill="none" stroke="none" />
                <circle r={radius} fill={fill} stroke={stroke}
                >
                  <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                    <mpath href={`#${pathId}`} />
                  </animateMotion>
                  <animate attributeName="opacity" values={visibleArr.join(";")} dur={`${totalDuration}s`} repeatCount="indefinite" calcMode="discrete" />
                </circle>
                <g>
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
                  <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite" rotate="auto">
                    <mpath href={`#${pathId}`} />
                  </animateMotion>
                </g>
              </g>
            );
          })}
        </svg>
      )}
    </ClockScreenFrame>
  );
}

export default ClockScreenSmooth;
export type { ClockScreenSmoothProps };
