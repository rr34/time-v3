import { useEffect } from "react";
import { msToTime } from "../utils/functions";
import { ClockTimeObj, DailyEventsObj } from "../App";

interface ClockStringsProps {
  cto: ClockTimeObj;
  setcto: React.Dispatch<React.SetStateAction<{ currenttime: Date; sunindex: number }>>;
  deo: DailyEventsObj;
}

const ClockStrings = ({ cto, setcto, deo }: ClockStringsProps) => {
  useEffect(() => {
    const intervalID = setInterval(() => {
      const addhours = 0;
      const newdate = new Date(Date.now() + addhours * 1000 * 60 * 60);
      const sunindex = deo.sundaily.findIndex((date) => newdate < date);
      setcto({ currenttime: newdate, sunindex });
    }, 1000);

    return () => clearInterval(intervalID);
  }, [deo.sundaily, setcto]);

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

  const { currenttime, sunindex } = cto;

  // sun events string
  if (sunindex === 4 || sunindex === 8) {
    const since_ms = currenttime.getTime() - deo.sundaily[sunindex - 1].getTime();
    const until_ms = deo.sundaily[sunindex].getTime() - currenttime.getTime();
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since midnight.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunrise.
    </>;
  } else if (sunindex === 5 || sunindex === 9) {
    const since_ms = currenttime.getTime() - deo.sundaily[sunindex - 1].getTime();
    const until_ms = deo.sundaily[sunindex].getTime() - currenttime.getTime();
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunrise.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until high noon.
    </>;
  } else if (sunindex === 6) {
    const since_ms = currenttime.getTime() - deo.sundaily[sunindex - 1].getTime();
    const until_ms = deo.sundaily[sunindex].getTime() - currenttime.getTime();
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since high noon.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until sunset.
    </>;
  } else if (sunindex === 7) {
    const since_ms = currenttime.getTime() - deo.sundaily[sunindex - 1].getTime();
    const until_ms = deo.sundaily[sunindex].getTime() - currenttime.getTime();
    suneventsstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since sunset.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until midnight.
    </>;
  }

  // moon events string
  const moon_index = deo.moondaily.findIndex((date) => currenttime < date);
  if (moon_index === 2 || moon_index === 4) {
    const since_ms = currenttime.getTime() - deo.moondaily[moon_index - 1].getTime();
    const until_ms = deo.moondaily[moon_index].getTime() - currenttime.getTime();
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonset.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonrise.
    </>;
  } else if (moon_index === 3 || moon_index === 5) {
    const since_ms = currenttime.getTime() - deo.moondaily[moon_index - 1].getTime();
    const until_ms = deo.moondaily[moon_index].getTime() - currenttime.getTime();
    mooneventstring = <>
      <span style={timeStyle}>{msToTime(since_ms)}</span> since moonrise.{" "}
      <span style={timeStyle}>{msToTime(until_ms)}</span> until moonset.
    </>;
  }

  // moon phase string todo: correct the calculation of the moon phase name to be from phase angle instead of time-based.
  const timedelta_new = currenttime.getTime() - deo.nearestnew.getTime();
  const timedelta_full = currenttime.getTime() - deo.nearestfull.getTime();
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

  // day and night length string. todo: only update when sunindex changes
  if (sunindex === 4 || sunindex === 5) {
    const day_ms = deo.sundaily[6].getTime() - deo.sundaily[4].getTime();
    const night_ms = deo.sundaily[4].getTime() - deo.sundaily[2].getTime();
    const daylengthchange_ms = day_ms - (deo.sundaily[2].getTime() - deo.sundaily[0].getTime());
    daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Day length change since yesterday: <span style={timeStyle}>{msToTime(daylengthchange_ms, false)}</span>
    </>;
  } else if (sunindex === 6 || sunindex === 7) {
      const day_ms = deo.sundaily[6].getTime() - deo.sundaily[4].getTime();
      const night_ms = deo.sundaily[8].getTime() - deo.sundaily[6].getTime();
      const daylengthchange_ms = day_ms - (deo.sundaily[2].getTime() - deo.sundaily[0].getTime());
      daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Day length change since yesterday: <span style={timeStyle}>{msToTime(daylengthchange_ms, false)}</span>
    </>;
  } else if (sunindex === 8 || sunindex === 9) {
      const day_ms = deo.sundaily[10].getTime() - deo.sundaily[8].getTime();
      const night_ms = deo.sundaily[8].getTime() - deo.sundaily[6].getTime();
      const daylengthchange_ms = day_ms - (deo.sundaily[6].getTime() - deo.sundaily[4].getTime());
    daynightlengthstring = <>
      <span style={timeStyle}>{msToTime(day_ms, false)}</span> day length / <span style={timeStyle}>{msToTime(night_ms, false)}</span> night length. Day length change since yesterday: <span style={timeStyle}>{msToTime(daylengthchange_ms, false)}</span>
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
    <><br/>Industrial Time: <span style={timeStyle}>{new Intl.DateTimeFormat("en-GB", options).format(currenttime)}</span></>
  );
  comptime = <><span style={timeStyle}>{currenttime.toISOString()}</span></>;

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
