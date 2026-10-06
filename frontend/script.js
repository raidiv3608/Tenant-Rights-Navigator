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
// ASK QUESTION
// =========================================================

askButton.addEventListener(
    "click",
    askQuestion
);


async function askQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        alert(
            "Please enter a legal question first."
        );

        questionInput.focus();

        return;
    }


    // ---------------------------------------------
    // RESET PREVIOUS RESULTS
    // ---------------------------------------------

    answerSection.classList.add("hidden");

    sourcesSection.classList.add("hidden");

    answer.innerHTML = "";

    sources.innerHTML = "";


    // ---------------------------------------------
    // LOADING STATE
    // ---------------------------------------------

    loading.classList.remove("hidden");

    askButton.disabled = true;

    askButton.innerHTML =
        "Searching...";


    try {

        /*
         * The FastAPI backend will be connected here.
         *
         * For now this is intentionally disabled.
         *
         * Once app.py is created, this becomes:
         *
         * fetch("http://127.0.0.1:8000/ask", ...)
         */

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
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


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );

        }


        const data =
            await response.json();


        // -----------------------------------------
        // ANSWER
        // -----------------------------------------

        answer.textContent =
            data.answer ||
            "No answer was returned.";


        answerSection
            .classList
            .remove("hidden");


        // -----------------------------------------
        // SOURCES
        // -----------------------------------------

        if (
            data.sources &&
            data.sources.length > 0
        ) {

            data.sources.forEach(
                (source, index) => {

                    const sourceElement =
                        document.createElement("div");

                    sourceElement.className =
                        "source-item";

                    sourceElement.innerHTML = `
                        <strong>
                            ${index + 1}.
                            ${source.source || "Legal Source"}
                        </strong>

                        <div>
                            Page:
                            ${source.page || "N/A"}
                        </div>

                        <div class="source-text">
                            ${source.text || ""}
                        </div>
                    `;

                    sources.appendChild(
                        sourceElement
                    );

                }
            );


            sourcesSection
                .classList
                .remove("hidden");

        }


        // -----------------------------------------
        // SCROLL TO ANSWER
        // -----------------------------------------

        answerSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    }

    catch (error) {

        console.error(error);

        answer.textContent =
            "Unable to connect to the Tenant Rights Navigator backend. Make sure the FastAPI server is running.";

        answerSection
            .classList
            .remove("hidden");

    }

    finally {

        loading.classList.add("hidden");

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

                if (entry.isIntersecting) {

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