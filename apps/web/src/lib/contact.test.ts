import { describe, it, expect } from "vitest";
import { contactSchema, createSubmission } from "./contact";
describe("contact submission identity", () => {
  it("normalizes an optional subject before retrying without a new identity", () => {
    const submission = createSubmission(
      {
        name: " Alice ",
        email: "alice@example.com",
        message: " A real project inquiry. ",
        website: "",
      },
      "cbb65241-b305-4759-8457-17e79aa294ee",
    );
    expect(submission.payload).toEqual({
      name: "Alice",
      email: "alice@example.com",
      subject: "",
      message: "A real project inquiry.",
      website: "",
    });
    expect(submission.key).toBe("cbb65241-b305-4759-8457-17e79aa294ee");
  });
  it("rejects a short message and an invalid email before sending", () => {
    const result = contactSchema.safeParse({
      name: "Alice",
      email: "wrong",
      message: "hi",
    });
    expect(result.success).toBe(false);
    if (!result.success)
      expect(result.error.issues.map((x) => x.path[0])).toEqual(
        expect.arrayContaining(["email", "message"]),
      );
  });
});
