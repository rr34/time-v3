import { useState, useEffect } from "react";

export function useIntervalTimestamp(intervalMs: number) {
  const [nowMs, setNowMs] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => {
      setNowMs(Date.now());
    }, intervalMs);

    return () => clearInterval(timer);
  }, [intervalMs]);

  return nowMs;
}


export function msToTime(timeperiod: number, include_seconds = true, include_plussign = false) {
    const isNegative = timeperiod < 0;
    const absTime = Math.abs(timeperiod);

    const seconds = Math.floor((absTime / 1000) % 60),
        minutes = Math.floor((absTime / (1000 * 60)) % 60),
        hours = Math.floor((absTime / (1000 * 60 * 60)) % 24),
        days = Math.floor(absTime / (1000 * 60 * 60 * 24));

    let days_str = "";
    if (days === 1) {
        days_str = "1 day, ";
    } else if (days > 1) {
        days_str = `${days} days, `;
    }

    const hours_str = hours.toString() + ":";
    const minutes_str = minutes < 10 ? "0" + minutes : minutes.toString();
    let seconds_str = "";

    if (include_seconds) {
        seconds_str = seconds < 10 ? ":0" + seconds : ":" + seconds;
    }

    const result = days_str + hours_str + minutes_str + seconds_str;
    return isNegative ? "-" + result : include_plussign ? "+" + result : result;
}


export function moonSVGPath(phaseAngle: number, moonRadius: number) {
    // Radius of ellipse drawn for day/night demarcation line. Zero at 90° because when the radius is zero it's a line.
    const ry = moonRadius * Math.cos(phaseAngle * Math.PI/ 180);

    // Sweep flag for second arc. Negative ry values in the SVG would work, but unfortunately are treated same as positive, so this flag needs to change.
    // Greater than zero when phase angle less than 90°, means gibbous. Less than zero when phase angle greater than 90°, means crescent.
    const sweepDirection = ry > 0 ? 1 : 0;

    const svgPath: string = `M 50 0 A 50 50 0 0 1 -50 0 A 50 ${ry} 0 0 ${sweepDirection} 50 0`;

    return svgPath;
}


