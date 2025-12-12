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
    statusBox.className = "";
    statusBox.classList.add(type);
}

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        streamStarted = true;

        setStatus("Camera initialized. Please look directly at the camera.", "info");

        startTime = Date.now();
        timeLeftSpan.textContent = MAX_SECONDS.toString();

        verifyInterval = setInterval(captureAndVerify, 2000);
        timerInterval = setInterval(handleTimer, 1000);

    } catch (err) {
        console.error("Camera error:", err);
        setStatus("Unable to access camera. Please check permissions.", "error");
    }
}

function handleTimer() {
    if (verified) return;

    const elapsed = (Date.now() - startTime) / 1000;
    const remaining = Math.max(0, Math.ceil(MAX_SECONDS - elapsed));
    timeLeftSpan.textContent = remaining.toString();

    if (remaining <= 0) {
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

    if (video.videoWidth === 0) return;

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
            credentials: "same-origin", // ✅ IMPORTANT: keeps Flask session cookie working
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataUrl })
        });

        const result = await response.json();
        console.log("Verification result:", result);

        if (result.status === "verified") {
            verified = true;

            setStatus("Face verified successfully! Redirecting…", "success");
            clearInterval(verifyInterval);
            clearInterval(timerInterval);

            if (video.srcObject) {
                video.srcObject.getTracks().forEach(t => t.stop());
            }

            console.log("Redirecting to /vote …");

            setTimeout(() => {
                window.location.replace("/vote");
            }, 1200);

        } else {
            setStatus("Face not recognized yet. Please hold still.", "error");
        }

    } catch (e) {
        console.error("Error verifying:", e);
        setStatus("Network or server error. Retrying…", "error");
    } finally {
        verifying = false;
    }
}

window.onload = () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        setStatus("Requesting camera access…", "info");
        startCamera();
    } else {
        setStatus("Your browser does not support webcam access.", "error");
    }
};
