import { useEffect, useState } from "react";
// import ClockImage from "./ClockImage";
import CelestialBodies from "./CelestialBodies";

interface ClockScreenProps {
  NowMoments: string[];
}

function ClockScreen({ NowMoments }: ClockScreenProps) {
  const [imageSrc, setImageSrc] = useState<string>("");
  const [metadata, setMetadata] = useState<any>(null);
  const [astroData, setAstroData] = useState<number[][]|null>(null);
  const [bodiesInImage, setBodiesInImage] = useState<number[][]|null>(null);

  // Fetch image + metadata
  useEffect(() => {
    const fetchImageAndMetadata = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/clockimage`);
        const data = await response.json();

        const imageUrl = `${import.meta.env.VITE_FRONTEND_URL}${data.imageUrl}`;
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
        const response = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphoto`, {
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
        console.log('raw data celestial in image', data)
        console.log('astrodata celestial in image', data['astro dict'])
        console.log('in image data celestial in image', data['bodies in image dict'])
        setAstroData(data['astro dict']);
        setBodiesInImage(data['bodies in image dict']);
      } catch (error) {
        console.error("Error fetching celestial data:", error);
      }
    };

    fetchCelestialData();
  }, [metadata, NowMoments]);

  return (
    <>
      {imageSrc && <img src={imageSrc} className="clock-image" alt="Clock" />}
      {astroData && bodiesInImage ? (<CelestialBodies astroData={astroData} bodiesInImage={bodiesInImage} />) :
      (<p>Loading celestial data...</p>)}
    </>
  );
}

export default ClockScreen;
