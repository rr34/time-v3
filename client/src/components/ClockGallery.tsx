import { useEffect, useState } from "react";
import ClockScreen from "./ClockScreen";

interface ClockGalleryProps {
  MomentsArray: string[];
  TagsInclude: string[];
  TagsExclude: string[];
}

function ClockGallery({ MomentsArray, TagsInclude, TagsExclude }: ClockGalleryProps) {
  const [imagesSet, setImagesSet] = useState<any[]>([]);
  const [astroData, setAstroData] = useState<any>(null);
  const [bodiesInImages, setBodiesInImages] = useState<any>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Fetch the image list based on tags
  useEffect(() => {
    const fetchImageList = async () => {
      try {
        const imagesRes = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ TagsInclude, TagsExclude }),
        });

        const imageList = await imagesRes.json();
        setImagesSet(imageList);
      } catch (err) {
        console.error("Error fetching image list:", err);
      }
    };

    fetchImageList();
  }, [TagsInclude, TagsExclude]);

  // Fetch celestial data after imagesSet is loaded
  useEffect(() => {
    const fetchCelestialData = async () => {
      if (imagesSet.length === 0) return;

      try {
        const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphotos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awims_list: imagesSet,
            momentsarray: MomentsArray,
            requestlist: ["stars", "sun", "moon", "planets"],
          }),
        });

        const response = await celestialRes.json();
        setAstroData(response["astro dict"]);
        setBodiesInImages(response["bodies in image dicts"]);
      } catch (err) {
        console.error("Error fetching celestial data:", err);
      }
    };

    fetchCelestialData();
  }, [imagesSet, MomentsArray]);

  // Auto-advance every 60 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % imagesSet.length);
    }, 60000);

    return () => clearInterval(interval);
  }, [imagesSet]);

  if (imagesSet.length === 0 || !astroData || !bodiesInImages) return <p>Loading...</p>;

  const currentImage = imagesSet[currentIndex];
  const baseName = currentImage["Basename"];

  return (
    <div>
      <ClockScreen
        imageSrc={`${import.meta.env.VITE_FRONTEND_URL}/clockimages/${baseName}.PNG`}
        awimtag={currentImage["awimTag"]}
        astroData={astroData}
        bodiesInImage={bodiesInImages[baseName]}
        NowMoments={MomentsArray}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + imagesSet.length) % imagesSet.length)}>Previous</button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % imagesSet.length)}>Next</button>
    </div>
  );
}

export default ClockGallery;
