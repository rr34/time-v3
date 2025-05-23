import { useEffect, useState } from "react";

function radiusFromMagnitude(mag: number): number {
  const minMag = -1.46;
  const maxMag = 4;
  const minRadius = 3;
  const maxRadius = 20;
  const magRange = maxMag - minMag;
  const radRange = maxRadius - minRadius;

  const radius = maxRadius - (mag - minMag) * radRange / magRange;
  const clampedRad = Math.min(Math.max(radius, minRadius), maxRadius);

  return clampedRad;
}

interface ClockScreenProps {
  NowMoments: string[];
}

function ClockScreen({ NowMoments }: ClockScreenProps) {
  const [imageSrc, setImageSrc] = useState<string>("");
  const [AWIMdata, setAWIMdata] = useState<any>(null);
  const [astroData, setAstroData] = useState<{ [key: string]: number[][] } | null>(null);
  const [bodiesInImage, setBodiesInImage] = useState<{ [key: string]: any } | null>(null);
  const [refImageSize, setRefImageSize] = useState<[number, number] | null>(null);

  const frameDuration = 2;
  const totalFrames = NowMoments.length;
  const totalDuration = frameDuration * totalFrames;

  const bodyStyleMap: { [key: string]: { fill: string; radius: number; stroke?: string } } = {
    sun: { fill: "yellow", radius: 50 },
    moon: { fill: "white", radius: 50 },
    mercury: { fill: "#b0b0b0", radius: 20 },
    venus: { fill: "#e6c07b", radius: 20 },
    mars: { fill: "#d95f02", radius: 20 },
    jupiter: { fill: "#c49c94", radius: 20 },
    saturn: { fill: "#deb887", radius: 20 },
    uranus: { fill: "#76d7ea", radius: 20 },
    neptune: { fill: "#4169e1", radius: 20 },
  };

  useEffect(() => {
    const fetchImageAndAWIMdata = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/clockimage`);
        const data = await response.json();
        const imageUrl = `${import.meta.env.VITE_FRONTEND_URL}${data.imageUrl}`;

        setImageSrc(imageUrl);
        setAWIMdata(data.metadata);

        const refSize = data.metadata['awim Ref Image Size in Pixels'];
        if (Array.isArray(refSize) && refSize.length === 2) {
          setRefImageSize([refSize[0], refSize[1]]);
        } else {
          console.error("Invalid ref image size format.");
        }
      } catch (error) {
        console.error("Error fetching image or metadata:", error);
      }
    };

    fetchImageAndAWIMdata();
  }, []);

  useEffect(() => {
    const fetchCelestialData = async () => {
      if (!AWIMdata) return;

      try {
        const response = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphoto`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awim: AWIMdata,
            momentsarray: NowMoments,
            requestlist: ["stars", "sun", "moon", "planets"],
            returnastro: "true",
          }),
        });

        const data = await response.json();
        setAstroData(data["astro dict"]);
        setBodiesInImage(data["bodies in image dict"]);
      } catch (error) {
        console.error("Error fetching celestial data:", error);
      }
    };

    fetchCelestialData();
  }, [AWIMdata, NowMoments]);

  if (!refImageSize) return <p>Loading image and metadata...</p>;

  const [refWidth, refHeight] = refImageSize;

  return (
    <div
      className="aspect-container"
      style={{
        aspectRatio: `${refWidth} / ${refHeight}`,
      }}
    >
      {imageSrc && (
        <img src={imageSrc} className="clock-image" alt="Clock" />
      )}

      {astroData && bodiesInImage && (
        <svg
          className="celestial-overlay"
          viewBox={`0 0 ${refWidth} ${refHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {Object.entries(bodiesInImage).map(([bodyName, bodyData], index) => {
            console.log("bodyData:", bodyData);
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
                  <g transform="translate(0, -20)">
                    <text
                      fill="white"
                      fontSize="24"
                      textAnchor="middle"
                      dominantBaseline="middle"
                    >
                      {bodyData['ReadableName']?.trim() || bodyName}
                    </text>
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
    </div>
  );
}

export default ClockScreen;
