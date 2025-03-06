import './App.css';
import { useState } from "react";
import { useEffect } from "react";
import ClockStrings from "./components/ClockStrings";

import ClockScreen from './components/ClockScreen';

function App() {
  // initialize location variables
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;

  // initialize state variables
  const [SunIndex, setSunIndex] = useState(0);

  const [SunDaily, setSunDaily] = useState<Date[]>([]);
  const [MoonDaily, setMoonDaily] = useState<Date[]>([]);
  const [NearestNew, setNearestNew] = useState<Date>(new Date());
  const [NearestNewAngle, setNearestNewAngle] = useState<number>(0);
  const [NearestFull, setNearestFull] = useState<Date>(new Date());
  const [NearestFullAngle, setNearestFullAngle] = useState<number>(0);

  // don't need the following until I start animating SVG
  const NowMoments: string[] = [];
  let MomentsCount: number = 300;
  for (let i=-60; i<MomentsCount-60; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    let idate = new Date(CurrentTime.getTime());
    NowMoments.push(idate.toISOString());
  }

  // update the day and night length string whenever the sun index changes, which means we passed a daily sun event
  useEffect(() => {
    UpdateDayNightLengthString(SunDaily, SunIndex, setDayNightLengthsString)
  }, [SunIndex]); // I can put variables in the dependency array and this will run whenever the variables change value.

  useEffect(() => {
      const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({location: clockLatLong, elevation: clockMSL, currenttime: CurrentTime})
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
      <ClockStrings suneventsstring={SunEventsString} daynightlengthsstring={DayNightLengthsString} moonphasestring={MoonPhaseString} mooneventstring={MoonEventString} industrialdttimestring={IndustrialDTString} />
      <p>{}</p>
    </div>
  );
}

export default App
