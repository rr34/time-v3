import { useEffect, useState } from "react";
// import ClockImage from "./ClockImage";
import CelestialBodies from "./CelestialBodies";

interface ClockScreenProps {
  NowMoments: string[];
}

function ClockScreen({ NowMoments }: ClockScreenProps) {
  const [imageSrc, setImageSrc] = useState<string>("");
  const [metadata, setMetadata] = useState<any>(null);
  const [astroData, setAstroData] = useState<any>(null);

  // Fetch image + metadata
  useEffect(() => {
    const fetchImageAndMetadata = async () => {
      try {
        const response = await fetch("http://localhost:5000/clockimage");
        const data = await response.json();

        const imageUrl = `http://localhost:5000${data.imageUrl}`;
        setImageSrc(imageUrl);
        setMetadata(data.metadata);
      } catch (error) {
        console.error("Error fetching image or metadata:", error);
      }
    };

    fetchImageAndMetadata();
  }, []);

  // Fetch celestial data (dependent on metadata and NowMoments)
  useEffect(() => {
    const fetchCelestialData = async () => {
      if (!metadata) return;

      try {
        const response = await fetch("http://localhost:8000/celestialinphoto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awim: metadata,
            momentsarray: NowMoments,
            requestlist: ["stars", "sun", "moon", "planets"],
            returnastro: "true",
          }),
        });

        const data = await response.json();
        console.log(data) // todonext: use this data to place celestial objects in the image.
        setAstroData(data); // optional
      } catch (error) {
        console.error("Error fetching celestial data:", error);
      }
    };

    fetchCelestialData();
  }, [metadata, NowMoments]);

  return (
    <>
      {imageSrc && <img src={imageSrc} className="clock-image" alt="Clock" />}
      <CelestialBodies />
    </>
  );
}

export default ClockScreen;
