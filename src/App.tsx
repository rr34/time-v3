import { useState } from "react";
import { useEffect } from "react";
import ClockScreen from './components/ClockScreen';

import './App.css';

function App() {

  // initialize some variables
  const [CurrentTime, setCurrentTime] = useState(new Date());
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;
  const NowMoments: string[] = [];
  var MomentsCount = 300;
  // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
  for (let i=-60; i<MomentsCount-60; i++) {
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
          .then(data => console.log(JSON.parse(data)['id']));
  }, []);

  return (
    <div>
      {/* <ClockScreen /> */}
      <p>{CurrentTime.toISOString()}</p>
    </div>
  );
}

export default App
