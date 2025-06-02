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
