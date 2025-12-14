"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface NewsletterFormProps {
  variant?: "default" | "dark" | "footer";
  showName?: boolean;
  source?: string;
  className?: string;
  onSuccess?: (data: unknown) => void;
}

export function NewsletterForm({
  variant = "default",
  showName = false,
  source = "website",
  className = "",
  onSuccess,
}: NewsletterFormProps) {
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setStatus("error");
      setMessage("Please enter your email address");
      return;
    }

    setIsLoading(true);
    setStatus("idle");
    setMessage("");

    try {
      // The API endpoint - using the SalarsU API
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://www.salars.net";

      const response = await fetch(`${apiUrl}/api/newsletter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          firstName: firstName || undefined,
          source,
          categories: ["dreamweaving"], // Default to dreamweaving for this site
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus("success");
        setMessage("Welcome aboard! Check your inbox for a welcome message.");
        setEmail("");
        setFirstName("");
        onSuccess?.(data);
      } else {
        setStatus("error");
        setMessage(data.error || "Something went wrong. Please try again.");
      }
    } catch (error) {
      console.error("Newsletter signup error:", error);
      setStatus("error");
      setMessage("Unable to connect. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  const inputClasses =
    variant === "dark"
      ? "h-11 w-full rounded-lg border border-white/20 bg-white/10 px-3 text-sm text-white placeholder:text-slate-300 focus:border-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-400"
      : "h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500";

  const buttonClasses =
    variant === "dark"
      ? "bg-white text-slate-900 hover:bg-slate-100"
      : "";

  return (
    <form onSubmit={handleSubmit} className={`space-y-3 ${className}`}>
      {showName && (
        <input
          type="text"
          aria-label="First name"
          placeholder="First name (optional)"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          className={inputClasses}
          disabled={isLoading}
        />
      )}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          type="email"
          aria-label="Email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={inputClasses}
          disabled={isLoading}
          required
        />
        <Button
          type="submit"
          variant={variant === "dark" ? "secondary" : "default"}
          className={buttonClasses}
          disabled={isLoading}
        >
          {isLoading ? "Subscribing..." : "Subscribe"}
        </Button>
      </div>

      {/* Status Messages */}
      {status === "success" && (
        <p className={`text-sm ${variant === "dark" ? "text-green-400" : "text-green-600"}`}>
          {message}
        </p>
      )}
      {status === "error" && (
        <p className={`text-sm ${variant === "dark" ? "text-red-400" : "text-red-600"}`}>
          {message}
        </p>
      )}
    </form>
  );
}

export default NewsletterForm;
