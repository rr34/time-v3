import { useEffect, useState } from "react";
// import ClockImage from "./ClockImage";
import CelestialBodies from "./CelestialBodies";

interface ClockScreenProps {
  NowMoments: string[];
}

function ClockScreen({ NowMoments }: ClockScreenProps) {
  const [imageSrc, setImageSrc] = useState<string>("");
  const [metadata, setMetadata] = useState<any>(null);

  useEffect(() => {
    const fetchImageAndMetadata = async () => {
      try {
        const response = await fetch("http://localhost:5000/clockimage");
        const data = await response.json();

        const imageUrl = `http://localhost:5000${data.imageUrl}`;
        const metadata = data.metadata;

        setImageSrc(imageUrl);
        setMetadata(metadata);

        const requestOptions = {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awim: metadata, // sending the object, not URL
            momentsarray: NowMoments,
            requestlist: ["stars", "sun", "moon", "planets"],
            returnastro: "true",
          }),
        };

        const astroResponse = await fetch("http://localhost:8000/celestialinphoto", requestOptions);
        const astroData = await astroResponse.json();
        // Optionally: setCelestialBodies(astroData);
      } catch (error) {
        console.error("Error fetching image or celestial data:", error);
      }
    };

    fetchImageAndMetadata();
  }, [NowMoments]);

  return (
    <>
      {imageSrc && <img src={imageSrc} className="clock-image" alt="Clock" />}
      <CelestialBodies />
    </>
  );
}

export default ClockScreen;
