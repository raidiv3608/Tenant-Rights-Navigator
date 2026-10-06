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

            answer.textContent =
                data.answer;

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


                    // ---------------------------------------
                    // SOURCE TITLE
                    // ---------------------------------------

                    const title =
                        document.createElement("strong");

                    title.textContent =
                        `${index + 1}. ${
                            source.source ||
                            "Legal Source"
                        }`;


                    // ---------------------------------------
                    // PAGE
                    // ---------------------------------------

                    const page =
                        document.createElement("div");

                    page.textContent =
                        `Page: ${
                            source.page ||
                            "N/A"
                        }`;


                    // ---------------------------------------
                    // JURISDICTION
                    // ---------------------------------------

                    const jurisdiction =
                        document.createElement("div");

                    jurisdiction.textContent =
                        `Jurisdiction: ${
                            source.jurisdiction ||
                            "N/A"
                        }`;


                    // ---------------------------------------
                    // LEGAL TEXT
                    // ---------------------------------------

                    const sourceText =
                        document.createElement("div");

                    sourceText.className =
                        "source-text";

                    sourceText.textContent =
                        source.text ||
                        "No source text available.";


                    // ---------------------------------------
                    // BUILD SOURCE CARD
                    // ---------------------------------------

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


    // =======================================================
    // ERROR HANDLING
    // =======================================================

    catch (error) {

        console.error(
            "Tenant Rights Navigator error:",
            error
        );


        answer.textContent =
            `Unable to generate the legal answer.

${error.message}

Please make sure the Tenant Rights Navigator backend is running.`;


        answerSection
            .classList
            .remove("hidden");

    }


    // =======================================================
    // RESTORE BUTTON
    // =======================================================

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