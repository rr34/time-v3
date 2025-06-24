import { useState } from "react";
import ClockScreen from "./ClockScreen";
import { BodiesDict, ImagesSet } from "../types/interfaces";

interface ClockGalleryProps {
  loading: boolean;
  MomentsArray: string[];
  basenamesList: string[];
  imagesSet: ImagesSet;
  astroData: BodiesDict;
  bodiesInImages: Record<string, BodiesDict>;
  MagRankAllMax: number;
  RepeatLimit: number;
  frameDuration: number;
}
function ClockGallery({ loading, MomentsArray, basenamesList, imagesSet, astroData, bodiesInImages, MagRankAllMax, RepeatLimit, frameDuration }: ClockGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (loading) return <p>Loading image, awimtag, astroData, bodiesInImageData. This can take some minutes.</p>;

  return (
    <div>
      <ClockScreen
        MomentsArray={MomentsArray}
        imageSrc={`${import.meta.env.VITE_BACKEND_URL}/clockimages/${basenamesList[currentIndex]}.png`}
        awimtag={imagesSet[basenamesList[currentIndex]]['awimTag']} // JSON.parse not necessary here because the Express backend parses the json string it receives from the DB
        astroData={astroData}
        bodiesInImage={bodiesInImages?.[basenamesList[currentIndex]]}
        MagRankAllMax={MagRankAllMax}
        onAnimationComplete={() => {setCurrentIndex((i) => (i + 1) % basenamesList.length);}}
        RepeatLimit={RepeatLimit}
        frameDuration={frameDuration}
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
