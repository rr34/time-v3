function msToTime(duration: number, include_seconds = true) {
    let seconds = Math.floor((duration / 1000) % 60),
      minutes = Math.floor((duration / (1000 * 60)) % 60),
      hours = Math.floor((duration / (1000 * 60 * 60)) % 24),
      days = Math.floor(duration / (1000 * 60 * 60 * 24));
  
    let hours_str = hours.toString(),
    minutes_str = (minutes < 10) ? "0" + minutes : minutes.toString();
    if (include_seconds) {
        var seconds_str = (seconds < 10) ? ":0" + seconds : ":" + seconds.toString();
    }
    else {
        var seconds_str = "";
    }
    if (days >= 1) {
        var days_str = days + " days, ";
    }
    else {
        var days_str = "";
    }
  
    return days_str + hours_str + ":" + minutes_str + seconds_str;
  }


export function UpdateClockStrings(SunDaily: Date[], SunIndex: number, MoonDaily: Date[], setSunIndex: Function, setCurrentTime: Function, setSunEventsString: Function, setMoonPhaseString: Function, setMoonEventString: Function, setIndustrialDTString: Function) {
    console.log('ran update clock strings function')
    let newdate = new Date();
    let addhours = -96;
    newdate = new Date(newdate.getTime() + addhours*1000*60*60);
    setCurrentTime(newdate);
    let options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'US/Eastern',
        timeZoneName: 'shortOffset',
    };
    setIndustrialDTString(new Intl.DateTimeFormat("en-GB", options).format(newdate) + ' industrial time');

    setSunIndex(SunDaily.findIndex((date, i) => newdate < date));
    if (SunIndex === 4 || SunIndex === 8) {
        let since_ms = newdate.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - newdate.getTime();
        setSunEventsString(msToTime(since_ms) + " since midnight. " + msToTime(until_ms) + " until sunrise.")
    }
    else if (SunIndex === 5 || SunIndex === 9) {
        let since_ms = newdate.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - newdate.getTime();
        setSunEventsString(msToTime(since_ms) + " since sunrise. " + msToTime(until_ms) + " until high noon.")
    }
    else if (SunIndex === 6) {
        let since_ms = newdate.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - newdate.getTime();
        setSunEventsString(msToTime(since_ms) + " since high noon. " + msToTime(until_ms) + " until sunset.")
    }
    else if (SunIndex === 7) {
        let since_ms = newdate.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - newdate.getTime();
        setSunEventsString(msToTime(since_ms) + " since sunset. " + msToTime(until_ms) + " until midnight.")
    }
    
    setMoonPhaseString('successs, set moon phase string');
    
    let moon_index = MoonDaily.findIndex((date, i) => newdate < date);
    if (moon_index === 2 || moon_index === 4) {
        let since_ms = newdate.getTime() - MoonDaily[moon_index - 1].getTime();
        let until_ms = MoonDaily[moon_index].getTime() - newdate.getTime();
        setMoonEventString(msToTime(since_ms) + " since moonset. " + msToTime(until_ms) + " until moonrise.")
    }
    else if (moon_index === 3 || moon_index === 5) {
        let since_ms = newdate.getTime() - MoonDaily[moon_index - 1].getTime();
        let until_ms = MoonDaily[moon_index].getTime() - newdate.getTime();
        setMoonEventString(msToTime(since_ms) + " since moonrise. " + msToTime(until_ms) + " until moonset.")
    }
}

export function UpdateDayNightLengthString(SunDaily: Date[], SunIndex: number, setDayNightLengthsString: Function) {
    console.log('ran update day night length strings function')
    // I want to change the day length at midnight and change the night length at noon so the length refers to the same day / night as the sunrise / sunset in the sun events string.
    if (SunIndex === 4 || SunIndex === 5) { // until noon
        let day_ms = SunDaily[6].getTime() - SunDaily[4].getTime();
        let night_ms = SunDaily[4].getTime() - SunDaily[2].getTime();
        setDayNightLengthsString(msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.")
    }
    else if (SunIndex === 6 || SunIndex === 7) { // change the night length after noon
        let day_ms = SunDaily[6].getTime() - SunDaily[4].getTime();
        let night_ms = SunDaily[8].getTime() - SunDaily[6].getTime();
        setDayNightLengthsString(msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.")
    }
    else if (SunIndex === 8 || SunIndex === 9) { // change the day length after midnight
        let day_ms = SunDaily[10].getTime() - SunDaily[8].getTime();
        let night_ms = SunDaily[8].getTime() - SunDaily[6].getTime();
        setDayNightLengthsString(msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.")
    }
}