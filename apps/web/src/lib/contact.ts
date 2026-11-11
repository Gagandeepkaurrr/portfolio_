import { z } from "zod";
export const contactSchema = z.object({
  name: z.string().trim().min(1, "Please enter your name.").max(100),
  email: z.email("Please enter a valid email address.").max(254),
  subject: z.string().trim().max(150).optional(),
  message: z
    .string()
    .trim()
    .min(10, "Please write at least 10 characters.")
    .max(5000),
  website: z.string().max(0, "Please leave this field empty.").optional(),
});
export type ContactInput = z.input<typeof contactSchema>;
export type Submission = {
  key: string;
  payload: {
    name: string;
    email: string;
    subject: string;
    message: string;
    website: string;
  };
};
export function createSubmission(
  input: ContactInput,
  key: string = crypto.randomUUID(),
): Submission {
  const parsed = contactSchema.parse(input);
  return {
    key,
    payload: {
      ...parsed,
      subject: parsed.subject || "",
      website: parsed.website || "",
    },
  };
}
