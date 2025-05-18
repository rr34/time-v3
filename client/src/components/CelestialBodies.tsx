export interface CelestialBodiesProps {
    astroData: { [key: string]: number[][] };
    bodiesInImage: { [key: string]: number[][] };
}

function CelestialBodies({ astroData, bodiesInImage }: CelestialBodiesProps) {
    const frameDuration = 1; // seconds per frame
    const totalFrames = 16;
    const totalDuration = frameDuration * totalFrames;

    return (
        <svg width="3840" height="2160" viewBox="0 0 3840 2160" className="celestial-bodies">
            {Object.entries(bodiesInImage).map(([bodyName, [visibleArr, xArr, yArr]], index) => {
                // Skip if all visibility values are 0
                if (visibleArr.every(val => val === 0)) return null; // not necessary because the API wouldn't give us the array if visible were all zeros.

                // Generate path data from x/y arrays
                const pathId = `motionPath-${index}`;
                const pathD = xArr.map((x, i) => {
                    const y = yArr[i];
                    return i === 0 ? `M ${x},${y}` : `L ${x},${y}`;
                }).join(' ');

                return (
                    <g key={bodyName}>
                        {/* Define the path for motion */}
                        <path id={pathId} d={pathD} fill="none" stroke="none" />

                        {/* Moving circle */}
                        <circle r="5" fill="white" stroke="black" strokeWidth="1">
                            <animateMotion dur={`${totalDuration}s`} repeatCount="indefinite">
                                <mpath href={`#${pathId}`} />
                            </animateMotion>
                            {/* Optional: animate opacity to match visibility (basic frame-to-frame toggle) */}
                            <animate
                                attributeName="opacity"
                                values={visibleArr.join(';')}
                                dur={`${totalDuration}s`}
                                repeatCount="indefinite"
                            />
                        </circle>

                        {/* Label following the body */}
                        <text fill="white" fontSize="24" textAnchor="middle">
                            <textPath href={`#${pathId}`} startOffset="0%">
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
