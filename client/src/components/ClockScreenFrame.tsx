import { ReactNode } from "react";
import { formatIndustrialDate, msToTime, useIntervalTimestamp } from "../utils/functions";

interface ClockScreenFrameProps {
  refWidth: number;
  refHeight: number;
  imageSrc: string;
  MomentsArray: string[];
  frameIndex: number;
  GSTitle?: string;
  children?: ReactNode;
}

function ClockScreenFrame({ refWidth, refHeight, imageSrc, MomentsArray, frameIndex, GSTitle, children }: ClockScreenFrameProps) {
  const nowFast = useIntervalTimestamp(100); // update every tenth of second
  const nowMinute = useIntervalTimestamp(60 * 1000); // update every minute
  const frameTimestampMs = MomentsArray[frameIndex] ? Date.parse(MomentsArray[frameIndex]) : Number.NaN;
  const frameDateLabel = Number.isFinite(frameTimestampMs) ? formatIndustrialDate(frameTimestampMs, false) : "Unknown date";
  const gsTitleText = GSTitle?.trim();

  return (
    <div className="aspect-container" style={{ aspectRatio: `${refWidth} / ${refHeight}` }}>
      {children}

      {imageSrc && (
        <img src={imageSrc} className="clock-image" alt="Clock" />
      )}
      <div style={{ position: "absolute", bottom: 10, left: 10, color: "white", fontSize: "12px", backgroundColor: "rgba(0, 0, 0, 0.4)", padding: "6px 10px", borderRadius: "6px" }}>
        <div>
          {(() => {
            const beginning_relative = Date.parse(MomentsArray[0]) - nowMinute;
            const end_relative = Date.parse(MomentsArray[MomentsArray.length - 1]) - nowMinute;
            return "Showing time period " + msToTime(beginning_relative, false) + " to +" + msToTime(end_relative, false);
          })()}
        </div>
        <div>
          {"Lapse progress: now " + (frameTimestampMs - nowFast < 0 ? "-" : "+") + msToTime(Math.abs(frameTimestampMs - nowFast), false)}
        </div>
        <div>
          {imageSrc}
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 12, left: "50%", transform: "translateX(-50%)", color: "white", fontSize: "30px", backgroundColor: "rgba(0, 0, 0, 0.5)", padding: "6px 14px", borderRadius: "8px", letterSpacing: "0.02em", textAlign: "center" }}>
        {gsTitleText && <div>{gsTitleText}</div>}
        <div>{frameDateLabel}</div>
      </div>
    </div>
  );
}

export default ClockScreenFrame;
