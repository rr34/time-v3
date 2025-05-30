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
  const [astroData, setGlobalAstroData] = useState(null);

  useEffect(() => {
    const fetchClockImageData = async () => {
      try {
        // 1. Get images set matching the tag filters
        const imagesRes = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ TagsInclude, TagsExclude }),
        });

        const imagesSet = await imagesRes.json();

        // 2. Get celestial data
        const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphotos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awims_dict: imagesSet,
            momentsarray: MomentsArray,
            requestlist: ["stars", "sun", "moon", "planets"],
          }),
        });

        const awimAPI_response = await celestialRes.json();
        const globalAstroData = awimAPI_response["astro dict"];
        const bodiesInImages = awimAPI_response["bodies in image dicts"];

        setGlobalAstroData(globalAstroData);

        // 3. Combine into screensData
        const combined = Object.entries(imagesSet).map(([baseName, set]) => ({
          imageSrc: `${import.meta.env.VITE_FRONTEND_URL}/clockimages/${baseName}.PNG`,
          awimTag: set.awimTag,
          bodiesInImage: bodiesInImages[baseName] || {},
        }));

        setScreensData(combined);
      } catch (err) {
        console.error("Error fetching clock image data:", err);
      }
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
        metadata={screensData[currentIndex].awimTag}
        astroData={astroData}
        bodiesInImage={screensData[currentIndex].bodiesInImage}
        NowMoments={MomentsArray}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + screensData.length) % screensData.length)}>
        Previous
      </button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % screensData.length)}>
        Next
      </button>
    </div>
  );
}

export default ClockGallery;
