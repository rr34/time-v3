import { useEffect, useState } from "react";
import { msToTime } from "../utils/functions";
import { DailyEventsObj } from "../types/interfaces";
import { useIntervalTimestamp } from "../utils/functions";

interface ClockStringsProps {
  deo: DailyEventsObj;
  addHours: number;
}

const ClockStrings = ({ deo, addHours }: ClockStringsProps) => {
  const nowSecond = useIntervalTimestamp(1000) + addHours*1000*60*60; // update every second and allow for addHours parameter
  const [sunIndex, setSunIndex] = useState(0);
  const [moonIndex, setMoonIndex] = useState(0);
  const [detailIndex, setDetailIndex] = useState(0);
  useEffect(() => {
    if (deo.sundaily.length > 0 && deo.sundaily[0] !== 0) {
      setSunIndex(deo.sundaily.findIndex((date) => nowSecond < date)); // sets sunIndex to the index of the next event to occur
      setMoonIndex(deo.moondaily.findIndex((date) => nowSecond < date)); // sets moonIndex to the index of the next event to occur
      setDetailIndex(deo.momentsarrayDetails.findIndex((date) => nowSecond < date)); // sets detailIndex to the index of the next timestamp
    }
  }, [nowSecond, deo.sundaily, deo.moondaily]);


  const timeStyle: React.CSSProperties = {
    fontFamily: "'Courier New', monospace, 'Orbitron'",
    fontSize: '1.8rem',
    color: '#F5EBFF',
    margin: '0 0.3rem',
    fontWeight: 800,
  };

    let sundetailsstring: React.ReactNode = "sun details string";
    let suneventsstring: React.ReactNode = "sun events string";
    let daynightlengthstring: React.ReactNode = "day and night lengths string";
    let moondetailsstring: React.ReactNode = "moon details string";
    let moonphaseanglestring: React.ReactNode = "moon phase angle string";
    let moonphasestring: React.ReactNode = "moon phase string";
    let mooneventstring: React.ReactNode = "moon events string";
    let industrialdtstring: React.ReactNode = "industrial datetime string";
    let comptime: React.ReactNode = "computer time";

  // sun details string
    sundetailsstring = <>
      Sun azimuth, artifae: <span style={timeStyle}>{deo.sunmoonDetails?.sun.azimuths?.[detailIndex] ?? 'Loading...'}°, {deo.sunmoonDetails?.sun.artifaes?.[detailIndex] ?? 'Loading...'}°</span>
    </>;

// sun events string
  if (sunIndex === 4 || sunIndex === 8) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since midnight at artifae {deo.sundailydata?.artifaes?.[sunIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunrise at azimuth {deo.sundailydata?.azimuths?.[sunIndex] ?? 'Loading...'}°.
    </>;
  } else if (sunIndex === 5 || sunIndex === 9) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunrise at azimuth {deo.sundailydata?.azimuths?.[sunIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until high noon at artifae {deo.sundailydata?.artifaes?.[sunIndex] ?? 'Loading...'}°.
    </>;
  } else if (sunIndex === 6) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since high noon at artifae {deo.sundailydata?.artifaes?.[sunIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunset at azimuth {deo.sundailydata?.azimuths?.[sunIndex] ?? 'Loading...'}°.
    </>;
  } else if (sunIndex === 7) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunset at azimuth {deo.sundailydata?.azimuths?.[sunIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until midnight at artifae {deo.sundailydata?.artifaes?.[sunIndex] ?? 'Loading...'}°.
    </>;
  }

  // moon details string
    moondetailsstring = <>
      Moon azimuth, artifae: <span style={timeStyle}>{deo.sunmoonDetails?.moon.azimuths?.[detailIndex] ?? 'Loading...'}°, {deo.sunmoonDetails?.moon.artifaes?.[detailIndex] ?? 'Loading...'}°</span>
    </>;
  
  // moon phase angle string
    moonphaseanglestring = <>
      Moon phase angle: <span style={timeStyle}>{deo.sunmoonDetails?.moon.moonphaseangles?.[detailIndex] ?? 'Loading...'}°</span>
    </>;
  
  // moon events string
  if (moonIndex === 2 || moonIndex === 4) {
    const since_ms = nowSecond - deo.moondaily[moonIndex - 1];
    const until_ms = deo.moondaily[moonIndex] - nowSecond;
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonset at azimuth {deo.moondailydata?.azimuths?.[moonIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonrise at azimuth {deo.moondailydata?.azimuths?.[moonIndex] ?? 'Loading...'}°.
    </>;
  } else if (moonIndex === 3 || moonIndex === 5) {
    const since_ms = nowSecond - deo.moondaily[moonIndex - 1];
    const until_ms = deo.moondaily[moonIndex] - nowSecond;
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonrise at azimuth {deo.moondailydata?.azimuths?.[moonIndex-1] ?? 'Loading...'}°.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonset at azimuth {deo.moondailydata?.azimuths?.[moonIndex] ?? 'Loading...'}°.
    </>;
  }

  // moon phase string todo: correct the calculation of the moon phase name to be from phase angle instead of time-based.
  const timedelta_new = nowSecond - deo.nearestnew;
  const timedelta_full = nowSecond - deo.nearestfull;
  if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) > 0) {
    const timedelta_str: string = msToTime(Math.abs(timedelta_new));
    const eclipse_string: string = (deo.nearestnewangle > 178.5) ? ' > ~~178.5° means solar eclipse.' : '';
    moonphasestring = <>
      Waxing crescent. <span style={timeStyle}>{timedelta_str}</span> since new moon at {deo.nearestnewangle.toString()}° phase angle.{eclipse_string}
    </>;
  } else if (Math.abs(timedelta_new) < Math.abs(timedelta_full) && Math.sign(timedelta_new) < 0) {
    const timedelta_str: string = msToTime(Math.abs(timedelta_new));
    const eclipse_string: string = (deo.nearestnewangle > 178.5) ? ' > than ~~178.5° means solar eclipse.' : '';
    moonphasestring = <>
      Waning crescent. <span style={timeStyle}>{timedelta_str}</span> until new moon at {deo.nearestnewangle.toString()}° phase angle.{eclipse_string}
    </>;
  } else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) > 0) {
    const timedelta_str: string = msToTime(Math.abs(timedelta_full));
    const eclipse_string: string = (deo.nearestfullangle < 1.5) ? ' < ~1.5° means lunar eclipse.' : '';
    moonphasestring = <>
      Waning gibbous. <span style={timeStyle}>{timedelta_str}</span> since full moon at {deo.nearestfullangle.toString()}° phase angle.{eclipse_string}
    </>;
  } else if (Math.abs(timedelta_new) > Math.abs(timedelta_full) && Math.sign(timedelta_full) < 0) {
    const timedelta_str: string = msToTime(Math.abs(timedelta_full));
    const eclipse_string: string = (deo.nearestfullangle < 1.5) ? ' < ~1.5° means lunar eclipse.' : '';
    moonphasestring = <>
      Waxing gibbous. <span style={timeStyle}>{timedelta_str}</span> until full moon at {deo.nearestfullangle.toString()}° phase angle.{eclipse_string}
    </>;
  }

  // day and night length string. todo: only update when sunIndex changes
  if (sunIndex === 4 || sunIndex === 5) {
    const day_ms = deo.sundaily[6] - deo.sundaily[4];
    const night_ms = deo.sundaily[4] - deo.sundaily[2];
    const daylengthchange_ms = day_ms - (deo.sundaily[2] - deo.sundaily[0]);
    daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Change: <span style={timeStyle}>{msToTime(daylengthchange_ms, true)}</span>
    </>;
  } else if (sunIndex === 6 || sunIndex === 7) {
      const day_ms = deo.sundaily[6] - deo.sundaily[4];
      const night_ms = deo.sundaily[8] - deo.sundaily[6];
      const daylengthchange_ms = day_ms - (deo.sundaily[2] - deo.sundaily[0]);
      daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Change: <span style={timeStyle}>{msToTime(daylengthchange_ms, true)}</span>
    </>;
  } else if (sunIndex === 8 || sunIndex === 9) {
      const day_ms = deo.sundaily[10] - deo.sundaily[8];
      const night_ms = deo.sundaily[8] - deo.sundaily[6];
      const daylengthchange_ms = day_ms - (deo.sundaily[6] - deo.sundaily[4]);
    daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Change: <span style={timeStyle}>{msToTime(daylengthchange_ms, true)}</span>
    </>;
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
  industrialdtstring = (
    <><br/>Industrial Time: {new Intl.DateTimeFormat("en-GB", options).format(nowSecond)}</>
  );
  comptime = <>Computer Time: {new Date(nowSecond).toISOString()}</>;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        width: '100vw',
        backgroundColor: 'black',
        color: 'white',
        padding: '1rem',
        textAlign: 'center',
        fontFamily: 'Georgia, serif',
        fontSize: '1.5rem',
      }}
    >
      <p>
        Sun<br />
        {sundetailsstring}<br />
        {suneventsstring}<br />
        {daynightlengthstring}<br /><br />
        Moon<br />
        {moondetailsstring}<br />
        {mooneventstring}<br />
        {moonphaseanglestring}<br />
        {moonphasestring}<br />
        <span style={{ fontSize: '0.8rem' }}>
        {industrialdtstring}<br />
        {comptime}
        </span>
      </p>
    </div>
  );
};

export default ClockStrings;
