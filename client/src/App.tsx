import { useMemo, useState } from "react";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import './App.css';
import ClockStrings from "./components/ClockStrings";
import ClockGallery from './components/ClockGallery';
import { useClockGalleryData } from "./utils/useClockGalleryData";
import { BodyData, emptyBodyData, DailyEventsObj, emptyBodiesDict, BodiesDict } from "./types/interfaces";
import { useIntervalTimestamp } from "./utils/functions";


function App() {
  
  const [selectedScreen, setSelectedScreen] = useState<'screen' | 'strings'>('strings');
  const [currentIndex, setCurrentIndex] = useState(0);

  
  const [searchParams] = useSearchParams();
  const tagsIncludeParam = searchParams.get("tagsinclude");  // comma-separated
  const tagsExcludeParam = searchParams.get("tagsexclude");
  const MagRankAllMaxParam = searchParams.get("magrankallmax");
  const RepeatLimitParam = searchParams.get("frameduration");
  const frameDurationParam = searchParams.get("frameduration");
  const addHoursParam = searchParams.get("addhours");
  
  const TagsInclude = useMemo(() => (
    tagsIncludeParam ? tagsIncludeParam.split(",") : ['ourhouse','best']),
    [tagsIncludeParam]);
  const TagsExclude = useMemo(() => (
    tagsExcludeParam ? tagsExcludeParam.split(",") : []),
    [tagsExcludeParam]);
  const MagRankAllMax = useMemo(() => (
    MagRankAllMaxParam ? Number(MagRankAllMaxParam) : 350), // 350 includes 12 from Orion and 7 from Cassiopeia.
    [MagRankAllMaxParam]);
  const RepeatLimit = useMemo(() => (
    RepeatLimitParam ? Number(RepeatLimitParam) : 1),
    [RepeatLimitParam]);
  const frameDuration = useMemo(() => (
    frameDurationParam ? Number(frameDurationParam) : 1.0),
    [frameDurationParam]);
  const addHours = useMemo(() => (
    addHoursParam ? Number(addHoursParam) : 0.0),
    [addHoursParam]);
  const LatDecFilter = true; // Filter example: with top 350 stars, for latitude of 40, declination > -50 filters out 58 stars leaving 292 possibly visible above horizon.

  const now15Min = useIntervalTimestamp(15 * 60 * 1000) + addHours*1000*60*60; // update every 15 minutes
  const nowDaily = useIntervalTimestamp(24 * 60 * 60 * 1000) + addHours*1000*60*60; // update just daily

  const momentsarray_animation = useMemo(() => {
    const momentscount: number = 20 + 1; // plus one makes the duration from the beginning to end match stepminutes times the first number.
    const stepsbefore: number = 10;
    const stepminutes: number = 3; // 3 minutes is twenty steps per hour.
    const arr: string[] = [];
    for (let i = -stepsbefore; i < momentscount - stepsbefore; i++) {
      const idate = new Date(now15Min + i * stepminutes*1000*60);
      arr.push(idate.toISOString());
    }
    return arr;
  }, [now15Min])
 
  const momentsarray_details = useMemo(() => {
    const momentscount: number = 15*60 + 1; // plus one makes the duration from the beginning to end match stepseconds times the first number.
    const stepsbefore: number = 0;
    const stepseconds: number = 1;
    const arr: string[] = [];
    for (let i = -stepsbefore; i < momentscount - stepsbefore; i++) {
      const idate = new Date(now15Min + i * stepseconds*1000);
      arr.push(idate.toISOString());
    }
    return arr;
  }, [now15Min])
 
    // initialize daily events object
    const [DailyEventsObj, setDailyEventsObj] = useState<DailyEventsObj>({ sundaily: [0], sundailydata: emptyBodyData, moondaily: [0], moondailydata: emptyBodyData, nearestnew: 0, nearestnewangle: 0, nearestfull: 0, nearestfullangle: 0, momentsarrayDetails: [0], sunmoonDetails: emptyBodiesDict });
  
    useEffect(() => {
      // initialize location variables. todo get the location(s) and MSL from the photo tags
      const clockLatLong: number[] = [40.229,-83.2092];
      const clockMSL: number = 280;
      
      const fetchDailyEvents = async () => {
        try {
          const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: new Date(nowDaily), nowmoments_clockstrings: momentsarray_details }),
          };
          
        const response = await fetch(`${import.meta.env.VITE_AWIM_URL}/getevents`, requestOptions);
        const data = await response.json();
        
        const sundaily_strings: string[] = data['sundaily'];
        const sundaily_ms: number[] = sundaily_strings.map(str => new Date(str).getTime());
        const sundailydata: BodyData = data['sundailydata']
        
        const moondaily_strings: string[] = data['moondaily'];
        const moondaily_ms: number[] = moondaily_strings.map(str => new Date(str).getTime());
        const moondailydata: BodyData = data['moondailydata']

        const newmoon_time: string = data['newmoon time'];
        const newmoon_angle: number = Math.round(data['newmoon angle'] * 100) / 100;

        const fullmoon_time: string = data['fullmoon time'];
        const fullmoon_angle: number = Math.round(data['fullmoon angle'] * 100) / 100;

        const sunmoonDetails: BodiesDict = data['sunmoon_details']

        setDailyEventsObj({
          sundaily: sundaily_ms,
          sundailydata: sundailydata,
          moondaily: moondaily_ms,
          moondailydata: moondailydata,
          nearestnew: new Date(newmoon_time).getTime(),
          nearestnewangle: newmoon_angle,
          nearestfull: new Date(fullmoon_time).getTime(),
          nearestfullangle: fullmoon_angle,
          momentsarrayDetails: momentsarray_details.map(d => Date.parse(d)),
          sunmoonDetails: sunmoonDetails,
        });
      } catch (error) {
        console.error("Error fetching daily events:", error);
      }
    };

    fetchDailyEvents();
  }, [nowDaily, momentsarray_details]);

    const { loading, basenamesList, imagesSet, astroData, bodiesInImages } = useClockGalleryData(momentsarray_animation, TagsInclude, TagsExclude, MagRankAllMax, LatDecFilter);

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
  <button
    onClick={() =>
      setCurrentIndex((i) => (i - 1 + basenamesList.length) % basenamesList.length)
    }
  >
    Previous
  </button>
  <button
    onClick={() => setCurrentIndex((i) => (i + 1) % basenamesList.length)}
  >
    Next
  </button>
        </div>

        {/* Clock display area */}
        <div style={{ width: '100%', height: '100%', pointerEvents: 'none' }}>
          {
            selectedScreen === 'strings'
              ? <ClockStrings deo={DailyEventsObj} addHours={addHours} />
              : <ClockGallery
                  loading={loading}
                  MomentsArray={momentsarray_animation}
                  basenamesList={basenamesList}
                  imagesSet={imagesSet}
                  astroData={astroData}
                  bodiesInImages={bodiesInImages}
                  MagRankAllMax={MagRankAllMax}
                  RepeatLimit={RepeatLimit}
                  frameDuration={frameDuration}
                  currentIndex={currentIndex}
                  setCurrentIndex={setCurrentIndex}
                  />
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
