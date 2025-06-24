import { useEffect, useState } from "react";
import { msToTime } from "../utils/functions";
import { DailyEventsObj } from "../types/interfaces";
import { useIntervalTimestamp } from "../utils/functions";

interface ClockStringsProps {
  deo: DailyEventsObj;
}

const ClockStrings = ({ deo }: ClockStringsProps) => {
  const nowSecond = useIntervalTimestamp(1000); // update every second
  const [sunIndex, setSunIndex] = useState(0);
  useEffect(() => {
    if (deo.sundaily.length > 0 && deo.sundaily[0] !== 0) {
      setSunIndex(deo.sundaily.findIndex((date) => nowSecond < date));
    }
  }, [nowSecond, deo.sundaily]);


  const timeStyle: React.CSSProperties = {
    fontFamily: "'Courier New', monospace, 'Orbitron'",
    fontSize: '1.8rem',
    color: '#F5EBFF',
    margin: '0 0.3rem',
    fontWeight: 800,
  };

    let suneventsstring: React.ReactNode = "sun events string";
    let daynightlengthstring: React.ReactNode = "day and night lengths string";
    let moonphasestring: React.ReactNode = "moon phase string";
    let mooneventstring: React.ReactNode = "moon events string";
    let industrialdtstring: React.ReactNode = "industrial datetime string";
    let comptime: React.ReactNode = "computer time";

  // sun events string
  if (sunIndex === 4 || sunIndex === 8) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since midnight.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunrise.
    </>;
  } else if (sunIndex === 5 || sunIndex === 9) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunrise.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until high noon.
    </>;
  } else if (sunIndex === 6) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since high noon.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunset.
    </>;
  } else if (sunIndex === 7) {
    const since_ms = nowSecond - deo.sundaily[sunIndex - 1];
    const until_ms = deo.sundaily[sunIndex] - nowSecond;
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunset.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until midnight.
    </>;
  }

  // moon events string
  const moon_index = deo.moondaily.findIndex((date) => nowSecond < date);
  if (moon_index === 2 || moon_index === 4) {
    const since_ms = nowSecond - deo.moondaily[moon_index - 1];
    const until_ms = deo.moondaily[moon_index] - nowSecond;
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonset.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonrise.
    </>;
  } else if (moon_index === 3 || moon_index === 5) {
    const since_ms = nowSecond - deo.moondaily[moon_index - 1];
    const until_ms = deo.moondaily[moon_index] - nowSecond;
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonrise.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonset.
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
    <><br/>Industrial Time: <span style={timeStyle}>{new Intl.DateTimeFormat("en-GB", options).format(nowSecond)}</span></>
  );
  comptime = <><span style={timeStyle}>{new Date(nowSecond).toISOString()}</span></>;

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
        {suneventsstring}<br />
        {daynightlengthstring}<br />
        {moonphasestring}<br />
        {mooneventstring}<br />
        {industrialdtstring}<br />
        {comptime}
      </p>
    </div>
  );
};

export default ClockStrings;
