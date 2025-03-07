import './App.css';
import { Suspense, useState } from "react";
import { useEffect } from "react";
import ClockStrings from "./components/ClockStrings";

import ClockScreen from './components/ClockScreen';
import imageAWIM from './assets/clock_images/timhouse20220410 - NL100550.json';

export interface ClockTimeObj {
  currenttime: Date;
  sunindex: number;
};

export interface DailyEventsObj {
  sundaily: Date[];
  moondaily: Date[];
  nearestnew: Date;
  nearestnewangle: number;
  nearestfull: Date;
  nearestfullangle: number;
}

function App() {
  // initialize location variables
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;

  // initialize time state object
  let addhours = 0;
  let newdate = new Date(Date.now() + addhours*1000*60*60);
  const [ClockTimeObj, setClockTimeObj] = useState({ currenttime: newdate, sunindex: 0 });
  
  // initialize daily events object
  const [DailyEventsObj, setDailyEventsObj] = useState({ sundaily: [new Date()], moondaily: [new Date()], nearestnew: newdate, nearestnewangle: 0, nearestfull: newdate, nearestfullangle: 0 });

  // update the clock strings every second. todo: fix this because it causes the entire app to reload twice every second when it fires.
  // useEffect(() => {
  //     const intervalID = setInterval(() => {
  //         let addhours = 0;
  //         let newdate = new Date(Date.now() + addhours*1000*60*60);
  //         let sunindex = DailyEventsObj.sundaily.findIndex((date, i) => newdate < date);
  //         setClockTimeObj({ currenttime: newdate, sunindex: sunindex })
  //     }, 1*1000);

  // return () => clearInterval(intervalID);
  // });

  // don't need the following until I start animating SVG
  const NowMoments: string[] = [];
  let MomentsCount: number = 300;
  for (let i=-60; i<MomentsCount-60; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    let idate = new Date(Date.now());
    NowMoments.push(idate.toISOString());
  }

  // todo: this is firing twice on initialization and making a duplicate request to the API
  // useEffect(() => {
  //     const requestOptions = {
  //         method: 'POST',
  //         headers: { 'Content-Type': 'application/json' },
  //         body: JSON.stringify({ location: clockLatLong, elevation: clockMSL, currenttime: ClockTimeObj.currenttime })
  //     };
  //     fetch('http://localhost:8000/getevents', requestOptions)
  //         .then(response => {
  //           return response.json()
  //         })
  //         .then(data => {
  //           let sundaily_strings: string[] = JSON.parse(data)['sundaily'];
  //           let sundaily_dates: Date[] = [];
  //           sundaily_strings.forEach(element => {
  //             sundaily_dates.push(new Date(element));
  //           });
            
  //           let moonDaily_strings: string[] = JSON.parse(data)['moondaily'];
  //           let moondaily_dates: Date[] = [];
  //           moonDaily_strings.forEach(element => {
  //             moondaily_dates.push(new Date(element));
  //           });
  //           let newmoon_time: string = JSON.parse(data)['newmoon time'];
  //           let newmoon_angle: number = Math.round(JSON.parse(data)['newmoon angle']*100) / 100;
  //           let fullmoon_time: string = JSON.parse(data)['fullmoon time'];
  //           let fullmoon_angle: number = Math.round(JSON.parse(data)['fullmoon angle']*100) / 100;
  //           setDailyEventsObj({ sundaily: sundaily_dates, moondaily: moondaily_dates, nearestnew: new Date(newmoon_time), nearestnewangle: newmoon_angle, nearestfull: new Date(fullmoon_time), nearestfullangle: fullmoon_angle })
  //         })
  // }, []); // I can put variables in the dependency array and this will run whenever the variables change value.

  useEffect(() => {
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ awim: imageAWIM, momentsarray: NowMoments, elevation: clockMSL, requestlist: ['sun', 'moon', 'planets', 'stars'] })
      };
      fetch('http://localhost:8000/celestialinphoto', requestOptions)
          .then(response => {
            return response.json()
          })
          .then(data => {
            console.log('do here like above to retrieve the data')
          })
  }, []);

  return (
    <div>
      <ClockScreen />
      {/* <ClockStrings cto={ClockTimeObj} deo={DailyEventsObj} /> */}
    </div>
  );
}

export default App