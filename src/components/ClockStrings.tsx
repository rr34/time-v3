import { useEffect, useState } from "react";

function msToTime(duration: number, include_seconds = true) {
    let seconds = Math.floor((duration / 1000) % 60),
      minutes = Math.floor((duration / (1000 * 60)) % 60),
      hours = Math.floor((duration / (1000 * 60 * 60)) % 24),
      days = Math.floor(duration / (1000 * 60 * 60 * 24));
  
    if (days > 1) {
        var days_str = days.toString() + " days, ";
    }
    else if (days == 1) {
        var days_str = days.toString() + " day, ";
    }
    else {
        var days_str = "";
    }
    let hours_str = hours.toString() + ":",
    minutes_str = (minutes < 10) ? "0" + minutes.toString() : minutes.toString();
    if (include_seconds) {
        var seconds_str = (seconds < 10) ? ":0" + seconds.toString() : ":" + seconds.toString();
    }
    else {
        var seconds_str = "";
    }
  
    return days_str + hours_str + minutes_str + seconds_str;
}
interface ClockStringsProps {
    SunDaily: Date[];
    SunIndex: number;
    setSunIndex: Function;
    MoonDaily: Date[];
    NearestNew: Date;
    NearestNewAngle: number;
    NearestFull: Date;
    NearestFullAngle: number
  }

const ClockStrings: React.FC<ClockStringsProps> = ({ SunDaily, SunIndex, setSunIndex, MoonDaily, NearestNew, NearestNewAngle, NearestFull, NearestFullAngle}) => {
    const [CurrentTime, setCurrentTime] = useState(new Date());

    const [SunEventsString, setSunEventsString] = useState('current sun events');
    const [DayNightLengthsString, setDayNightLengthsString] = useState('day and night lengths');
    const [MoonPhaseString, setMoonPhaseString] = useState('moon phase string');
    const [MoonEventString, setMoonEventString] = useState('moon events');
    const [IndustrialDTString, setIndustrialDTString] = useState('industrial time');

    // update the clock strings every second
    useEffect(() => {
        const intervalID = setInterval(() => {
            let addhours = 0;
            let newdate = new Date(Date.now() + addhours*1000*60*60);
            setCurrentTime(newdate);
        }, 1*1000);

    return () => clearInterval(intervalID);
    });

    // industrial time string
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
    setIndustrialDTString('Industrial Time: ' + new Intl.DateTimeFormat("en-GB", options).format(CurrentTime));

    // sun events string
    setSunIndex(SunDaily.findIndex((date, i) => CurrentTime < date));
    if (SunIndex === 4 || SunIndex === 8) {
        let since_ms = CurrentTime.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - CurrentTime.getTime();
        setSunEventsString(msToTime(since_ms) + " since midnight. " + msToTime(until_ms) + " until sunrise.")
    }
    else if (SunIndex === 5 || SunIndex === 9) {
        let since_ms = CurrentTime.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - CurrentTime.getTime();
        setSunEventsString(msToTime(since_ms) + " since sunrise. " + msToTime(until_ms) + " until high noon.")
    }
    else if (SunIndex === 6) {
        let since_ms = CurrentTime.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - CurrentTime.getTime();
        setSunEventsString(msToTime(since_ms) + " since high noon. " + msToTime(until_ms) + " until sunset.")
    }
    else if (SunIndex === 7) {
        let since_ms = CurrentTime.getTime() - SunDaily[SunIndex - 1].getTime();
        let until_ms = SunDaily[SunIndex].getTime() - CurrentTime.getTime();
        setSunEventsString(msToTime(since_ms) + " since sunset. " + msToTime(until_ms) + " until midnight.")
    }

    // moon events string
    let moon_index = MoonDaily.findIndex((date, i) => CurrentTime < date);
    if (moon_index === 2 || moon_index === 4) {
        let since_ms = CurrentTime.getTime() - MoonDaily[moon_index - 1].getTime();
        let until_ms = MoonDaily[moon_index].getTime() - CurrentTime.getTime();
        setMoonEventString(msToTime(since_ms) + " since moonset. " + msToTime(until_ms) + " until moonrise.")
    }
    else if (moon_index === 3 || moon_index === 5) {
        let since_ms = CurrentTime.getTime() - MoonDaily[moon_index - 1].getTime();
        let until_ms = MoonDaily[moon_index].getTime() - CurrentTime.getTime();
        setMoonEventString(msToTime(since_ms) + " since moonrise. " + msToTime(until_ms) + " until moonset.")
    }

    // moon phase string
    let timedelta_new = CurrentTime.getTime() - NearestNew.getTime();
    let timedelta_full = CurrentTime.getTime() - NearestFull.getTime();
    if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) > 0) {
        let timedelta_str: string = msToTime(Math.abs(timedelta_new));
        let eclipse_string: string = (NearestNewAngle > 178.5) ? ' Phase angle greater than ~~178.5° means solar eclipse.' : '';
        setMoonPhaseString(timedelta_str + ' since new moon at ' + NearestNewAngle.toString() + '° phase angle.' + eclipse_string);
    }
    else if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) < 0) {
        let timedelta_str: string = msToTime(Math.abs(timedelta_new));
        let eclipse_string: string = (NearestNewAngle > 178.5) ? ' Phase angle greater than ~~178.5° means solar eclipse.' : '';
        setMoonPhaseString(timedelta_str + ' until new moon at ' + NearestNewAngle.toString() + '° phase angle.' + eclipse_string);
    }
    else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) > 0) {
        let timedelta_str: string = msToTime(Math.abs(timedelta_full));
        let eclipse_string: string = (NearestFullAngle < 1.5) ? ' Phase angle less than ~1.5° means lunar eclipse.' : '';
        setMoonPhaseString(timedelta_str + ' since full moon at ' + NearestFullAngle.toString() + '° phase angle.' + eclipse_string);
    }
    else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) < 0) {
        let timedelta_str: string = msToTime(Math.abs(timedelta_full));
        let eclipse_string: string = (NearestFullAngle < 1.5) ? ' Phase angle less than ~1.5° means lunar eclipse.' : '';
        setMoonPhaseString(timedelta_str + ' until full moon at ' + NearestFullAngle.toString() + '° phase angle.' + eclipse_string);
    }

    // day and night length string
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

    return (
        <div>
            <p>{ SunEventsString }<br></br>
            { DayNightLengthsString }<br></br>
            { MoonPhaseString }<br></br>
            { MoonEventString }<br></br>
            { IndustrialDTString }<br></br>
            { CurrentTime.toISOString() }</p>
        </div>
    )
};

export default ClockStrings;