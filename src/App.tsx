import './App.css';
import { useState } from "react";
import { useEffect } from "react";
import ClockStrings from "./components/ClockStrings";

import ClockScreen from './components/ClockScreen';

function App() {
  // initialize location variables
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;

  // initialize time state variables
  let addhours = 0;
  let newdate = new Date(Date.now() + addhours*1000*60*60);
  const [CurrentTime, setCurrentTime] = useState(newdate);
  const [SunIndex, setSunIndex] = useState(0);

  // initialize daily events variables
  const [SunDaily, setSunDaily] = useState<Date[]>([]);
  const [MoonDaily, setMoonDaily] = useState<Date[]>([]);
  const [NearestNew, setNearestNew] = useState<Date>(new Date());
  const [NearestNewAngle, setNearestNewAngle] = useState<number>(0);
  const [NearestFull, setNearestFull] = useState<Date>(new Date());
  const [NearestFullAngle, setNearestFullAngle] = useState<number>(0);

  // update the clock strings every second
  useEffect(() => {
      const intervalID = setInterval(() => {
          let addhours = 0;
          let newdate = new Date(Date.now() + addhours*1000*60*60);
          setCurrentTime(newdate);
          setSunIndex(SunDaily.findIndex((date, i) => CurrentTime < date));
      }, 1*1000);

  return () => clearInterval(intervalID);
  });


  // don't need the following until I start animating SVG
  const NowMoments: string[] = [];
  let MomentsCount: number = 300;
  for (let i=-60; i<MomentsCount-60; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    let idate = new Date(Date.now());
    NowMoments.push(idate.toISOString());
  }

  useEffect(() => {
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({location: clockLatLong, elevation: clockMSL, currenttime: new Date()})
      };
      fetch('http://localhost:8000/getevents', requestOptions)
          .then(response => {
            return response.json()
          })
          .then(data => {
            let sundaily_strings: string[] = JSON.parse(data)['sundaily'];
            let sundaily_dates: Date[] = [];
            sundaily_strings.forEach(element => {
              sundaily_dates.push(new Date(element));
            });
            setSunDaily(sundaily_dates);
            
            let moonDaily_strings: string[] = JSON.parse(data)['moondaily'];
            let moondaily_dates: Date[] = [];
            moonDaily_strings.forEach(element => {
              moondaily_dates.push(new Date(element));
            });
            setMoonDaily(moondaily_dates);
            let newmoon_time: string = JSON.parse(data)['newmoon time'];
            let newmoon_angle: number = Math.round(JSON.parse(data)['newmoon angle']*100) / 100;
            setNearestNew(new Date(newmoon_time))
            setNearestNewAngle(newmoon_angle)
            let fullmoon_time: string = JSON.parse(data)['fullmoon time'];
            let fullmoon_angle: number = Math.round(JSON.parse(data)['fullmoon angle']*100) / 100;
            setNearestFull(new Date(fullmoon_time))
            setNearestFullAngle(fullmoon_angle)
          })
  }, []); // I can put variables in the dependency array and this will run whenever the variables change value.

  return (
    <div>
      {/* <ClockScreen /> */}
      <ClockStrings CurrentTime={CurrentTime} SunIndex={SunIndex} SunDaily={SunDaily} MoonDaily={MoonDaily} NearestNew={NearestNew} NearestNewAngle={NearestNewAngle} NearestFull={NearestFull} NearestFullAngle={NearestFullAngle} />
    </div>
  );
}

export default App
