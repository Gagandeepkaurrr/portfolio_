import { useState } from "react";
import { Link } from 'react-router';
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion, useReducedMotion } from "motion/react";
import {
  contactSchema,
  createSubmission,
  type ContactInput,
  type Submission,
} from "@/lib/contact";
import { Arrow } from "./icons";
export function ContactForm({ email }: { email: string }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ContactInput>({ resolver: zodResolver(contactSchema) });
  const [pending, setPending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState<Submission | null>(null);
  const reduced = useReducedMotion();
  async function deliver(submission: Submission) {
    setPending(true);
    setError("");
    setAttempt(submission);
    try {
      const response = await fetch("/api/v1/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": submission.key,
        },
        body: JSON.stringify(submission.payload),
        signal: AbortSignal.timeout(15000),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        if (response.status === 429) {
          setAttempt(null);
          throw new Error(
            "You've sent several messages recently. Please try again later or use the email link.",
          );
        }
        if (
          response.status >= 400 &&
          response.status < 500 &&
          response.status !== 409
        )
          setAttempt(null);
        throw new Error(
          data?.error?.message ||
            "Your message couldn't be saved. Please try again, or email me directly.",
        );
      }
      setSent(true);
      setAttempt(null);
      reset();
    } catch (e) {
      setError(
        e instanceof Error &&
          e.name !== "TimeoutError" &&
          e.name !== "AbortError"
          ? e.message
          : "The connection was interrupted. Retry this message to check whether it was received.",
      );
    } finally {
      setPending(false);
    }
  }
  if (sent)
    return (
      <div className="contact-success" role="status">
        <span className="success-mark" aria-hidden="true">
          ✓
        </span>
        <h3>Message received.</h3>
        <p>Your message has been received. Thank you for getting in touch.</p>
        <button className="text-link" onClick={() => setSent(false)}>
          Write another message <Arrow />
        </button>
      </div>
    );
  return (
    <form
      className="contact-form"
      onSubmit={handleSubmit((values) => deliver(createSubmission(values)))}
      noValidate
    >
      <fieldset disabled={pending || !!attempt}>
        <legend className="sr-only">Send a message</legend>
        <div className="form-row">
          <div className="form-field">
            <label htmlFor="contact-name">
              Name <span>*</span>
            </label>
            <input
              id="contact-name"
              autoComplete="name"
              placeholder="Your name"
              {...register("name")}
              aria-invalid={!!errors.name}
              aria-describedby={errors.name ? "name-error" : undefined}
            />
            {errors.name && (
              <span id="name-error" className="field-error">
                {errors.name.message}
              </span>
            )}
          </div>
          <div className="form-field">
            <label htmlFor="contact-email">
              Email <span>*</span>
            </label>
            <input
              id="contact-email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              {...register("email")}
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? "email-error" : undefined}
            />
            {errors.email && (
              <span id="email-error" className="field-error">
                {errors.email.message}
              </span>
            )}
          </div>
        </div>
        <div className="form-field">
          <label htmlFor="contact-subject">
            Subject <span className="optional">(optional)</span>
          </label>
          <input
            id="contact-subject"
            placeholder="What's on your mind?"
            {...register("subject")}
            aria-invalid={!!errors.subject}
          />
          {errors.subject && (
            <span className="field-error">{errors.subject.message}</span>
          )}
        </div>
        <div className="form-field">
          <label htmlFor="contact-message">
            Message <span>*</span>
          </label>
          <textarea
            id="contact-message"
            rows={4}
            placeholder="A little about your project, opportunity, or question…"
            {...register("message")}
            aria-invalid={!!errors.message}
            aria-describedby={errors.message ? "message-error" : undefined}
          />
          {errors.message && (
            <span id="message-error" className="field-error">
              {errors.message.message}
            </span>
          )}
        </div>
        <div hidden aria-hidden="true">
          <label htmlFor="website">Website</label>
          <input
            id="website"
            tabIndex={-1}
            autoComplete="off"
            {...register("website")}
          />
        </div>
      </fieldset>
      {error && (
        <div className="form-error" role="alert">
          <p>{error}</p>
          {attempt && (
            <>
              <p>
                Your original message is kept here to prevent a duplicate. Retry
                it before starting a different message.
              </p>
              <button
                type="button"
                className="text-link"
                disabled={pending}
                onClick={() => deliver(attempt)}
              >
                Retry original message <Arrow />
              </button>
            </>
          )}
          <a href={`mailto:${email}`}>Email me directly ↗</a>
        </div>
      )}
      <div className="form-bottom">
        <p>
          Your details are used to receive and respond to your inquiry.{" "}
          <Link to="/privacy">Privacy notice</Link>
        </p>
        <motion.button
          whileTap={reduced ? undefined : { scale: 0.98 }}
          className="button button-primary"
          type="submit"
          disabled={pending || !!attempt}
        >
          {pending ? "Sending…" : "Send message"}
          <Arrow diagonal />
        </motion.button>
      </div>
    </form>
  );
}
