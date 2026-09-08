document.addEventListener("DOMContentLoaded", function () {
    const inputText = document.getElementById("inputText");
    const translatedText = document.getElementById("translatedText");
    const sourceLanguage = document.getElementById("sourceLanguage");
    const targetLanguage = document.getElementById("targetLanguage");
    const translateButton = document.getElementById("translateButton");
    const swapButton = document.getElementById("swapButton");
    const clearButton = document.getElementById("clearButton");
    const copyButton = document.getElementById("copyButton");
    const characterCount = document.getElementById("characterCount");
    const statusMessage = document.getElementById("statusMessage");

    // Live character counter
    if (inputText && characterCount) {
        inputText.addEventListener("input", function () {
            characterCount.textContent = inputText.value.length + " / 500";
        });
    }

    // Translate action
    if (translateButton) {
        translateButton.addEventListener("click", async function () {
            const text = inputText.value.trim();
            const source = sourceLanguage.value;
            const target = targetLanguage.value;

            if (!text) {
                statusMessage.style.color = "#e67e22";
                statusMessage.textContent = "Please enter text to translate.";
                return;
            }

            if (source === target) {
                statusMessage.style.color = "#e67e22";
                statusMessage.textContent = "Source and target languages cannot be the same.";
                return;
            }

            translateButton.disabled = true;
            translateButton.textContent = "Translating...";
            statusMessage.style.color = "#3498db";
            statusMessage.textContent = "Processing translation...";
            translatedText.value = "";

            try {
                const response = await fetch("/translate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        text: text,
                        source: source,
                        target: target
                    })
                });

                const data = await response.json();

                if (data.success) {
                    translatedText.value = data.translation;
                    statusMessage.style.color = "#2ecc71";
                    statusMessage.textContent = "Translation successful!";
                } else {
                    statusMessage.style.color = "#e74c3c";
                    statusMessage.textContent = "Error: " + data.error;
                }
            } catch (err) {
                statusMessage.style.color = "#e74c3c";
                statusMessage.textContent = "Connection failed. Please ensure Flask server is running.";
                console.error("Fetch error:", err);
            } finally {
                translateButton.disabled = false;
                translateButton.textContent = "Translate";
            }
        });
    }

    // Swap languages
    if (swapButton) {
        swapButton.addEventListener("click", function () {
            const temp = sourceLanguage.value;
            sourceLanguage.value = targetLanguage.value;
            targetLanguage.value = temp;

            if (translatedText.value.trim() !== "") {
                inputText.value = translatedText.value;
                translatedText.value = "";
                characterCount.textContent = inputText.value.length + " / 500";
            }
        });
    }

    // Clear input/output
    if (clearButton) {
        clearButton.addEventListener("click", function () {
            inputText.value = "";
            translatedText.value = "";
            characterCount.textContent = "0 / 500";
            statusMessage.textContent = "";
        });
    }

    // Copy to clipboard
    if (copyButton) {
        copyButton.addEventListener("click", async function () {
            if (!translatedText.value.trim()) return;

            try {
                await navigator.clipboard.writeText(translatedText.value);
                const prev = copyButton.textContent;
                copyButton.textContent = "✓ Copied!";
                setTimeout(function () {
                    copyButton.textContent = prev;
                }, 2000);
            } catch (err) {
                console.error("Copy failed:", err);
            }
        });
    }
});