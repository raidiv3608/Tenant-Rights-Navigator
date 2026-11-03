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
        self.primary_model = "gemini-3.5-flash-lite"

        # Faster fallback model
        self.fallback_model = "gemini-3.5-flash"


    def generate_answer(self, question, context):

        prompt = f"""
You are NyayaSetu, an AI assistant that provides general legal
information based strictly on the supplied legislation.

CORE RULES:

1. Answer the user's actual question directly and clearly.
2. Use only the supplied legal context. Do not introduce facts,
   laws, rights, penalties, or procedures from outside it.
3. If the context does not adequately answer the question, clearly
   identify what information is missing.
4. Use only section numbers explicitly established by the legal text
   or its supplied metadata.
5. NEVER interpret isolated numbers at the beginning of extracted
   text as section numbers. These may be page numbers or PDF
   extraction artefacts.
6. If a passage is a continuation of a section and its section number
   cannot be established reliably, write "Section not identified".
7. Do not claim that a provision establishes a responsibility,
   entitlement, deadline, or procedure unless the supplied text
   supports that claim.
8. Distinguish between different parties' responsibilities whenever
   the question asks who is responsible.
9. Include only provisions directly relevant to the user's question.
   Do not force three provisions if fewer are supported.
10. Cite the source, section and page only when those details are
    available in the supplied context.
11. Do not present the response as personalized legal advice.
12. If relevant passages conflict or are incomplete, acknowledge
    that limitation instead of guessing.

LEGAL CONTEXT:
{context}

USER QUESTION:
{question}

RESPONSE FORMAT:

Use plain text without Markdown formatting.

Summary:
Give a direct, concise answer to the question.

Relevant provisions:
Explain only the relevant provisions supported by the context.
Include the section number only when reliably established.
If the available context is insufficient, explain precisely what
cannot be established.

Source:
Karnataka Rent Act, 1999
Section: [verified section number, or "Section not identified"]
Page: [page number supported by the context]

Disclaimer:
This is general legal information based on the supplied
legislation, not personalized legal advice.
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