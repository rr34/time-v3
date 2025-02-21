function ClockString({suneventsstring, daynightlengthsstring, moonphasestring, mooneventstring, datestring, industrialtimestring}) {
    return (
        <div>
            <p>{ suneventsstring }<br></br>
            { daynightlengthsstring }<br></br>
            { moonphasestring }<br></br>
            { mooneventstring }<br></br>
            { datestring }<br></br>
            { industrialtimestring }</p>
        </div>
    )
}

export default ClockString;