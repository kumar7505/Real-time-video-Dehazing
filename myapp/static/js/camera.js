document.getElementById("startWebcam").addEventListener("click", function() {
    fetch("/start-webcam/")
    .then(response => response.json())
    .then(data => {
        console.log(data.status);
        alert("Webcam started!");
    });
});