import { useEffect, useState } from "react";
import ClockScreen from "./ClockScreen";

interface ClockGalleryProps {
  MomentsArray: string[];
  TagsInclude: string[];
  TagsExclude: string[];
}

function ClockGallery({ MomentsArray, TagsInclude, TagsExclude }: ClockGalleryProps) {
  const [imagesSet, setImagesSet] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [astroData, setAstroData] = useState(null);
  const [bodiesInImages, setBodiesInImages] = useState(null);

  useEffect(() => {
    const fetchClockImageData = async () => {
      try {
        // Step 1: Fetch matching images
        const imagesRes = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ TagsInclude, TagsExclude }),
        });

        const images = await imagesRes.json(); // local variable
        setImagesSet(images); // also store in state for rendering

        // Step 2: Fetch celestial data using the same images list
        const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphotos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awims_list: images, // use local variable, not state
            momentsarray: MomentsArray,
            requestlist: ["stars", "sun", "moon", "planets"],
          }),
        });

        const awimAPI_response = await celestialRes.json();
        setAstroData(awimAPI_response["astro dict"]);
        setBodiesInImages(awimAPI_response["bodies in images dicts"]);
      } catch (err) {
        console.error("Error fetching clock image data:", err);
      }
    };

    fetchClockImageData();
  }, [TagsInclude, TagsExclude, MomentsArray]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % imagesSet.length);
    }, 30_000);

    return () => clearInterval(interval);
  }, [imagesSet]);

  if (imagesSet.length === 0) return <p>Loading...</p>;

  return (
    <div>
      <ClockScreen
        imageSrc={`${import.meta.env.VITE_FRONTEND_URL}/clockimages/${imagesSet[currentIndex]['Basename']}.png`}
        awimtag={JSON.parse(imagesSet[currentIndex]['awimTag'])}
        astroData={astroData}
        bodiesInImage={bodiesInImages?.[imagesSet[currentIndex]['Basename']]}
        MomentsArray={MomentsArray}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + imagesSet.length) % imagesSet.length)}>
        Previous
      </button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % imagesSet.length)}>
        Next
      </button>
    </div>
  );
}

export default ClockGallery;
