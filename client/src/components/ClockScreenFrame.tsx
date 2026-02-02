import { ReactNode } from "react";
import { msToTime, useIntervalTimestamp } from "../utils/functions";

interface ClockScreenFrameProps {
  refWidth: number;
  refHeight: number;
  imageSrc: string;
  MomentsArray: string[];
  frameIndex: number;
  children?: ReactNode;
}

function ClockScreenFrame({ refWidth, refHeight, imageSrc, MomentsArray, frameIndex, children }: ClockScreenFrameProps) {
  const nowFast = useIntervalTimestamp(100); // update every tenth of second
  const nowMinute = useIntervalTimestamp(60 * 1000); // update every minute

  return (
    <div className="aspect-container" style={{ aspectRatio: `${refWidth} / ${refHeight}` }}>
      {children}

      {imageSrc && (
        <img src={imageSrc} className="clock-image" alt="Clock" />
      )}
      <div style={{ position: "absolute", bottom: 10, left: 10, color: "white", fontSize: "5px", backgroundColor: "rgba(0, 0, 0, 0.4)", padding: "4px 8px", borderRadius: "6px" }}>
        <div>
          {(() => {
            const beginning_relative = Date.parse(MomentsArray[0]) - nowMinute;
            const end_relative = Date.parse(MomentsArray[MomentsArray.length - 1]) - nowMinute;
            return "Showing time period " + msToTime(beginning_relative, false) + " to +" + msToTime(end_relative, false);
          })()}
        </div>
        <div>
          {"Lapse progress: now " + (Date.parse(MomentsArray[frameIndex]) - nowFast < 0 ? "-" : "+") + msToTime(Math.abs(Date.parse(MomentsArray[frameIndex]) - nowFast), false)}
        </div>
        <div>
          {imageSrc}
        </div>
      </div>
    </div>
  );
}

export default ClockScreenFrame;
