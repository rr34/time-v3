import { useEffect, useState } from "react";
import ClockScreen from "./ClockScreen";

interface ClockGalleryProps {
  MomentsArray: string[];
  TagsInclude: string[];
  TagsExclude: string[];
}

function ClockGallery({ MomentsArray, TagsInclude, TagsExclude }: ClockGalleryProps) {
  const [screensData, setScreensData] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchClockImageData = async () => {
      // 1. Get image sets matching the tag filters
      const imagesRes = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/getimageslist/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ TagsInclude, TagsExclude }),
      });

      const imageSets = await imagesRes.json(); // { [baseName]: { imageUrl, metadata, ... } }
      console.log('raw response', imagesRes)
      console.log('after dot json', imageSets)

      // 2. Prepare array of metadata for celestial call
      const awimarray = Object.values(imageSets).map(set => set.metadata);

      // 3. Get celestial data
      const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphoto`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          awimarray,
          momentsarray: MomentsArray,
          requestlist: ["stars", "sun", "moon", "planets"],
          returnastro: "true"
        }),
      });

      const celestialData = await celestialRes.json();

      // 4. Combine into screensData
      const combined = Object.entries(imageSets).map(([baseName, set], idx) => ({
        imageSrc: `${import.meta.env.VITE_FRONTEND_URL}${set.imageUrl}`,
        metadata: set.metadata,
        astroData: celestialData[idx]["astro dict"],
        bodiesInImage: celestialData[idx]["bodies in image dict"],
      }));

      setScreensData(combined);
    };

    fetchClockImageData();
  }, [TagsInclude, TagsExclude, MomentsArray]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % screensData.length);
    }, 60_000);

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
        NowMoments={MomentsArray}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + screensData.length) % screensData.length)}>Previous</button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % screensData.length)}>Next</button>
    </div>
  );
}

export default ClockGallery;
