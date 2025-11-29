// face.js

const video = document.getElementById("video");
const statusBox = document.getElementById("status");
const timeLeftSpan = document.getElementById("timeLeft");

let streamStarted = false;
let verifying = false;
let verifyInterval = null;
let timerInterval = null;

const MAX_SECONDS = 30;
let startTime = null;
let verified = false;

function setStatus(message, type = "info") {
    statusBox.textContent = message;
    statusBox.className = ""; // reset classes
    statusBox.classList.add(type); // you can style .info, .success, .error in CSS
}

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        streamStarted = true;
        setStatus("Camera initialized. Please look directly at the camera.", "info");

        startTime = Date.now();
        timeLeftSpan.textContent = MAX_SECONDS.toString();

        // start verification loop
        verifyInterval = setInterval(captureAndVerify, 2000); // every 2 seconds

        // start countdown timer
        timerInterval = setInterval(handleTimer, 1000);
    } catch (err) {
        console.error("Error accessing webcam:", err);
        setStatus("Unable to access camera. Please check permissions.", "error");
    }
}

function handleTimer() {
    if (verified) {
        clearInterval(timerInterval);
        return;
    }
    const elapsed = (Date.now() - startTime) / 1000;
    const remaining = Math.max(0, Math.ceil(MAX_SECONDS - elapsed));
    timeLeftSpan.textContent = remaining.toString();

    if (remaining <= 0) {
        // time out: stop verification and go back with error
        clearInterval(timerInterval);
        clearInterval(verifyInterval);
        setStatus("Time limit exceeded. Voter not recognized.", "error");

        setTimeout(() => {
            window.location.href = "/voter_validation?face_failed=1";
        }, 1500);
    }
}

async function captureAndVerify() {
    if (!streamStarted || verifying || verified) return;

    // sometimes early frames are invalid; guard against that
    if (video.videoWidth === 0 || video.videoHeight === 0) {
        console.log("Video not ready yet, skipping frame.");
        return;
    }

    verifying = true;
    setStatus("Scanning face...", "info");

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg");

    try {
        const response = await fetch("/verify_face_stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataUrl })
        });

        if (!response.ok) {
            console.error("Server responded with status", response.status);
            setStatus("Error during verification. Retrying...", "error");
            return;
        }

        const result = await response.json();
        console.log("Verify response:", result);

        if (result.status === "verified") {
            verified = true;

            // Show success modal if it exists
            const modal = document.getElementById("successModal");
            if (modal) {
                modal.style.display = "flex";
            }

            setStatus("Voter verified. Proceeding to ballot…", "success");

            clearInterval(verifyInterval);
            clearInterval(timerInterval);

            // Redirect to ballot after short delay
            setTimeout(() => {
                window.location.href = "/vote";
            }, 2000);

        } else if (result.status === "unverified") {
            // Just keep scanning within time window
            setStatus("Face not recognized yet. Please hold still.", "error");
        } else {
            // status "error" or anything else
            setStatus("Error scanning face. Retrying...", "error");
        }
    } catch (e) {
        console.error("Error calling /verify_face_stream:", e);
        setStatus("Network error. Retrying...", "error");
    } finally {
        verifying = false;
    }
}

// Start camera on load
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    setStatus("Requesting camera access...", "info");
    startCamera();
} else {
    setStatus("This browser does not support webcam access.", "error");
}
