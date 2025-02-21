export default function UpdateClockStrings(setCurrentTime: Function, setSunEventsString: Function, setDayNightLengthsString: Function, setMoonPhaseString: Function, setMoonEventString: Function, setDateString: Function, setIndustrialTimeString: Function) {
    let newdate = new Date();
    //   newdate.setSeconds(0,0);
    setCurrentTime(newdate);
    
    setSunEventsString('successs, set sun events string');
    setDayNightLengthsString('successs, set string');
    setMoonPhaseString('successs, set string');
    setMoonEventString('successs, set string');
    setDateString('successs, set string');
    setIndustrialTimeString('successs, set string');
}