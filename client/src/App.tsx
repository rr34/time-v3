import './App.css';
import { Suspense, useState } from "react";
import { useEffect } from "react";
import ClockStrings from "./components/ClockStrings";
import ClockScreen from './components/ClockScreen';


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

  // don't need the following until I start animating SVG
  const momentscount: number = 20;
  const stepminutes: number = 15;
  const stepsbefore: number = 4;
  const nowdate: number = Date.now();
  const momentsarray: string[] = [];
  for (let i=-stepsbefore; i<momentscount-stepsbefore; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    const idate = new Date(nowdate + i * stepminutes*1000*60);
    momentsarray.push(idate.toISOString());
  }
  const [NowMoments, setNowMoments] = useState<string[]>(momentsarray);

  // todo: this is firing twice on initialization and making a duplicate request to the API
  useEffect(() => {
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: ClockTimeObj.currenttime })
      };
      fetch('http://localhost:8000/getevents', requestOptions)
          .then(response => {
            return response.json()
          })
          .then(data => {
            const sundaily_strings: string[] = JSON.parse(data)['sundaily'];
            const sundaily_dates: Date[] = [];
            sundaily_strings.forEach(element => {
              sundaily_dates.push(new Date(element));
            });
            
            const moonDaily_strings: string[] = JSON.parse(data)['moondaily'];
            const moondaily_dates: Date[] = [];
            moonDaily_strings.forEach(element => {
              moondaily_dates.push(new Date(element));
            });
            const newmoon_time: string = JSON.parse(data)['newmoon time'];
            const newmoon_angle: number = Math.round(JSON.parse(data)['newmoon angle']*100) / 100;
            const fullmoon_time: string = JSON.parse(data)['fullmoon time'];
            const fullmoon_angle: number = Math.round(JSON.parse(data)['fullmoon angle']*100) / 100;
            setDailyEventsObj({ sundaily: sundaily_dates, moondaily: moondaily_dates, nearestnew: new Date(newmoon_time), nearestnewangle: newmoon_angle, nearestfull: new Date(fullmoon_time), nearestfullangle: fullmoon_angle })
          })
  }, []);

  return (
    <>
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ marginLeft: '1rem' }}>
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
          Clock Screen
        </label>
      </div>
      {
        selectedScreen === 'strings' ?
        (<ClockStrings cto={ClockTimeObj} setcto={setClockTimeObj} deo={DailyEventsObj} />) :
        (<ClockScreen NowMoments={NowMoments}/>)
      }
    </>
  );
}

export default App