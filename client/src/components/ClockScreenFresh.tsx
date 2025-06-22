import { useEffect, useRef, useState } from "react";

interface ClockScreenFreshProps {
  totalDuration?: number;
  repeatLimit?: string;
}

function ClockScreenFresh({ totalDuration = 15, repeatLimit = "2" }: ClockScreenFreshProps) {
  const startTimeRef = useRef(performance.now());
  const [elapsed, setElapsed] = useState("0.00");

  useEffect(() => {
    let frame: number;

    const update = () => {
      const now = performance.now();
      const delta = ((now - startTimeRef.current) / 1000).toFixed(2);
      setElapsed(delta);
      frame = requestAnimationFrame(update);
    };

    update();
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <>
      <svg width="200" height="200" viewBox="-50 -50 100 100" xmlns="http://www.w3.org/2000/svg">
        <path fill="gray">
          <animate
            attributeName="d"
            dur={`${totalDuration}s`}
            repeatCount="indefinite"
            values="
              M 0 -40 A 0 40 0 0 0 0 40 A 40 40 0 0 0 0 -40;
              M 0 -40 A 40 40 0 0 1 0 40 A 40 40 0 0 0 0 -40;
              M 0 -40 A 0 40 0 0 1 0 40 A 40 40 0 0 0 0 -40;
            "
          />
        </path>
      </svg>

      <p>Time elapsed since animation start: {elapsed}s</p>
    </>
  );
}

export default ClockScreenFresh;
