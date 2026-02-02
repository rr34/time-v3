import ClockScreenSmooth, { ClockScreenSmoothProps } from "./ClockScreenSmooth";
import ClockScreenStep from "./ClockScreenStep";

export type ClockScreenMode = "smooth" | "step";

interface ClockScreenProps extends ClockScreenSmoothProps {
  mode?: ClockScreenMode;
}

function ClockScreen({ mode = "smooth", ...props }: ClockScreenProps) {
  if (mode === "step") {
    return <ClockScreenStep {...props} />;
  }

  return <ClockScreenSmooth {...props} />;
}

export default ClockScreen;
export type { ClockScreenProps };
