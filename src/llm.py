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

        # Primary model
        self.primary_model = "gemini-3.5-flash"

        # Faster fallback model
        self.fallback_model = "gemini-3.5-flash-lite"


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

FORMAT YOUR RESPONSE AS PLAIN TEXT.

Do not use Markdown.
Do not use *, **, \*, #, ###, bullet symbols, or other Markdown formatting.

Use this structure:

Summary:
[short explanation]

Relevant provisions:
1. [provision]
2. [provision]
3. [provision]

Source:
Karnataka Rent Act, 1999
Section: [relevant section]
Page: [page]

Disclaimer:
This information is general legal information based strictly on the supplied legislation and is not personalized legal advice.
"""


        # =====================================================
        # TRY PRIMARY MODEL
        # =====================================================

        try:

            response = self.client.models.generate_content(
                model=self.primary_model,
                contents=prompt
            )

            return response.text


        except Exception as primary_error:

            error_text = str(primary_error)

            print(
                "\nPrimary Gemini model failed:"
            )

            print(error_text)


            # =================================================
            # TEMPORARY FAILURE → TRY FALLBACK
            # =================================================

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                print(
                    "\nTrying fallback Gemini model..."
                )

                try:

                    response = self.client.models.generate_content(
                        model=self.fallback_model,
                        contents=prompt
                    )

                    return response.text


                except Exception as fallback_error:

                    print(
                        "\nFallback Gemini model also failed:"
                    )

                    print(
                        str(fallback_error)
                    )

                    return (
                        "Gemini is temporarily unavailable.\n\n"
                        "The legal document retrieval system "
                        "worked correctly, but the AI generation "
                        "service is currently unavailable. "
                        "Please try again shortly."
                    )


            # =================================================
            # OTHER ERROR
            # =================================================

            return (
                "Gemini could not generate the answer.\n\n"
                f"Technical error: "
                f"{type(primary_error).__name__}: "
                f"{primary_error}"
            )