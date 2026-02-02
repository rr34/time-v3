import { useState } from "react";
import ClockScreen, { ClockScreenMode } from "./ClockScreen";
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
  currentIndex: number;
  setCurrentIndex: (i: number) => void;
  mode?: ClockScreenMode;
}
function ClockGallery({ loading, MomentsArray, basenamesList, imagesSet, astroData, bodiesInImages, MagRankAllMax, RepeatLimit, frameDuration, currentIndex, setCurrentIndex, mode }: ClockGalleryProps) {

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
        onAnimationComplete={() => setCurrentIndex((currentIndex + 1) % basenamesList.length)}
        RepeatLimit={RepeatLimit}
        frameDuration={frameDuration}
        mode={mode}
      />
    </div>
  );
}

export default ClockGallery;
