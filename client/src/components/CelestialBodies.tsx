export interface CelestialBodiesProps {
    astroData: { [key: string]: number[][] };
    bodiesInImage: { [key: string]: number[][] };
    refImageSize: number[];
}

function CelestialBodies({ astroData, bodiesInImage, refImageSize }: CelestialBodiesProps) {
    console.log('ref image size inside of celestialbodies: ', refImageSize)
    const frameDuration = 1; // seconds per frame
    const totalFrames = 16;
    const totalDuration = frameDuration * totalFrames;
    const screenDims = [3840, 2160];
    const scaleFactor: number = screenDims[0] / refImageSize[0];
    
    return (
        <svg width={screenDims[0]} height={screenDims[1]} viewBox={`0 0 ${screenDims[0]} ${screenDims[1]}`} className="celestial-bodies">
            {Object.entries(bodiesInImage).map(([bodyName, [visibleArr, xArr, yArr]], index) => {
                if (visibleArr.every(val => val === 0)) return null;
                
                const pathId = `motionPath-${index}`;
                const scaledX = xArr.map(x => x * scaleFactor);
                const scaledY = yArr.map(y => y * scaleFactor);
                const pathD = scaledX.map((x, i) => {
                    const y = scaledY[i];
                    return i === 0 ? `M ${x},${y}` : `L ${x},${y}`;
                }).join(' ');

                return (
                    <g key={bodyName}>
                        {/* Motion path in global coords */}
                        <path id={pathId} d={pathD} fill="none" stroke="none" />

                        {/* Body */}
                        <circle r="5" fill="white">
                            <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                                <mpath href={`#${pathId}`} />
                            </animateMotion>

                        {/* Animate visibility via opacity if needed */}
                            <animate
                                attributeName="opacity"
                                values={visibleArr.join(';')}
                                dur={`${totalDuration}s`}
                                repeatCount="indefinite"
                                />
                        </circle>

                        {/* Label */}
                        <text fill="white" fontSize="24" textAnchor="middle">
                            <textPath href={`#${pathId}`} startOffset="50%">
                                {bodyName}
                            </textPath>
                            <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                                <mpath href={`#${pathId}`} />
                            </animateMotion>
                        </text>
                    </g>
                );
            })}
        </svg>
    );
}

export default CelestialBodies;
