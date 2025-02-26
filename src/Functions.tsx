function msToTime(duration) {
    let seconds = Math.floor((duration / 1000) % 60),
      minutes = Math.floor((duration / (1000 * 60)) % 60),
      hours = Math.floor((duration / (1000 * 60 * 60)) % 24),
      days = Math.floor(duration / (1000 * 60 * 60 * 24));
  
    let hours_str = hours,
    minutes_str = (minutes < 10) ? "0" + minutes : minutes,
    seconds_str = (seconds < 10) ? "0" + seconds : seconds;
    if (days >= 1) {
        var days_str = days + " days, ";
    }
    else {
        var days_str = "";
    }
  
    return days_str + hours_str + ":" + minutes_str + ":" + seconds_str;
  }
  console.log(msToTime(300000))

export default function UpdateClockStrings(SunDaily: Date[], setCurrentTime: Function, setSunEventsString: Function, setDayNightLengthsString: Function, setMoonPhaseString: Function, setMoonEventString: Function, setDateString: Function, setIndustrialTimeString: Function) {
    let newdate: Date = new Date();
    setCurrentTime(newdate);
    
    let nowIndex: number = SunDaily.findIndex((date, i) => newdate < date);
    console.log(nowIndex);
    if (nowIndex === 4) {
        let since_ms = newdate.getTime() - SunDaily[nowIndex - 1].getTime();
        let until_ms = SunDaily[nowIndex].getTime() - newdate.getTime();
        setSunEventsString(msToTime(since_ms) + " since midnight. " + msToTime(until_ms) + " until sunrise.")
    }


    // if any(i == sun_just_passed_event for i in (0, 1, 2)):
    //     sun_string = '%i:%.2i since sunrise. %i:%.2i until high noon.' % sun_times_tuple
    // elif any(i == sun_just_passed_event for i in (3, 4, 5)):
    //     sun_string = '%i:%.2i since high noon. %i:%.2i until sunset.' % sun_times_tuple
    // elif any(i == sun_just_passed_event for i in (6, 7, 8)):
    //     sun_string = '%i:%.2i since sunset. %i:%.2i until midnight.' % sun_times_tuple
    // elif any(i == sun_just_passed_event for i in (9, 10, 11)):
    //     sun_string = '%i:%.2i since midnight. %i:%.2i until sunrise.' % sun_times_tuple

    setDayNightLengthsString('successs, set string');
    setMoonPhaseString('successs, set string');
    setMoonEventString('successs, set string');
    setDateString('successs, set string');
    setIndustrialTimeString('successs, set string');
}