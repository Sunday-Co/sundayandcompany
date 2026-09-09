// Sunday & Company — form delivery. Keys from the site's lib/web3forms.ts
export const WEB3FORM_KEYS = {
  inquiry: "1588df12-aa7f-4dc6-8f28-d913d94b6f79",
  contact: "00d91493-ffa7-4406-9bcb-d5a561c6d6eb",
  reservation: "11c5669e-71cc-4a76-aa59-cdb03bed3f27",
};

// Bots fill hidden fields; humans never see them. A filled honeypot is
// resolved as a success so the bot gets no signal, but nothing is sent.
const HONEYPOT = "botcheck";

export async function submitToWeb3Forms(form, accessKey, subject, fields = {}) {
  const data = new FormData(form);

  if (data.get(HONEYPOT)) return { success: true, skipped: true };

  data.set("access_key", accessKey);
  data.set("subject", subject);
  data.set("from_name", "Sunday & Company Website");
  data.delete(HONEYPOT);
  Object.entries(fields).forEach(([name, value]) => data.set(name, value));

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  let response;
  try {
    response = await fetch("https://api.web3forms.com/submit", {
      method: "POST",
      body: data,
      signal: controller.signal,
    });
  } catch (e) {
    clearTimeout(timeout);
    throw new Error("We could not reach the server. Please check your connection and try again.");
  }
  clearTimeout(timeout);

  let result = {};
  try { result = await response.json(); } catch (e) { result = {}; }

  if (!response.ok || !result.success) {
    throw new Error(result.message || "We could not send your form. Please try again.");
  }
  return result;
}
