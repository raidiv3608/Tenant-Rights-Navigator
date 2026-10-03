
import os
import time

from google import genai


class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.8-flash"

    def generate_answer(self, question, context):

        prompt = f"""
You are Tenant Rights Navigator, an AI assistant that provides
general legal information based strictly on the supplied legislation.

IMPORTANT RULES:

1. Answer only using the supplied legal context.
2. Do not invent laws, sections, penalties, rights, or procedures.
3. If the supplied context does not contain enough information,
   clearly say that the available source material is insufficient.
4. Identify the relevant section of the legislation whenever possible.
5. Explain the provision in simple language.
6. Do not present the response as personalized legal advice.
7. Mention the source and page number available in the context.

LEGAL CONTEXT:
{context}

USER QUESTION:
{question}

Provide a concise answer based only on the legal context.
"""

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):

            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                return response.text

            except Exception as e:

                error_text = str(e)

                # Retry temporary server/rate-limit problems
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    if attempt < max_attempts:

                        wait_time = attempt * 5

                        print(
                            f"\nGemini is temporarily unavailable."
                            f" Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                    else:

                        return (
                            "Gemini is temporarily unavailable after "
                            f"{max_attempts} attempts.\n\n"
                            "Your legal-document retrieval system is "
                            "working correctly, but the Gemini service "
                            "did not accept the request."
                        )

                else:

                    return (
                        "Gemini could not generate the answer.\n\n"
                        f"Technical error: {type(e).__name__}: {e}"
                    )

