import { useEffect, useState } from "react";
import ClockScreen from "./ClockScreen";
import { BodiesDict, ImagesSet } from "../types/interfaces";

interface ClockGalleryProps {
  MomentsArray: string[];
  nowMS: number;
  TagsInclude: string[];
  TagsExclude: string[];
}
function ClockGallery({ MomentsArray, nowMS, TagsInclude, TagsExclude }: ClockGalleryProps) {
  const [imagesSet, setImagesSet] = useState<ImagesSet>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [basenameList, setBasenameList] = useState<string[]>([]);
  const [astroData, setAstroData] = useState<BodiesDict>({});
  const [bodiesInImages, setBodiesInImages] = useState<Record<string, BodiesDict>>({});

  useEffect(() => {
    const fetchClockImageData = async () => {
      try {
        // Step 1: Fetch matching images
        const imagesRes = await fetch(`${import.meta.env.VITE_FRONTEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ TagsInclude, TagsExclude }),
        });

        const imagesSetLocal = await imagesRes.json(); // local variable
        setImagesSet(imagesSetLocal); // also store in state for rendering
        setBasenameList(Object.keys(imagesSetLocal))

        // Step 2: Fetch celestial data using the same images list
        const celestialRes = await fetch(`${import.meta.env.VITE_AWIM_URL}/celestialinphotos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awims_dict: imagesSetLocal, // use local variable, not state
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

  if (basenameList.length === 0) return <p>Loading...</p>;

  return (
    <div>
      <ClockScreen
        imageSrc={`${import.meta.env.VITE_FRONTEND_URL}/clockimages/${basenameList[currentIndex]}.png`}
        awimtag={imagesSet[basenameList[currentIndex]]['awimTag']} // JSON.parse not necessary here because the Express backend parses the json string it receives from the DB
        astroData={astroData}
        bodiesInImage={bodiesInImages?.[basenameList[currentIndex]]}
        MomentsArray={MomentsArray}
        nowMS={nowMS}
        onAnimationComplete={() => {setCurrentIndex((i) => (i + 1) % basenameList.length);}}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + basenameList.length) % basenameList.length)}>
        Previous
      </button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % basenameList.length)}>
        Next
      </button>
    </div>
  );
}

export default ClockGallery;
