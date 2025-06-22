import { useState } from "react";
import ClockScreen from "./ClockScreen";
import { BodiesDict, ImagesSet } from "../types/interfaces";

interface ClockGalleryProps {
  loading: boolean;
  MomentsArray: string[];
  nowMinute: number;
  nowFast: number;
  basenamesList: string[];
  imagesSet: ImagesSet;
  astroData: BodiesDict;
  bodiesInImages: Record<string, BodiesDict>;
}
function ClockGallery({ loading, MomentsArray, nowMinute, nowFast, basenamesList, imagesSet, astroData, bodiesInImages }: ClockGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (loading) return <p>Loading image, awimtag, astrodata, bodiesInImage data...</p>;

  return (
    <div>
      <ClockScreen
        loading={loading}
        MomentsArray={MomentsArray}
        nowMinute={nowMinute}
        nowFast={nowFast}
        imageSrc={`${import.meta.env.VITE_BACKEND_URL}/clockimages/${basenamesList[currentIndex]}.png`}
        awimtag={imagesSet[basenamesList[currentIndex]]['awimTag']} // JSON.parse not necessary here because the Express backend parses the json string it receives from the DB
        astroData={astroData}
        bodiesInImage={bodiesInImages?.[basenamesList[currentIndex]]}
        onAnimationComplete={() => {setCurrentIndex((i) => (i + 1) % basenamesList.length);}}
      />
      <button onClick={() => setCurrentIndex((i) => (i - 1 + basenamesList.length) % basenamesList.length)}>
        Previous
      </button>
      <button onClick={() => setCurrentIndex((i) => (i + 1) % basenamesList.length)}>
        Next
      </button>
    </div>
  );
}

export default ClockGallery;
