import { useEffect } from "react";
import { ClockTimeObj, DailyEventsObj } from "../App";

function msToTime(duration: number, include_seconds = true) {
    const seconds = Math.floor((duration / 1000) % 60),
        minutes = Math.floor((duration / (1000 * 60)) % 60),
        hours = Math.floor((duration / (1000 * 60 * 60)) % 24),
        days = Math.floor(duration / (1000 * 60 * 60 * 24));

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


interface ClockStringsProps {
    cto: ClockTimeObj;
    setcto: React.Dispatch<React.SetStateAction<{ currenttime: Date; sunindex: number }>>;
    deo: DailyEventsObj;
}


const ClockStrings: React.FC<ClockStringsProps> = ({ cto, setcto, deo }) => {
    // update the clock strings every second. todo: fix this because it causes the entire app to reload twice every second when it fires.
    useEffect(() => {
        const intervalID = setInterval(() => {
            const addhours = 0;
            const newdate = new Date(Date.now() + addhours*1000*60*60);
            const sunindex = deo.sundaily.findIndex((date, i) => newdate < date);
            setcto({ currenttime: newdate, sunindex: sunindex })
        }, 1*1000);

    return () => clearInterval(intervalID);
    });


    console.log("reloaded the clock strings") // todo: Why does this log twice every second when this component should be rendering a single time every second? Tried wrapping in React memo and tried making the time variables a single object so there's only one state variable updating at a time to trigger the rerender, but still rerenders twice for some reason.
    
    let suneventsstring = "sun events string";
    let daynightlengthstring = "day and night lengths string";
    let moonphasestring = "moon phase string";
    let mooneventstring = "moon events string";
    let industrialdtstring = "industrial datetime string";
    let comptime = "computer time";

    // sun events string
    if (cto.sunindex === 4 || cto.sunindex === 8) {
        const since_ms = cto.currenttime.getTime() - deo.sundaily[cto.sunindex - 1].getTime();
        const until_ms = deo.sundaily[cto.sunindex].getTime() - cto.currenttime.getTime();
        suneventsstring = msToTime(since_ms) + " since midnight. " + msToTime(until_ms) + " until sunrise.";
    }
    else if (cto.sunindex === 5 || cto.sunindex === 9) {
        const since_ms = cto.currenttime.getTime() - deo.sundaily[cto.sunindex - 1].getTime();
        const until_ms = deo.sundaily[cto.sunindex].getTime() - cto.currenttime.getTime();
        suneventsstring = msToTime(since_ms) + " since sunrise. " + msToTime(until_ms) + " until high noon.";
    }
    else if (cto.sunindex === 6) {
        const since_ms = cto.currenttime.getTime() - deo.sundaily[cto.sunindex - 1].getTime();
        const until_ms = deo.sundaily[cto.sunindex].getTime() - cto.currenttime.getTime();
        suneventsstring = msToTime(since_ms) + " since high noon. " + msToTime(until_ms) + " until sunset.";
    }
    else if (cto.sunindex === 7) {
        const since_ms = cto.currenttime.getTime() - deo.sundaily[cto.sunindex - 1].getTime();
        const until_ms = deo.sundaily[cto.sunindex].getTime() - cto.currenttime.getTime();
        suneventsstring = msToTime(since_ms) + " since sunset. " + msToTime(until_ms) + " until midnight.";
    }

    // moon events string
    const moon_index = deo.moondaily.findIndex((date, i) => cto.currenttime < date);
    if (moon_index === 2 || moon_index === 4) {
        const since_ms = cto.currenttime.getTime() - deo.moondaily[moon_index - 1].getTime();
        const until_ms = deo.moondaily[moon_index].getTime() - cto.currenttime.getTime();
        mooneventstring = msToTime(since_ms) + " since moonset. " + msToTime(until_ms) + " until moonrise.";
    }
    else if (moon_index === 3 || moon_index === 5) {
        const since_ms = cto.currenttime.getTime() - deo.moondaily[moon_index - 1].getTime();
        const until_ms = deo.moondaily[moon_index].getTime() - cto.currenttime.getTime();
        mooneventstring = msToTime(since_ms) + " since moonrise. " + msToTime(until_ms) + " until moonset.";
    }

    // moon phase string
    const timedelta_new = cto.currenttime.getTime() - deo.nearestnew.getTime();
    const timedelta_full = cto.currenttime.getTime() - deo.nearestfull.getTime();
    if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) > 0) {
        const timedelta_str: string = msToTime(Math.abs(timedelta_new));
        const eclipse_string: string = (deo.nearestnewangle > 178.5) ? ' > ~~178.5° means solar eclipse.' : '';
        moonphasestring = timedelta_str + ' since new moon at ' + deo.nearestnewangle.toString() + '° phase angle.' + eclipse_string;
    }
    else if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) < 0) {
        const timedelta_str: string = msToTime(Math.abs(timedelta_new));
        const eclipse_string: string = (deo.nearestnewangle > 178.5) ? ' > than ~~178.5° means solar eclipse.' : '';
        moonphasestring = timedelta_str + ' until new moon at ' + deo.nearestnewangle.toString() + '° phase angle.' + eclipse_string;
    }
    else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) > 0) {
        const timedelta_str: string = msToTime(Math.abs(timedelta_full));
        const eclipse_string: string = (deo.nearestfullangle < 1.5) ? ' < ~1.5° means lunar eclipse.' : '';
        moonphasestring = timedelta_str + ' since full moon at ' + deo.nearestfullangle.toString() + '° phase angle.' + eclipse_string;
    }
    else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) < 0) {
        const timedelta_str: string = msToTime(Math.abs(timedelta_full));
        const eclipse_string: string = (deo.nearestfullangle < 1.5) ? ' < ~1.5° means lunar eclipse.' : '';
        moonphasestring = timedelta_str + ' until full moon at ' + deo.nearestfullangle.toString() + '° phase angle.' + eclipse_string;
    }

    // day and night length string. todo: only update when sunindex changes
    if (cto.sunindex === 4 || cto.sunindex === 5) { // until noon
        const day_ms = deo.sundaily[6].getTime() - deo.sundaily[4].getTime();
        const night_ms = deo.sundaily[4].getTime() - deo.sundaily[2].getTime();
        daynightlengthstring = msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.";
    }
    else if (cto.sunindex === 6 || cto.sunindex === 7) { // change the night length after noon
        const day_ms = deo.sundaily[6].getTime() - deo.sundaily[4].getTime();
        const night_ms = deo.sundaily[8].getTime() - deo.sundaily[6].getTime();
        daynightlengthstring = msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.";
    }
    else if (cto.sunindex === 8 || cto.sunindex === 9) { // change the day length after midnight
        const day_ms = deo.sundaily[10].getTime() - deo.sundaily[8].getTime();
        const night_ms = deo.sundaily[8].getTime() - deo.sundaily[6].getTime();
        daynightlengthstring = msToTime(day_ms, false) + " day length / " + msToTime(night_ms, false) + " night length.";
    }

    // industrial time string
    const options: Intl.DateTimeFormatOptions = {
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
    industrialdtstring = ('Industrial Time: ' + new Intl.DateTimeFormat("en-GB", options).format(cto.currenttime));
    comptime = cto.currenttime.toISOString();

    return (
        <div>
            <p>{ suneventsstring }<br></br>
            { daynightlengthstring }<br></br>
            { moonphasestring }<br></br>
            { mooneventstring }<br></br>
            { industrialdtstring }<br></br>
            { comptime }</p>
        </div>
    )
};

export default ClockStrings;