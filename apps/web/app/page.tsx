import {PortfolioLab} from "./portfolio-lab";
import designState from "../../../.agentic/design.json";

export default function Page() {
  const profile = {
    name: process.env.NEXT_PUBLIC_PORTFOLIO_NAME ?? "Mara Voss",
    role: process.env.NEXT_PUBLIC_PORTFOLIO_ROLE ?? "Product designer & creative technologist",
    location: process.env.NEXT_PUBLIC_PORTFOLIO_LOCATION ?? "London ↔ anywhere",
  };

  const approvedDirection =
    designState.status === "approved" ? (designState.approved_direction as string | null) : null;

  return <PortfolioLab profile={profile} approvedDirection={approvedDirection} />;
}
