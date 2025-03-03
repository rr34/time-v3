import React from "react";

interface ClockStringProps {
    suneventsstring: string;
    daynightlengthsstring: string;
    moonphasestring: string;
    mooneventstring: string;
    industrialdttimestring: string;
  }

const ClockString: React.FC<ClockStringProps> = ({suneventsstring, daynightlengthsstring, moonphasestring, mooneventstring, industrialdttimestring}) => {
    return (
        <div>
            <p>{ suneventsstring }<br></br>
            { daynightlengthsstring }<br></br>
            { moonphasestring }<br></br>
            { mooneventstring }<br></br>
            { industrialdttimestring }</p>
        </div>
    )
};

export default ClockString