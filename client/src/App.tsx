import './App.css';
import { Suspense, useState } from "react";
import { useEffect } from "react";
import ClockStrings from "./components/ClockStrings";
import ClockScreen from './components/ClockScreen';
import ClockGallery from './components/ClockGallery';


export interface ClockTimeObj {
  currenttime: Date;
  sunindex: number;
};

export interface DailyEventsObj {
  sundaily: Date[];
  moondaily: Date[];
  nearestnew: Date;
  nearestnewangle: number; // this is the phase angle associated with the nearest new moon
  nearestfull: Date;
  nearestfullangle: number; // this is the phase angle associated with the nearest full moon
}


function App() {
  const [selectedScreen, setSelectedScreen] = useState<'screen' | 'strings'>('strings');

  // initialize location variables
  const clockLatLong: number[] = [40.229,-83.2092];
  const clockMSL: number = 280;

  // initialize time state object
  const addhours = 0;
  const newdate = new Date(Date.now() + addhours*1000*60*60);
  const [ClockTimeObj, setClockTimeObj] = useState({ currenttime: newdate, sunindex: 0 });
  
  // initialize daily events object
  const [DailyEventsObj, setDailyEventsObj] = useState({ sundaily: [new Date()], moondaily: [new Date()], nearestnew: newdate, nearestnewangle: 0, nearestfull: newdate, nearestfullangle: 0 });

  const momentscount: number = 24;
  const stepminutes: number = 15;
  const stepsbefore: number = 8;
  const nowdate: number = Date.now();
  const momentsarray: string[] = [];
  for (let i=-stepsbefore; i<momentscount-stepsbefore; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    const idate = new Date(nowdate + i * stepminutes*1000*60);
    momentsarray.push(idate.toISOString());
  }
  const [NowMoments, setNowMoments] = useState<string[]>(momentsarray);
  const [nowMS, setNowMS] = useState<number>(nowdate);

  // todo: this is firing twice on initialization and making a duplicate request to the API
useEffect(() => {
  const fetchDailyEvents = async () => {
    try {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: ClockTimeObj.currenttime }),
      };
      const response = await fetch('http://localhost:8000/getevents', requestOptions);
      const data = await response.json();
      
      const sundaily_strings: string[] = data['sundaily'];
      const sundaily_dates: Date[] = sundaily_strings.map(str => new Date(str));

      const moondaily_strings: string[] = data['moondaily'];
      const moondaily_dates: Date[] = moondaily_strings.map(str => new Date(str));

      const newmoon_time: string = data['newmoon time'];
      const newmoon_angle: number = Math.round(data['newmoon angle'] * 100) / 100;

      const fullmoon_time: string = data['fullmoon time'];
      const fullmoon_angle: number = Math.round(data['fullmoon angle'] * 100) / 100;

      setDailyEventsObj({
        sundaily: sundaily_dates,
        moondaily: moondaily_dates,
        nearestnew: new Date(newmoon_time),
        nearestnewangle: newmoon_angle,
        nearestfull: new Date(fullmoon_time),
        nearestfullangle: fullmoon_angle,
      });
    } catch (error) {
      console.error("Error fetching daily events:", error);
    }
  };

  fetchDailyEvents();
}, []);

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
              ? <ClockStrings cto={ClockTimeObj} setcto={setClockTimeObj} deo={DailyEventsObj} />
              : <ClockGallery MomentsArray={NowMoments} nowMS={nowMS} TagsInclude={['timhouse']} TagsExclude={['withpeople','skipfornow']} />
          }
        </div>
      </div>
    </>
  );
}

export default App