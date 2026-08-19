import type {ButtonHTMLAttributes} from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  size?: "compact" | "default";
};

export function Button({className = "", size = "default", ...props}: ButtonProps) {
  return <button className={`eae-button ${className}`.trim()} data-size={size} {...props} />;
}
