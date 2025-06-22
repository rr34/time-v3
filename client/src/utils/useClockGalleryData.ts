import { useEffect, useState } from "react";
import { BodiesDict, ImagesSet } from "../types/interfaces";

export function useClockGalleryData (MomentsArray: string[], TagsInclude: string[], TagsExclude: string[] ) {
  const [imagesSet, setImagesSet] = useState<ImagesSet>({});
  const [basenamesList, setBasenamesList] = useState<string[]>([]);
  const [astroData, setAstroData] = useState<BodiesDict>({});
  const [bodiesInImages, setBodiesInImages] = useState<Record<string, BodiesDict>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

const tagsIncludeKey = TagsInclude.join(',');
const tagsExcludeKey = TagsExclude.join(',');
const momentsArrayKey = MomentsArray.join(',');

  useEffect(() => {
    const fetchClockImageData = async () => {
      try {
        setLoading(true);
        setError(null);
        // Step 1: Fetch matching images
        const imagesRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/getimageslist/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ TagsInclude, TagsExclude }),
        });

        const imagesSetLocal = await imagesRes.json(); // local variable
        setImagesSet(imagesSetLocal); // also store in state for rendering
        setBasenamesList(Object.keys(imagesSetLocal))

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

        setLoading(false);
      } catch (err) {
        console.error("Error fetching clock image data:", err);
        setError(false);
        setLoading(false);
      }
    };

    fetchClockImageData();
  }, [tagsIncludeKey, tagsExcludeKey, momentsArrayKey]);

  return { loading, error, basenamesList, imagesSet, astroData, bodiesInImages};
}
