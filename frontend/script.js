// =========================================================
// ELEMENTS
// =========================================================

const questionInput =
    document.getElementById("questionInput");

const askButton =
    document.getElementById("askButton");

const loading =
    document.getElementById("loading");

const answerSection =
    document.getElementById("answerSection");

const answer =
    document.getElementById("answer");

const sourcesSection =
    document.getElementById("sourcesSection");

const sources =
    document.getElementById("sources");


// =========================================================
// BACKEND CONFIGURATION
// =========================================================

const API_URL =
    "http://127.0.0.1:8000/ask";


// =========================================================
// SUGGESTION BUTTONS
// =========================================================

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener("click", () => {

            questionInput.value =
                button.dataset.question;

            questionInput.focus();

        });

    });


// =========================================================
// ASK BUTTON
// =========================================================

askButton.addEventListener(
    "click",
    askQuestion
);


// =========================================================
// ENTER KEY SUPPORT
// =========================================================

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();

        }

    }
);


// =========================================================
// ASK QUESTION
// =========================================================

async function askQuestion() {

    const question =
        questionInput.value.trim();


    // -------------------------------------------------------
    // VALIDATE QUESTION
    // -------------------------------------------------------

    if (!question) {

        alert(
            "Please enter a legal question first."
        );

        questionInput.focus();

        return;
    }


    // -------------------------------------------------------
    // RESET PREVIOUS RESULTS
    // -------------------------------------------------------

    answerSection.classList.add(
        "hidden"
    );

    sourcesSection.classList.add(
        "hidden"
    );

    answer.textContent = "";

    sources.innerHTML = "";


    // -------------------------------------------------------
    // LOADING STATE
    // -------------------------------------------------------

    loading.classList.remove(
        "hidden"
    );

    askButton.disabled = true;

    askButton.innerHTML =
        "Searching...";


    try {

        // ===================================================
        // SEND QUESTION TO FASTAPI
        // ===================================================

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        // ===================================================
        // CHECK SERVER RESPONSE
        // ===================================================

        if (!response.ok) {

            let errorMessage =
                `Server returned ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    errorMessage =
                        errorData.detail;

                }

            } catch (_) {

                // Ignore JSON parsing failure.

            }

            throw new Error(
                errorMessage
            );

        }


        // ===================================================
        // READ RESPONSE
        // ===================================================

        const data =
            await response.json();


        // ===================================================
        // DISPLAY ANSWER
        // ===================================================

        if (
            data.answer &&
            data.answer.trim()
        ) {

            answer.innerHTML =
                formatAnswer(data.answer);

        } else {

            answer.textContent =
                "No answer was returned by the legal assistant.";

        }


        answerSection
            .classList
            .remove("hidden");


        // ===================================================
        // DISPLAY SOURCES
        // ===================================================

        if (
            Array.isArray(data.sources) &&
            data.sources.length > 0
        ) {

            data.sources.forEach(
                (source, index) => {

                    const sourceElement =
                        document.createElement("div");

                    sourceElement.className =
                        "source-item";


                    const title =
                        document.createElement("strong");

                    title.textContent =
                        `${index + 1}. ${
                            source.source ||
                            "Legal Source"
                        }`;


                    const page =
                        document.createElement("div");

                    page.textContent =
                        `Page: ${
                            source.page ||
                            "N/A"
                        }`;


                    const jurisdiction =
                        document.createElement("div");

                    jurisdiction.textContent =
                        `Jurisdiction: ${
                            source.jurisdiction ||
                            "N/A"
                        }`;


                    const sourceText =
                        document.createElement("div");

                    sourceText.className =
                        "source-text";

                    sourceText.textContent =
                        source.text ||
                        "No source text available.";


                    sourceElement.appendChild(
                        title
                    );

                    sourceElement.appendChild(
                        page
                    );

                    sourceElement.appendChild(
                        jurisdiction
                    );

                    sourceElement.appendChild(
                        sourceText
                    );


                    sources.appendChild(
                        sourceElement
                    );

                }
            );


            sourcesSection
                .classList
                .remove("hidden");

        }


        // ===================================================
        // SCROLL TO ANSWER
        // ===================================================

        setTimeout(() => {

            answerSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);


    }

    catch (error) {

        console.error(
            "Tenant Rights Navigator error:",
            error
        );


        answer.innerHTML =
            formatAnswer(
                `Unable to generate the legal answer.

${error.message}

Please make sure the Tenant Rights Navigator backend is running.`
            );


        answerSection
            .classList
            .remove("hidden");

    }


    finally {

        loading.classList.add(
            "hidden"
        );

        askButton.disabled = false;

        askButton.innerHTML =
            "Search Legal Database →";

    }

}


// =========================================================
// FORMAT GEMINI ANSWER
// =========================================================

function formatAnswer(text) {

    let formatted = text;


    // -------------------------------------------------------
    // Escape HTML for safety
    // -------------------------------------------------------

    formatted = formatted
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");


    // -------------------------------------------------------
    // Remove escaped Markdown characters
    // -------------------------------------------------------

    formatted = formatted.replace(
        /\\([*_#])/g,
        "$1"
    );


    // -------------------------------------------------------
    // Remove Markdown heading symbols
    // -------------------------------------------------------

    formatted = formatted.replace(
        /^#{1,6}\s*/gm,
        ""
    );


    // -------------------------------------------------------
    // Remove horizontal-rule Markdown
    // -------------------------------------------------------

    formatted = formatted.replace(
        /^\s*\*{3,}\s*$/gm,
        ""
    );


    // -------------------------------------------------------
    // Bold + italic
    // ***text***
    // -------------------------------------------------------

    formatted = formatted.replace(
        /\*\*\*(.*?)\*\*\*/gs,
        "<strong><em>$1</em></strong>"
    );


    // -------------------------------------------------------
    // Bold
    // **text**
    // -------------------------------------------------------

    formatted = formatted.replace(
        /\*\*(.*?)\*\*/gs,
        "<strong>$1</strong>"
    );


    // -------------------------------------------------------
    // Italic
    // *text*
    // -------------------------------------------------------

    formatted = formatted.replace(
        /(^|[^\*])\*([^*\n]+)\*(?!\*)/g,
        "$1<em>$2</em>"
    );


    // -------------------------------------------------------
    // Remove escaped periods
    // -------------------------------------------------------

    formatted = formatted.replaceAll(
    "\\.",
    "."
);


    // -------------------------------------------------------
    // Convert escaped numbered-list markers
    // -------------------------------------------------------

    formatted = formatted.replace(
        /^(\d+)\\\.\s*/gm,
        "$1. "
    );


    // -------------------------------------------------------
    // Convert Markdown bullet markers
    // -------------------------------------------------------

    formatted = formatted.replace(
        /^[ \t]*[-•]\s+/gm,
        "• "
    );


    // -------------------------------------------------------
    // Convert line breaks
    // -------------------------------------------------------

    formatted = formatted.replace(
        /\n/g,
        "<br>"
    );


    // -------------------------------------------------------
    // Clean excessive line breaks
    // -------------------------------------------------------

    formatted = formatted.replace(
        /(<br>\s*){3,}/g,
        "<br><br>"
    );


    return formatted.trim();

}


// =========================================================
// SCROLL REVEAL
// =========================================================

const featureCards =
    document.querySelectorAll(
        ".feature-card"
    );


const observer =
    new IntersectionObserver(
        entries => {

            entries.forEach(entry => {

                if (
                    entry.isIntersecting
                ) {

                    entry.target.classList.add(
                        "visible"
                    );

                }

            });

        },

        {
            threshold: 0.15
        }

    );


featureCards.forEach(card => {

    observer.observe(card);

});