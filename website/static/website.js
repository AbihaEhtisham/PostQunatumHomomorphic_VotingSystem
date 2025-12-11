function updateLiveVotes() {
    fetch('/live_votes')
        .then(res => res.json())
        .then(data => {
            voteChart.data.datasets[0].data = Object.values(data);
            voteChart.update();
        })
        .catch(err => console.error("Error fetching live votes:", err));
}

// Update every 5 seconds
setInterval(updateLiveVotes, 5000);
