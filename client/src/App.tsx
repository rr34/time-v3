import { useMemo, useState } from "react";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import './App.css';
import ClockStrings from "./components/ClockStrings";
import ClockGallery from './components/ClockGallery';
import { useClockGalleryData } from "./utils/useClockGalleryData";
import { BodyData, emptyBodyData, DailyEventsObj, emptyBodiesDict, BodiesDict, ImagesSet } from "./types/interfaces";
import { useIntervalTimestamp } from "./utils/functions";


function App() {
  
  const [showPanel, setShowPanel] = useState(true);
  const [selectedScreen, setSelectedScreen] = useState<'screen' | 'strings' | 'glockenspiel'>('strings');
  const [showGlockenspielPicker, setShowGlockenspielPicker] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [gsCurrentIndex, setGsCurrentIndex] = useState(0);

  type GlockenspielType = 'moonrise_month' | 'sunset_year';
  const [glockenspielType, setGlockenspielType] = useState<GlockenspielType>('moonrise_month');
  const [glockenspielMoments, setGlockenspielMoments] = useState<string[]>([]);
  const [glockenspielLoading, setGlockenspielLoading] = useState(false);
  const [glockenspielError, setGlockenspielError] = useState<string | null>(null);
  const [gsImagesSet, setGsImagesSet] = useState<ImagesSet>({});

  
  const [searchParams] = useSearchParams();
  const groupIdParam = searchParams.get("group_id");
  const groupSlugParam = searchParams.get("clock") ?? searchParams.get("group_slug");
  const MagRankAllMaxParam = searchParams.get("magrankallmax");
  const RepeatLimitParam = searchParams.get("frameduration");
  const frameDurationParam = searchParams.get("frameduration");
  const addHoursParam = searchParams.get("addhours");
  
  const groupSlug = useMemo(() => {
    const trimmed = groupSlugParam?.trim();
    return trimmed ? trimmed : null;
  }, [groupSlugParam]);

  const groupId = useMemo(() => {
    const parsed = Number(groupIdParam);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
    return 1;
  }, [groupIdParam]);
  const groupQuery = useMemo(() => ({
    groupSlug,
    groupId,
  }), [groupSlug, groupId]);
  const MagRankAllMax = useMemo(() => (
    MagRankAllMaxParam ? Number(MagRankAllMaxParam) : 350), // 350 includes 12 from Orion and 7 from Cassiopeia.
    [MagRankAllMaxParam]);
  const RepeatLimit = useMemo(() => (
    RepeatLimitParam ? Number(RepeatLimitParam) : 1),
    [RepeatLimitParam]);
  const frameDuration = useMemo(() => (
    frameDurationParam ? Number(frameDurationParam) : 1.0),
    [frameDurationParam]);
  // Glockenspiel display parameters (hard-coded). Adjust here.
  const glockenspielParams = {
    moonrise_month: { frameDuration: 2.0, GSTitle: "Next 30 Moonrises" },
    sunset_year: { frameDuration: 0.7, GSTitle: "Sunset Each Day for a Year" },
  } as const;
  const glockenspielOptions: Array<{
    type: GlockenspielType;
    label: string;
    detail: string;
  }> = [
    { type: "moonrise_month", label: "Moonrise Month", detail: "Next 30 moonrises (+2 hours)" },
    { type: "sunset_year", label: "Sunset Year", detail: "Sunset (30 minutes prior) every day for a year, 366 frames." },
  ];
  const gsFrameDuration = glockenspielParams[glockenspielType].frameDuration;
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
      // initialize location variables. todo get the location(s) and MSL from the photo metadata
      const clockLatLong: number[] = [40.229,-83.2092];
      const clockMSL: number = 280;
      
      const fetchDailyEvents = async () => {
        try {
          const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: new Date(nowDaily), nowmoments_clockstrings: momentsarray_details }),
          };
          
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/awim/getevents`, requestOptions);
        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`getevents failed (${response.status}): ${errText}`);
        }
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

  useEffect(() => {
    if (selectedScreen !== 'glockenspiel') return;
    let cancelled = false;

    const fetchGlockenspiel = async () => {
      try {
        setGlockenspielLoading(true);
        setGlockenspielError(null);

        const body = { group_slug: glockenspielType, group_type: "glockenspiel" };
        const imagesRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });

        if (!imagesRes.ok) {
          const errText = await imagesRes.text();
          throw new Error(`getimageslist/query failed (${imagesRes.status}): ${errText}`);
        }

        const imagesSetLocal: ImagesSet = await imagesRes.json();
        const basenames = Object.keys(imagesSetLocal);
        if (basenames.length === 0) {
          throw new Error("No photos matched this group.");
        }

        if (cancelled) return;
        setGsImagesSet(imagesSetLocal);
        setGsCurrentIndex(0);

        const awimTag = imagesSetLocal[basenames[0]]?.awimTag;
        if (!awimTag) {
          throw new Error("Selected glockenspiel photo is missing awimTag.");
        }

        const gsBody: Record<string, unknown> = {
          type: glockenspielType,
          awimTag,
          currenttime: new Date(nowDaily).toISOString(),
        };

        const gsRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/awim/glockenspiel`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(gsBody),
        });

        if (!gsRes.ok) {
          const errText = await gsRes.text();
          throw new Error(`glockenspiel failed (${gsRes.status}): ${errText}`);
        }

        const gsData = await gsRes.json();
        if (cancelled) return;
        setGlockenspielMoments(gsData.momentsarray ?? []);
      } catch (error) {
        if (cancelled) return;
        const msg = error instanceof Error ? error.message : String(error);
        setGlockenspielError(msg);
        setGlockenspielMoments([]);
        setGsImagesSet({});
      } finally {
        if (!cancelled) setGlockenspielLoading(false);
      }
    };

    fetchGlockenspiel();
    return () => {
      cancelled = true;
    };
  }, [selectedScreen, glockenspielType, nowDaily]);

  const { loading, basenamesList, imagesSet, astroData, bodiesInImages } = useClockGalleryData(
    momentsarray_animation,
    groupQuery,
    MagRankAllMax,
    LatDecFilter
  );

  const gsBasenamesList = useMemo(() => Object.keys(gsImagesSet), [gsImagesSet]);
  const gsEnabled = selectedScreen === 'glockenspiel' && glockenspielMoments.length > 0;
  const {
    loading: gsLoading,
    astroData: gsAstroData,
    bodiesInImages: gsBodiesInImages,
  } = useClockGalleryData(
    glockenspielMoments,
    groupQuery,
    MagRankAllMax,
    LatDecFilter,
    { enabled: gsEnabled, imagesSetOverride: gsImagesSet }
  );

  const activeBasenamesList = selectedScreen === 'glockenspiel' ? gsBasenamesList : basenamesList;
  const setActiveIndex = selectedScreen === 'glockenspiel' ? setGsCurrentIndex : setCurrentIndex;

  return (
    <>
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
    <button
      style={{
        position: 'absolute',
        top: 10,
        left: 10,
        zIndex: 101,
        padding: '4px 8px',
      }}
      onClick={() => setShowPanel(!showPanel)}
    >
      {showPanel ? "Hide Controls" : "Show Controls"}
    </button>
      {/* Floating Control Panel */}
      {showPanel && (
      <div className="control-panel">
        <label>
          <input
            type="radio"
            value="strings"
            checked={selectedScreen === 'strings'}
            onChange={() => {
              setSelectedScreen('strings');
              setShowGlockenspielPicker(false);
            }}
          />
          Clock Strings
        </label>
        <label>
          <input
            type="radio"
            value="screen"
            checked={selectedScreen === 'screen'}
            onChange={() => {
              setSelectedScreen('screen');
              setShowGlockenspielPicker(false);
            }}
          />
          Clock Gallery
        </label>
        <button
          type="button"
          className={`panel-mode-button ${selectedScreen === 'glockenspiel' ? 'is-active' : ''}`}
          onClick={() => setShowGlockenspielPicker((isOpen) => !isOpen)}
        >
          Glockenspielen
        </button>
        {showGlockenspielPicker && (
          <div className="glockenspiel-picker">
            {glockenspielOptions.map((option) => (
              <button
                key={option.type}
                type="button"
                className={`glockenspiel-option ${selectedScreen === 'glockenspiel' && glockenspielType === option.type ? 'is-active' : ''}`}
                onClick={() => {
                  setGlockenspielType(option.type);
                  setSelectedScreen('glockenspiel');
                  setShowGlockenspielPicker(false);
                }}
              >
                <span>{option.label}</span>
                <small>{option.detail}</small>
              </button>
            ))}
          </div>
        )}
        <button
          onClick={() => {
            if (!activeBasenamesList.length) return;
            setActiveIndex((i) => (i - 1 + activeBasenamesList.length) % activeBasenamesList.length);
          }}
        >
          Previous
        </button>
        <button
          onClick={() => {
            if (!activeBasenamesList.length) return;
            setActiveIndex((i) => (i + 1) % activeBasenamesList.length);
          }}
        >
          Next
        </button>
      </div>
        )}

        {/* Clock display area */}
        <div style={{ width: '100%', height: '100%', pointerEvents: 'none' }}>
          {
            selectedScreen === 'strings'
              ? <ClockStrings deo={DailyEventsObj} addHours={addHours} />
              : selectedScreen === 'glockenspiel'
                ? (
                    glockenspielLoading
                      ? <p>Loading Glockenspielen config...</p>
                      : glockenspielError
                        ? <p>Glockenspielen error: {glockenspielError}</p>
                        : (!glockenspielMoments.length || !gsBasenamesList.length)
                          ? <p>No Glockenspielen data yet.</p>
                          : <ClockGallery
                              loading={gsLoading}
                              MomentsArray={glockenspielMoments}
                              basenamesList={gsBasenamesList}
                              imagesSet={gsImagesSet}
                              astroData={gsAstroData}
                              bodiesInImages={gsBodiesInImages}
                              MagRankAllMax={MagRankAllMax}
                              RepeatLimit={RepeatLimit}
                              frameDuration={gsFrameDuration}
                              currentIndex={gsCurrentIndex}
                              setCurrentIndex={setGsCurrentIndex}
                              mode="step"
                              GSTitle={glockenspielParams[glockenspielType].GSTitle}
                            />
                  )
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
