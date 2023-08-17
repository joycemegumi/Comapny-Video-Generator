function checkUserKeydown(event) {
    return event instanceof KeyboardEvent;
}
function pollVideoStatus(url) {
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            if (data) {
                // Check if the response contains the video URL
                var videoURL = data.video_url;
                if (videoURL) {
                    // Video generation successful
                    // Redirect the user to the video playback page with the video URL as a query parameter
                    window.location.href = "video.html?videoURL=" + encodeURIComponent(videoURL);
                } else {
                    // Video URL not found in the response
                    console.log("Video URL not found in the response. Waiting 2 seconds.");
                    document.getElementById("loading").innerHTML = "Video generation in progress. Please wait..." + data.message;
                    setTimeout(function() {
                        pollVideoStatus(url);
                    }, 2000);
                }
            } else {
                // Video generation failed or other error occurred
                console.log("An error occurred while generating the video.");
            }
        });
}
function submit(event) {
    event.preventDefault();
    console.log("submitted", form.action);

    fetch(form.action, {
        method: "POST",
        headers: {
            "Content-Type": "x-www-form-urlencoded",
        },
        body: new URLSearchParams(new FormData(form)),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data) {
            // Check if the response contains the video URL
            var videoURL = data.video_url;
            if (videoURL) {
                // Video generation successful
                // Redirect the user to the video playback page with the video URL as a query parameter
                window.location.href = "video.html?videoURL=" + encodeURIComponent(videoURL);
            } else {
                // Video URL not found in the response
                console.log("Video URL not found in the response.");
                pollVideoStatus(form.action + "/" + data.video_id);
            }
        } else {
            // Video generation failed or other error occurred
            console.log("An error occurred while generating the video.");
        }
    })
    .catch((error) => {
        console.log("Error:", error);
        console.log("An error occurred while processing your request.");
    });
}
const form = document.getElementById("form");

form.addEventListener("submit", submit);