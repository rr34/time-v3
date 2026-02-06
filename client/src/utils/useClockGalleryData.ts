import { useEffect, useState } from "react";
import { BodiesDict, ImagesSet } from "../types/interfaces";

interface UseClockGalleryOptions {
  enabled?: boolean;
  imagesSetOverride?: ImagesSet;
}

interface GroupQuery {
  groupSlug?: string | null;
  groupId?: number | null;
}

export function useClockGalleryData (
  MomentsArray: string[],
  groupQuery: GroupQuery,
  MagRankAllMax: number,
  LatDecFilter: boolean,
  options: UseClockGalleryOptions = {}
) {
  const [imagesSet, setImagesSet] = useState<ImagesSet>({});
  const [basenamesList, setBasenamesList] = useState<string[]>([]);
  const [astroData, setAstroData] = useState<BodiesDict>({});
  const [bodiesInImages, setBodiesInImages] = useState<Record<string, BodiesDict>>({});
  const [loading, setLoading] = useState(true);

  const groupSlug = groupQuery.groupSlug ?? null;
  const groupId = groupQuery.groupId ?? null;
  const groupKey = groupSlug ? `slug:${groupSlug}` : (groupId ?? "none");
  const momentsArrayKey = MomentsArray.join(',');
  const { enabled = true, imagesSetOverride } = options;
  const imagesSetOverrideKey = imagesSetOverride ? Object.keys(imagesSetOverride).join(',') : '';

  useEffect(() => {
    const fetchClockImageData = async () => {
      try {
        if (!enabled) return;
        if (!groupSlug && !Number.isFinite(groupId)) {
          setLoading(false);
          return;
        }
        if (!MomentsArray.length) {
          setLoading(false);
          return;
        }
        setLoading(true);
        let imagesSetLocal: ImagesSet | undefined = imagesSetOverride;
        if (!imagesSetLocal || Object.keys(imagesSetLocal).length === 0) {
          // Step 1: Fetch matching images
          const body = groupSlug
            ? { group_slug: groupSlug }
            : { group_id: groupId };
          const imagesRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/getimageslist/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });

          if (!imagesRes.ok) {
            const errText = await imagesRes.text();
            throw new Error(`getimageslist/query failed (${imagesRes.status}): ${errText}`);
          }

          imagesSetLocal = await imagesRes.json(); // local variable
        }

        setImagesSet(imagesSetLocal);
        setBasenamesList(Object.keys(imagesSetLocal));

        if (Object.keys(imagesSetLocal).length === 0) {
          setAstroData({});
          setBodiesInImages({});
          setLoading(false);
          return;
        }

        // Step 2: Fetch celestial data using the same images list
        const celestialRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/awim/celestialinphotos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            awims_dict: imagesSetLocal, // use local variable, not state
            momentsarray: MomentsArray,
            requestlist: ["stars", "sun", "moon", "planets"],
            MagRankAllMax: MagRankAllMax,
            LatDecFilter: LatDecFilter,
          }),
        });

        if (!celestialRes.ok) {
          const errText = await celestialRes.text();
          throw new Error(`celestialinphotos failed (${celestialRes.status}): ${errText}`);
        }

        const awimAPI_response = await celestialRes.json();
        setAstroData(awimAPI_response["astro dict"]);
        setBodiesInImages(awimAPI_response["bodies in images dicts"]);

        setLoading(false);
      } catch (err) {
        console.error("Error fetching clock image data:", err);
        setLoading(false);
      }
    };

    fetchClockImageData();
  }, [groupKey, momentsArrayKey, enabled, imagesSetOverrideKey, groupId, groupSlug]);

  return { loading, basenamesList, imagesSet, astroData, bodiesInImages};
}
