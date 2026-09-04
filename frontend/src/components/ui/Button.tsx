"use client";

import React from "react";
import styles from "./Button.module.css";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  iconOnly?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "secondary", iconOnly, children, ...props }, ref) => {
    
    const classes = [
      styles.button,
      variant === "primary" ? styles.primary : "",
      iconOnly ? styles["icon-only"] : "",
      className
    ].filter(Boolean).join(" ");

    return (
      <button ref={ref} className={classes} {...props}>
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
