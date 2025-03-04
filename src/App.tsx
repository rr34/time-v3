import { useState } from "react";
import { useEffect } from "react";
import ClockScreen from './components/ClockScreen';
import { UpdateClockStrings } from "./Functions";
import { UpdateDayNightLengthString } from "./Functions";

import './App.css';
import ClockString from "./components/ClockString";

function App() {

  // initialize variables
  const clockLatLong = [40.229,-83.2092];
  const clockMSL = 280;

  // initialize state variables
  let newdate = new Date();
  let addhours = 8*24;
  newdate = new Date(newdate.getTime() + addhours*1000*60*60);

  const [CurrentTime, setCurrentTime] = useState(newdate);
  const [SunDaily, setSunDaily] = useState<Date[]>([]);
  const [MoonDaily, setMoonDaily] = useState<Date[]>([]);
  const [NearestNew, setNearestNew] = useState<Date | false>(false);
  const [NearestNewAngle, setNearestNewAngle] = useState<number | false>(false);
  const [NearestFull, setNearestFull] = useState<Date | false>(false);
  const [NearestFullAngle, setNearestFullAngle] = useState<number | false>(false);

  // initialize clock string state variables
  const [SunIndex, setSunIndex] = useState(0);
  const [SunEventsString, setSunEventsString] = useState('current sun events');
  const [DayNightLengthsString, setDayNightLengthsString] = useState('day and night lengths');
  const [MoonPhaseString, setMoonPhaseString] = useState('moon phase string');
  const [MoonEventString, setMoonEventString] = useState('moon events');
  const [IndustrialDTString, setIndustrialDTString] = useState('industrial time');

  useEffect(() => {
    const interval = setInterval(() => {
      UpdateClockStrings(SunDaily, SunIndex, MoonDaily, NearestNew, NearestNewAngle, NearestFull, NearestFullAngle, setSunIndex, setCurrentTime, setSunEventsString, setMoonPhaseString, setMoonEventString, setIndustrialDTString);
    }, 1*1000);

    return () => clearInterval(interval);
  });

  // don't need the following until I start animating SVG
  const NowMoments: string[] = [];
  let MomentsCount = 300;
  for (let i=-60; i<MomentsCount-60; i++) { // generates times from an hour prior to CurrentTime until 4 hours after CurrentTime
    let idate = new Date(CurrentTime.getTime());
    NowMoments.push(idate.toISOString());
  }

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
            if (newmoon_time !== 'false') {
              setNearestNew(new Date(newmoon_time))
              setNearestNewAngle(newmoon_angle)
            }
            let fullmoon_time: string = JSON.parse(data)['fullmoon time'];
            let fullmoon_angle: number = Math.round(JSON.parse(data)['fullmoon angle']*100) / 100;
            if (fullmoon_time !== 'false') {
              setNearestFull(new Date(fullmoon_time))
              setNearestFullAngle(fullmoon_angle)
            }
          })
  }, []); // I can put variables in the dependency array and this will run whenever the variables change value.

  return (
    <div>
      {/* <ClockScreen /> */}
      <p>{CurrentTime.toISOString()}</p>
      <ClockString suneventsstring={SunEventsString} daynightlengthsstring={DayNightLengthsString} moonphasestring={MoonPhaseString} mooneventstring={MoonEventString} industrialdttimestring={IndustrialDTString} />
      {/* <p>{SunDaily}</p> */}
    </div>
  );
}

export default App
