import { useEffect } from "react";
import ClockImage from "./ClockImage";
import CelestialBodies from "./CelestialBodies";

function ClockScreen() {
    useEffect(() => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ awim: imageAWIM, momentsarray: NowMoments, elevation: clockMSL, requestlist: ['stars', 'sun', 'moon', 'planets'], returnastro: 'true' })
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
        <>
            <ClockImage />
            <CelestialBodies />
        </>
      );
}

export default ClockScreen;