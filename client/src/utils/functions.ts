export function msToTime(timeperiod: number, include_seconds = true) {
    const seconds = Math.floor((timeperiod / 1000) % 60),
        minutes = Math.floor((timeperiod / (1000 * 60)) % 60),
        hours = Math.floor((timeperiod / (1000 * 60 * 60)) % 24),
        days = Math.floor(timeperiod / (1000 * 60 * 60 * 24));

    let days_str = "";
    if (days > 1) {
        days_str = days.toString() + " days, ";
    }
    else if (days == 1) {
        days_str = days.toString() + " day, ";
    }
    else {
        days_str = "";
    }
    const hours_str = hours.toString() + ":",
    minutes_str = (minutes < 10) ? "0" + minutes.toString() : minutes.toString()
    let seconds_str = "";
    if (include_seconds) {
        seconds_str = (seconds < 10) ? ":0" + seconds.toString() : ":" + seconds.toString();
    }
  
    return days_str + hours_str + minutes_str + seconds_str;
}


export function moonSVGPath(phaseAngle: number, moonRadius: number) {
    // Radius of ellipse drawn for day/night demarcation line. Zero at 90° because when the radius is zero it's a line.
    const ry = moonRadius * Math.cos(phaseAngle * Math.PI/ 180);

    // Sweep flag for second arc. Negative ry values in the SVG would work, but unfortunately are treated same as positive, so this flag needs to change.
    // Greater than zero when phase angle less than 90°, means gibbous. Less than zero when phase angle greater than 90°, means crescent.
    const sweepDirection = ry > 0 ? 1 : 0;

    const svgPath: string = `M 50 0 A 50 50 0 0 1 -50 0 A 50 ${ry} 0 0 ${sweepDirection} 50 0`;

    console.log(`for phase angle ${phaseAngle}, the svg path is ${svgPath}`)

    return svgPath;
}
