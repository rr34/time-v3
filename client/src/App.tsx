import { useMemo, useState } from "react";
import { useEffect } from "react";
import './App.css';
import ClockStrings from "./components/ClockStrings";
import ClockGallery from './components/ClockGallery';
import { useSearchParams } from "react-router-dom";
import { useClockGalleryData } from "./utils/useClockGalleryData";
import { DailyEventsObj } from "./types/interfaces";
import ClockScreen from "./components/ClockScreen";
import ClockScreenFresh from "./components/ClockScreenFresh";


function useIntervalTimestamp(intervalMs: number) {
  const [nowMs, setNowMs] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => {
      setNowMs(Date.now());
    }, intervalMs);

    return () => clearInterval(timer);
  }, [intervalMs]);

  return nowMs;
}


function App() {
  
  const nowFast = useIntervalTimestamp(100); // update every second
  const nowSecond = useIntervalTimestamp(1000); // update every second
  const nowMinute = useIntervalTimestamp(60 * 1000); // update every minute
  const now15Min = useIntervalTimestamp(15 * 60 * 1000); // update every 15 minutes
  const nowDaily = useIntervalTimestamp(24 * 60 * 60 * 1000); // update just daily
  
  const [sunIndex, setSunIndex] = useState(0);
  
  const [selectedScreen, setSelectedScreen] = useState<'screen' | 'strings'>('strings');
  
  const [searchParams] = useSearchParams();
  const tagsIncludeParam = searchParams.get("tagsinclude");  // comma-separated
  const tagsExcludeParam = searchParams.get("tagsexclude");

  const TagsInclude = useMemo(() => (
    tagsIncludeParam ? tagsIncludeParam.split(",") : []),
    [tagsIncludeParam]);
  const TagsExclude = useMemo(() => (
    tagsExcludeParam ? tagsExcludeParam.split(",") : []),
    [tagsExcludeParam]);

    // initialize daily events object
    const [DailyEventsObj, setDailyEventsObj] = useState<DailyEventsObj>({ sundaily: [0], moondaily: [0], nearestnew: 0, nearestnewangle: 0, nearestfull: 0, nearestfullangle: 0 });

    const momentsarray = useMemo(() => {
    const momentscount: number = 40 + 1; // plus one makes the duration from the beginning to end match stepminutes times the first number.
    const stepminutes: number = 6; // 6 minutes is ten steps per hour, which makes a good animation up to ~12 hours.
    const stepsbefore: number = 10;
    const arr: string[] = [];
    for (let i = -stepsbefore; i < momentscount - stepsbefore; i++) {
      const idate = new Date(now15Min + i * stepminutes * 1000 * 60);
      arr.push(idate.toISOString());
    }
    return arr;
  }, [now15Min])
  
  useEffect(() => {
    const clockLatLong: number[] = [40.229,-83.2092];
    const clockMSL: number = 280;
    const fetchDailyEvents = async () => {
      // initialize location variables. todo get the location(s) and MSL from the photo tags
      try {
        const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: new Date(nowDaily) }),
        };

        const response = await fetch(`${import.meta.env.VITE_AWIM_URL}/getevents`, requestOptions);
        const data = await response.json();
        
        const sundaily_strings: string[] = data['sundaily'];
        const sundaily_ms: number[] = sundaily_strings.map(str => new Date(str).getTime());

        const moondaily_strings: string[] = data['moondaily'];
        const moondaily_ms: number[] = moondaily_strings.map(str => new Date(str).getTime());

        const newmoon_time: string = data['newmoon time'];
        const newmoon_angle: number = Math.round(data['newmoon angle'] * 100) / 100;

        const fullmoon_time: string = data['fullmoon time'];
        const fullmoon_angle: number = Math.round(data['fullmoon angle'] * 100) / 100;

        setDailyEventsObj({
          sundaily: sundaily_ms,
          moondaily: moondaily_ms,
          nearestnew: new Date(newmoon_time).getTime(),
          nearestnewangle: newmoon_angle,
          nearestfull: new Date(fullmoon_time).getTime(),
          nearestfullangle: fullmoon_angle,
        });
      } catch (error) {
        console.error("Error fetching daily events:", error);
      }
    };

    fetchDailyEvents();
  }, [nowDaily]);

useEffect(() => {
  if (DailyEventsObj.sundaily.length > 0 && DailyEventsObj.sundaily[0] !== 0) {
    setSunIndex(DailyEventsObj.sundaily.findIndex((date) => nowSecond < date));
  }
}, [nowSecond, DailyEventsObj.sundaily]);

    const { loading, basenamesList, imagesSet, astroData, bodiesInImages } = useClockGalleryData(momentsarray, TagsInclude, TagsExclude);

  return (
    <>
      <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
        {/* Floating Control Panel */}
        <div className="control-panel">
          <label>
            <input
              type="radio"
              value="strings"
              checked={selectedScreen === 'strings'}
              onChange={() => setSelectedScreen('strings')}
            />
            Clock Strings
          </label>
          <label>
            <input
              type="radio"
              value="screen"
              checked={selectedScreen === 'screen'}
              onChange={() => setSelectedScreen('screen')}
            />
            Clock Gallery
          </label>
        </div>

        {/* Clock display area */}
        <div style={{ width: '100%', height: '100%', pointerEvents: 'none' }}>
          {
            selectedScreen === 'strings'
              ? <ClockStrings nowSecond={nowSecond} sunIndex={sunIndex} deo={DailyEventsObj} />
              : <ClockGallery loading={loading} MomentsArray={momentsarray} nowMinute={nowMinute} nowFast={nowFast} basenamesList={basenamesList} imagesSet={imagesSet} astroData={astroData} bodiesInImages={bodiesInImages} />
          }
          {/* {
            selectedScreen === 'strings_remove_this'
              ? <ClockScreenFresh totalDuration={15} repeatLimit={"1"} />
              : <ClockScreenFresh totalDuration={15} repeatLimit={"1"} />
          } */}
        </div>
      </div>
    </>
  );
}

export default App
