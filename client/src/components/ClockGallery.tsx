import { useEffect, useState } from "react";
import ClockScreen from "./ClockScreen";


async function fetchClockImageData(): Promise<any[]> {
  const res = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/clockimages`);
  const imageSets = await res.json(); // { [baseName]: { imageUrl, metadata, ... } }

  const awimarray = Object.values(imageSets).map(set => set.metadata);

  const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphoto`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      awimarray,
      momentsarray: YOUR_NOW_MOMENTS_ARRAY,
      requestlist: ["stars", "sun", "moon", "planets"],
      returnastro: "true"
    }),
  });

  const celestialData = await celestialRes.json();

  return Object.entries(imageSets).map(([baseName, set], idx) => ({
    imageSrc: `${import.meta.env.VITE_FRONTEND_URL}${set.imageUrl}`,
    metadata: set.metadata,
    astroData: celestialData[idx]["astro dict"],
    bodiesInImage: celestialData[idx]["bodies in image dict"],
  }));
}


function ClockGallery() {
  const [screensData, setScreensData] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchClockImageData();
      setScreensData(data);
    };

    loadData();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % screensData.length);
    }, 60_000); // 1-minute cycle

    return () => clearInterval(interval);
  }, [screensData]);

  if (screensData.length === 0) return <p>Loading...</p>;

  return (
    <div>
      <ClockScreen
        imageSrc={screensData[currentIndex].imageSrc}
        metadata={screensData[currentIndex].metadata}
        astroData={screensData[currentIndex].astroData}
        bodiesInImage={screensData[currentIndex].bodiesInImage}
        NowMoments={YOUR_NOW_MOMENTS_ARRAY}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + screensData.length) % screensData.length)}>Previous</button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % screensData.length)}>Next</button>
    </div>
  );
}

export default ClockGallery;