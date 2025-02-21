import { useState } from "react";
import { useEffect } from "react";
import ClockScreen from './components/ClockScreen';
import UpdateClockStrings from "./Functions";

import './App.css';
import ClockString from "./components/ClockString";

function App() {

  // initialize variables
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;

  // initialize state variables
  let newdate = new Date();
  newdate.setSeconds(0,0);
  const [CurrentTime, setCurrentTime] = useState(newdate);
  const [SunDaily, setSunDaily] = useState(['some time string', 'another time string']);

  // initialize clock string state variables
  const [SunEventsString, setSunEventsString] = useState('sun events');
  const [DayNightLengthsString, setDayNightLengthsString] = useState('day and night lengths');
  const [MoonPhaseString, setMoonPhaseString] = useState('moon phase string');
  const [MoonEventString, setMoonEventString] = useState('moon events');
  const [DateString, setDateString] = useState('date string');
  const [IndustrialTimeString, setIndustrialTimeString] = useState('industrial time');

  useEffect(() => {
    const interval = setInterval(() => {
      UpdateClockStrings(setCurrentTime, setSunEventsString, setDayNightLengthsString, setMoonPhaseString, setMoonEventString, setDateString, setIndustrialTimeString);
    }, 1*60*1000);

    return () => clearInterval(interval);
  });

  // don't need the following until I start animating SVG
  const NowMoments: string[] = [];
  var MomentsCount = 300;
  for (let i=-60; i<MomentsCount-60; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    let idate = new Date(CurrentTime.getTime() + i*60*1000 - 4*60*60*1000);
    NowMoments.push(idate.toISOString());
  }

  useEffect(() => {
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({location: clockLatLong, elevation: clockMSL, currenttime: CurrentTime, nowmoments: NowMoments})
      };
      fetch('http://localhost:8000/timestrings', requestOptions)
          .then(response => {
            return response.json()
          })
          .then(data => setSunDaily(JSON.parse(data)['sundaily']));
  }, []); // I can put variables in the dependency array and this will run whenever the variables change value.

  return (
    <div>
      {/* <ClockScreen /> */}
      <p>{CurrentTime.toISOString()}</p>
      <ClockString suneventsstring={SunEventsString} daynightlengthsstring={DayNightLengthsString} moonphasestring={MoonPhaseString} mooneventstring={MoonEventString} datestring={DateString} industrialtimestring={IndustrialTimeString} />
      <p>{SunDaily}</p>
    </div>
  );
}

export default App
