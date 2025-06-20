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


export function moonSVGPath(phaseAngle: number) {
  // Clamp angle between 0 and 180
  const angle = Math.max(0, Math.min(180, phaseAngle));

  // Interpolate rx: 50 at full/new (0 or 180), 0 at quarter (90)
  const ry = (Math.abs(angle - 90) * (50 / 90)).toFixed(3);

  // Sweep flag for second arc
  const sweep = angle > 90 ? 0 : 1;

  const svgPath: string = `M 50 0 A 50 50 0 0 1 -50 0 A 50 ${ry} 0 0 ${sweep} 50 0`;

  console.log(`for phase angle ${phaseAngle}, the svg path is ${svgPath}`)

  return svgPath;
}

// normalized = Math.cos((angle * Math.PI) / 180); // -1 to 1 todo maybe use something like this to translate from the angle to the radius?